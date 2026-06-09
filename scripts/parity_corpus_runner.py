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
from typing import Any

from kryon import __version__
from kryon.corpus import corpus_vectors, deterministic_corpus, corpus_hex_lines

RUST_DIR = ROOT / "native" / "rust"


def _run(cmd: list[str], *, cwd: Path, input_text: str | None = None, timeout: int = 120) -> dict[str, Any]:
    try:
        proc = subprocess.run(cmd, cwd=cwd, input=input_text, text=True, capture_output=True, timeout=timeout, check=False)
        return {
            "cmd": cmd,
            "returncode": proc.returncode,
            "stdout_tail": proc.stdout[-4000:],
            "stderr_tail": proc.stderr[-4000:],
        }
    except Exception as exc:  # pragma: no cover
        return {"cmd": cmd, "returncode": None, "error": repr(exc)}


def build_parity_corpus_report(*, profile: str = "standard", digest_bits: int = 384, max_cases: int | None = None, run_cargo: bool = True, timeout: int = 120) -> dict[str, Any]:
    cases = list(deterministic_corpus(profile=profile))
    if max_cases is not None:
        cases = cases[:max_cases]
    vectors = corpus_vectors(cases, digest_bits=digest_bits)

    cargo_path = shutil.which("cargo")
    report: dict[str, Any] = {
        "version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "profile": profile,
        "digest_bits": digest_bits,
        "case_count": len(cases),
        "python_vectors": vectors,
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

    # Rust example receives Python-selected corpus as TSV and prints JSON vectors.
    cmd = [cargo_path, "run", "--example", "kryon_corpus", "--locked", "--", "--digest-bits", str(digest_bits)]
    corpus_input = "".join(f"{case.name}\t{case.category}\t{case.data.hex()}\n" for case in cases)
    check = _run(cmd, cwd=RUST_DIR, input_text=corpus_input, timeout=timeout)
    rust["checks"] = [check]
    if check.get("returncode") != 0:
        rust["status"] = "failed"
        return report

    try:
        rust_vectors = json.loads(check.get("stdout_tail", "[]"))
        rust["vector_count"] = len(rust_vectors)
        rust["status"] = "passed" if rust_vectors == vectors else "mismatch"
    except Exception as exc:
        rust["status"] = "parse_failed"
        rust["parse_error"] = repr(exc)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Kryon v0.8 corpus parity checks")
    parser.add_argument("--profile", choices=["smoke", "standard", "long"], default="standard")
    parser.add_argument("--digest-bits", type=int, default=384)
    parser.add_argument("--max-cases", type=int)
    parser.add_argument("--no-cargo", action="store_true")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--out", default="docs/reports/parity_corpus_v0.8.json")
    args = parser.parse_args(argv)

    report = build_parity_corpus_report(profile=args.profile, digest_bits=args.digest_bits, max_cases=args.max_cases, run_cargo=not args.no_cargo, timeout=args.timeout)
    out = ROOT / args.out if not Path(args.out).is_absolute() else Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"report": str(out), "rust_status": report["rust"]["status"], "case_count": report["case_count"]}, indent=2, ensure_ascii=False))
    return 0 if report["rust"]["status"] in {"passed", "skipped_cargo_not_found", "skipped_by_argument"} else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
