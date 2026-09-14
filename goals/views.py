from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.docs.schema_utils import auto_schema_view
from core.permission import IsOwner
from goals.docs.schemas import GOAL_COMPLETIONS_SCHEMA, GOAL_CREATE_SCHEMA, GOAL_DESTROY_SCHEMA, GOAL_LIST_SCHEMA, GOAL_PARTIAL_UPDATE_SCHEMA, GOAL_RETRIEVE_SCHEMA, GOAL_UPDATE_SCHEMA,GOAL_MARK_COMPLETION_SCHEMA
from .models import Goal
from .serializers import (
    GoalSerializer,
    GoalCompletionSerializer,
    GoalCompletionMarkSerializer,
)
from .services import sync_completions, compliance_rate

@auto_schema_view(
    list=GOAL_LIST_SCHEMA,
    retrieve=GOAL_RETRIEVE_SCHEMA,
    create=GOAL_CREATE_SCHEMA,
    update=GOAL_UPDATE_SCHEMA,
    partial_update=GOAL_PARTIAL_UPDATE_SCHEMA,
    destroy=GOAL_DESTROY_SCHEMA,
    completions=GOAL_COMPLETIONS_SCHEMA,
    mark_completion=GOAL_MARK_COMPLETION_SCHEMA,
)
class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_fields = ["island", "active"]
 
    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user).select_related("island")
 
    @action(detail=True, methods=["get"])
    def completions(self, request, pk=None):
        """List all expected periods up to today, generating any missing
        rows on the fly (no cron job — see goals/services.py).
        """
        goal = self.get_object()
        rows = sync_completions(goal, as_of=timezone.localdate())
        return Response({
            "compliance_rate": compliance_rate(goal),
            "results": GoalCompletionSerializer(rows, many=True).data,
        })
 
    @action(detail=True, methods=["post"], url_path="completions/mark")
    def mark_completion(self, request, pk=None):
        """Mark a specific expected period as fulfilled.
 
        This always results in a real ledger.Transaction being linked —
        either one the user already logged (`transaction_id` given), or one
        created here automatically for `actual_amount` / target_amount.
        A completion is never just a label with no money behind it.
        """
        goal = self.get_object()
        payload = GoalCompletionMarkSerializer(
            data=request.data, context={"request": request}
        )
        payload.is_valid(raise_exception=True)
        data = payload.validated_data
 
        # ensure the row exists (covers periods not yet synced)
        sync_completions(goal, as_of=data["expected_date"])
        completion = goal.completions.get(expected_date=data["expected_date"])
 
        if completion.completed_date is not None:
            raise serializers.ValidationError(
                "This period is already marked as completed."
            )
 
        tx = data.get("transaction")
        amount = data.get("actual_amount") or goal.target_amount
 
        with db_transaction.atomic():
            if tx is None:
                # No existing transaction linked — create the real deposit
                # here, so "completed" always means money actually moved.
                tx = Transaction.objects.create(
                    island=goal.island,
                    user=request.user,
                    type=Transaction.Type.DEPOSIT,
                    date=timezone.localdate(),
                    amount=amount,
                    note=f"Goal fulfillment for {data['expected_date']}",
                )
 
            completion.completed_date = timezone.localdate()
            completion.transaction = tx
            completion.actual_amount = amount
            completion.save()
 
        return Response(GoalCompletionSerializer(completion).data)
 