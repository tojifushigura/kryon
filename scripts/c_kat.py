from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kryon import __version__, hexdigest

C_DIR = ROOT / "native" / "c"


def _expected_rows() -> list[dict[str, str]]:
    messages = ["", "abc", "The quick brown fox jumps over the lazy dog"]
    return [{"message": msg, "kryon": hexdigest(msg.encode(), 384)} for msg in messages]


def build_c_kat_report(*, cc: str | None = None, timeout: int = 120, run_compile: bool = True) -> dict[str, Any]:
    compiler = cc or shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
    report: dict[str, Any] = {
        "version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "tool": "c_kat",
        "compiler": compiler,
        "expected": _expected_rows(),
        "status": "not_run",
    }
    if not run_compile:
        report["status"] = "skipped_by_argument"
        return report
    if not compiler:
        report["status"] = "skipped_c_compiler_not_found"
        return report

    exe = C_DIR / "kryon_kat"
    compile_proc = subprocess.run(
        [compiler, "-std=c11", "-O2", "-Wall", "-Wextra", "-pedantic", "kryon_native.c", "kryon_kat.c", "-o", str(exe)],
        cwd=C_DIR,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    report["compile"] = {"returncode": compile_proc.returncode, "stdout": compile_proc.stdout[-4000:], "stderr": compile_proc.stderr[-4000:]}
    if compile_proc.returncode != 0:
        report["status"] = "failed_compile"
        return report

    run_proc = subprocess.run([str(exe)], cwd=C_DIR, text=True, capture_output=True, timeout=timeout, check=False)
    report["run"] = {"returncode": run_proc.returncode, "stdout": run_proc.stdout, "stderr": run_proc.stderr[-4000:]}
    if run_proc.returncode != 0:
        report["status"] = "failed_run"
        return report

    actual: list[dict[str, str]] = []
    for line in run_proc.stdout.splitlines():
        msg, digest = line.split("\t", 1)
        actual.append({"message": msg, "kryon": digest.strip()})
    report["actual"] = actual
    report["status"] = "passed" if actual == report["expected"] else "failed_mismatch"
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile and run the Kryon native C KAT smoke test")
    parser.add_argument("--cc")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--no-compile", action="store_true")
    parser.add_argument("--out", default="docs/reports/c_kat_v1.0.json")
    args = parser.parse_args(argv)

    report = build_c_kat_report(cc=args.cc, timeout=args.timeout, run_compile=not args.no_compile)
    out = ROOT / args.out if not Path(args.out).is_absolute() else Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"report": str(out), "status": report["status"]}, indent=2, ensure_ascii=False))
    return 0 if report["status"] in {"passed", "skipped_c_compiler_not_found", "skipped_by_argument"} else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
