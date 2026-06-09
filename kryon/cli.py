from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .core import KryonError, new
from .fileio import build_manifest, file_hexdigest, hash_stream, manifest_digest, manifest_text, verify_manifest
from .kats import iter_kat_rows
from .security import keyed_digest

CHUNK_SIZE = 1024 * 1024


def _hash_stream(stream, bits: int) -> bytes:
    return hash_stream(stream, bits, chunk_size=CHUNK_SIZE)


def _hash_file(path: Path, bits: int) -> bytes:
    with path.open("rb") as f:
        return _hash_stream(f, bits)


def _hash_text(text: str, bits: int, *, key: str | None = None, person: str | None = None) -> bytes:
    if key is not None:
        return keyed_digest(key, text, bits, personalization=person)
    h = new(out_bits=bits)
    h.update(text)
    return h.digest()


def _print_digest(d: bytes, *, bits: int, source: str, raw: bool, as_json: bool) -> None:
    if raw:
        if as_json:
            raise KryonError("--raw and --json cannot be used together")
        sys.stdout.buffer.write(d)
    elif as_json:
        print(json.dumps({"algorithm": f"Kryon-{bits}", "version": __version__, "source": source, "digest": d.hex()}, ensure_ascii=False))
    else:
        print(d.hex())


def _run_self_test() -> int:
    rows = iter_kat_rows()
    ok = all(len(row["kryon_384"]) == 96 for row in rows)
    payload = {"version": __version__, "status": "passed" if ok else "failed", "vectors": len(rows)}
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="kryon",
        description="Kryon hash CLI: files, text, stdin, manifests, keyed mode, and self-test.",
    )
    parser.add_argument("target", nargs="*", help="Text to hash, file path with --file, or file paths with --manifest")
    parser.add_argument("-b", "--bits", type=int, choices=(256, 384, 512), default=384, help="Digest size in bits")
    parser.add_argument("-f", "--file", action="store_true", help="Treat target as a single file path and stream it in chunks")
    parser.add_argument("--raw", action="store_true", help="Write raw digest bytes instead of hex")
    parser.add_argument("--json", action="store_true", help="Print JSON metadata and digest")
    parser.add_argument("--key", help="Use domain-separated keyed digest for text/stdin/file hashing")
    parser.add_argument("--person", help="Optional personalization string for keyed mode")
    parser.add_argument("--manifest", action="store_true", help="Build a manifest for target file paths")
    parser.add_argument("--manifest-digest", action="store_true", help="Append a domain-separated digest of the produced manifest")
    parser.add_argument("--check", metavar="MANIFEST", help="Verify a Kryon manifest")
    parser.add_argument("--self-test", action="store_true", help="Run embedded KAT smoke tests")
    parser.add_argument("--version", action="version", version=f"kryon {__version__}")
    args = parser.parse_args(argv)

    try:
        if args.self_test:
            return _run_self_test()

        if args.check:
            results = verify_manifest(args.check)
            failed = [r for r in results if not r.ok]
            if args.json:
                print(json.dumps({"version": __version__, "status": "passed" if not failed else "failed", "results": [r.__dict__ for r in results]}, indent=2, ensure_ascii=False))
            else:
                for r in results:
                    print(f"{'OK' if r.ok else 'FAIL'}  {r.path}" + (f"  {r.error}" if r.error else ""))
            return 0 if not failed else 1

        if args.manifest:
            if not args.target:
                parser.error("--manifest requires one or more file paths")
            entries = build_manifest(args.target, args.bits)
            text = manifest_text(entries)
            print(text, end="")
            if args.manifest_digest:
                print(f"# manifest-digest-{args.bits}: {manifest_digest(entries, args.bits)}")
            return 0

        if args.file:
            if len(args.target) != 1:
                parser.error("--file requires exactly one file path")
            path = Path(args.target[0])
            if args.key is not None:
                data = path.read_bytes()
                d = keyed_digest(args.key, data, args.bits, personalization=args.person)
            else:
                d = _hash_file(path, args.bits)
            _print_digest(d, bits=args.bits, source=str(path), raw=args.raw, as_json=args.json)
            return 0

        if not args.target:
            data = sys.stdin.buffer.read()
            d = keyed_digest(args.key, data, args.bits, personalization=args.person) if args.key is not None else new(data, args.bits).digest()
            _print_digest(d, bits=args.bits, source="stdin", raw=args.raw, as_json=args.json)
            return 0

        text = " ".join(args.target)
        d = _hash_text(text, args.bits, key=args.key, person=args.person)
        _print_digest(d, bits=args.bits, source="text", raw=args.raw, as_json=args.json)
        return 0
    except (OSError, KryonError) as exc:
        print(f"kryon: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
