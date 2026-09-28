"""Compare frozen File B and File C obligations and gross outlay checkpoints.

Read build() first. Source rows retain their physical ZIP/member/line pointers.
The reported difference is an accounting comparison, not an attribution.
"""
from __future__ import annotations

from collections import defaultdict
import csv
from decimal import Decimal, InvalidOperation
from io import TextIOWrapper
import json
from pathlib import Path
import zipfile

from scripts.prepare_chart_data import ACCOUNTS, file_sha256, local_path, stream_sha256
from scripts.prepare_comparison_data import DOWN_FIELD, verify_inputs


PROJECT = Path(__file__).resolve().parents[1]
JOBS = (("DHS_FY2025P04_ab", "B", 2025, 4),
        ("DHS_FY2025P12_ab", "B", 2025, 12),
        ("DHS_FY2026P10_ab", "B", 2026, 10),
        ("DHS_FY2025P12_c", "C", 2025, 12),
        ("DHS_FY2026P10_c", "C", 2026, 10))
DIMENSIONS = ("treasury_account_symbol", "program_activity_reporting_key",
              "program_activity_code", "object_class_code",
              "direct_or_reimbursable_funding_source", "disaster_emergency_fund_code")
OUTLAY = "gross_outlay_amount_FYB_to_period_end"
OBLIGATION = "transaction_obligated_amount"
INTERVALS = ("feb_sep_2025", "oct_2025_jul_2026")
SOURCE_FIELDS = ("layer", "component", "submission_period", "federal_account_symbol",
                 *DIMENSIONS, "award_unique_key", "obligation", "outlay",
                 "source_row_id", "source_zip_path", "source_member", "source_line_number",
                 "source_url")
TABLE_FIELDS = ("measure", "interval", "account", "object_class", "file_b",
                "file_b_status", "file_c", "file_c_status", "b_minus_c", "c_share_of_b")
UNMATCHED_FIELDS = ("side", "account", "component", *DIMENSIONS,
                    "award_unique_key", "row_count", "reported_outlay")


def amount(value: str, row_id: str) -> Decimal | None:
    if value is None or not value.strip():
        return None
    try:
        result = Decimal(value.strip())
    except InvalidOperation as exc:
        raise ValueError(f"invalid amount: {row_id}") from exc
    if not result.is_finite():
        raise ValueError(f"nonfinite amount: {row_id}")
    return result


def money(value: Decimal | None) -> str:
    return "" if value is None else f"{value:.2f}"


def read_job(project: Path, job: str, layer: str, year: int, endpoint: int) -> list[dict]:
    """Validate a receipt/member and retain all rows in the two federal accounts."""
    relative = f"data/raw/{job}"
    receipt = json.loads(local_path(project, f"{relative}/acquisition_receipt.json").read_text())
    requested = receipt["requested"]
    filters = requested["filters"]
    expected_types = (["account_balances", "object_class_program_activity"] if layer == "B"
                      else ["award_financial"])
    if (requested.get("account_level") != "treasury_account" or
            requested.get("file_format") != "csv" or str(filters.get("agency")) != "63" or
            str(filters.get("fy")) != str(year) or filters.get("period") != endpoint or
            sorted(filters.get("submission_types", [])) != expected_types):
        raise ValueError(f"source request differs from frozen scope: {job}")
    zip_relative = f"{relative}/{Path(receipt['zip_path']).name}"
    archive_path = local_path(project, zip_relative)
    if archive_path.stat().st_size != receipt["zip_bytes"] or file_sha256(archive_path) != receipt["zip_sha256"]:
        raise ValueError(f"ZIP receipt mismatch: {job}")
    rows = []
    seen_components = set()
    with zipfile.ZipFile(archive_path) as archive:
        members = receipt["members"]
        if sorted(m["member"] for m in members) != sorted(archive.namelist()):
            raise ValueError(f"ZIP member list mismatch: {job}")
        for member in members:
            name = member["member"]
            component = ("B" if layer == "B" else next((c for c in ("Contracts", "Assistance", "Unlinked")
                                                        if f"_{c}_AccountBreakdownByAward_" in name), ""))
            if layer == "B" and "_AccountBreakdownByPA-OC_" not in name:
                # The File A member is verified but intentionally not analyzed.
                if "_AccountBalances_" not in name:
                    raise ValueError(f"unexpected File A/B member: {name}")
                component = "A"
            if layer == "C" and not component:
                raise ValueError(f"unexpected File C member: {name}")
            seen_components.add(component)
            if archive.getinfo(name).file_size != int(member["bytes"]):
                raise ValueError(f"ZIP member size mismatch: {name}")
            with archive.open(name) as handle:
                if stream_sha256(handle) != member["sha256"]:
                    raise ValueError(f"ZIP member hash mismatch: {name}")
            if component == "A":
                continue
            with archive.open(name) as binary, TextIOWrapper(binary, encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle, strict=True)
                fields = reader.fieldnames or []
                required = {"submission_period", "federal_account_symbol", *DIMENSIONS, OUTLAY}
                required |= ({"obligations_incurred", DOWN_FIELD} if layer == "B" else
                             {OBLIGATION, "award_unique_key"})
                if len(fields) != len(set(fields)) or not required <= set(fields):
                    raise ValueError(f"missing or duplicate source columns: {name}")
                next_line = reader.line_num + 1
                for raw in reader:
                    line, next_line = next_line, reader.line_num + 1
                    if None in raw or any(v is None for v in raw.values()):
                        raise ValueError(f"malformed source row: {name}:{line}")
                    if raw["federal_account_symbol"] not in ACCOUNTS:
                        continue
                    period = raw["submission_period"]
                    if not period.startswith(f"FY{year}P") or not period[-2:].isdigit() or int(period[-2:]) > endpoint:
                        raise ValueError(f"unexpected reporting period: {name}:{line}")
                    if layer == "B" and period != f"FY{year}P{endpoint:02d}":
                        raise ValueError(f"unexpected File B checkpoint: {name}:{line}")
                    row_id = f"{job}:{name}:row:{line}"
                    if layer == "B":
                        incurred = amount(raw["obligations_incurred"], row_id)
                        reduction = amount(raw[DOWN_FIELD], row_id)
                        if (incurred is None) != (reduction is None):
                            raise ValueError(f"partial File B net obligation: {row_id}")
                        obligation = "" if incurred is None else money(incurred + reduction)
                    else:
                        obligation = raw[OBLIGATION]
                    rows.append({"layer": layer, "component": component,
                                 "submission_period": period,
                                 "federal_account_symbol": raw["federal_account_symbol"],
                                 **{field: raw[field] for field in DIMENSIONS},
                                 "award_unique_key": raw.get("award_unique_key", ""),
                                 "obligation": obligation, "outlay": raw[OUTLAY],
                                 "source_row_id": row_id, "source_zip_path": zip_relative,
                                 "source_member": name, "source_line_number": str(line),
                                 "source_url": receipt["download_url"]})
    expected_components = {"A", "B"} if layer == "B" else {"Contracts", "Assistance", "Unlinked"}
    if seen_components != expected_components:
        raise ValueError(f"missing source component: {job}")
    return rows


def _state(values: list[Decimal | None]) -> tuple[Decimal | None, str]:
    if not values:
        return None, "absent"
    numeric = [v for v in values if v is not None]
    if not numeric:
        return None, "all_blank"
    return sum(numeric, Decimal(0)), "partial_blank" if len(numeric) < len(values) else "numeric"


def _row(measure: str, interval: str, account: str, obj: str,
         grouped: dict) -> dict:
    b, bs = _state(grouped.get("B", []))
    c, cs = _state(grouped.get("C", []))
    # A numeric subtotal remains reportable when other rows are blank, but its
    # partial_blank status must travel with the difference and its interpretation.
    difference = (b or Decimal(0)) - (c or Decimal(0)) if bs != "all_blank" and cs != "all_blank" else None
    share = c / b * 100 if b not in (None, Decimal(0)) and c is not None else None
    return {"measure": measure, "interval": interval, "account": account,
            "object_class": obj, "file_b": money(b), "file_b_status": bs,
            "file_c": money(c), "file_c_status": cs,
            "b_minus_c": money(difference),
            "c_share_of_b": "" if share is None else f"{share:.4f}"}


def _unmatched(c_rows: list[dict]) -> list[dict]:
    # A blank award key cannot prove the same award persisted across checkpoints.
    buckets = defaultdict(lambda: {"p04": [], "p12": []})
    for row in c_rows:
        if row["submission_period"] not in {"FY2025P04", "FY2025P12"}:
            continue
        key = (row["federal_account_symbol"], row["component"],
               *(row.get(field, "") for field in DIMENSIONS), row.get("award_unique_key", ""))
        period = "p04" if row["submission_period"].endswith("P04") else "p12"
        buckets[key][period].append(amount(row["outlay"], row["source_row_id"]))
    result = []
    for key, periods in sorted(buckets.items()):
        unkeyed = not key[-1]
        if not unkeyed and periods["p04"] and periods["p12"]:
            continue
        for period in ("p04", "p12"):
            values = periods[period]
            if not values:
                continue
            total, status = _state(values)
            result.append({"side": ("unkeyed_" if unkeyed else "") + period + ("" if unkeyed else "_only"),
                           "account": key[0], "component": key[1],
                           **dict(zip(DIMENSIONS, key[2:-1])),
                           "award_unique_key": key[-1], "row_count": str(len(values)),
                           "reported_outlay": money(total), "value_status": status})
    return result


def summarize(b_rows: list[dict], c_rows: list[dict]) -> dict:
    """Produce three tables and the checkpoint exception diagnostic from rows."""
    keys = [r["source_row_id"] for r in (*b_rows, *c_rows)]
    if any(not key for key in keys) or len(keys) != len(set(keys)):
        raise ValueError("blank or duplicate source row ID")
    grouped = defaultdict(lambda: {"B": [], "C": []})
    for row in (*b_rows, *c_rows):
        layer, period = row["layer"], row["submission_period"]
        if layer == "C" and period == "FY2026P01" and amount(row["obligation"], row["source_row_id"]) is not None:
            raise ValueError("FY2026 P01 has numeric File C obligations; resolve P02 overlap")
        if layer == "B" and period not in {"FY2025P04", "FY2025P12", "FY2026P10"}:
            raise ValueError(f"unexpected File B period: {period}")
        for measure, field in (("obligations", "obligation"), ("gross_outlays", "outlay")):
            if measure == "obligations" and layer == "C":
                selected = (period.startswith("FY2025P") and 5 <= int(period[-2:]) <= 12 or
                            period.startswith("FY2026P") and 2 <= int(period[-2:]) <= 10)
                multiplier = 1
            else:
                selected = period in {"FY2025P04", "FY2025P12", "FY2026P10"}
                multiplier = -1 if period == "FY2025P04" else 1
            if not selected:
                continue
            interval = INTERVALS[0] if period.startswith("FY2025") else INTERVALS[1]
            value = amount(row[field], row["source_row_id"])
            if value is not None:
                value *= multiplier
            for acct in (row["federal_account_symbol"], "combined"):
                for obj in (row["object_class_code"], "(all)"):
                    grouped[(measure, interval, acct, obj)][layer].append(value)
    rows = [_row(*key, values) for key, values in sorted(grouped.items())]
    classes = [r for r in rows if r["object_class"] != "(all)"]
    intervals = [r for r in rows if r["object_class"] == "25.4" and r["account"] == "combined"]
    measures = []
    for measure in ("obligations", "gross_outlays"):
        parts = [r for r in intervals if r["measure"] == measure]
        b = sum((Decimal(r["file_b"]) for r in parts if r["file_b"]), Decimal(0))
        c = sum((Decimal(r["file_c"]) for r in parts if r["file_c"]), Decimal(0))
        measures.append({"measure": measure, "window": "feb_2025_jul_2026", "file_b": money(b),
                         "file_c": money(c), "b_minus_c": money(b-c),
                         "c_share_of_b": "" if b == 0 else f"{c/b*100:.4f}",
                         "file_c_status": "partial_blank" if any(r["file_c_status"] == "partial_blank" for r in parts) else "numeric"})
    offsets = []
    for measure in ("obligations", "gross_outlays"):
        for interval in INTERVALS:
            subset = [r for r in classes if r["measure"] == measure and r["interval"] == interval
                      and r["account"] == "combined"]
            target = next(r for r in subset if r["object_class"] == "25.4")
            denominator = Decimal(target["b_minus_c"]) if target["b_minus_c"] else Decimal(0)
            others = [r for r in subset if r["object_class"] != "25.4"]
            signed = [Decimal(r["b_minus_c"]) for r in others if r["b_minus_c"]]
            negative = -sum((v for v in signed if v < 0), Decimal(0))
            positive = sum((v for v in signed if v > 0), Decimal(0))
            plausible = [r for r in others if (r["object_class"].startswith("25.") or
                                                  r["object_class"] in {"26.0", "31.0"}) and r["b_minus_c"]]
            plausible_negative = -sum((Decimal(r["b_minus_c"]) for r in plausible
                                      if Decimal(r["b_minus_c"]) < 0), Decimal(0))
            offsets.append({"measure": measure, "interval": interval,
                            "gap_25_4": target["b_minus_c"],
                            "positive_other_classes": money(positive),
                            "negative_other_classes": money(negative),
                            "net_other_classes": money(positive-negative),
                            "negative_review_set": money(plausible_negative),
                            "all_offset_pct": "" if denominator <= 0 else f"{negative/denominator*100:.4f}",
                            "review_set_offset_pct": "" if denominator <= 0 else f"{plausible_negative/denominator*100:.4f}",
                            "unresolved_class_rows": sum(not r["b_minus_c"] for r in others)})
    return {"measures": measures, "classes": classes, "intervals": intervals,
            "unmatched": _unmatched(c_rows),
            "account_intervals": [r for r in rows if r["object_class"] == "25.4"],
            "offsets": offsets, "all_rows": rows}


def build(project: Path = PROJECT, output: Path | None = None) -> dict:
    """Verify frozen sources, calculate, reconcile, then write review tables."""
    verified = verify_inputs(project)
    b_rows, c_rows = [], []
    for job, layer, year, endpoint in JOBS:
        target = b_rows if layer == "B" else c_rows
        target.extend(read_job(project, job, layer, year, endpoint))
    result = summarize(b_rows, c_rows)
    totals = {r["measure"]: r for r in result["measures"]}
    if totals["obligations"]["file_b"] != "5907357331.34" or totals["obligations"]["file_c"] != "3136530747.79":
        raise ValueError("25.4 Chart 1 check requires object-class selection; see verification")
    # The accounting class union must reconstruct each independent account
    # subtotal on both source sides, including signed baseline subtraction.
    for total in (r for r in result["all_rows"] if r["object_class"] == "(all)"):
        parts = [r for r in result["classes"] if r["measure"] == total["measure"]
                 and r["interval"] == total["interval"] and r["account"] == total["account"]]
        for field in ("file_b", "file_c"):
            reconstructed = sum((Decimal(r[field]) for r in parts if r[field]), Decimal(0))
            if money(reconstructed) != total[field]:
                raise ValueError(f"object-class reconciliation failed: {total['measure']} {total['interval']} {total['account']} {field}")
    output = output or project / "outputs/bc_gap"
    output.mkdir(parents=True, exist_ok=True)
    for name, table, fields in (("measure_comparison.csv", result["measures"],
                                 ("measure", "window", "file_b", "file_c", "b_minus_c", "c_share_of_b", "file_c_status")),
                                ("object_class_differences.csv", result["classes"], TABLE_FIELDS),
                                ("interval_stability.csv", result["account_intervals"], TABLE_FIELDS),
                                ("offset_summary.csv", result["offsets"],
                                 ("measure", "interval", "gap_25_4", "positive_other_classes",
                                  "negative_other_classes", "net_other_classes", "negative_review_set",
                                  "all_offset_pct", "review_set_offset_pct", "unresolved_class_rows")),
                                ("unmatched_checkpoints.csv", result["unmatched"], (*UNMATCHED_FIELDS, "value_status")),
                                ("source_rows.csv", b_rows + c_rows, SOURCE_FIELDS)):
        with (output / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(table)
    checks = {"status": "WARN", "calculation_status": "PASS", "manifest_files_verified": len(verified),
              "source_members_verified": "all listed receipt members",
              "object_class_reconciliation": "PASS", "chart_1_obligation_reproduction": "PASS",
              "file_b_rows": len(b_rows), "file_c_rows": len(c_rows),
              "script_sha256": file_sha256(Path(__file__)),
              "output_sha256": {name: file_sha256(output / name) for name in (
                  "measure_comparison.csv", "object_class_differences.csv", "interval_stability.csv",
                  "offset_summary.csv", "unmatched_checkpoints.csv", "source_rows.csv")},
              "limitations": ["Frozen extracts cannot establish late reporting or misclassification.",
                              "FY2025 P04 File B was retrieved after the P12 endpoint.",
                              "File C includes blank outlay and obligation amounts; sums use reported numeric values only."]}
    (output / "verification.json").write_text(json.dumps(checks, indent=2) + "\n")
    return result


if __name__ == "__main__":
    build()
