# Kryon Fuzzing & Analysis

Kryon includes deterministic fuzzing, corpus mutation checks, reduced-round automation, and native parity runners.

---

## 1. Python deterministic fuzz

Small smoke run:

```bash
python scripts/fuzz_smoke.py --cases 256 --max-size 4096
```

Longer run:

```bash
python scripts/long_fuzz.py --cases 512 --max-size 16384
```

These checks verify:

- one-shot digest stability;
- streaming split equivalence;
- supported output sizes;
- deterministic behavior across repeated runs.

---

## 2. Corpus checks

```bash
python scripts/corpus_diff_runner.py --profile standard
python scripts/differential_clustering.py --profile standard
```

Corpus profiles:

| Profile | Purpose |
|---|---|
| `smoke` | fast CI/local check |
| `standard` | normal release check |
| `long` | larger manual run |

---

## 3. Reduced-round automation

Reduced-round tooling is intentionally separate from the canonical digest API.

```bash
python scripts/reduced_attack_automation.py --mode sweep --rounds 1,2,3,4 --digest-bits 16
python scripts/reduced_attack_automation.py --mode prefix --rounds 2 --digest-bits 16 --target-prefix-hex 00
```

Tiny digest sizes are expected to produce matches. These tools are used to inspect behavior, not to replace canonical release checks.

---

## 4. Toy model

```bash
python scripts/toy_smt_model.py --variable-bits 12 --digest-bits 8 --rounds 1
```

The toy model uses deterministic enumeration and SAT/SMT-style report fields.

---

## 5. Rust fuzzing

```bash
cd native/rust/fuzz
cargo fuzz run kryon_streaming
```

Target behavior:

```text
digest(data) == digest(stream_split(data))
```

---

## 6. C fuzzing ideas

Useful native C fuzz targets:

- one-shot digest;
- streaming split equivalence;
- invalid API argument handling;
- C/Python corpus parity;
- repeated `final()` calls on copied state.

---

## 7. Reports

By default, scripts write reports to:

```text
docs/reports/
```

The directory is ignored by Git and can be safely regenerated locally.
