import os
import django
from django.db.models import Sum

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend_server.settings")
django.setup()

from raw_material.models import HoldMaterial, BatchTracking

def run():
    tolerance = 20  # kg tolerance

    for block in HoldMaterial.objects.all():
        total_issued = BatchTracking.objects.filter(
            batch_id=block.batch_id
        ).aggregate(total=Sum('issue_qty_kg'))['total'] or 0

        diff = abs(float(block.hold_material_qty_kg) - float(total_issued))

        if total_issued == 0:
            block.status = 'open'
        elif total_issued < block.hold_material_qty_kg and diff > tolerance:
            block.status = 'partial'
        else:
            block.status = 'complete'

        block.save(update_fields=['status'])

    print("✅ Block statuses updated successfully!")

if __name__ == "__main__":
    run()
