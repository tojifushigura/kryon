# Kryon v1.0 Cryptanalysis Notes

## Internal analysis coverage

| Tool | Purpose |
|---|---|
| `scripts/avalanche.py` | one-bit avalanche smoke checks |
| `scripts/bit_frequency.py` | digest bit distribution checks |
| `scripts/corpus_diff_runner.py` | mutation/corpus differential matrix |
| `scripts/differential_clustering.py` | grouping of differential patterns |
| `scripts/reduced_attack_automation.py` | reduced-round collision/preimage search |
| `scripts/toy_smt_model.py` | brute-force SAT/SMT-style toy model |
| `scripts/long_fuzz.py` | deterministic streaming fuzz |

## Review focus

Reviewers can focus on:

1. collision shortcuts from the dual-rail state;
2. algebraic relations introduced by modulo 257;
3. whether the binary/residue lifts create exploitable linear biases;
4. finalization/padding domain separation;
5. reduced-round distinguishers that scale toward canonical rounds.
