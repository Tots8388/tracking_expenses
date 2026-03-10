from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Transaction, Category
import datetime

class TransactionAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user   = User.objects.create_user('testuser', password='pass1234')
        self.client.force_authenticate(user=self.user)
        self.cat = Category.objects.create(name='Food')

    def _make_tx(self, amount=100, ttype='expense'):
        return Transaction.objects.create(
            user=self.user, amount=amount, category=self.cat,
            type=ttype, date=datetime.date.today(), description='test'
        )

    def test_create_transaction(self):
        data = {'amount': 500, 'category': self.cat.id,
                'type': 'income', 'date': '2025-06-01', 'description': 'Salary'}
        r = self.client.post('/api/transactions/', data)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 1)

    def test_list_transactions(self):
        self._make_tx(200)
        self._make_tx(300)
        r = self.client.get('/api/transactions/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.data), 2)

    def test_update_transaction(self):
        tx = self._make_tx()
        r  = self.client.patch(f'/api/transactions/{tx.id}/', {'amount': 999})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        tx.refresh_from_db()
        self.assertEqual(float(tx.amount), 999)

    def test_delete_transaction(self):
        tx = self._make_tx()
        r  = self.client.delete(f'/api/transactions/{tx.id}/')
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Transaction.objects.count(), 0)

    def test_summary(self):
        self._make_tx(1000, 'income')
        self._make_tx(400,  'expense')
        r = self.client.get('/api/summary/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['balance'], 600.0)

    def test_other_user_cannot_access(self):
        tx    = self._make_tx()
        other = User.objects.create_user('other', password='pass')
        self.client.force_authenticate(user=other)
        r = self.client.get(f'/api/transactions/{tx.id}/')
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)
