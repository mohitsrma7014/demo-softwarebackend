# masters/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('bulk-add/', BulkAddForgingAPIView.as_view(), name='bulk_add_forging'),
    path('ForgingListAPIView/', ForgingListAPIView.as_view(), name='ForgingListAPIView'),
    path('export/', ForgingExportAPIView.as_view(), name='ForgingExportAPIView'),
    path('fields/', ForgingFieldsAPIView.as_view(), name='forging-fields'),
    path('dashboard/', ForgingDashboardAPIView.as_view(), name='ForgingDashboardAPIView'),


]
