# Kryon Native Parity

Kryon keeps the Python package as the canonical reference implementation. Native C and Rust ports are included to verify implementation consistency and support native integration work.

---

## Parity matrix

| Port | Location | Status | Main checks |
|---|---|---:|---|
| Python | `kryon/` | canonical | pytest, KAT, corpus |
| C | `native/c/` | reference | `make c-kat`, `make c-corpus` |
| Rust | `native/rust/` | reference | `cargo test`, examples, fuzz target |

---

## Python ↔ C

Run from repository root:

```bash
python scripts/c_kat.py
python scripts/c_corpus_parity.py --profile smoke
```

Or directly from the C directory:

```bash
cd native/c
make c-kat
make c-corpus
```

Expected result:

```text
C output == Python output
```

---

## Python ↔ Rust

```bash
python scripts/parity_runner.py
python scripts/parity_corpus_runner.py --profile standard
```

Direct Rust commands:

```bash
cd native/rust
cargo test --locked
cargo run --example kryon_kat --locked
```

---

## Skip behavior

Some environments do not have `cc`, `gcc`, `clang`, or `cargo` installed. In that case, parity scripts report a clean skip instead of pretending success.

| Missing tool | Status |
|---|---|
| C compiler | `skipped_c_compiler_not_found` |
| Cargo | `skipped_cargo_not_found` |
| Explicit skip flag | `skipped_by_argument` |

---

## Native metadata

| Component | Version marker |
|---|---|
| C header | `KRYON_NATIVE_VERSION` |
| Rust crate | `version = "1.0.0"` |
| Python package | `__version__ = "1.0.0"` |

---

## Release rule

A native port must not change canonical digest behavior. If native output differs from Python for the same input and output size, Python wins and the native port must be fixed.
