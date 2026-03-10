# tracker/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('transactions/', views.transaction_list, name='transactions'),
    
    path('transactions/<int:pk>/', views.TransactionDetailView.as_view()),
    path('summary/',           views.SummaryView.as_view()),
    path('categories/',        views.CategoryListView.as_view()),
]

# expense_tracker/urls.py  (root)
from django.urls import path, include

urlpatterns = [
    path('api/', include('tracker.urls')),
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
]
