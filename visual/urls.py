# urls.py

from django.urls import path
from .views import *

urlpatterns = [
    
    path('bulk-add/', BulkAddVisualAPIView.as_view(), name='BulkAddVisualAPIView'),
    path('VisualListAPIView/', VisualListAPIView.as_view(), name='VisualListAPIView'),
    path('export/', VisualExportAPIView.as_view(), name='VisualExportAPIView'),
    path('fields/', VisualFieldsAPIView.as_view(), name='FiFieldsAPIVVisualFieldsAPIViewiew-fields'),
]
