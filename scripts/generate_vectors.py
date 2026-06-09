from __future__ import annotations

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kryon import hexdigest

MESSAGES = [
    ("empty string", b""),
    ("abc", b"abc"),
    ("quick fox", b"The quick brown fox jumps over the lazy dog"),
    ("quick fox dot", b"The quick brown fox jumps over the lazy dog."),
    ("bytes 0..255", bytes(range(256))),
]


def main() -> None:
    for bits in (256, 384, 512):
        print(f"## Kryon-{bits}")
        for label, payload in MESSAGES:
            print(f"{label}: {hexdigest(payload, bits)}")
        print()


if __name__ == "__main__":
    main()
