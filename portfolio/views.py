from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from core.docs.response import RESPONSE_404
from core.docs.schema_utils import auto_schema_view
from core.permission import IsOwner
from portfolio.docs.schemas import ISLAND_CREATE_SCHEMA, ISLAND_DESTROY_SCHEMA, ISLAND_LIST_SCHEMA, ISLAND_PARTIAL_UPDATE_SCHEMA, ISLAND_RETRIEVE_SCHEMA, ISLAND_TEMPLATE_LIST_SCHEMA, ISLAND_TEMPLATE_RETRIEVE_SCHEMA, ISLAND_UPDATE_SCHEMA, MODULE_CREATE_SCHEMA, MODULE_DESTROY_SCHEMA, MODULE_LIST_SCHEMA, MODULE_PARTIAL_UPDATE_SCHEMA, MODULE_RETRIEVE_SCHEMA, MODULE_UPDATE_SCHEMA

from .models import IslandTemplate, Module, Island
from .serializers import IslandTemplateSerializer, ModuleSerializer, IslandSerializer

@auto_schema_view(
    list=ISLAND_TEMPLATE_LIST_SCHEMA,
    retrieve=ISLAND_TEMPLATE_RETRIEVE_SCHEMA,
)
class IslandTemplateViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             viewsets.GenericViewSet):
    """Read-only catalog (Nu, Mercado Pago, SPY...). Managed by admins only,
    via Django admin — not writable through this API.
    """
    queryset = IslandTemplate.objects.all()
    serializer_class = IslandTemplateSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["kind"]
    search_fields = ["name", "symbol"]

@auto_schema_view(
    list=MODULE_LIST_SCHEMA,
    retrieve=MODULE_RETRIEVE_SCHEMA,
    create=MODULE_CREATE_SCHEMA,
    update=MODULE_UPDATE_SCHEMA,
    partial_update=MODULE_PARTIAL_UPDATE_SCHEMA,
    destroy=MODULE_DESTROY_SCHEMA,
)
class ModuleViewSet(viewsets.ModelViewSet):
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated, IsOwner]
 
    def get_queryset(self):
        # Never trust a client-supplied user filter — scope to request.user always.
        # prefetch avoids N+1 when ModuleSerializer sums each island's summary.
        return (
            Module.objects
            .filter(user=self.request.user)
            .prefetch_related("islands__transactions")
        )
 
@auto_schema_view(
    list=ISLAND_LIST_SCHEMA,
    retrieve=ISLAND_RETRIEVE_SCHEMA,
    create=ISLAND_CREATE_SCHEMA,
    update=ISLAND_UPDATE_SCHEMA,
    partial_update=ISLAND_PARTIAL_UPDATE_SCHEMA,
    destroy=ISLAND_DESTROY_SCHEMA,
)
class IslandViewSet(viewsets.ModelViewSet):
    serializer_class = IslandSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_fields = ["module", "kind"]
 
    def get_queryset(self):
        return (
            Island.objects
            .filter(user=self.request.user)
            .select_related("module", "template")
            .prefetch_related("transactions")  # avoid N+1 when computing summary
        )