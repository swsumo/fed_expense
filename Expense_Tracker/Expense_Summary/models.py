from django.db import models
from django.conf import settings  # ✅ Use custom user model

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ("Food", "Food"),
        ("Transport", "Transport"),
        ("Entertainment", "Entertainment"),
        ("Shopping", "Shopping"),
        ("Bills", "Bills"),
        ("Other", "Other"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    sub_category = models.CharField(max_length=100, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    is_recurring = models.BooleanField(default=False)
    recurring_interval = models.CharField(
        max_length=20, choices=[("Daily", "Daily"), ("Weekly", "Weekly"), ("Monthly", "Monthly")], blank=True, null=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.category}"

class Budget(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    monthly_budget = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username} - Budget: {self.monthly_budget}"
