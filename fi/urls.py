# urls.py

from django.urls import path
from .views import *

urlpatterns = [
   
    path('bulk-add/', BulkAddFiAPIView.as_view(), name='BulkAddFiAPIView'),
    path('FiListAPIView/', FiListAPIView.as_view(), name='FiListAPIView'),
    path('export/', FiExportAPIView.as_view(), name='FiExportAPIView'),
    path('fields/', FiFieldsAPIView.as_view(), name='FiFieldsAPIView-fields'),
]
