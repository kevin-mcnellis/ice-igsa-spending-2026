#!/usr/bin/env python3
"""Purpose: Fetch frozen USAspending ZIPs and extract exact registered CSV members.
Inputs: data/manifest.csv, with URL, retrieval date, SHA-256, byte count, and
    role for each source; existing local inputs are checked before any request.
    If an official URL fails, the identical ZIP is fetched from the
    repository's GitHub release (MIRROR_BASE_URL) and checked the same way.
Outputs: Missing data/raw ZIPs and named CSV members matching the manifest.
Key: Unique manifest-relative path; checked before any download or output.
Run by: run_all.py before analytical scripts; --offline only verifies inputs.
Randomness: none.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import hashlib
import http.client
import json
import os
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from urllib.parse import urlparse
from urllib.request import urlopen
from zipfile import BadZipFile, ZipFile


REQUIRED = {"path", "source_url", "retrieved_at", "sha256", "bytes", "role",
            "archive_path", "archive_member", "source_ref", "original_sha256"}
ARCHIVE_ROLES = {"file_a_archive", "file_b_archive", "file_c_archive"}
MEMBER_ROLE = "file_c_member"
BUNDLED_ROLE = "bundled_source"
# USAspending generated-download links are not guaranteed to persist, so the
# same frozen ZIPs are also attached to this repository's GitHub release. The
# mirror is used only if the official URL fails; its bytes must match the same
# registered SHA-256, so it cannot substitute a different vintage.
MIRROR_BASE_URL = ("https://github.com/kevin-mcnellis/ice-igsa-spending-2026/"
                   "releases/download/usaspending-archives-2026-09/")


class InputError(ValueError):
    """A manifest entry or local/downloaded source failed its identity check."""


# --- Step 1: Treat the source manifest as untrusted path and URL input. ---
# Only exact, relative archive destinations and official HTTPS download hosts
# may trigger a network request. Tests exercise traversal and invalid URL failures.
def records(manifest: Path) -> list[dict[str, str]]:
    with manifest.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, strict=True)
        if not REQUIRED <= set(reader.fieldnames or ()):
            raise InputError("input manifest lacks required columns")
        rows = list(reader)
    if not rows:
        raise InputError("input manifest is empty")
    seen = set()
    for row in rows:
        name = row["path"]
        if any(not row.get(field, "").strip() for field in ("path", "sha256", "bytes", "role")):
            raise InputError(f"missing provenance field: {name}")
        if row["role"] not in ARCHIVE_ROLES | {MEMBER_ROLE, BUNDLED_ROLE}:
            raise InputError(f"invalid input role: {name}")
        if row["role"] in ARCHIVE_ROLES:
            if not row["retrieved_at"] or not row["source_url"]:
                raise InputError(f"missing provenance field: {name}")
        if row["retrieved_at"]:
            try:
                datetime.fromisoformat(row["retrieved_at"].replace("Z", "+00:00"))
            except ValueError as error:
                raise InputError(f"invalid retrieval date: {name}") from error
        source_url = urlparse(row["source_url"])
        if row["source_url"] and (source_url.scheme != "https" or not source_url.hostname or
                                  source_url.username or source_url.password):
            raise InputError(f"invalid source URL: {name}")
        relative = PurePosixPath(name)
        if (not name or "\\" in name or relative.is_absolute() or
                any(part in {"", ".", ".."} for part in name.split("/"))):
            raise InputError(f"unsafe input path: {name}")
        if name in seen:
            raise InputError(f"duplicate input path: {name}")
        seen.add(name)
        try:
            size = int(row["bytes"])
        except (TypeError, ValueError) as error:
            raise InputError(f"invalid byte count: {name}") from error
        if size < 0 or len(row["sha256"]) != 64 or any(c not in "0123456789abcdef" for c in row["sha256"]):
            raise InputError(f"invalid hash or byte count: {name}")
        if row["role"] in ARCHIVE_ROLES:
            url = urlparse(row["source_url"])
            if (relative.parts[:2] != ("data", "raw") or relative.suffix.lower() != ".zip" or
                    url.scheme != "https" or url.hostname != "files.usaspending.gov" or
                    url.username or url.password):
                raise InputError(f"unsafe archive path or URL: {name}")
        elif row["role"] == MEMBER_ROLE:
            member = row["archive_member"]
            if (relative.parts[:2] != ("data", "raw") or relative.suffix.lower() != ".csv" or
                    not row["archive_path"] or not member or
                    PurePosixPath(member).name != member or member != relative.name):
                raise InputError(f"unsafe archive member: {name}")
        elif row["role"] == BUNDLED_ROLE and not row["source_ref"]:
            raise InputError(f"bundled input lacks source reference: {name}")
    archives = {row["path"] for row in rows if row["role"] in ARCHIVE_ROLES}
    identities = [(row["archive_path"], row["archive_member"])
                  for row in rows if row["role"] == MEMBER_ROLE]
    if len(identities) != len(set(identities)):
        raise InputError("duplicate frozen archive member identity")
    for row in rows:
        if row["role"] == MEMBER_ROLE and row["archive_path"] not in archives:
            raise InputError(f"member archive missing from manifest: {row['path']}")
    receipt_root = manifest.parent / "raw"
    receipts = sorted(receipt_root.glob("*/acquisition_receipt.json"))
    if receipts:
        file_c_archives = {row["path"]: row for row in rows if row["role"] == "file_c_archive"}
        expected = set()
        for receipt_path in receipts:
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            if receipt["zip_path"] not in file_c_archives:
                continue
            archive = file_c_archives[receipt["zip_path"]]
            if (receipt["zip_sha256"] != archive["sha256"] or
                    int(receipt["zip_bytes"]) != int(archive["bytes"])):
                raise InputError("frozen File C receipt archive differs from manifest")
            expected.update((receipt["zip_path"], member["member"],
                             int(member["bytes"]), member["sha256"])
                            for member in receipt["members"])
        actual = {(row["archive_path"], row["archive_member"],
                   int(row["bytes"]), row["sha256"])
                  for row in rows if row["role"] == MEMBER_ROLE}
        if len(receipts) == 5 and (len(expected) != 7 or actual != expected):
            raise InputError("seven frozen File C members differ from acquisition receipts")
    return rows


def local_file(root: Path, name: str) -> Path:
    # LEARN: checking every existing parent prevents a manifest path from
    # writing through a symbolic link to a location outside this package.
    path = root
    for part in PurePosixPath(name).parts:
        path = path / part
        if path.is_symlink():
            raise InputError(f"symlink input path: {name}")
    if not path.resolve().is_relative_to(root.resolve()):
        raise InputError(f"input escapes release root: {name}")
    return path


def fingerprint(path: Path) -> tuple[int, str]:
    hasher = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            size += len(block)
            hasher.update(block)
    return size, hasher.hexdigest()


def check(path: Path, row: dict[str, str]) -> None:
    if not path.is_file():
        raise InputError(f"missing input: {row['path']}")
    if fingerprint(path) != (int(row["bytes"]), row["sha256"]):
        raise InputError(f"existing input differs from frozen manifest: {row['path']}")


# --- Step 2: Verify every registered local input before interpreting results. ---
# A fresh clone's missing archive is a hard error in offline mode, not a zero.
# Check: tests cover missing, matching, and mismatched frozen bytes.
def verify_inputs(root: Path, manifest: Path) -> dict[str, int]:
    root = Path(root).resolve()
    rows = records(Path(manifest))
    for row in rows:
        check(local_file(root, row["path"]), row)
    return {"verified": len(rows)}


def download_verified(opener, url: str, stage: Path, row: dict[str, str]) -> None:
    """Download one URL into `stage`, overwriting it, and check registered bytes."""
    with opener(url) as response, stage.open("wb") as output:
        downloaded = 0
        for block in iter(lambda: response.read(1024 * 1024), b""):
            downloaded += len(block)
            if downloaded > int(row["bytes"]):
                raise InputError(f"download exceeds registered byte count: {row['path']}")
            output.write(block)
    if fingerprint(stage) != (int(row["bytes"]), row["sha256"]):
        raise InputError(f"download hash or byte count mismatch: {row['path']}")


# --- Step 3: Download archives, extract named members, and verify exact bytes. ---
# A saved mismatching file is never overwritten. A same-directory hard link
# installs a validated temporary file without replacing an entry that appears
# concurrently. Tests cover wrong bytes and preservation of an existing file.
def fetch_inputs(root: Path, manifest: Path, opener=None) -> dict[str, int]:
    root = Path(root).resolve()
    rows = records(Path(manifest))
    if opener is None:
        opener = lambda url: urlopen(url, timeout=60)
    # A missing bundled file or an existing hash mismatch stops before network.
    for row in rows:
        target = local_file(root, row["path"])
        if target.exists():
            check(target, row)
        elif row["role"] == BUNDLED_ROLE:
            raise InputError(f"missing bundled input: {row['path']}")
    for row in rows:
        if row["role"] not in ARCHIVE_ROLES:
            continue
        target = local_file(root, row["path"])
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(prefix=".frozen-input-", dir=target.parent) as temporary:
            stage = Path(temporary) / "archive.part"
            # Try the official URL first, then the repository mirror. Each
            # attempt is a complete download plus size and SHA-256 check into a
            # fresh stage file, so an unreachable, interrupted, or wrong-content
            # official response moves on to the mirror, and no unverified bytes
            # are ever installed. The last source's error is raised unchanged.
            # Check: tests cover open failure, interrupted and truncated reads,
            # wrong official bytes, a wrong mirror hash, and both sources failing.
            urls = [row["source_url"], MIRROR_BASE_URL + PurePosixPath(row["path"]).name]
            # LEARN: enumerate yields (position, url) pairs, so the loop knows
            # LEARN: when it is on the last URL.
            for position, url in enumerate(urls):
                # LEARN: except catches only network/HTTP failures (OSError, or
                # LEARN: HTTPException for a response cut off mid-stream) and
                # LEARN: failed byte checks (InputError); a bare `raise` re-raises
                # LEARN: the last one, so an outage never becomes an empty file.
                # LEARN: `break` stops after the first fully verified download.
                try:
                    download_verified(opener, url, stage, row)
                    break
                except (OSError, http.client.HTTPException, InputError):
                    if position == len(urls) - 1:
                        raise
            try:
                os.link(stage, target)
            except FileExistsError as error:
                raise InputError(f"input appeared during download: {row['path']}") from error
    for row in rows:
        if row["role"] != MEMBER_ROLE:
            continue
        target = local_file(root, row["path"])
        if target.exists():
            continue
        archive = local_file(root, row["archive_path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(prefix=".frozen-member-", dir=target.parent) as temporary:
            stage = Path(temporary) / "member.part"
            try:
                with ZipFile(archive) as zipped, zipped.open(row["archive_member"]) as source, stage.open("wb") as output:
                    size = 0
                    for block in iter(lambda: source.read(1024 * 1024), b""):
                        size += len(block)
                        if size > int(row["bytes"]):
                            raise InputError(f"member exceeds registered byte count: {row['path']}")
                        output.write(block)
            except (BadZipFile, KeyError) as error:
                raise InputError(f"missing or invalid archive member: {row['path']}") from error
            if fingerprint(stage) != (int(row["bytes"]), row["sha256"]):
                raise InputError(f"archive member hash or byte count mismatch: {row['path']}")
            try:
                os.link(stage, target)
            except FileExistsError as error:
                raise InputError(f"input appeared during extraction: {row['path']}") from error
    return verify_inputs(root, manifest)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("data/manifest.csv"))
    parser.add_argument("--offline", action="store_true", help="Verify registered bytes without downloads.")
    args = parser.parse_args()
    try:
        result = (verify_inputs if args.offline else fetch_inputs)(Path.cwd(), args.manifest)
    except (InputError, OSError, http.client.HTTPException, csv.Error) as error:
        parser.exit(2, f"Input verification stopped: {error}\n")
    print(f"PASS: verified {result['verified']} registered inputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
