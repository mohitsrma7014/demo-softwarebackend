from django.contrib import admin
from .models import Location, InventoryTransaction

admin.site.register(Location)
admin.site.register(InventoryTransaction)