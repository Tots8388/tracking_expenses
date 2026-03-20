from django.contrib import admin
from .models import Transaction, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'type', 'category', 'date', 'description']
    list_filter = ['type', 'category', 'date']
    search_fields = ['description', 'user__username']
    ordering = ['-date']