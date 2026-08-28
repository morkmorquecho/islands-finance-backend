from datetime import timedelta

from django.utils import timezone

from .models import Goal, GoalCompletion


def sync_completions(goal: Goal, as_of=None) -> list[GoalCompletion]:
    """Ensure a GoalCompletion row exists for every expected period between
    goal.start_date and `as_of` (defaults to today). Cheap and idempotent —
    safe to call on every read (e.g. every time the goal detail is requested).
    No cron job needed: periods are derived purely from start_date +
    frequency_days, walked forward until they pass `as_of`.
    """
    as_of = as_of or timezone.localdate()

    existing_dates = set(
        goal.completions.values_list("expected_date", flat=True)
    )

    expected_date = goal.start_date
    to_create = []
    while expected_date <= as_of:
        if expected_date not in existing_dates:
            to_create.append(
                GoalCompletion(goal=goal, expected_date=expected_date)
            )
        expected_date += timedelta(days=goal.frequency_days)

    if to_create:
        GoalCompletion.objects.bulk_create(to_create, ignore_conflicts=True)

    return list(goal.completions.order_by("expected_date"))


def compliance_rate(goal: Goal, as_of=None) -> float:
    """Fraction of expected periods (up to as_of) that were fulfilled."""
    completions = sync_completions(goal, as_of=as_of)
    if not completions:
        return 0.0
    fulfilled = sum(1 for c in completions if c.completed_date is not None)
    return fulfilled / len(completions)