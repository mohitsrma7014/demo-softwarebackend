from django.contrib import admin
from import_export import resources,fields,widgets
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget, DateTimeWidget
from django.db.models import Sum
from .models import Supplier, Grade, Customer, TypeOfMaterial, Location

# ---- Resources ----
class SupplierResource(resources.ModelResource):
    class Meta:
        model = Supplier
        fields = ('id', 'name', 'delivery_days', 'supplier_details', 'supplier_gstin')

class GradeResource(resources.ModelResource):
    class Meta:
        model = Grade
        fields = ('id', 'name')

class CustomerResource(resources.ModelResource):
    class Meta:
        model = Customer
        fields = ('id', 'name')

class TypeOfMaterialResource(resources.ModelResource):
    class Meta:
        model = TypeOfMaterial
        fields = ('id', 'name')

class LocationResource(resources.ModelResource):
    class Meta:
        model = Location
        fields = ('id', 'name')


# ---- Admin Classes ----
@admin.register(Supplier)
class SupplierAdmin(ImportExportModelAdmin):
    resource_class = SupplierResource
    list_display = ('name', 'delivery_days', 'supplier_gstin')
    search_fields = ('name', 'supplier_gstin')
    list_filter = ('delivery_days',)

@admin.register(Grade)
class GradeAdmin(ImportExportModelAdmin):
    resource_class = GradeResource
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Customer)
class CustomerAdmin(ImportExportModelAdmin):
    resource_class = CustomerResource
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(TypeOfMaterial)
class TypeOfMaterialAdmin(ImportExportModelAdmin):
    resource_class = TypeOfMaterialResource
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Location)
class LocationAdmin(ImportExportModelAdmin):
    resource_class = LocationResource
    list_display = ('name',)
    search_fields = ('name',)

from .models import RMReceiving, HoldMaterial, BatchTracking


# -------------------- Resources --------------------

class RMReceivingResource(resources.ModelResource):
    class Meta:
        model = RMReceiving
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ('uid',)
        fields = (
            'id','uid', 'date', 'supplier', 'grade', 'dia', 'customer',
            'standerd', 'heatno', 'reciving_weight_kg', 'hold_weight_kg',
            'remaining', 'rack_no', 'location', 'type_of_material',
            'cost_per_kg', 'invoice_no', 'approval_status', 'verified_by','milltc','spectro','ssb_inspection_report','customer_approval',
            'status', 'comments',
        )


class HoldMaterialResource(resources.ModelResource):
    
    class Meta:
        model = HoldMaterial
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ('batch_id',)
        fields = (
            'batch_id', 'component', 'customer', 'supplier', 'grade',
            'standerd', 'heatno', 'dia', 'rack_no', 'pieces',
            'hold_material_qty_kg', 'remaining', 'line', 'status',
            'verified_by', 'created_at', 'rm_receiving',
        )
    # ✅ 1️⃣ After import hook — update all RMReceiving stats
    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        if dry_run:
            return  # Skip during test run

        # 🔹 Find all unique heat numbers in the imported data
        heatnos = set(dataset['heatno'])

        for heat in heatnos:
            # 🔹 Sum total hold qty for this heatno
            total_hold = HoldMaterial.objects.filter(heatno=heat).aggregate(
                total=Sum('hold_material_qty_kg')
            )['total'] or 0

            # 🔹 Find all corresponding RMReceiving rows for this heatno
            matching_receivings = RMReceiving.objects.filter(heatno=heat)

            if not matching_receivings.exists():
                continue  # skip if no matching RMReceiving

            for rm in matching_receivings:
                rm.hold_weight_kg = total_hold
                rm.remaining = max(rm.reciving_weight_kg - total_hold, 0)

                # 🔹 Update status based on total hold
                diff = abs(float(rm.reciving_weight_kg) - float(total_hold))
                if total_hold == 0:
                    rm.status = 'open'
                elif total_hold < rm.reciving_weight_kg and diff > 20:
                    rm.status = 'partial'
                else:
                    rm.status = 'complete'

                rm.save(update_fields=['hold_weight_kg', 'remaining', 'status'])


class BatchTrackingResource(resources.ModelResource):
    batch_id = fields.Field(
        column_name='batch_id',
        attribute='batch_id',
        widget=ForeignKeyWidget(HoldMaterial, 'batch_id')  # maps by HoldMaterial.batch_id string
    )

    created_at = fields.Field(
        column_name='created_at',
        attribute='created_at',
        widget=DateTimeWidget(format='%m/%d/%Y %H:%M')  # matches CSV like "11/6/2025 9:31"
    )

    class Meta:
        model = BatchTracking
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ('issue_id',)
        fields = (
            'issue_id', 'batch_id', 'customer', 'standard', 'component',
            'grade', 'dia', 'heatno', 'rack_no', 'issue_bar_qty',
            'issue_qty_kg', 'line', 'supplier', 'created_at', 'verified_by',
        )


# -------------------- Admin Classes --------------------

@admin.register(RMReceiving)
class RMReceivingAdmin(ImportExportModelAdmin):
    resource_class = RMReceivingResource
    list_display = ('date', 'supplier', 'grade', 'dia', 'customer', 'invoice_no', 'approval_status', 'status', 'remaining')
    list_filter = ('supplier', 'grade', 'approval_status', 'status', 'date')
    search_fields = ('supplier', 'grade', 'invoice_no', 'heatno', 'customer')
    ordering = ('-date',)
    readonly_fields = ('remaining',)


@admin.register(HoldMaterial)
class HoldMaterialAdmin(ImportExportModelAdmin):
    resource_class = HoldMaterialResource
    list_display = ('batch_id', 'component', 'customer', 'supplier', 'grade', 'hold_material_qty_kg', 'remaining', 'status', 'created_at')
    list_filter = ('status', 'supplier', 'grade', 'customer')
    search_fields = ('batch_id', 'component', 'supplier', 'customer', 'heatno')
    ordering = ('-created_at',)
    readonly_fields = ('remaining',)


@admin.register(BatchTracking)
class BatchTrackingAdmin(ImportExportModelAdmin):
    resource_class = BatchTrackingResource
    list_display = ('issue_id', 'batch_id', 'component', 'grade', 'issue_qty_kg', 'customer', 'line', 'created_at')
    list_filter = ('customer', 'grade', 'line')
    search_fields = ('issue_id', 'batch_id__batch_id', 'component', 'customer')
    ordering = ('-created_at',)

from simple_history.admin import SimpleHistoryAdmin
from .models import Masterlist


# ------------------ Resource for Import/Export ------------------

class MasterlistResource(resources.ModelResource):
    class Meta:
        model = Masterlist
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ('component', 'drawing_sr_number')
        fields = (
            'id', 'component', 'part_name', 'customer', 'supplier',
            'customer_location', 'drawing_rev_number', 'drawing_rev_date',
            'forging_line', 'drawing_sr_number', 'standerd', 'grade', 'slug_weight',
            'dia', 'ht_process', 'hardness_required', 'running_status',
            'packing_condition', 'ring_weight', 'cost',
            'op_10_time', 'op_10_target', 'op_20_time', 'op_20_target',
            'cnc_target_remark', 'parent_component', 'created_at', 'verified_by'
        )


# ------------------ Admin Configuration ------------------

@admin.register(Masterlist)
class MasterlistAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = MasterlistResource
    list_display = (
        'component', 'part_name', 'customer', 'supplier',
        'grade', 'dia', 'slug_weight', 'ring_weight',
        'cost', 'running_status', 'created_at'
    )
    list_filter = ('customer', 'supplier', 'grade', 'running_status')
    search_fields = (
        'component', 'part_name', 'customer', 'supplier',
        'grade', 'dia', 'drawing_rev_number'
    )
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


from .models import TagGeneration

# Create a resource class
class TagGenerationResource(resources.ModelResource):
    class Meta:
        model = TagGeneration
        import_id_fields = ['tag_uid']  # Unique identifier for import
        fields = (
            'tag_uid', 'generated_at', 'generated_by', 'current_process', 'next_process',
            'qty', 'grade', 'heat_no', 'customer', 'component', 'batch_id',
            'status', 'is_printed', 'printed_at'
        )

# Register with ImportExportModelAdmin
@admin.register(TagGeneration)
class TagGenerationAdmin(ImportExportModelAdmin):
    resource_class = TagGenerationResource
    list_display = ('tag_uid', 'component', 'batch_id', 'customer', 'status', 'is_printed', 'generated_at')
    search_fields = ('tag_uid', 'component', 'batch_id', 'customer', 'grade', 'heat_no')
    list_filter = ('status', 'is_printed', 'generated_at', 'current_process', 'next_process')
    readonly_fields = ('tag_uid', 'generated_at', 'printed_at')  # Auto-generated fields


from .models import Schedule

# Define a resource for import/export behavior
class ScheduleResource(resources.ModelResource):
    class Meta:
        model = Schedule
        fields = (
            'id',
            'component',
            'customer',
            'supplier',
            'grade',
            'standerd',
            'dia',
            'slug_weight',
            'pices',
            'weight',
            'date1',
            'location',
            'planned',
            'verified_by',
            'created_at',
            'disclosure_status',
            'disclosure_notes',
            'disclosure_date',
            'disclosed_by',
        )
        export_order = fields  # Keep consistent column order in export

# Register Schedule with ImportExportModelAdmin
@admin.register(Schedule)
class ScheduleAdmin(ImportExportModelAdmin):
    resource_class = ScheduleResource
    list_display = (
        'component', 'customer', 'grade', 'dia',
        'pices', 'weight', 'date1', 'planned',
        'verified_by', 'disclosure_status'
    )
    list_filter = ('customer', 'grade', 'disclosure_status', 'date1')
    search_fields = ('component', 'customer', 'grade', 'dia')
    ordering = ('-date1',)