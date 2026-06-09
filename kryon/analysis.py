from __future__ import annotations

import os
import random
import statistics
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

from .core import KryonError, digest
from .reduced import digest_reduced

HashFunction = Callable[[bytes], bytes]


@dataclass(frozen=True)
class AvalancheReport:
    samples: int
    message_bits: int
    digest_bits: int
    min_distance: int
    max_distance: int
    mean_distance: float
    median_distance: float
    expected_distance: float

    @property
    def mean_ratio(self) -> float:
        return self.mean_distance / self.digest_bits

    def as_dict(self) -> dict[str, float | int]:
        return {
            "samples": self.samples,
            "message_bits": self.message_bits,
            "digest_bits": self.digest_bits,
            "min_distance": self.min_distance,
            "max_distance": self.max_distance,
            "mean_distance": round(self.mean_distance, 4),
            "median_distance": round(self.median_distance, 4),
            "expected_distance": round(self.expected_distance, 4),
            "mean_ratio": round(self.mean_ratio, 6),
        }


@dataclass(frozen=True)
class BitFrequencyReport:
    samples: int
    digest_bits: int
    min_ones: int
    max_ones: int
    mean_ones: float
    min_ratio: float
    max_ratio: float
    mean_ratio: float
    worst_bias: float
    chi_square: float
    bit_one_counts: tuple[int, ...]

    def as_dict(self, *, include_counts: bool = False) -> dict[str, float | int | list[int]]:
        result: dict[str, float | int | list[int]] = {
            "samples": self.samples,
            "digest_bits": self.digest_bits,
            "min_ones": self.min_ones,
            "max_ones": self.max_ones,
            "mean_ones": round(self.mean_ones, 4),
            "min_ratio": round(self.min_ratio, 6),
            "max_ratio": round(self.max_ratio, 6),
            "mean_ratio": round(self.mean_ratio, 6),
            "worst_bias": round(self.worst_bias, 6),
            "chi_square": round(self.chi_square, 4),
        }
        if include_counts:
            result["bit_one_counts"] = list(self.bit_one_counts)
        return result


@dataclass(frozen=True)
class TrailPoint:
    rounds: int
    distance: int
    ratio: float
    digest_hex: str
    mutated_digest_hex: str

    def as_dict(self) -> dict[str, float | int | str]:
        return {
            "rounds": self.rounds,
            "distance": self.distance,
            "ratio": round(self.ratio, 6),
            "digest": self.digest_hex,
            "mutated_digest": self.mutated_digest_hex,
        }


@dataclass(frozen=True)
class DifferentialTrailReport:
    message_size: int
    flipped_bit: int
    digest_bits: int
    points: tuple[TrailPoint, ...]

    @property
    def final_ratio(self) -> float:
        return self.points[-1].ratio if self.points else 0.0

    def as_dict(self) -> dict[str, int | float | list[dict[str, float | int | str]]]:
        return {
            "message_size": self.message_size,
            "flipped_bit": self.flipped_bit,
            "digest_bits": self.digest_bits,
            "final_ratio": round(self.final_ratio, 6),
            "points": [point.as_dict() for point in self.points],
        }


def _validate_positive_int(name: str, value: int) -> None:
    if not isinstance(value, int):
        raise KryonError(f"{name} must be an integer")
    if value <= 0:
        raise KryonError(f"{name} must be positive")


def bit_distance(a: bytes, b: bytes) -> int:
    if len(a) != len(b):
        raise KryonError("digests must have the same length")
    return sum((x ^ y).bit_count() for x, y in zip(a, b))


def flip_bit(data: bytes, bit_index: int) -> bytes:
    if bit_index < 0 or bit_index >= len(data) * 8:
        raise KryonError("bit_index is outside of the message")
    buf = bytearray(data)
    buf[bit_index // 8] ^= 1 << (bit_index % 8)
    return bytes(buf)


def bits_from_bytes(data: bytes) -> Iterable[int]:
    for byte in data:
        for bit in range(8):
            yield (byte >> bit) & 1


def structured_corpus(*, seed: int = 20260608, include_random: bool = True) -> list[bytes]:
    """Return a small deterministic corpus for smoke testing hash behavior.

    The corpus intentionally includes empty inputs, repeated bytes, block-boundary
    inputs, natural-language strings, UTF-8 text, and deterministic random data.
    It is not a replacement for a full cryptographic test suite.
    """

    rng = random.Random(seed)
    corpus: list[bytes] = [
        b"",
        b"a",
        b"abc",
        b"message digest",
        b"The quick brown fox jumps over the lazy dog",
        b"The quick brown fox jumps over the lazy dog.",
        "привет".encode("utf-8"),
        bytes(range(256)),
    ]

    for size in (31, 32, 33, 63, 64, 65, 127, 128, 129, 255, 256, 257, 1024):
        corpus.append(b"\x00" * size)
        corpus.append(b"\xff" * size)
        corpus.append(bytes((i * 17 + size) % 256 for i in range(size)))

    if include_random:
        for size in (1, 7, 16, 32, 64, 128, 512, 1024):
            corpus.append(rng.randbytes(size))

    return corpus


def corpus_digest_matrix(
    corpus: Sequence[bytes] | None = None,
    *,
    out_bits: int = 384,
    limit: int | None = None,
) -> list[dict[str, str | int]]:
    selected = list(corpus if corpus is not None else structured_corpus())
    if limit is not None:
        if limit <= 0:
            raise KryonError("limit must be positive")
        selected = selected[:limit]

    rows: list[dict[str, str | int]] = []
    for idx, message in enumerate(selected):
        rows.append(
            {
                "index": idx,
                "length": len(message),
                "preview_hex": message[:16].hex(),
                "digest": digest(message, out_bits).hex(),
            }
        )
    return rows


def avalanche_report(
    *,
    samples: int = 128,
    message_size: int = 128,
    digest_bits: int = 384,
    seed: int | None = 20260608,
    hash_fn: HashFunction | None = None,
) -> AvalancheReport:
    _validate_positive_int("samples", samples)
    _validate_positive_int("message_size", message_size)

    rng = random.Random(seed) if seed is not None else random.Random(os.urandom(32))
    hash_fn = hash_fn or (lambda data: digest_reduced(data, digest_bits=digest_bits, absorb_rounds=10, final_absorb_rounds=14, final_mix_rounds=16, post_mix_rounds=6))

    distances: list[int] = []
    for _ in range(samples):
        data = rng.randbytes(message_size)
        bit = rng.randrange(message_size * 8)
        distances.append(bit_distance(hash_fn(data), hash_fn(flip_bit(data, bit))))

    return AvalancheReport(
        samples=samples,
        message_bits=message_size * 8,
        digest_bits=digest_bits,
        min_distance=min(distances),
        max_distance=max(distances),
        mean_distance=statistics.mean(distances),
        median_distance=statistics.median(distances),
        expected_distance=digest_bits / 2,
    )


def bit_frequency_report(
    *,
    samples: int = 256,
    message_size: int = 128,
    digest_bits: int = 384,
    seed: int = 20260608,
    corpus: Sequence[bytes] | None = None,
    hash_fn: HashFunction | None = None,
) -> BitFrequencyReport:
    """Measure one-bit frequency over many digest outputs.

    A perfectly random digest stream would put each bit near 50% ones. This is a
    smoke-test statistic, not a proof of security.
    """

    _validate_positive_int("samples", samples)
    _validate_positive_int("message_size", message_size)
    if digest_bits % 8 != 0:
        raise KryonError("digest_bits must be a multiple of 8")

    hash_fn = hash_fn or (lambda data: digest(data, digest_bits))
    rng = random.Random(seed)
    messages = list(corpus) if corpus is not None else []
    while len(messages) < samples:
        messages.append(rng.randbytes(message_size))
    messages = messages[:samples]

    counts = [0] * digest_bits
    for message in messages:
        d = hash_fn(message)
        if len(d) * 8 != digest_bits:
            raise KryonError("hash_fn returned a digest with unexpected length")
        for i, bit in enumerate(bits_from_bytes(d)):
            counts[i] += bit

    ratios = [count / samples for count in counts]
    expected = samples / 2
    chi_square = sum(((count - expected) ** 2) / expected for count in counts)
    return BitFrequencyReport(
        samples=samples,
        digest_bits=digest_bits,
        min_ones=min(counts),
        max_ones=max(counts),
        mean_ones=statistics.mean(counts),
        min_ratio=min(ratios),
        max_ratio=max(ratios),
        mean_ratio=statistics.mean(ratios),
        worst_bias=max(abs(ratio - 0.5) for ratio in ratios),
        chi_square=chi_square,
        bit_one_counts=tuple(counts),
    )


def differential_trail_report(
    message: bytes | bytearray | memoryview | str = b"Kryon differential trail seed",
    *,
    flipped_bit: int = 0,
    max_rounds: int = 10,
    out_bits: int = 384,
    digest_bits: int = 128,
) -> DifferentialTrailReport:
    """Trace how a one-bit difference propagates through reduced profiles.

    Each point hashes the same message pair with a different reduced-round count.
    This intentionally explores weak/non-canonical configurations.
    """

    if isinstance(message, str):
        message_bytes = message.encode("utf-8")
    else:
        message_bytes = bytes(message)
    if not message_bytes:
        raise KryonError("message must not be empty for differential trails")
    _validate_positive_int("max_rounds", max_rounds)
    if max_rounds > 18:
        raise KryonError("max_rounds must be <= 18")

    mutated = flip_bit(message_bytes, flipped_bit)
    points: list[TrailPoint] = []
    for rounds in range(1, max_rounds + 1):
        a = digest_reduced(
            message_bytes,
            out_bits=out_bits,
            digest_bits=digest_bits,
            absorb_rounds=rounds,
            final_absorb_rounds=rounds,
            final_mix_rounds=rounds,
            post_mix_rounds=max(1, rounds // 2),
        )
        b = digest_reduced(
            mutated,
            out_bits=out_bits,
            digest_bits=digest_bits,
            absorb_rounds=rounds,
            final_absorb_rounds=rounds,
            final_mix_rounds=rounds,
            post_mix_rounds=max(1, rounds // 2),
        )
        distance = bit_distance(a, b)
        points.append(TrailPoint(rounds=rounds, distance=distance, ratio=distance / digest_bits, digest_hex=a.hex(), mutated_digest_hex=b.hex()))

    return DifferentialTrailReport(
        message_size=len(message_bytes),
        flipped_bit=flipped_bit,
        digest_bits=digest_bits,
        points=tuple(points),
    )
