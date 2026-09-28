"""Prepare the first chart: File B after prior-year reductions versus File C.

Read prepare() first, then build_tables(). The scope is object class 25.4 in
accounts 070-0540/0545 from February 2025 through July 2026. File B subtracts
the January 2025 checkpoint from September 2025, then adds July 2026.
File C sums the matching reporting-period flows.
The result is a reported-total comparison, not an estimate of IGSA spending.
"""
from __future__ import annotations

from collections import defaultdict
import csv
from decimal import Decimal
from io import TextIOWrapper
import json
from pathlib import Path
import re
import zipfile

from scripts.prepare_chart_data import (
    ACCOUNTS, JOBS, amount_or_blank, file_sha256, local_path, read_job, stream_sha256,
)


DOWN_FIELD = "deobligations_or_recoveries_or_refunds_from_prior_year"
DOWN_COMPONENTS = (
    "USSGL487100_downward_adj_prior_year_unpaid_undeliv_orders_oblig",
    "USSGL497100_downward_adj_prior_year_unpaid_deliv_orders_oblig",
    "USSGL487200_downward_adj_prior_year_prepaid_undeliv_order_oblig",
    "USSGL497200_downward_adj_of_prior_year_paid_deliv_orders_oblig",
)
TRANSFER_FIELDS = (
    "USSGL483100_undelivered_orders_obligations_transferred_unpaid",
    "USSGL493100_delivered_orders_obligations_transferred_unpaid",
    "USSGL483200_undeliv_orders_oblig_transferred_prepaid_advanced",
)
KEY_FIELDS = (
    "fiscal_year", "federal_account_symbol", "treasury_account_symbol",
    "program_activity_reporting_key", "program_activity_code", "object_class_code",
    "direct_or_reimbursable_funding_source", "disaster_emergency_fund_code",
)
B_FIELDS = ("obligations_incurred", DOWN_FIELD, *DOWN_COMPONENTS, *TRANSFER_FIELDS)
SOURCE_FIELDS = (
    "source_layer", "source_row_id", "source_zip_path", "source_member",
    "source_line_number", "source_file_path", "source_url", "component",
    "submission_period", "endpoint_period", *KEY_FIELDS, *B_FIELDS,
    "transaction_obligated_amount", "award_unique_key", "award_id_piid",
    "parent_award_id_piid", "award_id_fain", "award_id_uri", "recipient_uei",
    "recipient_name", "usaspending_permalink", "last_modified_date",
    "calculation_role", "calculation_multiplier", "file_b_reported_net",
    "weighted_obligations_incurred", "weighted_prior_year_adjustments",
    "comparison_amount", "comparison_value_status",
)
BRIDGE_FIELDS = (
    "file_b_bridge_status", "file_b_baseline_status", "file_b_endpoint_status",
    "file_b_baseline_obligations_incurred", "file_b_baseline_prior_year_adjustments",
    "file_b_baseline_net", "file_b_endpoint_obligations_incurred",
    "file_b_endpoint_prior_year_adjustments", "file_b_endpoint_net",
    "file_b_baseline_row_count", "file_b_endpoint_row_count",
)
AMOUNT_FIELDS = (
    "file_b_status", "file_c_status", "file_b_obligations_incurred",
    "file_b_prior_year_adjustments", "file_b_net", "file_c_numeric_obligations",
    "file_b_minus_file_c", "file_b_row_count", "file_b_numeric_row_count",
    "file_b_blank_row_count", "file_c_row_count", "file_c_numeric_row_count",
    "file_c_blank_row_count", *BRIDGE_FIELDS,
)
PERIOD_FIELDS = ("fiscal_year", "endpoint_period", "federal_account_symbol", *AMOUNT_FIELDS)
ACCOUNTING_FIELDS = (*KEY_FIELDS, "endpoint_period", *AMOUNT_FIELDS)
TOTAL_FIELDS = ("bar_id", "label", "amount", "source_row_count", "blank_row_count")
LABELS = (
    ("file_b_net", "File B — after prior-year reductions"),
    ("file_c", "File C — reported transaction obligations"),
)
BASELINE_JOB = ("DHS_FY2025P04_ab", 2025, 4)


def verify_inputs(project_dir: Path) -> list[dict]:
    """Check ten local ZIP/receipt files, including the required January baseline."""
    with (project_dir / "data/comparison_source_manifest.csv").open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, strict=True)
        required = {"path", "source_url", "retrieved_at", "sha256", "bytes", "role"}
        fields = reader.fieldnames or []
        if len(fields) != len(set(fields)) or not required <= set(fields):
            raise ValueError("invalid comparison manifest columns")
        records = list(reader)
    paths = [record["path"] for record in records]
    if len(paths) != 10 or len(set(paths)) != 10:
        raise ValueError("comparison manifest must contain ten distinct files")
    expected = set()
    jobs = [BASELINE_JOB[0], *(job for c_job, _, _ in JOBS
                              for job in (c_job, c_job.removesuffix("_c") + "_ab"))]
    for job in jobs:
        receipt_path = f"data/raw/{job}/acquisition_receipt.json"
        receipt = json.loads(local_path(project_dir, receipt_path).read_text(encoding="utf-8"))
        expected.update((receipt_path, f"data/raw/{job}/{Path(receipt['zip_path']).name}"))
    if set(paths) != expected:
        raise ValueError("comparison manifest names do not match the five source jobs")
    for record in records:
        path = local_path(project_dir, record["path"])
        if path.stat().st_size != int(record["bytes"]) or file_sha256(path) != record["sha256"]:
            raise ValueError(f"comparison input hash/size mismatch: {record['path']}")
    return [{**record, "hash_status": "verified"} for record in records]


def pya_columns(fields: list[str]) -> list[str]:
    """Record whether the source exposes the prior-year-adjustment category."""
    return [field for field in fields if field.lower() in {
        "pya", "prior_year_adjustment", "prior_year_adjustment_code", "prior_year_adjustment_type",
    }]


def read_b_job(project_dir: Path, job: str, year: int, endpoint: int):
    """Verify both A/B members; select the requested File B checkpoint in 25.4."""
    relative = f"data/raw/{job}"
    receipt = json.loads(local_path(project_dir, f"{relative}/acquisition_receipt.json").read_text(encoding="utf-8"))
    requested, filters = receipt.get("requested", {}), receipt.get("requested", {}).get("filters", {})
    if not (requested.get("account_level") == "treasury_account" and requested.get("file_format") == "csv"
            and str(filters.get("agency")) == "63" and str(filters.get("fy")) == str(year)
            and filters.get("period") == endpoint
            and sorted(filters.get("submission_types", [])) == ["account_balances", "object_class_program_activity"]):
        raise ValueError(f"wrong File B receipt scope: {job}")
    zip_relative = f"{relative}/{Path(receipt['zip_path']).name}"
    path = local_path(project_dir, zip_relative)
    if path.stat().st_size != int(receipt["zip_bytes"]) or file_sha256(path) != receipt["zip_sha256"]:
        raise ValueError(f"File B ZIP hash/size mismatch: {zip_relative}")
    rows, checks, layers = [], [], set()
    with zipfile.ZipFile(path) as archive:
        names = [item["member"] for item in receipt["members"]]
        if len(names) != len(set(names)) or sorted(names) != sorted(archive.namelist()):
            raise ValueError(f"File B receipt and ZIP members differ: {job}")
        for item in receipt["members"]:
            name = item["member"]
            match = re.fullmatch(rf"FY{year}P01-P{endpoint:02d}_All_TAS_(AccountBalances|AccountBreakdownByPA-OC)_[^/]+\.csv", name)
            if not match:
                raise ValueError(f"unexpected A/B member: {name}")
            layer = "A" if match[1] == "AccountBalances" else "B"
            layers.add(layer)
            if archive.getinfo(name).file_size != int(item["bytes"]):
                raise ValueError(f"member byte-size mismatch: {name}")
            with archive.open(name) as handle:
                digest = stream_sha256(handle)
            if digest != item["sha256"]:
                raise ValueError(f"member SHA-256 mismatch: {name}")
            check = {"source_id": f"{job}:{name}", "zip_path": zip_relative, "member": name,
                     "layer": layer, "bytes": item["bytes"], "sha256": digest,
                     "hash_status": "verified", "selected_rows": 0}
            checks.append(check)
            if layer == "A":
                continue  # Verified source member, deliberately unused in the analysis.
            with archive.open(name) as binary, TextIOWrapper(binary, encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle, strict=True)
                fields = reader.fieldnames or []
                required = set(KEY_FIELDS[1:]) | set(B_FIELDS) | {"submission_period"}
                if len(fields) != len(set(fields)) or not required <= set(fields):
                    raise ValueError(f"missing or duplicate File B columns: {name}")
                check["pya_columns"] = pya_columns(fields)
                next_line = reader.line_num + 1
                for row in reader:
                    line, next_line = next_line, reader.line_num + 1
                    if None in row or any(value is None for value in row.values()):
                        raise ValueError(f"malformed File B row: {name}:{line}")
                    if row["federal_account_symbol"] not in ACCOUNTS or row["object_class_code"] != "25.4":
                        continue
                    if row["submission_period"] != f"FY{year}P{endpoint:02d}":
                        raise ValueError(f"unexpected File B checkpoint: {name}:{line}")
                    rows.append({**row, "component": "B", "source_row_id": f"{job}:{name}:row:{line}",
                                 "source_zip_path": zip_relative, "source_member": name,
                                 "source_line_number": str(line), "source_file_path": f"{zip_relative}!{name}",
                                 "source_url": receipt["download_url"]})
                    check["selected_rows"] += 1
    if layers != {"A", "B"}:
        raise ValueError(f"missing A/B source component: {job}")
    return rows, checks


def observed_sum(rows: list[dict], field: str) -> str:
    """Return a sum only when at least one numeric value was observed."""
    values = [amount_or_blank(row.get(field, ""), row["source_row_id"]) for row in rows]
    numeric = [value for value in values if value is not None]
    return f"{sum(numeric, Decimal('0')):.2f}" if numeric else ""


def describe_group(rows: list[dict]) -> dict:
    """Keep missing groups and blank-only groups distinct from reported zeros."""
    b = [row for row in rows if row["source_layer"] == "B"]
    c = [row for row in rows if row["source_layer"] == "C"]
    b_net, c_amount = observed_sum(b, "comparison_amount"), observed_sum(c, "comparison_amount")
    b_blank = sum(row["comparison_value_status"] == "blank" for row in b)
    c_blank = sum(row["comparison_value_status"] == "blank" for row in c)
    baseline = [row for row in b if row["calculation_role"] == "baseline"]
    endpoint = [row for row in b if row["calculation_role"] == "endpoint"]
    needs_baseline = rows[0]["fiscal_year"] == "2025"
    bridge = ("both" if baseline and endpoint else "baseline_only" if baseline
              else "endpoint_only" if endpoint else "absent") if needs_baseline else "not_required"
    return {
        "file_b_status": "absent" if not b else "all_blank" if b_blank == len(b) else "numeric",
        "file_c_status": "absent" if not c else "all_blank" if c_blank == len(c) else "numeric",
        "file_b_obligations_incurred": observed_sum(b, "weighted_obligations_incurred"),
        "file_b_prior_year_adjustments": observed_sum(b, "weighted_prior_year_adjustments"),
        "file_b_net": b_net, "file_c_numeric_obligations": c_amount,
        "file_b_minus_file_c": f"{Decimal(b_net) - Decimal(c_amount):.2f}" if b_net and c_amount else "",
        "file_b_row_count": str(len(b)), "file_b_numeric_row_count": str(len(b) - b_blank),
        "file_b_blank_row_count": str(b_blank), "file_c_row_count": str(len(c)),
        "file_c_numeric_row_count": str(len(c) - c_blank), "file_c_blank_row_count": str(c_blank),
        "file_b_bridge_status": bridge,
        "file_b_baseline_status": ("numeric" if baseline else "absent") if needs_baseline else "not_required",
        "file_b_endpoint_status": "numeric" if endpoint else "absent",
        "file_b_baseline_obligations_incurred": observed_sum(baseline, "obligations_incurred"),
        "file_b_baseline_prior_year_adjustments": observed_sum(baseline, DOWN_FIELD),
        "file_b_baseline_net": observed_sum(baseline, "file_b_reported_net"),
        "file_b_endpoint_obligations_incurred": observed_sum(endpoint, "obligations_incurred"),
        "file_b_endpoint_prior_year_adjustments": observed_sum(endpoint, DOWN_FIELD),
        "file_b_endpoint_net": observed_sum(endpoint, "file_b_reported_net"),
        "file_b_baseline_row_count": str(len(baseline)), "file_b_endpoint_row_count": str(len(endpoint)),
    }


def build_tables(b_rows: list[dict], c_rows: list[dict]) -> dict:
    """Validate values, calculate each contribution, and sum by visible keys."""
    ids = [row["source_row_id"] for row in (*b_rows, *c_rows)]
    if any(not identifier for identifier in ids) or len(ids) != len(set(ids)):
        raise ValueError("blank or duplicate source row ID")
    traced, nonzero_transfers, blank_transfers = [], [], []
    for layer, rows in (("B", b_rows), ("C", c_rows)):
        for original in rows:
            row = dict(original)
            if row["federal_account_symbol"] not in ACCOUNTS or row["object_class_code"] != "25.4":
                raise ValueError(f"unexpected account/object class: {row['source_row_id']}")
            match = re.fullmatch(r"FY(2025|2026)P(\d{2})", row["submission_period"])
            if not match:
                raise ValueError(f"unexpected period: {row['source_row_id']}")
            year, period = int(match[1]), int(match[2])
            endpoint = 12 if year == 2025 else 10
            is_baseline = layer == "B" and year == 2025 and period == 4
            c_first_period = 5 if year == 2025 else 2
            if (layer == "B" and not is_baseline and period != endpoint) or (layer == "C" and not c_first_period <= period <= endpoint):
                raise ValueError(f"unexpected {layer} period {row['submission_period']}; P01 is included in P02, not added separately")
            if layer == "B":
                values = {field: amount_or_blank(row[field], row["source_row_id"]) for field in B_FIELDS}
                if any(values[field] is None for field in ("obligations_incurred", DOWN_FIELD, *DOWN_COMPONENTS)):
                    raise ValueError(f"blank File B amount/component: {row['source_row_id']}")
                if values[DOWN_FIELD] != sum((values[field] for field in DOWN_COMPONENTS), Decimal("0")):
                    raise ValueError(f"File B adjustment components do not reconcile: {row['source_row_id']}")
                if any(values[field] is None for field in TRANSFER_FIELDS):
                    blank_transfers.append(row["source_row_id"])
                if any(values[field] is not None and values[field] != 0 for field in TRANSFER_FIELDS):
                    nonzero_transfers.append(row["source_row_id"])
                # The public download already carries negative reductions.
                # Add that signed field; subtracting it would reverse the sign.
                reported_net = values["obligations_incurred"] + values[DOWN_FIELD]
                multiplier = -1 if is_baseline else 1
                amount = multiplier * reported_net
                row.update(calculation_role="baseline" if is_baseline else "endpoint",
                           calculation_multiplier=str(multiplier), file_b_reported_net=format(reported_net, "f"),
                           weighted_obligations_incurred=format(multiplier * values["obligations_incurred"], "f"),
                           weighted_prior_year_adjustments=format(multiplier * values[DOWN_FIELD], "f"))
            else:
                if row["component"] not in {"Contracts", "Assistance", "Unlinked"}:
                    raise ValueError(f"unexpected File C component: {row['source_row_id']}")
                amount = amount_or_blank(row["transaction_obligated_amount"], row["source_row_id"])
                row.update(calculation_role="period_flow", calculation_multiplier="1")
            row.update(source_layer=layer, fiscal_year=str(year), endpoint_period=f"FY{year}P{endpoint:02d}",
                       comparison_amount="" if amount is None else format(amount, "f"),
                       comparison_value_status="blank" if amount is None else "numeric")
            traced.append(row)

    if not any(row["calculation_role"] == "baseline" for row in traced):
        raise ValueError("missing usable FY2025P04 File B baseline; cannot assume a zero baseline")
    totals = []
    for layer, (bar_id, label) in zip(("B", "C"), LABELS):
        rows = [row for row in traced if row["source_layer"] == layer]
        amount = observed_sum(rows, "comparison_amount")
        if not amount:
            raise ValueError(f"File {layer} has no numeric selected obligations")
        totals.append({"bar_id": bar_id, "label": label, "amount": amount,
                       "source_row_count": str(len(rows)),
                       "blank_row_count": str(sum(r["comparison_value_status"] == "blank" for r in rows))})
    period_groups, key_groups = defaultdict(list), defaultdict(list)
    for row in traced:
        period_groups[(row["fiscal_year"], row["endpoint_period"], row["federal_account_symbol"])].append(row)
        key_groups[tuple(row.get(field, "") for field in KEY_FIELDS)].append(row)
    by_period = [{**dict(zip(PERIOD_FIELDS[:3], key)), **describe_group(rows)}
                 for key, rows in sorted(period_groups.items())]
    accounting_keys = [{**dict(zip(KEY_FIELDS, key)), "endpoint_period": rows[0]["endpoint_period"],
                        **describe_group(rows)} for key, rows in sorted(key_groups.items())]
    # Reconcile amounts and counts through both independently grouped tables.
    for grouped in (by_period, accounting_keys):
        for index, prefix, field in ((0, "file_b", "file_b_net"), (1, "file_c", "file_c_numeric_obligations")):
            amount = sum((Decimal(row[field]) for row in grouped if row[field]), Decimal("0"))
            count = sum(int(row[f"{prefix}_row_count"]) for row in grouped)
            blank = sum(int(row[f"{prefix}_blank_row_count"]) for row in grouped)
            if amount != Decimal(totals[index]["amount"]) or count != int(totals[index]["source_row_count"]) or blank != int(totals[index]["blank_row_count"]):
                raise ValueError("grouped amounts/counts do not reconcile to chart totals")
    return {
        "source_rows": traced, "totals": totals, "by_period": by_period, "accounting_keys": accounting_keys,
        "checks": {
            "grouped_output_reconciliation_status": "PASS", "file_b_adjustment_components_status": "PASS",
            "file_b_transfer_status": "WARN" if nonzero_transfers or blank_transfers else "PASS",
            "file_b_nonzero_transfer_rows": nonzero_transfers, "file_b_blank_transfer_rows": blank_transfers,
            "aggregate_difference": f"{Decimal(totals[0]['amount']) - Decimal(totals[1]['amount']):.2f}",
            "file_b_obligations_incurred": observed_sum([r for r in traced if r["source_layer"] == "B"], "weighted_obligations_incurred"),
            "file_b_prior_year_adjustments": observed_sum([r for r in traced if r["source_layer"] == "B"], "weighted_prior_year_adjustments"),
            "file_b_baseline_only_key_count": sum(r["file_b_bridge_status"] == "baseline_only" for r in accounting_keys),
            "file_b_endpoint_only_key_count": sum(r["file_b_bridge_status"] == "endpoint_only" for r in accounting_keys),
            "file_b_only_key_count": sum(r["file_c_status"] == "absent" for r in accounting_keys),
            "file_c_only_key_count": sum(r["file_b_status"] == "absent" for r in accounting_keys),
            "file_c_all_blank_key_count": sum(r["file_c_status"] == "all_blank" for r in accounting_keys),
            "file_c_blank_rows": int(totals[1]["blank_row_count"]),
        },
    }


def prepare(project_dir: Path, output_dir: Path) -> dict:
    """Verify originals -> select 25.4 -> calculate -> reconcile -> save tables."""
    inputs = verify_inputs(project_dir)
    b_rows, members = read_b_job(project_dir, *BASELINE_JOB)
    c_rows, excluded_early_c, excluded_p01_c = [], [], []
    for c_job, year, endpoint in JOBS:
        b_job = c_job.removesuffix("_c") + "_ab"
        selected_b, checked_b = read_b_job(project_dir, b_job, year, endpoint)
        selected_c, checked_c = read_job(project_dir, c_job, year, endpoint)
        b_rows.extend(selected_b)
        for row in selected_c:
            if row["object_class_code"] != "25.4":
                continue
            period = int(row["submission_period"][-2:])
            if year == 2025 and period < 5:
                excluded_early_c.append(row)
            elif year == 2026 and period == 1:
                # P02 includes October. Preserve the existing overlap guard:
                # a numeric P01 needs review, not silent exclusion or addition.
                if amount_or_blank(row["transaction_obligated_amount"], row["source_row_id"]) is not None:
                    raise ValueError(f"FY2026 P01 has numeric obligations; resolve overlap with P02: {row['source_row_id']}")
                excluded_p01_c.append(row)
            else:
                c_rows.append(row)
        # The reused C reader retains selected fields. Inspect original headers
        # explicitly so absence of PYA is a source finding, not an assumption.
        for check in checked_c:
            with zipfile.ZipFile(local_path(project_dir, check["zip_path"])) as archive:
                with archive.open(check["member"]) as binary, TextIOWrapper(binary, encoding="utf-8-sig", newline="") as handle:
                    check["pya_columns"] = pya_columns(next(csv.reader(handle)))
            check["layer"] = "C"
            check["selected_25_4_rows"] = sum(r["source_member"] == check["member"] for r in c_rows)
        members.extend((*checked_b, *checked_c))
    tables = build_tables(b_rows, c_rows)
    tables["checks"].update(
        file_c_excluded_early_row_count=len(excluded_early_c),
        file_c_excluded_early_numeric_obligations=observed_sum(excluded_early_c, "transaction_obligated_amount"),
        file_c_excluded_early_blank_row_count=sum(row["transaction_obligated_amount"].strip() == "" for row in excluded_early_c),
        file_c_excluded_early_periods=sorted({row["submission_period"] for row in excluded_early_c}),
        file_c_excluded_fy2026_p01_row_count=len(excluded_p01_c),
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, fields, table in (
        ("comparison_source_rows.csv", SOURCE_FIELDS, "source_rows"),
        ("comparison_totals.csv", TOTAL_FIELDS, "totals"),
        ("comparison_by_period.csv", PERIOD_FIELDS, "by_period"),
        ("comparison_accounting_keys.csv", ACCOUNTING_FIELDS, "accounting_keys"),
    ):
        with (output_dir / filename).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(tables[table])
    return {
        "status": "WARN", "calculation_status": "PASS", "inputs": inputs, "source_members": members,
        "bar_totals": tables["totals"], "checks": tables["checks"],
        "comparison_window": {
            "start_date": "2025-02-01", "end_date": "2026-07-31",
            "file_b_formula": "net(FY2025P12) - net(FY2025P04) + net(FY2026P10)",
            "file_b_baseline_period": "FY2025P04",
            "file_b_endpoint_periods": ["FY2025P12", "FY2026P10"],
            "file_c_selected_periods": [*(f"FY2025P{period:02d}" for period in range(5, 13)),
                                        *(f"FY2026P{period:02d}" for period in range(2, 11))],
        },
        "pya_absent": all(not member.get("pya_columns") for member in members if member["layer"] in {"B", "C"}),
        "file_c_observed_periods": sorted({row["submission_period"] for row in c_rows}),
        "limits": [
            "The difference is a reported-total comparison, not an IGSA estimate, government-recipient subtotal, or facility allocation.",
            "File C blanks remain missing. Only reported numeric transaction obligations enter its total.",
            "Visible-key diagnostics preserve B-only, C-only, and all-blank groups; their missing values are not observed zeros.",
            "PYA is not exposed in these downloads. Identical visible keys do not prove complete accounting comparability.",
            "PARK and program_activity_code are compared exactly; changes across periods are not silently crosswalked.",
            "The File B formula adds signed prior-year reductions; nonzero or blank transfer fields remain warnings rather than changing this formula.",
            "February 2025 through July 2026 uses File B FY2025 P12 minus P04 plus FY2026 P10; File C uses FY2025 P05-P12 and FY2026 P02-P10, with October included in P02.",
            "Baseline-only and endpoint-only keys are preserved without a crosswalk; an absent key is not an observed zero.",
            "Cumulative checkpoint differences may reflect revisions to earlier periods as well as activity in the selected window; the baseline and endpoints were downloaded at different recorded dates.",
            "Original downloads are frozen at recorded retrieval dates; publication/reporting completeness and full File B/File C accounting equivalence are not established.",
        ],
    }
