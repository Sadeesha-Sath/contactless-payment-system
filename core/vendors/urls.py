from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VendorViewSet, VendorTransactionViewSet

router = DefaultRouter()
router.register(r'vendors', VendorViewSet, basename='vendor')
router.register(r'transactions', VendorTransactionViewSet, basename='vendor-transaction')

urlpatterns = [
    path('', include(router.urls)),
] 