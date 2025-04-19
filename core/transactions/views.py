from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from .models import Transaction
from .serializers import TransactionSerializer, PaymentSerializer
from accounts.models import UserProfile
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from typing import Any, Dict, List, Optional, Union, cast

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
        # Use a type-safe approach to check for staff status
        user = self.request.user
        # Check if user is staff using the permission class
        is_staff = permissions.IsAdminUser().has_permission(self.request, self)
        
        if is_staff:
            return Transaction.objects.all()
        return Transaction.objects.filter(
            sender=user
        ) | Transaction.objects.filter(
            receiver=user
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
        # Use TransactionSerializer for validation
        serializer = TransactionSerializer(data={
            'sender_id': request.user.id,
            'receiver_id': request.data.get('receiver_id'),
            'amount': request.data.get('amount'),
            'transaction_type': 'PAYMENT',
            'description': request.data.get('description', '')
        })
        
        if serializer.is_valid():
            try:
                receiver = User.objects.get(id=request.data.get('receiver_id'))
                
                # Create the transaction
                transaction = Transaction.objects.create(
                    sender=request.user,
                    receiver=receiver,
                    amount=request.data.get('amount'),
                    transaction_type='PAYMENT',
                    status='COMPLETED',
                    description=request.data.get('description', '')
                )
                
                # The balance update is handled in the Transaction model's save method
                
                # Use getattr to safely access attributes
                transaction_id = getattr(transaction, 'id', None)
                transaction_amount = getattr(transaction, 'amount', None)
                receiver_username = getattr(getattr(transaction, 'receiver', None), 'username', 'Unknown')
                
                return Response({
                    'message': f'Payment of {transaction_amount} sent to {receiver_username}',
                    'transaction_id': transaction_id
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
        
        # Use getattr to safely access attributes
        transaction_id = getattr(transaction, 'id', None)
        
        return Response({
            'message': f'Transaction {transaction_id} has been cancelled'
        }, status=status.HTTP_200_OK) 