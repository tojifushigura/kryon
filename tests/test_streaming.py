import io

from kryon import digest, hexdigest, new
from kryon.cli import _hash_stream


def test_streaming_matches_one_shot_for_many_chunk_sizes():
    data = (b"Kryon streaming test vector:" + bytes(range(256))) * 64 + b"tail"
    expected = hexdigest(data, 384)

    for chunk_size in [1, 2, 3, 7, 16, 31, 32, 33, 64, 255, 1024]:
        h = new(out_bits=384)
        for i in range(0, len(data), chunk_size):
            h.update(data[i : i + chunk_size])
        assert h.hexdigest() == expected


def test_streaming_file_helper_matches_one_shot():
    data = b"abc" * 10000
    assert _hash_stream(io.BytesIO(data), 384) == digest(data, 384)


def test_string_input_is_utf8():
    assert hexdigest("привет", 384) == hexdigest("привет".encode("utf-8"), 384)
