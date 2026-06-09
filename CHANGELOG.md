# Changelog

## v0.8.0

- Added `kryon.attacks` with reduced collision, prefix-preimage, sweep and clustering reports.
- Added `kryon.toy_model` with a dependency-free SAT/SMT-style brute-force backend.
- Added `scripts/reduced_attack_automation.py`.
- Added `scripts/toy_smt_model.py`.
- Added `scripts/differential_clustering.py`.
- Replaced the C scaffold with a real dependency-free C reference port.
- Added `scripts/c_kat.py` and native C KAT smoke test.
- Extended release-check with reduced attack, toy model, clustering and C gates.
- Kept canonical digest compatible with v0.2+.

## v0.7.0

- Added `kryon.corpus` with deterministic corpus profiles.
- Added mutation generation for differential corpus checks.
- Added deterministic chunk plans for streaming tests.
- Added `scripts/corpus_diff_runner.py`.
- Added `scripts/long_fuzz.py`.
- Added `scripts/parity_corpus_runner.py`.
- Added Rust example `kryon_corpus` for externally supplied corpus parity.
- Extended release-check with long fuzz and corpus differential gates.
- Kept canonical digest compatible with v0.2+.

## v0.6.0

- Added CI, release-check, KAT generation and Python/Rust parity scaffolding.

## v0.5.0

- Added Rust reference port.

## v0.4.0

- Added bit-frequency, structured corpus and differential trail tools.

## v0.3.0

- Added reduced-round research API and toy collision tooling.

## v0.2.0

- Added real streaming core.

## v1.0.0 - launch-ready software release

- Promoted the project from iterative research toolkit to runnable v1 software project.
- Added domain-separated and keyed helper APIs in `kryon.security`.
- Added constant-time hex verification helper.
- Added file hashing and manifest build/verify helpers in `kryon.fileio`.
- Extended CLI with `--self-test`, `--manifest`, `--check`, `--key`, and `--person`.
- Added `py.typed` and package data metadata.
- Added C corpus parity runner and `native/c/kryon_corpus.c`.
- Added final launch audit script: `scripts/final_audit.py`.
- Added v1.0 specification, launch guide, and audit scope.
- Kept canonical digest compatible with v0.2-v0.8 vectors.
