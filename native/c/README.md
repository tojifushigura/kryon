# Kryon native C reference port v1.0

This directory contains a dependency-free C reference port of the canonical Kryon core. The Python implementation remains the reference implementation, and the C port exists for parity checks, fuzz harnesses, and native integration work.

## Status in v1.0

| Area | Status |
|---|---:|
| Canonical 256/384/512-bit digest | Implemented |
| Streaming update/final API | Implemented |
| KAT runner | Implemented |
| Corpus runner | Implemented |
| Native version API | Implemented |

## Build

```bash
cd native/c
make c-kat
make c-corpus
```

Project-level helpers:

```bash
python scripts/c_kat.py
python scripts/c_corpus_parity.py --profile smoke
```
