from rest_framework import serializers
from raw_material.models import HoldMaterial
from .models import Location, InventoryTransaction

class HoldMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = HoldMaterial
        fields = ['id', 'batch_id', 'component', 'customer', 'slug_weight', 'hold_material_qty_kg', 'remaining']

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    material_detail = HoldMaterialSerializer(source='material', read_only=True)
    location_detail = LocationSerializer(source='location', read_only=True)
    
    # Add these to handle foreign key relationships properly
    material = serializers.PrimaryKeyRelatedField(queryset=HoldMaterial.objects.all())
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())

    class Meta:
        model = InventoryTransaction
        fields = '__all__'
        read_only_fields = ('transaction_type',)

class InventorySummarySerializer(serializers.Serializer):
    material = serializers.CharField()
    batch_id = serializers.CharField()
    component = serializers.CharField()
    available_qty = serializers.IntegerField()
    slug_weight = serializers.DecimalField(max_digits=10, decimal_places=2)