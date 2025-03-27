from django import forms
from .models import Expense, Budget

class ExpenseForm(forms.ModelForm):
    SUBCATEGORY_CHOICES = [
        ("food", "Food"),
        ("transportation", "Transportation"),
        ("education", "Education"),
        ("utilities", "Utilities"),
        ("entertainment", "Entertainment"),
        ("groceries", "Groceries"),
        ("fitness", "Fitness"),
        ("health", "Health"),
        ("housing", "Housing"),
        ("shopping", "Shopping"),
        ("fuel", "Fuel"),
        ("dining", "Dining"),
        ("travel", "Travel"),
        ("personal_care", "Personal Care"),
        ("gifts", "Gifts"),
        ("donations", "Donations"),
        ("sports", "Sports"),
        ("electronics", "Electronics"),
        ("grooming", "Grooming"),
        ("income", "Income"),
    ]

    sub_category = forms.ChoiceField(choices=SUBCATEGORY_CHOICES, widget=forms.Select(attrs={"class": "form-select"}))

    class Meta:
        model = Expense
        fields = ["amount", "category", "sub_category", "is_recurring", "recurring_interval"]
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "recurring_interval": forms.Select(attrs={"class": "form-select"}),
        }

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ["monthly_budget"]
