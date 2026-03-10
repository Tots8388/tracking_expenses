from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Q
from django.utils.dateparse import parse_date
from .models import Transaction, Category
from .serializers import TransactionSerializer, CategorySerializer


class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class   = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs    = Transaction.objects.filter(user=self.request.user)
        ttype = self.request.query_params.get('type')
        cat   = self.request.query_params.get('category')
        month = self.request.query_params.get('month')  # YYYY-MM
        year  = self.request.query_params.get('year')   # YYYY
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
        qs = Transaction.objects.filter(user=request.user)
        month = request.query_params.get('month')
        year  = request.query_params.get('year')
        if month: qs = qs.filter(date__year=month[:4], date__month=month[5:])
        if year:  qs = qs.filter(date__year=year)

        total_income  = qs.filter(type='income') .aggregate(s=Sum('amount'))['s'] or 0
        total_expense = qs.filter(type='expense').aggregate(s=Sum('amount'))['s'] or 0

        by_category = (
            qs.filter(type='expense')
              .values('category__name')
              .annotate(total=Sum('amount'))
              .order_by('-total')
        )

        return Response({
            'total_income':  float(total_income),
            'total_expense': float(total_expense),
            'balance':       float(total_income - total_expense),
            'by_category':   list(by_category),
        })


class CategoryListView(generics.ListCreateAPIView):
    serializer_class   = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset           = Category.objects.all()

import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models.functions import TruncMonth

@login_required
def dashboard(request):
    month = request.GET.get('month', '')
    qs = Transaction.objects.filter(user=request.user)
    if month:
        qs = qs.filter(date__year=month[:4], date__month=month[5:])

    # Summary
    total_income  = qs.filter(type='income') .aggregate(s=Sum('amount'))['s'] or 0
    total_expense = qs.filter(type='expense').aggregate(s=Sum('amount'))['s'] or 0
    summary = {
        'total_income':  total_income,
        'total_expense': total_expense,
        'balance':       total_income - total_expense,
    }

    # Pie chart data
    by_cat  = (qs.filter(type='expense')
               .values('category__name')
               .annotate(total=Sum('amount'))
               .order_by('-total'))
    pie_data = {
        'labels': [r['category__name'] or 'Uncategorized' for r in by_cat],
        'values': [float(r['total']) for r in by_cat],
    }

    # Bar chart: last 6 months
    all_qs = Transaction.objects.filter(user=request.user)
    monthly = (all_qs.annotate(month=TruncMonth('date'))
                     .values('month', 'type')
                     .annotate(total=Sum('amount'))
                     .order_by('month'))
    months, income_vals, expense_vals = {}, {}, {}
    for row in monthly:
        lbl = row['month'].strftime('%b %Y')
        months[lbl] = True
        if row['type'] == 'income':  income_vals[lbl]  = float(row['total'])
        if row['type'] == 'expense': expense_vals[lbl] = float(row['total'])
    labels = sorted(months.keys())[-6:]
    bar_data = {
        'labels':  labels,
        'income':  [income_vals.get(l, 0)  for l in labels],
        'expense': [expense_vals.get(l, 0) for l in labels],
    }

    return render(request, 'dashboard.html', {
        'summary':        summary,
        'pie_data':       json.dumps(pie_data),
        'bar_data':       json.dumps(bar_data),
        'selected_month': month,
    })
