from django.core.management.base import BaseCommand
from api.models import BudgetScenario, BudgetLineItem

class Command(BaseCommand):
    help = 'Seed demo budget scenarios and line items.'

    def handle(self, *args, **options):
        if BudgetScenario.objects.exists():
            self.stdout.write('Demo data already seeded.')
            return

        scenario = BudgetScenario.objects.create(
            name='Q2 Operational Budget',
            period='2026 Q2',
            description='Marketing, Sales, and Engineering budgets for Q2.',
        )

        BudgetLineItem.objects.bulk_create([
            BudgetLineItem(
                scenario=scenario,
                department='Marketing',
                category='Paid Ads',
                budget_amount=50000,
                actual_amount=65000,
                risk_rating='High',
                notes='Digital campaigns exceeded plan.',
            ),
            BudgetLineItem(
                scenario=scenario,
                department='Sales',
                category='Travel',
                budget_amount=20000,
                actual_amount=27500,
                risk_rating='Medium',
                notes='Increased travel for field sales.',
            ),
            BudgetLineItem(
                scenario=scenario,
                department='Engineering',
                category='Contractors',
                budget_amount=30000,
                actual_amount=28500,
                risk_rating='Low',
                notes='Contractor spend below budget.',
            ),
            BudgetLineItem(
                scenario=scenario,
                department='Marketing',
                category='Events',
                budget_amount=15000,
                actual_amount=14000,
                risk_rating='Low',
                notes='On track for event spend.',
            ),
        ])

        self.stdout.write('Seed demo data created.')
