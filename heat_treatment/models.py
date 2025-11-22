from django.db import models

class HeatTreatment(models.Model):
    batch_number = models.CharField(max_length=50)
    date = models.DateField()
    shift = models.CharField(max_length=100)
    process = models.CharField(max_length=100)
    component = models.CharField(max_length=100)
    furnace = models.CharField(max_length=100)
    supervisor = models.CharField(max_length=100)
    operator = models.CharField(max_length=100)
    remark = models.CharField(max_length=250)
    ringweight = models.DecimalField(max_digits=10, decimal_places=3)
    production = models.IntegerField()
    cycle_time = models.CharField(max_length=100)
    unit = models.DecimalField(max_digits=10, decimal_places=2)
    heat_no = models.CharField(max_length=100)
    # Additional fields to track production values
    target = models.IntegerField()
    total_produced = models.IntegerField()
    remaining = models.IntegerField(default=0)
    hardness = models.CharField(max_length=100,blank=True)
    micro = models.FileField(upload_to='heat_treatment/micro/', null=True, blank=True)
    grain_size = models.FileField(upload_to='heat_treatment/grain_size/', null=True, blank=True)


    
    
    verified_by = models.CharField(max_length=100)

    def __str__(self):
        return self.component