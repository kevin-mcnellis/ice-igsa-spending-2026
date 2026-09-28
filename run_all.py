#!/usr/bin/env python3
"""Verify frozen inputs, rebuild the File C outputs, and compare reviewed hashes.

Run from any directory with `uv run --frozen python3 run_all.py`. The source
manifest identifies the exact archived vintage; this command does not issue a
new USAspending query. Selected Figure A and gap PNGs are hash-verified review
assets. Figure B and the analytical tables are rebuilt below.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory

from data.fetch.fetch_inputs import fetch_inputs, verify_inputs
from run_chart_1 import build as build_chart_1
from run_chart_2 import build as build_chart_2
from run_facility_name_screen import execute as screen_facilities
from scripts import check_facility_name_statistics as statistics
from scripts.plot_figure_b import plot as plot_figure_b
from scripts.prepare_figure_b import prepare as prepare_figure_b
from src.verify_outputs import verify_outputs


ROOT = Path(__file__).resolve().parent
SMALL = Path("data/small/facility_name_screen")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_facility_screen(root: Path) -> tuple[dict, dict]:
    small = root / SMALL
    output = root / "outputs/facility_name_screen"
    code, screen = screen_facilities(
        panel_path=small / "detention_roster_facility_snapshot_panel.csv",
        manifest_path=small / "source_manifest.json",
        blog_path=small / "v6/financial_rows.csv",
        source_root=root / "data/raw", production=True, write=True,
        fragment_path=small / "review_inputs/facility_name_fragments.csv",
        pilot_dir=small / "v6",
        camp_decisions_path=small / "review_inputs/camp_east_v6_decisions.csv",
        fragment_review_path=small / "review_inputs/facility_name_fragment_candidates.csv",
        review_approval_path=small / "review_inputs/facility_name_fragment_review_approval.json",
        link_root=root, output_path=output,
    )
    if code != 0 or screen.get("technical_status") != "PASS":
        raise ValueError(f"facility screen failed: {screen}")
    paths = {
        "panel": small / "detention_roster_facility_snapshot_panel.csv",
        "pairs": output / "award_facility_pairs.csv",
        "screen_receipt": output / "verification.json",
        "comparison": root / "outputs/chart_1/comparison_source_rows.csv",
    }
    frozen = {**statistics.FROZEN_HASHES,
              "panel": "24fb15db3a73d51d0c39068ba2764b60c15247336cd016f88c8c74ffcc2dc19b",
              "pairs": "152e33621b144b0b64d412c8c917b8d2d300fc59d52848b75b72f19cdca3f38f",
              "screen_receipt": "19c57917839429a6868219c86e240ebf05beae56637ccea2c0b0c2e46ff8ef8c"}
    code, report = statistics.execute(paths=paths, output=output, frozen_hashes=frozen,
                                      strict=False, write=True, link_root=root)
    if code != 0 or report.get("status") not in {"PASS", "WARN"}:
        raise ValueError(f"facility statistics failed: {report}")
    return screen, report


def build_figure_b(root: Path) -> dict:
    output = root / "outputs/figure_b"
    with TemporaryDirectory(prefix=".figure-b-build-", dir=root / "outputs") as temporary:
        stage = Path(temporary) / "new"
        report = prepare_figure_b(
            root, stage,
            panel_path=root / SMALL / "detention_roster_facility_snapshot_panel.csv",
            rulebook_path=root / "docs/semantic_rulebook.md",
        )
        plot_figure_b(stage / "figure_b_data.csv", stage)
        names = ("figure_b_data.csv", "figure_b.png", "figure_b_mobile.png",
                 "figure_b.svg", "figure_b_mobile.svg", "figure_b.html")
        for name in names:
            if not (stage / name).is_file() or not (stage / name).stat().st_size:
                raise ValueError(f"missing Figure B output: {name}")
        receipt = {"technical_status": "PASS", "interpretation_status": "WARN",
                   "analysis": report, "output_sha256": {name: sha256(stage / name) for name in names}}
        (stage / "verification.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        previous = Path(temporary) / "previous"
        try:
            if output.exists():
                os.replace(output, previous)
            os.replace(stage, output)
        except BaseException:
            if previous.exists() and not output.exists():
                os.replace(previous, output)
            raise
    return receipt


def run(*, offline: bool = False, strict_warnings: bool = False) -> int:
    manifest = ROOT / "data/manifest.csv"
    inputs = (verify_inputs if offline else fetch_inputs)(ROOT, manifest)
    print(f"PASS: {inputs['verified']} input files match the frozen manifest", flush=True)
    mutable = ("chart_1", "chart_2", "facility_name_screen", "figure_b")
    with TemporaryDirectory(prefix=".release-output-backup-", dir=ROOT) as temporary:
        backup = Path(temporary)
        for name in mutable:
            existing = ROOT / "outputs" / name
            if existing.exists():
                if existing.is_symlink() or not existing.is_dir():
                    raise ValueError(f"unsafe output directory: {name}")
                shutil.copytree(existing, backup / name, symlinks=True)
        try:
            chart_1 = build_chart_1(ROOT)
            chart_2 = build_chart_2(ROOT)
            screen, stats = build_facility_screen(ROOT)
            figure_b = build_figure_b(ROOT)
            checked = verify_outputs(ROOT, ROOT / "data/output_checks.json")
        except BaseException:
            for name in mutable:
                current = ROOT / "outputs" / name
                if current.exists():
                    if current.is_symlink() or not current.is_dir():
                        raise ValueError(f"cannot restore unsafe output directory: {name}")
                    shutil.rmtree(current)
                if (backup / name).exists():
                    os.replace(backup / name, current)
            raise
    print(f"PASS: {checked} stable released output hashes match the reviewed copy", flush=True)
    warnings = [label for label, report in (("Chart 1", chart_1), ("Chart 2", chart_2),
                                             ("facility screen", screen), ("Figure B", figure_b))
                if report.get("interpretation_status") == "WARN"]
    if stats.get("status") == "WARN":
        warnings.append("facility statistics")
    if warnings:
        print("WARN: interpretation limits remain in " + ", ".join(warnings), flush=True)
    return 1 if strict_warnings and warnings else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="Require every frozen input locally.")
    parser.add_argument("--strict-warnings", action="store_true",
                        help="Return 1 after checks when interpretation warnings remain.")
    args = parser.parse_args()
    try:
        return run(offline=args.offline, strict_warnings=args.strict_warnings)
    except (ValueError, OSError, KeyError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
