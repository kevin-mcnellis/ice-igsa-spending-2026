"""Offline 25.2 analysis: source rows -> proposed evidence -> reviewed decisions.

No network calls occur here. Only the separately named retrieval script accesses
USAspending. Read load_population(), classify(), calculate(), then build().
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import csv
from decimal import Decimal
from io import TextIOWrapper
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import zipfile

from scripts.bc_gap import read_job, amount, money, INTERVALS
from scripts.prepare_comparison_data import verify_inputs
from scripts.prepare_chart_data import file_sha256, local_path
from scripts import shared_recipients as shared

PROJECT = Path(__file__).resolve().parents[1]
CONTEXT = 'provenance/object_class_25_2_source_context.json'
EVIDENCE = 'provenance/object_class_25_2_entity_evidence.json'
CROSSWALK = shared.CROSSWALK
OUTPUT = 'outputs/object_class_25_2_recipients'
CATEGORIES = ('state_local_government','tribal_government','federal_entity',
              'other_public_nonprofit','private','review','unresolved')
STATE_LABELS = {'U.S. Local Government','U.S. Regional/State Government',
                'U.S. Government Authorities','U.S. Interstate Government Entity',
                'U.S. Territory Government','U.S. Regional Government Organization','Council of Governments'}
GOV_LABELS = STATE_LABELS | {'Native American Tribal Government','U.S. National Government'}
LOOKUP = json.loads((PROJECT/CONTEXT).read_text())['labels']
PUBLIC_LABELS = {LOOKUP[k] for k in ('nonprofit','foundation','community_development_corporations',
                 'higher_education','public_institution_of_higher_education','private_institution_of_higher_education',
                 'minority_serving_institution_of_higher_education','educational_institution','school_of_forestry','veterinary_college')}
PRIVATE_LABELS = {LOOKUP[k] for k in ('category_business','small_business','other_than_small_business',
                  'corporate_entity_not_tax_exempt','partnership_or_limited_liability_partnership',
                  'sole_proprietorship','manufacturer_of_goods','subchapter_s_corporation','limited_liability_corporation',
                  'us_owned_business','foreign_owned_and_us_located_business','foreign_owned','tribally_owned_firm',
                  'alaskan_native_corporation_owned_firm','native_hawaiian_organization_owned_firm')}
EXPECTED_TOTAL = Decimal('1071496898.71')
EXPECTED_PARTS = {('070-0540',INTERVALS[0]):Decimal('259127148.59'),
                  ('070-0545',INTERVALS[0]):Decimal('12065021.20'),
                  ('070-0540',INTERVALS[1]):Decimal('397644588.99'),
                  ('070-0545',INTERVALS[1]):Decimal('402660139.93')}
CW_FIELDS = ('recipient_key','recipient_uei','recipient_name','category','basis','deciding_endpoint',
             'evidence_url','second_award_agreement','chart_2_reference','review_status','evidence_source',
             'evidence_status','chart_2_category','source_path')


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        reader=csv.DictReader(f,strict=True)
        fields=reader.fieldnames or []
        if not fields or len(fields)!=len(set(fields)):raise ValueError(f'bad CSV columns: {path}')
        rows=list(reader)
        if any(None in r or any(v is None for v in r.values()) for r in rows):raise ValueError(f'bad CSV row: {path}')
        return rows


def write_csv(path, rows, fields=None):
    fields=fields or list(rows[0])
    with Path(path).open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)


def write_json(path, data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    temporary.replace(path)


def check_hash(path, expected):
    if file_sha256(Path(path))!=expected:raise ValueError(f'hash mismatch: {path}')


def protected_check(project=PROJECT):
    expected=json.loads((project/CONTEXT).read_text())['protected_sha256']
    for name,digest in expected.items():check_hash(project/name,digest)
    return expected


def recipient_key(row):
    uei=row['recipient_uei'].strip();name=row['recipient_name'].strip()
    return 'uei:'+uei if uei else 'name:'+name if name else 'missing'


def selected(row):
    p=row['submission_period']
    return row['object_class_code']=='25.2' and (
        p.startswith('FY2025P') and 5<=int(p[-2:])<=12 or
        p.startswith('FY2026P') and 2<=int(p[-2:])<=10)


def load_population(project=PROJECT):
    """Reuse bc_gap validation; recover identities via independently checked line joins."""
    manifest=verify_inputs(project)
    rows=[]
    for job,year,period in [('DHS_FY2025P12_c',2025,12),('DHS_FY2026P10_c',2026,10)]:
        base=[r for r in read_job(project,job,'C',year,period) if selected(r)]
        targets={r['source_row_id']:r for r in base}
        if len(targets)!=len(base):raise ValueError('duplicate source IDs')
        receipt=json.loads(local_path(project,f'data/raw/{job}/acquisition_receipt.json').read_text())
        zip_path=local_path(project,f'data/raw/{job}/{Path(receipt["zip_path"]).name}')
        found=set()
        with zipfile.ZipFile(zip_path) as archive:
            for member in receipt['members']:
                name=member['member']
                with archive.open(name) as binary, TextIOWrapper(binary,encoding='utf-8-sig',newline='') as f:
                    reader=csv.DictReader(f,strict=True)
                    required={'recipient_uei','recipient_name','award_id_piid','prime_award_base_transaction_description'}
                    if not required <= set(reader.fieldnames or []):raise ValueError('missing recipient source fields')
                    line=reader.line_num+1
                    for raw in reader:
                        row_id=f'{job}:{name}:row:{line}';line=reader.line_num+1
                        if row_id not in targets:continue
                        row=targets[row_id]
                        for field in ('submission_period','federal_account_symbol','object_class_code','award_unique_key'):
                            if row[field]!=raw[field]:raise ValueError('source locator join mismatch')
                        if row['obligation']!=raw['transaction_obligated_amount']:raise ValueError('amount join mismatch')
                        for field in ('recipient_uei','recipient_name','award_id_piid','award_id_fain','award_id_uri',
                                      'prime_award_base_transaction_description'):
                            row[field]=raw.get(field,'').strip()
                        row['recipient_key']=recipient_key(row)
                        row['interval']=INTERVALS[0] if year==2025 else INTERVALS[1]
                        row['source_path']=f'{row["source_zip_path"]}!{name}:line:{row["source_line_number"]}'
                        found.add(row_id)
        if found!=set(targets):raise ValueError('not every source locator recovered')
        check_hash(zip_path,receipt['zip_sha256'])
        rows.extend(base)
    rows.sort(key=lambda r:r['source_row_id'])
    controls=read_csv(project/'outputs/bc_gap/object_class_differences.csv')
    validate_population(rows,controls)
    return rows,manifest


def validate_population(rows, controls):
    ids=[r['source_row_id'] for r in rows]
    if len(ids)!=13860 or len(set(ids))!=len(ids):raise ValueError('25.2 row-count/unique-ID check failed')
    if len({r['recipient_key'] for r in rows})!=512:raise ValueError('25.2 recipient-key check failed')
    total=sum((amount(r['obligation'],r['source_row_id']) or Decimal(0) for r in rows),Decimal(0))
    if total!=EXPECTED_TOTAL:raise ValueError('25.2 total check failed')
    for (account,interval),expected in EXPECTED_PARTS.items():
        actual=sum((amount(r['obligation'],r['source_row_id']) or Decimal(0) for r in rows
                    if r['federal_account_symbol']==account and r['interval']==interval),Decimal(0))
        matched=[r for r in controls if r['measure']=='obligations' and r['object_class']=='25.2'
                 and r['account']==account and r['interval']==interval]
        if len(matched)!=1 or actual!=expected or actual!=Decimal(matched[0]['file_c']):
            raise ValueError(f'25.2 bc_gap reconciliation failed: {account} {interval}')


def stats(rows):
    values=[amount(r['obligation'],r['source_row_id']) for r in rows]
    nums=[v for v in values if v is not None]
    state='empty' if not rows else 'all_blank' if not nums else 'partial_blank' if len(nums)<len(rows) else 'numeric'
    return {'obligations':'' if state=='all_blank' else money(sum(nums,Decimal(0))),
            'amount_status':state,'numeric_row_count':len(nums),'blank_row_count':len(values)-len(nums),
            'recipient_count':len({r['recipient_key'] for r in rows}),
            'positive_obligations':money(sum((v for v in nums if v>0),Decimal(0))),
            'negative_obligations':money(sum((v for v in nums if v<0),Decimal(0)))}


def select_awards(rows):
    """Rank distinct awards by largest absolute source-row obligation, then period/key."""
    groups=defaultdict(list)
    for r in rows:groups[r['recipient_key']].append(r)
    result={}
    for key,group in sorted(groups.items()):
        if not group[0]['recipient_uei']:
            result[key]=[];continue
        awards={}
        for r in group:
            award=r['award_unique_key']
            if not award:continue
            value=amount(r['obligation'],r['source_row_id'])
            rank=(abs(value) if value is not None else Decimal(-1),r['submission_period'])
            if award not in awards or rank>awards[award][0]:awards[award]=(rank,r)
        ordered=sorted(awards,key=lambda a:(-awards[a][0][0],-int(awards[a][0][1].replace('FY','').replace('P','')),a))
        result[key]=[awards[a][1] for a in ordered[:2]]
    return result


def map_labels(labels, profile=False):
    if not labels:return 'unresolved','evidence_unavailable'
    if profile:
        if any(x not in LOOKUP for x in labels):return 'review','unknown_label'
        labels=[LOOKUP[x] for x in labels]
    values=set(labels)
    if not values<=set(LOOKUP.values()):return 'review','unknown_label'
    if 'Foreign Government' in values:return 'review','foreign_government'
    government=set()
    if values & STATE_LABELS:government.add('state_local_government')
    if 'Native American Tribal Government' in values:government.add('tribal_government')
    if 'U.S. National Government' in values:government.add('federal_entity')
    if len(government)>1:return 'unresolved','conflict'
    if government:return next(iter(government)),'available'
    if 'Government' in values:return 'review','generic_government'
    if values & PUBLIC_LABELS:return 'other_public_nonprofit','available'
    if values & PRIVATE_LABELS:return 'private','available'
    return 'review','no_decisive_label'


def award_category(record, uei):
    rec=record.get('recipient') or {}
    if record.get('error') or rec.get('recipient_uei')!=uei or record.get('identity_matches') is not True:
        return 'unresolved','evidence_unavailable'
    return map_labels(rec.get('business_categories') or [])


def propose(uei, record, expected_awards):
    awards=record.get('awards',[])
    pairs=[award_category(a,uei) for a in awards]
    statuses=[p[1] for p in pairs]
    result={'category':'unresolved','evidence_status':'evidence_unavailable','deciding_endpoint':'award',
            'second_award_agreement':'not_applicable' if expected_awards<2 else 'unavailable',
            'award_evidence_status':'|'.join(statuses) or 'evidence_unavailable',
            'deciding_labels':json.dumps((awards[0].get('recipient') or {}).get('business_categories',[]) if awards else []),
            'evidence_url':awards[0].get('request_url',awards[0].get('source_url','')) if awards else ''}
    if not uei:return result
    if len(pairs)==expected_awards and pairs:
        result['category'],result['evidence_status']=pairs[0]
        if expected_awards==2:
            signatures=[set((a.get('recipient') or {}).get('business_categories') or []) & GOV_LABELS for a in awards]
            if all(p[1]!='evidence_unavailable' for p in pairs):
                disagreement=signatures[0]!=signatures[1] or pairs[0][0]!=pairs[1][0]
                result['second_award_agreement']='disagree' if disagreement else 'agree'
                if disagreement:result.update(category='unresolved',evidence_status='conflict')
            else:result.update(category='unresolved',evidence_status='evidence_unavailable')
    if 'conflict' in statuses:result.update(category='unresolved',evidence_status='conflict')
    profile=record.get('profile') or {}
    # Preserve a contradictory award history even when the current profile looks clear.
    if (result['evidence_status'] not in ('conflict','unknown_label')
            and all(a.get('identity_matches') is True and (a.get('recipient') or {}).get('recipient_uei')==uei for a in awards)
            and result['category'] in ('review','unresolved')):
        if profile.get('identity_matches') is True and profile.get('uei')==uei and not profile.get('error'):
            category,status=map_labels(profile.get('business_types',[]),profile=True)
            if status=='available':
                result.update(category=category,evidence_status=status,deciding_endpoint='recipient_profile',
                              deciding_labels=json.dumps(profile['business_types']),evidence_url=profile.get('request_url',''))
    return result


def old_category(row, saved_record):
    mapping={'Selected private detention contractors':'private','Other private contractors':'private',
             'State and local governments':'state_local_government','Other public or nonprofit entities':'other_public_nonprofit'}
    result=mapping.get(row['type'],'unresolved')
    # Split only an explicit federal/tribal subtype already present in the saved Chart 2 evidence.
    subtype,_=map_labels((saved_record.get('recipient') or {}).get('business_categories',[]))
    if result=='other_public_nonprofit' and subtype=='federal_entity':result=subtype
    if result=='state_local_government' and subtype=='tribal_government':result=subtype
    return result


def classify(rows,evidence,project=PROJECT):
    plans=select_awards(rows);groups=defaultdict(list)
    for r in rows:groups[r['recipient_key']].append(r)
    old={r['key']:r for r in read_csv(project/'data/chart_2_recipient_crosswalk.csv') if r['review_status']=='reviewed'}
    old_evidence={r['uei']:r for r in json.loads((project/'provenance/chart_2_entity_evidence.json').read_text())['records']}
    proposed=[]
    for key,group in sorted(groups.items()):
        uei=group[0]['recipient_uei'];ev=evidence.get('records',{}).get(key,{})
        suggestion=propose(uei,ev,len(plans[key]))
        source='api_evidence';status='pending';old_type='';reference=''
        basis=f"API proposal only: {suggestion['evidence_status']}; award evidence: {suggestion['award_evidence_status']}"
        if key in old:
            previous=old[key];category=old_category(previous,old_evidence.get(uei,{}))
            source='chart_2_crosswalk';reference=key;old_type=previous['type']
            disagree=(suggestion['evidence_status']=='conflict' or suggestion['category']=='review' or
                      suggestion['category'] not in (category,'unresolved'))
            if disagree:
                suggestion.update(category='unresolved',evidence_status='conflict')
                basis=f"Chart 2 reviewed {category}; new award/profile evidence conflicts or requires review. {basis}"
            else:
                suggestion.update(category=category,deciding_endpoint='chart_2_crosswalk')
                status='reviewed';basis='Carried reviewed Chart 2 decision: '+previous['basis']+'; '+basis
                suggestion['evidence_url']=previous['evidence_url']
        proposed.append({'recipient_key':key,'recipient_uei':uei,
                         'recipient_name':' | '.join(sorted({r['recipient_name'] for r in group})),
                         **suggestion,'basis':basis,'review_status':status,'evidence_source':source,
                         'chart_2_reference':reference,'chart_2_category':old_type,'source_path':CROSSWALK,
                         'diagnostic_evidence_sha256':population_digest(ev)})
    return proposed


def apply_crosswalk(proposals, crosswalk):
    decisions={r['recipient_key']:r for r in crosswalk}
    if len(decisions)!=len(crosswalk) or set(decisions)!={r['recipient_key'] for r in proposals}:
        raise ValueError('crosswalk must contain every population key exactly once')
    result=[]
    for proposal in proposals:
        decision=decisions[proposal['recipient_key']]
        if decision['recipient_uei']!=proposal['recipient_uei']:raise ValueError('crosswalk UEI changed')
        if not proposal['recipient_uei'] and (decision['category']!='unresolved' or decision['review_status']!='pending'):
            raise ValueError('blank UEI/identity must remain unresolved and pending')
        if decision['category'] not in CATEGORIES or decision['review_status'] not in ('pending','reviewed'):
            raise ValueError('invalid category or review status')
        if decision['review_status']=='reviewed' and not all(decision.get(k) for k in ('basis','evidence_url')):
            raise ValueError('reviewed decision requires basis and evidence')
        if decision['review_status']=='reviewed' and decision['deciding_endpoint']!='manual_review':
            if proposal['review_status']!='reviewed' or decision['category']!=proposal['category']:
                raise ValueError('new approved decisions require manual_review endpoint and explicit review basis')
        row={**proposal,**decision}
        # Original evidence findings always remain visible after a human decision.
        row.update(evidence_status=proposal['evidence_status'],award_evidence_status=proposal['award_evidence_status'],
                   deciding_labels=proposal['deciding_labels'],second_award_agreement=proposal['second_award_agreement'])
        result.append(row)
    return result


def approved(row):
    return (row['review_status'] in shared.ACCEPTED_STATUSES and row['category'] not in ('review','unresolved')
            and not row.get('shared_decision_warning'))


def resolve_shared(proposals, decisions):
    """Attach shared decisions without letting new API evidence approve or erase one."""
    result=[]
    for p in proposals:
        d=decisions.get(p['recipient_key'])
        if d is None or d['recipient_uei']!=p['recipient_uei']:
            raise ValueError('shared crosswalk missing or mismatches source recipient')
        warning=''
        if d['review_status'] in shared.ACCEPTED_STATUSES:
            if p['evidence_status']=='conflict':warning='conflicting_evidence'
            elif p['evidence_status']=='available' and p['category'] not in (d['entity_type'],'unresolved'):
                warning='new_evidence_disagrees'
            elif p['category']=='review':warning='evidence_requires_review'
        # A manual decision can resolve the diagnostic, but its evidence stays visible.
        if (d['decision_origin']=='manual_review' and p.get('diagnostic_evidence_sha256')
                and d.get('reviewed_diagnostic_sha256')==p['diagnostic_evidence_sha256']):warning=''
        result.append({**p,'proposed_category':p['category'],
                       'category':d['entity_type'] if d['review_status'] in shared.ACCEPTED_STATUSES else p['category'],
                       'review_status':d['review_status'],'basis':d['basis'],'evidence_url':d['evidence_url'],
                       'deciding_endpoint':d['decision_origin'],'headline_type':shared.display_type(d),
                       'selected_detention_contractor':d['selected_detention_contractor'],
                       'shared_decision_warning':warning,'source_path':CROSSWALK,
                       'classification_rule_id':d.get('classification_rule_id',''),
                       'classification_evidence_sha256':d.get('classification_evidence_sha256','')})
    return result


def calculate(rows,decisions):
    ids=[r['source_row_id'] for r in rows]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate source row')
    if {r['recipient_key'] for r in rows}!=set(decisions):raise ValueError('classification universe differs from source keys')
    total=Decimal(stats(rows)['obligations'] or 0)
    tables=[]
    for view in ('proposed','reviewed'):
        for acct in ('070-0540','070-0545','combined'):
            for interval in (*INTERVALS,'full_window'):
                scope=[r for r in rows if (acct=='combined' or r['federal_account_symbol']==acct)
                       and (interval=='full_window' or r['interval']==interval)]
                denominator=Decimal(stats(scope)['obligations'] or 0)
                for category in CATEGORIES:
                    group=[]
                    for r in scope:
                        d=decisions[r['recipient_key']]
                        c=d['category'] if view=='proposed' or d['review_status'] in shared.ACCEPTED_STATUSES else 'unresolved'
                        if c==category:group.append(r)
                    summary=stats(group)
                    tables.append({'view':view,'category':category,'account':acct,'interval':interval,**summary,
                                   'share_of_matching_total':'' if not denominator or summary['obligations']=='' else
                                   str(Decimal(summary['obligations'])/denominator),
                                   'matching_total':money(denominator),'source_path':OUTPUT+'/source_rows.csv',
                                   'classification_source':CROSSWALK})
                reconstructed=sum((Decimal(r['obligations']) for r in tables if r['view']==view and r['account']==acct
                                   and r['interval']==interval and r['obligations']),Decimal(0))
                if reconstructed!=denominator:raise ValueError('category/account/interval reconciliation failed')
    known=Decimal(0);pending=Decimal(0)
    for row in rows:
        value=amount(row['obligation'],row['source_row_id']);d=decisions[row['recipient_key']]
        if value is None or value<=0:continue
        if not approved(d):pending+=value
        elif d['category'] in ('state_local_government','tribal_government'):known+=value
    threshold=total*Decimal('0.01')
    conclusion=('not_determinable' if total<=0 else 'not_negligible' if known>=threshold else
                'negligible_numeric_only' if known+pending<threshold else 'not_determinable')
    numeric_conclusion=conclusion
    if stats(rows)['blank_row_count'] and conclusion=='negligible_numeric_only':conclusion='not_determinable'
    return {'category_totals':tables,'bound':{'denominator':money(total),'threshold':str(threshold),
             'reviewed_government_positive':money(known),'unapproved_positive':money(pending),
             'positive_exposure':money(known+pending),'conclusion':conclusion,'numeric_conclusion':numeric_conclusion,
             'blank_row_count':stats(rows)['blank_row_count'],
             'scope_limit':'Only observed numeric obligations. Blank amounts are unbounded; never evidence of absence.'}}


def safe_output(project,output):
    if Path(output).resolve()!=(Path(project)/OUTPUT).resolve():raise ValueError('output must be the dedicated 25.2 folder')
    if Path(output).is_symlink():raise ValueError('output must not be a symlink')
    return Path(output)


def validation_exit(report,strict=False):
    return 2 if report['status']=='FAIL' else 1 if strict and report['status']=='WARN' else 0


def evidence_check(evidence, rows):
    expected=population_digest(rows)
    if evidence.get('population_sha256')!=expected:raise ValueError('evidence population hash mismatch')
    plans=select_awards(rows)
    if set(evidence.get('records',{}))!=set(plans):raise ValueError('evidence key coverage differs from population')
    for key,plan in plans.items():
        records=evidence['records'][key].get('awards',[])
        if [r.get('award_unique_key') for r in records]!=[r['award_unique_key'] for r in plan]:
            raise ValueError('saved evidence award selection differs from deterministic plan')
        for record in records:
            if record.get('request_url')!='https://api.usaspending.gov/api/v2/awards/'+record['award_unique_key']+'/':
                raise ValueError('unexpected saved endpoint')


def population_digest(rows):
    import hashlib
    return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def build(project=PROJECT):
    project=Path(project).resolve();protected=protected_check(project)
    rows,manifest=load_population(project)
    evidence=json.loads((project/EVIDENCE).read_text());evidence_check(evidence,rows)
    proposals=classify(rows,evidence,project)
    crosswalk=project/CROSSWALK
    classifications=resolve_shared(proposals,shared.load(project))
    shared_warnings=shared.diagnostics(project,shared.load(project))
    for row in classifications:
        diagnostic=shared_warnings.get(row['recipient_key'])
        row['shared_decision_warning']=diagnostic['shared_decision_warning'] if diagnostic else ''
        if diagnostic:row['diagnostic_evidence_sha256']=diagnostic['diagnostic_evidence_sha256']
    decisions={r['recipient_key']:r for r in classifications}
    result=calculate(rows,decisions)
    headline=[]
    for category in shared.TYPES:
        group=[r for r in rows if decisions[r['recipient_key']]['headline_type']==category]
        headline.append({'object_class':'25.2','type':category,**stats(group)})
    groups=defaultdict(list)
    for row in rows:groups[row['recipient_key']].append(row)
    for row in classifications:
        row.update(stats(groups[row['recipient_key']]))
        row['share_of_total']='' if not row['obligations'] else str(Decimal(row['obligations'])/EXPECTED_TOTAL)
        row['approved_for_findings']=str(approved(row)).lower()
        ev=evidence['records'][row['recipient_key']]
        row['award_urls']=' | '.join(r.get('award_url','') for r in ev.get('awards',[]))
        row['all_evidence_urls']=' | '.join(r.get('request_url','') for r in ev.get('awards',[]))
        row['profile_evidence_url']=(ev.get('profile') or {}).get('request_url','')
        row['evidence_source_path']=EVIDENCE
    queue=sorted((r for r in classifications if not approved(r)),key=lambda r:(-abs(Decimal(r['obligations'] or 0)),r['recipient_key']))
    exposure_order=sorted(queue,key=lambda r:(-Decimal(r['positive_obligations']),r['recipient_key']))
    for rank,row in enumerate(exposure_order,1):row['positive_exposure_rank']=rank
    for row in classifications:row.setdefault('positive_exposure_rank','')
    government=[]
    for row in rows:
        d=decisions[row['recipient_key']]
        if d['category'] in ('state_local_government','tribal_government'):
            government.append({**row,'category':d['category'],'review_status':d['review_status'],
                               'approved_for_findings':str(approved(d)).lower(),'evidence_url':d['evidence_url']})
    checks={name:{'status':'PASS'} for name in ('source_hashes','population_controls','bc_gap_reconciliation','chart_2_separation')}
    checks['population_controls'].update(rows=len(rows),recipient_keys=len(groups),total=money(EXPECTED_TOTAL),**stats(rows))
    for flag,predicate in [('evidence_coverage',lambda r:r['evidence_status']=='available'),
                            ('reviewed_classification',approved)]:
        chosen=[r for r in classifications if predicate(r)]
        known=sum((Decimal(r['obligations'] or 0) for r in chosen),Decimal(0))
        checks[flag]={'status':'PASS' if len(chosen)==len(classifications) else 'WARN',
                      'recipient_keys':len(chosen),'all_recipient_keys':len(classifications),
                      'signed_obligations':money(known),'share_of_total':str(known/EXPECTED_TOTAL),
                      'positive_source_row_obligations':money(sum((Decimal(r['positive_obligations']) for r in chosen),Decimal(0))),
                      'absolute_source_row_obligations':money(sum((Decimal(r['positive_obligations'])-Decimal(r['negative_obligations']) for r in chosen),Decimal(0)))}
    award_records=[a for ev in evidence['records'].values() for a in ev.get('awards',[])]
    identity=sum(a.get('identity_matches') is True for a in award_records)
    paired=[r for r in classifications if r['second_award_agreement']!='not_applicable']
    agreement=sum(r['second_award_agreement']=='agree' for r in paired)
    checks['identity_matches']={'status':'PASS' if identity==len(award_records) else 'WARN',
                                'matched':identity,'award_responses':len(award_records),
                                'rate':str(Decimal(identity)/len(award_records)) if award_records else ''}
    checks['second_award_agreement']={'status':'PASS' if agreement==len(paired) else 'WARN',
                                      'agree':agreement,'pairs':len(paired),
                                      'rate':str(Decimal(agreement)/len(paired)) if paired else ''}
    queue_amount=sum((Decimal(r['obligations'] or 0) for r in queue),Decimal(0))
    report={'status':'WARN' if queue or stats(rows)['blank_row_count'] else 'PASS','checks':checks,
            'shared_decision_warnings':{key:r['shared_decision_warning'] for key,r in shared_warnings.items()},
            'bound':result['bound'],'pending_or_unresolved_keys':len(queue),
            'pending_or_unresolved_signed_obligations':money(queue_amount),
            'pending_or_unresolved_share':str(queue_amount/EXPECTED_TOTAL),
            'source_manifest':manifest,'protected_sha256':protected,
            'evidence_sha256':file_sha256(project/EVIDENCE),'crosswalk_sha256':file_sha256(crosswalk),
            'population_sha256':population_digest(rows),
            'code_sha256':{name:file_sha256(project/name) for name in (
                'scripts/object_class_25_2_recipients.py','scripts/fetch_25_2_entity_evidence.py',CONTEXT)}}
    output=safe_output(project,project/OUTPUT);output.parent.mkdir(exist_ok=True)
    with TemporaryDirectory(prefix='.25-2-build-',dir=project) as t:
        stage=Path(t)/'new';stage.mkdir()
        write_csv(stage/'source_rows.csv',rows)
        write_csv(stage/'category_totals.csv',result['category_totals'])
        write_csv(stage/'headline_category_totals.csv',headline)
        write_csv(stage/'recipient_classification.csv',classifications)
        write_csv(stage/'review_queue.csv',queue,list(classifications[0]))
        write_csv(stage/'threshold_review_queue.csv',exposure_order,list(classifications[0]))
        write_csv(stage/'government_rows.csv',government,[*rows[0],'category','review_status','approved_for_findings','evidence_url'])
        for f in stage.glob('*.csv'):read_csv(f)
        protected_check(project)
        report['output_sha256']={p.name:file_sha256(p) for p in stage.glob('*.csv')}
        write_json(stage/'verification.json',report)
        old=Path(t)/'previous'
        try:
            if output.exists():output.rename(old)
            stage.rename(output)
        except BaseException:
            if old.exists() and not output.exists():old.rename(output)
            raise
    write_report(project,report,result['category_totals'],classifications,government)
    return report



def write_report(project,report,totals,classifications,government):
    """Regenerate the review guide and qualified headline from the verified tables."""
    def cell(view,category,acct='combined'):
        return next(r for r in totals if r['view']==view and r['category']==category
                    and r['account']==acct and r['interval']=='full_window')
    def dollars(value):return 'unreported' if value=='' else f"${Decimal(value):,.2f}"
    state=cell('reviewed','state_local_government');tribal=cell('reviewed','tribal_government')
    bound=report['bound'];pending=report['pending_or_unresolved_signed_obligations']
    text=[
        '# Object class 25.2: recipient review',
        '',
        'Scope: File_C_blog_post only. Parent: [session state](SESSION_STATE.md). Supporting analysis, not a publication prerequisite.',
        '',
        f"Of **$1,071,496,898.71 in reported File C 25.2 obligations**, **{dollars(state['obligations'])} is attributed to state/local governments across {state['recipient_count']} reviewed recipient keys**. A further **{dollars(tribal['obligations'])}** is attributed to reviewed tribal governments. **{dollars(pending)} ({Decimal(report['pending_or_unresolved_share'])*100:.2f}%) across {report['pending_or_unresolved_keys']} keys remains pending, unresolved or under review.** Their positive source-row exposure is **{dollars(bound['unapproved_positive'])}**, before netting reductions.",
        '',
        f"The observed-numeric positive-amount test is **{bound['numeric_conclusion']}**; the overall completeness conclusion is **{bound['conclusion']}**. Reviewed state/local/tribal positive amounts ({dollars(bound['reviewed_government_positive'])}) plus all unapproved positive amounts ({dollars(bound['unapproved_positive'])}) equal **{dollars(bound['positive_exposure'])}**. The exact 1% threshold is **${bound['threshold']}**. Negative adjustments do not cancel positive exposure. There are **{bound['blank_row_count']:,} blank amounts**; they are unbounded, so even a below-threshold result would mean only negligible within observed numeric obligations, never absent.",
        '',
        '## Account results',
        '',
        'These are signed obligations, not payments received. The accepted view retains the CSV label reviewed for compatibility and includes both individually reviewed and explicitly rule_approved decisions; decision status remains visible for each recipient. Pending proposals are not findings. Existing decisions remain in the category totals when diagnostics flag them, so affected totals are provisional. The conservative bound treats flagged positive amounts as unresolved exposure. Use headline_category_totals.csv for the six categories shared with 25.4; category_totals.csv preserves detailed types.',
        '',
        '| Account | Reviewed state/local | Reviewed tribal | Pending/unresolved signed obligations | Pending positive exposure | Proposed state/local (not final) | Proposed tribal (not final) |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |',
    ]
    for acct,label in [('070-0540','Operations and Support (070-0540)'),('070-0545','Construction (070-0545)'),('combined','Both accounts')]:
        parts=[dollars(cell(v,c,acct)['obligations']) for v,c in [
            ('reviewed','state_local_government'),('reviewed','tribal_government'),('reviewed','unresolved'),
            ('proposed','state_local_government'),('proposed','tribal_government')]]
        parts.insert(3,dollars(cell('reviewed','unresolved',acct)['positive_obligations']))
        text.append('| '+label+' | '+' | '.join(parts)+' |')
    text += ['',
        'Shared source: [category totals](outputs/object_class_25_2_recipients/category_totals.csv). The CSV also splits February–September 2025 and October 2025–July 2026. Each share uses the matching account and interval denominator. Recipient counts are distinct keys at each level, never summed across periods; the one missing-identity bucket is a key, not an identified recipient.',
        '', '## Review decisions', '',
        'Edit only [the shared decision crosswalk](data/shared_recipient_crosswalk.csv), following [the shared review guide](SHARED_RECIPIENTS.md). One row is one exact UEI, or an exact trimmed name when UEI is blank. Blank identities stay unresolved. Distinct UEIs remain separate even when their names are alike.',
        '',
        'The requested [review queue](outputs/object_class_25_2_recipients/review_queue.csv) is sorted by absolute signed amount. For the threshold decision, start with [the positive-exposure priority view](outputs/object_class_25_2_recipients/threshold_review_queue.csv), or sort by `positive_exposure_rank`; net-zero recipients can still have large positive exposure. Every pending private or government proposal is in this queue. Use the linked award pages and API evidence, check identity and agreement between the two awards, and read any profile evidence as a separate current-recipient check.',
        '',
        'To accept or change a proposal, edit `entity_type`, `basis`, `evidence_url`, and `checked_date` in the shared table; set `decision_origin=manual_review` and `review_status=reviewed`. Keep selected_detention_contractor unchanged unless separately approved. To resolve a diagnostic warning, record its exact combined evidence hash in reviewed_diagnostic_sha256 after review. Use unresolved/pending when evidence is insufficient. A name containing COUNTY is only a research lead.',
        '',
        'Illustrative decision only (not a pre-approved live record): an award with matching UEI and U.S. Local Government on both evidence awards supports a pending state/local proposal. Kevin can accept it using the fields above after inspecting the linked evidence. An award disagreement remains unresolved even if the latest recipient profile says private.',
        '',
        'Review is complete when each required decision has been accepted with evidence or explicitly left pending. A negligible conclusion requires the conservative bound to fall below 1%; unresolved dollar exposure that could change that result means not determinable. Original Chart 2 evidence and its historical crosswalk remain unchanged; both current consumers read the new shared table.',
        '', '## Source and evidence method', '',
        'The frozen population is object class exactly 25.2, accounts 070-0540/0545, FY2025 P05–P12 and FY2026 P02–P10, across Contracts, Assistance and Unlinked. This is a reporting-period selection; it can include adjustments to older commitments. The denominator is reported File C obligations, not all award-linked obligations and not outlays.',
        '',
        'The reader reuses `bc_gap.read_job` and its manifest/ZIP/member checks. A second raw read recovers recipient names and UEIs by the verified ZIP, member and first physical CSV line; the award, period, account, object class and amount must agree. Hard checks require 13,860 rows, 512 keys, the exact total and all four saved account/interval totals.',
        '',
        'For each UEI, distinct evidence awards are ranked by their largest absolute source-row 25.2 obligation, then latest submission period and lexical award key. Numeric zero ranks ahead of a blank; this ranking does not turn a blank amount into zero. The two largest distinct awards are retrieved when available. New proposals remain pending unless covered by an explicitly approved rule or individual decision. Reviewed Chart 2 decisions carry over with the original key, category and basis; conflicting new evidence sends them back to review.',
        '',
        'The award endpoint exposes recipient categories associated with the transaction selected by the award endpoint, not a historical registration snapshot for each File C row. The recipient-profile endpoint combines the latest registration data and latest transaction categories. It is secondary evidence for unresolved cases and cannot erase an award conflict or UEI mismatch. Empty labels and failed requests are unavailable evidence, never a private-entity finding. Hospital alone does not establish public/nonprofit status.',
        '',
        'Both object classes now use one shared decision per recipient and the same six display categories. The supplementary two-award and profile evidence informs proposals and a common review queue, never automatic approval. Detailed federal/tribal categories remain separate underneath; federal entities display with public/nonprofit entities, while tribal display remains unresolved pending a presentation decision.',
        '',
        'Official endpoint contracts: [award details](https://github.com/fedspendingtransparency/usaspending-api/blob/master/usaspending_api/api_contracts/contracts/v2/awards/award_id.md), [recipient profile](https://github.com/fedspendingtransparency/usaspending-api/blob/master/usaspending_api/api_contracts/contracts/v2/recipient/recipient_id.md), and [business-category labels](https://github.com/fedspendingtransparency/usaspending-api/blob/master/usaspending_api/common/helpers/business_categories_helper.py). The local inspected source commit and hashes are pinned in [source context](provenance/object_class_25_2_source_context.json); saved live responses control observations at their retrieval times.',
        '', '## One concrete trace', '',
    ]
    candidates=[r for r in government if r['obligation']]
    if not candidates:candidates=[]
    if candidates:
        row=max(candidates,key=lambda r:abs(Decimal(r['obligation'])))
        d=next(r for r in classifications if r['recipient_key']==row['recipient_key'])
        text += [f"`{row['recipient_key']}` ({row['recipient_name']}), **{dollars(row['obligation'])}** in {row['submission_period']}, account {row['federal_account_symbol']}: [original ZIP]({row['source_zip_path']}), member `{row['source_member']}`, first physical line **{row['source_line_number']}**, award `{row['award_unique_key']}`. [Evidence and the shared decision]({d['evidence_url']}) record category `{d['category']}` with review status **{d['review_status']}** and diagnostic warning **{d['shared_decision_warning'] or 'none'}**. Find this exact `source_row_id` in [government rows](outputs/object_class_25_2_recipients/government_rows.csv)."]
    else:
        text += ['No numeric proposed government row is available; inspect the linked recipient classification and source-row tables before drawing a government conclusion.']
    text += ['', '## Verification and reproduction', '',
        'Run from `File_C_blog_post/` using the existing Python runtime; no dependencies need installation:', '',
        '```bash',
        'python3 -m scripts.fetch_25_2_entity_evidence',
        '# Only if retrying recorded request failures:',
        'python3 -m scripts.fetch_25_2_entity_evidence --retry-errors',
        '# All subsequent analysis is offline:',
        'python3 run_shared_recipients.py',
        'python3 run_shared_recipients.py --strict',
        'python3 -m unittest tests.test_object_class_25_2_recipients -q',
        '```', '',
        'On this host the tested retrieval runtime is `/opt/homebrew/bin/python3` (3.14.2). System Python 3.9 failed TLS certificate verification; no TLS checks were disabled. Retrieval is paced at no more than two attempts per second, retries transient errors at most three times, uses at most four concurrent requests, saves after each completed recipient and resumes from existing evidence. It writes only the separately named 25.2 evidence file. Never execute the older Chart 2 fetch script for this analysis.',
        '',
        'The offline build returns 0 for advisory WARN, 1 for `--strict` with WARN, and 2 for a hard error. It preserves the last complete output folder on failure. The separate shared runner creates a crosswalk only with --initialize and refuses to replace an existing one; ordinary builds preserve the editable decisions. To refresh the frozen source universe or protected Chart 2 baseline requires a separately approved update.',
        '',
        '[Verification record](outputs/object_class_25_2_recipients/verification.json) separates source/population checks, evidence coverage, identity matches, second-award agreement, review coverage and Chart 2 preservation. [Recipient classification](outputs/object_class_25_2_recipients/recipient_classification.csv) links each decision to its evidence and source rows. Blank and partial-blank statuses travel with every subtotal. New proposals require individual approval or an explicit approved rule; rule_approved records identify the rule and frozen evidence separately from human review.',
        '', '## Limits and proposed methodology text', '',
        'Recipient type identifies the entity to which obligations are attributed, not who received a cash payment or what service the obligation financed. This analysis does not establish IGSA payments, their absence, or why File B differs from File C. Tribal governments are reported separately from state/local governments. Current API recipient evidence can differ from the older financial download; conflicts remain visible.',
        '',
        'The Word draft was not edited. The working methodology now documents shared classification. If used in the blog, add: “A separate object-class 25.2 review covers $1.071 billion in reported File C obligations for the same accounts and reporting periods. Recipient classifications combine carried-over reviewed decisions with new proposals awaiting review. The conservative government-exposure test includes all unapproved positive amounts and cannot establish the absence of IGSA obligations.” Replace or qualify any manuscript statement of no government funding until the review decisions and reporting scope support it.',
        '',
    ]
    target=project/'OBJECT_CLASS_25_2_RECIPIENTS.md'
    temporary=target.with_suffix('.md.tmp');temporary.write_text('\n'.join(text),encoding='utf-8');temporary.replace(target)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strict',action='store_true')
    args=parser.parse_args()
    try:
        report=build()
        print(json.dumps({k:report[k] for k in ('status','bound','pending_or_unresolved_keys','pending_or_unresolved_signed_obligations')},indent=2))
        return validation_exit(report,args.strict)
    except (ValueError,OSError,KeyError,csv.Error) as exc:
        print('FAIL: '+str(exc),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
