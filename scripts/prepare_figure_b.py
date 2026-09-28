"""Calculate the three approved Figure B shares from frozen local sources."""
import csv
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
import os
from pathlib import Path
import tempfile

TYPES = frozenset({'IGSA', 'DIGSA', 'USMS IGA'})
ICE_ONLY = frozenset({'IGSA', 'DIGSA'})
DATE = '2026-07-09'
PANEL = 'output/tables/detention_roster_facility_snapshot_panel.csv'
CHART = 'outputs/chart_2/recipient_type_totals.csv'
CLASSIFICATION = 'outputs/chart_2/recipient_classification.csv'
EXPECTED_CHART_SHA = '5d40e502de0f837f6c07a693434e9d51db377e27c9739d2312d9e4c1480d1c5c'
EXPECTED_PANEL_SHA = '021d3f49c5e9893b11cfb2f9d84778634dcca2735de911ef4a1259872135ae6c'
EXPECTED_PORTABLE_PANEL_SHA = '24fb15db3a73d51d0c39068ba2764b60c15247336cd016f88c8c74ffcc2dc19b'
EXPECTED_RULEBOOK_SHA = 'c76bb5c4066ad61d4e8da9970884e549fdaa4d6a04e85abd7b351ebc05972f9a'
EXPECTED_PORTABLE_RULEBOOK_SHA = '4d46c9d94f51b9f96dd7200103b8498d9002af4e3b25d32022bdf99a516d9d3f'
EXPECTED_PORTABLE_RULEBOOK_RECEIPT_SHA = '8a000464856f3eaafac1cdfc144aa4a3bf946fc3318a08449f530bef71487f34'


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rows(path):
    with Path(path).open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle, strict=True))


def prepare(project, output, *, panel_path=None, rulebook_path=None):
    project = Path(project).resolve()
    repository = project.parent
    portable = panel_path is not None or rulebook_path is not None
    if portable and (panel_path is None or rulebook_path is None):
        raise ValueError('portable Figure B requires both panel and rulebook paths')
    panel_path = Path(panel_path or repository/PANEL).resolve()
    rulebook_path = Path(rulebook_path or repository/'docs/semantic_rulebook.md').resolve()
    if portable and (not panel_path.is_relative_to(project) or
                     not rulebook_path.is_relative_to(project)):
        raise ValueError('portable Figure B inputs must be inside release root')
    if portable and (not Path(output).resolve().is_relative_to(project) or
                     Path(output).is_symlink()):
        raise ValueError('portable Figure B output must be inside release root')
    if portable and sha256(panel_path) not in {EXPECTED_PANEL_SHA, EXPECTED_PORTABLE_PANEL_SHA}:
        raise ValueError('portable Figure B panel hash mismatch')
    if portable:
        rulebook_sha = sha256(rulebook_path)
        if rulebook_sha not in {EXPECTED_RULEBOOK_SHA, EXPECTED_PORTABLE_RULEBOOK_SHA}:
            raise ValueError('portable Figure B rulebook hash mismatch')
        if rulebook_sha == EXPECTED_PORTABLE_RULEBOOK_SHA:
            receipt_path = project/'provenance/portable_rulebook_lineage.json'
            if (not receipt_path.is_file() or receipt_path.is_symlink() or
                    sha256(receipt_path) != EXPECTED_PORTABLE_RULEBOOK_RECEIPT_SHA):
                raise ValueError('portable Figure B rulebook lineage mismatch')
            receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
            if (receipt.get('schema') != 'portable-rulebook-1' or
                    receipt.get('original_sha256') != EXPECTED_RULEBOOK_SHA or
                    receipt.get('derived_sha256') != rulebook_sha):
                raise ValueError('portable Figure B rulebook lineage changed')
    panel_label = panel_path.relative_to(project).as_posix() if portable else PANEL
    rulebook_label = (rulebook_path.relative_to(project).as_posix()
                      if portable else 'docs/semantic_rulebook.md')
    rulebook = rulebook_path.read_text()
    if '`state_local` contains STATE, IGSA, DIGSA, and USMS IGA' not in rulebook:
        raise ValueError('governing state_local type set changed')
    observed = [r for r in rows(panel_path) if r['facility_iids_date'] == DATE and r['observed_flag'] == '1']
    if len(observed) != 208 or len({r['final_facility_entity_id'] for r in observed}) != 208:
        raise ValueError('July 9 controlling roster count or identity changed')
    if any(not r['type_detailed_as_reported'] for r in observed):
        raise ValueError('observed roster has a missing facility type')
    state_rows = [r for r in observed if r['type_detailed_as_reported'] == 'STATE']
    if len(state_rows) != 1 or state_rows[0]['display_name'] != 'BAKER CORRECTIONAL INSTITUTION':
        raise ValueError('July STATE exclusion no longer identifies Baker alone')
    selected = [r for r in observed if r['type_detailed_as_reported'] in TYPES]
    ice_only = [r for r in observed if r['type_detailed_as_reported'] in ICE_ONLY]
    if len(selected) != 168 or len(ice_only) != 64 or sum(r['type_detailed_as_reported']=='USMS IGA' for r in observed) != 104:
        raise ValueError('published July facility group controls changed')
    complete, missing = [], []
    for row in observed:
        levels = [row[k] for k in ('level_a','level_b','level_c','level_d')]
        (complete if all(levels) else missing).append(row)
    def adp(group):
        return sum((sum((Decimal(r[k]) for k in ('level_a','level_b','level_c','level_d')), Decimal(0)) for r in group), Decimal(0))
    total_adp, selected_adp, ice_adp = adp(complete), adp([r for r in complete if r in selected]), adp([r for r in complete if r in ice_only])
    if missing or total_adp.quantize(Decimal('1'), rounding=ROUND_HALF_UP) != 62517:
        raise ValueError('July ADP control or completeness changed')
    chart_path = project/CHART
    chart_sha = sha256(chart_path)
    verification = json.loads((project/'outputs/chart_2/verification.json').read_text())
    if chart_sha != EXPECTED_CHART_SHA or verification['output_sha256'][chart_path.name] != chart_sha:
        raise ValueError('Chart 2 recipient totals differ from its verified fingerprint')
    chart = rows(chart_path)
    local = [r for r in chart if r['type']=='State and local governments']
    if len(local)!=1 or any(not r['amount'] for r in chart):
        raise ValueError('Chart 2 category values missing or duplicated')
    local_amount = Decimal(local[0]['amount'])
    chart_total = sum((Decimal(r['amount']) for r in chart), Decimal(0))
    if (local_amount, chart_total) != (Decimal('-28520.00'), Decimal('3136530747.79')):
        raise ValueError('Chart 2 obligation controls changed')
    recipients = [r for r in rows(project/CLASSIFICATION) if r['type']=='State and local governments']
    names = {r['recipient_name'].upper().strip() for r in recipients}
    if len(recipients)!=3 or names != {'IMPERIAL COUNTY','COUNTY OF IMPERIAL','CITY OF COTTAGE GROVE'}:
        raise ValueError('local government identities need renewed review')
    government_entities = 2
    def output_row(metric,label,num,den,unit,source,secondary_num='',secondary_share=''):
        return {'metric':metric,'label':label,'numerator':str(num),'denominator':str(den),
                'share_percent':str(Decimal(num)/Decimal(den)*100),'unit':unit,'source_path':source,
                'ice_only_numerator':str(secondary_num),'ice_only_share_percent':str(secondary_share)}
    data = [output_row('facilities','Detention facilities listed under state or local agreements',len(selected),len(observed),'facilities',panel_label,
                       len(ice_only),Decimal(len(ice_only))/len(observed)*100),
            output_row('reported_adp','Detainees held at those facilities (average daily population)',selected_adp,total_adp,'derived reported ADP',panel_label,
                       ice_adp,ice_adp/total_adp*100),
            output_row('facility_obligations','Award-linked facility obligations to state or local governments',local_amount,chart_total,'signed dollars',CHART)]
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    data_path = output/'figure_b_data.csv'
    if portable and data_path.is_symlink():
        raise ValueError('portable Figure B data file must not be a symlink')
    with tempfile.NamedTemporaryFile('w', newline='', encoding='utf-8',
                                     dir=output, prefix='.figure_b_data.',
                                     delete=False) as handle:
        temporary = Path(handle.name)
        writer=csv.DictWriter(handle,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
    try:
        os.replace(temporary, data_path)
    finally:
        temporary.unlink(missing_ok=True)
    return {'status':'PASS','roster_date':DATE,'observed_facilities':len(observed),
            'state_local_facilities':len(selected),'usms_iga_facilities':104,
            'excluded_state_facilities':len(state_rows),
            'excluded_state_facility_id':state_rows[0]['final_facility_entity_id'],
            'excluded_state_facility_name':state_rows[0]['display_name'],
            'excluded_state_reported_adp':str(adp(state_rows)),
            'ice_only_facilities':len(ice_only),'reported_adp_total':str(total_adp),
            'reported_adp_state_local':str(selected_adp),'reported_adp_ice_only':str(ice_adp),
            'incomplete_adp_facilities':len(missing),'local_government_recipient_keys':3,
            'local_government_entities':government_entities,'obligations_local':str(local_amount),
            'obligations_total':str(chart_total),'source_sha256':{panel_label:sha256(panel_path),CHART:chart_sha,
                CLASSIFICATION:sha256(project/CLASSIFICATION),rulebook_label:sha256(rulebook_path)},
            'limits':'Figure B excludes Baker Correctional Institution, the one July STATE facility; the unchanged Figure A map includes it in its state/local contracting group. Roster agreement type does not establish operator or payment channel. This analysis does not test whether File C captures all IGSA-related detention payments. Negative net amounts have a visual minimum marker at zero. July roster and February 2025-July 2026 obligations use different time frames.'}
