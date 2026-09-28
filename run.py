#!/usr/bin/env python3
"""Rebuild the chart: prepare the three amounts, plot them, save verification.

Run `uv run --frozen python3 run.py` from this folder. Read build() first;
the two analysis stages live in scripts/. Inputs are never changed, and a
failed run leaves the previous outputs intact. No downloads happen here.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from scripts.prepare_chart_data import prepare
from scripts.plot_chart import plot

OUTPUTS = (
    "chart_source_rows.csv", "recipient_totals.csv", "chart_totals.csv",
    "obligations_chart.svg", "obligations_chart.png",
)
LIMITS = [
    "Name matches do not establish legal government identity or complete corporate families.",
    "The two subgroup bars may overlap and do not sum to the total.",
    "Reproducing File C does not establish complete agency reporting or reconcile to File B.",
    "These are signed obligations, not payments, IGSA spending, or facility allocations.",
]


def sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def code_version(project: Path) -> dict:
    """Record Git when available; a portable copy is identified by code hashes."""
    files = [project / "run.py", project / "pyproject.toml", project / "uv.lock",
             project / "data/source_manifest.csv", *sorted((project / "scripts").glob("*.py"))]
    result = {"git_commit": None, "git_dirty": None, "python": platform.python_version(),
              "file_sha256": {p.relative_to(project).as_posix(): sha256(p) for p in files if p.is_file()}}
    try:
        def git(*args):
            return subprocess.check_output(["git", "-C", str(project), *args],
                                           text=True, stderr=subprocess.DEVNULL, timeout=5).strip()
        git("ls-files", "--error-unmatch", "run.py")
        result.update(git_commit=git("rev-parse", "HEAD"), git_dirty=bool(git("status", "--porcelain")))
    except (OSError, subprocess.SubprocessError):
        pass  # A copied folder intentionally needs no Git repository.
    return result


def build(project: Path = ROOT) -> dict:
    """The reading path: calculate → plot → verify → publish complete outputs."""
    project = project.resolve()
    with TemporaryDirectory(prefix=".chart-build-", dir=project) as temporary:
        stage = Path(temporary) / "new"
        stage.mkdir()

        print("1/2  Checking frozen inputs and calculating the three bars…", flush=True)
        analysis = prepare(project, stage)
        print("2/2  Drawing SVG and PNG from chart_totals.csv…", flush=True)
        plot(stage / "chart_totals.csv", stage)

        for name in OUTPUTS:
            if not (stage / name).is_file() or not (stage / name).stat().st_size:
                raise ValueError(f"missing or empty output: {name}")
        report = {"technical_status": "PASS", "interpretation_status": "WARN",
                  "limitations": LIMITS, "analysis": analysis,
                  "source_version": code_version(project),
                  "completed_at_utc": datetime.now(timezone.utc).isoformat(),
                  "output_sha256": {name: sha256(stage / name) for name in OUTPUTS}}
        (stage / "verification.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

        # Only a complete new package can replace the previous generated package.
        output, previous = project / "outputs", Path(temporary) / "previous"
        try:
            if output.exists():
                output.rename(previous)
            stage.rename(output)
        except BaseException:
            # Also restore on Ctrl-C before the temporary backup is cleaned up.
            if previous.exists() and not output.exists():
                previous.rename(output)
            raise
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="Return failure while interpretation warnings remain.")
    args = parser.parse_args()
    try:
        report = build()
    except (ValueError, OSError) as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        return 2
    print(f"PASS: complete outputs saved to {ROOT / 'outputs'}")
    print("WARN: recipient-name and reporting limits remain; see outputs/verification.json.")
    return 1 if args.strict and report["interpretation_status"] == "WARN" else 0


if __name__ == "__main__":
    raise SystemExit(main())
