# Kryon Review Scope

This document defines the recommended review checklist for Kryon v1.0.

---

## 1. Core algorithm review

| Area | Review questions |
|---|---|
| Block absorption | Are message bytes injected into both rails correctly? |
| Padding | Is length/output/domain data encoded unambiguously? |
| Binary rail | Are rotations, additions, and xor operations implemented consistently? |
| Residue rail | Are modulo-257 operations handled correctly? |
| Final fold | Does finalization combine both rails as specified? |
| Output truncation | Are 256/384/512-bit outputs derived consistently? |

---

## 2. Implementation review

| Component | Review target |
|---|---|
| Python core | streaming, copy/finalize behavior, API validation |
| CLI | file paths, stdin, manifest format, exit codes |
| File I/O | chunked hashing and manifest verification |
| Security helpers | framed domain-separated/keyed payloads |
| C port | memory safety, bounds, parity with Python |
| Rust port | parity, error handling, streaming behavior |
| CI | tests, native gates, release checks |

---

## 3. Native parity review

Required checks:

```bash
python scripts/c_kat.py
python scripts/c_corpus_parity.py --profile smoke
python scripts/parity_runner.py
python scripts/parity_corpus_runner.py --profile smoke
```

Expected result:

```text
Python == C == Rust for the same vector set
```

---

## 4. Analysis review

Useful commands:

```bash
python scripts/fuzz_smoke.py --cases 256 --max-size 4096
python scripts/long_fuzz.py --cases 256 --max-size 8192
python scripts/corpus_diff_runner.py --profile smoke
python scripts/differential_clustering.py --profile smoke
python scripts/reduced_attack_automation.py --mode sweep --rounds 1,2,3 --digest-bits 16
```

---

## 5. Deliverables

A complete review can include:

1. confirmed KAT vectors;
2. Python/C/Rust parity report;
3. streaming split equivalence report;
4. reduced-round observations;
5. issue list with severity;
6. patch recommendations;
7. regression tests for discovered problems.

---

## 6. Release decision checklist

| Gate | Expected result |
|---|---:|
| Python tests | passed |
| CLI self-test | passed |
| C parity | passed or clean skip |
| Rust parity | passed or clean skip |
| release check | passed |
| final audit script | ready |
