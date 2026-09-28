"""Read Chart 1's population, apply reviewed recipient types, and reconcile.

The crosswalk is an explicit decision table. Names never infer an entity type.
The all-object-class government check uses only reviewed identities, and is
not an exhaustive government-recipient census.
"""
from collections import defaultdict
import csv
from decimal import Decimal
import json
from pathlib import Path

from scripts.prepare_chart_data import JOBS, amount_or_blank, file_sha256, read_job
from scripts import shared_recipients as shared

SELECTED = 'Selected private detention contractors'
OTHER_PRIVATE = 'Other private contractors'
GOVERNMENT = 'State and local governments'
OTHER_PUBLIC = 'Other public or nonprofit entities'
NO_RECIPIENT = 'No recipient reported'
UNRESOLVED = 'Unresolved'
TYPES = (SELECTED, OTHER_PRIVATE, GOVERNMENT, OTHER_PUBLIC, NO_RECIPIENT, UNRESOLVED)
ANCHOR = Decimal('3136530747.79')


def recipient_key(row):
    if row['recipient_uei'].strip():
        return 'uei:' + row['recipient_uei'].strip()
    if row['recipient_name'].strip():
        return 'name:' + row['recipient_name'].strip()
    return 'missing'


def value_summary(rows):
    values = [amount_or_blank(r['transaction_obligated_amount'], r['source_row_id']) for r in rows]
    numeric = [v for v in values if v is not None]
    amount = sum(numeric, Decimal(0))
    # Empty categories are observed empty, while present blank-only groups are unknown.
    status = ('empty' if not rows else 'all_blank' if not numeric else
              'partial_blank' if len(numeric) < len(rows) else 'numeric')
    return {'amount': '' if status == 'all_blank' else f'{amount:.2f}',
            'value_status': status, 'numeric_row_count': len(numeric),
            'blank_row_count': len(rows) - len(numeric)}


def type_for(row, crosswalk):
    key = recipient_key(row)
    if key == 'missing':
        return NO_RECIPIENT
    return crosswalk.get(key, {}).get('type', UNRESOLVED)


def summarize(rows, crosswalk, anchor=ANCHOR):
    ids = [r['source_row_id'] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate source row')
    groups, typed = defaultdict(list), defaultdict(list)
    traced = []
    for row in rows:
        key, category = recipient_key(row), type_for(row, crosswalk)
        if category not in TYPES:
            raise ValueError('unknown recipient type')
        groups[key].append(row)
        typed[category].append(row)
        traced.append({**row, 'recipient_key': key, 'recipient_type': category})
    recipients = []
    for key, group in sorted(groups.items()):
        recipients.append({'key': key, 'recipient_uei': group[0]['recipient_uei'],
                           'recipient_name': ' | '.join(sorted({r['recipient_name'] for r in group})),
                           'type': type_for(group[0], crosswalk), **value_summary(group)})
    totals = []
    for category in TYPES:
        stats = value_summary(typed[category])
        amount = stats['amount']
        totals.append({'type': category, **stats,
                       'share_of_file_c': '' if amount == '' or not anchor else str(Decimal(amount) / anchor),
                       'recipient_count': len({recipient_key(r) for r in typed[category]} - {'missing'})})
    if sum((Decimal(r['amount']) for r in totals if r['amount']), Decimal(0)) != anchor:
        raise ValueError('recipient categories do not equal Chart 1 File C total')
    return recipients, totals, traced


def government_table(rows, crosswalk):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row['object_class_code']].append(row)
    result = []
    for obj, group in sorted(grouped.items()):
        out = {'object_class_code': obj}
        for label, subset in (
            ('government', [r for r in group if type_for(r, crosswalk) == GOVERNMENT]),
            ('other_public_nonprofit', [r for r in group if type_for(r, crosswalk) == OTHER_PUBLIC]),
            ('all_file_c', group),
            ('unreviewed_named', [r for r in group if type_for(r, crosswalk) == UNRESOLVED]),
        ):
            stats = value_summary(subset)
            out[label + '_obligations'] = stats['amount']
            out[label + '_status'] = stats['value_status']
            out[label + '_blank_rows'] = stats['blank_row_count']
        result.append(out)
    return result


def read_csv(path):
    with path.open(newline='', encoding='utf-8') as handle:
        reader = csv.DictReader(handle, strict=True)
        fields = reader.fieldnames or []
        if not fields or len(fields) != len(set(fields)):
            raise ValueError(f'invalid columns: {path.name}')
        rows = list(reader)
        if any(None in r or any(v is None for v in r.values()) for r in rows):
            raise ValueError(f'malformed CSV: {path.name}')
        return rows


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def validate_evidence(crosswalk, records):
    evidence = {r['uei']: r for r in records}
    if len(evidence) != len(records):
        raise ValueError('duplicate official identity evidence')
    for decision in crosswalk.values():
        record = evidence.get(decision['recipient_uei'])
        if (record is None or record.get('identity_matches') is not True or
                record.get('recipient', {}).get('recipient_uei') != decision['recipient_uei'] or
                record.get('frozen_name') != decision['recipient_name'] or
                record.get('source_url') != decision['evidence_url']):
            raise ValueError('crosswalk does not match saved official identity evidence')


def prepare(project, output):
    from scripts.portable_chart_2_evidence import validate_bundle
    validate_bundle(project)
    source = project / 'outputs/chart_1/comparison_source_rows.csv'
    receipt = json.loads((project / 'outputs/chart_1/verification.json').read_text())
    if file_sha256(source) != receipt['output_sha256'][source.name]:
        raise ValueError('Chart 1 source rows differ from its verified receipt')
    rows = [r for r in read_csv(source) if r['source_layer'] == 'C']
    # Validate historical evidence as migration provenance, not as a second
    # editable decision table. Both current analyses read the shared table.
    historical = read_csv(project / 'data/chart_2_recipient_crosswalk.csv')
    evidence = json.loads((project / 'provenance/chart_2_entity_evidence.json').read_text())
    validate_evidence({r['key']:r for r in historical}, evidence['records'])
    shared_decisions = shared.load(project)
    decisions = list(shared.chart_crosswalk(shared_decisions).values())
    crosswalk = {r['key']: r for r in decisions}
    if len(crosswalk) != len(decisions):
        raise ValueError('duplicate crosswalk key')
    for key, row in crosswalk.items():
        if (key != recipient_key(row) or row['type'] not in TYPES or
                row['review_status'] in shared.ACCEPTED_STATUSES and not row['evidence_url'].startswith('https://')):
            raise ValueError('invalid crosswalk identity/type/evidence')
        if row['review_status'] not in (('pending',) if row['type'] == UNRESOLVED else shared.ACCEPTED_STATUSES):
            raise ValueError('crosswalk review status disagrees with type')
    warnings = shared.diagnostics(project, shared_decisions)
    recipients, totals, traced = summarize(rows, crosswalk)

    # Reuse the verified raw File C reader for the supporting all-class check.
    all_rows, members = [], []
    for job, year, end in JOBS:
        raw, checks = read_job(project, job, year, end)
        members.extend(checks)
        for row in raw:
            period = int(row['submission_period'][-2:])
            if year == 2025 and period < 5:
                continue
            if year == 2026 and period == 1:
                if amount_or_blank(row['transaction_obligated_amount'], row['source_row_id']) is not None:
                    raise ValueError('numeric FY2026 P01 requires overlap review')
                continue
            all_rows.append(row)
    raw_254 = {r['source_row_id']: r for r in all_rows if r['object_class_code'] == '25.4'}
    if set(raw_254) != {r['source_row_id'] for r in rows}:
        raise ValueError('raw 25.4 population differs from Chart 1')
    for row in rows:
        for field in ('recipient_uei', 'recipient_name', 'transaction_obligated_amount',
                      'submission_period', 'federal_account_symbol', 'object_class_code'):
            if row[field] != raw_254[row['source_row_id']][field]:
                raise ValueError(f'Chart 1/raw disagreement: {field}')
    gov = government_table(all_rows, crosswalk)
    all_stats = value_summary(all_rows)
    if sum((Decimal(r['all_file_c_obligations']) for r in gov if r['all_file_c_obligations']), Decimal(0)) != Decimal(all_stats['amount']):
        raise ValueError('all-class controls do not reconcile')
    classified = []
    for row in recipients:
        entry = crosswalk.get(row['key'])
        classified.append(entry if entry else {
            'key': row['key'], 'recipient_uei': row['recipient_uei'], 'recipient_name': row['recipient_name'],
            'type': row['type'], 'evidence_url': 'https://www.usaspending.gov/download_center/custom_account_data',
            'basis': 'No recipient reported in selected original records.' if row['key'] == 'missing' else 'No reviewed crosswalk entry.',
            'review_status': 'reviewed' if row['key'] == 'missing' else 'pending',
            'relationship_url': '', 'checked_date': '2026-09-23'})
    output.mkdir(parents=True, exist_ok=True)
    for name, table in (
        ('recipient_classification.csv', classified), ('recipient_totals.csv', recipients),
        ('recipient_type_totals.csv', totals), ('classified_source_rows.csv', traced),
        ('government_all_object_classes.csv', gov),
        ('government_source_rows.csv', [dict(r, recipient_type=type_for(r, crosswalk)) for r in all_rows
                                        if type_for(r, crosswalk) in (GOVERNMENT, OTHER_PUBLIC)]),
    ):
        write_csv(output / name, table)
    return {'file_c_total': str(ANCHOR), 'source_rows': len(rows),
            'named_recipients': len(recipients) - sum(r['key'] == 'missing' for r in recipients),
            'blank_amount_rows': sum(r['blank_row_count'] for r in totals),
            'all_class_total': all_stats['amount'], 'verified_members': members,
            'government_over_10m_other_classes': any(abs(Decimal(r['government_obligations'] or '0')) > 10000000
                                                     for r in gov if r['object_class_code'] != '25.4'),
            'government_coverage': 'Reviewed current-chart identities plus verified candidates from the earlier government name screen; not an exhaustive all-class census.',
            'source_sha256': file_sha256(source),
            'shared_decision_warnings': {key:row['shared_decision_warning'] for key,row in warnings.items()
                                         if key in {recipient_key(r) for r in rows}},
            'crosswalk_path': shared.CROSSWALK,
            'crosswalk_sha256': file_sha256(project / shared.CROSSWALK)}
