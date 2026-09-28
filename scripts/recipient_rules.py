"""Apply Kevin's approved, frozen 400-recipient private-entity rule offline.

Run once with --apply; ordinary builds only validate its receipt and evidence.
This is rule approval, not a claim of individual human review. No network calls.
"""
import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path

RULE_ID='private_entity_strong_labels_v1'
RECEIPT='provenance/private_entity_rule_v1.json'
STRONG_LABELS=frozenset({'Corporate Entity Not Tax Exempt',
    'Partnership or Limited Liability Partnership','Sole Proprietorship',
    'Subchapter S Corporation','Limited Liability Corporation','Small Business'})


def evidence_hash(record):
    return hashlib.sha256(json.dumps(record,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def eligible(uei,record):
    from scripts.object_class_25_2_recipients import propose
    awards=record.get('awards',[])
    if not uei or not awards:return False
    for award in awards:
        rec=award.get('recipient') or {}
        if (award.get('error') or award.get('identity_matches') is not True
                or rec.get('recipient_uei')!=uei
                or not award.get('award_unique_key')
                or award.get('returned_award_key')!=award['award_unique_key']
                or award.get('request_url')!='https://api.usaspending.gov/api/v2/awards/'+award['award_unique_key']+'/'
                or not STRONG_LABELS.intersection(rec.get('business_categories') or [])):
            return False
    proposal=propose(uei,{'awards':awards},len(awards))
    return proposal['category']=='private' and proposal['evidence_status']=='available'


def apply_decisions(rows,records,day):
    result=[];entries={}
    for original in rows:
        row=dict(original)
        row.setdefault('classification_rule_id','');row.setdefault('classification_evidence_sha256','')
        record=records.get(row['key'],{})
        if row['review_status']=='pending' and row['selected_detention_contractor']=='false' and eligible(row['recipient_uei'],record):
            digest=evidence_hash(record)
            entries[row['key']]={'before':dict(original),'evidence_sha256':digest,
                'awards':[{'award_unique_key':a['award_unique_key'],
                    'strong_labels':sorted(STRONG_LABELS.intersection(a['recipient']['business_categories'])),
                    'all_labels':a['recipient']['business_categories'],
                    'award_url':a['award_url'],'evidence_url':a['request_url']}
                    for a in record['awards']]}
            row.update(entity_type='private',proposed_entity_type='private',review_status='rule_approved',
                decision_origin='approved_rule',classification_rule_id=RULE_ID,
                classification_evidence_sha256=digest,checked_date=day,
                evidence_url=record['awards'][0]['request_url'],
                basis=f'Kevin-approved rule {RULE_ID}: exact UEI and award identities match; every checked award has a stronger private-form or small-business label and an available private proposal, with no conflicting category. Batch rule application, not individual human review. See {RECEIPT}.')
        result.append(row)
    return result,entries


def validate_record(row,record,entry,approved_evidence_sha256=None):
    if (not entry or row.get('classification_rule_id')!=RULE_ID
            or row['entity_type']!='private' or row['selected_detention_contractor']!='false'
            or row['decision_origin']!='approved_rule' or row['review_status']!='rule_approved'
            or row.get('classification_evidence_sha256')!=entry.get('evidence_sha256')
            or (approved_evidence_sha256 or evidence_hash(record))!=entry.get('evidence_sha256')
            or not eligible(row['recipient_uei'],record)):
        raise ValueError('rule-approved decision is outside its approved batch or evidence changed')


def validate_batch(project,decisions):
    from scripts.object_class_25_2_recipients import EVIDENCE
    chosen={k:r for k,r in decisions.items() if r['review_status']=='rule_approved'}
    path=project/RECEIPT
    if not path.exists() and not chosen:
        if any(r.get('classification_rule_id') or r.get('classification_evidence_sha256') for r in decisions.values()):
            raise ValueError('rule fields exist without an approval receipt')
        return
    receipt=json.loads(path.read_text())
    if receipt.get('rule_id')!=RULE_ID or set(receipt['strong_labels'])!=STRONG_LABELS:
        raise ValueError('unknown approved rule definition')
    if (not isinstance(receipt.get('entries'),dict) or len(receipt['entries'])!=400
            or receipt.get('recipient_count')!=400 or receipt.get('signed_25_2_obligations')!='552429912.72'
            or set(chosen)!=set(receipt['entries'])):
        raise ValueError('frozen rule batch membership or controls changed')
    source=project/EVIDENCE
    source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    original_record_hashes={}
    if source_hash!=receipt.get('source_evidence_sha256'):
        from scripts.portable_chart_2_evidence import validate_bundle
        lineage=validate_bundle(project)
        if (lineage is None or
                lineage['original_sha256'][source.name]!=receipt.get('source_evidence_sha256') or
                lineage['derived_sha256'][source.name]!=source_hash):
            raise ValueError('frozen rule evidence source changed; revalidation is required')
        original_record_hashes={r['record_key']:r['original_record_sha256']
                                for r in lineage['redactions'] if r['file']==source.name}
    records=json.loads(source.read_text())['records']
    for key,row in chosen.items():
        validate_record(row,records.get(key,{}),receipt['entries'].get(key),
                        original_record_hashes.get(key))


def run(project,apply=False):
    from scripts import object_class_25_2_recipients as m,shared_recipients as shared
    crosswalk=project/shared.CROSSWALK;receipt_path=project/RECEIPT
    # A completed application is a read-only validation on retry.
    # Resume the narrow receipt-written/CSV-not-replaced state only when the
    # original crosswalk bytes still match. Ordinary builds reject that state.
    prepared=(receipt_path.exists() and m.file_sha256(crosswalk)==
              json.loads(receipt_path.read_text()).get('before_crosswalk_sha256'))
    current={r['key']:r for r in m.read_csv(crosswalk)} if prepared else shared.load(project)
    if any(r['review_status']=='rule_approved' for r in current.values()):
        print('Existing rule approvals verified; no decisions changed.');return
    source_report=json.loads((project/m.OUTPUT/'verification.json').read_text())
    m.check_hash(crosswalk,source_report['crosswalk_sha256'])
    source=project/m.OUTPUT/'recipient_classification.csv'
    m.check_hash(source,source_report['output_sha256'][source.name])
    m.check_hash(project/m.EVIDENCE,source_report['evidence_sha256'])
    evidence=json.loads((project/m.EVIDENCE).read_text())
    before=m.read_csv(crosswalk)
    updated,entries=apply_decisions(before,evidence['records'],datetime.now(timezone.utc).date().isoformat())
    amounts={r['recipient_key']:r for r in m.read_csv(source)}
    total=sum((Decimal(amounts[k]['obligations'] or '0') for k in entries),Decimal(0))
    if len(entries)!=400 or total!=Decimal('552429912.72'):
        raise ValueError('candidate population differs from the approved 400-recipient batch')
    print(f'{len(entries)} eligible recipients; ${total:,.2f} signed 25.2 obligations.')
    if not apply:return
    receipt={'rule_id':RULE_ID,'strong_labels':sorted(STRONG_LABELS),
        'approval':'Kevin approved implementation of the documented 400-recipient batch in task 01a0ce91-1357-7582-ab5d-a155fabfebbf on 2026-09-25.',
        'applied_at_utc':datetime.now(timezone.utc).isoformat(),
        'before_crosswalk_sha256':m.file_sha256(crosswalk),'source_evidence_sha256':m.file_sha256(project/m.EVIDENCE),
        'source_classification_sha256':m.file_sha256(source),'recipient_count':len(entries),
        'signed_25_2_obligations':str(total),'entries':entries}
    if receipt_path.exists():
        prior=json.loads(receipt_path.read_text())
        if prior['before_crosswalk_sha256']!=receipt['before_crosswalk_sha256'] or prior['entries']!=entries:
            raise ValueError('incomplete rule application differs from saved receipt')
        receipt=prior
    # Save evidence first, so the atomic CSV replacement never references a missing receipt.
    m.write_json(receipt_path,receipt)
    temporary=crosswalk.with_suffix('.csv.tmp')
    with temporary.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=shared.FIELDS);writer.writeheader();writer.writerows(updated)
    temporary.replace(crosswalk)
    shared.load(project)
    print('Applied the frozen approved batch. Rebuild both analyses with run_shared_recipients.py.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    run(Path(__file__).resolve().parents[1],apply=args.apply)
