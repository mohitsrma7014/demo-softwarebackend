# urls.py

from django.urls import path
from .views import *

urlpatterns = [
    
    path('bulk-add/', BulkAddmarkingAPIView.as_view(), name='BulkAddmarkingAPIView'),
    path('MarkingListAPIView/', MarkingListAPIView.as_view(), name='MarkingListAPIView'),
    path('export/', markingExportAPIView.as_view(), name='markingExportAPIView'),
    path('fields/', MarkingFieldsAPIView.as_view(), name='MarkingFieldsAPIView-fields'),
]
