from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import qrcode  # type: ignore
from io import BytesIO
from django.core.files import File
from PIL import Image
from decimal import Decimal

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'),
                                validators=[MinValueValidator(0)])
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def generate_qr_code(self):
        qr = qrcode.QRCode(  # type: ignore
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,  # type: ignore
            box_size=10,
            border=4,
        )
        qr.add_data(str(self.user.id))
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        if self.qr_code:
            self.qr_code.delete()
            
        self.qr_code.save(
            f'qr_code_{self.user.id}.png',
            File(buffer),
            save=False
        )

    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs) 