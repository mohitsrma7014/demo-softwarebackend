from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Forging
from import_export import resources

# Create a resource class for import/export
class ForgingResource(resources.ModelResource):
    class Meta:
        model = Forging
        import_id_fields = []  # allow all imports as new
        fields = (
            'batch_number', 'date', 'shift', 'component', 'customer', 'slug_weight',
            'rm_grade', 'heat_number', 'line', 'line_incharge', 'forman',
            'target', 'production', 'rework', 'up_setting', 'half_piercing',
            'full_piercing', 'ring_rolling', 'sizing', 'overheat', 'bar_crack_pcs',
            'verified_by', 'machine_status', 'downtime_minutes',
            'reason_for_downtime', 'reason_for_low_production'
        )

# Register with import/export
@admin.register(Forging)
class ForgingAdmin(ImportExportModelAdmin):
    resource_class = ForgingResource
    list_display = ('batch_number', 'date', 'shift', 'component', 'customer', 'production', 'verified_by')
    search_fields = ('batch_number', 'component', 'customer', 'line')
    list_filter = ('shift', 'line', 'machine_status', 'date')
