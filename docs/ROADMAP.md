# Kryon Roadmap

Kryon v1.0 is the first complete public release of the project. The core library, CLI, native reference ports, tests, and release workflow are implemented.

---

## Completed in v1.0

| Area | Result |
|---|---:|
| Streaming Python core | ✅ Done |
| Hashlib-like API | ✅ Done |
| 256 / 384 / 512-bit outputs | ✅ Done |
| Stable KAT vectors | ✅ Done |
| CLI utility | ✅ Done |
| File hashing | ✅ Done |
| Manifest build/verify | ✅ Done |
| Keyed digest helpers | ✅ Done |
| Domain/person separation | ✅ Done |
| Deterministic corpus | ✅ Done |
| Analysis toolkit | ✅ Done |
| Reduced-round tooling | ✅ Done |
| C reference port | ✅ Done |
| Rust reference port | ✅ Done |
| Python/C parity checks | ✅ Done |
| Python/Rust parity checks | ✅ Done |
| GitHub Actions CI | ✅ Done |
| Release checklist | ✅ Done |
| Specification docs | ✅ Done |

---

## Optional future work

These items are not blockers for v1.0. They are useful improvements for contributors and future releases.

| Priority | Item | Notes |
|---:|---|---|
| P1 | PyPI packaging | publish `kryon` after metadata review |
| P1 | GitHub Release assets | attach source archive and generated checksums |
| P2 | More examples | add real manifest workflows and integration snippets |
| P2 | Rust performance tuning | benchmark and optimize after parity stability |
| P2 | C API examples | add small standalone examples for embedding |
| P3 | More language ports | Go, TypeScript, PHP wrappers |
| P3 | Extended fuzz campaigns | longer CI/manual fuzz runs |

---

## Version policy

| Release type | Meaning |
|---|---|
| Patch | bug fixes that keep canonical digest unchanged |
| Minor | new tooling or helpers that keep canonical digest unchanged |
| Major | any change to constants, padding, permutation, or canonical digest |

---

## Release state

Kryon v1.0 is ready as a complete software release. Future changes should be handled through issues, pull requests, and tagged releases.
