from django.db import models

class BudgetScenario(models.Model):
    name = models.CharField(max_length=180)
    period = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.period})"

class BudgetLineItem(models.Model):
    scenario = models.ForeignKey(BudgetScenario, related_name='line_items', on_delete=models.CASCADE)
    department = models.CharField(max_length=120)
    category = models.CharField(max_length=120)
    budget_amount = models.DecimalField(max_digits=14, decimal_places=2)
    actual_amount = models.DecimalField(max_digits=14, decimal_places=2)
    notes = models.TextField(blank=True)
    risk_rating = models.CharField(max_length=32, blank=True)

    def variance(self):
        return self.actual_amount - self.budget_amount

    def __str__(self):
        return f"{self.department} / {self.category}"
