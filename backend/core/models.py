import uuid
from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Account(models.Model):
    account_number = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"Account for {self.user.username}"

class Vendor(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True, verbose_name='Vendor_ID')
    # Assuming a vendor is also a user, we can link to the User model
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendors')
    # Add any additional vendor-specific fields here, e.g., store name, address
    store_name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Vendor: {self.user.username}"

class Item(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True, verbose_name='Item_ID')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    # Add other item details like stock, image, etc.

    def __str__(self):
        return f"{self.name} ({self.vendor.store_name or self.vendor.user.username})"

class Order(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True, verbose_name='Order_ID')
    items = models.ManyToManyField(Item, through='OrderItems')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='orders')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('partially_paid', 'Partially Paid'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    ], default='pending')
    order_type = models.CharField(max_length=50, choices=[
        ('pre-order', 'Purchase'),
        ('discount', 'Discount'),
        ('normal', 'Normal'),
    ], default='normal')
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    def __str__(self):
        return f"Order {self.id} - {self.items.count()} items"


class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item.name} in Order {self.order.id}"
    

class Transaction(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True, verbose_name='Transaction_ID')
    sender_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='sent_transactions')
    receiver_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='received_transactions')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True) # Optional link to an item
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    transaction_type = models.CharField(max_length=50, choices=[
        ('transfer', 'Transfer'),
        ('purchase', 'Purchase'),
        ('refund', 'Refund'),
        ('withdrawal', 'Withdrawal'),
        ('deposit', 'Deposit'),
    ], default='transfer')

    def __str__(self):
        return f"Transaction {self.pk or 'unsaved'}: {self.sender_account.user.username} -> {self.receiver_account.user.username} ({self.amount})"


