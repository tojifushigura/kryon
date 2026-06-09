from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .version import __version__
from .core import KryonError
from .reduced import digest_reduced, make_profile


@dataclass(frozen=True)
class ToyModelConfig:
    """Tiny dependency-free constraint model for reduced Kryon outputs.

    This is not a general SMT solver. It is a reproducible brute-force backend
    with a SAT/SMT-like interface so the project can later swap in Z3, Boolector
    or a CNF encoder without changing reports and tests.
    """

    fixed_prefix: bytes = b"cw-v08-toy:"
    variable_bits: int = 12
    digest_bits: int = 8
    rounds: int = 1
    out_bits: int = 384

    def validate(self) -> None:
        if self.variable_bits < 1 or self.variable_bits > 24:
            raise KryonError("variable_bits must be in the range 1..24 for the dependency-free toy backend")
        if self.digest_bits < 8 or self.digest_bits > self.out_bits or self.digest_bits % 8 != 0:
            raise KryonError("digest_bits must be a byte-aligned value between 8 and out_bits")
        if self.rounds < 1 or self.rounds > 18:
            raise KryonError("rounds must be in the range 1..18")
        if self.out_bits not in {256, 384, 512}:
            raise KryonError("out_bits must be one of: 256, 384, 512")

    @property
    def domain_size(self) -> int:
        return 1 << self.variable_bits

    @property
    def variable_bytes(self) -> int:
        return (self.variable_bits + 7) // 8

    def message_for_value(self, value: int) -> bytes:
        if value < 0 or value >= self.domain_size:
            raise KryonError("assignment is outside of the toy model domain")
        return self.fixed_prefix + value.to_bytes(self.variable_bytes, "little")

    def as_dict(self) -> dict[str, str | int]:
        return {
            "fixed_prefix_hex": self.fixed_prefix.hex(),
            "variable_bits": self.variable_bits,
            "domain_size": self.domain_size,
            "digest_bits": self.digest_bits,
            "rounds": self.rounds,
            "out_bits": self.out_bits,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _digest(message: bytes, config: ToyModelConfig) -> bytes:
    profile = make_profile(
        absorb_rounds=config.rounds,
        final_absorb_rounds=config.rounds,
        final_mix_rounds=config.rounds,
        post_mix_rounds=max(1, config.rounds // 2),
    )
    return digest_reduced(message, out_bits=config.out_bits, digest_bits=config.digest_bits, profile=profile)


def toy_collision_model(
    *,
    fixed_prefix: bytes | str = b"cw-v08-toy:",
    variable_bits: int = 12,
    digest_bits: int = 8,
    rounds: int = 1,
    out_bits: int = 384,
) -> dict[str, Any]:
    """Enumerate a tiny domain and return the first truncated collision."""

    prefix = fixed_prefix.encode("utf-8") if isinstance(fixed_prefix, str) else bytes(fixed_prefix)
    config = ToyModelConfig(prefix, variable_bits, digest_bits, rounds, out_bits)
    config.validate()

    seen: dict[bytes, tuple[int, bytes]] = {}
    for value in range(config.domain_size):
        message = config.message_for_value(value)
        d = _digest(message, config)
        if d in seen:
            previous_value, previous_message = seen[d]
            return {
                "version": __version__,
                "generated_at_utc": _now(),
                "model": "dependency_free_toy_collision",
                "solver": "bruteforce_enum",
                "config": config.as_dict(),
                "status": "sat",
                "assignments_checked": value + 1,
                "digest_hex": d.hex(),
                "assignment_a": previous_value,
                "assignment_b": value,
                "message_a_hex": previous_message.hex(),
                "message_b_hex": message.hex(),
            }
        seen[d] = (value, message)
    return {
        "version": __version__,
        "generated_at_utc": _now(),
        "model": "dependency_free_toy_collision",
        "solver": "bruteforce_enum",
        "config": config.as_dict(),
        "status": "unsat_in_domain",
        "assignments_checked": config.domain_size,
    }


def toy_preimage_model(
    *,
    target_hex: str,
    fixed_prefix: bytes | str = b"cw-v08-toy:",
    variable_bits: int = 12,
    digest_bits: int = 8,
    rounds: int = 1,
    out_bits: int = 384,
) -> dict[str, Any]:
    """Enumerate a tiny domain looking for an exact truncated digest."""

    try:
        target = bytes.fromhex(target_hex)
    except ValueError as exc:
        raise KryonError("target_hex is not valid hex") from exc
    if len(target) * 8 != digest_bits:
        raise KryonError("target_hex length must equal digest_bits")
    prefix = fixed_prefix.encode("utf-8") if isinstance(fixed_prefix, str) else bytes(fixed_prefix)
    config = ToyModelConfig(prefix, variable_bits, digest_bits, rounds, out_bits)
    config.validate()

    for value in range(config.domain_size):
        message = config.message_for_value(value)
        d = _digest(message, config)
        if d == target:
            return {
                "version": __version__,
                "generated_at_utc": _now(),
                "model": "dependency_free_toy_preimage",
                "solver": "bruteforce_enum",
                "config": config.as_dict(),
                "target_hex": target_hex,
                "status": "sat",
                "assignments_checked": value + 1,
                "assignment": value,
                "message_hex": message.hex(),
            }
    return {
        "version": __version__,
        "generated_at_utc": _now(),
        "model": "dependency_free_toy_preimage",
        "solver": "bruteforce_enum",
        "config": config.as_dict(),
        "target_hex": target_hex,
        "status": "unsat_in_domain",
        "assignments_checked": config.domain_size,
    }


def build_toy_model_report(
    *,
    fixed_prefix: bytes | str = b"cw-v08-toy:",
    variable_bits: int = 12,
    digest_bits: int = 8,
    rounds: int = 1,
) -> dict[str, Any]:
    collision = toy_collision_model(
        fixed_prefix=fixed_prefix,
        variable_bits=variable_bits,
        digest_bits=digest_bits,
        rounds=rounds,
    )
    target_hex = collision.get("digest_hex", "00")
    preimage = toy_preimage_model(
        target_hex=str(target_hex),
        fixed_prefix=fixed_prefix,
        variable_bits=variable_bits,
        digest_bits=digest_bits,
        rounds=rounds,
    )
    return {
        "version": __version__,
        "generated_at_utc": _now(),
        "analysis": "toy_smt_sat_model",
        "note": "Dependency-free brute-force backend with SAT/SMT-style report fields; intended for later replacement with a real solver.",
        "collision": collision,
        "preimage": preimage,
        "status": "passed" if collision["status"] == "sat" and preimage["status"] == "sat" else "review_needed",
    }
