# Kryon Launch Guide

This guide describes how to run Kryon locally, verify the release, and use the project as a CLI/library.

---

## 1. Clone and install

```bash
git clone https://github.com/tojifushigura/kryon.git
cd kryon
python -m venv .venv
. .venv/bin/activate
pip install -e . pytest
```

Windows PowerShell:

```powershell
git clone https://github.com/tojifushigura/kryon.git
cd kryon
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e . pytest
```

---

## 2. Run tests

```bash
python -m pytest -q
kryon --self-test
```

Expected result:

```text
all tests passed
self-test status: passed
```

---

## 3. CLI workflows

### Hash a string

```bash
kryon "abc"
```

### Hash a file

```bash
kryon --file ./artifact.zip
```

### Create a manifest

```bash
kryon --manifest ./a.bin ./b.bin > kryon.manifest
```

### Verify a manifest

```bash
kryon --check kryon.manifest
```

### Use keyed mode

```bash
kryon --key "$KRYON_KEY" --person "project-name" --file ./artifact.zip
```

---

## 4. Native checks

### C

```bash
cd native/c
make c-kat
make c-corpus
```

### Rust

```bash
cd native/rust
cargo test --locked
cargo run --example kryon_kat --locked
```

---

## 5. Release verification

From the repository root:

```bash
python scripts/release_check.py --run-pytest --run-c
python scripts/final_audit.py
```

Release gates:

| Gate | Expected result |
|---|---:|
| Python tests | passed |
| CLI self-test | passed |
| C KAT | passed when a C compiler exists |
| C corpus parity | passed when a C compiler exists |
| Rust tests | passed when Cargo exists |
| release check | passed |
| final audit | ready |

Generated files are written to `docs/reports/` and ignored by Git.

---

## 6. Recommended repository settings

| Setting | Recommended value |
|---|---|
| Default branch | `main` |
| Actions | enabled |
| Branch protection | optional after first release |
| Releases | use GitHub Releases for tagged versions |
| Topics | `hash`, `cryptography`, `checksum`, `integrity`, `streaming` |

Suggested repository description:

```text
Kryon is an irreversible streaming hash toolkit with CLI, manifests, keyed digests, and C/Rust reference ports.
```
