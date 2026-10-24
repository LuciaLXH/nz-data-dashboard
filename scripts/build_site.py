"""Package a validated snapshot with the same static site for either build mode."""
import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = ('population_growth.json', 'supply_per_capita.json', 'flow_percentile.json',
             'regions.json', 'network_records.json', '_runs.jsonl')


def build_site(processed: Path, destination: Path):
    source = ROOT / 'site'
    if destination.resolve() != source.resolve():
        destination.mkdir(parents=True, exist_ok=True)
        for name in ('index.html', 'app.js', 'style.css', 'public.html', 'public.js', 'public.css', 'public-analysis.js'):
            shutil.copy2(source/name, destination/name)
        shutil.copytree(source/'img', destination/'img', dirs_exist_ok=True)
    target = destination/'data'
    target.mkdir(parents=True, exist_ok=True)
    for name in SITE_DATA:
        shutil.copy2(processed/name, target/name)
    for src, dest in [('boundaries_regions_simple.geojson','boundaries.geojson'),
                      ('flow_sites.json','flow_sites.json'),('water_consents.json','water_consents.json')]:
        shutil.copy2(ROOT/'data/ref'/src, target/dest)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--processed',type=Path,default=ROOT/'data/processed')
    parser.add_argument('--out',type=Path,default=ROOT/'site')
    args=parser.parse_args()
    build_site(args.processed,args.out)
    print(f'site packaged → {args.out}')
