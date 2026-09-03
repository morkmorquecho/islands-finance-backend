from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from market_data.services import search_assets


@api_view(["GET"])
def asset_search(request):
    query = request.query_params.get("q", "")
    asset_type = request.query_params.get("asset_type")
    if not query or asset_type not in ("crypto", "stock"):
        return Response({"detail": "q and asset_type (crypto|stock) are required"}, status=400)
    return Response(search_assets(query, asset_type))