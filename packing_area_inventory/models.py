from django.db import models
from raw_material.models import HoldMaterial

class Location(models.Model):
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.code

class InventoryTransaction(models.Model):
    IN = 'IN'
    OUT = 'OUT'

    TYPE_CHOICES = [
        (IN, 'Stock In'),
        (OUT, 'Stock Out')
    ]

    material = models.ForeignKey(HoldMaterial, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    slug_weight = models.DecimalField(max_digits=10, decimal_places=2)
    qty = models.PositiveIntegerField()
    transaction_type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    verified_by = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']