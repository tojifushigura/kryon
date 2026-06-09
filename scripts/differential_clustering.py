from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kryon.attacks import differential_clustering_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Kryon v0.8 differential clustering report")
    parser.add_argument("--profile", choices=["smoke", "standard", "long"], default="standard")
    parser.add_argument("--digest-bits", type=int, default=384)
    parser.add_argument("--max-cases", type=int, default=64)
    parser.add_argument("--max-mutations", type=int, default=4)
    parser.add_argument("--reduced-rounds", type=int)
    parser.add_argument("--out", default="docs/reports/differential_clustering_v0.8.json")
    args = parser.parse_args(argv)

    report = differential_clustering_report(
        profile=args.profile,
        digest_bits=args.digest_bits,
        max_cases=args.max_cases,
        max_mutations=args.max_mutations,
        reduced_rounds=args.reduced_rounds,
    )
    out = ROOT / args.out if not Path(args.out).is_absolute() else Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"report": str(out), "status": report["status"]}, indent=2, ensure_ascii=False))
    return 0 if report["status"] in {"passed", "review_needed"} else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
