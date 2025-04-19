from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

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