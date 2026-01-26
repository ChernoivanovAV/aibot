"""Small helper utilities shared across the project."""

import hashlib


def sha256_hex(text: str) -> str:
    """Return the SHA-256 hex digest for the given text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
