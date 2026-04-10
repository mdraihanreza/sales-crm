from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static


def root_view(request):
    return JsonResponse(
        {
            "service": "Sales CRM API",
            "status": "ok",
            "admin_url": "/admin/",
            "api_base": "/api/",
            "frontend_url": "http://localhost:5173",
        }
    )

urlpatterns = [
    path("", root_view, name="root"),
    path("admin/", admin.site.urls),
    path("api/", include("users.urls")),
    path("api/", include("bids.urls")),
    path("api/", include("chat.urls")),
    path("api/", include("leads.urls")),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
