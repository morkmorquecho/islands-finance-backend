from datetime import date
from decimal import Decimal
from market_data.services import convert_to_base

from django.utils import timezone


def calculate_cash_island_value(island, as_of: date = None) -> dict:

    as_of = as_of or timezone.localdate()
    rate = island.annual_rate or Decimal("0")

    deposited = Decimal("0")
    value = Decimal("0")

    for tx in island.transactions.filter(date__lte=as_of).only("type", "amount", "date"):
        signed_amount = tx.amount if tx.type == "deposit" else -tx.amount
        days = (as_of - tx.date).days
        growth = signed_amount * (1 + rate) ** (Decimal(days) / Decimal(365))
        value += growth
        deposited += signed_amount

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

    price = get_price(island.symbol, island.asset_type) if quantity > 0 else Decimal("0")
    value_native = quantity * price
    value_base = convert_to_base(value_native, island.currency)

    return {
        "quantity": quantity,
        "currency": island.currency,
        "value_native": value_native,
        "value_base": value_base,
        "cost_basis": cost_basis,
        "gain_loss": value_native - cost_basis,
    }


def get_island_summary(island, as_of: date = None) -> dict:
    """Single entrypoint — picks cash vs asset logic based on island.kind."""
    if island.kind == "cash":
        return calculate_cash_island_value(island, as_of=as_of)
    return calculate_asset_island_value(island, as_of=as_of)