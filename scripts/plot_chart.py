"""Draw three bars from chart_totals.csv; this script does no source analysis.

Read in order: validate the three summary rows, draw on one signed dollar
scale, then save an SVG and a PNG. Amounts remain exact Decimals for labels;
only bar positions use floating-point numbers, as required by Matplotlib.
"""

import argparse
import csv
from decimal import Decimal, InvalidOperation
import math
import os
from pathlib import Path
import textwrap

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / ".cache/matplotlib"))
import matplotlib

matplotlib.use("Agg")
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter, MaxNLocator


BAR_IDS = ("all_file_c", "major_private_prison_contractors", "state_and_local_governments")
FIELDS = {"bar_id", "label", "amount", "source_row_count", "blank_row_count"}


def read_totals(summary_path: Path) -> list[dict]:
    """Reject incomplete summaries rather than turning missing values into zero."""
    with summary_path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if len(reader.fieldnames or []) != len(FIELDS) or set(reader.fieldnames or []) != FIELDS:
            raise ValueError("chart_totals.csv must have the five documented columns")
        rows = list(reader)
    if len(rows) != 3 or {row["bar_id"] for row in rows} != set(BAR_IDS):
        raise ValueError("chart_totals.csv must contain each of the three bar IDs exactly once")
    for row in rows:
        if None in row or any(value is None for value in row.values()) or not row["label"].strip():
            raise ValueError(f"incomplete or malformed summary row: {row['bar_id']}")
        try:
            amount = Decimal(row["amount"])
            count, blanks = int(row["source_row_count"]), int(row["blank_row_count"])
        except (InvalidOperation, ValueError) as error:
            raise ValueError(f"invalid amount or row count: {row['bar_id']}") from error
        if not amount.is_finite() or not math.isfinite(float(amount)) or not 0 <= blanks <= count:
            raise ValueError(f"nonfinite amount or impossible row count: {row['bar_id']}")
        row["amount"] = amount
    return sorted(rows, key=lambda row: BAR_IDS.index(row["bar_id"]))


def plot(summary_path: Path, output_dir: Path) -> dict[str, str]:
    """Read only the summary CSV and write obligations_chart.svg and .png."""
    rows = read_totals(summary_path)
    amounts = [float(row["amount"]) for row in rows]
    low, high = min(0, *amounts), max(0, *amounts)
    span = high - low or 1
    largest = max(abs(low), high)
    divisor, suffix = (1e9, "B") if largest >= 1e9 else ((1e6, "M") if largest >= 1e6 else (1, ""))
    background, ink = "#F7F5F1", "#26221B"
    style = {"font.family": "DejaVu Sans", "font.size": 11, "text.color": ink,
             "svg.fonttype": "path", "svg.hashsalt": "file-c-obligation-bars",
             "axes.labelcolor": ink, "xtick.color": ink, "ytick.color": ink}
    with matplotlib.rc_context(style):
        figure = Figure(figsize=(12.8, 7.2), facecolor=background)
        axis = figure.add_axes((0.32, 0.40, 0.63, 0.37), facecolor=background)
        bars = axis.barh(range(3), amounts, height=0.46, color=("#6E6759", "#BF3B14", "#56758E"), zorder=3)
        for bar, row in zip(bars, rows):
            bar.set_gid(f"bar-{row['bar_id']}")
            amount = row["amount"]
            label = f"{'-' if amount < 0 else ''}${abs(amount):,.2f}"
            axis.annotate(label, (float(amount), bar.get_y() + bar.get_height() / 2),
                          xytext=(-7 if amount < 0 else 7, 0), textcoords="offset points",
                          ha="right" if amount < 0 else "left", va="center", weight="bold")
        axis.set_yticks(range(3), [textwrap.fill(row["label"], 29) for row in rows])
        axis.set_ylim(2.6, -0.6)
        axis.set_xlim(low - (0.40 * span if low < 0 else 0), high + (0.40 * span if high > 0 else 0.05 * span))
        axis.xaxis.set_major_locator(MaxNLocator(nbins=5))
        axis.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{'-' if value < 0 else ''}${abs(value) / divisor:g}{suffix}"))
        axis.tick_params(axis="y", length=0, pad=14)
        axis.tick_params(axis="x", length=0, pad=8)
        axis.set_xlabel("Signed transaction obligations · US dollars · common linear scale", labelpad=14, fontsize=10)
        axis.grid(axis="x", color="#DDD8CC", linewidth=0.7, zorder=0)
        axis.axvline(0, color=ink, linewidth=1)
        for spine in axis.spines.values():
            spine.set_visible(False)
        figure.text(0.045, 0.945, "ICE ACCOUNTS · FILE C", color="#A83413", size=11, weight="bold")
        figure.text(0.045, 0.89, "Who appears in File C obligations?", size=23, weight="bold")
        figure.text(0.045, 0.845, "FY2025 + FY2026 through July · October 2024–July 2026 · Accounts 070-0540 and 070-0545", size=11)
        notes = [
            "The two name-screen bars are subsets, may overlap, and do not sum to the total.",
            "Government name matches are not verified government recipients; private-company matches are included.",
            "Selected contractor names and parent names do not identify complete corporate families.",
            "Blank obligations are excluded, not zero. Signed amounts retain negative adjustments.",
            "File C may omit reportable obligations; absence here does not establish that no payment occurred.",
            "Source: frozen USAspending File C downloads; source links and dates are in data/source_manifest.csv.",
            "Exploratory chart for draft review; no administration or facility-spending attribution.",
        ]
        for index, note in enumerate(notes):
            figure.text(0.045, 0.245 - index * 0.029, note, fontsize=10)
        output_dir.mkdir(parents=True, exist_ok=True)
        paths = {extension: str(output_dir / f"obligations_chart.{extension}") for extension in ("svg", "png")}
        figure.savefig(paths["svg"], metadata={"Date": None, "Creator": "File C blog chart"})
        figure.savefig(paths["png"], dpi=180, metadata={"Software": "File C blog chart"})
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary_path", type=Path)
    parser.add_argument("output_dir", type=Path)
    arguments = parser.parse_args()
    plot(arguments.summary_path, arguments.output_dir)
