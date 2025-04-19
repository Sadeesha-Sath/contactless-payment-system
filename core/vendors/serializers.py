from rest_framework import serializers
from .models import Vendor, VendorTransaction
from accounts.serializers import UserSerializer

class VendorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Vendor
        fields = [
            'id', 'user', 'user_id', 'business_name', 'business_address', 
            'contact_number', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class VendorTransactionSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer(read_only=True)
    vendor_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = VendorTransaction
        fields = ['id', 'vendor', 'vendor_id', 'amount', 'transaction_date', 'description']
        read_only_fields = ['id', 'transaction_date'] 