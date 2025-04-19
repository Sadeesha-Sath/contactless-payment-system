from rest_framework import serializers
from .models import Transaction
from accounts.serializers import UserSerializer

class TransactionSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    sender_id = serializers.IntegerField(write_only=True)
    receiver_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'sender', 'receiver', 'sender_id', 'receiver_id', 
            'amount', 'transaction_type', 'status', 'description', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def validate(self, data):
        # Ensure sender has sufficient balance for payment
        if data.get('transaction_type') == 'PAYMENT':
            sender = data.get('sender_id')
            amount = data.get('amount')
            
            if sender and amount:
                from django.contrib.auth.models import User
                user = User.objects.get(id=sender)
                if user.profile.balance < amount:
                    raise serializers.ValidationError(
                        {"amount": "Insufficient balance for this transaction"}
                    )
        
        return data

class PaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True)
    receiver_id = serializers.IntegerField() 