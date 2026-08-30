-- 02_supply_per_capita.sql
-- Demand-side supply pressure per regional council, derived from the FULL
-- NEPR 2024/25 unit-level extract (all registered drinking-water supplies in
-- the 6 regions — not just the main urban supplier):
--   population (2025) × per-capita water supply → implied daily system demand,
--   leakage, and a 5-year projection.
--
-- Table `nepr_network` (one row per supply; loaded by scripts/transform.py
-- from the raw NEPM unit-level CSV, orgs mapped to the 6 project regions):
--   region TEXT, org, supply, res_connections, pop_served,
--   water_supplied_m3 (m³/yr), loss_m3 (m³/yr), carl_m3_year (m³/yr),
--   ili, median_res_l_conn_day
-- Table `population(region, year, pop)` as in sql/01.
--
-- Definitions:
--   coverage_pct        = NEPR pop served / regional ERP 2025 (rural areas are
--                         self-supplied, so <100% is expected; the national
--                         share on public networks is ~84%, per NEPR 2024/25)
--   l_per_person_day    = water_supplied_m3 × 1000 ÷ 365 ÷ pop_served
--   loss_pct            = loss_m3 ÷ water_supplied_m3 × 100
--   carl_l_conn_day     = carl_m3_year × 1000 ÷ 365 ÷ res_connections
--   daily_demand_m3     = regional ERP × weighted supply / 1000   (m³/day)
--   leak_m3_day         = daily_demand × weighted loss%
--   proj_demand_m3_day  = daily_demand × (1 + cagr5)^5

WITH pop AS (
    SELECT region, year, pop FROM population
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
sup AS (
    SELECT
        region,
        pop_served,
        water_supplied_m3 * 1000 / 365 / NULLIF(pop_served, 0)  AS l_per_person_day,
        loss_m3 / NULLIF(water_supplied_m3, 0) * 100            AS loss_pct,
        carl_m3_year * 1000 / 365 / NULLIF(res_connections, 0)  AS carl_l_conn_day,
        ili,
        res_connections
    FROM nepr_network
),
demand AS (
    SELECT
        region,
        SUM(pop_served) AS pop_served,
        SUM(l_per_person_day * pop_served) FILTER (WHERE l_per_person_day IS NOT NULL)
            / NULLIF(SUM(pop_served) FILTER (WHERE l_per_person_day IS NOT NULL), 0) AS l_per_person_day_w,
        SUM(loss_pct * pop_served) FILTER (WHERE loss_pct IS NOT NULL)
            / NULLIF(SUM(pop_served) FILTER (WHERE loss_pct IS NOT NULL), 0) AS loss_pct_w,
        SUM(carl_l_conn_day * pop_served) FILTER (WHERE carl_l_conn_day IS NOT NULL)
            / NULLIF(SUM(pop_served) FILTER (WHERE carl_l_conn_day IS NOT NULL), 0) AS carl_l_conn_day_w,
        SUM(ili * pop_served) FILTER (WHERE ili IS NOT NULL)
            / NULLIF(SUM(pop_served) FILTER (WHERE ili IS NOT NULL), 0) AS ili_w
    FROM sup
    GROUP BY region
)
SELECT
    d.region,
    l.pop_2025,
    d.pop_served,
    ROUND(d.pop_served / l.pop_2025 * 100, 1) AS coverage_pct,
    ROUND(d.l_per_person_day_w, 1) AS l_per_person_day_w,
    ROUND(d.loss_pct_w, 1) AS loss_pct_w,
    ROUND(d.carl_l_conn_day_w, 1) AS carl_l_conn_day_w,
    ROUND(d.ili_w, 2) AS ili_w,
    ROUND(l.pop_2025 * d.l_per_person_day_w / 1000, 0) AS daily_demand_m3,
    ROUND(l.pop_2025 * d.l_per_person_day_w * d.loss_pct_w / 100000, 0) AS leak_m3_day,
    ROUND(c.cagr5 * 100, 2) AS cagr5_pct,
    ROUND(l.pop_2025 * POWER(1 + c.cagr5, 5) * d.l_per_person_day_w / 1000, 0) AS proj_demand_m3_day
FROM demand d
JOIN latest l USING (region)
JOIN cagr c USING (region)
ORDER BY cagr5_pct DESC;
