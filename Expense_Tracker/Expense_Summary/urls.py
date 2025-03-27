from django.urls import path
from .views import expense_summary, delete_expense, reset_expenses, set_budget

urlpatterns = [
    path('', expense_summary, name='expense_summary'),
    path('delete/<int:expense_id>/', delete_expense, name='delete_expense'),
    path('reset/', reset_expenses, name='reset_expenses'),
    path('set-budget/', set_budget, name='set_budget'),
]
