from __future__ import annotations

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import json
from pathlib import Path

from kryon import __version__
from kryon.kats import build_kat_document


def build_vectors() -> dict[str, object]:
    return build_kat_document(version=__version__, note="Expected Python/Rust canonical parity vectors")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate canonical Kryon KAT vectors for native parity checks")
    parser.add_argument("--out", default="docs/reports/native_kat_v0.8.json")
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build_vectors(), indent=2, ensure_ascii=False), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
