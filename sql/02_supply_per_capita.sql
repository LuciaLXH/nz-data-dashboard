-- Version 2: reported network inputs and boundary-specific paired water loss.
-- Inputs are identity-resolved by nepr.py, with invalid numeric values NULL.
-- No rounding here: preserve contributions for reconciliation, round in the UI.
-- build_context supplies period_days and scenario_horizon_years explicitly.
WITH pop_latest AS (
    SELECT region, year, pop FROM population
    QUALIFY ROW_NUMBER() OVER (PARTITION BY region ORDER BY year DESC) = 1
), growth AS (
    SELECT p.*, p.year - 5 AS cagr_start_year,
        CASE WHEN h.n = 6 AND past.pop > 0
             THEN POWER(p.pop / past.pop, 1.0 / 5) - 1 END AS cagr
    FROM pop_latest p
    LEFT JOIN population past ON past.region = p.region AND past.year = p.year - 5
    LEFT JOIN LATERAL (
        SELECT COUNT(*) AS n FROM population v
        WHERE v.region = p.region AND v.year BETWEEN p.year - 5 AND p.year AND v.pop > 0
    ) h ON TRUE
), eligible AS (
    SELECT *,
        supply_m3_year IS NOT NULL AND population_served > 0 AS per_person_eligible,
        supply_m3_year > 0 AND loss_m3_year IS NOT NULL
            AND loss_m3_year <= supply_m3_year AS paired_eligible
    FROM nepr_network
), totals AS (
    SELECT region, COUNT(*) AS candidate_networks,
        COUNT(supply_m3_year) AS reported_supply_networks,
        SUM(supply_m3_year) AS reported_supply_m3_year,
        COUNT(*) FILTER (WHERE per_person_eligible) AS supply_population_networks,
        SUM(supply_m3_year) FILTER (WHERE per_person_eligible) AS supply_population_supply_m3_year,
        SUM(population_served) FILTER (WHERE per_person_eligible) AS supply_population_served_people,
        COUNT(*) FILTER (WHERE supply_m3_year IS NULL) AS missing_or_invalid_supply_networks,
        COUNT(*) FILTER (WHERE loss_m3_year IS NULL) AS missing_or_invalid_loss_networks,
        COUNT(*) FILTER (WHERE loss_m3_year > supply_m3_year) AS loss_above_supply_networks
    FROM eligible GROUP BY region
), boundaries AS (
    SELECT g.region, b.boundary
    FROM growth g CROSS JOIN (VALUES ('No'), ('Yes'), ('unknown')) b(boundary)
), cohort AS (
    SELECT b.region, b.boundary,
        COUNT(e.network_key) AS boundary_candidate_networks,
        COUNT(e.loss_m3_year) AS reported_loss_networks,
        SUM(e.loss_m3_year) AS reported_loss_m3_year,
        COUNT(*) FILTER (WHERE e.paired_eligible) AS paired_networks,
        SUM(e.supply_m3_year) FILTER (WHERE e.paired_eligible) AS paired_supply_m3_year,
        SUM(e.loss_m3_year) FILTER (WHERE e.paired_eligible) AS paired_loss_m3_year,
        COUNT(*) FILTER (WHERE e.loss_m3_year > e.supply_m3_year) AS loss_above_supply_networks
    FROM boundaries b LEFT JOIN eligible e
        ON e.region = b.region AND e.private_loss_boundary = b.boundary
    GROUP BY b.region, b.boundary
), cohort_rates AS (
    SELECT c.*,
        100.0 * c.paired_loss_m3_year / NULLIF(c.paired_supply_m3_year, 0) AS paired_loss_pct,
        100.0 * c.paired_networks / NULLIF(t.candidate_networks, 0) AS paired_network_coverage_pct,
        100.0 * c.paired_supply_m3_year / NULLIF(t.reported_supply_m3_year, 0) AS paired_supply_coverage_pct
    FROM cohort c LEFT JOIN totals t USING (region)
), cohort_lists AS (
    SELECT region, LIST(STRUCT_PACK(
        boundary := boundary,
        boundary_candidate_networks := boundary_candidate_networks,
        reported_loss_networks := reported_loss_networks,
        reported_loss_m3_year := reported_loss_m3_year,
        paired_networks := paired_networks,
        paired_supply_m3_year := paired_supply_m3_year,
        paired_loss_m3_year := paired_loss_m3_year,
        paired_loss_pct := paired_loss_pct,
        paired_network_coverage_pct := paired_network_coverage_pct,
        paired_supply_coverage_pct := paired_supply_coverage_pct,
        loss_above_supply_networks := loss_above_supply_networks
    ) ORDER BY boundary) AS loss_cohorts
    FROM cohort_rates GROUP BY region
), measures AS (
    SELECT g.region, g.year AS population_base_year, g.pop AS population_base,
        g.cagr_start_year, g.year AS cagr_end_year, g.cagr * 100 AS cagr5_pct,
        g.year + ctx.scenario_horizon_years AS projection_year,
        ctx.scenario_horizon_years, ctx.period_days,
        COALESCE(t.candidate_networks, 0) AS candidate_networks,
        COALESCE(t.reported_supply_networks, 0) AS reported_supply_networks,
        t.reported_supply_m3_year, t.reported_supply_m3_year / ctx.period_days AS reported_supply_m3_day,
        COALESCE(t.supply_population_networks, 0) AS supply_population_networks,
        t.supply_population_supply_m3_year, t.supply_population_served_people,
        1000.0 * t.supply_population_supply_m3_year / ctx.period_days
            / NULLIF(t.supply_population_served_people, 0) AS supply_l_person_day,
        100.0 * t.supply_population_networks / NULLIF(t.candidate_networks, 0) AS supply_population_network_coverage_pct,
        100.0 * t.supply_population_supply_m3_year / NULLIF(t.reported_supply_m3_year, 0) AS supply_population_supply_coverage_pct,
        COALESCE(t.missing_or_invalid_supply_networks, 0) AS missing_or_invalid_supply_networks,
        COALESCE(t.missing_or_invalid_loss_networks, 0) AS missing_or_invalid_loss_networks,
        COALESCE(t.loss_above_supply_networks, 0) AS loss_above_supply_networks,
        c.paired_loss_pct, c.paired_networks, c.paired_supply_coverage_pct,
        lists.loss_cohorts,
        CASE WHEN g.cagr IS NOT NULL THEN POWER(1 + g.cagr, ctx.scenario_horizon_years) END AS growth_factor
    FROM growth g CROSS JOIN build_context ctx
    LEFT JOIN totals t USING (region)
    LEFT JOIN cohort_rates c ON c.region = g.region AND c.boundary = 'No'
    LEFT JOIN cohort_lists lists ON lists.region = g.region
)
SELECT * EXCLUDE (growth_factor),
    100.0 * (growth_factor - 1) AS scenario_growth_pct,
    population_base * supply_l_person_day / 1000 AS scenario_base_supply_m3_day,
    population_base * supply_l_person_day / 1000 * growth_factor AS scenario_projected_supply_m3_day
FROM measures ORDER BY region;
