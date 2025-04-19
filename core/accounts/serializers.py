from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile
from vendors.models import Vendor
import csv
from io import TextIOWrapper
from decimal import Decimal

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    qr_code_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'balance', 'qr_code_url', 'created_at', 'updated_at']
        read_only_fields = ['id', 'qr_code_url', 'created_at', 'updated_at']

    def get_qr_code_url(self, obj):
        request = self.context.get('request')
        if obj.qr_code and request is not None and hasattr(request, 'build_absolute_uri'):
            return request.build_absolute_uri(obj.qr_code.url)
        return None

class BalanceUpdateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True)

class BatchUserCreationSerializer(serializers.Serializer):
    csv_file = serializers.FileField(required=True)
    
    def validate_csv_file(self, value):
        # Check if the file is a CSV
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("Only CSV files are allowed.")
        
        # Check file size (limit to 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size must be less than 5MB.")
        
        return value
    
    def process_csv(self, csv_file):
        """Process the CSV file and create users"""
        results = {
            'success': [],
            'errors': []
        }
        
        # Read the CSV file
        csv_file = TextIOWrapper(csv_file, encoding='utf-8')
        reader = csv.DictReader(csv_file)
        
        # Check required fields
        required_fields = ['username', 'email', 'password', 'user_type']
        for field in required_fields:
            if field not in reader.fieldnames:
                results['errors'].append(f"CSV file is missing required field: {field}")
                return results
        
        # Process each row
        for row_num, row in enumerate(reader, start=2):  # Start from 2 to account for header row
            try:
                # Extract user data
                username = row.get('username', '').strip()
                email = row.get('email', '').strip()
                password = row.get('password', '').strip()
                user_type = row.get('user_type', '').strip().upper()
                first_name = row.get('first_name', '').strip()
                last_name = row.get('last_name', '').strip()
                initial_balance = row.get('initial_balance', '0.00').strip()
                
                # Validate required fields
                if not username or not email or not password or not user_type:
                    results['errors'].append(f"Row {row_num}: Missing required fields")
                    continue
                
                # Validate user type
                if user_type not in ['USER', 'VENDOR']:
                    results['errors'].append(f"Row {row_num}: Invalid user_type. Must be 'USER' or 'VENDOR'")
                    continue
                
                # Check if user already exists
                if User.objects.filter(username=username).exists():
                    results['errors'].append(f"Row {row_num}: Username '{username}' already exists")
                    continue
                
                if User.objects.filter(email=email).exists():
                    results['errors'].append(f"Row {row_num}: Email '{email}' already exists")
                    continue
                
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Create user profile with initial balance
                try:
                    initial_balance_decimal = Decimal(initial_balance)
                except:
                    initial_balance_decimal = Decimal('0.00')
                
                profile = UserProfile.objects.create(
                    user=user,
                    balance=initial_balance_decimal
                )
                
                # If user is a vendor, create vendor profile
                if user_type == 'VENDOR':
                    vendor_name = row.get('vendor_name', username).strip()
                    vendor_description = row.get('vendor_description', '').strip()
                    
                    Vendor.objects.create(
                        user=user,
                        name=vendor_name,
                        description=vendor_description
                    )
                
                results['success'].append(f"Row {row_num}: Created {user_type.lower()} '{username}'")
                
            except Exception as e:
                results['errors'].append(f"Row {row_num}: Error - {str(e)}")
        
        return results 