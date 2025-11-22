from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import HeatTreatment


# Define Resource for import/export
class HeatTreatmentResource(resources.ModelResource):
    class Meta:
        model = HeatTreatment
        fields = (
            'id',
            'batch_number',
            'date',
            'shift',
            'process',
            'component',
            'furnace',
            'supervisor',
            'operator',
            'remark',
            'ringweight',
            'production',
            'cycle_time',
            'unit',
            'heat_no',
            'target',
            'total_produced',
            'remaining',
            'hardness',
            'micro',
            'grain_size',
            'verified_by',
        )


# Register admin
@admin.register(HeatTreatment)
class HeatTreatmentAdmin(ImportExportModelAdmin):
    resource_class = HeatTreatmentResource
    list_display = (
        'id', 'batch_number', 'date', 'shift', 'process',
        'component', 'furnace', 'supervisor', 'operator',
        'production', 'total_produced', 'remaining', 'verified_by'
    )
    search_fields = ('batch_number', 'component', 'furnace', 'operator', 'supervisor')
    list_filter = ('shift', 'process', 'furnace', 'date')
