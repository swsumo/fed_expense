from django import forms
from .models import ExpenseGroup, GroupExpense, DebtSettlement
from django.contrib.auth import get_user_model

User = get_user_model()

class ExpenseGroupForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = ExpenseGroup
        fields = ['name', 'description', 'members']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['members'].queryset = User.objects.exclude(id=user.id)


class GroupExpenseForm(forms.ModelForm):
    split_type = forms.ChoiceField(
        choices=GroupExpense.SPLIT_TYPES,
        initial=GroupExpense.EQUAL,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = GroupExpense
        fields = ['amount', 'description', 'split_type']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }


class DebtSettlementForm(forms.ModelForm):
    class Meta:
        model = DebtSettlement
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class AddMemberForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text="Enter the email of the user you want to add"
    )