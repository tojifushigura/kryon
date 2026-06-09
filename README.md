<p align="center">
  <br>
  <strong style="font-size: 32px;">Kryon</strong>
</p>

<p align="center">
  <b>Irreversible streaming hash toolkit for files, manifests, keyed digests, and native parity.</b>
</p>

<p align="center">
  <a href="https://github.com/tojifushigura/kryon/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/tojifushigura/kryon/actions/workflows/ci.yml/badge.svg"></a>
  <img alt="Python" src="https://img.shields.io/badge/python-3.10%2B-blue">
  <img alt="Rust" src="https://img.shields.io/badge/rust-reference-orange">
  <img alt="C" src="https://img.shields.io/badge/C-reference-lightgrey">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green">
</p>

---

## What is Kryon?

**Kryon** is a complete custom hash project built around a streaming one-way digest design. It includes a Python package, CLI utility, file manifest workflow, keyed/domain-separated helpers, deterministic test vectors, corpus tooling, C reference port, Rust reference port, and CI-ready release checks.

Kryon is designed for modern integrity workflows where old MD5-style checksums feel too small and outdated. Hashes are not decoded back; they are verified by recomputing the digest and comparing the result.

---

## Highlights

| Feature | Status |
|---|---:|
| Python library API | ✅ Ready |
| CLI for text, stdin, and files | ✅ Ready |
| Streaming large file hashing | ✅ Ready |
| Manifest build and verify | ✅ Ready |
| Keyed digest helpers | ✅ Ready |
| Domain/person separation | ✅ Ready |
| 256 / 384 / 512-bit output | ✅ Ready |
| C reference port | ✅ Ready |
| Rust reference port | ✅ Ready |
| Deterministic corpus | ✅ Ready |
| Native parity checks | ✅ Ready |
| Fuzzing and analysis tooling | ✅ Ready |
| GitHub Actions CI | ✅ Ready |

---

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e . pytest
python -m pytest -q
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e . pytest
python -m pytest -q
```

---

## CLI usage

Hash a string:

```bash
kryon "abc"
```

JSON output:

```bash
kryon --json "abc"
```

Hash a file:

```bash
kryon --file ./artifact.zip
```

Read from stdin:

```bash
echo "hello" | kryon
```

Create and verify a manifest:

```bash
kryon --manifest ./a.bin ./b.bin > kryon.manifest
kryon --check kryon.manifest
```

Keyed/domain-separated mode:

```bash
kryon --key "secret" --person "my-app" "abc"
```

Built-in self-test:

```bash
kryon --self-test
```

---

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

File hashing:

```python
from kryon import file_hexdigest

print(file_hexdigest("./artifact.zip", 384))
```

Keyed digest:

```python
from kryon import keyed_hexdigest

print(keyed_hexdigest("secret", b"payload", 384, personalization="app-v1"))
```

---

## Native reference ports

C reference port:

```bash
cd native/c
make c-kat
make c-corpus
```

Rust reference port:

```bash
cd native/rust
cargo test --locked
cargo run --example kryon_kat --locked
```

---

## Project layout

| Path | Purpose |
|---|---|
| `kryon/core.py` | canonical streaming hash core |
| `kryon/security.py` | keyed/domain-separated helpers |
| `kryon/fileio.py` | file hashing and manifests |
| `kryon/corpus.py` | deterministic corpus and mutations |
| `kryon/analysis.py` | avalanche, bit-frequency, differential tools |
| `kryon/attacks.py` | reduced-round analysis automation |
| `native/c/` | dependency-free C reference port |
| `native/rust/` | Rust reference port and fuzz target layout |
| `scripts/` | parity, fuzzing, reports, release checks |
| `docs/` | specification, launch, review, and native notes |
| `.github/workflows/` | CI workflow |

---

## Documentation

| Document | Description |
|---|---|
| [`docs/SPEC.md`](docs/SPEC.md) | algorithm structure and parameters |
| [`docs/LAUNCH.md`](docs/LAUNCH.md) | local launch and release workflow |
| [`docs/NATIVE_PARITY.md`](docs/NATIVE_PARITY.md) | Python/C/Rust parity checks |
| [`docs/FUZZING.md`](docs/FUZZING.md) | fuzzing and reduced-round automation |
| [`docs/CRYPTOANALYSIS.md`](docs/CRYPTOANALYSIS.md) | analysis tooling overview |
| [`docs/AUDIT_SCOPE.md`](docs/AUDIT_SCOPE.md) | review checklist |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | completed work and optional future items |
| [`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md) | release gates |

---

## Release checks

```bash
python scripts/release_check.py --run-pytest --run-c
python scripts/final_audit.py
```

Generated reports are written to `docs/reports/`. This directory is ignored by Git so local reports do not pollute the release tree.

---

## Design summary

Kryon uses a dual-rail state:

- a binary 12 × 64-bit lane state;
- a residue rail modulo 257;
- continuous cross-injection between the two rails;
- streaming block absorption;
- domain-separated finalization;
- selectable output sizes: 256, 384, and 512 bits.

The implementation is intentionally transparent: constants, test vectors, native ports, corpus generators, and analysis tools are all included in the repository.

---

## License

MIT License. See [`LICENSE`](LICENSE).
