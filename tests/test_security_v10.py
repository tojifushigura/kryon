from kryon import (
    KryonError,
    domain_hexdigest,
    hexdigest,
    keyed_hexdigest,
    verify_hexdigest,
)


def test_domain_separation_changes_digest():
    plain = hexdigest(b"abc", 384)
    file_tag = domain_hexdigest("file", b"abc", 384)
    manifest_tag = domain_hexdigest("manifest", b"abc", 384)
    assert plain != file_tag
    assert file_tag != manifest_tag


def test_keyed_digest_uses_key_and_personalization():
    a = keyed_hexdigest("secret-a", b"abc", 384)
    b = keyed_hexdigest("secret-b", b"abc", 384)
    c = keyed_hexdigest("secret-a", b"abc", 384, personalization="app-1")
    assert a != b
    assert a != c


def test_verify_hexdigest_constant_time_helper():
    expected = hexdigest(b"abc", 384)
    assert verify_hexdigest(expected, b"abc", 384)
    assert not verify_hexdigest(expected, b"abcd", 384)
    assert not verify_hexdigest("not hex", b"abc", 384)


def test_keyed_digest_requires_key():
    import pytest
    with pytest.raises(KryonError):
        keyed_hexdigest(b"", b"abc", 384)
