from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    INCOME  = 'income'
    EXPENSE = 'expense'
    TYPE_CHOICES = [(INCOME, 'Income'), (EXPENSE, 'Expense')]

    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount      = models.DecimalField(max_digits=12, decimal_places=2)
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    type        = models.CharField(max_length=10, choices=TYPE_CHOICES)
    date        = models.DateField()
    description = models.CharField(max_length=255, blank=True)
    receipt     = models.ImageField(upload_to='receipts/', null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'created_at']

    def save(self, *args, **kwargs):
        if self.type == 'expense':
            self.amount = -abs(self.amount)
        else:
            self.amount = abs(self.amount)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.type}: {self.amount} ({self.date})'


class EmailNotificationPreference(models.Model):
    user               = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_prefs')
    weekly_summary     = models.BooleanField(default=True)
    budget_alerts      = models.BooleanField(default=True)
    large_expense_alert = models.BooleanField(default=True)
    large_expense_threshold = models.DecimalField(max_digits=12, decimal_places=2, default=1000)

    def __str__(self):
        return f'Notification prefs for {self.user.username}'