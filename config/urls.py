"""
URL configuration for ERP Backend.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# API Documentation with drf-yasg
schema_view = get_schema_view(
    openapi.Info(
        title="ERP System API",
        default_version='v1',
        description="API documentation for ERP System Backend",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="contact@erp-system.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API endpoints
    path('api/auth/', include('apps.authentication.urls')),
    path('api/hrm/', include('apps.hrm.urls')),
    path('api/inventory/', include('apps.inventory.urls')),
    path('api/sales/', include('apps.sales.urls')),
    path('api/finance/', include('apps.finance.urls')),
    path('api/reports/', include('apps.reports.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

# Customize admin site
admin.site.site_header = "ERP System Administration"
admin.site.site_title = "ERP Admin"
admin.site.index_title = "Welcome to ERP System Admin Portal"
