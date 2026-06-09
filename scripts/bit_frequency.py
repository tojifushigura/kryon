from __future__ import annotations

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import json

from kryon.analysis import bit_frequency_report, structured_corpus


def main() -> int:
    parser = argparse.ArgumentParser(description="Kryon v0.4 bit-frequency smoke analyzer")
    parser.add_argument("--samples", type=int, default=256)
    parser.add_argument("--message-size", type=int, default=128)
    parser.add_argument("--digest-bits", type=int, choices=(256, 384, 512), default=384)
    parser.add_argument("--seed", type=int, default=20260608)
    parser.add_argument("--corpus", action="store_true", help="Use the structured corpus first, then deterministic random messages")
    parser.add_argument("--include-counts", action="store_true", help="Include per-bit one counts in JSON output")
    args = parser.parse_args()

    corpus = structured_corpus(seed=args.seed) if args.corpus else None
    report = bit_frequency_report(
        samples=args.samples,
        message_size=args.message_size,
        digest_bits=args.digest_bits,
        seed=args.seed,
        corpus=corpus,
    )
    print(json.dumps(report.as_dict(include_counts=args.include_counts), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
