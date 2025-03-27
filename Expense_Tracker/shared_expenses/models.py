from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db.models import Sum

    

class ExpenseGroup(models.Model):
    """Group for shared expenses"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="admin_groups"
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name="expense_groups"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_total_expenses(self):
        return self.expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    def get_member_count(self):
        return self.members.count()

    class Meta:
        ordering = ['-created_at']


class GroupExpense(models.Model):
    """Expense inside a shared group"""
    group = models.ForeignKey(
        ExpenseGroup, 
        on_delete=models.CASCADE, 
        related_name="expenses"
    )
    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="paid_expenses"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255)
    date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Split types
    EQUAL = 'EQUAL'
    UNEQUAL = 'UNEQUAL'
    PERCENTAGE = 'PERCENTAGE'
    SPLIT_TYPES = [
        (EQUAL, 'Equal'),
        (UNEQUAL, 'Unequal'),
        (PERCENTAGE, 'Percentage'),
    ]
    split_type = models.CharField(
        max_length=10,
        choices=SPLIT_TYPES,
        default=EQUAL,
    )

    def __str__(self):
        return f"{self.description} - ${self.amount} ({self.group.name})"

    def get_absolute_url(self):
        return reverse('expense_detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['-date']


class ExpenseSplit(models.Model):
    """Tracks how much each member owes for an expense"""
    expense = models.ForeignKey(
        GroupExpense, 
        on_delete=models.CASCADE, 
        related_name="splits"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="owed_expenses"
    )
    amount_owed = models.DecimalField(max_digits=12, decimal_places=2)
    is_settled = models.BooleanField(default=False)
    settled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} owes ${self.amount_owed} for {self.expense.description}"

    class Meta:
        unique_together = ('expense', 'user')


class DebtSettlement(models.Model):
    """Tracks debt settlements between users"""
    group = models.ForeignKey(
        ExpenseGroup, 
        on_delete=models.CASCADE, 
        related_name="debt_settlements"
    )
    debtor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="debts_paid"
    )
    creditor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="debts_received"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.debtor.username} paid {self.creditor.username} ${self.amount}"

    class Meta:
        ordering = ['-date']