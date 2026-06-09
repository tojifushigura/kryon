from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_rust_crate_metadata_is_v1():
    cargo = (ROOT / "native/rust/Cargo.toml").read_text(encoding="utf-8")
    lock = (ROOT / "native/rust/Cargo.lock").read_text(encoding="utf-8")
    assert 'name = "kryon-native"' in cargo
    assert 'version = "1.0.0"' in cargo
    assert 'version = "1.0.0"' in lock


def test_c_header_metadata_is_v1():
    header = (ROOT / "native/c/kryon_native.h").read_text(encoding="utf-8")
    assert '#define KRYON_NATIVE_VERSION "kryon-native-c-1.0.0"' in header
    assert "KRYON_ERR_UNIMPLEMENTED" not in header


def test_native_readmes_are_v1():
    c_readme = (ROOT / "native/c/README.md").read_text(encoding="utf-8")
    rust_readme = (ROOT / "native/rust/README.md").read_text(encoding="utf-8")
    assert "v1.0" in c_readme
    assert "v1.0" in rust_readme
