from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Vendor, VendorTransaction
from .serializers import VendorSerializer, VendorTransactionSerializer
from transactions.models import Transaction

class IsVendorUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and hasattr(request.user, 'vendor_profile')

class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Vendor.objects.all()
        if hasattr(self.request.user, 'vendor_profile'):
            return Vendor.objects.filter(user=self.request.user)
        return Vendor.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        vendor = self.get_object()
        transactions = VendorTransaction.objects.filter(vendor=vendor)
        serializer = VendorTransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        vendor = self.get_object()
        
        if not vendor.is_active:
            return Response(
                {'error': 'Vendor account is not active'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        amount = request.data.get('amount')
        description = request.data.get('description', '')
        
        if not amount:
            return Response(
                {'error': 'Amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount = float(amount)
            
            # Create the payment transaction
            transaction = Transaction.objects.create(
                sender=request.user,
                receiver=vendor.user,
                amount=amount,
                transaction_type='PAYMENT',
                status='COMPLETED',
                description=description
            )
            
            # Record the vendor transaction
            vendor_transaction = VendorTransaction.objects.create(
                vendor=vendor,
                amount=amount,
                description=description
            )
            
            return Response({
                'message': f'Payment of {amount} processed for {vendor.business_name}',
                'transaction_id': transaction.id,
                'vendor_transaction_id': vendor_transaction.id
            }, status=status.HTTP_201_CREATED)
            
        except ValueError:
            return Response(
                {'error': 'Invalid amount format'},
                status=status.HTTP_400_BAD_REQUEST
            )

class VendorTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = VendorTransaction.objects.all()
    serializer_class = VendorTransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendorUser]

    def get_queryset(self):
        if self.request.user.is_staff:
            return VendorTransaction.objects.all()
        if hasattr(self.request.user, 'vendor_profile'):
            return VendorTransaction.objects.filter(vendor=self.request.user.vendor_profile)
        return VendorTransaction.objects.none() 