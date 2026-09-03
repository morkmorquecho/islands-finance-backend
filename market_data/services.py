import logging
from decimal import Decimal

from django.core.cache import cache

from market_data.exceptions import MarketDataError
from market_data.providers import banxico, coingecko, twelvedata

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 300  # 5 min — adjust based on how tight the free-tier limits get
BASE_CURRENCY = "MXN"
RATE_CACHE_TIMEOUT = 60 * 60 * 24

_PROVIDERS = {
    "crypto": coingecko.get_price,
    "stock": twelvedata.get_price,
}


def get_price(symbol: str, asset_type: str) -> Decimal:
    """Looks up the current price for `symbol`, dispatching to the right
    provider based on `asset_type` (island.asset_type — no guessing).

    Returns Decimal("0") on any failure — same contract as the original
    placeholder: 0 means "price unavailable", not a real zero value. The
    frontend is responsible for treating 0 as unavailable.
    """
    provider = _PROVIDERS.get(asset_type)
    if provider is None:
        logger.error("get_price called with unknown asset_type=%s", asset_type)
        return Decimal("0")

    cache_key = f"market_data:price:{asset_type}:{symbol}"
    cached = cache.get(cache_key)
    if cached is not None:
        return Decimal(str(cached))

    try:
        price = provider(symbol)
    except MarketDataError as exc:
        logger.warning("Price lookup failed for %s (%s): %s", symbol, asset_type, exc)
        return Decimal("0")

    decimal_price = Decimal(str(price))
    cache.set(cache_key, str(decimal_price), timeout=CACHE_TIMEOUT)
    return decimal_price


def search_assets(query: str, asset_type: str) -> list[dict]:
    if asset_type == "crypto":
        return coingecko.search_coins(query)
    elif asset_type == "stock":
        return twelvedata.search_symbols(query)
    return []

def get_exchange_rate(from_currency: str, to_currency: str = BASE_CURRENCY) -> Decimal:
    if from_currency == to_currency:
        return Decimal("1")

    cache_key = f"market_data:fx:{from_currency}:{to_currency}"
    cached = cache.get(cache_key)
    if cached is not None:
        return Decimal(str(cached))

    try:
        if from_currency == "USD" and to_currency == "MXN":
            rate = banxico.get_usd_to_mxn()
        else:
            raise MarketDataError(f"Unsupported pair {from_currency}->{to_currency}")
    except MarketDataError as exc:
        logger.warning("Exchange rate lookup failed %s->%s: %s", from_currency, to_currency, exc)
        return Decimal("1")

    cache.set(cache_key, str(rate), timeout=RATE_CACHE_TIMEOUT)
    return rate


def convert_to_base(amount: Decimal, currency: str) -> Decimal:
    if not currency or currency == BASE_CURRENCY:
        return amount
    rate = get_exchange_rate(currency, BASE_CURRENCY)
    return amount * rate