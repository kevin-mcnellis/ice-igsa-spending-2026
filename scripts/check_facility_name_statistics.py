"""Recompute frozen facility-name statistics from reviewed pairs and source rows.

The pair CSV is a facility–award relationship table. Its award amount may appear
on several rows, so group totals use distinct award keys rather than row sums.
"""

from collections import defaultdict
import csv
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from urllib.parse import quote

try:
    from File_C_blog_post.scripts import screen_igsa_ddp_descriptions as screen
except ModuleNotFoundError as error:
    if error.name != 'File_C_blog_post':
        raise
    from scripts import screen_igsa_ddp_descriptions as screen


REPO = Path(__file__).resolve().parents[2]
PACKAGE = REPO / 'File_C_blog_post'
PATHS = {
    'panel': REPO / 'output/tables/detention_roster_facility_snapshot_panel.csv',
    'pairs': PACKAGE / 'outputs/facility_name_screen/award_facility_pairs.csv',
    'screen_receipt': PACKAGE / 'outputs/facility_name_screen/verification.json',
    'comparison': PACKAGE / 'outputs/chart_1/comparison_source_rows.csv',
}
OUTPUT = PACKAGE / 'outputs/facility_name_screen'
START_DATE, END_DATE = '2025-01-21', '2026-07-09'
IGA_TYPES = frozenset({'IGSA', 'DIGSA', 'USMS IGA'})
OTHER_TYPES = frozenset({'BOP', 'SPC', 'CDF', 'STAGING', 'DOD', 'USMS CDF', 'MOC'})
BROADER_TYPES = IGA_TYPES | {'STATE', 'FAMILY', 'JUVENILE'}
ACCOUNTS = {'070-0540', '070-0545'}
FROZEN_HASHES = {
    'panel': '021d3f49c5e9893b11cfb2f9d84778634dcca2735de911ef4a1259872135ae6c',
    'pairs': 'acc2cbb3b438427587e3e9f942bfac2841f1974400d97a9b95883e20c13e4c89',
    'screen_receipt': 'd3d5d54f44ce39729c31f4b11db4493965e5abac9d43b10ccd1fbd4cd1389e85',
    'comparison': 'b38b2010fe8b57f10d8896303a81b824e7c80e290398a85cdfc0dfd570fa3a59',
    'screen_code': '4201a88071942fbac2daaa993158bb306a120a36bd9c6b92efb94460ffc2b4f5',
}
EXPECTED = {
    'roster_entities': 271,
    'iga_group_entities': 224,
    'federal_contract_group_entities': 49,
    'broader_state_local_entities_reference_only': 227,
    'both_group_facility_count': 5,
    'both_group_facility_names': [
        'CCA, FLORENCE CORRECTIONAL CENTER',
        'LA SALLE COUNTY REGIONAL DETENTION CENTER',
        'MONTGOMERY COUNTY JAIL',
        'ROBERT A DEYTON DETENTION FACILITY',
        'T DON HUTTO DETENTION CENTER',
    ],
    'federal_contract_matched_facilities': 21,
    'federal_contract_distinct_awards': 76,
    'federal_contract_25_4_amount': '2229581023.16',
    'iga_matched_facilities': 5,
    'iga_distinct_awards': 12,
    'iga_25_4_amount': '96196138.33',
    'solely_iga_facility_ids': [
        'fac_634a761f7f915b7da95ecf9a40d37123',
        'fac_c22c29576bef59ae8338b8e10d09e3e2',
    ],
    'solely_iga_award_piids': ['70CDCR26FR0000058', '70CDCR26FR0000060'],
    'solely_iga_25_4_amount': '17465361.06',
    'iga_not_solely_facility_names': [
        'CCA, FLORENCE CORRECTIONAL CENTER',
        'ROBERT A DEYTON DETENTION FACILITY',
        'T DON HUTTO DETENTION CENTER',
    ],
    'iga_not_solely_25_4_amount': '78730777.27',
    'file_c_25_4_amount': '3136530747.79',
    'federal_contract_share_percent': '71.08',
    'iga_share_percent': '3.07',
}
MATCH_FIELDS = ('facility_entity_id', 'facility_name', 'award_unique_key',
                'award_id_piid', 'solely_iga', 'observed_labels',
                'award_25_4_amount', 'amount_status', 'shared_award',
                'matched_phrase', 'match_tier', 'source_row_link', 'award_url')
APPROVED_PAIR_SHA = FROZEN_HASHES['pairs']


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def table(path, required):
    with Path(path).open(newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle, strict=True)
        missing = set(required) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f'missing columns in {Path(path).name}: {sorted(missing)}')
        return list(reader)


def compare_pair_exports(approved_path, portable_path, *,
                         approved_sha256=APPROVED_PAIR_SHA,
                         source_prefix='data/raw'):
    """Prove relocation changed only the pair table's source-row links."""
    if sha256(approved_path) != approved_sha256:
        raise ValueError('approved pair CSV hash mismatch')
    def read(path):
        with Path(path).open(newline='', encoding='utf-8-sig') as stream:
            reader = csv.DictReader(stream, strict=True)
            return reader.fieldnames, list(reader)
    fields, approved = read(approved_path)
    portable_fields, portable = read(portable_path)
    if (fields != portable_fields or len(approved) != len(portable) or
            not {'source_row_link', 'example_source_file',
                 'example_source_line'} <= set(fields or [])):
        raise ValueError('portable pair CSV shape differs from approved file')
    if source_prefix != 'data/raw':
        raise ValueError('portable source prefix must be data/raw')
    locator_changes = 0
    for index, (original, current) in enumerate(zip(approved, portable), start=2):
        if any(original[field] != current[field]
               for field in fields if field != 'source_row_link'):
            raise ValueError(f'analytic pair row differs at CSV line {index}')
        for row, portable_link in ((original, False), (current, True)):
            match = re.fullmatch(r'\[source row\]\(<(.+):(\d+)>\)',
                                 row['source_row_link'])
            if not match or match.group(2) != row['example_source_line']:
                raise ValueError(f'pair source-row locator differs at CSV line {index}')
            expected = row['example_source_file']
            if portable_link:
                if match.group(1) != source_prefix + '/' + expected:
                    raise ValueError(f'portable source-row path differs at CSV line {index}')
            elif not match.group(1).endswith('/' + expected):
                raise ValueError(f'approved source-row path differs at CSV line {index}')
        locator_changes += original['source_row_link'] != current['source_row_link']
    if not locator_changes:
        raise ValueError('portable pair CSV has no relocated source-row links')
    return {'status': 'PASS', 'rows': len(approved),
            'analytic_columns_identical': True,
            'relocated_source_row_links': locator_changes,
            'approved_sha256': approved_sha256,
            'portable_sha256': sha256(portable_path)}


def amount(value, label):
    try:
        result = Decimal(value)
    except (InvalidOperation, TypeError) as exc:
        raise ValueError(f'invalid amount in {label}: {value!r}') from exc
    if not result.is_finite():
        raise ValueError(f'nonfinite amount in {label}')
    return result


def money(value):
    return f'{value:.2f}'


def percent(numerator, denominator):
    if not denominator:
        raise ValueError('File C denominator is zero')
    return f'{(numerator / denominator * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP):.2f}'


def check(paths=PATHS, *, expected=EXPECTED, frozen_hashes=FROZEN_HASHES,
          link_root=None):
    """Return a comparison receipt and IGSA pair rows; raise on invalid inputs."""
    # --- Step 1 --- Pin the source screen's rule/window and all input bytes.
    if (screen.START_DATE, screen.END_DATE, set(screen.LEGACY_IGA_TYPES)) != (
            START_DATE, END_DATE, set(IGA_TYPES)):
        raise ValueError('screen observation window mismatch')
    if (set(screen.TYPE_FAMILIES['other_type_family']) != set(OTHER_TYPES) or
            set(screen.TYPE_FAMILIES['state_local_type_family']) != set(BROADER_TYPES)):
        raise ValueError('screen type-family window mismatch')
    for key, path in paths.items():
        if not Path(path).is_file():
            raise ValueError(f'missing input: {key}: {path}')
    hashes = {key: sha256(path) for key, path in paths.items()}
    hashes['screen_code'] = sha256(screen.__file__)
    for key, digest in frozen_hashes.items():
        if hashes.get(key) != digest:
            raise ValueError(f'{key} hash mismatch')
    receipt = json.loads(Path(paths['screen_receipt']).read_text())
    if (receipt['pair_csv_sha256'] != hashes['pairs'] or
            receipt['input_sha256']['panel'] != hashes['panel']):
        raise ValueError('screen receipt hash mismatch')
    if (set(receipt['type_families']['other_type_family']) != set(OTHER_TYPES) or
            set(receipt['type_families']['state_local_type_family']) != set(BROADER_TYPES)):
        raise ValueError('screen receipt type-family window mismatch')

    # --- Step 2 --- Derive every observed label from the controlling panel.
    panel = table(paths['panel'], ('final_facility_entity_id', 'display_name',
                                   'observed_flag', 'facility_iids_date',
                                   'type_detailed_as_reported'))
    panel_ids = {row['final_facility_entity_id'] for row in panel if row['final_facility_entity_id']}
    types = defaultdict(set)
    names = {}
    for row in panel:
        if row['observed_flag'] == '1' and START_DATE <= row['facility_iids_date'] <= END_DATE:
            entity_id = row['final_facility_entity_id']
            if not entity_id or not row['type_detailed_as_reported']:
                raise ValueError('observed panel row lacks ID or type')
            types[entity_id].add(row['type_detailed_as_reported'])
            names[entity_id] = row['display_name']
    if set().union(*types.values()) - (IGA_TYPES | OTHER_TYPES | {'STATE', 'FAMILY', 'JUVENILE'}):
        raise ValueError('unclassified observed panel type')

    # --- Step 3 --- Recover a single signed amount per award and validate pairs.
    pairs = table(paths['pairs'], ('facility_entity_id', 'facility_name',
                                   'reported_types', 'type_families',
                                   'award_unique_key', 'award_id_piid',
                                   'selected_25_4_amount', 'shared_award_25_4_amount',
                                   'source_row_link', 'matched_phrase', 'match_tier'))
    seen_pairs = set()
    award_values = defaultdict(set)
    award_keys = set()
    warnings = []
    for row in pairs:
        entity_id, award = row['facility_entity_id'], row['award_unique_key']
        if entity_id not in panel_ids:
            raise ValueError(f'facility ID outside controlling panel: {entity_id}')
        if entity_id not in types:
            raise ValueError(f'facility ID outside observed window: {entity_id}')
        if not award or (entity_id, award) in seen_pairs:
            raise ValueError('blank award key or duplicate facility–award pair')
        seen_pairs.add((entity_id, award))
        award_keys.add(award)
        if set(row['reported_types'].split('|')) != types[entity_id]:
            raise ValueError(f'pair observed-label window mismatch: {entity_id}')
        families = {family for family, members in screen.TYPE_FAMILIES.items()
                    if types[entity_id] & members}
        if set(row['type_families'].split('|')) != families:
            raise ValueError(f'pair type-family window mismatch: {entity_id}')
        link = re.fullmatch(r'\[source row\]\(<(.+):(\d+)>\)', row['source_row_link'])
        if not link:
            warnings.append(f'source row is not directly inspectable: {award}')
        else:
            source_path = Path(link.group(1))
            if link_root is not None:
                root = Path(link_root).resolve()
                if source_path.is_absolute():
                    raise ValueError('portable source-row link must be relative')
                source_path = (root/source_path).resolve()
                if not source_path.is_relative_to(root):
                    raise ValueError('portable source-row link escapes release root')
            elif not source_path.is_absolute():
                source_path = REPO/source_path
            if not source_path.is_file() or int(link.group(2)) < 2:
                warnings.append(f'source row is not directly inspectable: {award}')
        selected, shared = row['selected_25_4_amount'], row['shared_award_25_4_amount']
        if selected and shared:
            raise ValueError('pair has both selected and shared amounts: ' + award)
        if selected or shared:
            award_values[award].add(amount(selected or shared, award))
    if any(len(values) != 1 for values in award_values.values()):
        raise ValueError('conflicting pair amount for one award')
    pair_amounts = {key: next(iter(values)) for key, values in award_values.items()}

    # --- Step 4 --- Sum File C source rows without converting blanks to zero.
    source_rows = table(paths['comparison'], ('source_layer', 'source_row_id',
                         'object_class_code', 'federal_account_symbol',
                         'submission_period', 'calculation_role',
                         'comparison_value_status', 'comparison_amount',
                         'award_unique_key'))
    file_c_total = Decimal('0')
    source_awards = defaultdict(lambda: Decimal('0'))
    numeric_awards = set()
    source_ids = set()
    blank_rows = 0
    for row in source_rows:
        if row['source_layer'] != 'C':
            continue
        if (row['object_class_code'] != '25.4' or
                row['federal_account_symbol'] not in ACCOUNTS or
                row['calculation_role'] != 'period_flow' or
                not (row['submission_period'].startswith('FY2025P') and
                     5 <= int(row['submission_period'][-2:]) <= 12 or
                     row['submission_period'].startswith('FY2026P') and
                     2 <= int(row['submission_period'][-2:]) <= 10)):
            raise ValueError('File C source row outside frozen comparison scope')
        if row['source_row_id'] in source_ids:
            raise ValueError('duplicate File C source row ID')
        source_ids.add(row['source_row_id'])
        if row['comparison_value_status'] == 'blank':
            if row['comparison_amount']:
                raise ValueError('blank File C status has amount')
            blank_rows += 1
            continue
        if row['comparison_value_status'] != 'numeric':
            raise ValueError('unknown File C amount status')
        value = amount(row['comparison_amount'], row['source_row_id'])
        file_c_total += value
        if row['award_unique_key']:
            source_awards[row['award_unique_key']] += value
            numeric_awards.add(row['award_unique_key'])

    # LEARN: a repeated award amount on several facility rows is one award,
    # not several additive financial records. Apply set() inside each group.
    def group_total(selected_pairs):
        awards = {row['award_unique_key'] for row in selected_pairs}
        return len(awards), sum((pair_amounts[key] for key in awards if key in pair_amounts),
                                 Decimal('0'))

    iga_pairs = [row for row in pairs if types[row['facility_entity_id']] & IGA_TYPES]
    other_pairs = [row for row in pairs if types[row['facility_entity_id']] & OTHER_TYPES]
    broader_pairs = [row for row in pairs if types[row['facility_entity_id']] & BROADER_TYPES]
    solely_pairs = [row for row in iga_pairs if types[row['facility_entity_id']] <= IGA_TYPES]
    not_solely_pairs = [row for row in iga_pairs if not types[row['facility_entity_id']] <= IGA_TYPES]
    iga_awards, iga_amount = group_total(iga_pairs)
    other_awards, other_amount = group_total(other_pairs)
    _, solely_amount = group_total(solely_pairs)
    _, not_solely_amount = group_total(not_solely_pairs)
    broader_awards, broader_amount = group_total(broader_pairs)
    both_ids = {eid for eid, kinds in types.items() if kinds & IGA_TYPES and kinds & OTHER_TYPES}
    actual = {
        'roster_entities': len(types),
        'iga_group_entities': sum(bool(kinds & IGA_TYPES) for kinds in types.values()),
        'federal_contract_group_entities': sum(bool(kinds & OTHER_TYPES) for kinds in types.values()),
        'broader_state_local_entities_reference_only': sum(bool(kinds & BROADER_TYPES) for kinds in types.values()),
        'both_group_facility_count': len(both_ids),
        'both_group_facility_names': sorted(names[eid] for eid in both_ids),
        'federal_contract_matched_facilities': len({r['facility_entity_id'] for r in other_pairs}),
        'federal_contract_distinct_awards': other_awards,
        'federal_contract_25_4_amount': money(other_amount),
        'iga_matched_facilities': len({r['facility_entity_id'] for r in iga_pairs}),
        'iga_distinct_awards': iga_awards,
        'iga_25_4_amount': money(iga_amount),
        'solely_iga_facility_ids': sorted({r['facility_entity_id'] for r in solely_pairs}),
        'solely_iga_award_piids': sorted({r['award_id_piid'] for r in solely_pairs}),
        'solely_iga_25_4_amount': money(solely_amount),
        'iga_not_solely_facility_names': sorted({names[r['facility_entity_id']] for r in not_solely_pairs}),
        'iga_not_solely_25_4_amount': money(not_solely_amount),
        'file_c_25_4_amount': money(file_c_total),
        'federal_contract_share_percent': percent(other_amount, file_c_total),
        'iga_share_percent': percent(iga_amount, file_c_total),
    }
    mismatches = {key: {'expected': wanted, 'actual': actual.get(key)}
                  for key, wanted in expected.items() if actual.get(key) != wanted}
    receipt_checks = {
        'roster_entities': (receipt['roster_entities'], len(types)),
        'legacy_iga_subset.roster_entities': (receipt['legacy_iga_subset']['roster_entities'],
                                              actual['iga_group_entities']),
        'other_type_family.distinct_awards': (receipt['family_totals']['other_type_family']['distinct_awards'], other_awards),
        'other_type_family.selected_25_4_amount': (receipt['family_totals']['other_type_family']['selected_25_4_amount'], money(other_amount)),
        'state_local_type_family.distinct_awards': (receipt['family_totals']['state_local_type_family']['distinct_awards'], broader_awards),
        'state_local_type_family.selected_25_4_amount': (receipt['family_totals']['state_local_type_family']['selected_25_4_amount'], money(broader_amount)),
    }
    for key, (saved, computed) in receipt_checks.items():
        if saved != computed:
            mismatches['screen_receipt.' + key] = {'expected': saved, 'actual': computed}
    for award in sorted(award_keys):
        saved = pair_amounts.get(award)
        computed = source_awards.get(award) if award in numeric_awards else None
        if saved != computed:
            mismatches['award_amount.' + award] = {
                'expected_from_file_c_rows': money(computed) if computed is not None else '',
                'actual_pair_amount': money(saved) if saved is not None else '',
            }

    # --- Step 5 --- Emit inspectable IGSA pair rows and a status-bearing receipt.
    matches = []
    for row in sorted(iga_pairs, key=lambda r: (r['facility_entity_id'], r['award_unique_key'])):
        entity_id, award = row['facility_entity_id'], row['award_unique_key']
        value = pair_amounts.get(award)
        matches.append({
            'facility_entity_id': entity_id,
            'facility_name': row['facility_name'],
            'award_unique_key': award,
            'award_id_piid': row['award_id_piid'],
            'solely_iga': str(types[entity_id] <= IGA_TYPES).lower(),
            'observed_labels': '|'.join(sorted(types[entity_id])),
            'award_25_4_amount': money(value) if value is not None else '',
            'amount_status': 'numeric' if value is not None else 'blank',
            'shared_award': str(bool(row['shared_award_25_4_amount'])).lower(),
            'matched_phrase': row['matched_phrase'],
            'match_tier': row['match_tier'],
            'source_row_link': row['source_row_link'],
            'award_url': 'https://www.usaspending.gov/award/' + quote(award, safe=''),
        })
    report = {
        'status': 'WARN' if mismatches or warnings else 'PASS',
        'mismatches': mismatches,
        'warnings': sorted(set(warnings)),
        'actual': actual,
        'expected': expected,
        'input_sha256': hashes,
        'code_version_sha256': sha256(__file__),
        'observation_window': {'start': START_DATE, 'end': END_DATE,
                               'rule': 'observed_flag=1; any observed type in window'},
        'blank_file_c_rows': blank_rows,
        'numeric_file_c_rows': len(source_ids) - blank_rows,
        'igsa_group_pairs': len(matches),
        'both_group_facilities': [
            {'facility_entity_id': eid, 'facility_name': names[eid],
             'observed_labels': sorted(types[eid])} for eid in sorted(both_ids)],
        'limits': ('Amounts are signed selected File C 25.4 obligations per distinct award within each group. '
                   'Groups and award totals overlap; pair rows are not additive facility allocations or proof of IGA payments.'),
    }
    return report, matches


def write_outputs(output, report, matches):
    """Promote the CSV first and its hash-bearing receipt last."""
    output = Path(output)
    if output.is_symlink():
        raise ValueError('output directory must not be a symlink')
    output.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.statistics-', dir=output))
    try:
        csv_path = stage/'igsa_group_matches.csv'
        with csv_path.open('w', newline='', encoding='utf-8') as handle:
            writer = csv.DictWriter(handle, fieldnames=MATCH_FIELDS)
            writer.writeheader()
            writer.writerows(matches)
        report['igsa_group_matches_sha256'] = sha256(csv_path)
        (stage/'statistics_check.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
        os.replace(csv_path, output/csv_path.name)
        os.replace(stage/'statistics_check.json', output/'statistics_check.json')
    finally:
        shutil.rmtree(stage)


def execute(*, paths=PATHS, output=OUTPUT, expected=EXPECTED,
            frozen_hashes=FROZEN_HASHES, strict=False, write=True,
            link_root=None):
    """Return (exit code, receipt): advisory 0, strict warning 1, hard error 2."""
    try:
        if link_root is not None and write:
            root = Path(link_root).resolve()
            if (not Path(output).resolve().is_relative_to(root) or
                    Path(output).is_symlink()):
                raise ValueError('output must be inside release root')
        report, matches = check(paths, expected=expected,
                                frozen_hashes=frozen_hashes, link_root=link_root)
        if write:
            write_outputs(output, report, matches)
        return (1 if strict and report['status'] == 'WARN' else 0), report
    except (ValueError, OSError, KeyError, TypeError) as exc:
        return 2, {'status': 'FAIL', 'error': str(exc)}
