from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import machining


# Resource for import/export
class MachiningResource(resources.ModelResource):
    class Meta:
        model = machining
        fields = (
            'id',
            'batch_number',
            'date',
            'shift',
            'component',
            'machine_no',
            'mc_type',
            'operator',
            'inspector',
            'setup',
            'target',
            'production',
            'remark',
            'cnc_height',
            'cnc_od',
            'cnc_bore',
            'cnc_groove',
            'cnc_dent',
            'forging_height',
            'forging_od',
            'forging_bore',
            'forging_crack',
            'forging_dent',
            'pre_mc_height',
            'pre_mc_od',
            'pre_mc_bore',
            'rework_height',
            'rework_od',
            'rework_bore',
            'rework_groove',
            'rework_dent',
            'verified_by',
            'heat_no',
            'target1',
            'total_produced',
            'remaining',
        )


# Register with admin
@admin.register(machining)
class MachiningAdmin(ImportExportModelAdmin):
    resource_class = MachiningResource

    list_display = (
        'id', 'batch_number', 'date', 'shift', 'component', 'machine_no',
        'mc_type', 'operator', 'inspector', 'production', 'total_produced',
        'remaining', 'verified_by'
    )

    search_fields = ('batch_number', 'component', 'machine_no', 'operator', 'inspector', 'heat_no')
    list_filter = ('shift', 'mc_type', 'machine_no', 'date')
    ordering = ('-date', '-id')
