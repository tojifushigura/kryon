import pytest

from kryon import KryonError, digest, digest_reduced, hexdigest, hexdigest_reduced, make_profile, new_reduced
from kryon.core import RoundProfile
from kryon.analysis import avalanche_report, bit_distance, flip_bit


def test_canonical_profile_still_matches_standard_digest():
    profile = RoundProfile()
    assert digest_reduced(b"abc", out_bits=384, profile=profile) == digest(b"abc", 384)
    assert hexdigest_reduced(b"abc", out_bits=384, profile=profile) == hexdigest(b"abc", 384)


def test_reduced_profile_is_deterministic_and_different_from_canonical():
    a = hexdigest_reduced(b"abc", absorb_rounds=2)
    b = hexdigest_reduced(b"abc", absorb_rounds=2)
    assert a == b
    assert a != hexdigest(b"abc", 384)


def test_reduced_streaming_matches_one_shot():
    data = b"streaming reduced profile" * 20
    profile = make_profile(absorb_rounds=3)
    expected = digest_reduced(data, profile=profile)
    h = new_reduced(profile=profile)
    for chunk in [data[:7], data[7:64], data[64:]]:
        h.update(chunk)
    assert h.digest() == expected


@pytest.mark.parametrize("bits,size", [(8, 1), (16, 2), (32, 4), (64, 8)])
def test_reduced_digest_truncation(bits, size):
    assert len(digest_reduced(b"abc", digest_bits=bits, absorb_rounds=2)) == size


@pytest.mark.parametrize("bits", [0, 7, 9, 520])
def test_invalid_reduced_digest_bits(bits):
    with pytest.raises(KryonError):
        digest_reduced(b"abc", digest_bits=bits)


def test_invalid_round_profile():
    with pytest.raises(KryonError):
        make_profile(absorb_rounds=0)
    with pytest.raises(KryonError):
        make_profile(absorb_rounds=19)


def test_analysis_helpers():
    assert bit_distance(b"\x00", b"\xff") == 8
    assert flip_bit(b"\x00", 0) == b"\x01"
    report = avalanche_report(samples=4, message_size=16, digest_bits=64, seed=1)
    assert report.samples == 4
    assert report.digest_bits == 64
    assert 0 <= report.mean_ratio <= 1
