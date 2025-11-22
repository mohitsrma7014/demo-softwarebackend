from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import marking
class MarkingResource(resources.ModelResource):

    class Meta:
        model = marking
        skip_unchanged = True
        report_skipped = True
        fields = (
            'id', 'batch_number', 'date', 'machine', 'operator', 'shift', 'component',
            'qty', 'verified_by', 'heat_no', 'target', 'total_produced', 'remaining'
        )


# ------------------ ADMIN CONFIG ------------------

@admin.register(marking)
class MarkingAdmin(ImportExportModelAdmin):
    resource_class = MarkingResource
    list_display = (
        'batch_number', 'date', 'shift', 'component', 'machine',
        'qty', 'target', 'total_produced', 'remaining', 'verified_by'
    )
    list_filter = ('shift', 'machine', 'component', 'verified_by', 'date')
    search_fields = ('batch_number', 'component', 'machine', 'operator', 'heat_no')
    ordering = ('-date',)