import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Transaction, Category
from .serializers import TransactionSerializer, CategorySerializer
from .forms import TransactionForm


# ── REST API Views ──

class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class   = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs    = Transaction.objects.filter(user=self.request.user)
        ttype = self.request.query_params.get('type')
        cat   = self.request.query_params.get('category')
        month = self.request.query_params.get('month')
        year  = self.request.query_params.get('year')
        if ttype: qs = qs.filter(type=ttype)
        if cat:   qs = qs.filter(category__name__icontains=cat)
        if month: qs = qs.filter(date__year=month[:4], date__month=month[5:])
        if year:  qs = qs.filter(date__year=year)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class SummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs    = Transaction.objects.filter(user=request.user)
        month = request.query_params.get('month')
        year  = request.query_params.get('year')
        if month: qs = qs.filter(date__year=month[:4], date__month=month[5:])
        if year:  qs = qs.filter(date__year=year)

        amounts       = [float(t.amount) for t in qs]
        balance       = sum(amounts)
        total_income  = sum(a for a in amounts if a > 0)
        total_expense = abs(sum(a for a in amounts if a < 0))
        total_volume  = sum(abs(a) for a in amounts)

        return Response({
            'balance':       balance,
            'total_income':  total_income,
            'total_expense': total_expense,
            'total_volume':  total_volume,
        })


class CategoryListView(generics.ListCreateAPIView):
    serializer_class   = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset           = Category.objects.all()


# ── Helper ──

def _build_financials(qs):
    amounts       = [float(t.amount) for t in qs]
    balance       = sum(amounts)
    total_income  = sum(a for a in amounts if a > 0)
    total_expense = abs(sum(a for a in amounts if a < 0))
    total_volume  = sum(abs(a) for a in amounts)

    running = 0
    balance_points  = []
    transaction_log = []

    for tx in qs:
        running += float(tx.amount)
        balance_points.append({'x': str(tx.date), 'y': round(running, 2)})
        transaction_log.append({
            'date':        str(tx.date),
            'description': tx.description or '',
            'category':    tx.category.name if tx.category else 'Uncategorized',
            'type':        tx.type,
            'amount':      float(tx.amount),
            'balance':     round(running, 2),
        })

    return {
        'balance':       balance,
        'total_income':  total_income,
        'total_expense': total_expense,
        'total_volume':  total_volume,
        'balance_points':  balance_points,
        'transaction_log': transaction_log,
    }

def signup_view(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Account created! You can now log in.')
        return redirect('login')
    return render(request, 'registration/signup.html', {'form': form})

# ── Template Views ──

@login_required
def dashboard(request):
    month = request.GET.get('month', '')
    qs    = Transaction.objects.filter(user=request.user).order_by('date', 'created_at')
    if month:
        qs = qs.filter(date__year=month[:4], date__month=month[5:])

    fin = _build_financials(qs)

    by_cat = (qs.filter(type='expense')
               .values('category__name')
               .annotate(total=Sum('amount'))
               .order_by('total'))
    pie_data = {
        'labels': [r['category__name'] or 'Uncategorized' for r in by_cat],
        'values': [abs(float(r['total'])) for r in by_cat],
    }

    return render(request, 'dashboard.html', {
        'summary': {
            'total_income':  fin['total_income'],
            'total_expense': fin['total_expense'],
            'balance':       fin['balance'],
            'total_volume':  fin['total_volume'],
        },
        'pie_data':        json.dumps(pie_data),
        'balance_points':  json.dumps(fin['balance_points']),
        'transaction_log': json.dumps(fin['transaction_log']),
        'selected_month':  month,
    })


@login_required
def transaction_list(request):
    qs    = Transaction.objects.filter(user=request.user).order_by('-date', '-created_at')
    ttype = request.GET.get('type')
    month = request.GET.get('month')
    if ttype: qs = qs.filter(type=ttype)
    if month: qs = qs.filter(date__year=month[:4], date__month=month[5:])

    fin = _build_financials(qs)

    return render(request, 'transactions.html', {
        'transactions':  qs,
        'total_income':  fin['total_income'],
        'total_expense': fin['total_expense'],
        'balance':       fin['balance'],
        'total_volume':  fin['total_volume'],
    })


@login_required
def transaction_add(request):
    form = TransactionForm(request.POST or None)
    if form.is_valid():
        tx      = form.save(commit=False)
        tx.user = request.user
        tx.save()
        messages.success(request, 'Transaction added successfully.')
        return redirect('transaction_list')
    return render(request, 'transaction_form.html', {'form': form, 'title': 'Add Transaction'})


@login_required
def transaction_edit(request, pk):
    tx   = get_object_or_404(Transaction, pk=pk, user=request.user)
    form = TransactionForm(request.POST or None, instance=tx)
    if form.is_valid():
        form.save()
        messages.success(request, 'Transaction updated.')
        return redirect('transaction_list')
    return render(request, 'transaction_form.html', {'form': form, 'title': 'Edit Transaction'})


@login_required
def transaction_delete(request, pk):
    tx = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        tx.delete()
        messages.success(request, 'Transaction deleted.')
        return redirect('transaction_list')
    return render(request, 'transaction_confirm_delete.html', {'tx': tx})