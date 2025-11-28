from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import profile

urlpatterns = [
    path("admin/", admin.site.urls),

    # JWT Auth
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Profile
    path("api/profile/", profile, name="profile"),
    path('api/raw_material/', include('raw_material.urls')),
    path('api/forging/', include('forging.urls')),
    path('api/heat_treatment/', include('heat_treatment.urls')),
    path('api/pre_mc/', include('pre_mc.urls')),
    path('api/machining/', include('machining.urls')),
    path('api/fi/', include('fi.urls')),
    path('api/marking/', include('marking.urls')),
    path('api/visual/', include('visual.urls')),
    path('api/dispatch/', include('dispatch.urls')),
    path('api/packing_area_inventory/', include('packing_area_inventory.urls')),
    path('api/ims_documents/', include('ims_documents.urls'))

]
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)