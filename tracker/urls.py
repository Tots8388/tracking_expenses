from django.urls import path
from . import views
from tracker.views import signup_view

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/add/', views.transaction_add, name='transaction_add'),
    path('transactions/<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    path('reports/', views.reports, name='reports'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('settings/notifications/', views.notification_settings, name='notification_settings'),
    path('signup/', signup_view, name='signup'),
]