from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.docs.schema_utils import auto_schema_view
from core.permission import IsOwner

from .models import Transaction
from .serializers import TransactionSerializer
from .docs.schemas import (
    TRANSACTION_CREATE_SCHEMA,
    TRANSACTION_DESTROY_SCHEMA,
    TRANSACTION_LIST_SCHEMA,
    TRANSACTION_PARTIAL_UPDATE_SCHEMA,
    TRANSACTION_RETRIEVE_SCHEMA,
    TRANSACTION_UPDATE_SCHEMA,
)

@auto_schema_view(
    list=TRANSACTION_LIST_SCHEMA,
    retrieve=TRANSACTION_RETRIEVE_SCHEMA,
    create=TRANSACTION_CREATE_SCHEMA,
    update=TRANSACTION_UPDATE_SCHEMA,
    partial_update=TRANSACTION_PARTIAL_UPDATE_SCHEMA,
    destroy=TRANSACTION_DESTROY_SCHEMA,
)
class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_fields = ["island", "type", "category"]
    # lets the frontend do e.g. ?date__gte=2026-01-01&date__lte=2026-01-31
    # for a given month's transactions or expense report range
    ordering_fields = ["date", "created_at"]

    def get_queryset(self):
        # Never trust a client-supplied user filter — scope to request.user always.
        return (
            Transaction.objects
            .filter(user=self.request.user)
            .select_related("island")
        )