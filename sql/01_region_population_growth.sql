-- 01_region_population_growth.sql
-- Population growth per regional council: YoY % and 5-year CAGR (window fns).
-- Source: Stats NZ subnational population estimates (POPES_SUB_001, as at 30 June),
-- loaded by scripts/transform.py into DuckDB table `population`:
--   population(region TEXT, year INTEGER, pop DOUBLE, medage DOUBLE, netmig DOUBLE)
--
-- Definitions:
--   yoy_growth_pct  = (pop_t / pop_{t-1} - 1) * 100
--   cagr5_pct       = (pop_t / pop_{t-5})^(1/5) - 1, in %  (5-year compound growth)
--   pop_gain_5yr    = pop_t - pop_{t-5}                     (absolute change, people)

WITH pop AS (
    SELECT region, year, pop
    FROM population
),
growth AS (
    SELECT
        region,
        year,
        pop,
        LAG(pop)      OVER (PARTITION BY region ORDER BY year) AS prev_year_pop,
        LAG(pop, 5)   OVER (PARTITION BY region ORDER BY year) AS five_yr_ago_pop
    FROM pop
)
SELECT
    region,
    year,
    pop,
    ROUND((pop / prev_year_pop - 1) * 100, 2)   AS yoy_growth_pct,
    CASE
        WHEN five_yr_ago_pop IS NOT NULL
        THEN ROUND((POWER(pop / five_yr_ago_pop, 1.0 / 5) - 1) * 100, 2)
    END                                          AS cagr5_pct,
    CASE
        WHEN five_yr_ago_pop IS NOT NULL
        THEN pop - five_yr_ago_pop
    END                                          AS pop_gain_5yr
FROM growth
WHERE prev_year_pop IS NOT NULL   -- no YoY for the first year
ORDER BY region, year;
