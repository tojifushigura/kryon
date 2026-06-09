from pathlib import Path

from kryon.cli import main
from kryon.fileio import build_manifest, file_hexdigest, manifest_digest, manifest_text, verify_manifest


def test_file_hexdigest_and_manifest_roundtrip(tmp_path: Path):
    f = tmp_path / "sample.bin"
    f.write_bytes(b"abc" * 100)
    digest = file_hexdigest(f, 384)
    assert len(digest) == 96
    entries = build_manifest([f], 384, base_dir=tmp_path)
    assert entries[0].path == "sample.bin"
    text = manifest_text(entries)
    assert digest in text
    m = tmp_path / "kryon.manifest"
    m.write_text(text, encoding="utf-8")
    results = verify_manifest(m, base_dir=tmp_path)
    assert len(results) == 1
    assert results[0].ok is True
    assert len(manifest_digest(entries, 384)) == 96


def test_cli_self_test(capsys):
    rc = main(["--self-test"])
    captured = capsys.readouterr()
    assert rc == 0
    assert '"status": "passed"' in captured.out


def test_cli_manifest_check(tmp_path: Path, capsys):
    f = tmp_path / "sample.txt"
    f.write_text("hello", encoding="utf-8")
    entries = build_manifest([f], 384, base_dir=tmp_path)
    m = tmp_path / "cw.txt"
    m.write_text(manifest_text(entries), encoding="utf-8")
    rc = main(["--check", str(m)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "OK  sample.txt" in out
