-- Calendar-year joins: missing years never become the previous available row.
SELECT p.region, p.year, p.pop,
    p.year - 1 AS previous_year,
    p.year - 5 AS cagr_start_year,
    p.year AS cagr_end_year,
    100.0 * (p.pop / NULLIF(prev.pop, 0) - 1) AS yoy_growth_pct,
    CASE WHEN history.n = 6 AND past.pop > 0
         THEN 100.0 * (POWER(p.pop / past.pop, 1.0 / 5) - 1) END AS cagr5_pct,
    CASE WHEN history.n = 6 THEN p.pop - past.pop END AS pop_gain_5yr
FROM population p
LEFT JOIN population prev ON prev.region = p.region AND prev.year = p.year - 1
LEFT JOIN population past ON past.region = p.region AND past.year = p.year - 5
LEFT JOIN LATERAL (
    SELECT COUNT(*) AS n FROM population h
    WHERE h.region = p.region AND h.year BETWEEN p.year - 5 AND p.year AND h.pop > 0
) history ON TRUE
ORDER BY p.region, p.year;
