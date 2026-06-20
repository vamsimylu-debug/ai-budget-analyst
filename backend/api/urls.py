from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import BudgetScenarioViewSet, BudgetLineItemViewSet, budget_summary, scenario_chat

router = DefaultRouter()
router.register(r'scenarios', BudgetScenarioViewSet, basename='scenario')
router.register(r'line-items', BudgetLineItemViewSet, basename='lineitem')

urlpatterns = [
    path('', include(router.urls)),
    path('scenarios/<int:scenario_id>/summary/', budget_summary, name='scenario-summary'),
    path('scenarios/<int:scenario_id>/chat/', scenario_chat, name='scenario-chat'),
]
