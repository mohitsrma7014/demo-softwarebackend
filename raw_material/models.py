from django.db import models
import uuid
from django.db.models import F
from django.db.models import Sum
from simple_history.models import HistoricalRecords
from django.db import transaction, IntegrityError
import os
from datetime import datetime
import json
from django.conf import settings
from django.core.exceptions import ValidationError

# Create your models here.
class Supplier(models.Model):
    name = models.CharField(max_length=100, unique=True)
    delivery_days = models.IntegerField()  # No. of days required for delivery
    supplier_details = models.CharField(max_length=100, blank=True, null=True)  # No. of days required for delivery
    supplier_gstin = models.CharField(max_length=100, blank=True, null=True)  # No. of days required for delivery

    def __str__(self):
        return self.name

class Grade(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Customer(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class TypeOfMaterial(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    


class RMReceiving(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    date = models.DateField()
    supplier = models.CharField(max_length=100, db_index=True)
    grade = models.CharField(max_length=50, db_index=True)
    dia = models.CharField(max_length=100, db_index=True)
    customer = models.CharField(max_length=100, db_index=True)
    standerd = models.CharField(max_length=100)
    heatno = models.CharField(max_length=50)
    reciving_weight_kg = models.DecimalField(max_digits=10, decimal_places=2)   # total received kg
    hold_weight_kg = models.DecimalField(max_digits=10, decimal_places=2, default=None)  # remaining kg available
    remaining = models.DecimalField(max_digits=10, decimal_places=2,default=None)
    rack_no = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    type_of_material = models.CharField(max_length=100)
    cost_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_no = models.CharField(max_length=50)
    milltc = models.FileField(upload_to='reports/MILLTC', null=True, blank=True)
    spectro = models.FileField(upload_to='reports/SPECTRO', null=True, blank=True)
    ssb_inspection_report = models.FileField(upload_to='reports/SSBINSPECTION', null=True, blank=True)
    customer_approval = models.FileField(upload_to='reports/CUSTOMERAPPROVAL', null=True, blank=True)

    verified_by = models.CharField(max_length=150, blank=True)
    approval_status = models.CharField(
        max_length=20,
        blank=True, null=True,
        choices=[
            ('Under Inspection', 'Under Inspection'),
            ('Hold', 'Hold'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected')
        ],
        default=None
    )
    comments = models.CharField(max_length=300, blank=True, null=True)
    STATUS_CHOICES = [('open','Open'),('partial','Partial Issue'),('complete','Complete Issue')]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    def __str__(self):
        return f"{self.supplier} - {self.grade} - {self.invoice_no} - {self.heatno}"

    def save(self, *args, **kwargs):
        # on initial save, set available_kg = weight
        if not self.pk:
            self.remaining = self.reciving_weight_kg
            if not self.approval_status:
                if self.type_of_material.strip().upper() == 'JOB WORK':
                    self.approval_status = 'Approved'
                else:
                    self.approval_status = 'Under Inspection'
        super().save(*args, **kwargs)

    def update_status(self):
        total_hold = HoldMaterial.objects.filter(rm_receiving=self).aggregate(total=Sum('hold_material_qty_kg'))['total'] or 0
        self.remaining = max(self.reciving_weight_kg - total_hold, 0)
        self.hold_weight_kg =  total_hold
        diff = abs(float(self.reciving_weight_kg) - float(total_hold))
        if total_hold == 0:
            self.status = 'open'
        elif total_hold < self.reciving_weight_kg and diff > 20:
            self.status = 'partial'
        else:
            self.status = 'complete'
        self.save(update_fields=['status','remaining', 'hold_weight_kg'])

class HoldMaterial(models.Model):
    rm_receiving = models.ForeignKey(
        'raw_material.RMReceiving',
        on_delete=models.CASCADE,
        related_name='holds',null=True,       
    blank=True 
    )
    batch_id = models.CharField(max_length=100, unique=True, blank=True, db_index=True)
    component = models.CharField(max_length=100, db_index=True)
    customer = models.CharField(max_length=100)
    slug_weight = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True )
    supplier = models.CharField(max_length=100)
    grade = models.CharField(max_length=50)
    standerd = models.CharField(max_length=100)
    heatno = models.CharField(max_length=50)
    dia = models.CharField(max_length=100)
    rack_no = models.CharField(max_length=50)
    pieces = models.IntegerField()
    hold_material_qty_kg = models.DecimalField(max_digits=10, decimal_places=2)
    line = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_by = models.CharField(max_length=150, blank=True)
    STATUS_CHOICES = [
        ('open','Open'),
        ('partial','Partial Issue'),
        ('complete','Complete Issue')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    remaining = models.DecimalField(max_digits=10, decimal_places=2, default=None)
    issue_qty_kg = models.DecimalField(max_digits=10, decimal_places=2, default=None) 

    def __str__(self):
        return f"{self.batch_id} - {self.component} - {self.hold_material_qty_kg}"

    def save(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, 'counts.json')
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump({}, f)

        if not self.batch_id:
            counts = read_counts(file_path)
            customer_name = self.customer or "XX"
            current_date = datetime.now().strftime("%Y%m%d")
            customer_initials = customer_name[:2].upper()
            key = f"{current_date}_{customer_initials}"

            current_count = counts.get(key, 0) + 1
            counts[key] = current_count

            self.batch_id = generate_mt_block_number(customer_name, current_count)
            write_counts(file_path, counts)

        if not self.pk:
            self.remaining = self.hold_material_qty_kg

        super().save(*args, **kwargs)

    def update_status(self):
        from django.db.models import Sum

        total_issued = BatchTracking.objects.filter(batch_id=self).aggregate(
            total=Sum('issue_qty_kg')
        )['total'] or 0

        # print("DEBUG | Total Issued:", total_issued)
        # print("DEBUG | Before Update | Remaining:", self.remaining, "Issue Qty:", self.issue_qty_kg)

        self.issue_qty_kg = total_issued
        self.remaining = max(self.hold_material_qty_kg - total_issued, 0)

        if total_issued == 0:
            self.status = 'open'
        elif total_issued < self.hold_material_qty_kg:
            self.status = 'partial'
        else:
            self.status = 'complete'

        # print("DEBUG | After Update | Remaining:", self.remaining, "Issue Qty:", self.issue_qty_kg, "Status:", self.status)

        self.save(update_fields=['status', 'remaining', 'issue_qty_kg'])



def generate_mt_block_number(customer_name, count):
    current_date = datetime.now()
    prefix = 'PP'
    customer_initials = customer_name[:2].upper()
    return f"{prefix}-{current_date:%Y%m%d}-{customer_initials}-{count:02d}"


def read_counts(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception:
        return {}


def write_counts(file_path, counts):
    with open(file_path, 'w') as file:
        json.dump(counts, file)

class BatchTracking(models.Model):
    batch_id = models.ForeignKey(HoldMaterial, on_delete=models.CASCADE, related_name='batches')
    issue_id = models.CharField(max_length=50, unique=True, db_index=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    customer = models.CharField(max_length=100)
    standard = models.CharField(max_length=100)
    component = models.CharField(max_length=100)
    grade = models.CharField(max_length=100)
    dia = models.CharField(max_length=100)
    heatno = models.CharField(max_length=100)
    rack_no = models.CharField(max_length=100)
    issue_bar_qty = models.CharField(max_length=100)
    issue_qty_kg = models.DecimalField(max_digits=10, decimal_places=2)
    line = models.CharField(max_length=100)
    supplier = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_by = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.issue_id

    def save(self, *args, **kwargs):
        if not self.issue_id:
            prefix = "ISSUE"
            unique_code = uuid.uuid4().hex[:8].upper()
            self.issue_id = f"{prefix}-{unique_code}"

        super().save(*args, **kwargs)
        if self.batch_id:
            self.batch_id.update_status()
        


class Masterlist(models.Model):
    component = models.CharField(max_length=100)
    part_name= models.CharField(max_length=100)
    customer = models.CharField(max_length=100)
    supplier = models.CharField(max_length=100)
    customer_location = models.CharField(max_length=100,blank=True, null=True)
    drawing_rev_number = models.CharField(max_length=100,blank=True, null=True)
    drawing_rev_date = models.CharField(max_length=100,blank=True, null=True)
    forging_line = models.CharField(max_length=100,blank=True, null=True)
    drawing_sr_number = models.IntegerField()
    standerd= models.CharField(max_length=100)
    grade= models.CharField(max_length=100)
    slug_weight = models.DecimalField(max_digits=10, decimal_places=2)
    dia = models.CharField(max_length=100)
    ht_process = models.CharField(max_length=100)
    hardness_required = models.CharField(max_length=100,blank=True, null=True)
    running_status = models.CharField(max_length=100,blank=True, null=True)
    packing_condition = models.CharField(max_length=100,blank=True, null=True)
    ring_weight = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    op_10_time = models.IntegerField(blank=True, null=True)
    op_10_target = models.IntegerField(blank=True, null=True)
    op_20_time = models.IntegerField(blank=True, null=True)
    op_20_target = models.IntegerField(blank=True, null=True)
    cnc_target_remark = models.CharField(max_length=500,blank=True, null=True)

    parent_component = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_components'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    verified_by = models.CharField(max_length=150, blank=True, null=True)  # New field to store the username
    
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.component} - {self.customer} - {self.drawing_sr_number}"
    def save(self, *args, **kwargs):
        # Any custom logic before saving can go here
        super().save(*args, **kwargs)
        


class MasterlistDocument(models.Model):
    masterlist = models.ForeignKey('Masterlist', on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50)
    catagory = models.CharField(max_length=50,blank=True, null=True)
    document = models.FileField(upload_to='masterlist_documents/')
    version = models.PositiveIntegerField(default=1)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_current = models.BooleanField(default=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    verified_by = models.CharField(max_length=150, blank=True, null=True) 
    history = HistoricalRecords()
    
    def clean(self):
        # Ensure only one current version per document type per masterlist
        if self.is_current:
            existing_current = MasterlistDocument.objects.filter(
                masterlist=self.masterlist,
                document_type=self.document_type,
                is_current=True
            ).exclude(pk=self.pk if self.pk else None)
            
            if existing_current.exists():
                raise ValidationError(f"There is already a current version for {self.document_type}")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.masterlist} - {self.document_type} (v{self.version})"
    
class SPCDimension(models.Model):
    component = models.CharField(max_length=250)
    dimension = models.CharField(max_length=250)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    instrument = models.CharField(max_length=100)
    remark = models.CharField(max_length=250, blank=True, null=True)
    spc_time_period_days = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"{self.component} - {self.name}"


class SPCRecord(models.Model):
    dimension = models.ForeignKey(SPCDimension, on_delete=models.CASCADE, related_name="records")  # ← FK now
    cp_value = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    cpk_value = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    spc_file = models.FileField(upload_to='spc_records/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        ordering = ['-uploaded_at']
    
from django.utils.timezone import now

def generate_tag_uid():
    date_str = now().strftime("%y%m")  # e.g. 2510 (year+month)
    last_tag = TagGeneration.objects.filter(tag_uid__startswith=date_str).order_by("tag_uid").last()
    if last_tag:
        last_num = int(last_tag.tag_uid[-4:])
        new_num = last_num + 1
    else:
        new_num = 1
    return f"{date_str}{new_num:04d}"  # e.g. "25100001"

class TagGeneration(models.Model):
    STATUS_CHOICES = [
        ('ok', 'OK'),
        ('reject', 'Reject'),
        ('rework', 'Rework'),
    ]
    # System generated fields
    tag_uid = models.CharField(max_length=20, unique=True, editable=False)  # changed from UUIDField
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.CharField(max_length=100)  # Changed to CharField
    
    # Process fields
    current_process = models.CharField(max_length=100)
    next_process = models.CharField(max_length=100)
    
    # Production data
    qty = models.IntegerField()
    grade = models.CharField(max_length=50)
    heat_no = models.CharField(max_length=50)
    
    # Customer and component info
    customer = models.CharField(max_length=100)
    component = models.CharField(max_length=100)
    batch_id = models.CharField(max_length=50)

    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='ok'
    )
    
    # Additional fields for tracking
    is_printed = models.BooleanField(default=False)
    printed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"Tag {self.tag_uid} - {self.component}"
    
    def save(self, *args, **kwargs):
        if not self.tag_uid:  # Only generate if new
            self.tag_uid = generate_tag_uid()
        super().save(*args, **kwargs)

    def can_proceed_to_next_operation(self):
        """Check if material can proceed to next operation based on status"""
        return self.status == 'ok'
    



class Schedule(models.Model):
    component = models.CharField(max_length=100)
    customer = models.CharField(max_length=100)
    supplier = models.CharField(max_length=100, blank=True)
    grade = models.CharField(max_length=50)
    standerd = models.CharField(max_length=100, blank=True)
    dia = models.CharField(max_length=100)
    slug_weight=  models.DecimalField(max_digits=10, decimal_places=3)
    pices = models.IntegerField()
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    date1 = models.CharField(max_length=100)
    location = models.CharField(max_length=150, blank=True)
    planned = models.IntegerField(default=0)
    verified_by = models.CharField(max_length=150, blank=True)  # New field to store the username
    created_at = models.DateTimeField(auto_now_add=True)  # Add this field
    DISCLOSURE_CHOICES = [
        ('none', 'No Disclosure'),
        ('not_received', 'Not Received by Customer'),
        ('not_produced', 'Not Produced'),
        ('delay', 'Delay in Production'),
        ('customer_denied', 'Customer Denied'),
    ]
        
    disclosure_status = models.CharField(
        max_length=20,
        choices=DISCLOSURE_CHOICES,
        default='none'
    )
    disclosure_notes = models.TextField(blank=True)
    disclosure_date = models.DateTimeField(null=True, blank=True)
    disclosed_by = models.CharField(
        null=True,
        blank=True,
        max_length=30,
    )

    class Meta:
        ordering = ['-date1']
        indexes = [
            models.Index(fields=['disclosure_status']),
            models.Index(fields=['date1']),
        ]

    def __str__(self):
        return f"{self.component} - {self.date1}"