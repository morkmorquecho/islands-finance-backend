from decimal import Decimal

from django.core.exceptions import ValidationError

from .models import Transaction

# Which types move the balance up vs down, per island kind.
CASH_INFLOW = {Transaction.Type.DEPOSIT}
CASH_OUTFLOW = {Transaction.Type.WITHDRAWAL, Transaction.Type.EXPENSE}
ASSET_INFLOW = {Transaction.Type.BUY}
ASSET_OUTFLOW = {Transaction.Type.SELL}


def current_cash_balance(island) -> Decimal:
    """Raw sum of amounts (deposits minus withdrawals/expenses), no interest.
    Used only to check "can this withdrawal actually happen?" — NOT the
    number shown to the user (that's interest_engine's job, compounded).
    """
    total = Decimal("0")
    for tx in island.transactions.filter(
        type__in=CASH_INFLOW | CASH_OUTFLOW
    ).only("type", "amount"):
        if tx.type in CASH_INFLOW:
            total += tx.amount
        else:
            total -= tx.amount
    return total


def current_asset_quantity(island) -> Decimal:
    """Raw sum of quantity held (buys minus sells)."""
    total = Decimal("0")
    for tx in island.transactions.filter(
        type__in=ASSET_INFLOW | ASSET_OUTFLOW
    ).only("type", "quantity"):
        if tx.type in ASSET_INFLOW:
            total += tx.quantity
        else:
            total -= tx.quantity
    return total


def assert_sufficient_funds(island, tx_type, amount=None, quantity=None, exclude_pk=None):
    """Raise ValidationError if this transaction would overdraw the island.
    `exclude_pk` lets an update-in-place recheck without double-counting itself.
    """
    if tx_type in CASH_OUTFLOW:
        balance = current_cash_balance(island)
        if exclude_pk:
            prior = island.transactions.filter(pk=exclude_pk).first()
            if prior and prior.type in CASH_OUTFLOW:
                balance += prior.amount  # undo its own prior effect before recomputing
        if amount > balance:
            raise ValidationError(
                f"Insufficient balance: island has {balance}, tried to move {amount}."
            )

    elif tx_type in ASSET_OUTFLOW:
        held = current_asset_quantity(island)
        if exclude_pk:
            prior = island.transactions.filter(pk=exclude_pk).first()
            if prior and prior.type in ASSET_OUTFLOW:
                held += prior.quantity
        if quantity > held:
            raise ValidationError(
                f"Insufficient holdings: island has {held}, tried to sell {quantity}."
            )