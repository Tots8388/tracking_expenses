from rest_framework import serializers
from .models import Transaction, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ['id', 'name']


class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model  = Transaction
        fields = [
            'id', 'amount', 'category', 'category_name',
            'type', 'date', 'description', 'created_at'
        ]
        read_only_fields = ['created_at']

    def validate_amount(self, value):
        # Always validate absolute value — sign is enforced in model.save()
        if abs(value) <= 0:
            raise serializers.ValidationError('Amount must be non-zero.')
        return value
    