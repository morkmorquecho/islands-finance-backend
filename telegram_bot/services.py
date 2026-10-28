"""Business logic for the Telegram bot. The webhook view only authenticates and delegates here."""
import hashlib
import logging
import secrets
from datetime import timedelta

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import transaction as db_transaction
from django.utils import timezone

from ledger.models import Transaction
from portfolio.models import Island

from . import telegram_client as tg
from .models import PendingTransaction, TelegramLink, TelegramLinkCode, TelegramUpdate
from .parser import DEPOSIT, ParseError, parse_message

logger = logging.getLogger(__name__)

LINK_CODE_TTL = timedelta(minutes=10)
PENDING_TTL = timedelta(minutes=15)
RATE_LIMIT_PER_MIN = 30
CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no 0/O/1/I

CATEGORY_LABELS_ES = {
    "food": "Comida", "transport": "Transporte", "subscriptions": "Suscripciones",
    "housing": "Vivienda", "leisure": "Ocio", "health": "Salud", "clothing": "Ropa",
    "travel": "Viajes", "education": "Educación", "finance": "Finanzas",
    "family_events": "Eventos familiares", "taxes": "Impuestos", "work": "Trabajo",
    "sport": "Deporte", "other": "Otro",
}
TYPE_LABELS_ES = {
    "expense": "Gasto", "deposit": "Ingreso", "withdrawal": "Retiro",
    "buy": "Compra", "sell": "Venta",
}

HELP_TEXT = (
    "Cómo registrar:\n"
    "350 tacos → gasto\n"
    "+15000 nómina → ingreso\n\n"
    "Extras opcionales: #categoría  @isla  hoy | ayer | 25/10\n"
    "Ejemplos:\n"
    "• 350 tacos #comida\n"
    "• 1200 renta @nu ayer\n"
    "• +800 venta 25/10\n\n"
    "Comandos:\n"
    "/isla – elegir isla predeterminada\n"
    "/ultimos – últimos 5 registros\n"
    "/deshacer – borrar el último registro hecho desde Telegram\n"
    "/desconectar – desvincular esta cuenta"
)
NOT_LINKED_TEXT = (
    "Aún no has vinculado tu cuenta. En Island Finance entra a la sección de Telegram, "
    "genera un código y envíame: /start TUCODIGO"
)


# ---------------------------------------------------------------- linking

def hash_code(code: str) -> str:
    return hashlib.sha256(code.strip().upper().encode()).hexdigest()


def create_link_code(user) -> str:
    """Invalidate the user's previous unused codes and return a fresh plain code (shown once)."""
    now = timezone.now()
    TelegramLinkCode.objects.filter(user=user, used_at__isnull=True).update(expires_at=now)
    code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(8))
    TelegramLinkCode.objects.create(
        user=user, code_hash=hash_code(code), expires_at=now + LINK_CODE_TTL
    )
    return code


def redeem_link_code(code: str, chat_id: int, username: str = ""):
    """Return (link, None) on success or (None, user_facing_error)."""
    now = timezone.now()
    with db_transaction.atomic():
        link_code = (
            TelegramLinkCode.objects.select_for_update()
            .select_related("user")
            .filter(code_hash=hash_code(code))
            .first()
        )
        if link_code is None:
            return None, "Código inválido. Genera uno nuevo desde la app."
        if link_code.used_at is not None or link_code.expires_at <= now:
            return None, "El código expiró o ya fue usado. Genera uno nuevo desde la app."

        if TelegramLink.objects.filter(chat_id=chat_id).exclude(user=link_code.user).exists():
            return None, "Este chat ya está vinculado a otra cuenta. Usa /desconectar primero."

        link, _ = TelegramLink.objects.update_or_create(
            user=link_code.user,
            defaults={"chat_id": chat_id, "telegram_username": username or ""},
        )
        islands = list(
            Island.objects.filter(user=link_code.user, kind=Island.Kind.CASH, is_active=True)[:2]
        )
        if len(islands) == 1 and link.default_island_id is None:
            link.default_island = islands[0]
            link.save(update_fields=["default_island"])

        link_code.used_at = now
        link_code.save(update_fields=["used_at"])
    return link, None


# ---------------------------------------------------------------- entry point

def handle_update(update: dict) -> None:
    update_id = update.get("update_id")
    if update_id is None:
        return
    try:
        with db_transaction.atomic():
            TelegramUpdate.objects.create(update_id=update_id)
    except IntegrityError:
        return  # webhook retry of an update we already processed

    if "message" in update:
        _handle_message(update["message"])
    elif "callback_query" in update:
        _handle_callback(update["callback_query"])


def _rate_limited(chat_id: int) -> bool:
    key = f"tg:rl:{chat_id}"
    if cache.add(key, 1, 60):
        return False
    try:
        return cache.incr(key) > RATE_LIMIT_PER_MIN
    except ValueError:  # key expired between add() and incr()
        cache.set(key, 1, 60)
        return False


def _get_link(chat_id: int):
    return TelegramLink.objects.select_related("user", "default_island").filter(chat_id=chat_id).first()


# ---------------------------------------------------------------- messages

def _handle_message(message: dict) -> None:
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    if chat.get("type") != "private" or chat_id is None:
        return

    if _rate_limited(chat_id):
        tg.send_message(chat_id, "Vas muy rápido, espera un momento e intenta de nuevo.")
        return

    text = (message.get("text") or "").strip()
    if not text:
        tg.send_message(chat_id, "Por ahora solo entiendo mensajes de texto. Usa /ayuda.")
        return

    command, arg = None, ""
    if text.startswith("/"):
        raw_command, _, arg = text.partition(" ")
        command = raw_command.split("@", 1)[0].lower()
        arg = arg.strip()

    if command == "/start":
        username = (message.get("from") or {}).get("username", "")
        return _cmd_start(chat_id, arg, username)
    if command == "/ayuda":
        tg.send_message(chat_id, HELP_TEXT)
        return

    link = _get_link(chat_id)
    if link is None:
        tg.send_message(chat_id, NOT_LINKED_TEXT)
        return

    if command is None:
        return _register_from_text(link, chat_id, text)

    handlers = {
        "/isla": _cmd_island,
        "/ultimos": _cmd_recent,
        "/deshacer": _cmd_undo,
        "/desconectar": _cmd_unlink,
    }
    handler = handlers.get(command)
    if handler is None:
        tg.send_message(chat_id, "Comando no reconocido. Usa /ayuda.")
        return
    handler(link, chat_id)


def _cmd_start(chat_id: int, code: str, username: str) -> None:
    if not code:
        if _get_link(chat_id):
            tg.send_message(chat_id, "Tu cuenta ya está vinculada. Usa /ayuda para ver cómo registrar.")
        else:
            tg.send_message(chat_id, "¡Hola! " + NOT_LINKED_TEXT)
        return

    link, error = redeem_link_code(code, chat_id, username)
    if error:
        tg.send_message(chat_id, error)
        return

    text = "✅ Cuenta vinculada.\n"
    if link.default_island_id:
        text += f"Isla predeterminada: {link.default_island.name}\n"
    else:
        text += "Elige tu isla predeterminada con /isla.\n"
    text += "\n" + HELP_TEXT
    tg.send_message(chat_id, text)


def _cmd_island(link: TelegramLink, chat_id: int) -> None:
    islands = list(
        Island.objects.filter(user=link.user, kind=Island.Kind.CASH, is_active=True).order_by("name")[:20]
    )
    if not islands:
        tg.send_message(chat_id, "No tienes islas de efectivo activas. Crea una en la app.")
        return
    keyboard = {"inline_keyboard": [
        [{
            "text": ("✓ " if island.pk == link.default_island_id else "") + island.name,
            "callback_data": f"isl:{island.pk}",
        }]
        for island in islands
    ]}
    tg.send_message(chat_id, "Elige tu isla predeterminada:", reply_markup=keyboard)


def _cmd_recent(link: TelegramLink, chat_id: int) -> None:
    transactions = list(Transaction.objects.filter(user=link.user).select_related("island")[:5])
    if not transactions:
        tg.send_message(chat_id, "Aún no tienes registros.")
        return
    lines = ["Últimos registros:"]
    for tx in transactions:
        value = tx.amount if tx.amount is not None else tx.quantity
        label = TYPE_LABELS_ES.get(tx.type, tx.type)
        detail = tx.note or CATEGORY_LABELS_ES.get(tx.category or "", "")
        lines.append(f"• {tx.date.isoformat()} · {label} · {value:,.2f} · {tx.island.name} · {detail}".rstrip(" ·"))
    tg.send_message(chat_id, "\n".join(lines))


def _cmd_undo(link: TelegramLink, chat_id: int) -> None:
    with db_transaction.atomic():
        pending = (
            PendingTransaction.objects.select_for_update()
            .select_related("transaction")
            .filter(link=link, status=PendingTransaction.Status.CONFIRMED, transaction__isnull=False)
            .order_by("-confirmed_at")
            .first()
        )
        if pending is None:
            tg.send_message(chat_id, "No hay registros recientes hechos desde Telegram para deshacer.")
            return
        summary = _summary_line(pending)
        pending.transaction.delete()
        pending.status = PendingTransaction.Status.UNDONE
        pending.save(update_fields=["status"])
    tg.send_message(chat_id, f"↩️ Deshecho: {summary}")


def _cmd_unlink(link: TelegramLink, chat_id: int) -> None:
    link.delete()
    tg.send_message(chat_id, "Cuenta desvinculada. Puedes volver a vincularla desde la app cuando quieras.")


# ---------------------------------------------------------------- registering

def _resolve_island(link: TelegramLink, hint):
    """Return (island, None) or (None, user_facing_error)."""
    cash_islands = Island.objects.filter(user=link.user, kind=Island.Kind.CASH, is_active=True)

    if hint:
        exact = list(cash_islands.filter(name__iexact=hint)[:2])
        if len(exact) == 1:
            return exact[0], None
        partial = list(cash_islands.filter(name__icontains=hint)[:6])
        if len(partial) == 1:
            return partial[0], None
        if not partial:
            return None, f"No encontré una isla de efectivo que coincida con @{hint}. Usa /isla para ver las tuyas."
        names = ", ".join(i.name for i in partial)
        return None, f"@{hint} coincide con varias islas ({names}). Sé más específico."

    default = link.default_island
    if default and default.is_active and default.kind == Island.Kind.CASH:
        return default, None
    return None, "Primero elige tu isla predeterminada con /isla (o usa @isla en el mensaje)."


def _money(amount, island) -> str:
    return f"${amount:,.2f} {island.currency or ''}".strip()


def _summary_line(pending: PendingTransaction) -> str:
    label = TYPE_LABELS_ES.get(pending.type, pending.type)
    detail = pending.note or CATEGORY_LABELS_ES.get(pending.category or "", "")
    return f"{label} {_money(pending.amount, pending.island)} · {pending.island.name} · {detail}".rstrip(" ·")


def _summary_text(pending: PendingTransaction) -> str:
    lines = [
        f"{TYPE_LABELS_ES.get(pending.type, pending.type)} de {_money(pending.amount, pending.island)}",
        f"Isla: {pending.island.name}",
    ]
    if pending.category:
        lines.append(f"Categoría: {CATEGORY_LABELS_ES.get(pending.category, pending.category)}")
    if pending.note:
        lines.append(f"Nota: {pending.note}")
    lines.append(f"Fecha: {pending.date.isoformat()}")
    lines += ["", "¿Lo registro?"]
    return "\n".join(lines)


def _register_from_text(link: TelegramLink, chat_id: int, text: str) -> None:
    try:
        parsed = parse_message(text, timezone.localdate())
    except ParseError as exc:
        tg.send_message(chat_id, f"{exc}\n\nUsa /ayuda para ver ejemplos.")
        return

    island, error = _resolve_island(link, parsed.island_hint)
    if error:
        tg.send_message(chat_id, error)
        return

    pending = PendingTransaction.objects.create(
        link=link,
        island=island,
        type=parsed.type,
        amount=parsed.amount,
        category=parsed.category,
        note=parsed.note,
        date=parsed.date,
        expires_at=timezone.now() + PENDING_TTL,
    )
    keyboard = {"inline_keyboard": [[
        {"text": "✅ Registrar", "callback_data": f"ok:{pending.pk}"},
        {"text": "❌ Cancelar", "callback_data": f"no:{pending.pk}"},
    ]]}
    tg.send_message(chat_id, _summary_text(pending), reply_markup=keyboard)


# ---------------------------------------------------------------- callbacks

def _handle_callback(callback: dict) -> None:
    callback_id = callback.get("id")
    message = callback.get("message") or {}
    chat_id = (message.get("chat") or {}).get("id")
    message_id = message.get("message_id")
    if chat_id is None or message_id is None:
        tg.answer_callback(callback_id)
        return

    link = _get_link(chat_id)
    if link is None:
        tg.answer_callback(callback_id, "Cuenta no vinculada.")
        return

    action, _, ref = (callback.get("data") or "").partition(":")
    if action == "isl":
        _cb_set_island(link, callback_id, chat_id, message_id, ref)
    elif action in ("ok", "no"):
        _cb_resolve_pending(link, callback_id, chat_id, message_id, ref, confirm=(action == "ok"))
    else:
        tg.answer_callback(callback_id)


def _cb_set_island(link, callback_id, chat_id, message_id, island_ref) -> None:
    try:
        island = Island.objects.filter(
            pk=island_ref, user=link.user, kind=Island.Kind.CASH, is_active=True
        ).first()
    except (ValueError, ValidationError):
        island = None
    if island is None:
        tg.answer_callback(callback_id, "Esa isla ya no está disponible.")
        return
    link.default_island = island
    link.save(update_fields=["default_island"])
    tg.answer_callback(callback_id)
    tg.edit_message(chat_id, message_id, f"✅ Isla predeterminada: {island.name}")


def _cb_resolve_pending(link, callback_id, chat_id, message_id, pending_ref, confirm: bool) -> None:
    Status = PendingTransaction.Status
    with db_transaction.atomic():
        try:
            pending = (
                PendingTransaction.objects.select_for_update()
                .select_related("island")
                .filter(pk=pending_ref, link=link)
                .first()
            )
        except (ValueError, ValidationError):
            pending = None

        if pending is None:
            tg.answer_callback(callback_id, "No encontré ese registro.")
            return
        if pending.status != Status.PENDING:
            tg.answer_callback(callback_id, "Ese registro ya fue procesado.")
            return

        if not confirm:
            pending.status = Status.CANCELLED
            pending.save(update_fields=["status"])
            result = "❌ Cancelado."
        elif pending.expires_at <= timezone.now():
            pending.status = Status.EXPIRED
            pending.save(update_fields=["status"])
            result = "⌛ Expiró. Vuelve a enviar el mensaje."
        else:
            tx = Transaction.objects.create(
                island=pending.island,
                user=link.user,
                type=Transaction.Type.DEPOSIT if pending.type == DEPOSIT else Transaction.Type.EXPENSE,
                date=pending.date,
                amount=pending.amount,
                category=pending.category,
                note=pending.note,
            )
            pending.status = Status.CONFIRMED
            pending.transaction = tx
            pending.confirmed_at = timezone.now()
            pending.save(update_fields=["status", "transaction", "confirmed_at"])
            result = f"✅ Registrado: {_summary_line(pending)}"

    tg.answer_callback(callback_id)
    tg.edit_message(chat_id, message_id, result)
