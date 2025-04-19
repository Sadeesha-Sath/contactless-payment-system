from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Transaction
from .serializers import TransactionSerializer, PaymentSerializer
from accounts.models import UserProfile

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

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