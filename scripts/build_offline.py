"""No credentials or network requests: build and validate attributed excerpts."""
import argparse
import hashlib
import json
from pathlib import Path

from build_site import build_site
from transform import ROOT, build
from validate import validate

FIXTURES = ROOT / 'fixtures/offline'


def build_example(output_dir: Path) -> dict:
    manifest = json.loads((FIXTURES/'MANIFEST.json').read_text())
    for name, expected in manifest['files'].items():
        actual = hashlib.sha256((FIXTURES/name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f'Fixture integrity mismatch: {name}; update attribution before rebuilding')
    datasets = build(output_dir,
                     json.loads((FIXTURES/'population.json').read_text()),
                     json.loads((FIXTURES/'flow.json').read_text()),
                     FIXTURES/'networks.csv', input_mode='offline_example',
                     processed_utc=manifest['as_of_utc'])
    for name in ('network_records','supply_per_capita'):
        datasets[name]['example_provenance'] = manifest
        (output_dir/f'{name}.json').write_text(json.dumps(datasets[name],ensure_ascii=False,indent=1,allow_nan=False)+'\n')
    validate(output_dir)
    return datasets


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=ROOT/'.tmp/offline')
    args=parser.parse_args()
    build_example(args.out/'processed')
    build_site(args.out/'processed',args.out/'site')
    print(f'Offline example built and validated → {args.out}/site (sample values, not regional totals)')
