from django.db import models

class Forging(models.Model):
    batch_number = models.CharField(max_length=50)
    date = models.DateField()
    shift = models.CharField(max_length=100)
    component = models.CharField(max_length=100)
    customer = models.CharField(max_length=100)
    slug_weight = models.DecimalField(max_digits=10, decimal_places=2)
    rm_grade = models.CharField(max_length=100)
    heat_number = models.CharField(max_length=100)
    line = models.CharField(max_length=100)
    line_incharge = models.CharField(max_length=100)
    forman = models.CharField(max_length=100)
    target = models.IntegerField()
    production = models.IntegerField()
    rework = models.IntegerField()
    up_setting = models.IntegerField()
    half_piercing = models.IntegerField()
    full_piercing = models.IntegerField()
    ring_rolling = models.IntegerField()
    sizing = models.IntegerField()
    overheat = models.IntegerField()
    bar_crack_pcs = models.IntegerField()
    verified_by = models.CharField(max_length=100, blank=True)

    # 🔽 New fields for KPI & reason tracking
    machine_status = models.CharField(max_length=50, choices=[
        ('running', 'Running'),
        ('idle', 'Idle'),
        ('breakdown', 'Breakdown'),
        ('maintenance', 'Maintenance')
    ], default='running')

    downtime_minutes = models.IntegerField(default=0)
    reason_for_downtime = models.TextField(blank=True, null=True)
    reason_for_low_production = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.component
