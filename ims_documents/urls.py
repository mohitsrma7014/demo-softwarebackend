from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'manuals', ManualDocumentViewSet, basename='manual')
router.register(r'procedures', ProcedureDocumentViewSet, basename='procedure')
router.register(r'current-documents', CurrentDocumentsViewSet, basename='current-documents')
urlpatterns = [
    
    path('', include(router.urls)),
]
