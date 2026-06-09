from __future__ import annotations

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import json

from kryon.analysis import differential_trail_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Explore reduced-round differential propagation for Kryon")
    parser.add_argument("message", nargs="?", default="Kryon differential trail seed")
    parser.add_argument("--flipped-bit", type=int, default=0)
    parser.add_argument("--max-rounds", type=int, default=10)
    parser.add_argument("--out-bits", type=int, choices=(256, 384, 512), default=384)
    parser.add_argument("--digest-bits", type=int, default=128)
    args = parser.parse_args()

    report = differential_trail_report(
        args.message,
        flipped_bit=args.flipped_bit,
        max_rounds=args.max_rounds,
        out_bits=args.out_bits,
        digest_bits=args.digest_bits,
    )
    print(json.dumps(report.as_dict(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
