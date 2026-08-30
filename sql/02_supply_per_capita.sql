-- 02_supply_per_capita.sql
-- Demand-side supply pressure per regional council:
--   population (2025) × per-capita water supply (NEPR 2024/25, weighted across
--   suppliers) → implied daily system demand, leakage, and a 5-year projection.
--
-- Tables (loaded by scripts/transform.py):
--   population(region TEXT, year INT, pop DOUBLE, medage, netmig)
--   water_demand(region TEXT, supplier TEXT, pop_served INT,
--                l_per_person_day DOUBLE, median_res_l_per_conn_day DOUBLE,
--                loss_pct DOUBLE, carl_l_per_conn_day DOUBLE, ili DOUBLE,
--                res_metering_pct DOUBLE)
--
-- Definitions:
--   coverage_pct        = NEPR-supplied pop / regional ERP 2025 (rural areas are
--                         outside piped networks, so <100% is expected; a LOW
--                         value means our demand picture only covers part of the
--                         region, e.g. Waikato = Hamilton city only)
--   l_per_person_day_w  = pop-served-weighted mean of supply L/person/day
--   daily_demand_m3     = regional ERP × weighted supply / 1000  (m³/day)
--   leak_m3_day         = daily_demand × weighted loss%           (m³/day)
--   proj_demand_m3_day  = daily_demand × (1 + cagr5)^5           (5-yr horizon)

WITH pop AS (
    SELECT region, year, pop
    FROM population
),
latest AS (
    SELECT region, pop AS pop_2025
    FROM pop
    WHERE year = (SELECT MAX(year) FROM pop)
),
cagr AS (
    SELECT
        region,
        POWER(pop / LAG(pop, 5) OVER (PARTITION BY region ORDER BY year), 1.0 / 5) - 1 AS cagr5
    FROM pop
    QUALIFY LAG(pop, 5) OVER (PARTITION BY region ORDER BY year) IS NOT NULL
           AND year = (SELECT MAX(year) FROM pop)
),
demand AS (
    SELECT
        region,
        SUM(pop_served) AS pop_served,
        SUM(l_per_person_day * pop_served) FILTER (WHERE l_per_person_day IS NOT NULL)
            / NULLIF(SUM(pop_served) FILTER (WHERE l_per_person_day IS NOT NULL), 0) AS l_per_person_day_w,
        SUM(loss_pct * pop_served) FILTER (WHERE loss_pct IS NOT NULL)
            / NULLIF(SUM(pop_served) FILTER (WHERE loss_pct IS NOT NULL), 0) AS loss_pct_w,
        SUM(res_metering_pct * pop_served) FILTER (WHERE res_metering_pct IS NOT NULL)
            / NULLIF(SUM(pop_served) FILTER (WHERE res_metering_pct IS NOT NULL), 0) AS metering_pct_w,
        SUM(ili * pop_served) FILTER (WHERE ili IS NOT NULL)
            / NULLIF(SUM(pop_served) FILTER (WHERE ili IS NOT NULL), 0) AS ili_w
    FROM water_demand
    GROUP BY region
)
SELECT
    d.region,
    l.pop_2025,
    d.pop_served,
    ROUND(d.pop_served / l.pop_2025 * 100, 1) AS coverage_pct,
    ROUND(d.l_per_person_day_w, 1) AS l_per_person_day_w,
    ROUND(d.loss_pct_w, 1) AS loss_pct_w,
    ROUND(d.metering_pct_w, 1) AS metering_pct_w,
    ROUND(d.ili_w, 2) AS ili_w,
    ROUND(l.pop_2025 * d.l_per_person_day_w / 1000, 0) AS daily_demand_m3,
    ROUND(l.pop_2025 * d.l_per_person_day_w * d.loss_pct_w / 100000, 0) AS leak_m3_day,
    ROUND(c.cagr5 * 100, 2) AS cagr5_pct,
    ROUND(l.pop_2025 * POWER(1 + c.cagr5, 5) * d.l_per_person_day_w / 1000, 0) AS proj_demand_m3_day
FROM demand d
JOIN latest l USING (region)
JOIN cagr c USING (region)
ORDER BY cagr5_pct DESC;
