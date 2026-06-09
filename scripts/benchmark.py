from __future__ import annotations

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import hashlib
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kryon import new


def bench_kryon(data: bytes, bits: int, chunk_size: int) -> float:
    h = new(out_bits=bits)
    start = time.perf_counter()
    for i in range(0, len(data), chunk_size):
        h.update(data[i : i + chunk_size])
    h.digest()
    elapsed = time.perf_counter() - start
    return len(data) / elapsed / 1024 / 1024


def bench_hashlib(data: bytes, name: str, chunk_size: int) -> float:
    h = hashlib.new(name)
    start = time.perf_counter()
    for i in range(0, len(data), chunk_size):
        h.update(data[i : i + chunk_size])
    h.digest()
    elapsed = time.perf_counter() - start
    return len(data) / elapsed / 1024 / 1024


def main() -> None:
    size = int(os.environ.get("KRYON_BENCH_SIZE", 4 * 1024 * 1024))
    chunk_size = int(os.environ.get("KRYON_BENCH_CHUNK", 1024 * 1024))
    data = os.urandom(size)

    print(f"Data: {size / 1024 / 1024:.1f} MiB, chunk: {chunk_size / 1024:.0f} KiB")
    print(f"Kryon-384 pure Python: {bench_kryon(data, 384, chunk_size):.3f} MiB/s")
    print(f"hashlib sha256 native:       {bench_hashlib(data, 'sha256', chunk_size):.3f} MiB/s")
    print(f"hashlib sha3_384 native:     {bench_hashlib(data, 'sha3_384', chunk_size):.3f} MiB/s")


if __name__ == "__main__":
    main()
