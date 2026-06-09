# Kryon v1.0 Release Checklist

## Required commands

```bash
python -m pytest -q
kryon --self-test
python scripts/release_check.py --run-pytest --run-c
python scripts/final_audit.py
```

## Required results

| Gate | Required result |
|---|---:|
| Python tests | passed |
| KAT vectors | stable |
| Streaming fuzz | passed |
| Corpus diff | passed or review_needed |
| Reduced attack sweep | passed or review_needed |
| Toy model | passed or review_needed |
| C KAT | passed when C compiler exists |
| C corpus parity | passed when C compiler exists |
| Rust KAT/corpus | passed in CI where Cargo exists |
| Final audit | `ready_to_launch_as_v1_software_project` |

## Version rules

- Patch release: bug fixes that do not change canonical digest.
- Minor release: new tools/APIs that do not change canonical digest.
- Major release: any change to canonical digest, padding, constants, or permutation.

## Release statement

Kryon v1.0 is ready to launch as a complete custom hash software project.
