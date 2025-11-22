from django.db import models

class dispatch(models.Model):
    date = models.DateField()
    component = models.CharField(max_length=100)
    pices = models.IntegerField()
    invoiceno= models.CharField(max_length=100)
    addpdf=models.FileField(upload_to='reports/', null=True, blank=True)
    verified_by = models.CharField(max_length=150, blank=True)  # New field to store the username
    heat_no = models.CharField(max_length=100)
    # Additional fields to track production values
    target1 = models.IntegerField(default=0)
    total_produced = models.IntegerField(default=0)
    remaining = models.IntegerField(default=0)
    batch_number = models.CharField(max_length=50)
    verified_by = models.CharField(max_length=100, blank=True)  # Allow it to be blank
    price =models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)

    def __str__(self):
        return f"{self.component} - {self.invoiceno}"