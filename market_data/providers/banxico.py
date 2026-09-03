from decimal import Decimal

import requests
from decouple import config

from market_data.exceptions import ProviderUnavailableError

URL = "https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43718/datos/oportuno"
TIMEOUT = 3


def get_usd_to_mxn() -> Decimal:
    """SF43718 = tipo de cambio FIX USD/MXN, serie oficial de Banxico."""
    try:
        response = requests.get(
            URL,
            headers={"Bmx-Token": config("CONSULT_BMX_TOKEN")},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ProviderUnavailableError(f"Banxico request failed: {exc}") from exc

    try:
        dato = response.json()["bmx"]["series"][0]["datos"][0]["dato"]
    except (KeyError, IndexError) as exc:
        raise ProviderUnavailableError(f"Unexpected Banxico response shape: {exc}") from exc

    return Decimal(dato)