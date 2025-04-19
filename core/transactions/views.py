from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Transaction
from .serializers import TransactionSerializer, PaymentSerializer
from accounts.models import UserProfile
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

class TransactionPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = TransactionPagination

    def get_queryset(self):
        if self.request.user.is_staff:
            return Transaction.objects.all()
        return Transaction.objects.filter(
            sender=self.request.user
        ) | Transaction.objects.filter(
            receiver=self.request.user
        )

    def perform_create(self, serializer):
        # Set the sender to the current user
        serializer.save(sender=self.request.user)

    @action(detail=False, methods=['get'])
    def my_transactions(self, request):
        """Get the current user's transactions with optional filtering and pagination"""
        # Get query parameters for filtering
        transaction_type = request.query_params.get('type', None)
        status_filter = request.query_params.get('status', None)
        
        # Base queryset for the current user
        queryset = Transaction.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user)
        ).order_by('-created_at')
        
        # Apply filters if provided
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type.upper())
        
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())
        
        # Paginate the results
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        # If pagination is disabled, return all results
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'transactions': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def make_payment(self, request):
        serializer = PaymentSerializer(data=request.data)
        
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            receiver_id = serializer.validated_data['receiver_id']
            description = serializer.validated_data.get('description', '')
            
            try:
                receiver = User.objects.get(id=receiver_id)
                
                # Check if sender has sufficient balance
                if request.user.profile.balance < amount:
                    return Response(
                        {'error': 'Insufficient balance for this payment'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Create the transaction
                transaction = Transaction.objects.create(
                    sender=request.user,
                    receiver=receiver,
                    amount=amount,
                    transaction_type='PAYMENT',
                    status='COMPLETED',
                    description=description
                )
                
                # The balance update is handled in the Transaction model's save method
                
                return Response({
                    'message': f'Payment of {amount} sent to {receiver.username}',
                    'transaction_id': transaction.id
                }, status=status.HTTP_201_CREATED)
                
            except User.DoesNotExist:
                return Response(
                    {'error': 'Receiver not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def cancel_transaction(self, request, pk=None):
        transaction = self.get_object()
        
        if transaction.status != 'PENDING':
            return Response(
                {'error': 'Only pending transactions can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transaction.status = 'CANCELLED'
        transaction.save()
        
        return Response({
            'message': f'Transaction {transaction.id} has been cancelled'
        }, status=status.HTTP_200_OK) 