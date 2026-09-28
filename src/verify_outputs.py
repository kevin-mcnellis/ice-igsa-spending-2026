"""Check stable public output bytes against the reviewed release fingerprints."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath


class OutputError(ValueError):
    """A released output is absent, unsafe, or different from the review copy."""


def verify_outputs(root: Path, checks: Path) -> int:
    root = Path(root).resolve()
    expected = json.loads(Path(checks).read_text(encoding="utf-8"))
    if expected.get("schema_version") != 2 or not isinstance(expected.get("files"), dict) or not expected["files"]:
        raise OutputError("output checks are missing or invalid")
    dynamic = expected.get("dynamic_receipts")
    unreleased = expected.get("generated_unreleased")
    released = expected.get("released_files")
    if (not isinstance(dynamic, list) or not isinstance(unreleased, list) or
            not isinstance(released, list) or len(dynamic) != 3):
        raise OutputError("output inventory is missing or invalid")
    expected_names = set(expected["files"]) | set(dynamic) | set(unreleased)
    if any(not isinstance(name, str) or not name.startswith("outputs/") or
           any(part in {"", ".", ".."} for part in name.split("/"))
           for name in expected_names):
        raise OutputError("unsafe output inventory entry")
    if set(released) != set(expected["files"]) | set(dynamic):
        raise OutputError("released output inventory differs from checked outputs")
    if len(expected_names) != len(expected["files"]) + len(dynamic) + len(unreleased):
        raise OutputError("duplicate output inventory entry")
    actual_names = {path.relative_to(root).as_posix() for path in (root / "outputs").rglob("*")
                    if path.is_file() or path.is_symlink()}
    if actual_names != expected_names:
        raise OutputError(f"output inventory differs: missing={sorted(expected_names - actual_names)}, extra={sorted(actual_names - expected_names)}")
    for name, digest in expected["files"].items():
        relative = PurePosixPath(name)
        if (not name.startswith("outputs/") or relative.is_absolute() or
                any(part in {"", ".", ".."} for part in name.split("/")) or
                not isinstance(digest, str) or len(digest) != 64):
            raise OutputError(f"unsafe output check: {name}")
        path = root
        for part in relative.parts:
            path = path / part
            if path.is_symlink():
                raise OutputError(f"symlink output: {name}")
        if not path.is_file() or not path.resolve().is_relative_to(root):
            raise OutputError(f"missing output: {name}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            raise OutputError(f"output SHA-256 differs: {name}")
    for name in dynamic:
        if not name.startswith("outputs/") or Path(name).name != "verification.json":
            raise OutputError(f"unsafe dynamic receipt: {name}")
        receipt = json.loads((root / name).read_text(encoding="utf-8"))
        if receipt.get("technical_status") != "PASS" or not isinstance(receipt.get("output_sha256"), dict):
            raise OutputError(f"invalid dynamic receipt: {name}")
        folder = Path(name).parent
        produced = {p.name for p in (root / folder).iterdir() if p.is_file() and p.name != "verification.json"}
        if set(receipt["output_sha256"]) != produced:
            raise OutputError(f"dynamic receipt output inventory differs: {name}")
        for filename, digest in receipt["output_sha256"].items():
            if filename != Path(filename).name or len(digest) != 64:
                raise OutputError(f"invalid dynamic output: {name}")
            if hashlib.sha256((root / folder / filename).read_bytes()).hexdigest() != digest:
                raise OutputError(f"dynamic output SHA-256 differs: {folder / filename}")
    return len(expected["files"])
