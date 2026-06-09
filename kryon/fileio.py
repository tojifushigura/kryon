from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterable

from .core import KryonError, new
from .security import domain_hexdigest

DEFAULT_CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True)
class ManifestEntry:
    path: str
    bits: int
    digest: str
    ok: bool | None = None
    error: str | None = None

    def line(self) -> str:
        return f"{self.digest}  {self.bits}  {self.path}"


def hash_stream(stream: BinaryIO, out_bits: int = 384, *, chunk_size: int = DEFAULT_CHUNK_SIZE) -> bytes:
    if chunk_size <= 0:
        raise KryonError("chunk_size must be positive")
    h = new(out_bits=out_bits)
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        h.update(chunk)
    return h.digest()


def hash_file(path: str | Path, out_bits: int = 384, *, chunk_size: int = DEFAULT_CHUNK_SIZE) -> bytes:
    p = Path(path)
    with p.open("rb") as f:
        return hash_stream(f, out_bits, chunk_size=chunk_size)


def file_hexdigest(path: str | Path, out_bits: int = 384, *, chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
    return hash_file(path, out_bits, chunk_size=chunk_size).hex()


def build_manifest(paths: Iterable[str | Path], out_bits: int = 384, *, base_dir: str | Path | None = None) -> list[ManifestEntry]:
    base = Path(base_dir).resolve() if base_dir is not None else None
    entries: list[ManifestEntry] = []
    for raw in paths:
        p = Path(raw)
        digest = file_hexdigest(p, out_bits)
        display = str(p)
        if base is not None:
            try:
                display = str(p.resolve().relative_to(base))
            except ValueError:
                display = str(p)
        entries.append(ManifestEntry(path=display, bits=out_bits, digest=digest))
    return entries


def manifest_text(entries: Iterable[ManifestEntry]) -> str:
    return "\n".join(entry.line() for entry in entries) + "\n"


def parse_manifest_line(line: str) -> ManifestEntry:
    stripped = line.rstrip("\n")
    if not stripped or stripped.lstrip().startswith("#"):
        raise KryonError("empty/comment manifest line")
    parts = stripped.split("  ", 2)
    if len(parts) != 3:
        raise KryonError("manifest line must be: <hex>  <bits>  <path>")
    digest, bits_s, path = parts
    try:
        bits = int(bits_s)
    except ValueError as exc:
        raise KryonError("manifest bits must be an integer") from exc
    if bits not in {256, 384, 512}:
        raise KryonError("manifest bits must be 256, 384, or 512")
    try:
        bytes.fromhex(digest)
    except ValueError as exc:
        raise KryonError("manifest digest must be hex") from exc
    return ManifestEntry(path=path, bits=bits, digest=digest.lower())


def verify_manifest(manifest_path: str | Path, *, base_dir: str | Path | None = None) -> list[ManifestEntry]:
    mpath = Path(manifest_path)
    base = Path(base_dir) if base_dir is not None else mpath.parent
    results: list[ManifestEntry] = []
    for lineno, line in enumerate(mpath.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            entry = parse_manifest_line(line)
            actual = file_hexdigest(base / entry.path, entry.bits)
            results.append(ManifestEntry(path=entry.path, bits=entry.bits, digest=entry.digest, ok=(actual == entry.digest)))
        except Exception as exc:  # keep verification useful for all lines
            results.append(ManifestEntry(path=f"<line {lineno}>", bits=0, digest="", ok=False, error=str(exc)))
    return results


def manifest_digest(entries: Iterable[ManifestEntry], out_bits: int = 384) -> str:
    return domain_hexdigest("manifest-v1", manifest_text(entries).encode("utf-8"), out_bits)


__all__ = [
    "DEFAULT_CHUNK_SIZE",
    "ManifestEntry",
    "build_manifest",
    "file_hexdigest",
    "hash_file",
    "hash_stream",
    "manifest_digest",
    "manifest_text",
    "parse_manifest_line",
    "verify_manifest",
]
