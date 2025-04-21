from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import DashboardStatsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/transactions/', include('transactions.urls')),
    path('api/vendors/', include('vendors.urls')),
    path('api/dashboard/stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 