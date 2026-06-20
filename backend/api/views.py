import json
import os
import re
from django.http import StreamingHttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.decorators import renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import BaseRenderer, JSONRenderer
from .models import BudgetScenario, BudgetLineItem
from .serializers import BudgetScenarioSerializer, BudgetLineItemSerializer
try:
    import openai
except ImportError:
    openai = None

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')


class ServerSentEventRenderer(BaseRenderer):
    media_type = 'text/event-stream'
    format = 'event-stream'
    charset = None

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data

class BudgetScenarioViewSet(viewsets.ModelViewSet):
    queryset = BudgetScenario.objects.all().order_by('-created_at')
    serializer_class = BudgetScenarioSerializer

class BudgetLineItemViewSet(viewsets.ModelViewSet):
    queryset = BudgetLineItem.objects.all().order_by('id')
    serializer_class = BudgetLineItemSerializer

@api_view(['GET'])
def budget_summary(request, scenario_id):
    scenario = BudgetScenario.objects.filter(id=scenario_id).first()
    if not scenario:
        return Response({'detail': 'Scenario not found.'}, status=status.HTTP_404_NOT_FOUND)
    items = scenario.line_items.all()
    total_budget = sum(item.budget_amount for item in items)
    total_actual = sum(item.actual_amount for item in items)
    items_data = [
        {
            'department': item.department,
            'category': item.category,
            'budget_amount': float(item.budget_amount),
            'actual_amount': float(item.actual_amount),
            'variance': float(item.variance()),
            'risk_rating': item.risk_rating,
        }
        for item in items
    ]
    return Response({
        'scenario': BudgetScenarioSerializer(scenario).data,
        'totals': {
            'budget': float(total_budget),
            'actual': float(total_actual),
            'variance': float(total_actual - total_budget),
        },
        'items': items_data,
    })


def normalize_question(question):
    return re.sub(r'\s+', ' ', question.lower().strip())


def parse_risk_levels(question):
    normalized = normalize_question(question)
    if 'only high-risk' in normalized or 'only high risk' in normalized:
        return ['high']
    if 'only medium-risk' in normalized or 'only medium risk' in normalized:
        return ['medium']
    if 'only low-risk' in normalized or 'only low risk' in normalized:
        return ['low']

    levels = []
    if 'high-risk' in normalized or 'high risk' in normalized or 'high' in normalized:
        levels.append('high')
    if 'medium-risk' in normalized or 'medium risk' in normalized or 'medium' in normalized:
        levels.append('medium')
    if 'low-risk' in normalized or 'low risk' in normalized or 'low' in normalized:
        levels.append('low')
    return list(dict.fromkeys(levels))


def matches_keywords(item, question):
    question_lower = question.lower()
    return item.department.lower() in question_lower or item.category.lower() in question_lower


def risk_matches(risk_rating, risk_levels):
    rating = risk_rating.strip().lower()
    return any(rating.startswith(level) for level in risk_levels)


def scenario_analysis_text(scenario, question):
    items = list(scenario.line_items.all())
    if not items:
        return {
            'title': 'Empty Scenario',
            'text': 'This scenario has no line items yet.',
        }

    question_normalized = normalize_question(question)
    filtered_items = [item for item in items if matches_keywords(item, question)] or items
    risk_levels = parse_risk_levels(question)
    if risk_levels:
        filtered_items = [item for item in filtered_items if risk_matches(item.risk_rating, risk_levels)]

    if 'group' in question_normalized and 'department' in question_normalized:
        if not filtered_items:
            return {
                'title': 'No matching items',
                'text': 'No items matched the requested filters.',
            }
        grouped = {}
        for item in filtered_items:
            values = grouped.setdefault(item.department, {'budget': 0.0, 'actual': 0.0, 'item_count': 0})
            values['budget'] += float(item.budget_amount)
            values['actual'] += float(item.actual_amount)
            values['item_count'] += 1

        rows = [
            {
                'department': department,
                'budget': values['budget'],
                'actual': values['actual'],
                'variance': float(values['actual'] - values['budget']),
                'item_count': values['item_count'],
            }
            for department, values in grouped.items()
        ]
        risk_text = f" Filtered to {', '.join(risk_levels)}-risk items." if risk_levels else ''
        return {
            'title': 'Department Summary',
            'text': f"Found {len(filtered_items)} line items grouped by department.{risk_text}",
            'table': sorted(rows, key=lambda r: r['variance'], reverse=True),
            'summary': {
                'department_count': len(rows),
                'item_count': len(filtered_items),
            },
        }

    if 'over budget' in question_normalized or 'overbudget' in question_normalized:
        over_budget = [item for item in filtered_items if item.variance() > 0]
        rows = [
            {
                'department': item.department,
                'category': item.category,
                'variance': float(item.variance()),
                'risk_rating': item.risk_rating,
            }
            for item in sorted(over_budget, key=lambda i: i.variance(), reverse=True)
        ]
        return {
            'title': 'Over Budget Items',
            'text': f"Found {len(rows)} over-budget line items.",
            'table': rows,
            'summary': {
                'item_count': len(rows),
            },
        }

    if 'largest variances' in question_normalized or 'variances' in question_normalized:
        rows = [
            {
                'department': item.department,
                'category': item.category,
                'variance': float(item.variance()),
                'budget_amount': float(item.budget_amount),
                'actual_amount': float(item.actual_amount),
            }
            for item in sorted(filtered_items, key=lambda i: abs(i.variance()), reverse=True)
        ]
        return {
            'title': 'Largest Variances',
            'text': 'Line items with the largest absolute variances first.',
            'table': rows[:10],
            'summary': {
                'item_count': len(rows[:10]),
            },
        }

    if 'reduce' in question_normalized and 'marketing' in question_normalized:
        marketing = [item for item in filtered_items if item.department.lower() == 'marketing']
        if not marketing:
            return {'title': 'Marketing impact', 'text': 'No marketing items found for this scenario.'}
        original = sum(item.actual_amount for item in marketing)
        new_actual = original * 0.90
        savings = float(original - new_actual)
        return {
            'title': 'Marketing Spend Reduction Impact',
            'text': f'Reducing Marketing actual spend by 10% saves ${savings:,.2f}.',
            'summary': {
                'original_actual': float(original),
                'new_actual': float(new_actual),
                'savings': savings,
            },
        }

    total_budget = float(sum(item.budget_amount for item in filtered_items))
    total_actual = float(sum(item.actual_amount for item in filtered_items))
    total_variance = float(sum(item.variance() for item in filtered_items))
    return {
        'title': 'Scenario Summary',
        'text': 'Here is a quick scenario summary with totals and notable items.',
        'summary': {
            'total_budget': total_budget,
            'total_actual': total_actual,
            'total_variance': total_variance,
            'item_count': len(filtered_items),
        },
    }


def build_ai_answer(scenario, question, analysis):
    if not openai or not OPENAI_API_KEY:
        return analysis.get('text', 'Here is the analysis result.')

    openai.api_key = OPENAI_API_KEY
    prompt = (
        'You are a budget analyst assistant. Use only the provided scenario details and analysis results. '
        f'Scenario: {scenario.name} ({scenario.period})\nDescription: {scenario.description}\nQuestion: {question}\n'
        f'Analysis data: {json.dumps(analysis, default=str)}\n'
        'Answer concisely and refer to the table or summary content when relevant.'
    )
    try:
        completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': 'You answer budget questions using structured analysis.'},
                {'role': 'user', 'content': prompt},
            ],
            max_tokens=250,
            temperature=0.2,
        )
        return completion.choices[0].message.content.strip()
    except Exception:
        return analysis.get('text', 'Here is the analysis result.')


def sse_event(event_name, payload):
    return f"event: {event_name}\ndata: {json.dumps(payload, default=str)}\n\n"


@api_view(['GET', 'POST'])
@renderer_classes([JSONRenderer, ServerSentEventRenderer])
def scenario_chat(request, scenario_id):
    scenario = BudgetScenario.objects.filter(id=scenario_id).first()
    if not scenario:
        return Response({'detail': 'Scenario not found.'}, status=status.HTTP_404_NOT_FOUND)

    question = (
        request.GET.get('question', '').strip()
        or request.data.get('question', '').strip()
    )

    if not question:
        return Response({'detail': 'Question is required.'}, status=status.HTTP_400_BAD_REQUEST)

    analysis = scenario_analysis_text(scenario, question)
    analysis['text'] = build_ai_answer(scenario, question, analysis)

    stream_param = request.GET.get('stream', '1').lower()

    # ✅ Non-streaming JSON mode (tests / fallback)
    if stream_param in ('0', 'false'):
        return Response(analysis)

    def event_stream():
        yield sse_event('message', {'text': analysis['text']})

        if analysis.get('table') is not None:
            yield sse_event('table', analysis['table'])

        if analysis.get('summary') is not None:
            yield sse_event('summary', analysis['summary'])

        yield sse_event('done', {})

    # ✅ Streaming response
    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )

    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'  # important for Nginx
    return response