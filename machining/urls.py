# urls.py

from django.urls import path
from .views import *

urlpatterns = [
    
    path('bulk-add/', BulkAddCncAPIView.as_view(), name='BulkAddCncAPIView'),
    path('machiningListAPIView/', machiningListAPIView.as_view(), name='machiningListAPIView'),
    path('export/', machiningExportAPIView.as_view(), name='machiningExportAPIView'),
    path('fields/', machiningFieldsAPIView.as_view(), name='machining-fields'),

    ]

