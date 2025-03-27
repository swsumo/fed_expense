from django.shortcuts import render, redirect
from .models import Expense, Budget
from .forms import ExpenseForm, BudgetForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import datetime, timedelta


@login_required
def expense_summary(request):
    user = request.user
    expenses = Expense.objects.filter(user=user).order_by("-date_added")

    budget, created = Budget.objects.get_or_create(user=user)
    total_spent = expenses.aggregate(Sum("amount"))["amount__sum"] or 0

    budget_alert = None
    if budget.monthly_budget and total_spent > 0:
        spent_percentage = (total_spent / budget.monthly_budget) * 100
        if spent_percentage >= 80:
            budget_alert = f" You have spent {spent_percentage:.2f}% of your budget!"

    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = user
            expense.save()
            return redirect("expense_summary")

    form = ExpenseForm()
    budget_form = BudgetForm(instance=budget)

    return render(
        request,
        "Expense_Summary/summary_index.html",
        {
            "expenses": expenses,
            "form": form,
            "budget_form": budget_form,
            "budget": budget,
            "total_spent": total_spent,
            "budget_alert": budget_alert,
        },
    )

@login_required
def reset_expenses(request):
    """Delete all expenses for the logged-in user."""
    Expense.objects.filter(user=request.user).delete()
    return redirect("expense_summary")

@login_required
def delete_expense(request, expense_id):
    """Delete a single expense."""
    Expense.objects.filter(id=expense_id, user=request.user).delete()
    return redirect("expense_summary")

@login_required
def set_budget(request):
    """Handles setting the user's monthly budget."""
    if request.method == "POST":
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget, created = Budget.objects.get_or_create(user=request.user)
            budget.monthly_budget = form.cleaned_data["monthly_budget"]
            budget.save()
            return redirect("expense_summary")  
    else:
        form = BudgetForm()

    return render(request, "Expense_Summary/set_budget.html", {"form": form})
