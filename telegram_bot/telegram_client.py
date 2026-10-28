"""Thin wrapper over the Telegram Bot API. Never raises: failures are logged."""
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

API_URL = "https://api.telegram.org/bot{token}/{method}"
EMPTY_KEYBOARD = {"inline_keyboard": []}


def _call(method: str, **payload):
    url = API_URL.format(token=settings.TELEGRAM_BOT_TOKEN, method=method)
    try:
        response = requests.post(url, json=payload, timeout=5)
    except requests.RequestException:
        logger.exception("Telegram %s failed", method)
        return None
    if not response.ok:
        logger.warning("Telegram %s returned %s: %s", method, response.status_code, response.text[:300])
        return None
    return response.json()


def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return _call("sendMessage", **payload)


def edit_message(chat_id, message_id, text, reply_markup=None):
    return _call(
        "editMessageText",
        chat_id=chat_id,
        message_id=message_id,
        text=text,
        reply_markup=reply_markup or EMPTY_KEYBOARD,
    )


def answer_callback(callback_id, text=None):
    payload = {"callback_query_id": callback_id}
    if text:
        payload["text"] = text
    return _call("answerCallbackQuery", **payload)
