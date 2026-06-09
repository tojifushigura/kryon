# Kryon Cryptanalysis Notes

This document maps the analysis tooling included with Kryon v1.0. The goal is to keep review work reproducible and easy to run.

---

## Tooling overview

| Tool | Purpose |
|---|---|
| `scripts/avalanche.py` | one-bit avalanche checks |
| `scripts/bit_frequency.py` | digest bit distribution checks |
| `scripts/corpus_diff_runner.py` | corpus mutation distance matrix |
| `scripts/differential_clustering.py` | grouping of differential patterns |
| `scripts/reduced_attack_automation.py` | reduced-round collision/prefix search |
| `scripts/toy_smt_model.py` | toy SAT/SMT-style enumeration |
| `scripts/long_fuzz.py` | deterministic streaming fuzz |

---

## Recommended local run

```bash
python scripts/avalanche.py
python scripts/bit_frequency.py
python scripts/corpus_diff_runner.py --profile smoke
python scripts/differential_clustering.py --profile smoke
python scripts/reduced_attack_automation.py --mode sweep --rounds 1,2,3 --digest-bits 16
```

---

## Review focus areas

| Area | Questions |
|---|---|
| Collision behavior | Are there visible structural shortcuts? |
| Preimage behavior | Does the dual-rail state leak useful relations? |
| Differential trails | Do reduced-round patterns extend as rounds increase? |
| Modulo-257 rail | Does the residue rail introduce exploitable bias? |
| Finalization | Are length/output/domain fields injected correctly? |
| Native parity | Do C/Rust ports match canonical Python output? |

---

## Reduced-round mode

Reduced-round mode is provided for experiments and reports. It is exposed through separate helper APIs and scripts so it does not mix with the canonical digest path.

Example:

```bash
python scripts/reduced_attack_automation.py --mode sweep --rounds 1,2,3,4 --digest-bits 16
```

---

## Report files

Generated reports are local artifacts. They are written to:

```text
docs/reports/
```

This path is ignored by Git.
