from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import pre_mc


# Resource for import/export functionality
class PreMcResource(resources.ModelResource):
    class Meta:
        model = pre_mc
        fields = (
            'id',
            'batch_number',
            'date',
            'heat_no',
            'customer',
            'component',
            'qty',
            'shop_floor',
            'target',
            'total_produced',
            'remaining',
            'verified_by',
        )


# Register model in admin with import/export support
@admin.register(pre_mc)
class PreMcAdmin(ImportExportModelAdmin):
    resource_class = PreMcResource
    list_display = (
        'id',
        'batch_number',
        'date',
        'heat_no',
        'customer',
        'component',
        'qty',
        'shop_floor',
        'target',
        'total_produced',
        'remaining',
        'verified_by',
    )
    search_fields = ('batch_number', 'component', 'customer', 'shop_floor')
    list_filter = ('shop_floor', 'date', 'customer')
