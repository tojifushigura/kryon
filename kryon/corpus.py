from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, Sequence

from .core import KryonError, hexdigest


@dataclass(frozen=True)
class CorpusCase:
    """A deterministic message used by Kryon analysis tooling."""

    name: str
    data: bytes
    category: str = "generic"

    def as_row(self, *, digest_bits: int = 384) -> dict[str, str | int]:
        return {
            "name": self.name,
            "category": self.category,
            "length": len(self.data),
            "preview_hex": self.data[:32].hex(),
            "kryon": hexdigest(self.data, digest_bits),
        }


def _pattern(size: int, multiplier: int, addend: int = 0) -> bytes:
    return bytes(((i * multiplier + addend) & 0xFF) for i in range(size))


def deterministic_corpus(*, profile: str = "standard", seed: int = 20260608) -> tuple[CorpusCase, ...]:
    """Build a reproducible corpus for smoke, standard, or long analysis.

    The corpus focuses on cryptographic edge cases: empty input, block
    boundaries, repeated bytes, incremental patterns, UTF-8, and deterministic
    pseudo-random messages.  It is deliberately deterministic so reports can be
    regenerated and compared across Python/Rust/native implementations.
    """

    if profile not in {"smoke", "standard", "long"}:
        raise KryonError("profile must be one of: smoke, standard, long")

    rng = random.Random(seed)
    cases: list[CorpusCase] = [
        CorpusCase("empty", b"", "edge"),
        CorpusCase("one_zero", b"\x00", "edge"),
        CorpusCase("one_ff", b"\xff", "edge"),
        CorpusCase("ascii_a", b"a", "text"),
        CorpusCase("ascii_abc", b"abc", "text"),
        CorpusCase("quick_fox", b"The quick brown fox jumps over the lazy dog", "text"),
        CorpusCase("quick_fox_period", b"The quick brown fox jumps over the lazy dog.", "text"),
        CorpusCase("utf8_ru_privet", "привет".encode("utf-8"), "utf8"),
        CorpusCase("utf8_mixed", "Kryon / хеш / 測試 / 🔐".encode("utf-8"), "utf8"),
        CorpusCase("bytes_0_255", bytes(range(256)), "pattern"),
    ]

    boundary_sizes = [0, 1, 2, 3, 7, 15, 16, 17, 31, 32, 33, 63, 64, 65]
    if profile in {"standard", "long"}:
        boundary_sizes += [95, 96, 97, 127, 128, 129, 191, 192, 193, 255, 256, 257, 511, 512, 513, 1023, 1024, 1025]
    if profile == "long":
        boundary_sizes += [2047, 2048, 2049, 4095, 4096, 4097, 8191, 8192]

    for size in boundary_sizes:
        cases.append(CorpusCase(f"zero_{size}", b"\x00" * size, "boundary"))
        cases.append(CorpusCase(f"ff_{size}", b"\xff" * size, "boundary"))
        cases.append(CorpusCase(f"inc17_{size}", _pattern(size, 17, size), "pattern"))
        cases.append(CorpusCase(f"inc31_{size}", _pattern(size, 31, size // 3), "pattern"))

    random_sizes = [1, 7, 16, 31, 32, 33, 64]
    if profile in {"standard", "long"}:
        random_sizes += [128, 255, 256, 257, 512, 1024]
    if profile == "long":
        random_sizes += [2048, 4096, 8192]
    for size in random_sizes:
        cases.append(CorpusCase(f"rand_{seed}_{size}", rng.randbytes(size), "random"))

    # Preserve first occurrence of duplicated size/name combinations while still
    # allowing the generated boundary list to include zero explicitly.
    seen: set[str] = set()
    unique: list[CorpusCase] = []
    for case in cases:
        if case.name in seen:
            continue
        seen.add(case.name)
        unique.append(case)
    return tuple(unique)


def chunk_plans(length: int) -> tuple[tuple[int, ...], ...]:
    """Return deterministic streaming plans for a message length."""

    if length < 0:
        raise KryonError("length must be non-negative")
    if length == 0:
        return ((),)

    one_byte = tuple(1 for _ in range(length))
    primes: list[int] = []
    remaining = length
    for step in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31):
        if remaining <= 0:
            break
        take = min(step, remaining)
        primes.append(take)
        remaining -= take
    if remaining:
        primes.append(remaining)

    blocks: list[int] = []
    remaining = length
    while remaining > 0:
        take = min(32, remaining)
        blocks.append(take)
        remaining -= take

    uneven: list[int] = []
    remaining = length
    toggle = 1
    while remaining > 0:
        take = min(1 + (toggle * 37) % 97, remaining)
        uneven.append(take)
        remaining -= take
        toggle += 1

    return (tuple([length]), one_byte, tuple(primes), tuple(blocks), tuple(uneven))


def mutate_case(case: CorpusCase, *, max_mutations: int = 4) -> tuple[CorpusCase, ...]:
    """Create deterministic one-bit mutations for a corpus case."""

    if max_mutations <= 0:
        raise KryonError("max_mutations must be positive")
    data = case.data
    if not data:
        return (CorpusCase(case.name + "__append_00", b"\x00", case.category + ":mutated"),)

    bit_positions = [0, len(data) * 4, len(data) * 8 - 1, (len(data) * 8 * 7) // 13]
    bit_positions = bit_positions[:max_mutations]
    mutated: list[CorpusCase] = []
    seen: set[int] = set()
    for bit in bit_positions:
        bit = max(0, min(bit, len(data) * 8 - 1))
        if bit in seen:
            continue
        seen.add(bit)
        buf = bytearray(data)
        buf[bit // 8] ^= 1 << (bit % 8)
        mutated.append(CorpusCase(f"{case.name}__flip_{bit}", bytes(buf), case.category + ":mutated"))
    return tuple(mutated)


def corpus_vectors(cases: Sequence[CorpusCase] | None = None, *, digest_bits: int = 384) -> list[dict[str, str | int]]:
    selected = cases if cases is not None else deterministic_corpus()
    return [case.as_row(digest_bits=digest_bits) for case in selected]


def corpus_hex_lines(cases: Iterable[CorpusCase]) -> str:
    return "\n".join(f"{case.name}\t{case.data.hex()}" for case in cases) + "\n"
