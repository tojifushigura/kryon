import pytest

from kryon import KryonError, digest, hexdigest, new


KAT_384 = {
    b"": "ce22c2f741871b79ad60664f786b3e314cab314d5c9e8d7b63c725ba7596e681f9de5dccbd19d8243c82e57a22ab25ae",
    b"abc": "06f61fabf777a7653a46c921eb46bc9a52c876f0cb7afd60495118b5b81f73830b0cab537db8aea4bade55d717f71370",
    b"The quick brown fox jumps over the lazy dog": "6afd3754f279989a9b76b1bbf093bb2dc36557e4371089a7c02dacd9aac1ff918c8bff4846933e02d908c6ebcdba4e1e",
}


@pytest.mark.parametrize("message,expected", KAT_384.items())
def test_kryon_384_vectors(message, expected):
    assert hexdigest(message, 384) == expected


@pytest.mark.parametrize("bits,size", [(256, 32), (384, 48), (512, 64)])
def test_digest_sizes(bits, size):
    assert len(digest(b"abc", bits)) == size


def test_hashlib_like_api_copy_and_update():
    h1 = new(out_bits=384)
    h1.update(b"ab")
    h2 = h1.copy()
    h1.update(b"c")
    h2.update(b"c")
    assert h1.hexdigest() == h2.hexdigest() == hexdigest(b"abc", 384)


def test_digest_does_not_finalize_object():
    h = new(b"ab", out_bits=384)
    before = h.hexdigest()
    assert before == hexdigest(b"ab", 384)
    h.update(b"c")
    assert h.hexdigest() == hexdigest(b"abc", 384)


def test_invalid_digest_size():
    with pytest.raises(KryonError):
        digest(b"abc", 128)
