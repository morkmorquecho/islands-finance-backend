class MarketDataError(Exception):
    """Base exception for any provider failure."""


class PriceNotFoundError(MarketDataError):
    """Symbol doesn't exist / provider returned no data for it."""


class ProviderUnavailableError(MarketDataError):
    """Network error, timeout, rate limit, or bad response shape."""