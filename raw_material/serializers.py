# masters/serializers.py
from rest_framework import serializers
from .models import MasterlistDocument,Supplier, Grade, Customer, TypeOfMaterial,Location, RMReceiving, HoldMaterial, BatchTracking,Masterlist

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'delivery_days', 'supplier_details', 'supplier_gstin']

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'name']

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name']

class TypeOfMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeOfMaterial
        fields = ['id', 'name']

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name']



class RMReceivingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RMReceiving
        fields = '__all__'
        # Add extra_kwargs to make fields optional for PATCH requests
        extra_kwargs = {
            'milltc': {'required': False, 'allow_null': True},
            'spectro': {'required': False, 'allow_null': True},
            'ssb_inspection_report': {'required': False, 'allow_null': True},
            'customer_approval': {'required': False, 'allow_null': True},
            'approval_status': {'required': False, 'allow_null': True},
        }

    def validate(self, data):
        # Only validate receiving_weight_kg during creation, not updates
        if self.instance is None and data.get('reciving_weight_kg', 0) <= 0:
            raise serializers.ValidationError({"reciving_weight_kg": "Receiving weight must be greater than zero."})
        return data


class HoldMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = HoldMaterial
        fields = '__all__'

    def validate(self, data):
        if data.get('hold_material_qty_kg', 0) <= 0:
            raise serializers.ValidationError({"hold_material_qty_kg": "Hold material weight must be greater than zero."})
        
        # Validate rm_receiving exists and has enough remaining weight
        rm_receiving = data.get('rm_receiving')
        if rm_receiving:
            if data['hold_material_qty_kg'] > rm_receiving.remaining:
                raise serializers.ValidationError({
                    "hold_material_qty_kg": f"Hold weight ({data['hold_material_qty_kg']}) exceeds available remaining weight ({rm_receiving.remaining})"
                })
        
        return data


class BatchTrackingSerializer(serializers.ModelSerializer):
    batch_display = serializers.CharField(source='batch_id.batch_id', read_only=True)

    class Meta:
        model = BatchTracking
        fields = '__all__'
        read_only_fields = ['issue_id']  # ✅ Add this line
        extra_fields = ['batch_display']

    def validate(self, data):
        if data.get('issue_qty_kg', 0) <= 0:
            raise serializers.ValidationError({
                "issue_qty_kg": "Issue quantity must be greater than zero."
            })

        batch = data.get('batch_id')
        if batch and data['issue_qty_kg'] > batch.remaining:
            raise serializers.ValidationError({
                "issue_qty_kg": f"Issue weight ({data['issue_qty_kg']}) exceeds available remaining weight ({batch.remaining})"
            })

        return data

    
class MasterlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Masterlist
        fields = '__all__'

class RMReceivingFilterSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    class Meta:
        model = RMReceiving
        fields = "__all__"  # You can limit fields if you prefer

    def get_label(self, obj):
        index = self.context.get("index", 0)
        return f"f{index}"
    
class HoldMaterialListSerializer(serializers.ModelSerializer):
    issue_qty = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    remaining_qty = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = HoldMaterial
        fields = '__all__'


from .models import TagGeneration, Schedule
from django.utils import timezone

class TagGenerationSerializer(serializers.ModelSerializer):
    generated_at_formatted = serializers.SerializerMethodField()
    tag_uid_string = serializers.SerializerMethodField()
    can_proceed = serializers.SerializerMethodField()

    class Meta:
        model = TagGeneration
        fields = [
            'id', 'tag_uid', 'tag_uid_string', 'generated_at', 'generated_at_formatted', 
            'generated_by', 'current_process', 'next_process', 'qty', 'grade',
            'heat_no', 'customer', 'component', 'batch_id', 'is_printed', 'printed_at',
            'status', 'can_proceed'
        ]
        read_only_fields = ['tag_uid', 'generated_at', 'is_printed', 'printed_at']

    def get_generated_at_formatted(self, obj):
        return timezone.localtime(obj.generated_at).strftime('%Y-%m-%d %H:%M:%S')

    def get_tag_uid_string(self, obj):
        return str(obj.tag_uid)
    
    def get_can_proceed(self, obj):
        return obj.can_proceed_to_next_operation()

class TagGenerationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagGeneration
        fields = [
            'generated_by', 'current_process', 'next_process', 'qty', 'grade',
            'heat_no', 'customer', 'component', 'batch_id', 'status'
        ]

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'

class ScheduleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['pices', 'weight']  # Only these fields can be updated
        read_only_fields = ['component', 'customer', 'date1']  # Protect these from changes

class MasterlistDocumentSerializer(serializers.ModelSerializer):
    document_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MasterlistDocument
        fields = [
            'id', 'document_type', 'document_url', 'version', 
            'uploaded_at', 'is_current', 'remarks','verified_by' ,'catagory',
        ]
        read_only_fields = ['id', 'version', 'uploaded_at', 'is_current']
    
    def get_document_url(self, obj):
        if obj.document:
            return self.context['request'].build_absolute_uri(obj.document.url)
        return None

class MasterlistSerializer1(serializers.ModelSerializer):
    documents = MasterlistDocumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Masterlist
        fields = [
            'id', 'component', 'part_name', 'customer', 'drawing_sr_number',
             'grade', 'slug_weight', 'dia', 'ht_process',
            'ring_weight', 'cost', 'op_10_time',
            'op_10_target', 'op_20_time', 'op_20_target', 'cnc_target_remark',
            'created_at', 'documents','verified_by','packing_condition','running_status',
            'hardness_required','drawing_rev_date','drawing_rev_number','customer_location','forging_line'
        ]
        read_only_fields = ['id', 'created_at', 'documents']

class MasterlistCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Masterlist
        fields = [
            'component', 'part_name', 'customer', 'drawing_sr_number',
            'grade', 'slug_weight', 'dia', 'ht_process',
            'ring_weight', 'cost',  'op_10_time',
            'op_10_target', 'op_20_time', 'op_20_target', 'cnc_target_remark','verified_by','packing_condition','running_status',
            'hardness_required','drawing_rev_date','drawing_rev_number','customer_location','forging_line'
        ]

class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterlistDocument
        fields = ['document_type', 'catagory','document', 'remarks','verified_by']


class NpdTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Masterlist
        fields = [
            'id', 'component', 'part_name', 'customer', 'customer_location', 
            'drawing_rev_number', 'drawing_rev_date', 'forging_line',
            'drawing_sr_number', 'standerd', 'grade', 'slug_weight',
            'dia', 'ht_process', 'hardness_required', 'running_status',
            'packing_condition', 'ring_weight', 'cost',
            'op_10_time', 'op_10_target', 'op_20_time', 'op_20_target',
            'cnc_target_remark', 'created_at', 'verified_by'
        ]

class MasterListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Masterlist
        fields = '__all__'
