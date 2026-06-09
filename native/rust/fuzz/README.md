# Rust fuzzing

The Rust port includes a cargo-fuzz target layout for streaming parity checks. This directory is separated from the normal crate so the core library stays dependency-free.

Command once `cargo-fuzz` is installed:

```bash
cd native/rust/fuzz
cargo fuzz run kryon_streaming
```
