"""Deterministic parser for short Telegram messages.

Grammar (all extras optional, any order after the amount):

    [+]<amount> <free text> [#category] [@island] [hoy|ayer|anteayer|dd/mm|dd/mm/aaaa]

Examples:
    350 tacos                 -> expense, category inferred (food)
    +15000 nomina             -> deposit
    1200 renta @nu ayer       -> expense on island matching "nu", yesterday
    89 uber #transporte 25/10

Pure Python (no Django imports) so it is trivial to unit test.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

EXPENSE = "expense"
DEPOSIT = "deposit"
DEFAULT_CATEGORY = "other"
MAX_AMOUNT = Decimal("1000000000000")


class ParseError(ValueError):
    """Raised with a user-facing (Spanish) message."""


@dataclass(frozen=True)
class ParsedTransaction:
    type: str
    amount: Decimal
    note: str | None
    category: str | None  # None for deposits
    date: date
    island_hint: str | None


# Values must match ledger.Transaction.Category values.
# Keywords are stored lowercase and WITHOUT accents (see _normalize).
KEYWORDS: dict[str, set[str]] = {
    "food": {
        "comida", "taco", "tacos", "restaurante", "super", "supermercado", "cafe",
        "pizza", "desayuno", "comer", "cena", "almuerzo", "hamburguesa", "despensa",
        "mercado", "tortillas", "antojito", "antojitos", "sushi", "helado",
    },
    "transport": {
        "uber", "didi", "taxi", "gasolina", "gasolinera", "camion", "pasaje",
        "estacionamiento", "caseta", "casetas", "metro", "transporte", "cabify",
    },
    "subscriptions": {
        "netflix", "spotify", "disney", "hbo", "suscripcion", "suscripciones",
        "youtube", "icloud", "chatgpt", "prime",
    },
    "housing": {
        "renta", "luz", "agua", "internet", "predial", "hipoteca", "mantenimiento",
        "cfe", "gas", "casa",
    },
    "leisure": {
        "cine", "bar", "cerveza", "cervezas", "fiesta", "antro", "videojuego",
        "juego", "concierto", "salida",
    },
    "health": {
        "doctor", "medico", "farmacia", "medicina", "medicinas", "dentista",
        "consulta", "hospital", "salud",
    },
    "clothing": {"ropa", "zapatos", "tenis", "playera", "pantalon", "camisa"},
    "travel": {"viaje", "viajes", "hotel", "vuelo", "avion", "hospedaje", "airbnb"},
    "education": {"curso", "libro", "libros", "colegiatura", "escuela", "udemy"},
    "finance": {"comision", "interes", "prestamo", "tarjeta", "deuda"},
    "family_events": {"regalo", "cumpleanos", "boda", "bautizo", "funeral", "familia"},
    "taxes": {"sat", "impuesto", "impuestos", "isr", "iva"},
    "work": {"trabajo", "oficina", "herramienta", "herramientas"},
    "sport": {"gym", "gimnasio", "deporte", "futbol", "cancha"},
}

_WORD_TO_CATEGORY: dict[str, str] = {
    word: category for category, words in KEYWORDS.items() for word in words
}

# Hashtags accept everything above plus a few explicit aliases.
_TAG_TO_CATEGORY: dict[str, str] = dict(_WORD_TO_CATEGORY)
_TAG_TO_CATEGORY.update({
    "ocio": "leisure", "vivienda": "housing", "educacion": "education",
    "finanzas": "finance", "eventos": "family_events", "deporte": "sport",
    "otro": "other", "otros": "other", "other": "other",
})
for _value in list(KEYWORDS) + ["other"]:
    _TAG_TO_CATEGORY.setdefault(_value, _value)

AMOUNT_RE = re.compile(r"^(?P<sign>[+-])?\$?(?P<num>\d[\d,]*(?:\.\d+)?|\.\d+)$")
_DATE_RE = re.compile(r"^(\d{1,2})/(\d{1,2})(?:/(\d{2}|\d{4}))?$")
_RELATIVE_DAYS = {"hoy": 0, "ayer": 1, "anteayer": 2, "antier": 2}


def _normalize(word: str) -> str:
    word = unicodedata.normalize("NFKD", word.lower())
    word = "".join(c for c in word if not unicodedata.combining(c))
    return word.strip(".,;:!?()\"'")


def _parse_date_token(token: str, today: date) -> date | None:
    norm = _normalize(token)
    if norm in _RELATIVE_DAYS:
        return today - timedelta(days=_RELATIVE_DAYS[norm])

    match = _DATE_RE.match(token)
    if not match:
        return None

    day, month, year_str = int(match[1]), int(match[2]), match[3]
    try:
        if year_str:
            year = int(year_str)
            if year < 100:
                year += 2000
            result = date(year, month, day)
        else:
            result = date(today.year, month, day)
            if result > today:  # "25/12" typed in October means last December
                result = date(today.year - 1, month, day)
    except ValueError:
        raise ParseError(f"Fecha inválida: {token}") from None

    if result > today:
        raise ParseError("La fecha no puede ser futura.")
    return result


def parse_message(text: str, today: date) -> ParsedTransaction:
    tokens = text.split()
    if not tokens:
        raise ParseError("Escribe el monto primero, por ejemplo: 350 tacos")

    match = AMOUNT_RE.match(tokens[0])
    if not match:
        raise ParseError(
            "No pude leer el monto. Empieza con el monto, por ejemplo: 350 tacos "
            "(o +15000 nómina para un ingreso)."
        )

    try:
        amount = Decimal(match["num"].replace(",", ""))
    except InvalidOperation:
        raise ParseError("No pude leer el monto.") from None
    amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if amount <= 0 or amount >= MAX_AMOUNT:
        raise ParseError("El monto debe ser mayor a 0 y menor a 1,000,000,000,000.")

    tx_type = DEPOSIT if match["sign"] == "+" else EXPENSE

    tag_category: str | None = None
    island_hint: str | None = None
    tx_date: date | None = None
    words: list[str] = []

    for token in tokens[1:]:
        if token.startswith("#") and len(token) > 1:
            if tag_category is not None:
                raise ParseError("Usa solo una categoría (#) por mensaje.")
            category = _TAG_TO_CATEGORY.get(_normalize(token[1:]))
            if category is None:
                raise ParseError(f"No conozco la categoría {token}. Usa /ayuda para ver ejemplos.")
            tag_category = category
        elif token.startswith("@") and len(token) > 1:
            if island_hint is not None:
                raise ParseError("Usa solo una isla (@) por mensaje.")
            island_hint = token[1:].replace("_", " ")
        else:
            parsed_date = _parse_date_token(token, today) if tx_date is None else None
            if parsed_date is not None:
                tx_date = parsed_date
            else:
                words.append(token)

    category: str | None = None
    if tx_type == EXPENSE:
        category = tag_category
        if category is None:
            for word in words:
                category = _WORD_TO_CATEGORY.get(_normalize(word))
                if category:
                    break
        category = category or DEFAULT_CATEGORY

    return ParsedTransaction(
        type=tx_type,
        amount=amount,
        note=" ".join(words) or None,
        category=category,
        date=tx_date or today,
        island_hint=island_hint,
    )
