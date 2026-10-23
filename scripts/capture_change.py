"""Save immutable before/after page evidence for one logical change.

Optional dependency: requirements-review.txt plus `playwright install chromium`.
No data fetch/build is performed. Capture BEFORE editing and AFTER validating,
using the same dataset, section, viewport and comparison clock for each pair.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial
import json
from pathlib import Path
import shutil
import subprocess
import threading

ROOT = Path(__file__).resolve().parent.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture(site: Path, output: Path, section: str):
    from playwright.sync_api import sync_playwright
    if output.exists():
        raise FileExistsError(f'Refusing to overwrite evidence: {output}')
    site = site.resolve()
    flow = json.loads((site/'data/flow_percentile.json').read_text())
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, *_):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(site)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    output.mkdir(parents=True)
    errors, views = [], []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for name, width, height in [('desktop',1440,1000),('mobile',390,844)]:
                page = browser.new_page(viewport={'width':width,'height':height},
                                        device_scale_factor=1, timezone_id='Pacific/Auckland',
                                        locale='en-NZ', reduced_motion='reduce')
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='networkidle')
                page.wait_for_selector('#health-strip .run-bars')
                page.click(f'#sidenav a[data-section="{section}"]')
                page.wait_for_timeout(400)
                page.evaluate('document.fonts.ready')
                if page.evaluate('document.documentElement.scrollWidth > innerWidth'):
                    errors.append(f'{name}: horizontal page overflow')
                # Section crop keeps attention on the changed content; no arbitrary image edits.
                page.locator('#'+section).screenshot(path=str(output/(name+'.png')),animations='disabled')
                views.append({'name':name,'width':width,'height':height,'device_scale_factor':1,
                              'screenshot':name+'.png'})
                page.close()
            browser_version=browser.version
            browser.close()
        shutil.copy2(site/'data/flow_percentile.json',output/'flow_percentile.json')
        files = ['sql/03_flow_percentile.sql','scripts/transform.py','schemas/flow_percentile.schema.json',
                 'site/app.js','site/index.html','site/style.css','scripts/flow_policy.py','scripts/validate_flow.py']
        manifest={'captured_utc':datetime.now(timezone.utc).isoformat(),
                  'section':section,'input_mode':flow.get('input_mode'),
                  'processed_utc':flow['processed_utc'],'flow_schema_version':flow['schema_version'],
                  'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  'working_tree': 'uncommitted work included; hashes, not HEAD alone, identify this state',
                  'source_code_sha256':{f:sha(ROOT/f) for f in files if (ROOT/f).exists()},
                  'served_asset_sha256':{f:sha(site/f) for f in ['app.js','index.html','style.css']},
                  'served_data_sha256':{f.name:sha(f) for f in sorted((site/'data').glob('*')) if f.is_file()},
                  'browser':{'name':'Chromium','version':browser_version,'timezone':'Pacific/Auckland','locale':'en-NZ'},
                  'views':views,'errors':errors}
        manifest['evidence_sha256']={f.name:sha(f) for f in output.iterdir() if f.is_file()}
        (output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
        if errors:
            raise RuntimeError(f'Capture has errors, retain evidence and investigate: {errors}')
        print(f'Captured {section} before/after evidence → {output}')
    finally:
        server.shutdown()
        server.server_close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site',type=Path,default=ROOT/'site')
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--section',default='flow-section')
    args=parser.parse_args()
    capture(args.site,args.out,args.section)
