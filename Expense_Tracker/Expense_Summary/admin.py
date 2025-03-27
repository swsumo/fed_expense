from django.contrib import admin
from .models import Expense, Budget

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["user", "amount", "category", "date_added", "is_recurring"]
    list_filter = ["category", "is_recurring", "date_added"]
    search_fields = ["user__username", "category", "sub_category"]

class BudgetAdmin(admin.ModelAdmin):
    list_display = ["user", "monthly_budget"]
    search_fields = ["user__username"]

admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Budget, BudgetAdmin)
