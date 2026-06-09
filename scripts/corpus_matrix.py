from __future__ import annotations

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import json

from kryon.analysis import corpus_digest_matrix, structured_corpus


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a deterministic Kryon structured corpus digest matrix")
    parser.add_argument("--bits", type=int, choices=(256, 384, 512), default=384)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--no-random", action="store_true", help="Exclude deterministic random cases from the corpus")
    args = parser.parse_args()

    corpus = structured_corpus(include_random=not args.no_random)
    rows = corpus_digest_matrix(corpus, out_bits=args.bits, limit=args.limit)
    print(json.dumps({"algorithm": f"Kryon-{args.bits}", "cases": rows}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
