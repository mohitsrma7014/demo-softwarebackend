from django.db import models

# Create your models here.

from django.db import models
from django.utils import timezone

class ManualDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('manual', 'Manual'),
    ]
    
    document_name = models.CharField(max_length=255)
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES,
        default='manual'
    )
    document_file = models.FileField(upload_to='manuals/')  # Removed FileExtensionValidator
    status = models.CharField(
        max_length=20,
        choices=[('current', 'Current'), ('old', 'Old')],
        default='current'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Manual Document'
        verbose_name_plural = 'Manual Documents'

    def __str__(self):
        return f"{self.document_name} ({self.get_document_type_display()})"
class ProcedureDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('engineering', 'Engineering'),
        ('npd', 'NPD'),
        ('forging', 'Forging'),
        ('tool_room', 'Tool Room'),
        ('machining_division', 'Machining Division'),
        ('metallurgy_ht', 'Metallurgy & HT'),
        ('maintenance', 'Maintenance'),
        ('purchase', 'Purchase'),
        ('store_dispatch', 'Store and Dispatch'),
        ('qa', 'QA'),
        ('hr', 'HR'),
        ('mr', 'MR'),
        ('sales_marketing', 'Sales and Marketing'),
    ]
    
    document_name = models.CharField(max_length=255)
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES
    )
    document_file = models.FileField(upload_to='procedures/')  # Removed FileExtensionValidator
    status = models.CharField(
        max_length=20,
        choices=[('current', 'Current'), ('old', 'Old')],
        default='current'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Procedure Document'
        verbose_name_plural = 'Procedure Documents'

    def __str__(self):
        return f"{self.document_name} ({self.get_document_type_display()})"