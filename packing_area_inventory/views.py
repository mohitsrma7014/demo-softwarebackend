from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Case, When, IntegerField, F, Value
from django.db.models.functions import Coalesce
from .models import Location, InventoryTransaction
from .serializers import (
    LocationSerializer,
    TransactionSerializer, 
    InventorySummarySerializer
)
from raw_material.models import HoldMaterial

from raw_material.models import HoldMaterial, Masterlist
import re

@api_view(['GET'])
def search_batch_ids(request):
    """
    Search batch IDs with autocomplete functionality
    Returns similar batches when user types more than 2 characters
    """
    search_term = request.GET.get('search', '').strip()
    
    if not search_term:
        return Response({'error': 'Search term is required'}, status=400)
    
    if len(search_term) < 2:
        return Response({'error': 'Please enter at least 2 characters'}, status=400)
    
    # Search for similar batch IDs
    batches = HoldMaterial.objects.filter(
        batch_id__icontains=search_term
    ).values_list('batch_id', flat=True).distinct()[:10]  # Limit to 10 results
    
    return Response(list(batches))

@api_view(['GET'])
def get_batch_details(request):
    """
    Get complete details of a selected batch and check for parent/child components
    """
    batch_id = request.GET.get('batch_id', '').strip()
    
    if not batch_id:
        return Response({'error': 'Batch ID is required'}, status=400)
    
    try:
        # Get the hold material
        hold_material = HoldMaterial.objects.get(batch_id=batch_id)
        total_in_qty = InventoryTransaction.objects.filter(
            material=hold_material,
            transaction_type=InventoryTransaction.IN
        ).aggregate(total=Sum('qty'))['total'] or 0


        remaining_return_qty = hold_material.pieces - total_in_qty
        if remaining_return_qty < 0:
            remaining_return_qty = 0

        
        # Remove NPD from component name for matching
        component_clean = re.sub(r'\bNPD\b', '', hold_material.component).strip()
        
        # Try to find matching component in masterlist
        try:
            master_component = Masterlist.objects.get(
                component__iexact=component_clean
            )
            
            # Check if this component has parent or child components
            parent_component = None
            child_components = []
            
            if master_component.parent_component:
                # This is a child component, get parent
                parent_component = master_component.parent_component.component
                # Include parent and all siblings (other children of same parent)
                siblings = master_component.parent_component.child_components.all()
                child_components = [sib.component for sib in siblings]
                # Include parent itself
                child_components.insert(0, parent_component)
            elif master_component.child_components.exists():
                # This is a parent component, get all children
                child_components = list(master_component.child_components.all().values_list('component', flat=True))
                # Include parent itself
                child_components.insert(0, master_component.component)
            else:
                # No parent or children, use the component itself
                child_components = [master_component.component]
                
            # Get slug weight from masterlist
            slug_weight = master_component.slug_weight
            
            response_data = {
                'batch_id': hold_material.batch_id,
                'original_component': hold_material.component,
                'cleaned_component': component_clean,
                'component_options': child_components,
                'has_parent_child': len(child_components) > 1,
                'slug_weight': float(slug_weight) if slug_weight else None,
                'max_qty': remaining_return_qty,  # Max pieces from hold material
                'hold_material_id': hold_material.id,
                'customer': hold_material.customer,
                'supplier': hold_material.supplier,
                'grade': hold_material.grade,
                'remaining': float(hold_material.remaining) if hold_material.remaining else 0,
                'hold_material_qty_kg': float(hold_material.hold_material_qty_kg) if hold_material.hold_material_qty_kg else 0
            }
            
        except Masterlist.DoesNotExist:
            # No matching component in masterlist, use original data
            response_data = {
                'batch_id': hold_material.batch_id,
                'original_component': hold_material.component,
                'cleaned_component': component_clean,
                'component_options': [hold_material.component],
                'has_parent_child': False,
                'slug_weight': float(hold_material.slug_weight) if hold_material.slug_weight else None,
                'max_qty':remaining_return_qty,
                'hold_material_id': hold_material.id,
                'customer': hold_material.customer,
                'supplier': hold_material.supplier,
                'grade': hold_material.grade,
                'remaining': float(hold_material.remaining) if hold_material.remaining else 0,
                'hold_material_qty_kg': float(hold_material.hold_material_qty_kg) if hold_material.hold_material_qty_kg else 0
            }
        
        return Response(response_data)
        
    except HoldMaterial.DoesNotExist:
        return Response({'error': 'Batch ID not found'}, status=404)

@api_view(['POST'])
def stock_in(request):
    """
    Modified stock_in to handle the new flow with batch search and component selection
    """
    serializer = TransactionSerializer(data=request.data)
    if serializer.is_valid():
        try:
            # Additional validation for max quantity
            material_id = serializer.validated_data['material'].id
            qty = serializer.validated_data['qty']
            
            # Get the hold material to check max pieces
            hold_material = HoldMaterial.objects.get(id=material_id)
            
            # Check if quantity exceeds available pieces
            if qty > hold_material.pieces:
                return Response({
                    'error': f'Quantity exceeds available pieces. Maximum: {hold_material.pieces}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save(transaction_type="IN")
            return Response({"message": "Stock added", "data": serializer.data})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Keep all other existing views as they are...
@api_view(['POST'])
def stock_out(request):
    serializer = TransactionSerializer(data=request.data)
    if serializer.is_valid():
        material = serializer.validated_data['material']
        location = serializer.validated_data['location']
        qty = serializer.validated_data['qty']

        # calculate available qty
        available = get_available_stock(material.id, location.id)

        if qty > available:
            return Response({"error": f"Not enough stock available. Available: {available}, Requested: {qty}"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer.save(transaction_type="OUT")
            return Response({"message": "Stock removed", "data": serializer.data})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Helper function to get available stock
def get_available_stock(material_id, location_id):
    totals = InventoryTransaction.objects.filter(
        material_id=material_id,
        location_id=location_id
    ).aggregate(
        total_in=Coalesce(Sum(Case(When(transaction_type="IN", then="qty"), output_field=IntegerField())), 0),
        total_out=Coalesce(Sum(Case(When(transaction_type="OUT", then="qty"), output_field=IntegerField())), 0),
    )
    return totals["total_in"] - totals["total_out"]

@api_view(['GET'])
def location_inventory(request, code):
    try:
        # First verify the location exists
        location = Location.objects.filter(code=code).first()
        if not location:
            return Response({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get all transactions for this location and aggregate by material
        data = InventoryTransaction.objects.filter(location__code=code).values(
            "material_id",
            "material__component",
            "material__batch_id",
            "slug_weight"
        ).annotate(
            total_in=Coalesce(Sum(Case(
                When(transaction_type="IN", then="qty"), 
                output_field=IntegerField()
            )), 0),
            total_out=Coalesce(Sum(Case(
                When(transaction_type="OUT", then="qty"), 
                output_field=IntegerField()
            )), 0)
        ).annotate(
            available=F("total_in") - F("total_out")
        ).filter(available__gt=0)

        formatted = []
        for item in data:
            formatted.append({
                "material": item["material_id"],
                "component": item["material__component"],
                "batch": item["material__batch_id"],
                "slug_weight": str(item["slug_weight"]),
                "available_qty": item["available"]
            })

        return Response(formatted)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# NEW ENDPOINT: Get available materials for OUT transaction in specific location
@api_view(['GET'])
def available_materials_for_out(request, location_id):
    """
    Get materials that are available for OUT transaction in a specific location
    """
    try:
        # First verify the location exists
        location = Location.objects.filter(id=location_id).first()
        if not location:
            return Response({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

        print(f"DEBUG: Looking for materials in location ID: {location_id}, Code: {location.code}")

        # Get materials with available stock in the specified location - FIXED QUERY
        available_materials = InventoryTransaction.objects.filter(
            location_id=location_id
        ).values(
            "material_id",
            "material__component",
            "material__batch_id",
            "material__customer",
            "slug_weight"  # Use the slug_weight from InventoryTransaction, not from HoldMaterial
        ).annotate(
            total_in=Coalesce(Sum(Case(
                When(transaction_type="IN", then="qty"), 
                output_field=IntegerField()
            )), 0),
            total_out=Coalesce(Sum(Case(
                When(transaction_type="OUT", then="qty"), 
                output_field=IntegerField()
            )), 0)
        ).annotate(
            available=F("total_in") - F("total_out")
        ).filter(available__gt=0).order_by("material__component")

        print(f"DEBUG: Found {len(available_materials)} available materials")
        
        # Format the response
        formatted_data = []
        for item in available_materials:
            material_data = {
                "id": item["material_id"],
                "component": item["material__component"],
                "batch_id": item["material__batch_id"],
                "customer": item["material__customer"],
                "slug_weight": item["slug_weight"],  # From InventoryTransaction
                "available_in_location": item["available"]
            }
            formatted_data.append(material_data)
            print(f"DEBUG: Material - {material_data}")

        if not formatted_data:
            print("DEBUG: No materials found with available stock")
        
        return Response(formatted_data)
    except Exception as e:
        print(f"DEBUG: Error in available_materials_for_out: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def in_history(request):
    transactions = InventoryTransaction.objects.filter(transaction_type="IN")
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def out_history(request):
    transactions = InventoryTransaction.objects.filter(transaction_type="OUT")
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def location_list(request):
    locations = Location.objects.all()
    serializer = LocationSerializer(locations, many=True)
    return Response(serializer.data)

from .serializers import HoldMaterialSerializer

@api_view(['GET'])
def hold_material_list(request):
    materials = HoldMaterial.objects.all()
    serializer = HoldMaterialSerializer(materials, many=True)
    return Response(serializer.data)

# views.py
@api_view(['GET'])
def inventory_summary(request):
    """
    Get complete inventory summary with batch details, location, and quantities
    """
    try:
        # Get filter parameters
        location_filter = request.GET.get('location', '').strip()
        component_filter = request.GET.get('component', '').strip()
        
        # Base query for inventory transactions
        transactions = InventoryTransaction.objects.select_related(
            'material', 'location'
        ).all()
        
        # Apply filters
        if location_filter:
            transactions = transactions.filter(location__code__icontains=location_filter)
        
        if component_filter:
            transactions = transactions.filter(material__component__icontains=component_filter)
        
        # Group by material and location to get available quantities
        inventory_data = transactions.values(
            'material_id',
            'material__batch_id',
            'material__component',
            'material__customer',
            'location_id',
            'location__code',
            'slug_weight',
            'verified_by'
        ).annotate(
            total_in=Coalesce(Sum(Case(
                When(transaction_type="IN", then="qty"), 
                output_field=IntegerField()
            )), 0),
            total_out=Coalesce(Sum(Case(
                When(transaction_type="OUT", then="qty"), 
                output_field=IntegerField()
            )), 0)
        ).annotate(
            available_qty=F("total_in") - F("total_out")
        ).filter(available_qty__gt=0).order_by('material__component', 'location__code')
        
        # Calculate totals
        total_quantity = 0
        total_weight_kg = 0
        
        formatted_data = []
        for item in inventory_data:
            item_weight_kg = float(item['slug_weight']) * item['available_qty']
            item_weight_ton = item_weight_kg / 1000
            
            formatted_item = {
                "id": f"{item['material_id']}_{item['location_id']}",
                "batch_id": item['material__batch_id'],
                "component": item['material__component'],
                "customer": item['material__customer'],
                "location": item['location__code'],
                "slug_weight": float(item['slug_weight']),
                "available_qty": item['available_qty'],
                "weight_kg": round(item_weight_kg, 2),
                "weight_ton": round(item_weight_ton, 3),
                "verified_by": item['verified_by'],
                "material_id": item['material_id'],
                "location_id": item['location_id']
            }
            formatted_data.append(formatted_item)
            
            total_quantity += item['available_qty']
            total_weight_kg += item_weight_kg
        
        total_weight_ton = total_weight_kg / 1000
        
        response_data = {
            "inventory": formatted_data,
            "summary": {
                "total_items": len(formatted_data),
                "total_quantity": total_quantity,
                "total_weight_kg": round(total_weight_kg, 2),
                "total_weight_ton": round(total_weight_ton, 3)
            }
        }
        
        return Response(response_data)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def inventory_locations(request):
    """
    Get distinct locations for filter dropdown
    """
    locations = Location.objects.all().values('id', 'code').order_by('code')
    return Response(list(locations))

@api_view(['GET'])
def inventory_components(request):
    """
    Get distinct components for filter dropdown
    """
    components = Masterlist.objects.values_list('component', flat=True).distinct().order_by('component')
    return Response(list(components))