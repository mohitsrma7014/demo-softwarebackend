# urls.py

from django.urls import path
from .views import *
urlpatterns = [
   
    path('bulk-add/', BulkAddpre_mcAPIView.as_view(), name='BulkAddpre_mcAPIView'),
    path('pre_mcListAPIView/', pre_mcListAPIView.as_view(), name='pre_mcListAPIView'),
    path('export/', pre_mcExportAPIView.as_view(), name='pre_mcExportAPIView'),
    path('fields/', pre_mcFieldsAPIView.as_view(), name='Pre_mc-fields'),
]