# Analysis & Findings

> **Status: W0 scaffold** — outlines only. Numbers arrive in W2 once the
> data pipeline is live.

## The three findings (finalise in W2)

Each finding = **one number + one chart + one "so what"**. These land in the
README TL;DR section and on the site's Key Findings block.

### Finding 1 — [draft headline]
- **Evidence:** [number + source]
- **So what:** [what a council planner should do differently]

### Finding 2 — [draft headline]
- **Evidence:** [number + source]
- **So what:** [decision implication]

### Finding 3 — [draft headline]
- **Evidence:** [number + source]
- **So what:** [decision implication]

> Note: the review's example "Southland ~700 L vs Auckland ~146 L per capita
> per day" is **illustrative only** — verify against the actual Water NZ NPR
> snapshot before using any number.

---

## Section B — Can population growth explain regional water quality?

**Claim to test:** population growth does **not** explain NZ river water
quality once land use is accounted for.

- **Approach:** partial correlation / stratification — correlate population
  growth vs LAWA water-quality metrics, then control for land use (dairy
  intensity, irrigation area per council).
- **Method note:** this mirrors the analytical approach used in my PHF
  Science internship (flood-disturbance effects on water quality). **Method
  reused; data entirely from public LAWA snapshots. No PHF data or
  unpublished results appear in this repository.**
- **Expected output:** the population signal weakens or disappears after
  controlling for land use — the confounding itself becomes the finding.

## Limitations

- **Ecological fallacy** — council-level correlation says nothing about
  catchment-level mechanism.
- **n = 6** — no correlation across this few units is robust; one large
  council can flip the sign.
- **Confounding** — land use (dairy intensity, irrigation) drives NZ river
  water quality far more than urban population.
- **Site selection bias** — LAWA monitoring sites are not randomly located.
- Water NZ NPR is self-reported by councils; metering coverage varies.
