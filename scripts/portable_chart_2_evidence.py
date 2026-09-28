"""Make and verify release-only Chart 2 evidence with contact details removed.

Original evidence remains the authority. The released copies preserve every
classification field; a pinned receipt connects the changed descriptions to
their original record hashes without publishing the contact strings.
"""

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

PROVENANCE = 'provenance'
RECEIPT = 'provenance/portable_chart_2_evidence_lineage.json'
SOURCE_HASHES = {
    'chart_2_entity_evidence.json': 'e543b5724281eb67ea58d34adc2f5d59bb4ea3d3d0a22c5f63c773bf432203d6',
    'object_class_25_2_entity_evidence.json': '7064ca290604d427cd41d4b1382347c2bcd1442b1384cfce914d69389b4fba48',
    'shared_25_4_award_check.json': '582774f5e574329e1484d9cc02a636862869a418b7dfec0991727bb150ba7706',
    'object_class_25_2_source_context.json': '3b5f97caa94df6d6b2557b0c165342bc84fdd19b2c3fb3df39dd71b1288c31f2',
}
EXPECTED_CONTACT_PATHS = {
    ('chart_2_entity_evidence.json', 'RW46YPUKDTV5', None): (1, 1),
    ('chart_2_entity_evidence.json', 'VYUMS7L1EGL1', None): (0, 1),
    ('object_class_25_2_entity_evidence.json', 'uei:K5WASFGRFAG5', 0): (1, 1),
    ('shared_25_4_award_check.json', 'uei:VYUMS7L1EGL1', 0): (0, 1),
}
EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
PHONE = re.compile(r'(?<!\d)(?:\+1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}(?!\d)')
UPSTREAM_HELPER = 'usaspending_api/common/helpers/business_categories_helper.py'
RELEASE_RECEIPT_SHA = 'f99aa1930248ec4d98e338dbe509fd832caf59bbf08d86e32a104fc070974dcb'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def write_json(path, value):
    path = Path(path)
    if path.is_symlink():
        raise ValueError('release derivative destination must not be a symlink')
    with tempfile.NamedTemporaryFile('w', dir=path.parent, prefix='.portable-chart2-',
                                     encoding='utf-8', delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(json.dumps(value, indent=2, sort_keys=True) + '\n')
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def contact_copy(source, name):
    result = deepcopy(source)
    changes = []
    records = result['records']
    if isinstance(records, list):
        selected = ((row['uei'], None, row, row) for row in records)
    else:
        selected = ((key, index, award, record)
                    for key, record in records.items()
                    for index, award in enumerate(record.get('awards', [])))
    for key, index, target, record in selected:
        description = target.get('description', '')
        emails = len(EMAIL.findall(description))
        phones = len(PHONE.findall(description))
        if not (emails or phones):
            continue
        marker = (name, key, index)
        if EXPECTED_CONTACT_PATHS.get(marker) != (emails, phones):
            raise ValueError('contact redaction appeared at an unapproved evidence field')
        original_record = digest(record)
        revised = PHONE.sub('[CONTACT PHONE REMOVED]',
                            EMAIL.sub('[CONTACT EMAIL REMOVED]', description))
        if EMAIL.search(revised) or PHONE.search(revised):
            raise ValueError('contact redaction left a contact pattern')
        target['description'] = revised
        changes.append({'file': name, 'record_key': key, 'award_index': index,
                        'email_count': emails, 'phone_count': phones,
                        'original_description_sha256': hashlib.sha256(description.encode()).hexdigest(),
                        'derived_description_sha256': hashlib.sha256(revised.encode()).hexdigest(),
                        'original_record_sha256': original_record,
                        'derived_record_sha256': digest(record)})
    expected = {marker for marker in EXPECTED_CONTACT_PATHS if marker[0] == name}
    observed = {(row['file'], row['record_key'], row['award_index']) for row in changes}
    if observed != expected:
        raise ValueError('approved contact-redaction field was not found')
    return result, changes


def derive(original_project, output):
    """Create four public-safe copies and one non-sensitive lineage receipt."""
    source = Path(original_project)/PROVENANCE
    output = Path(output)
    if output.resolve() == source.resolve() or output.is_symlink():
        raise ValueError('release derivatives must not overwrite original evidence')
    output.mkdir(parents=True, exist_ok=True)
    originals = {}
    for name, expected in SOURCE_HASHES.items():
        path = source/name
        if sha(path) != expected:
            raise ValueError('original evidence hash changed: ' + name)
        originals[name] = json.loads(path.read_text(encoding='utf-8'))
    derived = {}
    redactions = []
    for name in list(SOURCE_HASHES)[:3]:
        derived[name], changes = contact_copy(originals[name], name)
        redactions.extend(changes)
    context = deepcopy(originals['object_class_25_2_source_context.json'])
    old_helper = context['helper_source']
    if not (Path(old_helper).is_absolute() and old_helper.endswith(UPSTREAM_HELPER)):
        raise ValueError('source-context helper path changed')
    if sha(old_helper) != context['helper_sha256']:
        raise ValueError('source-context helper bytes changed')
    if context['protected_sha256']['provenance/chart_2_entity_evidence.json'] != SOURCE_HASHES['chart_2_entity_evidence.json']:
        raise ValueError('source-context Chart 2 evidence hash changed')
    context['helper_source'] = ('https://github.com/fedspendingtransparency/usaspending-api/blob/'
                                + context['api_source_commit'] + '/' + UPSTREAM_HELPER)
    # The official commit-pinned URL and exact helper bytes were verified before
    # this release transformation; helper_sha256 remains unchanged.
    for name, value in derived.items():
        write_json(output/name, value)
    context['protected_sha256']['provenance/chart_2_entity_evidence.json'] = sha(output/'chart_2_entity_evidence.json')
    derived['object_class_25_2_source_context.json'] = context
    write_json(output/'object_class_25_2_source_context.json', context)
    receipt = {'schema': 'portable-chart-2-evidence-1',
               'original_sha256': SOURCE_HASHES,
               'derived_sha256': {name: sha(output/name) for name in SOURCE_HASHES},
               'source_context_rebaseline': {
                   'previous_context_sha256': '18fb2ed92d0d3a3964363647cf9c80ee0b5ebfdda0576b2922ae55c04d9104e9',
                   'changed_protected_files': {
                       'scripts/chart_style.py': {
                           'previous_sha256': '1cc45c47d46f973431e2aff54d7e41239cf8690ac4f608f4e10b79716c959946',
                           'current_sha256': '2b60b3fc05d16679db97daea3004b5f118c8396e036eee9391cbf3d2a9cdaa15',
                       },
                       'scripts/prepare_chart_data.py': {
                           'previous_sha256': 'f237068f4ab5017d299a965102ad52f7943e99498104b323fb490a4c409d47f9',
                           'current_sha256': '7a7d488d9efbf8efa69a045d31703ead7f44a45a1628b5fba77202a0d55237f6',
                       },
                   },
                   'check': 'Pinned and current File C readers produced identical selected rows and checks for both frozen FY2025 and FY2026 source ZIPs; the style change adds Figure B colors only.',
               },
               'redactions': redactions,
               'context_change': {
                   'field': 'helper_source',
                   'original_value_sha256': hashlib.sha256(old_helper.encode()).hexdigest(),
                   'derived_value': context['helper_source'],
                   'protected_chart_2_evidence_sha256': sha(output/'chart_2_entity_evidence.json'),
               }}
    write_json(output/'portable_chart_2_evidence_lineage.json', receipt)
    return receipt


def validate_bundle(project):
    """Return trusted release lineage, or None for the unchanged canonical run."""
    project = Path(project).resolve()
    receipt_path = project/RECEIPT
    if not receipt_path.exists():
        sources = [project/PROVENANCE/name for name in SOURCE_HASHES]
        if any(path.is_file() and sha(path) != SOURCE_HASHES[path.name]
               for path in sources):
            raise ValueError('portable Chart 2 evidence lineage receipt is missing')
        return None
    if (receipt_path.is_symlink() or not receipt_path.resolve().is_relative_to(project) or
            not RELEASE_RECEIPT_SHA or
            sha(receipt_path) != RELEASE_RECEIPT_SHA):
        raise ValueError('portable Chart 2 evidence receipt hash mismatch')
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    if (receipt.get('schema') != 'portable-chart-2-evidence-1' or
            receipt.get('original_sha256') != SOURCE_HASHES or
            len(receipt.get('redactions', [])) != len(EXPECTED_CONTACT_PATHS)):
        raise ValueError('portable Chart 2 evidence lineage changed')
    observed = {(r['file'], r['record_key'], r['award_index']) for r in receipt['redactions']}
    if observed != set(EXPECTED_CONTACT_PATHS):
        raise ValueError('portable Chart 2 redaction keys changed')
    for name in SOURCE_HASHES:
        path = project/PROVENANCE/name
        if (path.is_symlink() or not path.resolve().is_relative_to(project) or
                sha(path) != receipt['derived_sha256'][name]):
            raise ValueError('portable Chart 2 evidence hash mismatch: ' + name)
    context = json.loads((project/PROVENANCE/'object_class_25_2_source_context.json').read_text())
    if (context['helper_source'] != receipt['context_change']['derived_value'] or
            context['protected_sha256']['provenance/chart_2_entity_evidence.json'] !=
            receipt['derived_sha256']['chart_2_entity_evidence.json']):
        raise ValueError('portable Chart 2 context lineage mismatch')
    records = json.loads((project/PROVENANCE/'object_class_25_2_entity_evidence.json').read_text())['records']
    for change in receipt['redactions']:
        name, key = change['file'], change['record_key']
        if name != 'object_class_25_2_entity_evidence.json':
            continue
        record = records[key]
        award = record['awards'][change['award_index']]
        if (digest(record) != change['derived_record_sha256'] or
                hashlib.sha256(award['description'].encode()).hexdigest() !=
                change['derived_description_sha256']):
            raise ValueError('portable Chart 2 approval record changed')
    return receipt
