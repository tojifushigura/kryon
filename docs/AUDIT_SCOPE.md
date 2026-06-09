# Kryon v1.0 Review Scope

## Cryptographic review targets

| Area | Questions |
|---|---|
| Collision resistance | Are there structural collisions faster than generic attack? |
| Preimage resistance | Does dual-rail mixing leak shortcuts? |
| Second preimage | Does streaming block indexing prevent extension-style attacks? |
| Differential trails | Are reduced-round trails extendable to full rounds? |
| Algebraic structure | Does modulo-257 rail introduce exploitable relations? |
| Constants | Are generated constants free of suspicious trapdoors? |

## Implementation review targets

| Area | Questions |
|---|---|
| Python core | Is streaming/finalization correct? |
| C port | Does it match Python exactly for corpus/KAT? |
| Rust port | Does it match Python exactly for corpus/KAT? |
| CLI | Are file and manifest operations safe and predictable? |
| Packaging | Is versioning and API stable? |
| Tests | Are corpus, fuzz, and parity gates sufficient for releases? |

## Review deliverables

1. Review of specification and constants.
2. Independent implementation of KAT vectors.
3. Reduced-round attack report.
4. Full-round security argument or discovered weaknesses.
5. Implementation review for C/Rust memory safety and API misuse.

## Project statement

Kryon v1.0 is a custom, complete, one-way hash implementation and analysis toolkit.
