"""Screen approved DDP type families against frozen File C descriptions.

These are candidate description links, not agreement payments or facility costs.
Use the package entry point from the repository root:

    python3 -B File_C_blog_post/run_facility_name_screen.py
"""

import argparse
from collections import defaultdict
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile


REPO = Path(__file__).resolve().parents[2]
BLOG_DIR = REPO / 'File_C_blog_post'
PACKAGE_OUTPUT = BLOG_DIR / 'outputs/facility_name_screen'
PAIR_FIELDS = ('facility_entity_id', 'facility_name', 'reported_types', 'type_families',
               'award_unique_key', 'award_id_piid', 'recipient_names', 'match_tier',
               'matched_phrase', 'matched_file_c_rows', 'example_source_file',
               'example_source_line', 'example_source_end_line', 'source_row_link',
               'award_facility_count', 'selected_25_4_amount', 'shared_award_25_4_amount',
               'pilot_case_id', 'pilot_facility', 'pilot_review_status', 'needs_rereview')
FRAGMENT_REVIEW_FIELDS = ('fragment', 'facility_entity_id', 'target_display_name',
                          'type_families', 'matched_source_rows',
                          'potential_new_source_rows', 'example_description',
                          'example_source_row_link', 'example_award_url',
                          'decision', 'reviewer', 'review_date', 'notes')
PANEL = REPO / 'output/tables/detention_roster_facility_snapshot_panel.csv'
MANIFEST = REPO / 'File_C_blog_post/facility_pilot/v6/source_manifest.json'
BLOG_ROWS = REPO / 'File_C_blog_post/facility_pilot/v6/financial_rows.csv'
FRAGMENTS = BLOG_DIR / 'facility_pilot/review_inputs/facility_name_fragments.csv'
PILOT_DIR = BLOG_DIR / 'facility_pilot/v6'
CAMP_DECISIONS = BLOG_DIR / 'facility_pilot/review_inputs/camp_east_v6_decisions.csv'
FRAGMENT_REVIEW = BLOG_DIR / 'facility_pilot/review_inputs/facility_name_fragment_candidates.csv'
FRAGMENT_USES = BLOG_DIR / 'facility_pilot/review_inputs/facility_name_fragment_uses.csv'
REVIEW_APPROVAL = BLOG_DIR / 'facility_pilot/review_inputs/facility_name_fragment_review_approval.json'
FRAGMENT_USES_FIELDS = ('fragment', 'facility_entity_id', 'target_display_name',
                        'type_families', 'award_unique_key', 'description',
                        'source_row_link', 'source_row_count')
ACCOUNTS = {'070-0540', '070-0545'}
START_DATE = '2025-01-21'
END_DATE = '2026-07-09'
LEGACY_IGA_TYPES = {'IGSA', 'DIGSA', 'USMS IGA'}
LEGACY_REVIEWED_FRAGMENTS = {'T DON HUTTO'}
REVIEWED_AWARD_EXCLUSIONS = {
    ('PORT ISABEL', 'CONT_AWD_70CMSW25FR0000077_7012_47QMCA20D004S_4732'):
        'Utility vehicle description names Port Isabel, TX, not the detention center',
    ('CALIFORNIA CITY', 'CONT_AWD_70CTD025FC0000023_7012_70CTD025A00000001_7012'):
        'Equipment description names an ERO city site, not the detention facility',
}
TYPE_FAMILIES = {
    'state_local_type_family': LEGACY_IGA_TYPES | {'STATE', 'JUVENILE', 'FAMILY'},
    'other_type_family': {'BOP', 'SPC', 'CDF', 'STAGING', 'DOD', 'USMS CDF', 'MOC'},
}
TARGET_TYPES = set().union(*TYPE_FAMILIES.values())


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def normalize(text):
    """Compare whole name phrases after case and punctuation normalization."""
    return ' '.join(re.findall(r'[A-Z0-9]+', (text or '').upper()))


def contains_phrase(description, phrase):
    return ' ' + phrase + ' ' in ' ' + description + ' '


def require_fields(reader, fields, label):
    missing = set(fields) - set(reader.fieldnames or [])
    if missing:
        raise ValueError('missing ' + label + ' fields: ' + ', '.join(sorted(missing)))


def require_portable_paths(link_root, **paths):
    """Portable runs must name every input inside their explicit release root."""
    root = Path(link_root).resolve()
    for name, path in paths.items():
        if path is None or not Path(path).resolve().is_relative_to(root):
            raise ValueError(f'portable {name} must be inside release root')
    return root


def money(value, label):
    if not value:
        return None
    try:
        amount = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError('invalid amount at ' + label) from exc
    if not amount.is_finite():
        raise ValueError('nonfinite amount at ' + label)
    return amount


def review_date_iso(value):
    if not value:
        return ''
    for pattern in ('%Y-%m-%d', '%m/%d/%y'):
        try:
            return datetime.strptime(value, pattern).date().isoformat()
        except ValueError:
            pass
    raise ValueError('invalid fragment review date: ' + value)


def load_roster(path, fragment_path=None):
    entities = defaultdict(lambda: {'names': set(), 'aliases': set(), 'types': set()})
    all_aliases = defaultdict(set)
    panel_ids = set()
    with path.open(newline='', encoding='utf-8-sig') as stream:
        reader = csv.DictReader(stream)
        require_fields(reader, ('observed_flag', 'facility_iids_date',
                                'final_facility_entity_id', 'display_name',
                                'raw_facility_name', 'type_detailed_as_reported'), 'panel')
        for row in reader:
            eid = row['final_facility_entity_id']
            if eid:
                panel_ids.add(eid)
            aliases = {normalize(name) for name in
                       (row['display_name'], row['raw_facility_name'])}
            aliases.discard('')
            if not eid and aliases:
                raise ValueError('roster row with name lacks entity ID')
            all_aliases[eid].update(aliases)
            if (row['observed_flag'] != '1' or
                    not START_DATE <= row['facility_iids_date'] <= END_DATE):
                continue
            if not eid:
                raise ValueError('observed roster row lacks entity ID')
            entity = entities[eid]
            entity['types'].add(row['type_detailed_as_reported'])
            entity['names'].add(row['display_name'])
            entity['aliases'].update(aliases)

    unknown_types = {kind for entity in entities.values() for kind in entity['types']} - TARGET_TYPES
    if unknown_types:
        raise ValueError('unclassified reported roster types: ' + ', '.join(sorted(unknown_types)))
    targets = {eid: entity for eid, entity in entities.items()
               if entity['types'] & TARGET_TYPES}
    full_names = defaultdict(set)
    ambiguous = set()
    for eid, entity in targets.items():
        for alias in entity['aliases']:
            owners = {other for other, names in all_aliases.items()
                      if any(contains_phrase(name, alias) for name in names)}
            if owners != {eid}:
                ambiguous.add(alias)
            elif len(alias) >= 8:
                full_names[alias].add(eid)

    fragments = {}
    accepted_fragment_evidence = []
    with Path(fragment_path or FRAGMENTS).open(newline='', encoding='utf-8-sig') as stream:
        reader = csv.DictReader(stream, strict=True)
        require_fields(reader, ('fragment', 'facility_entity_id', 'target_display_name',
                                'reviewer', 'review_date', 'decision', 'notes'), 'fragment review')
        reviewed_rows = list(reader)
    seen_fragments = set()
    for row in reviewed_rows:
        phrase = row['fragment']
        normalized = normalize(phrase)
        eid = row['facility_entity_id']
        if eid not in panel_ids:
            raise ValueError('fragment entity ID outside controlling panel: ' + eid)
        if normalized in seen_fragments:
            raise ValueError('duplicate reviewed fragment: ' + phrase)
        seen_fragments.add(normalized)
        if row['decision'] not in {'accept', 'reject'}:
            raise ValueError('fragment decision must be accept or reject: ' + phrase)
        if not row['reviewer']:
            raise ValueError('fragment reviewer is required: ' + phrase)
        if not 2 <= len(normalized.split()) <= 4:
            raise ValueError('reviewed fragment must contain two to four words: ' + phrase)
        entity = targets.get(eid)
        if entity is None or normalize(row['target_display_name']) not in {
                normalize(name) for name in entity['names']}:
            raise ValueError('reviewed fragment target missing or ambiguous: ' + phrase)
        matching_entities = {eid for eid, aliases in all_aliases.items()
                             if any(contains_phrase(alias, normalized)
                                    for alias in aliases)}
        if matching_entities != {eid}:
            raise ValueError('reviewed fragment ambiguous across roster: ' + phrase)
        if row['decision'] == 'accept':
            fragments[normalized] = eid
            accepted_fragment_evidence.append({key: row[key] for key in (
                'fragment', 'facility_entity_id', 'target_display_name',
                'reviewer', 'review_date', 'notes')})
    return (targets, full_names, fragments, sorted(ambiguous), all_aliases,
            accepted_fragment_evidence, panel_ids)


def load_pilot_crosswalk(manifest, panel_ids, *, pilot_dir=None,
                         camp_decisions_path=None, link_root=None):
    """Read the frozen v6 review relationship; never import its dollar allocation."""
    expected = manifest['output_hashes']
    paths = {name: Path(pilot_dir or PILOT_DIR) / name for name in
             ('award_period_review.csv', 'review_facilities.csv')}
    for name, path in paths.items():
        if sha256(path) != expected[name]:
            raise ValueError('pilot output hash mismatch: ' + name)
    with paths['award_period_review.csv'].open(newline='', encoding='utf-8-sig') as stream:
        reader = csv.DictReader(stream, strict=True)
        require_fields(reader, ('review_id', 'case_id', 'award_key'), 'pilot awards')
        awards = list(reader)
    with paths['review_facilities.csv'].open(newline='', encoding='utf-8-sig') as stream:
        reader = csv.DictReader(stream, strict=True)
        require_fields(reader, ('review_id', 'facility_entity_id', 'display_name'),
                       'pilot facilities')
        facilities = list(reader)
    decision_path = Path(camp_decisions_path or CAMP_DECISIONS)
    registered_decisions = [item for item in manifest['inputs']
                            if Path(item['path']).name == decision_path.name]
    if (len(registered_decisions) != 1 or
            sha256(decision_path) != registered_decisions[0]['sha256']):
        raise ValueError('Camp East decision hash mismatch')
    with decision_path.open(newline='', encoding='utf-8-sig') as stream:
        reader = csv.DictReader(stream, strict=True)
        require_fields(reader, ('review_id', 'award_key', 'review_decision'),
                       'Camp East decisions')
        decisions = list(reader)
    known_reviews = {(row['review_id'], row['award_key']) for row in awards}
    accepted = set()
    for row in decisions:
        key = (row['review_id'], row['award_key'])
        if key not in known_reviews:
            raise ValueError('Camp East decision not in pilot awards: ' + str(key))
        if row['review_decision'] == 'accept_proposal':
            accepted.add(key)
    by_review = defaultdict(list)
    for row in facilities:
        eid = row['facility_entity_id']
        if eid not in panel_ids:
            raise ValueError('pilot facility ID outside controlling panel: ' + eid)
        by_review[row['review_id']].append(row)
    by_award = defaultdict(lambda: {'case_ids': set(), 'facility_ids': set(),
                                    'facility_names': set(), 'accepted': False})
    for row in awards:
        key = row['award_key']
        entry = by_award[key]
        entry['case_ids'].add(row['case_id'])
        entry['accepted'] |= ((row['review_id'], key) in accepted or
                              row.get('review_decision') == 'accept_proposal')
        for facility in by_review[row['review_id']]:
            entry['facility_ids'].add(facility['facility_entity_id'])
            entry['facility_names'].add(facility['display_name'])
    source_paths = (*paths.values(), decision_path)
    if link_root is not None:
        root = Path(link_root).resolve()
        names = [str(path.resolve().relative_to(root)) for path in source_paths]
    else:
        names = [str(path) for path in source_paths]
    return by_award, dict(zip(names, (sha256(path) for path in source_paths)))


def validate_review_approval(*, review_approval_path=None,
                             fragment_review_path=None, fragment_path=None):
    """Require Kevin's dated approval for the exact review and active fragments."""
    approval_path = Path(review_approval_path or REVIEW_APPROVAL)
    review_path = Path(fragment_review_path or FRAGMENT_REVIEW)
    active_path = Path(fragment_path or FRAGMENTS)
    if not approval_path.is_file():
        raise ValueError('fragment review approval is missing')
    approval = json.loads(approval_path.read_text(encoding='utf-8'))
    if (approval.get('approved_for_production') is not True or
            not approval.get('approved_by') or not approval.get('approved_at')):
        raise ValueError('fragment review approval is incomplete')
    if (approval.get('candidate_csv_sha256') != sha256(review_path) or
            approval.get('active_fragments_sha256') != sha256(active_path)):
        raise ValueError('fragment review approval hash mismatch')
    with review_path.open(newline='', encoding='utf-8-sig') as stream:
        candidates = list(csv.DictReader(stream, strict=True))
    with active_path.open(newline='', encoding='utf-8-sig') as stream:
        active = {normalize(row['fragment']): row for row in csv.DictReader(stream, strict=True)}
    for row in candidates:
        if row['decision']:
            selected = active.get(normalize(row['fragment']))
            decision = 'accept' if row['decision'].strip().lower() in {'approve', 'accept'} else row['decision']
            if (selected is None or selected['decision'] != decision or
                    selected['facility_entity_id'] != row['facility_entity_id'] or
                    selected['reviewer'] != row['reviewer'] or
                    selected['review_date'] != review_date_iso(row['review_date'])):
                raise ValueError('fragment review decision not transferred: ' + row['fragment'])
    return approval


def import_fragment_decisions(review_path, active_path, panel_path):
    """Normalize Kevin's reviewed values; preserve the review CSV verbatim."""
    with Path(active_path).open(newline='', encoding='utf-8-sig') as stream:
        reader = csv.DictReader(stream, strict=True)
        require_fields(reader, ('fragment', 'facility_entity_id', 'target_display_name',
                                'reviewer', 'review_date', 'decision', 'notes'),
                       'active fragments')
        active = list(reader)
    with Path(review_path).open(newline='', encoding='utf-8-sig') as stream:
        reader = csv.DictReader(stream, strict=True)
        require_fields(reader, ('fragment', 'facility_entity_id', 'target_display_name',
                                'reviewer', 'review_date', 'decision', 'notes'),
                       'fragment review queue')
        reviewed = list(reader)
    merged = {normalize(row['fragment']): row for row in active}
    if len(merged) != len(active):
        raise ValueError('duplicate active fragment')
    for row in reviewed:
        decision = row['decision'].strip().lower()
        if not decision:
            continue
        if decision not in {'approve', 'accept', 'reject'}:
            raise ValueError('invalid reviewed fragment decision: ' + row['fragment'])
        if not row['reviewer'] or not row['review_date'] or not row['notes']:
            raise ValueError('decided fragment lacks reviewer, date, or reason: ' + row['fragment'])
        review_date = review_date_iso(row['review_date'])
        selected = {key: row[key] for key in ('fragment', 'facility_entity_id',
                                               'target_display_name', 'reviewer', 'notes')}
        selected['review_date'] = review_date
        selected['decision'] = 'accept' if decision in {'approve', 'accept'} else 'reject'
        key = normalize(row['fragment'])
        # A fresh human decision supersedes an earlier imported decision for
        # the same phrase; the original review CSV remains unchanged.
        merged[key] = selected
    rows = list(merged.values())
    with tempfile.TemporaryDirectory(prefix='fragment-validation-') as folder:
        staged = Path(folder) / 'fragments.csv'
        with staged.open('w', newline='', encoding='utf-8') as stream:
            writer = csv.DictWriter(stream, fieldnames=('fragment', 'facility_entity_id',
                                                         'target_display_name', 'reviewer',
                                                         'review_date', 'decision', 'notes'))
            writer.writeheader()
            writer.writerows(rows)
        load_roster(Path(panel_path), staged)
    return rows


def diagnostic_candidates(targets, all_aliases):
    """Enumerate unique roster word sequences before human fragment review."""
    fragments = defaultdict(set)
    words = defaultdict(set)
    for eid, entity in targets.items():
        for alias in entity['aliases']:
            tokens = alias.split()
            for token in tokens:
                words[token].add(eid)
            for length in (2, 3, 4):
                for start in range(len(tokens) - length + 1):
                    fragments[' '.join(tokens[start:start + length])].add(eid)
    unique_fragments = {}
    for phrase, owners in fragments.items():
        if len(owners) != 1:
            continue
        owner = next(iter(owners))
        if all(not any(contains_phrase(alias, phrase) for alias in aliases)
               for eid, aliases in all_aliases.items() if eid != owner):
            unique_fragments[phrase] = owner
    return unique_fragments, words


def validate_output_path(path, *, root=None):
    """Replace only the canonical or an explicit release-root screen directory."""
    output = Path(path).absolute()
    if root is None:
        expected = PACKAGE_OUTPUT
        allowed_root = BLOG_DIR.resolve()
    else:
        allowed_root = Path(root).resolve()
        expected = allowed_root / 'outputs/facility_name_screen'
    if (output.name != expected.name or
            output.parent.resolve() != expected.parent.resolve() or
            not expected.parent.resolve().is_relative_to(allowed_root) or
            output.parent.is_symlink() or output.is_symlink()):
        if root is None:
            raise ValueError('output must be the canonical facility-name screen directory')
        raise ValueError('output must be the facility-name screen directory under the selected root')
    return expected


def write_package_atomic(output, result):
    """Stage a pair CSV and receipt, then replace their directory together."""
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.' + output.name + '.', dir=output.parent))
    previous = None
    try:
        pairs = stage / 'award_facility_pairs.csv'
        with pairs.open('w', newline='', encoding='utf-8') as stream:
            writer = csv.DictWriter(stream, fieldnames=PAIR_FIELDS, extrasaction='ignore')
            writer.writeheader()
            for row in result['candidate_awards']:
                writer.writerow({**row, 'recipient_names': '|'.join(row['recipient_names']),
                                 'needs_rereview': str(row['needs_rereview']).lower()})
        receipt = {key: value for key, value in result.items() if key != 'candidate_awards'}
        receipt['pair_csv_sha256'] = sha256(pairs)
        (stage / 'verification.json').write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        if output.exists():
            previous = Path(tempfile.mkdtemp(prefix='.' + output.name + '.old.', dir=output.parent))
            previous.rmdir()
            os.replace(output, previous)
        try:
            os.replace(stage, output)
        except BaseException:
            if previous is not None and not output.exists():
                os.replace(previous, output)
                previous = None
            raise
        if previous is not None:
            shutil.rmtree(previous)
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def write_fragment_review(path, result):
    """Build the undecided review queue without overwriting human decisions."""
    path = Path(path)
    if path.exists():
        with path.open(newline='', encoding='utf-8-sig') as stream:
            reader = csv.DictReader(stream)
            require_fields(reader, FRAGMENT_REVIEW_FIELDS, 'fragment review queue')
            if any(any(row.get(field) for field in ('decision', 'reviewer',
                                                     'review_date', 'notes'))
                   for row in reader):
                raise ValueError('fragment review queue has human decisions; refusing overwrite')
    candidates = [row for row in result['fragment_diagnostics']['two_to_four_word_candidates']
                  if row['potential_new_source_rows'] > 0]
    candidates.sort(key=lambda row: (-row['potential_new_source_rows'], row['phrase']))
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', newline='', encoding='utf-8',
                                         dir=path.parent, prefix='.' + path.name + '.',
                                         suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            writer = csv.DictWriter(stream, fieldnames=FRAGMENT_REVIEW_FIELDS)
            writer.writeheader()
            for row in candidates:
                writer.writerow({'fragment': row['phrase'],
                                 **{key: row[key] for key in FRAGMENT_REVIEW_FIELDS
                                    if key in row}})
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def write_fragment_uses(path, result):
    """Write every incremental phrase–award–description use for human review."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', newline='', encoding='utf-8',
                                         dir=path.parent, prefix='.' + path.name + '.',
                                         suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            writer = csv.DictWriter(stream, fieldnames=FRAGMENT_USES_FIELDS)
            writer.writeheader()
            writer.writerows(result['fragment_diagnostics']['potential_new_uses'])
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def load_blog_rows(path, expected_hash, selected_periods):
    if sha256(path) != expected_hash:
        raise ValueError('blog financial-row hash mismatch')
    locators = {}
    amounts = defaultdict(lambda: {'total': Decimal('0'), 'numeric_rows': 0})
    with path.open(newline='', encoding='utf-8-sig') as stream:
        reader = csv.DictReader(stream)
        require_fields(reader, ('source_file_path', 'source_line_number',
                                'award_unique_key', 'federal_account_symbol',
                                'object_class_code', 'submission_period',
                                'parsed_amount'), 'blog financial')
        for row in reader:
            locator = (row['source_file_path'], int(row['source_line_number']))
            if locator in locators:
                raise ValueError('duplicate blog source locator: ' + str(locator))
            if (row['federal_account_symbol'] not in ACCOUNTS or
                    row['object_class_code'] != '25.4' or
                    row['submission_period'] not in selected_periods):
                raise ValueError('blog financial row outside selected scope: ' + str(locator))
            locators[locator] = row
            key = row['award_unique_key']
            if key:
                amount = money(row['parsed_amount'], str(locator))
                if amount is not None:
                    amounts[key]['total'] += amount
                    amounts[key]['numeric_rows'] += 1
    return locators, amounts


def screen(panel_path=None, manifest_path=MANIFEST, blog_path=BLOG_ROWS,
           source_root=None, diagnostics=False, *, fragment_path=None,
           pilot_dir=None, camp_decisions_path=None, link_root=None):
    """Read verified sources and return deterministic search results."""
    if link_root is not None:
        require_portable_paths(
            link_root, fragment_path=fragment_path, panel_path=panel_path,
            manifest_path=manifest_path, blog_path=blog_path,
            source_root=source_root, pilot_dir=pilot_dir,
            camp_decisions_path=camp_decisions_path)
    manifest = json.loads(Path(manifest_path).read_text())
    registered_panels = [item for item in manifest['inputs']
                         if Path(item['path']).name == PANEL.name]
    if panel_path is None:
        panel_path = PANEL if PANEL.exists() else (
            Path(registered_panels[0]['path']) if len(registered_panels) == 1 else PANEL)
    panel_path = Path(panel_path)
    panel_hashes = {item['sha256'] for item in manifest['inputs']
                    if Path(item['path']).name == panel_path.name}
    if len(panel_hashes) != 1 or sha256(panel_path) not in panel_hashes:
        raise ValueError('panel hash mismatch')
    (targets, full_names, fragments, ambiguous, all_aliases,
     fragment_evidence, panel_ids) = load_roster(panel_path, fragment_path)
    pilot, pilot_hashes = load_pilot_crosswalk(
        manifest, panel_ids, pilot_dir=pilot_dir,
        camp_decisions_path=camp_decisions_path, link_root=link_root)
    eligible_fragments, eligible_words = (
        diagnostic_candidates(targets, all_aliases) if diagnostics else ({}, {}))
    fragment_counts = defaultdict(int)
    fragment_new_counts = defaultdict(int)
    fragment_examples = {}
    fragment_uses = {}
    exclusion_uses = {}
    word_counts = defaultdict(int)
    blog, blog_amounts = load_blog_rows(
        Path(blog_path), manifest['output_hashes']['financial_rows.csv'],
        set(manifest['selected_submission_periods']))
    root = Path(source_root or manifest['source_root']).resolve()
    pairs = {}
    seen_blog = set()
    seen_sources = set()
    ice_rows = blank_descriptions = matched_rows = legacy_matched_rows = 0
    legacy_baseline_pairs = set()

    for member in manifest['source_members']:
        relative = Path(member['path'])
        source = (root / relative).resolve()
        if not source.is_relative_to(root):
            raise ValueError('source member escapes source root')
        source_display = (source.relative_to(Path(link_root).resolve()).as_posix()
                          if link_root is not None else str(source))
        if source in seen_sources:
            raise ValueError('duplicate source member: ' + str(relative))
        seen_sources.add(source)
        if sha256(source) != member['sha256']:
            raise ValueError('source hash mismatch: ' + str(relative))
        with source.open(newline='', encoding='utf-8-sig') as stream:
            reader = csv.DictReader(stream)
            require_fields(reader, ('federal_account_symbol',
                                    'prime_award_base_transaction_description',
                                    'transaction_obligated_amount', 'award_unique_key',
                                    'award_id_piid', 'recipient_name', 'object_class_code',
                                    'submission_period'), 'File C')
            previous_end_line = 1
            for row in reader:
                start_line = previous_end_line + 1
                end_line = reader.line_num
                previous_end_line = end_line
                locator = (str(relative), end_line)
                if locator in blog:
                    seen_blog.add(locator)
                    saved_row = blog[locator]
                    for field in ('award_unique_key', 'federal_account_symbol',
                                  'object_class_code', 'submission_period'):
                        if saved_row[field] != row[field]:
                            raise ValueError(f'blog {field} differs from source: {locator}')
                    saved = saved_row['parsed_amount']
                    actual = row['transaction_obligated_amount']
                    if money(saved, str(locator)) != money(actual, str(locator)):
                        raise ValueError('blog amount differs from source: ' + str(locator))
                if row['federal_account_symbol'] not in ACCOUNTS:
                    continue
                ice_rows += 1
                description = normalize(row['prime_award_base_transaction_description'])
                if not description:
                    blank_descriptions += 1
                    continue
                if diagnostics:
                    tokens = description.split()
                    candidate_phrases = set()
                    for word in set(tokens) & eligible_words.keys():
                        word_counts[word] += 1
                    for length in (2, 3, 4):
                        phrases = {' '.join(tokens[start:start + length])
                                   for start in range(len(tokens) - length + 1)}
                        for phrase in phrases & eligible_fragments.keys():
                            fragment_counts[phrase] += 1
                            candidate_phrases.add(phrase)
                hits = {}
                for phrase, owners in full_names.items():
                    if contains_phrase(description, phrase):
                        for eid in owners:
                            old = hits.get(eid)
                            if old is None or len(phrase) > len(old[1]):
                                hits[eid] = ('full_name', phrase)
                # Freeze the earlier IGA method: full names plus its original
                # T DON HUTTO exception, before newer reviewed fragments enter.
                baseline_ids = {eid for eid in hits
                                if targets[eid]['types'] & LEGACY_IGA_TYPES}
                for phrase in LEGACY_REVIEWED_FRAGMENTS:
                    eid = fragments.get(phrase)
                    if (eid and targets[eid]['types'] & LEGACY_IGA_TYPES and
                            contains_phrase(description, phrase)):
                        baseline_ids.add(eid)
                if baseline_ids:
                    legacy_matched_rows += 1
                    if not row['award_unique_key']:
                        raise ValueError('legacy matched File C row lacks award key: ' + str(locator))
                    legacy_baseline_pairs.update((eid, row['award_unique_key'])
                                                 for eid in baseline_ids)
                for phrase, eid in fragments.items():
                    exclusion_key = (phrase, row['award_unique_key'])
                    if (exclusion_key in REVIEWED_AWARD_EXCLUSIONS and
                            contains_phrase(description, phrase)):
                        exclusion_uses.setdefault(exclusion_key, {
                            'fragment': phrase,
                            'award_unique_key': row['award_unique_key'],
                            'reason': REVIEWED_AWARD_EXCLUSIONS[exclusion_key],
                            'source_row_link': f'[source row](<{source_display}:{start_line}>)',
                        })
                        continue
                    if eid not in hits and contains_phrase(description, phrase):
                        hits[eid] = ('reviewed_fragment', phrase)
                if diagnostics:
                    for phrase in candidate_phrases:
                        if eligible_fragments[phrase] not in hits:
                            fragment_new_counts[phrase] += 1
                            key = (phrase, row['award_unique_key'], description)
                            use = fragment_uses.setdefault(key, {
                                'fragment': phrase,
                                'facility_entity_id': eligible_fragments[phrase],
                                'target_display_name': sorted(
                                    targets[eligible_fragments[phrase]]['names'])[0],
                                'type_families': '|'.join(sorted(
                                    family for family, kinds in TYPE_FAMILIES.items()
                                    if targets[eligible_fragments[phrase]]['types'] & kinds)),
                                'award_unique_key': row['award_unique_key'],
                                'description': row['prime_award_base_transaction_description'],
                                'source_row_link': f'[source row](<{source_display}:{start_line}>)',
                                'source_row_count': 0,
                            })
                            use['source_row_count'] += 1
                            fragment_examples.setdefault(phrase, {
                                'example_source_row_link': f'[source row](<{source_display}:{start_line}>)',
                                'example_award_url': ('https://www.usaspending.gov/award/' +
                                                      row['award_unique_key'])
                                if row['award_unique_key'] else '',
                                'example_description': row['prime_award_base_transaction_description'][:300],
                            })
                if hits:
                    matched_rows += 1
                for eid, (tier, phrase) in hits.items():
                    award = row['award_unique_key']
                    if not award:
                        raise ValueError('matched File C row lacks award key: ' + str(locator))
                    pair = pairs.setdefault((eid, award), {
                        'facility_entity_id': eid,
                        'facility_name': sorted(targets[eid]['names'])[0],
                        'reported_types': '|'.join(sorted(targets[eid]['types'])),
                        'type_families': '|'.join(sorted(
                            family for family, kinds in TYPE_FAMILIES.items()
                            if targets[eid]['types'] & kinds)),
                        'award_unique_key': award,
                        'award_id_piid': row['award_id_piid'],
                        'recipient_names': set(),
                        'match_tier': tier,
                        'matched_phrase': phrase,
                        'matched_file_c_rows': 0,
                        'example_source_file': str(relative),
                        'example_source_line': start_line,
                        'example_source_end_line': end_line,
                        'source_row_link': f'[source row](<{source_display}:{start_line}>)',
                    })
                    pair['matched_file_c_rows'] += 1
                    pair['recipient_names'].add(row['recipient_name'])
                    if pair['match_tier'] != 'full_name' and tier == 'full_name':
                        pair['match_tier'], pair['matched_phrase'] = tier, phrase

    if seen_blog != set(blog):
        raise ValueError('blog financial rows not all found in registered sources')
    candidates = []
    pilot_conflicts = []
    award_facilities = defaultdict(set)
    for eid, award in pairs:
        award_facilities[award].add(eid)
    distinct_amount = Decimal('0')
    numeric_awards = 0
    for award in award_facilities:
        selected = blog_amounts.get(award)
        if selected and selected['numeric_rows']:
            distinct_amount += selected['total']
            numeric_awards += 1
    for (eid, award), pair in sorted(pairs.items()):
        pair['recipient_names'] = sorted(pair['recipient_names'])
        selected = blog_amounts.get(award)
        amount = (f"{selected['total']:.2f}"
                  if selected and selected['numeric_rows'] else '')
        shared = len(award_facilities[award]) > 1
        pair['award_facility_count'] = len(award_facilities[award])
        pair['selected_25_4_amount'] = '' if shared else amount
        pair['shared_award_25_4_amount'] = amount if shared else ''
        pilot_entry = pilot.get(award)
        pair['pilot_case_id'] = '|'.join(sorted(pilot_entry['case_ids'])) if pilot_entry else ''
        pair['pilot_facility'] = '|'.join(sorted(pilot_entry['facility_names'])) if pilot_entry else ''
        pair['pilot_review_status'] = ('accepted' if pilot_entry['accepted'] else 'proposal') if pilot_entry else 'none'
        pair['needs_rereview'] = bool(pilot_entry)
        if pilot_entry and eid not in pilot_entry['facility_ids']:
            pilot_conflicts.append({'award_unique_key': award, 'screen_facility_entity_id': eid,
                                    'pilot_facility_entity_ids': sorted(pilot_entry['facility_ids']),
                                    'pilot_case_ids': sorted(pilot_entry['case_ids'])})
        candidates.append(pair)
    def award_total(award_keys):
        keys = set(award_keys)
        numeric = {key for key in keys if blog_amounts.get(key) and
                   blog_amounts[key]['numeric_rows']}
        return {'distinct_awards': len(keys), 'numeric_25_4_awards': len(numeric),
                'selected_25_4_amount': f"{sum((blog_amounts[key]['total'] for key in numeric), Decimal('0')):.2f}"}

    family_totals = {
        family: award_total(award for (eid, award), pair in pairs.items()
                            if family in pair['type_families'].split('|'))
        for family in TYPE_FAMILIES}
    legacy_entities = {eid for eid, entity in targets.items()
                       if entity['types'] & LEGACY_IGA_TYPES}
    legacy_total = award_total(award for _, award in legacy_baseline_pairs)
    legacy_total.update({'roster_entities': len(legacy_entities),
                         'matched_source_rows': legacy_matched_rows,
                         'candidate_pairs': len(legacy_baseline_pairs),
                         'matched_roster_entities': len({eid for eid, _ in legacy_baseline_pairs})})
    expanded_legacy_awards = {award for eid, award in pairs if eid in legacy_entities}
    baseline_legacy_awards = {award for _, award in legacy_baseline_pairs}
    new_legacy_awards = sorted(expanded_legacy_awards - baseline_legacy_awards)
    new_legacy_total = award_total(new_legacy_awards)
    new_legacy_total['award_unique_keys'] = new_legacy_awards
    other_total = Decimal(family_totals['other_type_family']['selected_25_4_amount'])
    old_figure = Decimal('2420000000')
    result = {
        'input_sha256': {
            'panel': sha256(panel_path),
            'source_manifest': sha256(Path(manifest_path)),
            'financial_rows': sha256(Path(blog_path)),
            'reviewed_fragments': sha256(Path(fragment_path or FRAGMENTS)),
            'pilot_files': pilot_hashes,
            'source_members': {item['path']: item['sha256'] for item in manifest['source_members']},
        },
        'roster_entities': len(targets),
        'target_types': sorted(TARGET_TYPES),
        'type_families': {family: sorted(kinds) for family, kinds in TYPE_FAMILIES.items()},
        'legacy_iga_subset': legacy_total,
        'new_fragment_additions_to_legacy_iga_subset': new_legacy_total,
        'family_totals': family_totals,
        'overall_total': award_total(award_facilities),
        'prior_unreproduced_figures': [{
            'label': 'prior federal-facility prose figure',
            'amount': '2420000000 (approx, as stated)',
            'source': 'IGSA_DDP_DESCRIPTION_SCREEN.md @ eb9c344',
            'computed_other_type_family_amount': f'{other_total:.2f}',
            'computed_minus_prior_amount': f'{other_total-old_figure:.2f}',
            'needs_rereview': True,
        }],
        'ambiguous_full_aliases_excluded': ambiguous,
        'retained_reviewed_fragments': sorted(fragments),
        'accepted_fragment_evidence': fragment_evidence,
        'reviewed_award_exclusions_applied': [exclusion_uses[key]
                                               for key in sorted(exclusion_uses)],
        'reviewed_award_exclusions_not_observed': [
            {'fragment': phrase, 'award_unique_key': award}
            for phrase, award in sorted(set(REVIEWED_AWARD_EXCLUSIONS) - set(exclusion_uses))],
        'source_members_verified': len(manifest['source_members']),
        'ice_rows': ice_rows,
        'blank_descriptions': blank_descriptions,
        'matched_source_rows': matched_rows,
        'candidate_pairs': len(candidates),
        'distinct_matched_awards': len(award_facilities),
        'matched_awards_with_numeric_25_4_amount': numeric_awards,
        'distinct_matched_award_25_4_amount': (
            f"{distinct_amount:.2f}" if numeric_awards else ''),
        'matched_roster_entities': len({r['facility_entity_id'] for r in candidates}),
        'candidate_awards': candidates,
        'pilot_conflicts': pilot_conflicts,
        'pilot_input_sha256': pilot_hashes,
    }
    if diagnostics:
        result['fragment_diagnostics'] = {
            'two_to_four_word_candidates': [
                {'phrase': phrase, 'facility_entity_id': eligible_fragments[phrase],
                 'target_display_name': sorted(targets[eligible_fragments[phrase]]['names'])[0],
                 'type_families': '|'.join(sorted(
                     family for family, kinds in TYPE_FAMILIES.items()
                     if targets[eligible_fragments[phrase]]['types'] & kinds)),
                 'matched_source_rows': count,
                 'potential_new_source_rows': fragment_new_counts[phrase],
                 **fragment_examples.get(phrase, {'example_source_row_link': '',
                                                  'example_award_url': '',
                                                  'example_description': ''})}
                for phrase, count in sorted(fragment_counts.items())],
            'single_word_candidates': [
                {'word': word, 'target_entity_count': len(eligible_words[word]),
                 'matched_source_rows': count}
                for word, count in sorted(word_counts.items())],
            'potential_new_uses': [fragment_uses[key] for key in sorted(fragment_uses)],
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--panel', type=Path,
                        help='Panel path; default checks the repo panel, then its manifest path')
    parser.add_argument('--source-manifest', type=Path, default=MANIFEST)
    parser.add_argument('--blog-financial', type=Path, default=BLOG_ROWS)
    parser.add_argument('--source-root', type=Path,
                        help='Override the frozen external source root in the manifest')
    parser.add_argument('--diagnose-fragments', action='store_true',
                        help='Also enumerate unique two-to-four-word and single-word search leads')
    parser.add_argument('--fragment-review', action='store_true',
                        help='Write the undecided canonical fragment review CSV')
    parser.add_argument('--fragment-uses', action='store_true',
                        help='Write all incremental phrase–award–description uses without touching decisions')
    args = parser.parse_args()
    result = screen(args.panel, args.source_manifest, args.blog_financial,
                    args.source_root, args.diagnose_fragments or args.fragment_review or args.fragment_uses)
    if args.fragment_review:
        write_fragment_review(FRAGMENT_REVIEW, result)
    if args.fragment_review or args.fragment_uses:
        write_fragment_uses(FRAGMENT_USES, result)
    if args.fragment_review or args.fragment_uses:
        print(json.dumps({'fragment_review': str(FRAGMENT_REVIEW),
                          'fragment_uses': str(FRAGMENT_USES),
                          'incremental_leads': sum(
                              row['potential_new_source_rows'] > 0 for row in
                              result['fragment_diagnostics']['two_to_four_word_candidates'])},
                         indent=2))
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
