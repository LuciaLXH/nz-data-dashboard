"""Optional browser regression check. Run make offline first; needs requirements-review.txt and Chromium.
Reads production and offline saved datasets without fetching sources. Saves local review screenshots.
"""
import json, threading, os
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
(ROOT/".tmp/public-review").mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory='.'))
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}'
water=json.loads(Path('site/data/supply_per_capita.json').read_text())
flow=json.loads(Path('site/data/flow_percentile.json').read_text())
errors=[]
with sync_playwright() as p:
    browser=p.chromium.launch()
    for width,height in [(1440,1000),(820,1000),(390,844)]:
        for lang in ['zh','en']:
            page=browser.new_page(viewport={'width':width,'height':height})
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(f'{base}/site/public.html?lang={lang}',wait_until='networkidle')
            page.wait_for_selector('body[data-ready="true"]')
            assert page.locator('html').get_attribute('lang')==('zh-CN' if lang=='zh' else 'en-NZ')
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
            for row in water['rows']:
                page.select_option('#region-select',row['region'])
                for metric,field in [('supply','supply_l_person_day'),('loss','paired_loss_pct'),('growth','cagr5_pct')]:
                    page.select_option('#measure-select',metric)
                    bars=page.locator('#comparison-bars li')
                    assert bars.count()==len(water['rows'])
                    for idx,raw in enumerate(water['rows']):
                        value=raw[field]
                        shown=bars.nth(idx).locator('.bar-value').inner_text()
                        if value is None:
                            assert shown==('暂无可比数据' if lang=='zh' else 'Unavailable')
                            assert bars.nth(idx).locator('.fill').count()==0
                        else:
                            numeric=float(shown.split()[0].replace(',',''))
                            assert abs(numeric-value)<=0.051,(shown,value)
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
            # Check the new plots against independent source fields, including empty cohorts.
            for boundary in ['No','Yes','unknown']:
                page.select_option('#story-boundary',boundary)
                chart_rows=page.locator('.coverage-row')
                assert chart_rows.count()==len(water['rows'])
                for i,r in enumerate(water['rows']):
                    cohort=next(c for c in r['loss_cohorts'] if c['boundary']==boundary)
                    for selector,field in [('loss-meter','paired_loss_pct'),('coverage-meter','paired_supply_coverage_pct')]:
                        bar=chart_rows.nth(i).locator('.'+selector+' .meter-track>span')
                        value=cohort[field]
                        assert bar.count()==(0 if value is None else 1)
                        if value is not None:
                            shown=float(bar.get_attribute('style').split(':')[1].rstrip('%'))
                            assert abs(shown-value)<1e-8
            point=page.locator('.scatter-point[data-select-region="hawkes_bay"]')
            point.focus();page.keyboard.press('Enter')
            assert page.locator('#region-select').input_value()=='hawkes_bay'
            assert page.locator('.region-link[data-select-region="hawkes_bay"]').get_attribute('aria-pressed')=='true'
            page.locator('.region-link[data-select-region="otago"]').click()
            assert page.locator('.scatter-point[data-select-region="otago"]').get_attribute('aria-pressed')=='true'
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
            page.select_option('#region-select','southland')
            assert ('暂无可比数据' if lang=='zh' else 'Unavailable') in page.locator('#region-results').inner_text()
            page.locator('#rivers .full-records > summary').click()
            assert page.locator('#river-rows tr').count()==len(flow['rows'])
            for i,r in enumerate(flow['rows']):
                cells=page.locator('#river-rows tr').nth(i).locator('td')
                assert r['latest_date'] in cells.nth(1).inner_text()
                if r['history_status']!='sufficient':
                    assert ('不足' if lang=='zh' else 'Not enough') in cells.nth(3).inner_text()
            page.click('#lang-'+('en' if lang=='zh' else 'zh'))
            page.wait_for_selector('body[data-ready="true"]')
            assert page.locator('#region-select').input_value()=='southland'
            page.close()
    for lang in ['zh','en']:
        page=browser.new_page(viewport={'width':390,'height':844})
        page.goto(f'{base}/.tmp/offline/site/public.html?lang={lang}',wait_until='networkidle')
        page.wait_for_selector('body[data-ready="true"]')
        assert page.locator('#example-banner').is_visible()
        page.locator('#rivers .full-records > summary').click()
        assert page.locator('#river-rows tr').count()==2
        assert ('不足' if lang=='zh' else 'Not enough') in page.locator('#river-rows').inner_text()
        page.close()
    page=browser.new_page()
    page.route('**/data/supply_per_capita.json',lambda route:route.fulfill(status=503,body='Unavailable'))
    page.goto(f'{base}/site/public.html?lang=zh',wait_until='networkidle')
    assert page.locator('#load-status').get_attribute('role')=='alert'
    assert page.locator('#region-select').is_disabled()
    assert page.locator('#background').is_visible()
    page.close()
    for lang in ['zh','en']:
        for label,width,height in [('desktop',1440,1000),('mobile',390,844)]:
            page=browser.new_page(viewport={'width':width,'height':height})
            page.goto(f'{base}/site/public.html?lang={lang}',wait_until='networkidle')
            page.wait_for_selector('body[data-ready="true"]')
            page.screenshot(path=f'.tmp/public-review/{lang}-{label}.png')
            if label=='desktop':
                page.locator('#regional').screenshot(path=f'.tmp/public-review/{lang}-regional.png')
            page.close()
    browser.close()
server.shutdown()
assert not errors,errors
print('PASS: both languages at 3 widths; region/metric data and 3 loss boundaries reconciled; linked plot controls and keyboard; dates/history; language state; offline and failure states; no errors/overflow.')
