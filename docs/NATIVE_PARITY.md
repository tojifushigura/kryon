# Native parity

Kryon keeps Python as the reference implementation. Native ports are used for implementation checks, profiling, and fuzzing.

| Port | Status in v1.0 | Check |
|---|---:|---|
| Rust | Implemented | `cargo test`, `scripts/parity_runner.py`, `scripts/parity_corpus_runner.py` |
| C | Implemented | `scripts/c_kat.py`, `scripts/c_corpus_parity.py` |

## Python/Rust

```bash
python scripts/parity_runner.py
python scripts/parity_corpus_runner.py --profile standard
```

When `cargo` is unavailable, the scripts report `skipped_cargo_not_found` or `skipped_by_argument` instead of pretending success.

## Python/C

```bash
python scripts/c_kat.py
python scripts/c_corpus_parity.py --profile smoke
```

When a C compiler is unavailable, the script reports `skipped_c_compiler_not_found`. When a compiler exists, it builds the native C runners and compares output with Python Kryon KAT/corpus values.
