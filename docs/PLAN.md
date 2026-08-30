# Execution plan (W0–W4)

Source: external review 2026-08-30 (see `docs/review/`). Target: 2.5–3 weeks
at 15–20 h/week; ~10–12 days full-time.

## W0 · Decisions before building ✅
- [x] Thesis A (supply pressure): **Where will population growth put NZ
      council water supplies under pressure first?**
- [x] Section B ("population can't explain water quality") → ANALYSIS.md
- [x] Cut Streamlit / dual frontend — static site only
- [x] 6 councils: Auckland · Canterbury · Otago · Hawke's Bay · Southland ·
      Waikato (verify Hilltop in W1; ORC/HBRC as confirmed backups)
- [x] Hosting: develop private → make public → open Pages
- 验收 ✅ One sentence: who / for what decision / why this page → README

## W1 · Data landing
- [x] `.gitignore` + `.env` in place（GH Secret 已配置：STATS_NZ_API_KEY）
- [x] Stats NZ 人口 API 跑通 ✅（**新 SDMX API** api.data.stats.govt.nz，2026-08-30；旧 opendata 仍 502）
- [x] Subnational population estimates ✅（6 councils × 2018–2025，`data/raw/population/`）
- [x] Water NZ NPR/NEPR 提取 ✅（NPR 2021/22 全量 + NEPR 2024/25 单位级 CSV，`data/ref/water_demand.json`）
- [x] Boundaries ✅ → `data/ref/boundaries_regions_simple.geojson`（4.9KB；LAWA WKT 替代 Stats NZ GDS，CC BY 4.0）
- [x] Region-name normalisation map ✅ → `data/ref/region_map.json`（REGC 官方验证 02/03/06/13/14/15）
- [x] Hilltop 取数脚本 ✅（HBRC 实时 + ORC 历史；ECan/Southland/Auckland/WRC 无公开时序，W1.5 候选 LAWA flowstats API）
- [x] LAWA water-quality snapshot downloaded manually, record date + URL
  （2026-08-30：7 个 xlsx → `data/raw/lawa/`，清单 `data/raw/lawa/MANIFEST.md`）
- [x] One command produces data/processed/*.json + schema + timestamps ✅（`make data`，schema 校验 8/8）

> **W1 进度（2026-08-30 下午）**：流量取数脚本落地 ✅（HBRC 3 站实时 5 年 + ORC 8 站历史 ~10 年，`scripts/fetch_hilltop.py`，日流量，0 错误；其余 council 公开端点无时序，见 `docs/W1-data-sources.md`）；边界简化 ✅（LAWA boundaryforNZ WKT → `data/ref/boundaries_regions_simple.geojson` 4.9KB，替代 Stats NZ GDS）；区域映射表 ✅（`data/ref/region_map.json`）；`make data` 从零跑通 ✅（W1 最小版 transform/validate，5/5 校验；流量 11 站 + 区域 6 + 人口降级记录）。Stats NZ ADE 仍 502/403（`fetch_population.py` 重试+优雅降级已实现）。
- 验收: `make data` runs from scratch ✅（2026-08-30）

## W2 · Analysis + static site
- [ ] DuckDB wired in; Python does IO/orchestration only
- [ ] sql/01_region_population_growth.sql — window fns YoY + 5yr CAGR
- [ ] sql/02_supply_per_capita.sql — pop × NPR join
- [ ] sql/03_flow_percentile.sql — same-week historical percentile
- [ ] Map: Leaflet + simplified boundary choropleth
- [ ] Chart 1: pop growth vs per-capita use (bubbles, coloured by metering)
- [ ] Chart 2: leakage ranking / demand-supply gap by council
- [ ] **Three written findings finalised** (number + chart + so what)
- [ ] "Why I don't claim causation" written
- 验收（关键闸门）: can tell a 3-minute story in front of the screen.
  If not — fix the thesis, don't add features.

## W3 · Engineering + packaging
- [ ] GH Actions schedule: flow 6 h (from 24 h) · water quality monthly ·
      population monthly
- [ ] retry + exponential backoff + cache last success + graceful degrade
- [ ] `_runs.jsonl` + **Data Health panel** on the site
- [ ] Times: store UTC, display Pacific/Auckland
- [ ] 6 tests: schema · units · region names · DST boundary · missing-value
      propagation · percentile
- [ ] README finalised + 15 s GIF (docs/demo.gif)
- [ ] Attribution blocks (site footer + README)
- [ ] keepalive workflow (scaffolded) + "pipeline paused" fallback text
- [ ] Data not committed to git — CI builds and deploys via deploy-pages
- [ ] Make repo public + open Pages + **verify no key in git history**
- 验收: mobile load < 3 s, no horizontal scroll, all links work

## W4 · After launch
- [ ] LinkedIn post + one chart
- [ ] CV line: link + one quantified result (update career-ops rule 10 then)
- [ ] Prepare for 3 questions: why no causation / how were sources chosen /
      what happens when the pipeline breaks
