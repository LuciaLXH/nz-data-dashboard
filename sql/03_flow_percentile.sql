-- Latest daily flow versus completed prior seasonal windows (v2).
-- Build the latest month/day separately in each season year; Feb 29 → Feb 28
-- only in non-leap years. Actual date intervals cross New Year correctly.
-- The current partial season is excluded. Window years label their centre,
-- so a Dec/Jan window is one season, not two independent historical years.
-- Empty seasons within the source record span remain visible in coverage.
-- The display gate is a project convention, not a climatological standard.
WITH flow_tbl AS (
    SELECT council, site, CAST(date AS DATE) AS d, flow, units
    FROM flow WHERE flow IS NOT NULL AND ISFINITE(flow) AND flow >= 0
), bounds AS (
    SELECT council, site, MIN(d) AS first_date, MAX(d) AS latest_date
    FROM flow_tbl GROUP BY council, site
), current AS (
    SELECT f.council, f.site, b.first_date, b.latest_date,
        f.flow AS latest_flow, f.units
    FROM flow_tbl f JOIN bounds b USING (council, site)
    WHERE f.d = b.latest_date
), anchors AS (
    SELECT c.council, c.site, c.first_date, c.latest_date, y.season_year,
        MAKE_DATE(y.season_year::INTEGER, MONTH(c.latest_date)::INTEGER,
            LEAST(DAY(c.latest_date), DAY(LAST_DAY(MAKE_DATE(
                y.season_year::INTEGER, MONTH(c.latest_date)::INTEGER, 1))))::INTEGER) AS anchor
    FROM current c,
         RANGE(YEAR(c.first_date) - 1, YEAR(c.latest_date) + 1) y(season_year)
), windows AS (
    SELECT a.*, p.window_radius_days * 2 + 1 AS expected_days,
           p.min_days_per_year
    FROM anchors a CROSS JOIN flow_policy p
    WHERE a.anchor + p.window_radius_days < a.latest_date
      AND a.anchor + p.window_radius_days >= a.first_date
), history AS (
    SELECT w.council, w.site, w.season_year, f.d, f.flow
    FROM windows w CROSS JOIN flow_policy p
    JOIN flow_tbl f ON f.council = w.council AND f.site = w.site
       AND f.d BETWEEN w.anchor - p.window_radius_days AND w.anchor + p.window_radius_days
), by_year AS (
    SELECT w.council, w.site, w.season_year, w.expected_days,
           COUNT(h.flow) AS observed_days,
           COUNT(h.flow) >= w.min_days_per_year AS qualifies
    FROM windows w LEFT JOIN history h USING (council, site, season_year)
    GROUP BY w.council, w.site, w.season_year, w.expected_days, w.min_days_per_year
), coverage AS (
    SELECT council, site,
        COUNT(*) AS n_history_seasons,
        COUNT(*) FILTER (WHERE observed_days > 0) AS n_history_years,
        COUNT(*) FILTER (WHERE qualifies) AS n_qualified_years,
        MIN(season_year) AS history_year_start, MAX(season_year) AS history_year_end,
        SUM(expected_days) AS expected_history_days,
        100.0 * SUM(observed_days) / SUM(expected_days) AS history_coverage_pct,
        LIST(STRUCT_PACK(season_year := season_year, observed_days := observed_days,
             expected_days := expected_days, qualifies := qualifies) ORDER BY season_year) AS history_years
    FROM by_year GROUP BY council, site
), stats AS (
    SELECT c.council, c.site, c.latest_date, c.latest_flow, c.units,
        COUNT(h.flow) AS n_history,
        COUNT(*) FILTER (WHERE h.flow < c.latest_flow) AS n_below_latest,
        MIN(h.d) AS history_first_date, MAX(h.d) AS history_last_date,
        MEDIAN(h.flow) AS median_hist_m3s, MIN(h.flow) AS min_hist_m3s,
        MAX(h.flow) AS max_hist_m3s
    FROM current c LEFT JOIN history h USING (council, site)
    GROUP BY c.council, c.site, c.latest_date, c.latest_flow, c.units
), measures AS (
    SELECT s.* EXCLUDE(latest_flow), s.latest_flow AS latest_flow_m3s,
        COALESCE(v.n_history_seasons, 0) AS n_history_seasons,
        COALESCE(v.n_history_years, 0) AS n_history_years,
        COALESCE(v.n_qualified_years, 0) AS n_qualified_years,
        v.history_year_start, v.history_year_end,
        COALESCE(v.expected_history_days, 0) AS expected_history_days,
        v.history_coverage_pct, COALESCE(v.history_years, []) AS history_years,
        CASE WHEN COALESCE(v.n_qualified_years, 0) >= p.min_history_years
             THEN 100.0 * s.n_below_latest / NULLIF(s.n_history, 0) END AS pctile_pct,
        DATE_DIFF('day', s.latest_date, (SELECT as_of_date FROM build_context)) AS stale_days
    FROM stats s LEFT JOIN coverage v USING (council, site) CROSS JOIN flow_policy p
)
SELECT *,
    CASE WHEN pctile_pct IS NULL THEN 'insufficient'
         WHEN pctile_pct < 25 THEN 'low'
         WHEN pctile_pct <= 75 THEN 'normal'
         ELSE 'high' END AS band,
    CASE WHEN pctile_pct IS NULL THEN 'insufficient_years' ELSE 'sufficient' END AS history_status
FROM measures ORDER BY council, site;
