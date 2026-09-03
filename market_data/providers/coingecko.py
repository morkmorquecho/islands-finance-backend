import requests

from market_data.exceptions import PriceNotFoundError, ProviderUnavailableError

BASE_URL = "https://api.coingecko.com/api/v3/simple/price"
TIMEOUT = 5


def get_price(symbol: str) -> float:
    """`symbol` here must be a CoinGecko coin id (e.g. "bitcoin"), not a
    ticker (e.g. "BTC") — CoinGecko's free /simple/price endpoint only
    accepts ids. See notes in services.py about this mismatch.
    """
    try:
        response = requests.get(
            BASE_URL,
            params={"ids": symbol.lower(), "vs_currencies": "usd"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ProviderUnavailableError(f"CoinGecko request failed: {exc}") from exc

    data = response.json()
    coin_data = data.get(symbol.lower())
    if not coin_data or "usd" not in coin_data:
        raise PriceNotFoundError(f"CoinGecko has no price for '{symbol}'")

    return coin_data["usd"]

def search_coins(query: str) -> list[dict]:
    """Returns [{"id": "bitcoin", "name": "Bitcoin", "symbol": "btc"}, ...]
    `id` is what you store in Island.symbol — that's what /simple/price expects.
    """
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/search",
            params={"query": query},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ProviderUnavailableError(f"CoinGecko search failed: {exc}") from exc

    coins = response.json().get("coins", [])
    return [
        {"id": c["id"], "name": c["name"], "symbol": c["symbol"], "currency": "USD"}
        for c in coins[:10]
    ]