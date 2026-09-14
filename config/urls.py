from django.contrib import admin
from django.urls import include, path

from auth.urls import authentications_patterns
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from users.urls import user_path
from django.conf import settings
from django.conf.urls.static import static

from portfolio.urls import urlpatterns as portfolio_patterns
from goals.urls import urlpatterns as goals_patterns
from ledger.urls import urlpatterns as ledgers_patterns
from market_data.urls import urlpatterns as market_data_patterns


def trigger_error(request):
    division_by_zero = 1 / 0


api_v1_patterns = [
    path("auth/", include(authentications_patterns)),
    path("users/", include(user_path)),
    path("portfolio/", include(portfolio_patterns)),
    path("goals/", include(goals_patterns)),
    path("transactions/", include(ledgers_patterns)),
    path("market-data/", include(market_data_patterns)),
]


urlpatterns = [
    path("admin/", admin.site.urls),
    path("sentry-debug/", trigger_error),
    path("api/v1/", include(api_v1_patterns)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("accounts/", include("allauth.urls")),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )