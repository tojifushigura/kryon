from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Sequence

from .version import __version__
from .analysis import bit_distance
from .core import KryonError, digest
from .corpus import CorpusCase, deterministic_corpus, mutate_case
from .reduced import digest_reduced, make_profile


@dataclass(frozen=True)
class AttackProfile:
    """Reduced Kryon round profile used by automated attack probes.

    These settings are intentionally weak and are meant only for cryptanalysis
    tooling.  They must not be interpreted as alternative production settings.
    """

    rounds: int = 2
    out_bits: int = 384
    digest_bits: int = 16

    def validate(self) -> None:
        if not isinstance(self.rounds, int) or self.rounds < 1 or self.rounds > 18:
            raise KryonError("rounds must be an integer in the range 1..18")
        if self.out_bits not in {256, 384, 512}:
            raise KryonError("out_bits must be one of: 256, 384, 512")
        if not isinstance(self.digest_bits, int) or self.digest_bits < 8 or self.digest_bits > self.out_bits or self.digest_bits % 8 != 0:
            raise KryonError("digest_bits must be a byte-aligned value between 8 and out_bits")

    def as_dict(self) -> dict[str, int]:
        return {"rounds": self.rounds, "out_bits": self.out_bits, "digest_bits": self.digest_bits}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _reduced_digest(data: bytes, profile: AttackProfile) -> bytes:
    profile.validate()
    round_profile = make_profile(
        absorb_rounds=profile.rounds,
        final_absorb_rounds=profile.rounds,
        final_mix_rounds=profile.rounds,
        post_mix_rounds=max(1, profile.rounds // 2),
    )
    return digest_reduced(data, out_bits=profile.out_bits, digest_bits=profile.digest_bits, profile=round_profile)


def reduced_collision_search(
    *,
    rounds: int = 2,
    digest_bits: int = 16,
    out_bits: int = 384,
    max_attempts: int = 100_000,
    seed: int = 20260608,
    prefix: bytes | str = b"cw-v08-collision:",
    payload_size: int = 16,
) -> dict[str, Any]:
    """Search a toy collision for a truncated reduced-round digest.

    This is a birthday-bound demonstration against deliberately tiny outputs.
    It is used to verify that the project has tooling for breaking weak modes,
    not to claim weakness in the canonical 384-bit configuration.
    """

    if max_attempts <= 0:
        raise KryonError("max_attempts must be positive")
    if payload_size <= 0:
        raise KryonError("payload_size must be positive")
    prefix_bytes = prefix.encode("utf-8") if isinstance(prefix, str) else bytes(prefix)
    profile = AttackProfile(rounds=rounds, out_bits=out_bits, digest_bits=digest_bits)
    profile.validate()

    rng = random.Random(seed)
    seen: dict[bytes, bytes] = {}
    expected_birthday = math.sqrt(math.pi / 2 * (2**digest_bits))

    for attempt in range(1, max_attempts + 1):
        payload = prefix_bytes + attempt.to_bytes(8, "little") + rng.randbytes(payload_size)
        d = _reduced_digest(payload, profile)
        previous = seen.get(d)
        if previous is not None and previous != payload:
            return {
                "version": __version__,
                "generated_at_utc": _now(),
                "attack": "truncated_reduced_collision",
                "profile": profile.as_dict(),
                "max_attempts": max_attempts,
                "attempts": attempt,
                "expected_birthday_attempts": round(expected_birthday, 4),
                "found": True,
                "status": "passed",
                "digest_hex": d.hex(),
                "message_a_hex": previous.hex(),
                "message_b_hex": payload.hex(),
            }
        seen[d] = payload

    return {
        "version": __version__,
        "generated_at_utc": _now(),
        "attack": "truncated_reduced_collision",
        "profile": profile.as_dict(),
        "max_attempts": max_attempts,
        "attempts": max_attempts,
        "expected_birthday_attempts": round(expected_birthday, 4),
        "found": False,
        "status": "not_found",
    }


def reduced_prefix_preimage_search(
    *,
    target_prefix_hex: str = "00",
    rounds: int = 2,
    digest_bits: int = 16,
    out_bits: int = 384,
    max_attempts: int = 100_000,
    seed: int = 20260608,
    prefix: bytes | str = b"cw-v08-preimage:",
    payload_size: int = 16,
) -> dict[str, Any]:
    """Find a toy input whose truncated digest starts with a hex prefix."""

    if len(target_prefix_hex) == 0 or len(target_prefix_hex) % 2 != 0:
        raise KryonError("target_prefix_hex must contain a whole number of bytes")
    try:
        target_prefix = bytes.fromhex(target_prefix_hex)
    except ValueError as exc:
        raise KryonError("target_prefix_hex is not valid hex") from exc
    if len(target_prefix) * 8 > digest_bits:
        raise KryonError("target prefix cannot be larger than digest_bits")
    if max_attempts <= 0:
        raise KryonError("max_attempts must be positive")
    if payload_size <= 0:
        raise KryonError("payload_size must be positive")

    prefix_bytes = prefix.encode("utf-8") if isinstance(prefix, str) else bytes(prefix)
    profile = AttackProfile(rounds=rounds, out_bits=out_bits, digest_bits=digest_bits)
    profile.validate()
    rng = random.Random(seed)
    expected = 2 ** (8 * len(target_prefix))

    for attempt in range(1, max_attempts + 1):
        payload = prefix_bytes + attempt.to_bytes(8, "little") + rng.randbytes(payload_size)
        d = _reduced_digest(payload, profile)
        if d.startswith(target_prefix):
            return {
                "version": __version__,
                "generated_at_utc": _now(),
                "attack": "truncated_reduced_prefix_preimage",
                "profile": profile.as_dict(),
                "target_prefix_hex": target_prefix_hex,
                "expected_attempts": expected,
                "max_attempts": max_attempts,
                "attempts": attempt,
                "found": True,
                "status": "passed",
                "digest_hex": d.hex(),
                "message_hex": payload.hex(),
            }
    return {
        "version": __version__,
        "generated_at_utc": _now(),
        "attack": "truncated_reduced_prefix_preimage",
        "profile": profile.as_dict(),
        "target_prefix_hex": target_prefix_hex,
        "expected_attempts": expected,
        "max_attempts": max_attempts,
        "attempts": max_attempts,
        "found": False,
        "status": "not_found",
    }


def differential_clustering_report(
    *,
    profile: str = "standard",
    digest_bits: int = 384,
    max_cases: int | None = 64,
    max_mutations: int = 4,
    reduced_rounds: int | None = None,
) -> dict[str, Any]:
    """Cluster one-bit differential distances into coarse buckets.

    The report is intentionally statistical and deterministic. It helps spot
    suspicious low-distance clusters that deserve manual cryptanalysis.
    """

    if max_mutations <= 0:
        raise KryonError("max_mutations must be positive")
    cases = list(deterministic_corpus(profile=profile))
    if max_cases is not None:
        if max_cases <= 0:
            raise KryonError("max_cases must be positive")
        cases = cases[:max_cases]

    def h(data: bytes) -> bytes:
        if reduced_rounds is None:
            return digest(data, digest_bits)
        return _reduced_digest(data, AttackProfile(rounds=reduced_rounds, out_bits=max(384, digest_bits), digest_bits=digest_bits))

    buckets: dict[str, list[dict[str, Any]]] = {
        "very_low_<35%": [],
        "low_35_45%": [],
        "normal_45_55%": [],
        "high_55_65%": [],
        "very_high_>65%": [],
    }
    category_distances: dict[str, list[int]] = {}
    all_distances: list[int] = []

    for case in cases:
        base_digest = h(case.data)
        for mutated in mutate_case(case, max_mutations=max_mutations):
            md = h(mutated.data)
            distance = bit_distance(base_digest, md)
            ratio = distance / digest_bits
            all_distances.append(distance)
            category_distances.setdefault(case.category, []).append(distance)
            row = {
                "case": case.name,
                "mutated": mutated.name,
                "category": case.category,
                "length": len(case.data),
                "distance": distance,
                "ratio": round(ratio, 6),
            }
            if ratio < 0.35:
                buckets["very_low_<35%"].append(row)
            elif ratio < 0.45:
                buckets["low_35_45%"].append(row)
            elif ratio <= 0.55:
                buckets["normal_45_55%"].append(row)
            elif ratio <= 0.65:
                buckets["high_55_65%"].append(row)
            else:
                buckets["very_high_>65%"].append(row)

    bucket_summary = {
        name: {
            "count": len(rows),
            "examples": rows[:5],
        }
        for name, rows in buckets.items()
    }
    category_summary = {
        category: {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": round(statistics.mean(values), 4),
            "mean_ratio": round(statistics.mean(values) / digest_bits, 6),
        }
        for category, values in sorted(category_distances.items())
    }
    status = "passed"
    # A tiny number of low bucket entries can happen in smoke tests, but a large
    # systematic low-distance cluster would need investigation.
    if all_distances and len(buckets["very_low_<35%"]) > max(4, len(all_distances) // 20):
        status = "review_needed"

    return {
        "version": __version__,
        "generated_at_utc": _now(),
        "analysis": "differential_clustering",
        "profile": profile,
        "digest_bits": digest_bits,
        "reduced_rounds": reduced_rounds,
        "cases": len(cases),
        "mutation_checks": len(all_distances),
        "distance_summary": {
            "min": min(all_distances) if all_distances else 0,
            "max": max(all_distances) if all_distances else 0,
            "mean": round(statistics.mean(all_distances), 4) if all_distances else 0,
            "median": round(statistics.median(all_distances), 4) if all_distances else 0,
            "mean_ratio": round(statistics.mean(all_distances) / digest_bits, 6) if all_distances else 0,
        },
        "bucket_summary": bucket_summary,
        "category_summary": category_summary,
        "status": status,
    }


def reduced_attack_sweep(
    *,
    rounds: Sequence[int] = (1, 2, 3, 4, 6, 8),
    digest_bits: int = 16,
    attempts: int = 20_000,
    seed: int = 20260608,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for r in rounds:
        rows.append(
            reduced_collision_search(
                rounds=int(r),
                digest_bits=digest_bits,
                max_attempts=attempts,
                seed=seed + int(r),
                prefix=f"cw-v08-sweep-r{r}:",
            )
        )
    found = sum(1 for row in rows if row.get("found"))
    return {
        "version": __version__,
        "generated_at_utc": _now(),
        "analysis": "reduced_attack_sweep",
        "digest_bits": digest_bits,
        "attempts_per_round": attempts,
        "rounds": list(map(int, rounds)),
        "found_collisions": found,
        "rows": rows,
        "status": "passed" if found > 0 else "review_needed",
    }
