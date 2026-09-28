#!/usr/bin/env python3
"""Build the recipient chart offline; leave Chart 1 and sources unchanged."""
from datetime import datetime, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET

from PIL import Image
from run import code_version, sha256
from scripts.prepare_chart_2 import prepare, read_csv
from scripts.plot_chart_2 import plot

ROOT = Path(__file__).resolve().parent


def build(project=ROOT):
    project = Path(project).resolve()
    chart1 = project / 'outputs/chart_1'
    before = {p.name: sha256(p) for p in chart1.iterdir() if p.is_file()}
    with TemporaryDirectory(prefix='.chart-build-2-', dir=project) as temp:
        stage = Path(temp) / 'new'
        print('1/2  Reconcile recipient types and the government supporting table…', flush=True)
        analysis = prepare(project, stage)
        print('2/2  Render and inspect the chart files…', flush=True)
        plot(stage / 'recipient_type_totals.csv', stage)
        for path in stage.glob('*.csv'):
            read_csv(path)
        ET.parse(stage / 'recipient_types_25_4.svg')
        with Image.open(stage / 'recipient_types_25_4.png') as image:
            image.verify()
        if before != {p.name: sha256(p) for p in chart1.iterdir() if p.is_file()}:
            raise ValueError('Chart 1 changed during Chart 2 build')
        version = code_version(project)
        for name in ('run_chart_2.py', 'scripts/prepare_chart_2.py', 'scripts/plot_chart_2.py',
                     'data/chart_2_recipient_crosswalk.csv', 'provenance/chart_2_entity_evidence.json',
                     'scripts/shared_recipients.py', 'data/shared_recipient_crosswalk.csv',
                     'scripts/object_class_25_2_recipients.py',
                     'provenance/object_class_25_2_entity_evidence.json',
                     'provenance/object_class_25_2_source_context.json',
                     'provenance/shared_25_4_award_check.json'):
            version['file_sha256'][name] = sha256(project / name)
        for name in ('scripts/recipient_rules.py','provenance/private_entity_rule_v1.json'):
            if (project/name).exists():version['file_sha256'][name] = sha256(project/name)
        report = {'technical_status': 'PASS', 'interpretation_status': 'WARN',
                  'analysis': analysis, 'source_version': version,
                  'chart_1_unchanged_sha256': before,
                  'completed_at_utc': datetime.now(timezone.utc).isoformat(),
                  'output_sha256': {p.name: sha256(p) for p in stage.iterdir() if p.is_file()}}
        (stage / 'verification.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
        output = project / 'outputs/chart_2'
        previous = Path(temp) / 'previous'
        try:
            if output.exists():
                output.rename(previous)
            stage.rename(output)
        except BaseException:
            if previous.exists() and not output.exists():
                previous.rename(output)
            raise
    return report


if __name__ == '__main__':
    build()
    print('PASS: Chart 2 rebuilt. WARN: recipient totals are not detention-specific payments; government coverage is bounded.')
