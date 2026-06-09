# Contributing to Kryon

Thanks for your interest in Kryon. Contributions are welcome for documentation, tests, native parity, tooling, examples, packaging, and review work.

---

## Local setup

```bash
git clone https://github.com/tojifushigura/kryon.git
cd kryon
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

## Before opening a pull request

Run the basic release checks:

```bash
python -m pytest -q
kryon --self-test
python scripts/release_check.py --run-pytest --run-c
```

Native checks, when available:

```bash
cd native/c && make c-kat && make c-corpus
cd native/rust && cargo test --locked
```

---

## Contribution areas

| Area | Examples |
|---|---|
| Documentation | examples, diagrams, usage notes |
| Testing | KAT vectors, corpus cases, CLI tests |
| Native ports | C/Rust parity, examples, fuzz targets |
| Tooling | release checks, reports, benchmarks |
| Packaging | PyPI metadata, GitHub Releases, build scripts |
| Review | reduced-round notes, differential observations |

---

## Digest compatibility rule

Do not change canonical digest output unless the change is intentionally planned as a major release.

Changes that affect any of these require extra review:

- constants;
- padding;
- permutation;
- block absorption;
- finalization;
- output truncation.

---

## Pull request style

A good PR includes:

1. short description;
2. affected files/components;
3. tests run;
4. before/after behavior;
5. notes about digest compatibility.

Example:

```text
Summary:
- improve CLI manifest error output

Tests:
- python -m pytest -q
- kryon --self-test

Digest compatibility:
- unchanged
```
