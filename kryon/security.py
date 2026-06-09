from __future__ import annotations

import hmac
import struct
from typing import Final

from .core import KryonError, digest, hexdigest, new

_DOMAIN_MAGIC: Final[bytes] = b"CWDS1000"
_MAX_FRAME_FIELD: Final[int] = (1 << 32) - 1


def _as_bytes(value: bytes | bytearray | memoryview | str | None, *, field: str) -> bytes:
    if value is None:
        return b""
    if isinstance(value, str):
        return value.encode("utf-8")
    try:
        return bytes(value)
    except TypeError as exc:
        raise KryonError(f"{field} must be bytes-like or str") from exc


def _frame(label: str, data: bytes, *, key: bytes = b"", personalization: bytes = b"") -> bytes:
    label_b = label.encode("utf-8")
    parts = (label_b, key, personalization, data)
    if any(len(part) > _MAX_FRAME_FIELD for part in parts):
        raise KryonError("domain-separated frame field is too large")
    header = bytearray(_DOMAIN_MAGIC)
    for part in parts:
        header.extend(struct.pack("<I", len(part)))
    return bytes(header) + label_b + key + personalization + data


def domain_digest(
    label: str,
    data: bytes | bytearray | memoryview | str,
    out_bits: int = 384,
    *,
    key: bytes | bytearray | memoryview | str | None = None,
    personalization: bytes | bytearray | memoryview | str | None = None,
) -> bytes:
    """Return a domain-separated Kryon digest.

    The canonical ``digest(data)`` API is intentionally kept stable.  This
    helper is for application protocols that need explicit separation between
    file hashing, manifests, keyed MAC-like usage, and project-specific tags.
    It is not a substitute for an independently audited MAC construction.
    """

    if not label:
        raise KryonError("domain label must be non-empty")
    data_b = _as_bytes(data, field="data")
    key_b = _as_bytes(key, field="key")
    person_b = _as_bytes(personalization, field="personalization")
    return digest(_frame(label, data_b, key=key_b, personalization=person_b), out_bits)


def domain_hexdigest(
    label: str,
    data: bytes | bytearray | memoryview | str,
    out_bits: int = 384,
    *,
    key: bytes | bytearray | memoryview | str | None = None,
    personalization: bytes | bytearray | memoryview | str | None = None,
) -> str:
    return domain_digest(label, data, out_bits, key=key, personalization=personalization).hex()


def keyed_digest(
    key: bytes | bytearray | memoryview | str,
    data: bytes | bytearray | memoryview | str,
    out_bits: int = 384,
    *,
    personalization: bytes | bytearray | memoryview | str | None = None,
) -> bytes:
    if len(_as_bytes(key, field="key")) == 0:
        raise KryonError("key must be non-empty")
    return domain_digest("keyed-digest", data, out_bits, key=key, personalization=personalization)


def keyed_hexdigest(
    key: bytes | bytearray | memoryview | str,
    data: bytes | bytearray | memoryview | str,
    out_bits: int = 384,
    *,
    personalization: bytes | bytearray | memoryview | str | None = None,
) -> str:
    return keyed_digest(key, data, out_bits, personalization=personalization).hex()


def verify_hexdigest(
    expected_hex: str,
    data: bytes | bytearray | memoryview | str,
    out_bits: int = 384,
    *,
    key: bytes | bytearray | memoryview | str | None = None,
    personalization: bytes | bytearray | memoryview | str | None = None,
    domain: str | None = None,
) -> bool:
    """Constant-time verification helper for hex digests."""

    try:
        bytes.fromhex(expected_hex)
    except ValueError:
        return False

    if key is not None:
        actual = keyed_hexdigest(key, data, out_bits, personalization=personalization)
    elif domain is not None:
        actual = domain_hexdigest(domain, data, out_bits, personalization=personalization)
    else:
        actual = hexdigest(data, out_bits)
    return hmac.compare_digest(actual, expected_hex.lower())


__all__ = [
    "domain_digest",
    "domain_hexdigest",
    "keyed_digest",
    "keyed_hexdigest",
    "verify_hexdigest",
]
