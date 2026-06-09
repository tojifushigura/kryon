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
from scripts.parity_runner import build_parity_report
from scripts.fuzz_smoke import run_fuzz_smoke
from scripts.long_fuzz import run_long_fuzz
from scripts.corpus_diff_runner import build_corpus_diff_report
from scripts.parity_corpus_runner import build_parity_corpus_report
from scripts.c_corpus_parity import build_c_corpus_report
from kryon.attacks import reduced_attack_sweep, differential_clustering_report
from kryon.toy_model import build_toy_model_report
from scripts.c_kat import build_c_kat_report


def _run_python_tests(*, timeout: int = 120) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, text=True, capture_output=True, timeout=timeout, check=False)
    return {"status": "passed" if proc.returncode == 0 else "failed", "returncode": proc.returncode, "stdout_tail": proc.stdout[-4000:], "stderr_tail": proc.stderr[-4000:]}


def _check_required_files() -> dict[str, Any]:
    required = [
        "README.md",
        "CHANGELOG.md",
        "LICENSE",
        "pyproject.toml",
        "kryon/py.typed",
        "docs/SPEC.md",
        "docs/LAUNCH.md",
        "docs/AUDIT_SCOPE.md",
        "docs/RELEASE_CHECKLIST.md",
        "native/c/kryon_native.c",
        "native/c/kryon_corpus.c",
        "native/rust/src/lib.rs",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    return {"status": "passed" if not missing else "failed", "missing": missing, "required_count": len(required)}


def build_release_report(*, run_pytest: bool = False, run_cargo: bool = False, run_c: bool = False, profile: str = "smoke") -> dict[str, Any]:
    report: dict[str, Any] = {
        "version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "profile": profile,
        "checks": {},
    }
    checks = report["checks"]
    checks["required_files"] = _check_required_files()
    checks["fuzz_smoke_small"] = run_fuzz_smoke(cases=8, max_size=256, seed=20260608)
    checks["long_fuzz_small"] = run_long_fuzz(cases=4, max_size=256, seed=20260608, include_corpus=True)
    checks["corpus_diff"] = build_corpus_diff_report(profile=profile, max_cases=24)
    checks["parity_rust_kat"] = build_parity_report(run_cargo=run_cargo)
    checks["parity"] = checks["parity_rust_kat"]  # backward-compatible report key
    checks["parity_rust_corpus"] = build_parity_corpus_report(profile=profile, max_cases=24, run_cargo=run_cargo)
    checks["c_kat"] = build_c_kat_report(run_compile=run_c)
    checks["c_corpus_parity"] = build_c_corpus_report(profile=profile, max_cases=24, run_compile=run_c)
    checks["reduced_attack_sweep"] = reduced_attack_sweep(rounds=(1, 2, 3), digest_bits=8, attempts=2048, seed=20260608)
    checks["toy_smt_model"] = build_toy_model_report(variable_bits=9, digest_bits=8, rounds=1)
    checks["differential_clustering"] = differential_clustering_report(profile=profile, max_cases=24, max_mutations=3)
    checks["pytest"] = _run_python_tests() if run_pytest else {"status": "skipped_by_argument"}

    hard_statuses = [
        checks["required_files"]["status"],
        checks["fuzz_smoke_small"]["status"],
        checks["long_fuzz_small"]["status"],
        checks["corpus_diff"]["status"],
        checks["reduced_attack_sweep"]["status"],
        checks["toy_smt_model"]["status"],
        checks["differential_clustering"]["status"],
    ]
    if run_pytest:
        hard_statuses.append(checks["pytest"]["status"])
    c_ok = checks["c_kat"]["status"] in {"passed", "skipped_c_compiler_not_found", "skipped_by_argument"}
    c_corpus_ok = checks["c_corpus_parity"]["status"] in {"passed", "skipped_c_compiler_not_found", "skipped_by_argument"}
    rust_ok = checks["parity_rust_kat"]["rust"]["status"] in {"passed", "skipped_cargo_not_found", "skipped_by_argument"}
    rust_corpus_ok = checks["parity_rust_corpus"]["rust"]["status"] in {"passed", "skipped_cargo_not_found", "skipped_by_argument"}
    acceptable = {"passed", "review_needed"}
    report["status"] = "passed" if all(status in acceptable for status in hard_statuses) and c_ok and c_corpus_ok and rust_ok and rust_corpus_ok else "failed"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Kryon release readiness report")
    parser.add_argument("--run-pytest", action="store_true")
    parser.add_argument("--run-cargo", action="store_true")
    parser.add_argument("--run-c", action="store_true")
    parser.add_argument("--profile", choices=("smoke", "standard", "long"), default="smoke")
    parser.add_argument("--out", default="docs/reports/release_check_v1.0.json")
    args = parser.parse_args()

    report = build_release_report(run_pytest=args.run_pytest, run_cargo=args.run_cargo, run_c=args.run_c, profile=args.profile)
    out = ROOT / args.out if not Path(args.out).is_absolute() else Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"report": str(out), "status": report["status"]}, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
