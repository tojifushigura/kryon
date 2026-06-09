# Kryon v1.0

**Kryon is a next-generation irreversible hashing toolkit for streaming integrity checks, manifests, keyed digests, native parity, and public review.**

Kryon is a complete runnable hash project: Python package, CLI, test vectors, deterministic corpus, C reference port, Rust reference port, fuzz/analyse scripts, CI layout, and release-readiness tooling.

The goal is to replace MD5-style legacy checksums in controlled tools with a larger, streaming, one-way digest design. Hashes are not decoded back; they are verified by recomputing and comparing the digest.

## Current launch status

| Area | Status |
|---|---:|
| Python library API | ready |
| CLI for text/file/stdin | ready |
| Manifest build/verify | ready |
| Streaming large files | ready |
| KAT vectors | ready |
| Deterministic corpus | ready |
| C reference port | ready |
| Rust reference port | ready, CI expected to run where Cargo exists |
| Reduced-round analysis tooling | ready |
| Release workflow | ready |

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e . pytest
python -m pytest -q
```

## CLI

```bash
kryon "abc"
kryon --json "abc"
kryon --file ./some-file.bin
kryon --manifest ./a.bin ./b.bin > kryon.manifest
kryon --check kryon.manifest
kryon --self-test
```

Keyed domain-separated mode:

```bash
kryon --key "secret" --person "my-app" "abc"
```

## Python API

```python
from kryon import hexdigest, new, file_hexdigest, verify_hexdigest

print(hexdigest(b"abc", 384))

h = new(out_bits=384)
h.update(b"a")
h.update(b"bc")
print(h.hexdigest())

expected = hexdigest(b"abc", 384)
print(verify_hexdigest(expected, b"abc", 384))
```

## Native checks

```bash
cd native/c
make c-kat
make c-corpus
```

```bash
cd native/rust
cargo test --locked
cargo run --example kryon_kat --locked
cargo run --example kryon_corpus --locked < ../../docs/reports/corpus_input.txt
```

## Release checks

```bash
python scripts/release_check.py --run-pytest --run-c
python scripts/final_audit.py
```

Generated reports are stored in `docs/reports/`.

## Project map

| Path | Purpose |
|---|---|
| `kryon/core.py` | canonical streaming hash |
| `kryon/security.py` | domain-separated/keyed helpers and constant-time verify |
| `kryon/fileio.py` | file hashing and manifests |
| `kryon/corpus.py` | deterministic corpus and mutations |
| `kryon/attacks.py` | reduced-round analysis automation |
| `native/c/` | dependency-free C reference implementation |
| `native/rust/` | Rust reference implementation |
| `scripts/` | reports, fuzzing, parity, release checks |
| `docs/SPEC.md` | algorithm specification |
| `docs/LAUNCH.md` | launch guide |
| `docs/AUDIT_SCOPE.md` | review checklist |
