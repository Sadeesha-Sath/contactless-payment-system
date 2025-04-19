from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import UserSerializer, UserProfileSerializer, BalanceUpdateSerializer, BatchUserCreationSerializer
from transactions.models import Transaction
from typing import Dict, Any, cast
import csv
from django.http import HttpResponse

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
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def download_template(self, request):
        """
        Download a CSV template for batch user creation.
        
        This endpoint provides a sample CSV file with the correct format
        for batch user creation, including example data.
        """
        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="user_creation_template.csv"'
        
        # Create a CSV writer
        writer = csv.writer(response)
        
        # Write the header row
        writer.writerow([
            'username', 'email', 'password', 'user_type', 
            'first_name', 'last_name', 'initial_balance',
            'vendor_name', 'vendor_description'
        ])
        
        # Write example rows
        writer.writerow([
            'john_doe', 'john@example.com', 'securepassword123', 'USER',
            'John', 'Doe', '100.00',
            '', ''
        ])
        
        writer.writerow([
            'jane_smith', 'jane@example.com', 'securepassword456', 'USER',
            'Jane', 'Smith', '50.00',
            '', ''
        ])
        
        writer.writerow([
            'coffee_shop', 'coffee@example.com', 'securepassword789', 'VENDOR',
            'Coffee', 'Shop', '0.00',
            'Downtown Coffee Shop', 'Best coffee in town'
        ])
        
        return response
    
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def batch_create_users(self, request):
        """
        Create multiple users from a CSV file upload.
        
        CSV format should include the following columns:
        - username (required): The username for the user
        - email (required): The email address for the user
        - password (required): The password for the user
        - user_type (required): Either 'USER' or 'VENDOR'
        - first_name (optional): The user's first name
        - last_name (optional): The user's last name
        - initial_balance (optional): Initial balance for the user (default: 0.00)
        - vendor_name (optional, for vendors only): Name of the vendor business
        - vendor_description (optional, for vendors only): Description of the vendor business
        
        This endpoint is only accessible to admin users.
        """
        serializer = BatchUserCreationSerializer(data=request.data)
        
        if serializer.is_valid():
            csv_file = serializer.validated_data['csv_file']
            results = serializer.process_csv(csv_file)
            
            if results['errors']:
                return Response({
                    'message': 'Some users could not be created',
                    'success_count': len(results['success']),
                    'error_count': len(results['errors']),
                    'success': results['success'],
                    'errors': results['errors']
                }, status=status.HTTP_207_MULTI_STATUS)
            
            return Response({
                'message': f'Successfully created {len(results["success"])} users',
                'success_count': len(results['success']),
                'success': results['success']
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

    @action(detail=True, methods=['get'], permission_classes=[IsAdminUser])
    def account_details(self, request, pk=None):
        """Get detailed account information for a user (admin only)"""
        try:
            profile = self.get_object()
            
            # Get user's transaction history
            sent_transactions = Transaction.objects.filter(sender=profile.user).order_by('-created_at')
            received_transactions = Transaction.objects.filter(receiver=profile.user).order_by('-created_at')
            
            # Prepare transaction data
            sent_transactions_data = [
                {
                    'id': t.id,
                    'amount': t.amount,
                    'type': t.transaction_type,
                    'status': t.status,
                    'description': t.description,
                    'created_at': t.created_at,
                    'receiver': t.receiver.username
                } for t in sent_transactions
            ]
            
            received_transactions_data = [
                {
                    'id': t.id,
                    'amount': t.amount,
                    'type': t.transaction_type,
                    'status': t.status,
                    'description': t.description,
                    'created_at': t.created_at,
                    'sender': t.sender.username
                } for t in received_transactions
            ]
            
            # Prepare response data
            response_data = {
                'user': {
                    'id': profile.user.id,
                    'username': profile.user.username,
                    'email': profile.user.email,
                    'first_name': profile.user.first_name,
                    'last_name': profile.user.last_name,
                    'is_active': profile.user.is_active,
                    'date_joined': profile.user.date_joined
                },
                'profile': {
                    'id': profile.id,
                    'balance': profile.balance,
                    'created_at': profile.created_at,
                    'updated_at': profile.updated_at
                },
                'transactions': {
                    'sent': sent_transactions_data,
                    'received': received_transactions_data
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'User profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def add_balance(self, request, pk=None):
        """Add balance to a user's account (admin only)"""
        profile = self.get_object()
        print(profile)
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
            
            # Update the user's balance
            profile.balance += amount
            profile.save()
            
            return Response({
                'message': f'Added {amount} to {profile.user.username}\'s balance',
                'transaction_id': transaction.id,
                'new_balance': profile.balance
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def remove_balance(self, request, pk=None):
        """Remove balance from a user's account (admin only)"""
        profile = self.get_object()
        serializer = BalanceUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            validated_data: Dict[str, Any] = cast(Dict[str, Any], serializer.validated_data)
            amount = validated_data['amount']
            description = validated_data.get('description', 'Balance removed by admin')
            
            # Check if user has sufficient balance or is an admin
            if profile.balance < amount and not profile.user.is_staff:
                return Response(
                    {'error': 'Insufficient balance to remove. Only admin users can have a negative balance.'},
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
            
            # Update the user's balance
            profile.balance -= amount
            profile.save()
            
            return Response({
                'message': f'Removed {amount} from {profile.user.username}\'s balance',
                'transaction_id': transaction.id,
                'new_balance': profile.balance
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 