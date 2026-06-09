from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .core import hexdigest


@dataclass(frozen=True)
class KatMessage:
    name: str
    data: bytes


KAT_MESSAGES: tuple[KatMessage, ...] = (
    KatMessage("empty", b""),
    KatMessage("abc", b"abc"),
    KatMessage("quick_fox", b"The quick brown fox jumps over the lazy dog"),
    KatMessage("quick_fox_period", b"The quick brown fox jumps over the lazy dog."),
    KatMessage("block_31_zeroes", b"\x00" * 31),
    KatMessage("block_32_zeroes", b"\x00" * 32),
    KatMessage("block_33_zeroes", b"\x00" * 33),
    KatMessage("block_64_zeroes", b"\x00" * 64),
    KatMessage("utf8_ru_privet", "привет".encode("utf-8")),
    KatMessage("bytes_0_255", bytes(range(256))),
)


def iter_kat_rows(messages: Iterable[KatMessage] = KAT_MESSAGES) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for message in messages:
        data = message.data
        rows.append(
            {
                "name": message.name,
                "length": len(data),
                "hex_preview": data[:24].hex(),
                "kryon_256": hexdigest(data, 256),
                "kryon_384": hexdigest(data, 384),
                "kryon_512": hexdigest(data, 512),
            }
        )
    return rows


def build_kat_document(*, version: str, note: str) -> dict[str, object]:
    return {"version": version, "note": note, "vectors": iter_kat_rows()}
