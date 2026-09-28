"""Copy a hash-verified Figure A image; default uses the published July 9 map."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

EXPECTED = '6251658338864e3e257e7213a8c2f8f4716a5b32e8e4a943f477a808b2bdaa0a'
POST = 'https://www.kevinmcnellis.com/posts/ice_facilities/'


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def copy_figure(project, output, *, expected_sha256=EXPECTED,
                source_path=None, verification_path=None):
    project = Path(project).resolve()
    if source_path is not None or verification_path is not None:
        if source_path is None or verification_path is None:
            raise ValueError('selected Figure A requires image and review receipt')
        source = Path(source_path).resolve()
        receipt = Path(verification_path).resolve()
        output = Path(output)
        if (not source.is_relative_to(project) or
                not receipt.is_relative_to(project) or
                not output.resolve().is_relative_to(project) or
                output.is_symlink()):
            raise ValueError('selected Figure A paths must stay inside release root')
        review = json.loads(receipt.read_text())
        if (review['output_sha256'].get(source.name) != expected_sha256 or
                sha256(source) != expected_sha256):
            raise ValueError('selected Figure A bytes differ from reviewed source')
        output.mkdir(parents=True, exist_ok=True)
        provenance = output/'figure_a_provenance.json'
        if provenance.is_symlink():
            raise ValueError('selected Figure A provenance must not be a symlink')
        target = output/source.name
        if target.is_symlink():
            raise ValueError('selected Figure A destination must not be a symlink')
        if target.exists():
            if sha256(target) != expected_sha256:
                raise ValueError('selected Figure A destination has different bytes')
        else:
            shutil.copyfile(source, target)
        if sha256(target) != expected_sha256:
            raise ValueError('selected Figure A copied bytes differ from verified source')
        report = {'reuse_status': 'copied_verified_selected_variant',
                  'source_path': source.relative_to(project).as_posix(),
                  'review_receipt_path': receipt.relative_to(project).as_posix(),
                  'source_sha256': expected_sha256,
                  'copy_sha256': sha256(target),
                  'note': 'Selected review variant reused byte for byte; this copy does not establish publication.'}
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=output,
                                         prefix='.figure_a_provenance.',
                                         delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(json.dumps(report, indent=2, sort_keys=True)+'\n')
        try:
            os.replace(temporary, provenance)
        finally:
            temporary.unlink(missing_ok=True)
        return report
    repository = project.parent
    source = repository/'output/map-graphic/panel_2026-07-09.png'
    published = repository.parent/'kevinmcnellis-site/posts/ice_facilities/images/panel_2026-07-09.png'
    manifest_path = repository/'output/map-graphic/run-manifest.json'
    manifest = json.loads(manifest_path.read_text())
    hashes = {'repository_map': sha256(source), 'published_source': sha256(published),
              'map_manifest': manifest['outputs_sha256'][source.name]}
    if len(set(hashes.values()) | {expected_sha256}) != 1:
        raise ValueError('Figure A source, published image, and map manifest hashes disagree')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    target = output/source.name
    shutil.copyfile(source, target)
    if sha256(target) != expected_sha256:
        raise ValueError('Figure A copied bytes differ from verified source')
    report = {'reuse_status': 'copied_unchanged', 'source_path': str(source),
              'published_source_path': str(published), 'map_manifest_path': str(manifest_path),
              'published_post_url': POST, 'source_hashes': hashes,
              'source_sha256': expected_sha256, 'copy_sha256': sha256(target),
              'schema_version': manifest['schema_version'], 'renderer': manifest['renderer'],
              'note': 'Published figure reused byte for byte; it was not rebuilt, cropped, or restyled.'}
    (output/'figure_a_provenance.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    return report
