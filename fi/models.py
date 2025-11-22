from django.db import models

class Fi(models.Model):
    batch_number = models.CharField(max_length=50)
    date = models.DateField()
    shift = models.CharField(max_length=100)
    component = models.CharField(max_length=100)
    target = models.IntegerField()
    chaker= models.CharField(max_length=100)
    production = models.IntegerField()
    remark =  models.CharField(max_length=100)
    cnc_height = models.IntegerField()
    cnc_od = models.IntegerField()
    cnc_bore = models.IntegerField()
    cnc_groove = models.IntegerField()
    cnc_dent = models.IntegerField()
    forging_height = models.IntegerField()
    forging_od = models.IntegerField()
    forging_bore = models.IntegerField()
    forging_crack = models.IntegerField() 
    forging_dent = models.IntegerField()
    pre_mc_height = models.IntegerField()
    pre_mc_od = models.IntegerField()
    pre_mc_bore = models.IntegerField()
    rework_height = models.IntegerField()
    rework_od = models.IntegerField()
    rework_bore = models.IntegerField()
    rework_groove = models.IntegerField()
    rework_dent = models.IntegerField()
    rust = models.IntegerField()
    verified_by = models.CharField(max_length=100)

    heat_no = models.CharField(max_length=100)
    # Additional fields to track production values
    target1 = models.IntegerField()
    total_produced = models.IntegerField()
    remaining = models.IntegerField(default=0)

    def __str__(self):
        return self.component
    