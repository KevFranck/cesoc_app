"""Utilitaires de securite pour les mots de passe."""

from __future__ import annotations

import hashlib
import hmac
import secrets


PBKDF2_ITERATIONS = 100_000


def hash_password(password: str) -> str:
    """Retourne un hash PBKDF2 stable pour un mot de passe."""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    ).hex()
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${digest}"


def verify_password(password: str, password_hash: str | None) -> bool:
    """Verifie un mot de passe contre son hash stocke."""
    if not password_hash:
        return False
    try:
        algorithm, iteration_text, salt, expected_digest = password_hash.split("$", 3)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iteration_text),
    ).hex()
    return hmac.compare_digest(digest, expected_digest)
