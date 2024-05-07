# Performance Metric Calculation Functions

def calculate_on_time_delivery_rate(vendor):
    completed_pos = vendor.purchaseorder_set.filter(status='completed')
    on_time_count = len([po for po in completed_pos if po.delivery_date >= po.order_date])
    if not completed_pos:
        return 0.0
    return on_time_count / len(completed_pos)

def calculate_quality_rating_avg(vendor):
    completed_pos = vendor.purchaseorder_set.filter(status='completed')
    ratings = [po.quality_rating for po in completed_pos if po.quality_rating is not None]
    if not ratings:
        return 0.0
    return sum(ratings) / len(ratings)

def calculate_average_response_time(vendor):
    acknowledged_pos = vendor.purchaseorder_set.filter(acknowledgment_date__isnull=False)
    time_diffs = [(po.acknowledgment_date - po.issue_date).total_seconds() for po in acknowledged_pos]
    if not time_diffs:
        return 0.0
    return sum(time_diffs) / len(time_diffs)

def calculate_fulfillment_rate(vendor):
    all_pos = vendor.purchaseorder_set.all()
    fulfilled_count = len([po for po in all_pos if po.status == 'completed'])
    if not all_pos:
        return 0.0
    return fulfilled_count / len(all_pos)

def calculate_and_update_metrics(vendor, save=True):
    on_time_delivery_rate = calculate_on_time_delivery_rate(vendor)
    quality_rating_avg = calculate_quality_rating_avg(vendor)
    average_response_time = calculate_average_response_time(vendor)
    fulfillment_rate = calculate_fulfillment_rate(vendor)
    vendor.on_time_delivery_rate = on_time_delivery_rate
    vendor.quality_rating_avg = quality_rating_avg
    vendor.average_response_time = average_response_time
    vendor.fulfillment_rate = fulfillment_rate
    if save:
        vendor.save()

def update_vendor_metrics_on_po_save(sender, instance, **kwargs):
    print("in save..................")
    print(instance.vendor)
    calculate_and_update_metrics(instance.vendor)

def update_vendor_metrics_on_po_delete(sender, instance, **kwargs):
    calculate_and_update_metrics(instance.vendor)
