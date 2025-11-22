import os
import django
from django.db.models import Sum, F
from django.db.models.functions import Lower

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend_server.settings")
django.setup()

from raw_material.models import RMReceiving, HoldMaterial


def run():
    tolerance = 20  # kg tolerance for marking complete

    print("🔧 Normalizing heat numbers to lowercase...")
    # Normalize all heat numbers in both tables
    RMReceiving.objects.exclude(heatno__isnull=True).update(heatno=Lower(F('heatno')))
    HoldMaterial.objects.exclude(heatno__isnull=True).update(heatno=Lower(F('heatno')))

    print("✅ Heat numbers normalized.\n")

    # Get distinct lowercase heatnos after normalization
    all_heatnos = (
        RMReceiving.objects.annotate(heatno_lower=Lower('heatno'))
        .values_list('heatno_lower', flat=True)
        .distinct()
    )

    for heatno_lower in all_heatnos:
        rm_records = RMReceiving.objects.filter(heatno=heatno_lower)
        if not rm_records.exists():
            continue

        total_hold = (
            HoldMaterial.objects.filter(heatno=heatno_lower)
            .aggregate(total=Sum('hold_material_qty_kg'))['total'] or 0
        )

        total_received = (
            rm_records.aggregate(total=Sum('reciving_weight_kg'))['total'] or 0
        )

        # Calculate remaining material
        remaining = total_received - total_hold

        # --- 🔧 Handle edge cases ---
        if remaining < 0:
            remaining = 0
            status = 'complete'
        elif remaining > total_received:
            remaining = 0
            status = 'complete'
        elif remaining <= tolerance:
            remaining = 0
            status = 'complete'
        elif total_hold == 0:
            status = 'open'
        else:
            status = 'partial'
        # -----------------------------

        # Apply updates to all matching RMReceiving records
        rm_records.update(
            hold_weight_kg=total_hold,
            remaining=remaining,
            status=status
        )

        print(f"✅ Updated {heatno_lower}: Received={total_received:.2f}, Hold={total_hold:.2f}, Remaining={remaining:.2f}, Status={status}")

    print("\n🎯 RMReceiving status update completed successfully!")


if __name__ == "__main__":
    run()
