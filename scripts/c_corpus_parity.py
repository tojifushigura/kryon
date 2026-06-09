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
from kryon.corpus import corpus_hex_lines, deterministic_corpus

C_DIR = ROOT / "native" / "c"


def build_c_corpus_report(*, profile: str = "smoke", max_cases: int | None = 64, cc: str | None = None, timeout: int = 120, run_compile: bool = True) -> dict[str, Any]:
    compiler = cc or shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
    cases = list(deterministic_corpus(profile=profile))
    if max_cases is not None:
        cases = cases[:max_cases]
    expected = [{"name": c.name, "kryon": hexdigest(c.data, 384)} for c in cases]
    report: dict[str, Any] = {
        "version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "tool": "c_corpus_parity",
        "profile": profile,
        "cases": len(cases),
        "compiler": compiler,
        "expected": expected,
        "status": "not_run",
    }
    if not run_compile:
        report["status"] = "skipped_by_argument"
        return report
    if not compiler:
        report["status"] = "skipped_c_compiler_not_found"
        return report

    exe = C_DIR / "kryon_corpus"
    compile_proc = subprocess.run(
        [compiler, "-std=c11", "-O2", "-Wall", "-Wextra", "-pedantic", "kryon_native.c", "kryon_corpus.c", "-o", str(exe)],
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

    run_proc = subprocess.run(
        [str(exe)],
        cwd=C_DIR,
        input=corpus_hex_lines(cases),
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    report["run"] = {"returncode": run_proc.returncode, "stdout_tail": run_proc.stdout[-4000:], "stderr_tail": run_proc.stderr[-4000:]}
    if run_proc.returncode != 0:
        report["status"] = "failed_run"
        return report

    actual: list[dict[str, str]] = []
    for line in run_proc.stdout.splitlines():
        name, digest_hex = line.split("\t", 1)
        actual.append({"name": name, "kryon": digest_hex.strip()})
    report["actual"] = actual
    report["status"] = "passed" if actual == expected else "failed_mismatch"
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile and run C corpus parity against Python")
    parser.add_argument("--profile", choices=("smoke", "standard", "long"), default="smoke")
    parser.add_argument("--max-cases", type=int, default=64)
    parser.add_argument("--cc")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--no-compile", action="store_true")
    parser.add_argument("--out", default="docs/reports/c_corpus_parity_v1.0.json")
    args = parser.parse_args(argv)
    report = build_c_corpus_report(profile=args.profile, max_cases=args.max_cases, cc=args.cc, timeout=args.timeout, run_compile=not args.no_compile)
    out = ROOT / args.out if not Path(args.out).is_absolute() else Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"report": str(out), "status": report["status"]}, indent=2, ensure_ascii=False))
    return 0 if report["status"] in {"passed", "skipped_c_compiler_not_found", "skipped_by_argument"} else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
