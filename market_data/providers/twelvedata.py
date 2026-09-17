from decouple import config

import requests
from django.conf import settings

from market_data.exceptions import PriceNotFoundError, ProviderUnavailableError

BASE_URL = "https://api.twelvedata.com/price"
TIMEOUT = 5

TWELVEDATA_API_KEY = config("TWELVEDATA_API_KEY")

def get_price(symbol: str, mic_code: str | None = None) -> float:
    params = {"symbol": symbol, "apikey": TWELVEDATA_API_KEY}
    if mic_code:
        params["mic_code"] = mic_code
    try:
        response = requests.get(BASE_URL, params=params, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ProviderUnavailableError(f"Twelve Data request failed: {exc}") from exc

    data = response.json()
    if data.get("status") == "error" or "price" not in data:
        message = data.get("message", "unknown error")
        if "not found" in message.lower() or "invalid" in message.lower():
            raise PriceNotFoundError(f"Twelve Data: no price for '{symbol}' ({message})")
        raise ProviderUnavailableError(f"Twelve Data error: {message}")

    return float(data["price"])


def search_symbols(query: str) -> list[dict]:
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
    results = []
    for s in data[:10]:
        currency = s.get("currency")
        if not currency:
            currency = "MXN" if s["symbol"].endswith(".MX") else None
        results.append({
            "symbol": s["symbol"],
            "name": s["instrument_name"],
            "exchange": s.get("exchange"),
            "mic_code": s.get("mic_code"),  # nuevo
            "currency": currency,
        })
    return results