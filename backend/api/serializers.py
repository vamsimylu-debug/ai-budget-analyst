from rest_framework import serializers
from .models import BudgetScenario, BudgetLineItem

class BudgetLineItemSerializer(serializers.ModelSerializer):
    variance = serializers.SerializerMethodField()

    class Meta:
        model = BudgetLineItem
        fields = [
            'id',
            'scenario',
            'department',
            'category',
            'budget_amount',
            'actual_amount',
            'variance',
            'risk_rating',
            'notes',
        ]

    def get_variance(self, obj):
        return obj.variance()

class BudgetScenarioSerializer(serializers.ModelSerializer):
    line_items = BudgetLineItemSerializer(many=True, read_only=True)

    class Meta:
        model = BudgetScenario
        fields = ['id', 'name', 'period', 'description', 'created_at', 'line_items']
