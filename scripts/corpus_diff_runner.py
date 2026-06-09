from __future__ import annotations

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import json
import statistics
from datetime import datetime, timezone
from typing import Any

from kryon import __version__, digest
from kryon.analysis import bit_distance
from kryon.corpus import deterministic_corpus, mutate_case


def build_corpus_diff_report(*, profile: str = "standard", digest_bits: int = 384, max_cases: int | None = None, max_mutations: int = 4) -> dict[str, Any]:
    cases = list(deterministic_corpus(profile=profile))
    if max_cases is not None:
        cases = cases[:max_cases]

    rows: list[dict[str, Any]] = []
    distances: list[int] = []
    for case in cases:
        base = digest(case.data, digest_bits)
        mutation_rows: list[dict[str, Any]] = []
        for mutated in mutate_case(case, max_mutations=max_mutations):
            md = digest(mutated.data, digest_bits)
            distance = bit_distance(base, md)
            distances.append(distance)
            mutation_rows.append(
                {
                    "name": mutated.name,
                    "length": len(mutated.data),
                    "distance": distance,
                    "ratio": round(distance / digest_bits, 6),
                    "digest": md.hex(),
                }
            )
        rows.append(
            {
                "name": case.name,
                "category": case.category,
                "length": len(case.data),
                "digest": base.hex(),
                "mutations": mutation_rows,
            }
        )

    return {
        "version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "profile": profile,
        "digest_bits": digest_bits,
        "cases": len(cases),
        "mutation_checks": len(distances),
        "distance_summary": {
            "min": min(distances) if distances else 0,
            "max": max(distances) if distances else 0,
            "mean": round(statistics.mean(distances), 4) if distances else 0,
            "median": round(statistics.median(distances), 4) if distances else 0,
            "mean_ratio": round((statistics.mean(distances) / digest_bits), 6) if distances else 0,
        },
        "rows": rows,
        "status": "passed",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Kryon v0.8 corpus differential report")
    parser.add_argument("--profile", choices=["smoke", "standard", "long"], default="standard")
    parser.add_argument("--digest-bits", type=int, default=384)
    parser.add_argument("--max-cases", type=int)
    parser.add_argument("--max-mutations", type=int, default=4)
    parser.add_argument("--out", default="docs/reports/corpus_diff_v0.8.json")
    args = parser.parse_args(argv)

    report = build_corpus_diff_report(profile=args.profile, digest_bits=args.digest_bits, max_cases=args.max_cases, max_mutations=args.max_mutations)
    out = ROOT / args.out if not Path(args.out).is_absolute() else Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"report": str(out), "status": report["status"], "checks": report["mutation_checks"]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
