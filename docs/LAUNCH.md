# Kryon v1.0 Launch Guide

## Local launch

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e . pytest
python -m pytest -q
kryon --self-test
```

## File integrity workflow

```bash
kryon --manifest ./file1.bin ./file2.bin > kryon.manifest
kryon --check kryon.manifest
```

## Internal keyed workflow

```bash
kryon --key "$KRYON_KEY" --person "project-name" --file ./artifact.zip
```

Store keys outside source code, for example in environment variables or a secret manager.

## Release workflow

```bash
python scripts/final_audit.py
python scripts/release_check.py --run-pytest --run-c
```

A launch is acceptable when:

| Gate | Required result |
|---|---|
| pytest | passed |
| self-test | passed |
| release_check | passed |
| C KAT | passed or compiler unavailable in environment |
| C corpus parity | passed or compiler unavailable in environment |
| Rust parity | passed in CI with Cargo |
| final_audit decision | `ready_to_launch_as_v1_software_project` |

## What can be launched now

- CLI utility for file checksums.
- Python package for deterministic hashing workflows.
- C/Rust reference implementations for parity review.
- GitHub repository for public use, testing, review, and development.
