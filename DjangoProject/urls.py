
from django.contrib import admin
from django.urls import path, include

from DjangoProject.settings import BASE_DIR


from django.conf import settings
from django.conf.urls.static import static


from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('chat/', include('chat.urls')),
    path('orders/', include('orders.urls')),
    path('users/', include('users.urls')),
    path('products/', include('products.urls')),
    path('content/', include('content.urls')),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#временно потом заменить на Nginx или Apache
#urlpatterns += [
#    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
#    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
#]

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]