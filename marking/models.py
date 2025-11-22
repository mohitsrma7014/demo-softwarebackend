from django.db import models


class marking(models.Model):
    batch_number = models.CharField(max_length=50)
    date = models.DateField()
    machine = models.CharField(max_length=50)
    operator = models.CharField(max_length=50)
    shift = models.CharField(max_length=100)
    component = models.CharField(max_length=100)
    qty = models.IntegerField()
    verified_by = models.CharField(max_length=100)
    heat_no = models.CharField(max_length=100)
    # Additional fields to track production values
    target = models.IntegerField()
    total_produced = models.IntegerField()
    remaining = models.IntegerField(default=0)


    def __str__(self):
        return self.component