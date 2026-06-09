from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kryon.toy_model import build_toy_model_report, toy_collision_model, toy_preimage_model


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Kryon v0.8 dependency-free toy SAT/SMT model")
    parser.add_argument("--mode", choices=["report", "collision", "preimage"], default="report")
    parser.add_argument("--fixed-prefix", default="cw-v08-toy:")
    parser.add_argument("--variable-bits", type=int, default=12)
    parser.add_argument("--digest-bits", type=int, default=8)
    parser.add_argument("--rounds", type=int, default=1)
    parser.add_argument("--target-hex", default="00")
    parser.add_argument("--out", default="docs/reports/toy_smt_v0.8.json")
    args = parser.parse_args(argv)

    if args.mode == "report":
        report = build_toy_model_report(
            fixed_prefix=args.fixed_prefix,
            variable_bits=args.variable_bits,
            digest_bits=args.digest_bits,
            rounds=args.rounds,
        )
    elif args.mode == "collision":
        report = toy_collision_model(
            fixed_prefix=args.fixed_prefix,
            variable_bits=args.variable_bits,
            digest_bits=args.digest_bits,
            rounds=args.rounds,
        )
    else:
        report = toy_preimage_model(
            target_hex=args.target_hex,
            fixed_prefix=args.fixed_prefix,
            variable_bits=args.variable_bits,
            digest_bits=args.digest_bits,
            rounds=args.rounds,
        )

    out = ROOT / args.out if not Path(args.out).is_absolute() else Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"report": str(out), "status": report.get("status")}, indent=2, ensure_ascii=False))
    return 0 if report.get("status") in {"passed", "sat"} else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
