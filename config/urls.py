"""
URL configuration for ALFA ERP Backend
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/auth/', include('apps.accounts.urls')),
    # Access control endpoints (menus, assignments)
    path('api/access/', include('apps.accesscontrol.urls')),
    
    path('api/sales/',include('apps.sales.urls')),
    
    # Analytics endpoints
    path('api/analytics/', include('apps.analytics.urls')),
    
    # Common/Developer endpoints
    path('api/', include('apps.common.urls'))
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
