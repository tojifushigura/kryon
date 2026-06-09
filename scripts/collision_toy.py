from __future__ import annotations

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kryon.reduced import digest_reduced, make_profile


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Toy collision search for truncated reduced Kryon outputs.")
    parser.add_argument("--digest-bits", type=int, default=16, help="Truncated digest size. Keep tiny for the toy demo.")
    parser.add_argument("--rounds", type=int, default=2, help="Reduced absorb rounds.")
    parser.add_argument("--max-attempts", type=int, default=200000)
    parser.add_argument("--seed", type=int, default=20260608)
    parser.add_argument("--prefix", default="cw-toy:")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    profile = make_profile(absorb_rounds=args.rounds)
    rng = random.Random(args.seed)
    seen: dict[bytes, bytes] = {}

    for attempt in range(1, args.max_attempts + 1):
        payload = f"{args.prefix}{attempt}:".encode() + rng.randbytes(16)
        d = digest_reduced(payload, out_bits=384, digest_bits=args.digest_bits, profile=profile)
        old = seen.get(d)
        if old is not None and old != payload:
            result = {
                "found": True,
                "attempts": attempt,
                "digest_bits": args.digest_bits,
                "rounds": args.rounds,
                "digest": d.hex(),
                "message_a_hex": old.hex(),
                "message_b_hex": payload.hex(),
            }
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print("toy collision found")
                for k, v in result.items():
                    print(f"{k}: {v}")
            return 0
        seen[d] = payload

    result = {"found": False, "attempts": args.max_attempts, "digest_bits": args.digest_bits, "rounds": args.rounds}
    print(json.dumps(result, indent=2) if args.json else result)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
