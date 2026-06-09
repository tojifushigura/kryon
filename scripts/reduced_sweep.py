from __future__ import annotations

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kryon.analysis import avalanche_report
from kryon.reduced import digest_reduced, make_profile


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Kryon reduced-round avalanche sweeps.")
    parser.add_argument("--rounds", default="1,2,3,4,6,8,10", help="Comma-separated absorb round counts")
    parser.add_argument("--samples", type=int, default=64)
    parser.add_argument("--message-size", type=int, default=128)
    parser.add_argument("--digest-bits", type=int, default=384)
    parser.add_argument("--seed", type=int, default=20260608)
    parser.add_argument("--format", choices=("table", "json", "csv"), default="table")
    parser.add_argument("--output", type=Path, help="Optional output file for json/csv/table text")
    return parser.parse_args()


def build_rows(args: argparse.Namespace) -> list[dict[str, float | int | str]]:
    rows = []
    for absorb_rounds in [int(x.strip()) for x in args.rounds.split(",") if x.strip()]:
        profile = make_profile(
            absorb_rounds=absorb_rounds,
            final_absorb_rounds=max(absorb_rounds, 2),
            final_mix_rounds=max(absorb_rounds, 2),
            post_mix_rounds=max(1, absorb_rounds // 2),
        )
        report = avalanche_report(
            samples=args.samples,
            message_size=args.message_size,
            digest_bits=args.digest_bits,
            seed=args.seed,
            hash_fn=lambda data, p=profile: digest_reduced(data, out_bits=384, digest_bits=args.digest_bits, profile=p),
        )
        row = report.as_dict()
        row.update(
            {
                "absorb_rounds": profile.absorb_rounds,
                "final_absorb_rounds": profile.final_absorb_rounds,
                "final_mix_rounds": profile.final_mix_rounds,
                "post_mix_rounds": profile.post_mix_rounds,
            }
        )
        rows.append(row)
    return rows


def render_table(rows: list[dict[str, float | int | str]]) -> str:
    headers = ["absorb", "final_absorb", "final_mix", "post", "min", "mean", "median", "max", "ratio"]
    lines = [" | ".join(headers), " | ".join(["---"] * len(headers))]
    for r in rows:
        lines.append(
            " | ".join(
                [
                    str(r["absorb_rounds"]),
                    str(r["final_absorb_rounds"]),
                    str(r["final_mix_rounds"]),
                    str(r["post_mix_rounds"]),
                    str(r["min_distance"]),
                    f"{float(r['mean_distance']):.2f}",
                    f"{float(r['median_distance']):.2f}",
                    str(r["max_distance"]),
                    f"{float(r['mean_ratio']):.4f}",
                ]
            )
        )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    rows = build_rows(args)

    if args.format == "json":
        rendered = json.dumps(rows, indent=2, ensure_ascii=False)
    elif args.format == "csv":
        import io

        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
        rendered = buffer.getvalue()
    else:
        rendered = render_table(rows)

    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
