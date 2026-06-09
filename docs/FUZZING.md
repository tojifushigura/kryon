# Fuzzing and attack automation

## Python deterministic fuzz

```bash
python scripts/fuzz_smoke.py --cases 256 --max-size 4096
python scripts/long_fuzz.py --cases 512 --max-size 16384
```

## Corpus differential checks

```bash
python scripts/corpus_diff_runner.py --profile standard
python scripts/differential_clustering.py --profile standard
```

## Reduced-round attack automation

```bash
python scripts/reduced_attack_automation.py --mode sweep --rounds 1,2,3,4 --digest-bits 16
python scripts/reduced_attack_automation.py --mode prefix --rounds 2 --digest-bits 16 --target-prefix-hex 00
```

These commands intentionally target truncated reduced-round outputs. Collisions and prefix matches are expected for tiny digest sizes.

## Toy SAT/SMT model

```bash
python scripts/toy_smt_model.py --variable-bits 12 --digest-bits 8 --rounds 1
```

The v0.8 model uses deterministic enumeration but keeps SAT/SMT-style fields in the output. A future v0.9 backend can replace it with Z3/Boolector without changing report consumers.

## Rust fuzzing plan

```bash
cd native/rust/fuzz
cargo fuzz run kryon_streaming
```

## C fuzzing plan

The C port now has a real canonical implementation. The next step is adding AFL/libFuzzer harnesses around:

- one-shot digest;
- streaming split equivalence;
- C/Python corpus parity;
- invalid API argument handling.
