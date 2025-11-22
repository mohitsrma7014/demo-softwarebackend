
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Visual


class VisualResource(resources.ModelResource):

    class Meta:
        model = Visual
        skip_unchanged = True
        report_skipped = True
        fields = (
            'id', 'batch_number', 'date', 'shift', 'component', 'target', 'chaker',
            'production', 'remark', 'cnc_height', 'cnc_od', 'cnc_bore', 'cnc_groove','cnc_rust', 
            'cnc_dent', 'forging_height', 'forging_od', 'forging_bore', 'forging_crack', 
            'forging_dent', 'pre_mc_height', 'pre_mc_od', 'pre_mc_bore',
            'rework_height', 'rework_od', 'rework_bore', 'rework_groove',
            'rework_dent',  'verified_by', 'heat_no','marking',
            'target1', 'total_produced', 'remaining'
        )


# ------------------ ADMIN CONFIG ------------------

@admin.register(Visual)
class VisualAdmin(ImportExportModelAdmin):
    resource_class = VisualResource
    list_display = (
        'batch_number', 'date', 'shift', 'component', 'production', 
        'target', 'total_produced', 'remaining', 'verified_by'
    )
    list_filter = ('shift', 'component', 'verified_by', 'date')
    search_fields = ('batch_number', 'component', 'heat_no', 'verified_by')
    ordering = ('-date',)