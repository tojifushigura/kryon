from __future__ import annotations

import struct
from dataclasses import dataclass, field
from typing import Iterable

MASK64 = (1 << 64) - 1
BLOCK_SIZE = 32
_ALLOWED_OUT_BITS = {256, 384, 512}
_MAX_MESSAGE_BYTES = (1 << 64) - 1
_VERSION_TAG = 0x4352574556323032  # "CRWEV202" domain tag for v0.2


class KryonError(ValueError):
    """Raised when Kryon parameters are invalid."""


@dataclass(frozen=True)
class RoundProfile:
    """Internal round profile used by the reference implementation.

    The default profile is the canonical Kryon profile. Non-default
    profiles are for reduced-round cryptanalysis and test tooling only.
    """

    absorb_rounds: int = 10
    final_absorb_rounds: int = 14
    final_mix_rounds: int = 16
    post_mix_rounds: int = 6

    def validate(self) -> None:
        values = {
            "absorb_rounds": self.absorb_rounds,
            "final_absorb_rounds": self.final_absorb_rounds,
            "final_mix_rounds": self.final_mix_rounds,
            "post_mix_rounds": self.post_mix_rounds,
        }
        for name, value in values.items():
            if not isinstance(value, int):
                raise KryonError(f"{name} must be an integer")
            if value < 1:
                raise KryonError(f"{name} must be >= 1")
            if value > 18:
                raise KryonError(f"{name} must be <= 18")


CANONICAL_ROUND_PROFILE = RoundProfile()


def _rotl64(x: int, n: int) -> int:
    n &= 63
    if n == 0:
        return x & MASK64
    return ((x << n) | (x >> (64 - n))) & MASK64


def _splitmix64(seed: int) -> int:
    z = (seed + 0x9E3779B97F4A7C15) & MASK64
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9 & MASK64
    z = (z ^ (z >> 27)) * 0x94D049BB133111EB & MASK64
    return (z ^ (z >> 31)) & MASK64


_ALPHA = [11, 17, 29, 37, 43, 53, 7, 13, 19, 31, 47, 59]
_BETA = [5, 23, 41, 3, 27, 49, 9, 35, 15, 45, 21, 61]
_GAMMA = [7, 19, 33, 47, 13, 29, 43, 57, 11, 25, 39, 53]
_PI = [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5]
_PSI = [0, 5, 10, 15, 20, 1, 6, 11, 16, 21, 2, 7, 12, 17, 22, 3, 8, 13, 18, 23, 4, 9, 14, 19]


def _init_constants() -> tuple[list[int], list[int], list[list[int]], list[list[int]]]:
    seed = 0x43524F5353574541  # "CROSSWEA" domain seed
    k1: list[int] = []
    k2: list[int] = []
    rc64: list[list[int]] = []
    s = seed

    for i in range(12):
        s = _splitmix64(s + i + _VERSION_TAG)
        k1.append(s)
        s = _splitmix64(s + 0x123456789ABCDEF)
        k2.append(s)

    # 18 rows are generated because v0.2 uses 14-round final absorption
    # and 16-round finalization in addition to 10-round regular absorption.
    for r in range(18):
        row = []
        for i in range(12):
            s = _splitmix64(s + r * 17 + i + 0xA5A5A5A5)
            row.append(s)
        rc64.append(row)

    rc257: list[list[int]] = []
    x = 97
    for r in range(18):
        row = []
        for j in range(24):
            x = (x * 45 + 17 + r + j) % 257
            row.append(x)
        rc257.append(row)

    return k1, k2, rc64, rc257


_K1, _K2, _RC64, _RC257 = _init_constants()

_IV_B = [
    0x243F6A8885A308D3,
    0x13198A2E03707344,
    0xA4093822299F31D0,
    0x082EFA98EC4E6C89,
    0x452821E638D01377,
    0xBE5466CF34E90C6C,
    0xC0AC29B7C97C50DD,
    0x3F84D5B5B5470917,
    0x9216D5D98979FB1B,
    0xD1310BA698DFB5AC,
    0x2FFD72DBD01ADFB7,
    0xB8E1AFED6A267E96,
]
_IV_R = [(i * i + 17 * i + 43) % 257 for i in range(24)]


def _ensure_bytes(data: bytes | bytearray | memoryview | str) -> bytes:
    if isinstance(data, str):
        return data.encode("utf-8")
    return bytes(data)


def _permute(binary_state: Iterable[int], residue_state: Iterable[int], rounds: int) -> tuple[list[int], list[int]]:
    b = list(binary_state)
    r_state = list(residue_state)

    if rounds > len(_RC64):
        raise KryonError("round count exceeds generated constants")

    for r in range(rounds):
        lift = [0] * 12
        for i in range(12):
            a = r_state[(2 * i) % 24]
            c = r_state[(2 * i + 1) % 24]
            x = ((a + 1) * _K1[i] + (c + 1) * _K2[i] + _RC64[r][i]) & MASK64
            y = _rotl64(
                (((a + 1) * 0x9E3779B185EBCA87) ^ ((c + 1) * 0xC2B2AE3D27D4EB4F)) & MASK64,
                (7 * i + 3 * r + 1) % 64,
            )
            lift[i] = (x ^ y) & MASK64

        mixed = [0] * 12
        for i in range(12):
            t = (b[i] + _rotl64(b[(i + 1) % 12], _ALPHA[i]) + lift[i]) & MASK64
            t ^= _rotl64(b[(i + 4) % 12], _BETA[i])
            t = (t + _rotl64(b[(i + 8) % 12], _GAMMA[i])) & MASK64
            t ^= _rotl64(lift[(i + 3) % 12], (i * 9 + r * 5 + 1) % 64)
            mixed[i] = t & MASK64
        b = [(mixed[_PI[i]] ^ lift[(5 * i + 7) % 12]) & MASK64 for i in range(12)]

        residue_mixed = [0] * 24
        for j in range(24):
            injected = (b[j % 12] >> (0 if j < 12 else 32)) & 0xFF
            x = (
                r_state[j]
                + 3 * r_state[(j + 1) % 24]
                + 5 * r_state[(j + 7) % 24]
                + 7 * r_state[(j + 13) % 24]
                + injected
                + _RC257[r][j]
            ) % 257
            residue_mixed[j] = pow(x, 3, 257)
        r_state = [residue_mixed[_PSI[j]] for j in range(24)]

    return b, r_state


def _initial_state(out_bits: int) -> tuple[list[int], list[int]]:
    if out_bits not in _ALLOWED_OUT_BITS:
        raise KryonError("out_bits must be one of: 256, 384, 512")

    b = _IV_B.copy()
    r_state = _IV_R.copy()
    b[0] ^= _VERSION_TAG
    b[1] ^= _rotl64(_VERSION_TAG, out_bits // 8)
    b[10] ^= out_bits
    b[11] ^= ((out_bits << 32) | BLOCK_SIZE) & MASK64

    for j in range(24):
        r_state[j] = (r_state[j] + ((out_bits >> (j % 8)) & 0xFF) + j + (_VERSION_TAG >> (j % 56) & 0xFF)) % 257
    return b, r_state


def _padding_blocks(tail: bytes, total_len: int, out_bits: int) -> bytes:
    if total_len > _MAX_MESSAGE_BYTES:
        raise KryonError("message is too large for the v0.2 reference encoding")
    payload = tail + b"\x80"
    trailer = total_len.to_bytes(8, "little") + out_bits.to_bytes(4, "little") + b"CW02"
    while (len(payload) + len(trailer)) % BLOCK_SIZE != 0:
        payload += b"\x00"
    return payload + trailer


@dataclass
class KryonHash:
    """hashlib-like streaming interface for canonical Kryon.

    Kryon is an experimental research hash. Do not use it as a replacement
    for SHA-2/SHA-3/BLAKE2/BLAKE3 in production systems without external review.
    """

    out_bits: int = 384
    _round_profile: RoundProfile = field(default_factory=RoundProfile, repr=False)
    _b: list[int] = field(init=False, repr=False)
    _r_state: list[int] = field(init=False, repr=False)
    _tail: bytearray = field(default_factory=bytearray, repr=False)
    _total_len: int = 0
    _block_index: int = 0

    def __post_init__(self) -> None:
        self._round_profile.validate()
        self._b, self._r_state = _initial_state(self.out_bits)

    @property
    def digest_size(self) -> int:
        return self.out_bits // 8

    @property
    def block_size(self) -> int:
        return BLOCK_SIZE

    @property
    def name(self) -> str:
        return f"kryon-{self.out_bits}"

    @property
    def round_profile(self) -> RoundProfile:
        return self._round_profile

    def _absorb_block(self, block: bytes, *, final: bool = False) -> None:
        if len(block) != BLOCK_SIZE:
            raise KryonError("internal block size error")

        idx = self._block_index
        words = struct.unpack("<4Q", block)

        for i in range(4):
            lane = (i + (idx & 3)) % 12
            self._b[lane] ^= words[i]
            self._b[(lane + 5) % 12] = (self._b[(lane + 5) % 12] + _rotl64(words[i] ^ _K1[(idx + i) % 12], (idx + 13 * i) % 64)) & MASK64

        self._b[4] ^= ((idx << 1) | int(final)) & MASK64
        self._b[5] ^= _rotl64(((idx + 1) * 0x9E3779B185EBCA87) & MASK64, idx % 64)
        self._b[11] ^= ((idx << 48) ^ (BLOCK_SIZE << 40) ^ (self.out_bits << 8) ^ _VERSION_TAG) & MASK64

        if final:
            self._b[8] ^= self._total_len & MASK64
            self._b[9] ^= _rotl64((self._total_len ^ (self.out_bits << 32)) & MASK64, 17)
            self._b[10] ^= _rotl64(((self._total_len + 1) * 0xD6E8FEB86659FD93) & MASK64, 29)

        for j in range(24):
            byte_a = block[j % BLOCK_SIZE]
            byte_b = block[(j * 7 + 13) % BLOCK_SIZE]
            byte_c = block[(j * 11 + 5) % BLOCK_SIZE]
            length_inject = ((self._total_len >> ((j % 8) * 8)) & 0xFF) if final else 0
            self._r_state[j] = (
                self._r_state[j]
                + byte_a
                + 3 * byte_b
                + 5 * byte_c
                + j
                + (idx & 0xFF)
                + length_inject
                + (17 if final else 0)
            ) % 257

        rounds = self._round_profile.final_absorb_rounds if final else self._round_profile.absorb_rounds
        self._b, self._r_state = _permute(self._b, self._r_state, rounds=rounds)
        self._block_index += 1

    def update(self, data: bytes | bytearray | memoryview | str) -> "KryonHash":
        data_bytes = _ensure_bytes(data)
        if not data_bytes:
            return self
        if self._total_len + len(data_bytes) > _MAX_MESSAGE_BYTES:
            raise KryonError("message is too large for the v0.2 reference encoding")

        self._total_len += len(data_bytes)
        self._tail.extend(data_bytes)

        while len(self._tail) >= BLOCK_SIZE:
            block = bytes(self._tail[:BLOCK_SIZE])
            del self._tail[:BLOCK_SIZE]
            self._absorb_block(block, final=False)
        return self

    def copy(self) -> "KryonHash":
        clone = KryonHash(out_bits=self.out_bits, _round_profile=self._round_profile)
        clone._b = self._b.copy()
        clone._r_state = self._r_state.copy()
        clone._tail = self._tail.copy()
        clone._total_len = self._total_len
        clone._block_index = self._block_index
        return clone

    def _finalized_copy(self) -> "KryonHash":
        h = self.copy()
        final_payload = _padding_blocks(bytes(h._tail), h._total_len, h.out_bits)
        h._tail.clear()
        final_blocks = len(final_payload) // BLOCK_SIZE
        for i in range(final_blocks):
            block = final_payload[i * BLOCK_SIZE : (i + 1) * BLOCK_SIZE]
            h._absorb_block(block, final=(i == final_blocks - 1))

        for i in range(12):
            a = h._r_state[(2 * i) % 24]
            c = h._r_state[(2 * i + 1) % 24]
            d = h._r_state[(2 * i + 5) % 24]
            fold = (a & 0x1FF) | ((c & 0x1FF) << 9) | ((d & 0x1FF) << 18)
            h._b[i] ^= _rotl64((fold * 0xD6E8FEB86659FD93) & MASK64, (11 * i) % 64)
            h._b[i] = (h._b[i] + _rotl64(_K2[i] ^ h._total_len, (7 * i + 3) % 64)) & MASK64

        for j in range(24):
            h._r_state[j] = (h._r_state[j] + ((h._b[j % 12] >> (j % 32)) & 0xFF) + _RC257[0][j] + (h.out_bits & 0xFF)) % 257

        h._b, h._r_state = _permute(h._b, h._r_state, rounds=h._round_profile.final_mix_rounds)

        for i in range(12):
            a = h._r_state[(2 * i) % 24]
            c = h._r_state[(2 * i + 11) % 24]
            h._b[i] ^= _rotl64((((a + 1) * _K1[i]) ^ ((c + 1) * _K2[i])) & MASK64, (3 + 5 * i) % 64)

        h._b, h._r_state = _permute(h._b, h._r_state, rounds=h._round_profile.post_mix_rounds)
        return h

    def digest(self) -> bytes:
        h = self._finalized_copy()
        out = b"".join(struct.pack("<Q", x) for x in h._b)
        return out[: self.out_bits // 8]

    def hexdigest(self) -> str:
        return self.digest().hex()


def new(data: bytes | bytearray | memoryview | str = b"", out_bits: int = 384) -> KryonHash:
    h = KryonHash(out_bits=out_bits)
    if data:
        h.update(data)
    return h


def digest(data: bytes | bytearray | memoryview | str, out_bits: int = 384) -> bytes:
    return new(data, out_bits=out_bits).digest()


def hexdigest(data: bytes | bytearray | memoryview | str, out_bits: int = 384) -> str:
    return digest(data, out_bits=out_bits).hex()
