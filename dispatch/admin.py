from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import dispatch

# Define the resource for import/export
class DispatchResource(resources.ModelResource):
    class Meta:
        model = dispatch
        fields = (
            'id',
            'date',
            'component',
            'pices',
            'invoiceno',
            'addpdf',
            'verified_by',
            'heat_no',
            'target1',
            'total_produced',
            'remaining',
            'batch_number',
            'price',
        )
        export_order = fields  # Keeps export order same as defined above

# Register the model with ImportExport functionality
@admin.register(dispatch)
class DispatchAdmin(ImportExportModelAdmin):
    resource_class = DispatchResource
    list_display = (
        'date',
        'component',
        'pices',
        'invoiceno',
        'batch_number',
        'heat_no',
        'verified_by',
        'target1',
        'total_produced',
        'remaining',
        'price',
    )
    search_fields = ('component', 'invoiceno', 'batch_number', 'heat_no')
    list_filter = ('date', 'component', 'verified_by')

