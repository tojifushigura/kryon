from __future__ import annotations

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from kryon import __version__

ROOT = Path(__file__).resolve().parents[1]
RUST_DIR = ROOT / "native" / "rust"


def run_rust_benchmark(*, iterations: int = 2000, size: int = 4096, timeout: int = 120) -> dict[str, Any]:
    cargo_path = shutil.which("cargo")
    report: dict[str, Any] = {
        "version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "iterations": iterations,
        "message_size": size,
        "cargo_available": bool(cargo_path),
        "status": "not_run",
    }
    if not cargo_path:
        report["status"] = "skipped_cargo_not_found"
        return report
    proc = subprocess.run(
        [cargo_path, "run", "--release", "--example", "kryon_bench", "--", str(iterations), str(size)],
        cwd=RUST_DIR,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    report.update({"status": "passed" if proc.returncode == 0 else "failed", "returncode": proc.returncode, "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:]})
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Kryon Rust benchmark example when Cargo is available")
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--size", type=int, default=4096)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--out", default="docs/reports/rust_benchmark_v0.8.json")
    args = parser.parse_args()

    report = run_rust_benchmark(iterations=args.iterations, size=args.size, timeout=args.timeout)
    out = ROOT / args.out if not Path(args.out).is_absolute() else Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["status"] in {"passed", "skipped_cargo_not_found"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
