from django.urls import path

from .views import asset_search

app_name = "market_data"

urlpatterns = [
    path("assets/search/", asset_search, name="asset-search"),
]