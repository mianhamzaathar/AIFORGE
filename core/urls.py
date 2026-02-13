from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('content/', include('content.urls')),
    path('image/', include('image.urls')),
    path('resume/', include('resume.urls')),
   path('code/', include('codehelper.urls')),

    path('subscription/', include('subscription.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


