from django.db import models
from django.db.models.signals import post_save, post_delete
from .signals import update_vendor_metrics_on_po_save, update_vendor_metrics_on_po_delete, calculate_average_response_time, calculate_fulfillment_rate, calculate_on_time_delivery_rate, calculate_quality_rating_avg
from django.utils import timezone

class Vendor(models.Model):
    name = models.CharField(max_length=255)
    contact_details = models.TextField()
    address = models.TextField()
    vendor_code = models.CharField(max_length=50, unique=True)
    on_time_delivery_rate = models.FloatField(default=0.0)
    quality_rating_avg = models.FloatField(default=0.0)
    average_response_time = models.FloatField(default=0.0)
    fulfillment_rate = models.FloatField(default=0.0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_historical_performance()

    def update_historical_performance(self):
        # Calculate metrics
        on_time_delivery_rate = calculate_on_time_delivery_rate(self)
        quality_rating_avg = calculate_quality_rating_avg(self)
        average_response_time = calculate_average_response_time(self)
        fulfillment_rate = calculate_fulfillment_rate(self)

        # Update or create HistoricalPerformance record
        historical_performance, created = HistoricalPerformance.objects.get_or_create(
            vendor=self,
            defaults={
                'date': timezone.now(),
                'on_time_delivery_rate': on_time_delivery_rate,
                'quality_rating_avg': quality_rating_avg,
                'average_response_time': average_response_time,
                'fulfillment_rate': fulfillment_rate
            }
        )
        # If the record already exists, update its fields with the new values
        if not created:
            historical_performance.date = timezone.now()
            historical_performance.on_time_delivery_rate = on_time_delivery_rate
            historical_performance.quality_rating_avg = quality_rating_avg
            historical_performance.average_response_time = average_response_time
            historical_performance.fulfillment_rate = fulfillment_rate
            historical_performance.save()

class PurchaseOrder(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    po_number = models.CharField(max_length=50, unique=True)
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField()
    items = models.JSONField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('canceled', 'Canceled')])
    quality_rating = models.FloatField(null=True)
    issue_date = models.DateTimeField(auto_now_add=True)
    acknowledgment_date = models.DateTimeField(null=True)

class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    on_time_delivery_rate = models.FloatField()
    quality_rating_avg = models.FloatField()
    average_response_time = models.FloatField()
    fulfillment_rate = models.FloatField()

post_save.connect(update_vendor_metrics_on_po_save, sender=PurchaseOrder)
post_delete.connect(update_vendor_metrics_on_po_delete, sender=PurchaseOrder)