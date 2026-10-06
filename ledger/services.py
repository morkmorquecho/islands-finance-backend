from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError

from interest_engine.services import cash_value_from_rows, daily_rate_for

from .models import Transaction

# Which types move the balance up vs down, per island kind.
CASH_INFLOW = {Transaction.Type.DEPOSIT}
CASH_OUTFLOW = {Transaction.Type.WITHDRAWAL, Transaction.Type.EXPENSE}
ASSET_INFLOW = {Transaction.Type.BUY}
ASSET_OUTFLOW = {Transaction.Type.SELL}

CENT = Decimal("0.01")


def _cash_rows(island, exclude_pk=None) -> list:
    """(type, amount, date) for every cash movement, optionally minus one tx."""
    qs = island.transactions.filter(type__in=CASH_INFLOW | CASH_OUTFLOW)
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)
    return list(qs.values_list("type", "amount", "date"))


def current_cash_balance(island, as_of: date = None, exclude_pk=None) -> Decimal:
    """Balance WITH compounded interest as of `as_of` (default: today).

    Same math as interest_engine, so the validation and the number shown
    to the user can never disagree.
    """
    from django.utils import timezone

    as_of = as_of or timezone.localdate()
    value, _ = cash_value_from_rows(
        _cash_rows(island, exclude_pk), as_of, daily_rate_for(island)
    )
    return value


def current_asset_quantity(island, exclude_pk=None) -> Decimal:
    """Raw sum of quantity held (buys minus sells)."""
    qs = island.transactions.filter(type__in=ASSET_INFLOW | ASSET_OUTFLOW)
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)

    total = Decimal("0")
    for tx in qs.only("type", "quantity"):
        if tx.type in ASSET_INFLOW:
            total += tx.quantity
        else:
            total -= tx.quantity
    return total


def _assert_cash_timeline_valid(island, tx_type, amount, tx_date, exclude_pk=None):
    """Check the compounded balance never goes negative because of this tx.

    1. If it's an outflow, the island must cover it (interest included)
       on the transaction's own date.
    2. From the earliest affected date onward, every withdrawal/expense
       date must still be covered. This catches backdated withdrawals and
       edits that shrink an earlier deposit.
    """
    daily_rate = daily_rate_for(island)
    base_rows = _cash_rows(island, exclude_pk)

    # Earliest date this change can influence (also covers edits that move the date).
    earliest = tx_date
    if exclude_pk:
        prior = island.transactions.filter(pk=exclude_pk).values_list("date", flat=True).first()
        if prior and prior < earliest:
            earliest = prior

    # 1) Direct check: can this outflow happen on its own date?
    if tx_type in CASH_OUTFLOW:
        available, _ = cash_value_from_rows(base_rows, tx_date, daily_rate)
        if amount.quantize(CENT) > available.quantize(CENT):
            raise ValidationError(
                f"Insufficient balance: island has {available.quantize(CENT)} "
                f"(interest included) on {tx_date}, tried to move {amount}."
            )

    # 2) Timeline check with the new/edited tx included.
    rows = base_rows + [(tx_type, amount, tx_date)]
    check_dates = sorted(
        {d for t, _, d in rows if t in CASH_OUTFLOW and d >= earliest}
    )
    for d in check_dates:
        value, _ = cash_value_from_rows(rows, d, daily_rate)
        if value.quantize(CENT) < 0:
            raise ValidationError(
                f"This change would leave the island with a negative balance "
                f"({value.quantize(CENT)}) on {d}."
            )


def assert_sufficient_funds(
    island, tx_type, amount=None, quantity=None, tx_date=None, exclude_pk=None
):
    """Raise ValidationError if this transaction would overdraw the island.

    Cash islands: validated against the balance *with compounded interest*
    on `tx_date`. Asset islands: validated against quantity held.
    `exclude_pk` lets an update-in-place recheck without double-counting itself.
    """
    if tx_type in CASH_INFLOW | CASH_OUTFLOW:
        if amount is None or tx_date is None:
            return  # required-field errors are raised elsewhere

        # Inflows only need rechecking when editing an existing tx
        # (lowering a deposit or moving its date can break later withdrawals).
        if tx_type in CASH_OUTFLOW or exclude_pk:
            _assert_cash_timeline_valid(island, tx_type, amount, tx_date, exclude_pk)

    elif tx_type in ASSET_OUTFLOW:
        held = current_asset_quantity(island, exclude_pk=exclude_pk)
        if quantity > held:
            raise ValidationError(
                f"Insufficient holdings: island has {held}, tried to sell {quantity}."
            )