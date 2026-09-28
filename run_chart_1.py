#!/usr/bin/env python3
"""Build chart 1: the provisional File B–File C obligation comparison for 25.4.

Run from this folder: uv --cache-dir .cache/uv run --frozen python3 run_chart_1.py
Read build() first, then the two scripts it calls. This command uses only local
frozen sources and writes outputs/chart_1/. Earlier recipient-screen results
remain available in outputs/ for the separate chart 2 research.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from run import code_version, sha256
from scripts.prepare_comparison_data import prepare
from scripts.plot_comparison import plot

DATA_OUTPUTS = (
    "comparison_source_rows.csv", "comparison_totals.csv",
    "comparison_by_period.csv", "comparison_accounting_keys.csv",
)
OUTPUTS = (*DATA_OUTPUTS, "obligations_comparison_25_4.svg", "obligations_comparison_25_4.png",
           "obligations_comparison_25_4_mobile.svg", "obligations_comparison_25_4_mobile.png",
           "obligations_comparison_25_4.html")


def build(project: Path = ROOT) -> dict:
    """Calculate → draw → check → replace this chart's complete output folder."""
    project = project.resolve()
    with TemporaryDirectory(prefix=".chart-build-", dir=project) as temporary:
        stage = Path(temporary) / "new"
        stage.mkdir()
        print("1/2  Checking frozen File B/C inputs and calculating the two bars…", flush=True)
        analysis = prepare(project, stage)
        print("2/2  Drawing the 25.4 comparison from comparison_totals.csv…", flush=True)
        plot(stage / "comparison_totals.csv", stage)

        for name in OUTPUTS:
            path = stage / name
            if not path.is_file() or not path.stat().st_size:
                raise ValueError(f"missing or empty output: {name}")
            if name in DATA_OUTPUTS:
                with path.open(encoding="utf-8", newline="") as handle:
                    reader = csv.DictReader(handle, strict=True)
                    if not reader.fieldnames:
                        raise ValueError(f"missing CSV header: {name}")
                    for row in reader:
                        if None in row or any(value is None for value in row.values()):
                            raise ValueError(f"malformed output CSV: {name}")

        version = code_version(project)
        for relative in ("run_chart_1.py", "data/comparison_source_manifest.csv"):
            path = project / relative
            if path.is_file():
                version["file_sha256"][relative] = sha256(path)
        report = {
            "technical_status": "PASS", "interpretation_status": "WARN",
            "analysis": analysis, "source_version": version,
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "output_sha256": {name: sha256(stage / name) for name in OUTPUTS},
        }
        (stage / "verification.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

        output = project / "outputs/chart_1"
        output.parent.mkdir(parents=True, exist_ok=True)
        previous = Path(temporary) / "previous"
        try:
            if output.exists():
                output.rename(previous)
            stage.rename(output)
        except BaseException:
            # Preserve the previous complete result even if Ctrl-C interrupts replacement.
            if previous.exists() and not output.exists():
                previous.rename(output)
            raise
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="Return 1 while accounting interpretation remains provisional.")
    args = parser.parse_args()
    try:
        build()
    except (ValueError, OSError) as error:
        print(f"Build failed: {error}", file=sys.stderr)
        return 2
    print(f"PASS: complete chart outputs saved to {ROOT / 'outputs/chart_1'}")
    print("WARN: accounting reconciliation remains provisional; see verification.json.")
    return 1 if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
