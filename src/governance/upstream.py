"""Fetch the pinned upstream repos and check file SHA-256s.

The churn repo has no packaging metadata, so it is not installed from git.
The archive at the pinned commit is downloaded and each file in the lock is hashed.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

from governance.paths import LOCK_PATH, VENDOR

_USER_AGENT = "responsible-ai-pack"


def file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def load_lock(path: Path | None = None) -> dict:
    return json.loads((path or LOCK_PATH).read_text())


def _download(url: str, dest: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response:
        dest.write_bytes(response.read())


def _hashes_match(root: Path, files: dict[str, str]) -> bool:
    for rel, expected in files.items():
        path = root / rel
        if not path.is_file() or file_sha256(path) != expected:
            return False
    return True


def _require_hashes(root: Path, files: dict[str, str]) -> None:
    mismatches = []
    for rel, expected in files.items():
        path = root / rel
        if not path.is_file():
            mismatches.append(f"missing {rel}")
            continue
        actual = file_sha256(path)
        if actual != expected:
            mismatches.append(f"{rel}: {actual} != {expected}")
    if mismatches:
        joined = "\n".join(mismatches)
        raise RuntimeError(f"Checksum mismatch under {root}:\n{joined}")


def _safe_extract(archive: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:gz") as tar:
        for member in tar.getmembers():
            target = (dest / member.name).resolve()
            if target != dest.resolve() and dest.resolve() not in target.parents:
                raise RuntimeError(f"Unsafe archive path {member.name}")
        tar.extractall(dest)


def _fetch_telco(spec: dict, vendor: Path) -> Path:
    dest = vendor / spec["dest"]
    if dest.is_dir() and _hashes_match(dest, spec["files"]):
        return dest
    vendor.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        archive = tmp_path / "source.tar.gz"
        _download(spec["archive_url"], archive)
        extract_root = tmp_path / "extract"
        _safe_extract(archive, extract_root)
        extracted = extract_root / spec["extract_prefix"]
        if not extracted.is_dir():
            found = sorted(path.name for path in extract_root.iterdir())
            raise RuntimeError(f"Archive prefix {spec['extract_prefix']} not found in {found}")
        _require_hashes(extracted, spec["files"])
        if dest.exists():
            shutil.rmtree(dest)
        shutil.move(str(extracted), dest)
    _require_hashes(dest, spec["files"])
    return dest


def _fetch_raw_tree(spec: dict, vendor: Path) -> Path:
    dest = vendor / spec["dest"]
    if dest.is_dir() and _hashes_match(dest, spec["files"]):
        return dest
    vendor.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        staged = Path(tmp) / spec["dest"]
        for rel in spec["files"]:
            target = staged / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            _download(spec["raw_base"] + rel, target)
        _require_hashes(staged, spec["files"])
        if dest.exists():
            shutil.rmtree(dest)
        shutil.move(str(staged), dest)
    _require_hashes(dest, spec["files"])
    return dest


def ensure_upstream(vendor: Path | None = None, lock_path: Path | None = None) -> dict[str, Path]:
    """Download anything missing and return the two vendor roots."""
    spec = load_lock(lock_path)
    root = vendor or VENDOR
    telco = _fetch_telco(spec["telco"], root)
    multihead = _fetch_raw_tree(spec["multihead"], root)
    src = telco / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    return {"telco": telco, "multihead": multihead}


def telco_root() -> Path:
    return ensure_upstream()["telco"]


def multihead_root() -> Path:
    return ensure_upstream()["multihead"]
