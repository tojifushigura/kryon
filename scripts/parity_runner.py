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
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from kryon import __version__
from kryon.kats import build_kat_document

ROOT = Path(__file__).resolve().parents[1]
RUST_DIR = ROOT / "native" / "rust"


def _run(cmd: list[str], *, cwd: Path, timeout: int = 120) -> dict[str, Any]:
    try:
        proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, timeout=timeout, check=False)
        return {
            "cmd": cmd,
            "returncode": proc.returncode,
            "stdout_tail": proc.stdout[-4000:],
            "stderr_tail": proc.stderr[-4000:],
        }
    except Exception as exc:  # pragma: no cover - defensive reporting path
        return {"cmd": cmd, "returncode": None, "error": repr(exc)}


def build_parity_report(*, run_cargo: bool = True, timeout: int = 120) -> dict[str, Any]:
    cargo_path = shutil.which("cargo")
    kat = build_kat_document(version=__version__, note="v0.8 Python canonical vectors used for native parity")

    report: dict[str, Any] = {
        "version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "canonical_digest_compatibility": "unchanged from v0.2/v0.3/v0.4/v0.5",
        "python_vectors": kat,
        "rust": {
            "cargo_available": bool(cargo_path),
            "cargo_path": cargo_path,
            "status": "not_run",
            "checks": [],
        },
    }

    rust = report["rust"]
    if not run_cargo:
        rust["status"] = "skipped_by_argument"
        return report
    if not cargo_path:
        rust["status"] = "skipped_cargo_not_found"
        return report

    checks = []
    checks.append(_run([cargo_path, "test", "--locked"], cwd=RUST_DIR, timeout=timeout))
    checks.append(_run([cargo_path, "run", "--example", "kryon_kat", "--locked"], cwd=RUST_DIR, timeout=timeout))
    rust["checks"] = checks
    rust["status"] = "passed" if all(item.get("returncode") == 0 for item in checks) else "failed"
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Kryon Python/Rust parity checks and write a JSON report")
    parser.add_argument("--out", default="docs/reports/parity_v0.8.json")
    parser.add_argument("--no-cargo", action="store_true", help="Generate vectors but do not execute cargo")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args(argv)

    report = build_parity_report(run_cargo=not args.no_cargo, timeout=args.timeout)
    out = ROOT / args.out if not Path(args.out).is_absolute() else Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"report": str(out), "rust_status": report["rust"]["status"]}, indent=2, ensure_ascii=False))
    return 0 if report["rust"]["status"] in {"passed", "skipped_cargo_not_found", "skipped_by_argument"} else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
