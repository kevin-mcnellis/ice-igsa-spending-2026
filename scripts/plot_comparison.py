"""Plot the two OC 25.4 totals; source selection happens before this stage.

Read the two summary rows, subtract File C from net File B for the callout,
and draw both bars on one signed dollar scale. Decimal preserves the inputs
and subtraction; floating-point numbers are used only for drawing positions.
"""

import argparse
import csv
from decimal import Decimal, InvalidOperation
import math
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / ".cache/matplotlib"))
import matplotlib

matplotlib.use("Agg")
from matplotlib.figure import Figure
try:
    from scripts import chart_style as style
except ModuleNotFoundError:  # Preserve direct script execution.
    import chart_style as style


BAR_IDS = ("file_b_net", "file_c")
FIELDS = {"bar_id", "label", "amount", "source_row_count", "blank_row_count"}


def read_totals(summary_path: Path) -> list[dict]:
    """Require both documented totals and reject blanks instead of making zeros."""
    with summary_path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if len(reader.fieldnames or []) != len(FIELDS) or set(reader.fieldnames or []) != FIELDS:
            raise ValueError("comparison_totals.csv must have the five documented columns")
        rows = list(reader)
    if len(rows) != 2 or {row["bar_id"] for row in rows} != set(BAR_IDS):
        raise ValueError("comparison_totals.csv must contain file_b_net and file_c exactly once")
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


compact_money = style.money

def plot(summary_path: Path, output_dir: Path, *, mobile=False) -> dict[str, str]:
    """Read only comparison_totals.csv and save the SVG and PNG comparison."""
    rows = read_totals(summary_path)
    amounts = [float(row["amount"]) for row in rows]
    difference = rows[0]["amount"] - rows[1]["amount"]
    low, high = min(0, *amounts), max(0, *amounts)
    span = high - low or 1
    limits = (low - (0.08 * span if low < 0 else 0), high + (0.08 * span if high > 0 else 0.05 * span))
    if not all(math.isfinite(value) for value in limits):
        raise ValueError("summary amounts exceed the supported plotting range")
    background, ink = style.BACKGROUND, style.INK
    accent, secondary = style.ACCENT, style.SECONDARY
    with matplotlib.rc_context(style.rc_params('file-b-c-comparison-25-4')):
        title = "ICE’s Award Disclosures Total About Half Its Facility Obligations"
        subtitle = "Obligations for facility operations and maintenance, reporting periods February 2025–July 2026"
        notes = [
            "The two totals have not been matched record by record. The difference is not an estimate of unreported spending or of payments to state and local governments.",
            "Account records subtract reductions to earlier years' commitments. Award records include some entries with no identified award.",
            "Obligations are commitments to spend, not cash payments. Records with a blank amount are left out of the totals, not counted as zero.",
            "Source: USAspending · Object class 25.4 · Accounts 070-0540 and 070-0545",
        ]
        figure, axis, available = style.page(title, subtitle, notes, mobile=mobile,
                                             body_height=225 if mobile else 195)
        axis.patch.set_gid("comparison-background")
        bars = axis.barh(range(2), amounts, height=0.56 if mobile else 0.42, color=(style.PRIMARY_BAR, style.SECONDARY_BAR), zorder=3)
        for bar, row in zip(bars, rows):
            bar.set_gid(f"bar-{row['bar_id']}")
            amount = row["amount"]
            inside = abs(float(amount)) >= 0.26 * span
            offset = (-10 if amount > 0 else 10) if inside else (-9 if amount < 0 else 9)
            align = ("right" if amount > 0 else "left") if inside else ("right" if amount < 0 else "left")
            annotation = axis.annotate(compact_money(amount).replace(' billion', '\nbillion') if mobile else compact_money(amount), (float(amount), bar.get_y() + bar.get_height() / 2),
                                       xytext=(offset, 0), textcoords="offset points",
                                       ha=align, va="center", size=style.VALUE_SIZE, weight="bold",
                                       color="white" if inside else ink)
            annotation.set_gid(f"value-{row['bar_id']}")
        labels = ["ICE's account records (File B)", "ICE's award records (File C)"]
        axis.set_yticks([])
        for index, label in enumerate(labels):
            axis.text(0, index - (0.37 if mobile else 0.32), style.wrap_text(label, available, style.ROW_SIZE), transform=axis.get_yaxis_transform(),
                      fontsize=style.ROW_SIZE, va="bottom", bbox=dict(facecolor=background, edgecolor="none", pad=1))
        axis.set_ylim(2.30, -0.65 if mobile else -0.60)
        axis.set_xlim(*limits)
        axis.set_xticks([])
        for spine in axis.spines.values():
            spine.set_visible(False)
        # The bracket spans the two actual bar ends; it is not a third bar.
        axis.plot([amounts[1], amounts[0]], [1.55, 1.55], color=accent,
                  linewidth=2.4, zorder=4)[0].set_gid("gap-span")
        for index, amount in enumerate(amounts):
            axis.plot([amount, amount], [index + 0.24, 1.55], color=accent,
                      linewidth=1.2, linestyle=(0, (3, 3)), zorder=2)
            axis.plot([amount, amount], [1.48, 1.62], color=accent, linewidth=2.4, zorder=4)
        axis.text((amounts[0] + amounts[1]) / 2, 1.88, f"{compact_money(difference)} difference".replace(" billion difference", " billion\ndifference") if mobile else f"{compact_money(difference)} difference",
                  ha="center", va="center", size=16, weight="bold",
                  color=accent).set_gid("accounting-difference")
        output_dir.mkdir(parents=True, exist_ok=True)
        paths = {extension: str(output_dir / f"obligations_comparison_25_4{'_mobile' if mobile else ''}.{extension}") for extension in ("svg", "png")}
        figure.savefig(paths["svg"], metadata={"Date": None, "Creator": "File C blog chart", "Description": " ".join(notes)})
        figure.savefig(paths["png"], dpi=180, metadata={"Software": "File C blog chart"})
    if not mobile:
        plot(summary_path, output_dir, mobile=True)
        description = f'{title}. {subtitle}. File B {compact_money(rows[0]["amount"])}; File C {compact_money(rows[1]["amount"])}; difference {compact_money(difference)}. ' + ' '.join(notes)
        style.web_preview(output_dir, 'obligations_comparison_25_4', title, description, 'comparison_totals.csv')
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary_path", type=Path)
    parser.add_argument("output_dir", type=Path)
    arguments = parser.parse_args()
    plot(arguments.summary_path, arguments.output_dir)
