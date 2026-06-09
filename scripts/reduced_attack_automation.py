from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kryon.attacks import reduced_attack_sweep, reduced_collision_search, reduced_prefix_preimage_search


def parse_rounds(value: str) -> tuple[int, ...]:
    out: list[int] = []
    for item in value.split(","):
        item = item.strip()
        if item:
            out.append(int(item))
    return tuple(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Kryon v0.8 reduced-round attack automation")
    parser.add_argument("--mode", choices=["sweep", "collision", "prefix"], default="sweep")
    parser.add_argument("--rounds", default="1,2,3,4,6,8")
    parser.add_argument("--digest-bits", type=int, default=16)
    parser.add_argument("--attempts", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=20260608)
    parser.add_argument("--target-prefix-hex", default="00")
    parser.add_argument("--out", default="docs/reports/reduced_attack_v0.8.json")
    args = parser.parse_args(argv)

    if args.mode == "sweep":
        report = reduced_attack_sweep(rounds=parse_rounds(args.rounds), digest_bits=args.digest_bits, attempts=args.attempts, seed=args.seed)
    elif args.mode == "collision":
        first_round = parse_rounds(args.rounds)[0]
        report = reduced_collision_search(rounds=first_round, digest_bits=args.digest_bits, max_attempts=args.attempts, seed=args.seed)
    else:
        first_round = parse_rounds(args.rounds)[0]
        report = reduced_prefix_preimage_search(
            rounds=first_round,
            digest_bits=args.digest_bits,
            max_attempts=args.attempts,
            seed=args.seed,
            target_prefix_hex=args.target_prefix_hex,
        )

    out = ROOT / args.out if not Path(args.out).is_absolute() else Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"report": str(out), "status": report.get("status")}, indent=2, ensure_ascii=False))
    return 0 if report.get("status") in {"passed", "review_needed"} else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
