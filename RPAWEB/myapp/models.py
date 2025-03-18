from django.db import models

# Create your models here.
class Order(models.Model):
    DISTRIBUTION_CHOICES = [
        ('DA', 'DA'),
        ('DC', 'DC'),
        ('DR', 'DR'),
    ]
    
    customer = models.CharField(max_length=100)
    source = models.CharField(max_length=20)
    name = models.CharField(max_length=100, blank=True)
    file_date = models.DateTimeField()
    po_number = models.CharField(max_length=20)
    po_date = models.DateTimeField()
    dist_channel = models.CharField(max_length=2, choices=DISTRIBUTION_CHOICES)
    so_number = models.CharField(max_length=20)
    so_date = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    sap_info = models.CharField(max_length=100, blank=True)
    jadwal_toko = models.DateTimeField(null=True, blank=True)
    notes = models.CharField(max_length=20)

    class Meta:
        ordering = ['id']
