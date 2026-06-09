from __future__ import annotations

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import json
import random
from datetime import datetime, timezone
from typing import Any

from kryon import __version__, digest, new
from kryon.corpus import chunk_plans, deterministic_corpus


def run_long_fuzz(*, cases: int = 16, max_size: int = 512, seed: int = 20260608, include_corpus: bool = True) -> dict[str, Any]:
    rng = random.Random(seed)
    checked = 0
    max_chunks = 0
    max_message_size = 0
    digest_variants = (256, 384, 512)

    messages: list[bytes] = []
    if include_corpus:
        messages.extend(case.data for case in deterministic_corpus(profile="standard", seed=seed))
    while len(messages) < cases:
        size = rng.randint(0, max_size)
        messages.append(rng.randbytes(size))
    messages = messages[:cases]

    for message in messages:
        max_message_size = max(max_message_size, len(message))
        plans = chunk_plans(len(message))
        max_chunks = max(max_chunks, max((len(p) for p in plans), default=0))
        for out_bits in digest_variants:
            expected = digest(message, out_bits)
            for plan in plans:
                h = new(out_bits=out_bits)
                offset = 0
                for chunk_size in plan:
                    h.update(message[offset : offset + chunk_size])
                    offset += chunk_size
                    # digest() must be non-mutating even mid-stream.
                    _ = h.digest()
                assert offset == len(message)
                assert h.digest() == expected
                assert h.hexdigest() == expected.hex()
                checked += 1

    return {
        "version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "cases": len(messages),
        "digest_variants": list(digest_variants),
        "streaming_plans_per_case": 5,
        "total_streaming_checks": checked,
        "max_size": max_size,
        "max_message_size_seen": max_message_size,
        "max_chunks_seen": max_chunks,
        "seed": seed,
        "include_corpus": include_corpus,
        "status": "passed",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Kryon v0.8 long deterministic streaming fuzz")
    parser.add_argument("--cases", type=int, default=16)
    parser.add_argument("--max-size", type=int, default=512)
    parser.add_argument("--seed", type=int, default=20260608)
    parser.add_argument("--no-corpus", action="store_true")
    parser.add_argument("--out", default="docs/reports/long_fuzz_v0.8.json")
    args = parser.parse_args(argv)
    report = run_long_fuzz(cases=args.cases, max_size=args.max_size, seed=args.seed, include_corpus=not args.no_corpus)
    out = ROOT / args.out if not Path(args.out).is_absolute() else Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"report": str(out), "status": report["status"], "checks": report["total_streaming_checks"]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
