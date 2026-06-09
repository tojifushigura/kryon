from __future__ import annotations

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kryon.analysis import avalanche_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a canonical Kryon avalanche smoke report.")
    parser.add_argument("--samples", type=int, default=64)
    parser.add_argument("--message-size", type=int, default=128)
    parser.add_argument("--digest-bits", type=int, choices=(256, 384, 512), default=384)
    parser.add_argument("--seed", type=int, default=20260608)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = avalanche_report(samples=args.samples, message_size=args.message_size, digest_bits=args.digest_bits, seed=args.seed)
    if args.json:
        print(json.dumps(report.as_dict(), indent=2))
    else:
        print(f"samples={report.samples} message_bits={report.message_bits} digest_bits={report.digest_bits}")
        print(
            f"min={report.min_distance} max={report.max_distance} "
            f"mean={report.mean_distance:.2f} median={report.median_distance:.2f} "
            f"expected={report.expected_distance:.2f} ratio={report.mean_ratio:.4f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
