from kryon import digest, hexdigest


def _bit_distance(a: bytes, b: bytes) -> int:
    return sum((x ^ y).bit_count() for x, y in zip(a, b))


def test_one_bit_change_changes_digest_substantially():
    a = digest(b"kryon property test", 384)
    b = digest(b"kryon property tesu", 384)
    assert _bit_distance(a, b) > 140


def test_domain_separation_by_output_length():
    assert hexdigest(b"abc", 256) != hexdigest(b"abc", 384)[:64]
    assert hexdigest(b"abc", 384) != hexdigest(b"abc", 512)[:96]


def test_deterministic():
    assert digest(b"same", 384) == digest(b"same", 384)
