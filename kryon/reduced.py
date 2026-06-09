from __future__ import annotations

from .core import KryonError, KryonHash, RoundProfile


def _validate_digest_bits(digest_bits: int) -> None:
    if not isinstance(digest_bits, int):
        raise KryonError("digest_bits must be an integer")
    if digest_bits < 8:
        raise KryonError("digest_bits must be >= 8")
    if digest_bits > 512:
        raise KryonError("digest_bits must be <= 512")
    if digest_bits % 8 != 0:
        raise KryonError("digest_bits must be a multiple of 8")


def make_profile(
    *,
    absorb_rounds: int = 4,
    final_absorb_rounds: int | None = None,
    final_mix_rounds: int | None = None,
    post_mix_rounds: int | None = None,
) -> RoundProfile:
    """Create a reduced-round profile for experiments.

    This is intentionally separate from the canonical API. Use it only for
    avalanche sweeps, toy collision searches, and other cryptanalysis tooling.
    """

    profile = RoundProfile(
        absorb_rounds=absorb_rounds,
        final_absorb_rounds=final_absorb_rounds if final_absorb_rounds is not None else max(absorb_rounds, 2),
        final_mix_rounds=final_mix_rounds if final_mix_rounds is not None else max(absorb_rounds, 2),
        post_mix_rounds=post_mix_rounds if post_mix_rounds is not None else max(1, absorb_rounds // 2),
    )
    profile.validate()
    return profile


def new_reduced(
    data: bytes | bytearray | memoryview | str = b"",
    *,
    out_bits: int = 384,
    profile: RoundProfile | None = None,
    absorb_rounds: int = 4,
    final_absorb_rounds: int | None = None,
    final_mix_rounds: int | None = None,
    post_mix_rounds: int | None = None,
) -> KryonHash:
    """Return a Kryon object using a non-canonical round profile.

    Passing ``profile`` takes precedence over the individual round arguments.
    The returned object still exposes the normal hashlib-like ``update`` and
    ``digest`` methods, but the result is not a canonical Kryon digest.
    """

    selected = profile or make_profile(
        absorb_rounds=absorb_rounds,
        final_absorb_rounds=final_absorb_rounds,
        final_mix_rounds=final_mix_rounds,
        post_mix_rounds=post_mix_rounds,
    )
    h = KryonHash(out_bits=out_bits, _round_profile=selected)
    if data:
        h.update(data)
    return h


def digest_reduced(
    data: bytes | bytearray | memoryview | str,
    *,
    out_bits: int = 384,
    digest_bits: int | None = None,
    profile: RoundProfile | None = None,
    absorb_rounds: int = 4,
    final_absorb_rounds: int | None = None,
    final_mix_rounds: int | None = None,
    post_mix_rounds: int | None = None,
) -> bytes:
    """Hash data with a reduced-round profile and optional digest truncation.

    ``digest_bits`` is meant for toy collision searches. It truncates the output
    to byte boundaries and must never be used as a security setting.
    """

    bits = digest_bits if digest_bits is not None else out_bits
    _validate_digest_bits(bits)
    if bits > out_bits:
        raise KryonError("digest_bits cannot exceed out_bits")
    full = new_reduced(
        data,
        out_bits=out_bits,
        profile=profile,
        absorb_rounds=absorb_rounds,
        final_absorb_rounds=final_absorb_rounds,
        final_mix_rounds=final_mix_rounds,
        post_mix_rounds=post_mix_rounds,
    ).digest()
    return full[: bits // 8]


def hexdigest_reduced(
    data: bytes | bytearray | memoryview | str,
    *,
    out_bits: int = 384,
    digest_bits: int | None = None,
    profile: RoundProfile | None = None,
    absorb_rounds: int = 4,
    final_absorb_rounds: int | None = None,
    final_mix_rounds: int | None = None,
    post_mix_rounds: int | None = None,
) -> str:
    return digest_reduced(
        data,
        out_bits=out_bits,
        digest_bits=digest_bits,
        profile=profile,
        absorb_rounds=absorb_rounds,
        final_absorb_rounds=final_absorb_rounds,
        final_mix_rounds=final_mix_rounds,
        post_mix_rounds=post_mix_rounds,
    ).hex()
