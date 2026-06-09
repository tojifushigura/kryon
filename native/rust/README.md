# Kryon native Rust port v1.0

This crate is the native Rust reference port of the canonical Kryon core. It is used for parity checks, profiling, fuzzing, and native integration work.

## API

```rust
use kryon_native::{Context, hexdigest};

let one_shot = hexdigest(b"abc", 384).unwrap();

let mut ctx = Context::new(384).unwrap();
ctx.update(b"a").unwrap();
ctx.update(b"bc").unwrap();
let streaming = ctx.hexdigest().unwrap();
assert_eq!(one_shot, streaming);
```

## Test

```bash
cd native/rust
cargo test --locked
cargo run --example kryon_kat --locked
cargo run --example kryon_corpus --locked < ../../docs/reports/corpus_input.txt
```

The expected Kryon-384 KAT values are duplicated in `src/lib.rs` tests and in `docs/VECTORS.md`.
