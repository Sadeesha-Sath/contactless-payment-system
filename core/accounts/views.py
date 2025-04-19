from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import UserSerializer, UserProfileSerializer, BalanceUpdateSerializer
from transactions.models import Transaction
from typing import Dict, Any, cast

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_balance(self, request):
        """Get the current user's balance"""
        try:
            profile = UserProfile.objects.get(user=request.user)
            return Response({
                'balance': profile.balance,
                'currency': 'USD'  # You can make this configurable if needed
            }, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'User profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def add_balance(self, request, pk=None):
        profile = self.get_object()
        serializer = BalanceUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            validated_data: Dict[str, Any] = cast(Dict[str, Any], serializer.validated_data)
            amount = validated_data['amount']
            description = validated_data.get('description', 'Balance added by admin')
            
            # Create a TOP_UP transaction
            transaction = Transaction.objects.create(
                sender=request.user,  # Admin user
                receiver=profile.user,
                amount=amount,
                transaction_type='TOP_UP',
                status='COMPLETED',
                description=description
            )
            
            return Response({
                'message': f'Added {amount} to {profile.user.username}\'s balance',
                'transaction_id': transaction.id
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def remove_balance(self, request, pk=None):
        profile = self.get_object()
        serializer = BalanceUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            validated_data: Dict[str, Any] = cast(Dict[str, Any], serializer.validated_data)
            amount = validated_data['amount']
            description = validated_data.get('description', 'Balance removed by admin')
            
            # Check if user has sufficient balance
            if profile.balance < amount:
                return Response(
                    {'error': 'Insufficient balance to remove'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create a transaction to record the balance removal
            transaction = Transaction.objects.create(
                sender=profile.user,
                receiver=request.user,  # Admin user
                amount=amount,
                transaction_type='REFUND',
                status='COMPLETED',
                description=description
            )
            
            return Response({
                'message': f'Removed {amount} from {profile.user.username}\'s balance',
                'transaction_id': transaction.id
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 