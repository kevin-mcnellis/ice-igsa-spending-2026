#!/usr/bin/env python3
"""Diagnose fragments, then build the reviewed combined facility-name screen.

From the repository root, run diagnostics with:
    python3 -B File_C_blog_post/run_facility_name_screen.py

Production is a separate, human-gated command:
    python3 -B File_C_blog_post/run_facility_name_screen.py --production
"""
import argparse
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
try:
    from File_C_blog_post.scripts import screen_igsa_ddp_descriptions as core
except ModuleNotFoundError as error:
    if error.name != 'File_C_blog_post':
        raise
    from scripts import screen_igsa_ddp_descriptions as core

LEGACY_BASELINE = {'roster_entities': 224, 'distinct_awards': 9,
                   'candidate_pairs': 9, 'matched_roster_entities': 4,
                   'numeric_25_4_awards': 8,
                   'selected_25_4_amount': '55731217.33'}
ICE_ROW_BASELINE = {'ice_rows': 54202, 'blank_descriptions': 300}


def execute(*, panel_path=None, manifest_path=core.MANIFEST,
            blog_path=core.BLOG_ROWS, source_root=None, strict=False,
            production=False, write=False, legacy_baseline=LEGACY_BASELINE,
            ice_row_baseline=ICE_ROW_BASELINE, fragment_path=None,
            pilot_dir=None, camp_decisions_path=None,
            fragment_review_path=None, review_approval_path=None,
            link_root=None, output_path=None):
    """Return (exit status, compact receipt); writing is explicit for tests."""
    try:
        if link_root is not None and write and not production:
            raise ValueError('portable output requires production mode')
        if link_root is not None and production:
            core.require_portable_paths(
                link_root, review_approval_path=review_approval_path,
                fragment_review_path=fragment_review_path)
        review_approval = core.validate_review_approval(
            review_approval_path=review_approval_path,
            fragment_review_path=fragment_review_path,
            fragment_path=fragment_path) if production else None
        result = core.screen(panel_path, manifest_path, blog_path, source_root,
                             diagnostics=not production, fragment_path=fragment_path,
                             pilot_dir=pilot_dir,
                             camp_decisions_path=camp_decisions_path,
                             link_root=link_root)
        if production:
            if result['reviewed_award_exclusions_not_observed']:
                raise ValueError('reviewed award exclusion not observed in frozen sources')
            for key, expected in legacy_baseline.items():
                if result['legacy_iga_subset'][key] != expected:
                    raise ValueError(f'legacy IGA subset changed: {key}')
            for key, expected in ice_row_baseline.items():
                if result[key] != expected:
                    raise ValueError(f'frozen ICE row baseline changed: {key}')
        report = {'technical_status': 'PASS', 'interpretation_status': 'WARN',
                  'mode': 'production' if production else 'fragment_diagnostics',
                  'candidate_pairs': result['candidate_pairs'],
                  'legacy_iga_subset': result['legacy_iga_subset'],
                  'new_fragment_additions_to_legacy_iga_subset': result[
                      'new_fragment_additions_to_legacy_iga_subset'],
                  'family_totals': result['family_totals'],
                  'pilot_conflicts': len(result['pilot_conflicts'])}
        if write:
            if production:
                destination = (output_path or
                               (Path(link_root)/'outputs/facility_name_screen'
                                if link_root is not None else core.PACKAGE_OUTPUT))
                destination = core.validate_output_path(destination, root=link_root)
                core.write_package_atomic(destination, {
                    **result, 'technical_status': 'PASS',
                    'interpretation_status': 'WARN',
                    'fragment_review_approval': review_approval})
                report['output'] = str(destination)
            else:
                core.write_fragment_review(core.FRAGMENT_REVIEW, result)
                report['fragment_review'] = str(core.FRAGMENT_REVIEW)
        return (1 if strict else 0), report
    except (ValueError, OSError, KeyError) as error:
        return 2, {'technical_status': 'FAIL', 'error': str(error)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--production', action='store_true',
                        help='write the combined pair CSV and verification receipt after human fragment review')
    parser.add_argument('--strict', action='store_true',
                        help='fail on the continuing interpretation warning')
    parser.add_argument('--panel', type=Path)
    parser.add_argument('--source-manifest', type=Path, default=core.MANIFEST)
    parser.add_argument('--blog-financial', type=Path, default=core.BLOG_ROWS)
    parser.add_argument('--source-root', type=Path)
    parser.add_argument('--fragment-file', type=Path)
    parser.add_argument('--pilot-dir', type=Path)
    parser.add_argument('--camp-decisions', type=Path)
    parser.add_argument('--fragment-review-file', type=Path)
    parser.add_argument('--review-approval', type=Path)
    parser.add_argument('--link-root', type=Path,
                        help='release root for stable source-row links and output')
    parser.add_argument('--output-dir', type=Path)
    args = parser.parse_args()
    status, report = execute(panel_path=args.panel, manifest_path=args.source_manifest,
                             blog_path=args.blog_financial, source_root=args.source_root,
                             strict=args.strict, production=args.production, write=True,
                             fragment_path=args.fragment_file, pilot_dir=args.pilot_dir,
                             camp_decisions_path=args.camp_decisions,
                             fragment_review_path=args.fragment_review_file,
                             review_approval_path=args.review_approval,
                             link_root=args.link_root, output_path=args.output_dir)
    print(json.dumps(report, indent=2, sort_keys=True))
    return status


if __name__ == '__main__':
    raise SystemExit(main())
