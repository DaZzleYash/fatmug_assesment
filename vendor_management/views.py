from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from .models import Vendor, PurchaseOrder
from .serializers import VendorSerializer, PurchaseOrderSerializer
from django.shortcuts import get_object_or_404
import datetime

def authenticate_user(username, password):
    user = authenticate(username=username, password=password)
    if user:
        if user.is_active:
            return user
    return None

class LoginView(APIView):
    '''
    POST api/token/
    body:{
        "username":specific_username, 
        "password":corresponding_password
    }
    returns: {
        "refresh":refresh_token, 
        "access":access_token
    }
    '''
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username or password is missing'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate_user(username, password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class TokenRefreshView(APIView):
    '''
    POST /api/token/refresh/
    This endpoint is used to refresh an expired access token. 
    It requires a valid refresh token (refresh token) in the request body. If successful, it returns a new access token.
    '''
    def post(self, request):
        try:
            refresh = RefreshToken(request.data['refresh'])
            refresh.access_token.user.is_active
            token = refresh.access_token
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            'refresh': str(refresh),
            'access': str(token),
        })

class VendorList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        '''
        GET api/vendors/
        retrive the list of all the vendors.[Authentication Required] 
        '''
        vendors = Vendor.objects.all()
        serializer = VendorSerializer(vendors, many=True)
        return Response(serializer.data)

    def post(self, request):
        '''
        POST api/vendors/
        Posts the payload for a newly created vendor object[Authentication Required]
        json structure for posting the vendor data
        {
            "name" : "abc xyz", 
            "contact_details" : "having@abc.com", 
            "address" : "vgy, india", 
            "vendor_code" : "Ven1", 
            "on_time_delivery_rate" : 0.0, 
            "quality_rating_avg" : 0.0,
            "average_response_time" : 0.0,
            "fulfillment_rate" : 0.0
        }
        NOTES-on_time_delivery_rate, quality_rating_avg, average_response_time, fulfillment_rate will be 0.0 by default []
        '''
        serializer = VendorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VendorDetail(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, vendor_id):
        '''
        GET /api/vendors/<vendor_id>/
        <vendor_id>: integer value of vendor_id
        fetches all the specific details of an individual vendor with id=<vendor_id>[Authentication required]
        '''
        vendor = get_object_or_404(Vendor, pk=vendor_id)
        serializer = VendorSerializer(vendor)
        return Response(serializer.data)

    def put(self, request, vendor_id):
        '''
        PUT /api/vendors/<vendor_id>/
        <vendor_id>: integer value that uniquely identify a vendor instance
        Allows updating specific vendor with updated data values [Authentication required]
        json structure for posting the vendor data
        {
            "name" : "abc xyz", 
            "contact_details" : "having@abc.com", 
            "address" : "vgy, india", 
            "vendor_code" : "Ven1", 
            "on_time_delivery_rate" : 0.0, 
            "quality_rating_avg" : 0.0,
            "average_response_time" : 0.0,
            "fulfillment_rate" : 0.0
        }
        NOTES-on_time_delivery_rate, quality_rating_avg, average_response_time, fulfillment_rate will be 0.0 by default
        '''
        vendor = get_object_or_404(Vendor, pk=vendor_id)
        serializer = VendorSerializer(vendor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, vendor_id):
        '''
        DELETE /api/vendors/<vendor_id>/
        <vendor_id>: integer value that uniquely identify a vendor instance
        allows deletion of a specific vendor details with id = <vendor_id> [Authentication required]
        '''
        vendor = get_object_or_404(Vendor, pk=vendor_id)
        vendor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PurchaseOrderList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        '''
        GET /api/purchase_orders/
        Retrives a list of all the purchase orders
        api/purchase_orders/?vendor=vendor_id : optionally, it can also filter the list on the basis of 'vendor' parameter 
        [Authentication required]
        '''
        purchase_orders = PurchaseOrder.objects.all()
        vendor_filter = request.query_params.get('vendor')
        if vendor_filter:
            purchase_orders = purchase_orders.filter(vendor=vendor_filter)
        serializer = PurchaseOrderSerializer(purchase_orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        '''
        POST /api/purchase_orders/
        Creates a new purchase order [Authentication required]
        json structure to post
        {
            "po_number": "PO-2023-10-27-006", {Can be of any format}
            "order_date": "2024-05-07T04:44:14.831732Z", {Will be populated automatically as we post the data, no need to explicitly specify}
            "delivery_date": "2024-11-10T00:00:00Z",
            "items": [
                {
                    "item_name": "Product A",
                    "quantity": 12,
                    "unit_price": 25.0
                }
            ],
            "quantity": 15,
            "status": "pending",
            "quality_rating": null,
            "issue_date": "2024-05-07T04:44:14.831732Z",{Will be populated automatically as we post the data, no need to explicitly specify}
            "acknowledgment_date": null,
            "vendor": 2
        }
        '''
        serializer = PurchaseOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PurchaseOrderDetail(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, po_id):
        '''
        GET /api/purchase_orders/<po_id>/
        retrives specific details on the basis of <po_id> which is a unique, purchase order instance id. [Authentication required]
        <po_id> will be an integer value
        '''
        purchase_order = get_object_or_404(PurchaseOrder, pk=po_id)
        serializer = PurchaseOrderSerializer(purchase_order)
        return Response(serializer.data)

    def put(self, request, po_id):
        '''
        PUT /api/purchase_orders/<po_id>/
        <po_id> will be an integer value
        Allows to update the details of a specific pruchase order with <po_id>. [Authentication required]
        json structure to PUT
        {
            "po_number": "PO-2023-10-27-006", {Can be of any format}
            "order_date": "2024-05-07T04:44:14.831732Z", {Will be populated automatically as we post the data, no need to explicitly specify}
            "delivery_date": "2024-11-10T00:00:00Z",
            "items": [
                {
                    "item_name": "Product A",
                    "quantity": 12,
                    "unit_price": 25.0
                }
            ],
            "quantity": 15,
            "status": "pending",
            "quality_rating": null,
            "issue_date": "2024-05-07T04:44:14.831732Z",{Will be populated automatically as we post the data, no need to explicitly specify}
            "acknowledgment_date": null,
            "vendor": 2
        }
        '''
        purchase_order = get_object_or_404(PurchaseOrder, pk=po_id)
        serializer = PurchaseOrderSerializer(purchase_order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, po_id):
        '''
        DELETE /api/purchase_orders/<po_id>/
        Allows to delete the details related to a specific purchase order. [Authentication required]
        <po_id> will be an integer value
        '''
        purchase_order = get_object_or_404(PurchaseOrder, pk=po_id)
        purchase_order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class VendorPerformance(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, vendor_id):
        '''
        GET /api/vendors/<vendor_id>/performance/
        retrives the performance metrices for a specific vendor with vendor_id = <vendor_id>. [Authentication required]
        <vendor_id>: a unique integer value for each vendor
        json response is shown below
        {
            "on_time_delivery_rate": 0.6666666666666666,
            "quality_rating_avg": 3.9000000000000004,
            "average_response_time": 112707.281423,
            "fulfillment_rate": 0.42857142857142855
        }
        '''
        vendor = get_object_or_404(Vendor, pk=vendor_id)
        data = {
            'on_time_delivery_rate': vendor.on_time_delivery_rate,
            'quality_rating_avg': vendor.quality_rating_avg,
            'average_response_time': vendor.average_response_time,
            'fulfillment_rate': vendor.fulfillment_rate,
        }
        return Response(data)

class AcknowledgePurchaseOrderView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, po_id):
        '''
        POST /api/purchase_orders/<po_id>/acknowledge/
        Allows acknowledging a purchase order identified by <po_id>
        <po_id> unique integer value to identify the purchase order(PO). [Authentication required]
        NOTES-Just pass the empty json for the body section to make acknowledgement
        sample json: {}
        '''
        po = get_object_or_404(PurchaseOrder, pk=po_id)
        if po.acknowledgment_date is None:
            po.acknowledgment_date = datetime.datetime.now()
            po.save()
            serializer = PurchaseOrderSerializer(po)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Purchase Order already acknowledged'}, status=status.HTTP_400_BAD_REQUEST)
