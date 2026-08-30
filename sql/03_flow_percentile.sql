-- 03_flow_percentile.sql
-- Source-water availability: latest observed river flow vs the same-week
-- historical percentile, per monitored site (Low / Normal / High).
--
-- Table `flow` (flattened by scripts/transform.py from the council Hilltop
-- snapshots; one row per site-day):
--   council TEXT ('hbrc' | 'orc'), site TEXT, date DATE, flow DOUBLE (m3/s),
--   units TEXT
--
-- Definitions (documented so the numbers are reproducible):
--   latest_date   = the most recent day with a measurement for the site
--                   (HBRC = telemetry up to run time; ORC = the public
--                   server's final day, 2021-01, so "current" means "last
--                   known" there — the front end flags stale sites)
--   window        = the same season in every year: each history date is
--                   shifted into the latest date's year and kept when it
--                   falls within ± 7 days of the latest date (leap-year
--                   dates can land 1 day off — negligible at this window)
--   history       = all days in that window across every year, EXCLUDING the
--                   latest measurement itself; earlier days of the current
--                   year inside the window are kept (they are legitimate
--                   same-period observations)
--   pctile_pct    = share of history strictly below the latest flow × 100
--   band          = < 25 'low' · 25–75 'normal' · > 75 'high'
--                   ('insufficient' when < 5 history days — too few to rank)
--   stale_days    = days since latest_date at run time (Data Health flag)

WITH flow_tbl AS (
    SELECT council, site, CAST(date AS DATE) AS d, flow, MAX(units) AS units
    FROM flow
    WHERE flow IS NOT NULL
    GROUP BY council, site, date, flow
),
latest AS (
    SELECT council, site, MAX(d) AS d
    FROM flow_tbl
    GROUP BY council, site
),
current AS (
    SELECT f.council, f.site, f.d AS latest_date, f.flow AS latest_flow, f.units
    FROM flow_tbl f
    JOIN latest l ON f.council = l.council AND f.site = l.site AND f.d = l.d
),
hist AS (
    SELECT f.council, f.site, f.flow
    FROM flow_tbl f
    JOIN latest l ON f.council = l.council AND f.site = l.site
    WHERE f.d < l.d  -- exclude the latest measurement itself
      -- same-season window: shift each history date into the latest date's
      -- year, keep dates within ± 7 days of the latest date
      AND abs(dayofyear(date_trunc('year', l.d) + (f.d - date_trunc('year', f.d)))
              - dayofyear(l.d)) <= 7
)
SELECT
    c.council,
    c.site,
    c.latest_date,
    ROUND(c.latest_flow, 3) AS latest_flow_m3s,
    c.units,
    COUNT(h.flow) AS n_history,
    ROUND(100.0 * COUNT(*) FILTER (WHERE h.flow < c.latest_flow)
          / NULLIF(COUNT(h.flow), 0), 1) AS pctile_pct,
    CASE
        WHEN COUNT(h.flow) < 5 THEN 'insufficient'
        WHEN 100.0 * COUNT(*) FILTER (WHERE h.flow < c.latest_flow)
             / NULLIF(COUNT(h.flow), 0) < 25 THEN 'low'
        WHEN 100.0 * COUNT(*) FILTER (WHERE h.flow < c.latest_flow)
             / NULLIF(COUNT(h.flow), 0) <= 75 THEN 'normal'
        ELSE 'high'
    END AS band,
    ROUND(MEDIAN(h.flow), 3) AS median_hist_m3s,
    ROUND(MIN(h.flow), 3) AS min_hist_m3s,
    ROUND(MAX(h.flow), 3) AS max_hist_m3s,
    DATE_DIFF('day', c.latest_date, CURRENT_DATE) AS stale_days
FROM current c
LEFT JOIN hist h USING (council, site)
GROUP BY c.council, c.site, c.latest_date, c.latest_flow, c.units
ORDER BY c.council, c.site;
