# urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('bulk-add/', BulkAddHeattreatmentAPIView.as_view(), name='BulkAddHeattreatmentAPIView'),
    path('HeatTreatmentListAPIView/', HeatTreatmentListAPIView.as_view(), name='HeatTreatmentListAPIView'),
    path('export/', HeatTreatmentExportAPIView.as_view(), name='HeatTreatmentExportAPIView'),
    path('fields/', HeatTreatmentFieldsAPIView.as_view(), name='ht-fields'),
]
