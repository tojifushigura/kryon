from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kryon import __version__
from kryon.kats import build_kat_document
from scripts.release_check import build_release_report
from scripts.c_corpus_parity import build_c_corpus_report


def _cmd(args: list[str], timeout: int = 180) -> dict[str, Any]:
    proc = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=timeout, check=False)
    return {"args": args, "returncode": proc.returncode, "status": "passed" if proc.returncode == 0 else "failed", "stdout_tail": proc.stdout[-4000:], "stderr_tail": proc.stderr[-4000:]}


def build_final_audit(*, run_c: bool = True, run_cargo: bool = False) -> dict[str, Any]:
    report: dict[str, Any] = {
        "version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "not_ready",
        "checks": {},
    }
    checks = report["checks"]
    checks["pytest"] = _cmd([sys.executable, "-m", "pytest", "-q"])
    checks["release_check"] = build_release_report(run_pytest=False, run_cargo=run_cargo, run_c=run_c, profile="smoke")
    checks["c_corpus_parity"] = build_c_corpus_report(profile="smoke", max_cases=32, run_compile=run_c)
    checks["kat_document"] = build_kat_document(version=__version__, note="v1.0 final KAT document")
    passed = checks["pytest"]["status"] == "passed" and checks["release_check"]["status"] == "passed" and checks["c_corpus_parity"]["status"] in {"passed", "skipped_c_compiler_not_found", "skipped_by_argument"}
    report["decision"] = "ready_to_launch_as_v1_software_project" if passed else "not_ready"
    report["security_boundary"] = "Ready to launch as software/checksum/integrity project; external cryptographic audit is still required before claiming standard-grade security for signatures, password storage, blockchain, or TLS-like protocols."
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the final Kryon v1.0 launch audit")
    parser.add_argument("--no-c", action="store_true")
    parser.add_argument("--run-cargo", action="store_true")
    parser.add_argument("--out", default="docs/reports/final_audit_v1.0.json")
    args = parser.parse_args(argv)
    report = build_final_audit(run_c=not args.no_c, run_cargo=args.run_cargo)
    out = ROOT / args.out if not Path(args.out).is_absolute() else Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"report": str(out), "decision": report["decision"]}, indent=2, ensure_ascii=False))
    return 0 if report["decision"].startswith("ready") else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
