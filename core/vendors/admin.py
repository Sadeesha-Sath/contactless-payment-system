from django.contrib import admin
from .models import Vendor, VendorTransaction

class VendorTransactionInline(admin.TabularInline):
    model = VendorTransaction
    extra = 0
    readonly_fields = ('transaction_date',)

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'contact_number', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('business_name', 'user__username', 'contact_number')
    inlines = [VendorTransactionInline]
    readonly_fields = ('created_at', 'updated_at')

@admin.register(VendorTransaction)
class VendorTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'vendor', 'amount', 'transaction_date')
    list_filter = ('transaction_date',)
    search_fields = ('vendor__business_name', 'description')
    readonly_fields = ('transaction_date',)
    ordering = ('-transaction_date',) 