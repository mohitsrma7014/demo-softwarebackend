from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import ManualDocument, ProcedureDocument
from .serializers import ManualDocumentSerializer, ProcedureDocumentSerializer

class ManualDocumentViewSet(viewsets.ModelViewSet):
    queryset = ManualDocument.objects.all()
    serializer_class = ManualDocumentSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'document_type']
    search_fields = ['document_name']
    ordering_fields = ['created_at', 'updated_at', 'document_name']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class ProcedureDocumentViewSet(viewsets.ModelViewSet):
    queryset = ProcedureDocument.objects.all()
    serializer_class = ProcedureDocumentSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'document_type']
    search_fields = ['document_name']
    ordering_fields = ['created_at', 'updated_at', 'document_name']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

from .serializers import DocumentSerializer

class CurrentDocumentsViewSet(viewsets.ViewSet):
    def list(self, request):
        # Get current manual documents
        manuals = ManualDocument.objects.filter(status='current')
        # Get current procedure documents
        procedures = ProcedureDocument.objects.filter(status='current')
        
        # Combine and serialize
        all_documents = list(manuals) + list(procedures)
        serializer = DocumentSerializer(all_documents, many=True)
        
        return Response(serializer.data)