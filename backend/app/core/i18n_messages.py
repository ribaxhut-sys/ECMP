"""Localized message catalog for API responses and outbound email.

Keep entries short and stable — these are user-facing strings, not audit
data. Add a language by adding a top-level key; missing keys fall back to
``id`` (the platform default) via :func:`get_message`.
"""

from __future__ import annotations

SUPPORTED_LANGUAGES: tuple[str, ...] = ("id", "en")
DEFAULT_LANGUAGE = "id"

MESSAGES: dict[str, dict[str, str]] = {
    "id": {
        "forgot_password": "Jika akun tersebut ada, tautan reset kata sandi telah dikirim.",
        "reset_password_success": "Kata sandi berhasil direset.",
        "password_reset_subject": "Permintaan Reset Kata Sandi ECMP",
        "password_reset_body": (
            "Kami menerima permintaan untuk mereset kata sandi akun Anda. "
            "Klik tautan berikut untuk melanjutkan: {reset_url}\n"
            "Tautan ini akan kedaluwarsa pada {expires_at}. "
            "Jika Anda tidak meminta ini, abaikan email ini."
        ),
        "password_changed_subject": "Kata Sandi ECMP Anda Telah Diubah",
        "password_changed_body": (
            "Kata sandi akun Anda baru saja diubah. Jika ini bukan Anda, "
            "segera hubungi administrator."
        ),
    },
    "en": {
        "forgot_password": "If the account exists, a reset link has been sent.",
        "reset_password_success": "Password has been reset successfully.",
        "password_reset_subject": "ECMP Password Reset Request",
        "password_reset_body": (
            "We received a request to reset your account password. "
            "Click the following link to continue: {reset_url}\n"
            "This link expires at {expires_at}. "
            "If you did not request this, please ignore this email."
        ),
        "password_changed_subject": "Your ECMP Password Was Changed",
        "password_changed_body": (
            "Your account password was just changed. If this was not you, "
            "please contact an administrator immediately."
        ),
    },
}


def normalize_language(language: str | None) -> str:
    """Resolve a raw language hint (user pref, header, etc.) to a supported code."""
    if not language:
        return DEFAULT_LANGUAGE
    cleaned = language.strip().lower()[:2]
    return cleaned if cleaned in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def get_message(key: str, language: str | None = None) -> str:
    lang = normalize_language(language)
    catalog = MESSAGES.get(lang, MESSAGES[DEFAULT_LANGUAGE])
    return catalog.get(key, MESSAGES[DEFAULT_LANGUAGE].get(key, key))


def parse_accept_language(header_value: str | None) -> str | None:
    """Best-effort primary language tag from an ``Accept-Language`` header."""
    if not header_value:
        return None
    first = header_value.split(",", 1)[0].strip()
    primary = first.split(";", 1)[0].strip()
    return primary.split("-", 1)[0].lower() if primary else None
