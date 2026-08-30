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

> **W1 完成（2026-08-30 晚）**：流量取数（HBRC 3 站实时 + ORC 8 站历史）；人口 6 council × 2018–2025（新 SDMX API，REGC 官方验证）；NPR/NEPR 需求数据（`data/ref/water_demand.json`）；区域映射（实测验证）；边界 4.9KB；`make data` 从零跑通（8/8 schema 校验）。唯一待办：GitHub 推送（等 workflow-scope token）。
- 验收: `make data` runs from scratch ✅（2026-08-30，含人口/NPR 全量）

## W2 · Analysis + static site
- [x] DuckDB wired in; Python does IO/orchestration only ✅（transform.py 经 DuckDB 跑 sql/；Makefile 用 .venv python）
- [x] sql/01_region_population_growth.sql — window fns YoY + 5yr CAGR ✅（→ data/processed/population_growth.json，10/10 校验）
- [x] sql/02_supply_per_capita.sql — pop × NEPR 全量 269 系统 ✅（→ supply_per_capita.json，6/6 校验）
- [x] sql/03_flow_percentile.sql — same-week historical percentile ✅（→ flow_percentile.json，11 站；同期窗口跨年按月-日对齐，独立 pandas 交叉验证一致）
- [x] Map: Leaflet + simplified boundary choropleth（供需压力着色 6/6 + 流量站标记 8 个有坐标）✅
- [x] Chart 1: pop growth vs per-capita use (bubbles, colour = leakage; metering 见 water_demand.json 9 供应商) ✅
- [x] Chart 2: leakage / demand–supply gap by council（现 vs 2030 投影 + 漏损叠加线）✅
- [x] **Three written findings finalised** (number + chart + so what) ✅ → ANALYSIS.md + README TL;DR + site Key Findings
- [x] "Why I don't claim causation" written ✅（README + ANALYSIS.md + site，含 flow 覆盖与自报数据限制）
- [ ] 验收（关键闸门）: can tell a 3-minute story in front of the screen.
  If not — fix the thesis, don't add features.（故事脚本见 docs/STORY-3MIN.md）

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
