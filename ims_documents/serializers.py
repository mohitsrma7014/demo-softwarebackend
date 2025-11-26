
from rest_framework import serializers
from .models import ManualDocument, ProcedureDocument

class ManualDocumentSerializer(serializers.ModelSerializer):
    document_url = serializers.SerializerMethodField()
    uploaded_by = serializers.StringRelatedField()
    
    class Meta:
        model = ManualDocument
        fields = [
            'id', 'document_name', 'document_type', 
            'document_file', 'document_url', 'status',
            'created_at', 'updated_at', 'uploaded_by'
        ]
        read_only_fields = ['created_at', 'updated_at', 'uploaded_by']
    
    def get_document_url(self, obj):
        request = self.context.get('request')
        if obj.document_file and hasattr(obj.document_file, 'url'):
            return request.build_absolute_uri(obj.document_file.url)
        return None

    def validate_document_file(self, value):
        if not value.name.endswith('.pdf'):
            raise serializers.ValidationError("Only PDF files are allowed.")
        return value


class ProcedureDocumentSerializer(serializers.ModelSerializer):
    document_url = serializers.SerializerMethodField()
    uploaded_by = serializers.StringRelatedField()
    
    class Meta:
        model = ProcedureDocument
        fields = [
            'id', 'document_name', 'document_type', 
            'document_file', 'document_url', 'status',
            'created_at', 'updated_at', 'uploaded_by'
        ]
        read_only_fields = ['created_at', 'updated_at', 'uploaded_by']
    
    def get_document_url(self, obj):
        request = self.context.get('request')
        if obj.document_file and hasattr(obj.document_file, 'url'):
            return request.build_absolute_uri(obj.document_file.url)
        return None

    def validate_document_file(self, value):
        if not value.name.endswith('.pdf'):
            raise serializers.ValidationError("Only PDF files are allowed.")
        return value

class DocumentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    document_name = serializers.CharField()
    document_type = serializers.CharField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    uploaded_by = serializers.CharField(allow_null=True)
    document_file = serializers.FileField()
    
    def to_representation(self, instance):
        # Handle both Manual and Procedure documents
        return {
            'id': instance.id,
            'document_name': instance.document_name,
            'document_type': instance.get_document_type_display(),
            'type': 'manual' if isinstance(instance, ManualDocument) else 'procedure',
            'status': instance.status,
            'created_at': instance.created_at,
            'uploaded_by': instance.uploaded_by,
            'document_file': instance.document_file.url if instance.document_file else None
        }