# urls.py

from django.urls import path
from .views import *

urlpatterns = [
    
    path('add/', DispatchListCreateAPIView.as_view(), name='DispatchListCreateAPIView'),
    path('DispatchListAPIView/', DispatchListAPIView.as_view(), name='DispatchListAPIView'),
    path('export/', DispatchExportAPIView.as_view(), name='DispatchExportAPIView'),
    path('fields/', DispatchFieldsAPIView.as_view(), name='DispatchFieldsAPIView-fields'),
]
