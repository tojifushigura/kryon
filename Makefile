.PHONY: test fuzz-smoke vectors parity release-check final-audit rust-test rust-bench c-kat c-corpus-parity clean corpus-diff long-fuzz parity-corpus attack-sweep toy-model diff-cluster

test:
	python -m pytest -q

fuzz-smoke:
	python scripts/fuzz_smoke.py --cases 256 --max-size 4096

vectors:
	python scripts/native_kat.py

parity:
	python scripts/parity_runner.py

release-check:
	python scripts/release_check.py --run-pytest --run-c

final-audit:
	python scripts/final_audit.py

rust-test:
	cd native/rust && cargo test --locked

rust-bench:
	python scripts/rust_benchmark.py

c-kat:
	python scripts/c_kat.py

c-corpus-parity:
	python scripts/c_corpus_parity.py --profile smoke

attack-sweep:
	python scripts/reduced_attack_automation.py --mode sweep --rounds 1,2,3,4 --digest-bits 16

toy-model:
	python scripts/toy_smt_model.py --variable-bits 12 --digest-bits 8 --rounds 1

diff-cluster:
	python scripts/differential_clustering.py --profile standard

corpus-diff:
	python scripts/corpus_diff_runner.py --profile standard

long-fuzz:
	python scripts/long_fuzz.py --cases 512 --max-size 16384

parity-corpus:
	python scripts/parity_corpus_runner.py --profile standard

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache build dist *.egg-info
	$(MAKE) -C native/c clean
