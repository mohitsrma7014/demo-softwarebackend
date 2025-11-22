from django.db import models

class pre_mc(models.Model):
    batch_number = models.CharField(max_length=50)
    date = models.DateField()
    heat_no = models.CharField(max_length=50)
    customer = models.CharField(max_length=100)
    component = models.CharField(max_length=100)
    qty = models.IntegerField()
    shop_floor = models.CharField(max_length=50)
    target = models.IntegerField()
    total_produced = models.IntegerField()
    remaining = models.IntegerField(blank=True , null=True)

    verified_by = models.CharField(max_length=100)

    def __str__(self):
        return self.component