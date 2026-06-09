# Kryon Release Checklist

Use this checklist before tagging a Kryon release.

---

## 1. Required commands

```bash
python -m pytest -q
kryon --self-test
python scripts/release_check.py --run-pytest --run-c
python scripts/final_audit.py
```

Native optional checks:

```bash
cd native/c && make c-kat && make c-corpus
cd native/rust && cargo test --locked
```

---

## 2. Required results

| Gate | Required result |
|---|---:|
| Python tests | passed |
| KAT vectors | stable |
| CLI self-test | passed |
| Manifest roundtrip | passed |
| Streaming split equivalence | passed |
| Fuzz smoke | passed |
| Corpus diff | passed or review-needed |
| C KAT | passed when C compiler exists |
| C corpus parity | passed when C compiler exists |
| Rust KAT/corpus | passed when Cargo exists |
| Final audit | ready |

---

## 3. File tree hygiene

Before release, check that the repository does not include local artifacts:

```bash
git status --short
git clean -ndX
```

Ignored generated paths:

```text
docs/reports/
.pytest_cache/
__pycache__/
build/
dist/
*.egg-info/
native/c/kryon_kat
native/c/kryon_corpus
native/rust/target/
```

---

## 4. Version rules

| Release type | Allowed changes |
|---|---|
| Patch | bug fixes, docs, CI, packaging; canonical digest unchanged |
| Minor | new helpers/tools; canonical digest unchanged |
| Major | constants, padding, permutation, or canonical digest changes |

---

## 5. Tagging

```bash
git tag -a v1.0.0 -m "Kryon v1.0.0"
git push origin v1.0.0
```

Suggested GitHub Release title:

```text
Kryon v1.0.0 — Initial Release
```

---

## 6. Release statement

Kryon v1.0 is ready to launch as a complete custom hash software project with CLI, Python API, native reference ports, tests, and documentation.
