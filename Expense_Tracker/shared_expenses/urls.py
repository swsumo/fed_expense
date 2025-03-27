from django.urls import path
from . import views
from .views import group_management

urlpatterns = [
    # Main SPA entry point
    path('group-management/', group_management, name='group_management'),

    # API Endpoints (for form submissions)
    path('api/groups/<int:group_id>/add-expense/', views.add_expense, name='api_add_expense'),
    path('api/expenses/<int:expense_id>/edit/', views.edit_expense, name='api_edit_expense'),
    path('api/expenses/<int:expense_id>/delete/', views.delete_expense, name='api_delete_expense'),
    path('api/settlements/<int:settlement_id>/verify/', views.verify_settlement, name='api_verify_settlement'),
    path('groups/create/', views.create_group, name='create_group'),
    path('groups/<int:group_id>/add_member/', views.add_member, name='add_member'),
    path('expenses/add/', views.add_expense, name='add_expense'),
    
]