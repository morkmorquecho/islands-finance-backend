import requests
from django.conf import settings

from market_data.exceptions import PriceNotFoundError, ProviderUnavailableError

BASE_URL = "https://api.twelvedata.com/price"
TIMEOUT = 5


def get_price(symbol: str) -> float:
    """`symbol` is a ticker, e.g. "SPY", "VOO", or "AMXL.MX" for BMV."""
    try:
        response = requests.get(
            BASE_URL,
            params={"symbol": symbol, "apikey": settings.TWELVEDATA_API_KEY},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ProviderUnavailableError(f"Twelve Data request failed: {exc}") from exc

    data = response.json()

    # Twelve Data returns 200 OK even on errors (invalid symbol, rate limit),
    # with the error inside the body instead of the HTTP status.
    if data.get("status") == "error" or "price" not in data:
        message = data.get("message", "unknown error")
        if "not found" in message.lower() or "invalid" in message.lower():
            raise PriceNotFoundError(f"Twelve Data: no price for '{symbol}' ({message})")
        raise ProviderUnavailableError(f"Twelve Data error: {message}")

    return float(data["price"])


def search_symbols(query: str) -> list[dict]:
    """Returns [{"symbol": "AMXL.MX", "name": "America Movil", "exchange": "BMV"}, ...]
    `symbol` is what you store in Island.symbol.
    """
    try:
        response = requests.get(
            "https://api.twelvedata.com/symbol_search",
            params={"symbol": query},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ProviderUnavailableError(f"Twelve Data search failed: {exc}") from exc

    data = response.json().get("data", [])
    return [
        {"symbol": s["symbol"], "name": s["instrument_name"], "exchange": s.get("exchange"), "currency": s.get("currency")}
        for s in data[:10]
    ]