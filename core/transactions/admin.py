from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'amount', 'transaction_type', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('sender__username', 'receiver__username', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',) 