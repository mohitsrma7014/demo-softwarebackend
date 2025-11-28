from django.urls import path
from . import views

urlpatterns = [
    path('inventory/in/', views.stock_in, name='stock_in'),
    path('inventory/out/', views.stock_out, name='stock_out'),
    path('inventory/locations/', views.location_list, name='location_list'),
    path('inventory/materials/', views.hold_material_list, name='hold_material_list'),
    path('inventory/available-out/<int:location_id>/', views.available_materials_for_out, name='available_materials_for_out'),
    path('inventory/location/<str:code>/', views.location_inventory, name='location_inventory'),
    path('inventory/history/in/', views.in_history, name='in_history'),
    path('inventory/history/out/', views.out_history, name='out_history'),
     # New endpoints for batch search and component handling
    path('inventory/search-batches/', views.search_batch_ids, name='search_batches'),
    path('inventory/batch-details/', views.get_batch_details, name='batch_details'),

    path('inventory/summary/', views.inventory_summary, name='inventory_summary'),
    path('inventory/summary/locations/', views.inventory_locations, name='inventory_locations'),
    path('inventory/summary/components/', views.inventory_components, name='inventory_components'),
]