# 3-minute story script (W2 acceptance gate)

> Demo in front of the live site. Each beat maps to a screen element.
> Timing: ~3 minutes total; the numbers are from the 2026-08-30 run.
> Read once out loud against the site before any interview/demo.

## Beat 0 — Hook (10 s)
"Which NZ council will run out of water first under population growth?
I built a pipeline — Stats NZ population × every registered water supply in
6 regions (Taumata Arowai NEPR) — to rank the pressure."

## Beat 1 — Map: where the pressure is (45 s)
"On the map, the six regions are shaded by **projected 2030 demand growth**
— population growth applied to today's per-capita use. Canterbury is darkest:
**+8.1% by 2030**, Waikato +7.2%, Auckland +6.1% (absolute volume: Auckland
+30,000 m³/day, the largest). Southland and Hawke's Bay grow the least.
So on the demand side, **Canterbury and Waikato are the first two to watch** —
but demand is only half the story."

## Beat 2 — Chart 1: the per-capita gap (40 s)
"Left chart: population growth vs litres per person per day; bubble size is
daily demand. **Auckland serves 1.7M people at 270 L/person/day — Hawke's Bay
uses 610.** That's a 2.3× gap. If Hawke's Bay matched Auckland's efficiency,
it would free ≈ 49,000 m³/day — **62% of the entire 6-region demand growth to
2030**. Efficiency is a lever that doesn't wait for population."

## Beat 3 — Chart 2: leaks (40 s)
"Right chart: demand now vs 2030, with leaked volume as the red line.
**22.5% of everything the networks put in is lost to leaks — 299,000 m³/day.**
Canterbury alone leaks 87,000 m³/day, **3.5× its own projected growth** —
its leak volume already exceeds a decade of its demand growth. Fixing leaks
is buying growth headroom."

## Beat 4 — Flow layer & the data finding (35 s)
"The circles are monitored river-flow sites vs their own same-week
historical percentile — the source-water side. But here's the honest finding:
**only 2 of the 6 councils publish open flow time series.** HBRC is live;
ORC's public server froze in 2021 (current values exist on their newer
portal). Where we can look, late-August 2026 flows are at the 9.5th–40.5th
percentile — Ngaruroro at Fernhill is in the driest ~10% of its 5-year
record. Source availability is only locally observable — that's why the
demand-side ranking has to lean on the 6/6 NEPR dataset."

## Beat 5 — Honesty (20 s)
"Why not causation? n = 6, ecological fallacy, and council data is
self-reported. The 2030 projection is demand-only — it's not a full
supply–demand model. What the pipeline does deliver: a reproducible,
data-versioned answer to *which regions to look at first*, with every number
traceable to a public source (Stats NZ, NEPR, LAWA)."

## Beats if asked (back-pocket)
- **Sources & licences:** Stats NZ CC BY 4.0 · NEPR CC BY 3.0 NZ · LAWA CC BY
  4.0 · council Hilltop per-council terms. All URLs/dates/hashes in MANIFEST.
- **Pipeline health:** `_runs.jsonl` records every run; the site degrades to
  stale rather than blank; schema checks record (don't hard-fail).
- **What next (W1.5/W3):** LAWA/ORC-AQWebPortal current flow for the other
  4 councils · metering in the bubble chart · Section B (land use vs quality).
