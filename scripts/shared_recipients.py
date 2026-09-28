"""One reviewed recipient decision and one display mapping for both object classes.

API evidence is not an approval. Edit the shared CSV only after reviewing its
linked evidence; saved Chart 2 decisions remain immutable migration evidence.
"""
import csv

CROSSWALK = 'data/shared_recipient_crosswalk.csv'
SELECTED = 'Selected private detention contractors'
OTHER_PRIVATE = 'Other private contractors'
GOVERNMENT = 'State and local governments'
OTHER_PUBLIC = 'Other public or nonprofit entities'
NO_RECIPIENT = 'No recipient reported'
UNRESOLVED = 'Unresolved'
TYPES = (SELECTED, OTHER_PRIVATE, GOVERNMENT, OTHER_PUBLIC, NO_RECIPIENT, UNRESOLVED)
ENTITY_TYPES = {'private','state_local_government','tribal_government',
                'federal_entity','other_public_nonprofit','unresolved'}
FIELDS = ('key','recipient_uei','recipient_name','entity_type',
          'selected_detention_contractor','review_status','basis','evidence_url',
          'relationship_url','checked_date','decision_origin','proposed_entity_type',
          'reviewed_diagnostic_sha256','classification_rule_id','classification_evidence_sha256')
ACCEPTED_STATUSES = ('reviewed','rule_approved')
LEGACY_FIELDS = ('key','recipient_uei','recipient_name','type','evidence_url',
                 'basis','review_status','relationship_url','checked_date')


def recipient_key(row):
    uei=row['recipient_uei'].strip();name=row['recipient_name'].strip()
    return 'uei:'+uei if uei else 'name:'+name if name else 'missing'


def display_type(decision, key=None):
    if key=='missing' or decision and decision['key']=='missing':return NO_RECIPIENT
    if not decision or decision['review_status'] not in ACCEPTED_STATUSES:return UNRESOLVED
    kind=decision['entity_type']
    if kind=='private':
        return SELECTED if decision['selected_detention_contractor']=='true' else OTHER_PRIVATE
    return {'state_local_government':GOVERNMENT,'federal_entity':OTHER_PUBLIC,
            'other_public_nonprofit':OTHER_PUBLIC}.get(kind,UNRESOLVED)


def load(project):
    with (project/CROSSWALK).open(newline='',encoding='utf-8') as f:
        reader=csv.DictReader(f,strict=True)
        if (len(reader.fieldnames or [])!=len(set(reader.fieldnames or [])) or
                set(reader.fieldnames or []) not in (set(FIELDS),set(FIELDS[:-2]))):
            raise ValueError('invalid shared crosswalk columns')
        rows=list(reader)
    historical_path=project/'data/chart_2_recipient_crosswalk.csv'
    historical={}
    if historical_path.exists():
        with historical_path.open(newline='',encoding='utf-8') as f:
            historical={r['key']:r for r in csv.DictReader(f)}
    out={}
    for row in rows:
        if None in row or any(v is None for v in row.values()):raise ValueError('malformed shared decision')
        row.setdefault('classification_rule_id','');row.setdefault('classification_evidence_sha256','')
        key=row['key']
        if key in out or key!=recipient_key(row):raise ValueError('duplicate or inconsistent shared key')
        if row['entity_type'] not in ENTITY_TYPES:raise ValueError('unknown shared entity type')
        if row['selected_detention_contractor'] not in ('true','false'):raise ValueError('invalid selected flag')
        if row['selected_detention_contractor']=='true' and row['entity_type']!='private':
            raise ValueError('selected contractor must be a private entity')
        if row['review_status'] not in (*ACCEPTED_STATUSES,'pending'):raise ValueError('unknown review status')
        if row['review_status'] in ACCEPTED_STATUSES:
            if not row['recipient_uei'] or row['entity_type']=='unresolved':
                raise ValueError('reviewed identity must have an exact UEI and resolved type')
            if not row['basis'] or not row['evidence_url'].startswith('https://') or not row['checked_date']:
                raise ValueError('reviewed decision requires dated evidence and basis')
        if row['decision_origin'] not in ('chart_2_review','manual_review','api_proposal','missing_identity','approved_rule'):
            raise ValueError('invalid shared decision origin')
        if row['decision_origin'] in ('api_proposal','missing_identity') and row['review_status']!='pending':
            raise ValueError('API proposals cannot approve themselves')
        if (row['review_status']=='rule_approved')!=(row['decision_origin']=='approved_rule'):
            raise ValueError('rule approval requires its explicit origin and status')
        if row['proposed_entity_type'] and row['proposed_entity_type'] not in ENTITY_TYPES:
            raise ValueError('unknown proposed entity type')
        if historical:
            prior=historical.get(key)
            selected=bool(prior and prior['type']==SELECTED)
            if (row['selected_detention_contractor']=='true')!=selected:
                raise ValueError('selected membership differs from approved historical list')
            if row['decision_origin']=='chart_2_review':
                if not prior or any(row[f]!=prior[f] for f in LEGACY_FIELDS if f!='type'):
                    raise ValueError('carried decision changed without manual review')
                if display_type(row)!=prior['type']:
                    raise ValueError('carried display category changed without review')
        out[key]=row
    from scripts.recipient_rules import validate_batch
    validate_batch(project,out)
    return out


def chart_crosswalk(decisions):
    """Adapt shared decisions to the stable Chart 2 CSV schema."""
    return {key:{**{field:row[field] for field in LEGACY_FIELDS if field not in ('type','review_status')},
                 'type':display_type(row),
                 'review_status':'pending' if display_type(row)==UNRESOLVED else row['review_status']}
            for key,row in decisions.items() if key!='missing'}


def diagnostics(project, decisions):
    """Read saved evidence only; expose unresolved warnings to both consumers."""
    import json
    from scripts import object_class_25_2_recipients as m
    from scripts.portable_chart_2_evidence import validate_bundle
    validate_bundle(project)
    sources={name:json.loads((project/path).read_text())['records'] for name,path in (
        ('25.2',m.EVIDENCE),('25.4','provenance/shared_25_4_award_check.json'))}
    results={}
    for obj,records in sources.items():
        for key,record in records.items():
            if key not in decisions:raise ValueError('diagnostic recipient outside shared universe')
            uei=decisions[key]['recipient_uei']
            digest=m.population_digest({name:items.get(key) for name,items in sources.items()})
            p={'recipient_key':key,'recipient_uei':uei,
               **m.propose(uei,record,len(record.get('awards',[]))),
               'diagnostic_evidence_sha256':digest}
            resolved=m.resolve_shared([p],decisions)[0]
            if resolved['shared_decision_warning']:
                urls=sorted({a.get('request_url',a.get('source_url','')) for a in record.get('awards',[])}
                            | {a.get('award_url','') for a in record.get('awards',[])}
                            | {(record.get('profile') or {}).get('request_url','')} - {''})
                prior=results.get(key)
                results[key]={**resolved,
                    'diagnostic_object_class':prior['diagnostic_object_class']+' | '+obj if prior else obj,
                    'diagnostic_details':(prior['diagnostic_details']+' | ' if prior else '')+
                                         obj+': '+resolved['shared_decision_warning'],
                    'diagnostic_urls':' | '.join(sorted(set(urls+(prior['diagnostic_urls'].split(' | ') if prior else []))))}
    return results


def initialize(project, proposals, old_rows, old_evidence, old_category):
    """Explicit one-time migration. Never overwrite a human-edited crosswalk."""
    path=project/CROSSWALK
    if path.exists():raise ValueError('shared crosswalk already exists; refusing to replace decisions')
    rows={}
    for old in old_rows:
        kind=old_category(old,old_evidence.get(old['recipient_uei'],{}))
        rows[old['key']]={**{f:old[f] for f in LEGACY_FIELDS if f!='type'},'entity_type':kind,
            'selected_detention_contractor':str(old['type']==SELECTED).lower(),
            'decision_origin':'chart_2_review','proposed_entity_type':'','reviewed_diagnostic_sha256':''}
    for p in proposals:
        key=p['recipient_key']
        if key in rows:continue
        kind=p['category'] if p['category'] in ENTITY_TYPES else 'unresolved'
        rows[key]={'key':key,'recipient_uei':p['recipient_uei'],'recipient_name':p['recipient_name'],
                   'entity_type':'unresolved','selected_detention_contractor':'false','review_status':'pending',
                   'basis':p['basis'],'evidence_url':p['evidence_url'],'relationship_url':'','checked_date':'',
                   'decision_origin':'api_proposal' if p['recipient_uei'] else 'missing_identity',
                   'proposed_entity_type':kind,'reviewed_diagnostic_sha256':''}
    with path.open('x',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS);writer.writeheader()
        writer.writerows(rows[k] for k in sorted(rows))
    return load(project)
