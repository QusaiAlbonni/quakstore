from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib import admin
import debug_toolbar

admin.site.site_header = 'QuakStore Administration'

admin.site.site_title = 'QuakStore Admin site'

schema_view = get_schema_view(
	openapi.Info(
    	title="QuakStore API",
    	default_version='v1',
    	description="",
    	license=openapi.License(name="MIT License"),
   ),
	public=True,
	permission_classes=(permissions.IsAdminUser,),
)

urlpatterns = [
	path('admin/', admin.site.urls),
   	path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
  	path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   	path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
   	path('api/v1/', include('djoser.urls')),
   	path('api/v1/', include('djoser.urls.authtoken')),
	path('api/v1/', include('reviews.urls')),
   	path('api/v1/', include('product.urls')),
   	path('api/v1/', include('cart.urls')),
   	path('api/v1/', include('payment.urls')),
   	path('api/v1/', include('orders.urls')),
   	path('api/v1/', include('favorites.urls')),
   	path('webhooks/', include('payment.webhooks_urls')),
]
if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
	urlpatterns += [
		path('__debug__/', include(debug_toolbar.urls)),
	]