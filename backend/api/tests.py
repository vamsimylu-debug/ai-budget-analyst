from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import BudgetScenario, BudgetLineItem

class BudgetAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.scenario = BudgetScenario.objects.create(name='Test Scenario', period='2026 Q3')
        BudgetLineItem.objects.create(
            scenario=self.scenario,
            department='Marketing',
            category='Paid Ads',
            budget_amount=10000,
            actual_amount=12000,
            risk_rating='High',
        )

    def test_scenario_list(self):
        response = self.client.get(reverse('scenario-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['name'], 'Test Scenario')

    def test_chat_endpoint(self):
        url = reverse('scenario-chat', kwargs={'scenario_id': self.scenario.id})
        response = self.client.post(url, {'question': 'Which area is over budget?'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/event-stream')

    def test_summary_endpoint(self):
        url = reverse('scenario-summary', kwargs={'scenario_id': self.scenario.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['totals']['budget'], 10000)
        self.assertEqual(data['totals']['actual'], 12000)

    def test_high_risk_department_grouping_chat(self):
        BudgetLineItem.objects.create(
            scenario=self.scenario,
            department='Travel',
            category='Travel',
            budget_amount=15000,
            actual_amount=20000,
            risk_rating='Medium',
        )
        url = reverse('scenario-chat', kwargs={'scenario_id': self.scenario.id})
        response = self.client.get(
            url,
            {
                'question': 'Paid Ads Travel 15000 7500 High Medium Group this by department and show only high-risk items',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/event-stream')
        payload = b''.join(response.streaming_content).decode('utf-8')
        self.assertIn('event: message', payload)
        self.assertIn('event: table', payload)
        self.assertIn('Marketing', payload)
        self.assertNotIn('Travel', payload)
