from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from typing import cast, TYPE_CHECKING

if TYPE_CHECKING:
    from accounts.models import UserProfile
    User.profile = property(lambda self: cast('UserProfile', self.profile))

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('PAYMENT', 'Payment'),
        ('TOP_UP', 'Top Up'),
        ('REFUND', 'Refund'),
    )

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    )

    sender = models.ForeignKey(User, on_delete=models.PROTECT, related_name='sent_transactions')
    receiver = models.ForeignKey(User, on_delete=models.PROTECT, related_name='received_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_type} Transaction - {self.amount} from {self.sender.username} to {self.receiver.username}"

    def save(self, *args, **kwargs):
        if self.status == 'COMPLETED':
            if self.transaction_type == 'PAYMENT':
                self.sender.profile.balance -= self.amount  # type: ignore
                self.receiver.profile.balance += self.amount  # type: ignore
            elif self.transaction_type == 'TOP_UP':
                self.receiver.profile.balance += self.amount  # type: ignore
            elif self.transaction_type == 'REFUND':
                self.sender.profile.balance += self.amount  # type: ignore
                self.receiver.profile.balance -= self.amount  # type: ignore

            self.sender.profile.save()  # type: ignore
            self.receiver.profile.save()  # type: ignore

        super().save(*args, **kwargs) 