# Changelog

All notable changes to Kryon are documented in this file.

The project follows semantic versioning after `v1.0.0`:

- `MAJOR` — canonical digest, padding, constants, permutation, or output format changes.
- `MINOR` — new public API, CLI features, native ports, or tooling that keeps canonical digests stable.
- `PATCH` — bug fixes, documentation, tests, CI, or internal cleanup.

---

## v1.0.0 — Initial stable release

**Status:** production-ready software release.

### Added

- Stable Python package `kryon` with public API:
  - `digest()`
  - `hexdigest()`
  - `new()`
  - `KryonHash.update()`
  - `KryonHash.digest()`
  - `KryonHash.hexdigest()`
  - `KryonHash.copy()`
- CLI command `kryon` with support for:
  - text input;
  - stdin hashing;
  - file hashing;
  - JSON output;
  - self-test mode;
  - manifest generation;
  - manifest verification;
  - keyed mode;
  - personalization/domain mode.
- Domain-separated helper API in `kryon.security`.
- Keyed digest helper API in `kryon.security`.
- Constant-time digest verification helper.
- File hashing helpers in `kryon.fileio`.
- Manifest build/verify helpers in `kryon.fileio`.
- `py.typed` marker for typed Python consumers.
- C reference implementation under `native/c`.
- C KAT runner and corpus runner.
- Rust reference implementation under `native/rust`.
- Rust KAT, corpus, and benchmark examples.
- GitHub Actions CI for Python, Rust, C, and release gates.
- Release tooling:
  - `scripts/release_check.py`
  - `scripts/final_audit.py`
  - `scripts/c_kat.py`
  - `scripts/c_corpus_parity.py`
  - `scripts/parity_runner.py`
  - `scripts/parity_corpus_runner.py`
- Final documentation set:
  - `README.md`
  - `docs/SPEC.md`
  - `docs/LAUNCH.md`
  - `docs/ROADMAP.md`
  - `docs/SECURITY.md`
  - `docs/FUZZING.md`
  - `docs/NATIVE_PARITY.md`
  - `docs/CRYPTOANALYSIS.md`
  - `docs/AUDIT_SCOPE.md`
  - `docs/RELEASE_CHECKLIST.md`
  - `CONTRIBUTING.md`

### Changed

- Project renamed and finalized as **Kryon**.
- Python package renamed from the internal CrossWeave-era naming to `kryon`.
- CLI command standardized as `kryon`.
- Native C metadata updated to `kryon-native-c-1.0.0`.
- Native Rust crate metadata updated to `1.0.0`.
- README and documentation redesigned for public release.
- Repository cleanup performed for release tree.
- Generated report files removed from the tracked release tree.
- `.gitignore` added for local caches, build outputs, virtualenvs, and generated reports.

### Compatibility

- Canonical digest vectors remain compatible with the stable v0.2+ streaming core line.
- v1.0.0 is the first stable public API point for Kryon.

---

## v0.9.0 — Release candidate cleanup

**Status:** release candidate stage before v1.0.0.

### Added

- Release-candidate documentation pass.
- Repository metadata preparation for GitHub publication.
- Public project naming cleanup around Kryon.
- Final release checklist structure.
- Native metadata checks for C and Rust.
- Production-oriented README structure.

### Changed

- Removed internal technical-assignment documents from the release tree.
- Removed generated historical reports from the release tree.
- Removed or emptied legacy versioned test files that were no longer needed for v1.0.
- Cleaned old wording from docs and README.
- Updated C/Rust README files to v1.0-oriented wording.
- Updated native C make targets to:
  - `make c-kat`
  - `make c-corpus`

### Compatibility

- No canonical digest changes.
- No CLI-breaking changes intended after this release-candidate stage.

---

## v0.8.0 — Native C port and attack automation

**Status:** advanced analysis and native C milestone.

### Added

- `kryon.attacks` module with:
  - reduced collision search;
  - prefix-preimage search;
  - reduced attack sweep;
  - differential clustering.
- `kryon.toy_model` module with dependency-free SAT/SMT-style brute-force backend.
- Reduced-round attack automation script.
- Toy SMT-style model script.
- Differential clustering script.
- Real dependency-free C reference port.
- Native C KAT smoke test.
- `scripts/c_kat.py`.
- C release-check gate.

### Changed

- Replaced C scaffold with implemented C reference code.
- Extended release checks with reduced attack, toy model, clustering, and C gates.

### Compatibility

- Canonical digest stayed compatible with the v0.2+ line.

---

## v0.7.0 — Deterministic corpus and long fuzzing

**Status:** corpus and fuzzing milestone.

### Added

- `kryon.corpus` module.
- Deterministic corpus profiles:
  - `smoke`
  - `standard`
  - `long`
- Mutation generation for differential corpus checks.
- Deterministic chunk plans for streaming tests.
- Long streaming fuzz script.
- Corpus differential runner.
- Python/Rust corpus parity runner.
- Rust example `kryon_corpus`.

### Changed

- Extended release-check with long fuzz and corpus differential gates.

### Compatibility

- Canonical digest stayed compatible with the v0.2+ line.

---

## v0.6.0 — CI and release gates

**Status:** infrastructure milestone.

### Added

- GitHub Actions CI layout.
- Release readiness checker.
- Python/Rust parity runner.
- Rust benchmark helper.
- Common KAT vector module.
- Makefile for common project commands.
- Fuzzing documentation.
- Native parity documentation.
- Release checklist documentation.

### Compatibility

- Canonical digest stayed compatible with the v0.2+ line.

---

## v0.5.0 — Rust reference port

**Status:** native Rust milestone.

### Added

- Rust reference implementation under `native/rust`.
- Rust API:
  - `Context`
  - `update()`
  - `finalize()`
  - `digest()`
  - `hexdigest()`
- Rust KAT example.
- Rust fuzz target layout.
- Python/Rust KAT parity report tooling.

### Compatibility

- Canonical Python digest stayed compatible with v0.2+.

---

## v0.4.0 — Analysis tooling and native scaffolds

**Status:** analysis milestone.

### Added

- Bit-frequency analyzer.
- Structured corpus generator.
- Differential trail explorer.
- `scripts/bit_frequency.py`.
- `scripts/corpus_matrix.py`.
- `scripts/differential_trail.py`.
- Initial native scaffolds for C and Rust.

### Compatibility

- Canonical digest stayed compatible with v0.2+.

---

## v0.3.0 — Reduced-round research API

**Status:** research tooling milestone.

### Added

- `RoundProfile` for reduced-round experiments.
- Reduced-round API:
  - `make_profile()`
  - `new_reduced()`
  - `digest_reduced()`
  - `hexdigest_reduced()`
- `kryon.analysis` module.
- Reduced sweep script.
- Toy collision search script.
- Vector generation script.
- Avalanche analysis script updates.

### Compatibility

- Canonical digest stayed compatible with v0.2.

---

## v0.2.0 — Streaming core

**Status:** canonical streaming core milestone.

### Added

- Real streaming block processor.
- Streaming `update()` implementation.
- Copy-on-finalize behavior for `digest()` and `hexdigest()`.
- Streaming file hashing through CLI.
- JSON CLI output mode.
- Version CLI output.
- Streaming equivalence tests.

### Changed

- Large files no longer need to be loaded fully into memory.

---

## v0.1.0 — Initial algorithm and project skeleton

**Status:** first working implementation.

### Added

- Initial Kryon/CrossWeave-era hash core.
- Python package skeleton.
- CLI skeleton.
- Basic test vectors.
- Determinism tests.
- Digest-size tests.
- Basic avalanche smoke test.
- Initial technical documentation.
