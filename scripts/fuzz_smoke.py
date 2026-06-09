from __future__ import annotations

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import json
import random
from pathlib import Path

from kryon import digest, new


def chunk_plan(length: int, rng: random.Random) -> list[int]:
    plan: list[int] = []
    remaining = length
    while remaining > 0:
        size = rng.randint(1, min(97, remaining))
        plan.append(size)
        remaining -= size
    return plan


def run_fuzz_smoke(*, cases: int = 256, max_size: int = 4096, seed: int = 20260608) -> dict[str, object]:
    rng = random.Random(seed)
    checked = 0
    max_chunks = 0
    max_message_size = 0

    for _ in range(cases):
        size = rng.randint(0, max_size)
        message = rng.randbytes(size)
        max_message_size = max(max_message_size, size)

        for out_bits in (256, 384, 512):
            expected = digest(message, out_bits)
            h = new(out_bits=out_bits)
            offset = 0
            plan = chunk_plan(size, rng)
            max_chunks = max(max_chunks, len(plan))
            for chunk_size in plan:
                h.update(message[offset : offset + chunk_size])
                offset += chunk_size
                _ = h.digest()
            assert h.digest() == expected
            checked += 1

    return {
        "version": __import__("kryon").__version__,
        "cases": cases,
        "digest_variants_per_case": 3,
        "total_digest_checks": checked,
        "max_size": max_size,
        "max_message_size_seen": max_message_size,
        "max_chunks_seen": max_chunks,
        "seed": seed,
        "status": "passed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Kryon deterministic fuzz/smoke streaming checker")
    parser.add_argument("--cases", type=int, default=256)
    parser.add_argument("--max-size", type=int, default=4096)
    parser.add_argument("--seed", type=int, default=20260608)
    parser.add_argument("--out", default="docs/reports/fuzz_smoke_v0.8.json")
    args = parser.parse_args()

    report = run_fuzz_smoke(cases=args.cases, max_size=args.max_size, seed=args.seed)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
