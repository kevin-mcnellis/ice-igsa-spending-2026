#!/usr/bin/env python3
"""Stage 1: turn the frozen File C downloads into three inspectable bar totals.

Reading order: prepare() at the bottom shows the whole process. read_job()
checks and reads the original ZIPs; summarize() decides which rows contribute.
Inputs: data/source_manifest.csv, two File C ZIPs/receipts, two Census ZIPs.
Outputs: chart_source_rows.csv, recipient_totals.csv, chart_totals.csv.
Only Python's standard library is used. The original ZIPs are never extracted
or changed. Dollar arithmetic uses Decimal so cents are retained exactly.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from decimal import Decimal, InvalidOperation
import hashlib
from io import TextIOWrapper
import json
from pathlib import Path
import re
import zipfile


# The approved scope and named-company screen are intentionally visible here.
PROJECT_DIR = Path(__file__).resolve().parents[1]
JOBS = (("DHS_FY2025P12_c", 2025, 12), ("DHS_FY2026P10_c", 2026, 10))
ACCOUNTS = {"070-0540", "070-0545"}
BAR_LABELS = (
    ("all_file_c", "Total File C transaction obligations"),
    ("major_private_prison_contractors", "Major Private Prison Contractors"),
    ("state_and_local_governments", "State and local government name matches"),
)
CONTRACTOR_NAMES = {
    "THE GEO GROUP INC": "The GEO Group",
    "CORECIVIC INC": "CoreCivic",
    "LASALLE CORRECTIONS V LLC": "LaSalle",
    "MANAGEMENT TRAINING CORPORATION": "Management & Training Corporation",
    "AKIMA GLOBAL SERVICES LLC": "Akima",
    "AKIMA INFRASTRUCTURE PROTECTION LLC": "Akima",
}
GEOGRAPHY_HASHES = {
    "state": "5c0bb56f4824af366538d73bffd229e790d301356624302eeca24d09cf27ba30",
    "counties": "4c90d0f805779923b5958ab13d0c1e9b99fe4932b786bfcf75dd739bb2dcb4ea",
}
COUNTY_SUFFIXES = (
    " CITY AND BOROUGH", " PLANNING REGION", " CENSUS AREA", " MUNICIPALITY",
    " BOROUGH", " PARISH", " COUNTY", " CITY",
)
# These exclusions apply only to the new agency-name rule. Existing broad
# state/county matches intentionally continue to include incidental companies.
NONAGENCY_WORDS = {
    "INC", "INCORPORATED", "LLC", "CORP", "CORPORATION", "COMPANY", "LP", "LLP", "LTD",
    "ASSOCIATION", "ASSOCIATIONS", "ASSOCIATES", "FOUNDATION",
    "FRATERNAL", "BENEVOLENT", "SUPPLY", "SUPPLIES", "EQUIPMENT", "UNIFORMS",
}
# UNION and COUNCIL can be place names (Union City, Council Bluffs).
# Use organization phrases rather than rejecting those words by themselves.
NONAGENCY_PHRASES = {
    "CREDIT UNION", "POLICE UNION", "SHERIFFS UNION", "SHERIFF S UNION",
    "OFFICERS UNION", "DEPUTIES UNION", "EMPLOYEES UNION",
}
LAW_ENFORCEMENT_PATTERNS = {
    "police_agency": (
        r"\bPOLICE (?:DEPARTMENT|DEPT|BUREAU|DIVISION|SERVICE|SERVICES|FORCE)\b",
        r"\b(?:DEPARTMENT|DEPT|BUREAU|DIVISION) OF (?:THE )?POLICE\b",
    ),
    "sheriff_agency": (
        r"\bSHERIFF(?:S| S)? (?:OFFICE|DEPARTMENT|DEPT)\b",
        r"\b(?:OFFICE|DEPARTMENT|DEPT) OF (?:THE )?SHERIFF(?:S| S)?\b",
    ),
}
REQUIRED = {
    "submission_period", "federal_account_symbol", "transaction_obligated_amount",
    "recipient_uei", "recipient_name", "recipient_parent_name",
}
DETAIL_FIELDS = (
    "bar_id", "recipient_key", "direct_recipient_uei", "direct_recipient_name",
    "parent_recipient_name", "contractor_group", "match_rule", "amount",
    "numeric_row_count", "blank_row_count", "first_source_file_path",
    "first_source_line_number",
)
RAW_FIELDS = (
    "submission_period", "federal_account_symbol", "treasury_account_symbol",
    "program_activity_reporting_key", "program_activity_code", "object_class_code",
    "direct_or_reimbursable_funding_source", "disaster_emergency_fund_code",
    "transaction_obligated_amount", "award_unique_key", "award_id_piid",
    "parent_award_id_piid", "award_id_fain", "award_id_uri",
    "recipient_uei", "recipient_name", "recipient_parent_uei", "recipient_parent_name",
    "prime_award_base_transaction_description", "usaspending_permalink", "last_modified_date",
)
TRACE_FIELDS = (
    "source_row_id", "source_zip_path", "source_member", "source_line_number",
    "source_file_path", "source_url", "component", *RAW_FIELDS,
    "recipient_key", "obligation_value_status", "all_file_c_contribution",
    "contractor_match", "contractor_group", "contractor_row_match_rule",
    "contractor_recipient_match_rule", "contractor_contribution",
    "government_match", "government_match_rule", "government_contribution",
)


def normalize_text(value: str) -> str:
    """Compare names in uppercase with punctuation replaced by spaces."""
    return " ".join(re.sub(r"[^A-Z0-9]+", " ", value.upper()).split())


def amount_or_blank(value: str, row_id: str) -> Decimal | None:
    """A blank stays missing; a reported zero is a numeric observation."""
    if not value.strip():
        return None
    try:
        amount = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"invalid obligation at {row_id}: {value!r}") from exc
    if not amount.is_finite():
        raise ValueError(f"invalid obligation at {row_id}: {value!r}")
    return amount


def file_sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return stream_sha256(handle)


def stream_sha256(handle) -> str:
    digest = hashlib.sha256()
    for block in iter(lambda: handle.read(1024 * 1024), b""):
        digest.update(block)
    return digest.hexdigest()


def local_path(project_dir: Path, relative: str) -> Path:
    """Reject input paths that resolve outside this copied project folder."""
    path = project_dir / relative
    if not path.resolve().is_relative_to(project_dir.resolve()):
        raise ValueError(f"input path escapes project: {relative}")
    return path


def verify_manifest(project_dir: Path) -> list[dict[str, str]]:
    """Check all six frozen files before interpreting their contents."""
    with (project_dir / "data/source_manifest.csv").open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, strict=True)
        if not {"path", "source_url", "sha256", "bytes", "role"} <= set(reader.fieldnames or ()):
            raise ValueError("missing source manifest columns")
        records = list(reader)
    paths = [record["path"] for record in records]
    if len(paths) != 6 or len(set(paths)) != len(paths):
        raise ValueError("expected six distinct manifest files")
    expected = {f"data/reference/2025_Gaz_{kind}_national.zip" for kind in GEOGRAPHY_HASHES}
    for job, _, _ in JOBS:
        receipt_relative = f"data/raw/{job}/acquisition_receipt.json"
        expected.add(receipt_relative)
        receipt = json.loads(local_path(project_dir, receipt_relative).read_text(encoding="utf-8"))
        expected.add(f"data/raw/{job}/{Path(receipt['zip_path']).name}")
    if set(paths) != expected:
        raise ValueError("source manifest does not describe the expected six inputs")
    for record in records:
        path = local_path(project_dir, record["path"])
        if path.stat().st_size != int(record["bytes"]) or file_sha256(path) != record["sha256"]:
            raise ValueError(f"source manifest hash/size mismatch: {record['path']}")
    return [{**record, "hash_status": "verified"} for record in records]


def read_job(project_dir: Path, job: str, year: int, last_period: int,
             extra_fields: tuple[str, ...] = (), *,
             account_filter=ACCOUNTS, row_handler=None, row_predicate=None):
    """Validate one receipt and stream each original CSV member in its order.

    Old absolute paths in acquisition receipts are historical notes. Only the
    ZIP basename is used here. Source line numbers count physical lines, so a
    quoted field containing a newline does not corrupt the locator.
    """
    job_relative = f"data/raw/{job}"
    receipt = json.loads(local_path(project_dir, f"{job_relative}/acquisition_receipt.json").read_text(encoding="utf-8"))
    requested = receipt.get("requested", {})
    filters = requested.get("filters", {})
    for valid, label in (
        (requested.get("account_level") == "treasury_account", "account level"),
        (requested.get("file_format") == "csv", "file format"),
        (str(filters.get("fy")) == str(year), "fiscal year"),
        (filters.get("period") == last_period, "submission period"),
        (str(filters.get("agency")) == "63", "agency filter"),
        (filters.get("submission_types") == ["award_financial"], "submission types"),
    ):
        if not valid:
            raise ValueError(f"wrong {label} in {job} receipt")
    zip_relative = f"{job_relative}/{Path(receipt['zip_path']).name}"
    zip_path = local_path(project_dir, zip_relative)
    if zip_path.stat().st_size != int(receipt["zip_bytes"]):
        raise ValueError(f"ZIP byte-size mismatch: {zip_relative}")
    if file_sha256(zip_path) != receipt["zip_sha256"]:
        raise ValueError(f"ZIP SHA-256 mismatch: {zip_relative}")

    rows, checks, components = [], [], set()
    with zipfile.ZipFile(zip_path) as archive:
        names = [member["member"] for member in receipt["members"]]
        if len(names) != len(set(names)) or sorted(names) != sorted(archive.namelist()):
            raise ValueError(f"receipt and ZIP members differ: {job}")
        for member in receipt["members"]:
            name = member["member"]
            pattern = rf"FY{year}P01-P{last_period:02d}_070_TAS_(Contracts|Assistance|Unlinked)_AccountBreakdownByAward_[^/]+\.csv"
            match = re.fullmatch(pattern, name)
            if not match:
                raise ValueError(f"unexpected File C member: {name}")
            component = match[1]
            components.add(component)
            if archive.getinfo(name).file_size != int(member["bytes"]):
                raise ValueError(f"member byte-size mismatch: {name}")
            with archive.open(name) as handle:
                digest = stream_sha256(handle)
            if digest != member["sha256"]:
                raise ValueError(f"member SHA-256 mismatch: {name}")
            source_id = f"{job}:{name}"
            selected, scanned = 0, 0
            with archive.open(name) as binary, TextIOWrapper(binary, encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle, strict=True)
                fields = reader.fieldnames or []
                if (len(fields) != len(set(fields)) or
                        not (REQUIRED | set(extra_fields)) <= set(fields)):
                    raise ValueError(f"missing or duplicate File C columns: {name}")
                next_line = reader.line_num + 1
                for row in reader:
                    line, next_line = next_line, reader.line_num + 1
                    scanned += 1
                    if None in row or any(value is None for value in row.values()):
                        raise ValueError(f"malformed CSV row: {name}:{line}")
                    if (account_filter is not None and
                            row["federal_account_symbol"].strip() not in account_filter):
                        continue
                    if not re.fullmatch(rf"FY{year}P(?:0[1-9]|1[0-2])", row["submission_period"]):
                        raise ValueError(f"unexpected period for source job: {name}:{line}")
                    if int(row["submission_period"][-2:]) > last_period:
                        raise ValueError(f"period exceeds source endpoint: {name}:{line}")
                    if row_predicate is not None and not row_predicate(row):
                        selected += 1
                        continue
                    selected_row = {
                        **{field: row.get(field, "") for field in (*RAW_FIELDS, *extra_fields)},
                        "source_row_id": f"{source_id}:row:{line}",
                        "source_zip_path": zip_relative, "source_member": name,
                        "source_file_path": f"{zip_relative}!{name}",
                        "source_line_number": str(line), "component": component,
                        "source_url": receipt["download_url"],
                    }
                    if row_handler is None:
                        rows.append(selected_row)
                    else:
                        row_handler(selected_row)
                    selected += 1
            checks.append({"source_id": source_id, "zip_path": zip_relative, "member": name,
                           "bytes": member["bytes"], "sha256": digest, "hash_status": "verified",
                           "scanned_rows": scanned, "selected_rows": selected})
    if components != {"Contracts", "Assistance", "Unlinked"}:
        raise ValueError(f"missing File C component: {job}")
    return rows, checks


def load_geographic_names(project_dir: Path) -> dict[str, set[str]]:
    """Load the frozen 50-state/county vocabulary, excluding DC and Puerto Rico."""
    terms = defaultdict(set)
    states = set()
    for kind, expected_hash in GEOGRAPHY_HASHES.items():
        filename = f"2025_Gaz_{kind}_national.zip"
        path = local_path(project_dir, f"data/reference/{filename}")
        if file_sha256(path) != expected_hash:
            raise ValueError(f"Census reference hash mismatch: {filename}")
        member = filename.removesuffix(".zip") + ".txt"
        with zipfile.ZipFile(path) as archive:
            if archive.namelist() != [member]:
                raise ValueError(f"unexpected Census ZIP members: {filename}")
            with archive.open(member) as binary, TextIOWrapper(binary, encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle, delimiter="|")
                if not {"USPS", "GEOID", "NAME"} <= set(reader.fieldnames or ()):
                    raise ValueError(f"missing Census columns: {filename}")
                for row in reader:
                    if row["USPS"] in {"DC", "PR"}:
                        continue
                    name = normalize_text(row["NAME"])
                    if kind == "state":
                        states.add(row["USPS"])
                        terms[name].add(f"state_name:{name}")
                    elif row["USPS"] in states:
                        suffix = next((s for s in COUNTY_SUFFIXES if name.endswith(s)), "")
                        if not suffix:
                            raise ValueError(f"unrecognized county suffix: {name}")
                        base = name[:-len(suffix)]
                        terms[base].add(f"county_name:{base}")
    if len(states) != 50 or not any(r.startswith("county_name:") for rules in terms.values() for r in rules):
        raise ValueError("incomplete 50-state Census vocabulary")
    return dict(terms)


def law_enforcement_name_matches(normalized: str) -> list[str]:
    """Flag agency-shaped names, not every occurrence of POLICE or SHERIFF.

    The caller has already uppercased the name and replaced punctuation with
    spaces. Thus SHERIFF'S and SHERIFF’S both become SHERIFF S. These are likely
    recipient-name matches, not verified identities or descriptions of awards.
    """
    if NONAGENCY_WORDS.intersection(normalized.split()):
        return []
    if any(f" {phrase} " in f" {normalized} " for phrase in NONAGENCY_PHRASES):
        return []
    # UNION CITY can be a place; UNION OF POLICE names an organization.
    if re.search(r"\b(?:UNION|COUNCIL) OF (?:THE )?(?:POLICE|SHERIFF(?:S| S)?)\b", normalized):
        return []
    return [f"law_enforcement:{kind}" for kind, patterns in LAW_ENFORCEMENT_PATTERNS.items()
            if any(re.search(pattern, normalized) for pattern in patterns)]


def government_name_matches(name: str, geographic_names: dict[str, set[str]]) -> list[str]:
    """Preserve the approved broad screen, including incidental company names."""
    normalized = normalize_text(name)
    rules = {f"keyword:{word}" for word in ("STATE", "COUNTY") if word in normalized.split()}
    padded = f" {normalized} "
    for term, matches in geographic_names.items():
        if f" {term} " in padded:
            rules.update(matches)
    rules.update(law_enforcement_name_matches(normalized))
    # These narrow city/state signals preserve the earlier classifier's rules.
    words = normalized.split()
    vendor = bool(words) and words[-1] in {"INC", "INCORPORATED", "LLC", "CORP", "CORPORATION", "LP"}
    federal = "BUREAU OF PRISONS" in normalized or normalized.startswith("FEDERAL PRISON INDUSTRIES")
    states = [term for term, hits in geographic_names.items() if f"state_name:{term}" in hits]
    if not vendor and not federal:
        if any(re.search(rf"\bSTATE OF {re.escape(state)}\b", normalized) for state in states):
            rules.add("state:state_of")
        elif any(re.search(rf"\b{re.escape(state)}(?: STATE)? (?:DEPARTMENT|DEPT) OF\b", normalized) for state in states):
            rules.add("state:named_state_department")
        elif normalized.startswith("CITY OF "):
            rules.add("city:city_of")
    return sorted(rules)


def contractor_match(name: str, parent: str) -> tuple[str, str]:
    direct = normalize_text(name)
    if direct in CONTRACTOR_NAMES:
        return CONTRACTOR_NAMES[direct], "exact_direct_name"
    if normalize_text(parent) == "THE GEO GROUP INC":
        return "The GEO Group", "exact_geo_parent_name"
    return "", ""


def summarize(rows: list[dict[str, str]], geographic_names: dict[str, set[str]]):
    """Return bar totals, recipient subtotals, and an explanation for every row.

    Contractor rules apply to all aliases of one recipient key. Government
    rules apply only to the direct name on that particular source row.
    The two subgroups can overlap; neither partitions the total.
    """
    ids = [row["source_row_id"] for row in rows]
    if len(ids) != len(set(ids)) or any(not value for value in ids):
        raise ValueError("blank or duplicate source row ID")
    by_recipient = defaultdict(list)
    traced = []
    name_cache = {}
    for row in rows:
        period = re.fullmatch(r"FY(\d{4})P(\d{2})", row["submission_period"].strip())
        if not period or (int(period[1]), int(period[2])) not in {
            *((2025, p) for p in range(1, 13)), *((2026, p) for p in range(1, 11)),
        }:
            raise ValueError(f"unexpected period at {row['source_row_id']}")
        if row["federal_account_symbol"] not in ACCOUNTS:
            raise ValueError(f"unexpected account at {row['source_row_id']}")
        amount = amount_or_blank(row["transaction_obligated_amount"], row["source_row_id"])
        # Preserve source precision until the final totals are displayed.
        value_text = "" if amount is None else format(amount, "f")
        name, uei = row["recipient_name"].strip(), row["recipient_uei"].strip()
        key = f"uei:{uei}" if uei else f"name:{normalize_text(name)}" if name else ""
        if name not in name_cache:
            name_cache[name] = government_name_matches(name, geographic_names)
        matches = name_cache[name] if key else []
        traced_row = {
            **row, "recipient_key": key,
            "obligation_value_status": "blank" if amount is None else "numeric",
            "all_file_c_contribution": value_text,
            "contractor_match": "false", "contractor_group": "",
            "contractor_row_match_rule": contractor_match(name, row["recipient_parent_name"])[1],
            "contractor_recipient_match_rule": "", "contractor_contribution": "",
            "government_match": str(bool(matches)).lower(),
            "government_match_rule": ";".join(matches),
            "government_contribution": value_text if matches else "",
        }
        traced.append(traced_row)
        if key:
            by_recipient[key].append((traced_row, amount))

    details = []
    for key, pairs in sorted(by_recipient.items()):
        hits = {contractor_match(row["recipient_name"], row["recipient_parent_name"]) for row, _ in pairs}
        hits.discard(("", ""))
        groups = {group for group, _ in hits}
        if len(groups) > 1:
            raise ValueError(f"conflicting contractor groups for {key}")
        group = next(iter(groups), "")
        contractor_rule = ";".join(sorted({rule for _, rule in hits}))
        if group:
            for row, amount in pairs:
                row.update(contractor_match="true", contractor_group=group,
                           contractor_recipient_match_rule=contractor_rule,
                           contractor_contribution=row["all_file_c_contribution"])
        government_pairs = [(row, amount) for row, amount in pairs if row["government_match"] == "true"]
        government_rule = ";".join(sorted({rule for row, _ in government_pairs
                                         for rule in row["government_match_rule"].split(";")}))
        for bar_id, rule, selected in (
            ("major_private_prison_contractors", contractor_rule, pairs if group else []),
            ("state_and_local_governments", government_rule, government_pairs),
        ):
            if not selected:
                continue
            first = selected[0][0]
            value = sum((amount for _, amount in selected if amount is not None), Decimal("0"))
            details.append({
                "bar_id": bar_id, "recipient_key": key,
                "direct_recipient_uei": first["recipient_uei"].strip(),
                "direct_recipient_name": " | ".join(sorted({r["recipient_name"].strip() for r, _ in selected})),
                "parent_recipient_name": " | ".join(sorted({r["recipient_parent_name"].strip() for r, _ in selected if r["recipient_parent_name"].strip()})),
                "contractor_group": group, "match_rule": rule, "amount": f"{value:.2f}",
                "numeric_row_count": str(sum(a is not None for _, a in selected)),
                "blank_row_count": str(sum(a is None for _, a in selected)),
                "first_source_file_path": first["source_file_path"],
                "first_source_line_number": first["source_line_number"],
            })
    summaries = []
    for (bar_id, label), prefix in zip(BAR_LABELS, ("all_file_c", "contractor", "government")):
        selected = [r for r in traced if prefix == "all_file_c" or r[f"{prefix}_match"] == "true"]
        values = [r[f"{prefix}_contribution"] for r in selected]
        summaries.append({"bar_id": bar_id, "label": label,
                          "amount": f"{sum((Decimal(v) for v in values if v), Decimal('0')):.2f}",
                          "source_row_count": str(len(selected)), "blank_row_count": str(values.count(""))})
    return summaries, details, traced


def check_periods(rows: list[dict[str, str]]) -> dict:
    """Show observed periods; stop if FY2026 P01 could be counted with P02."""
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["submission_period"]].append(amount_or_blank(row["transaction_obligated_amount"], row["source_row_id"]))
    p01_numeric = sum(value is not None for value in grouped.get("FY2026P01", []))
    if p01_numeric:
        raise ValueError("FY2026 P01 has numeric obligations; resolve possible overlap with combined P02 before summing")
    return {
        "status": "PASS", "fy2026_p01_numeric_rows": p01_numeric,
        "fy2026_p01_rows": len(grouped.get("FY2026P01", [])),
        "note": "FY2026 P02 is the combined October-November reporting window; no numeric P01 is added separately.",
        "periods": [{"submission_period": period, "source_row_count": len(values),
                     "numeric_row_count": sum(v is not None for v in values),
                     "blank_row_count": sum(v is None for v in values),
                     "amount": f"{sum((v for v in values if v is not None), Decimal('0')):.2f}"}
                    for period, values in sorted(grouped.items())],
    }


def reconcile(summary, details, traced) -> list[dict[str, str]]:
    """Cross-check both subgroup sums and counts against the recipient table."""
    checks = []
    for bar in summary[1:]:
        recipients = [row for row in details if row["bar_id"] == bar["bar_id"]]
        value = sum((Decimal(row["amount"]) for row in recipients), Decimal("0"))
        numeric = sum(int(row["numeric_row_count"]) for row in recipients)
        blank = sum(int(row["blank_row_count"]) for row in recipients)
        if value != Decimal(bar["amount"]) or numeric + blank != int(bar["source_row_count"]) or blank != int(bar["blank_row_count"]):
            raise ValueError(f"recipient reconciliation failed: {bar['bar_id']}")
        checks.append({"bar_id": bar["bar_id"], "status": "PASS", "amount_difference": "0.00",
                       "recipient_count": len(recipients), "numeric_row_count": numeric, "blank_row_count": blank})
    raw_total = sum((amount_or_blank(row["transaction_obligated_amount"], row["source_row_id"]) or Decimal("0")
                     for row in traced), Decimal("0"))
    if raw_total != Decimal(summary[0]["amount"]) or len(traced) != int(summary[0]["source_row_count"]):
        raise ValueError("source-row total reconciliation failed")
    return [{"bar_id": "all_file_c", "status": "PASS", "amount_difference": "0.00", "source_row_count": len(traced)}, *checks]


def prepare(project_dir: Path, output_dir: Path) -> dict:
    """Run the analysis in five steps; return checks for the runner's receipt."""
    # 1. Verify local inputs before accepting any financial values.
    inputs = verify_manifest(project_dir)
    rows, members = [], []
    for job, year, period in JOBS:
        selected, checked = read_job(project_dir, job, year, period)
        rows.extend(selected)
        members.extend(checked)

    # 2. Check the observed fiscal periods and load the geography vocabulary.
    periods = check_periods(rows)
    geography = load_geographic_names(project_dir)

    # 3. Apply the two screens, retaining an explanation for each source row.
    summary, details, traced = summarize(rows, geography)

    # 4. Reconcile source rows -> recipient amounts -> bar totals.
    reconciliations = reconcile(summary, details, traced)

    # 5. Save the three progressively smaller tables in the same reading order.
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, fields, records in (
        ("chart_source_rows.csv", TRACE_FIELDS, traced),
        ("recipient_totals.csv", DETAIL_FIELDS, details),
        ("chart_totals.csv", tuple(summary[0]), summary),
    ):
        with (output_dir / filename).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(records)
    overlap = [r for r in traced if r["contractor_match"] == r["government_match"] == "true"]
    return {
        "status": "WARN", "calculation_status": "PASS", "inputs": inputs, "source_members": members,
        "selected_source_rows": len(rows), "period_check": periods, "reconciliations": reconciliations,
        "bar_totals": summary,
        "subgroup_overlap": {"source_row_count": len(overlap), "amount": f"{sum((Decimal(r['all_file_c_contribution']) for r in overlap if r['all_file_c_contribution']), Decimal('0')):.2f}"},
        "limits": ["Name screening is not legal-entity verification; incidental private-company matches remain included.",
                   "File C is award-linked accounting detail and may not cover all agency obligations.",
                   "No independent File B/D1/D2 obligation reconciliation is performed by this package.",
                   "FY2026 through P10 is partial-year; the fiscal window starts before January 20, 2025.",
                   "The source vintage is frozen at its recorded retrieval dates, not refreshed from USAspending."],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", type=Path, default=PROJECT_DIR)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    report = prepare(args.project_dir, args.output_dir or args.project_dir / "outputs")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
