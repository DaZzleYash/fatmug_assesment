from django.urls import path, include
from . import views

urlpatterns = [
    path('api/vendors/', views.VendorList.as_view()),
    path('api/vendors/<int:vendor_id>/', views.VendorDetail.as_view()),
    path('api/purchase_orders/', views.PurchaseOrderList.as_view()),
    path('api/purchase_orders/<int:po_id>/', views.PurchaseOrderDetail.as_view()),
    path('api/vendors/<int:vendor_id>/performance/', views.VendorPerformance.as_view()),
    path('api/purchase_orders/<int:po_id>/acknowledge/', views.AcknowledgePurchaseOrderView.as_view(), name='acknowledge_po')
]
