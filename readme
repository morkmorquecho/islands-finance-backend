# 🏝️ Island Finance: Backend

REST API for **Island Finance**, a personal finance app built around an archipelago metaphor: financial modules are archipelagos and your accounts are islands.

> 🖥️ Frontend: [islands-finance-frontend](https://github.com/morkmorquecho/islands-finance-frontend)
> 🌐 Live app: [islandfinance.cc](https://islandfinance.cc)

This repository is public so you can see how I structure and build a production backend. It is not meant to be cloned and run.

## Features

- **Islands and archipelagos data model** to organize cash, stocks and crypto
- **Live market data** from CoinGecko (crypto), Twelve Data (stocks) and Banxico (exchange rates)
- **Asset search with autocomplete** across providers
- **Multi-currency support** with native and base-currency (MXN) values for clean aggregation
- **Interest projections** for cash islands, with an adjustable annual rate
- **Smart caching:** 5 minutes for prices, 24 hours for exchange rates
- **JWT authentication** with token refresh
- **Interactive API docs** generated from the OpenAPI schema
- **Error monitoring** with Sentry

## Stack

Python · Django · Django REST Framework · PostgreSQL · SimpleJWT · drf-spectacular · Docker · Gunicorn · Railway

## Engineering Decisions

**Explicit "price unavailable" instead of fake zeros.**
An early version returned `Decimal("0")` when a price could not be fetched, and downstream code treated it as a real price, producing false 100% losses and $0 totals. The fix was to propagate `None` / `price_unavailable` through the whole chain, so the UI can say "price not available" instead of showing wrong numbers.

**Native vs. base currency values.**
Each asset stores `value_native` and `value_base`, which lets a portfolio with crypto, USD stocks and MXN cash be aggregated in one currency without losing the original value.

**Disambiguating market symbols.**
The `Island` model carries an `asset_type` (crypto or stock) and a `mic_code` (e.g. `XMEX`), so symbol lookups on stock exchanges resolve to the right instrument.

**Accepting a provider limitation on purpose.**
The Twelve Data free plan does not cover some Mexican instruments. Instead of paying for a higher plan or stacking another provider, the app degrades gracefully and shows the price as unavailable.

**Validating the interest formula against reality.**
The cash-interest projection was tested against a real bank-app balance, comparing day-count conventions and compounding strategies, and keeping the nominal-rate approach with a user-adjustable rate.

**Isolated integrations.**
Third-party market providers live in their own `market_data` app, separate from the core finance logic, with cache TTLs tuned per data type.

## Where to Look

⚠️ VERIFICAR: ajusta las rutas a tu estructura real.

| Path | What you will find |
|------|--------------------|
| `market_data/` | Provider integrations, caching, asset search |
| `islands/` | Core models (islands, archipelagos) and serializers |
| `config/settings/` | Environment-based settings, security and proxy configuration |
| `Dockerfile` | Production image used on Railway |

## Deployment

Deployed on Railway from the Dockerfile, with a PostgreSQL plugin over the private network and a custom domain (`api.islandfinance.cc`). Running behind Railway's proxy required explicit `SECURE_PROXY_SSL_HEADER` and `CSRF_TRUSTED_ORIGINS` configuration.

## License

© Matias Morquecho. All rights reserved. The code is shown for portfolio purposes and may not be copied or redistributed without permission.
