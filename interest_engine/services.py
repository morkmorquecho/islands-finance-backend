from datetime import date
from decimal import Decimal
from market_data.services import convert_to_base

from django.utils import timezone


def daily_rate_for(island) -> Decimal:
    rate = island.annual_rate or Decimal("0")
    return rate / Decimal("360")


def cash_value_from_rows(rows, as_of: date, daily_rate: Decimal):
    """Compounded value and net principal as of `as_of`.

    `rows` is an iterable of (type, amount, date) tuples. Shared by the
    summary and by the funds validation so both agree on the balance.
    Returns (value, deposited).
    """
    value = Decimal("0")
    deposited = Decimal("0")
    for tx_type, amount, tx_date in rows:
        if tx_date > as_of:
            continue
        signed_amount = amount if tx_type == "deposit" else -amount
        days = (as_of - tx_date).days
        value += signed_amount * (1 + daily_rate) ** Decimal(days)
        deposited += signed_amount
    return value, deposited


def calculate_cash_island_value(island, as_of: date = None) -> dict:
    as_of = as_of or timezone.localdate()

    rows = island.transactions.filter(date__lte=as_of).values_list(
        "type", "amount", "date"
    )
    value, deposited = cash_value_from_rows(rows, as_of, daily_rate_for(island))

    return {
        "deposited": deposited,
        "currency": island.currency,
        "value_native": value,
        "value_base": convert_to_base(value, island.currency),
        "interest_earned": value - deposited,
    }


def calculate_asset_island_value(island, as_of: date = None) -> dict:
    from market_data.services import get_price

    quantity = Decimal("0")
    cost_basis = Decimal("0")

    for tx in island.transactions.filter(type__in=["buy", "sell"]).only(
        "type", "quantity", "price_at_tx"
    ):
        if tx.type == "buy":
            quantity += tx.quantity
            cost_basis += tx.quantity * tx.price_at_tx
        else:
            quantity -= tx.quantity
            cost_basis -= tx.quantity * tx.price_at_tx

    price = (
        get_price(island.symbol, island.asset_type, getattr(island, "mic_code", None))
        if quantity > 0
        else Decimal("0")
    )
    price_unavailable = quantity > 0 and price == 0

    if price_unavailable:
        value_native = None
        value_base = None
        gain_loss = None
    else:
        value_native = quantity * price
        value_base = convert_to_base(value_native, island.currency)
        gain_loss = value_native - cost_basis

    return {
        "quantity": quantity,
        "currency": island.currency,
        "value_native": value_native,
        "value_base": value_base,
        "cost_basis": cost_basis,
        "gain_loss": gain_loss,
        "price_unavailable": price_unavailable,
    }


def get_island_summary(island, as_of: date = None) -> dict:
    """Single entrypoint — picks cash vs asset logic based on island.kind."""
    if island.kind == "cash":
        return calculate_cash_island_value(island, as_of=as_of)
    return calculate_asset_island_value(island, as_of=as_of)