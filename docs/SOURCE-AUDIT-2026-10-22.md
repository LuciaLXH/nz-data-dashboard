# NEPR source audit and handling decisions

Date: 2026-10-22. This is the **stage-one historical diagnostic** and its handling
decisions. At that point, production transformation and SQL had not adopted them.
The subsequent local v2 implementation now applies these rules; see the
[data dictionary](DATA-DICTIONARY.md) and [change record](CHANGELOG.zh-CN.md).
The diagnostic JSON remains unchanged so the original audit can be reproduced.
Descriptions of the “existing” loader below refer to the loader at audit time.

## Evidence and reproduction

The audit uses the repository's pinned 2024/25 NEPR extract, released 2026-07-27,
its data dictionary, organization file and current `ORG_REGION` mapping. The
[diagnostic JSON](audits/nepr-2026-10-22.json) contains source SHA-256 hashes,
record identifiers, differences, missingness, mapping inventory and transfers.
CSV record numbers count the header as record 1, not physical text lines.

```bash
python3 scripts/audit_nepr.py
# Reproduce the saved report explicitly:
python3 scripts/audit_nepr.py --output docs/audits/nepr-2026-10-22.json
```

This command uses only Python's standard library, makes no API calls and does not
write pipeline inputs or outputs. It is an audit, not the planned offline dashboard
build. Counts below describe this pinned snapshot, not current national coverage.

## Identity and repeated records

The file contains 1,126 source records, including 567 empty template records.
The current organization map selects 272 records across 34 organizations.
Applying the review decisions would leave 268 candidate records before metric
validity and boundary checks.

| Case | Source evidence | Decision for the next transformation |
|---|---|---|
| OTO001 | CSV records 318 and 319, Otorohanga District Council, names Waipa and Otorohanga; population, supply, water loss and other reviewed fields differ | Quarantine both rows from comparable aggregates until the provider or a corrected extract resolves identity. Preserve both raw records. Do not take maxima, add them, choose a name or invent a replacement ID. |
| RIV001 | CSV records 406 and 407, Riverton; reviewed water measures, identity, quality and private-loss boundary agree. Abstraction count/source type differ | Count the repeated water measures once, retaining both source references. This is equivalence for the reviewed measures, not proof the entire source rows are duplicates. Do not deduplicate an abstraction analysis using this rule. |
| Albury | CSV record 152, Mackenzie District Council, service population 240 and estimated annual loss 61,320 m³; Supply ID and supply volume absent | Quarantine from keyed network aggregates pending identity confirmation. Retain the missing-ID reason and reported loss in the audit; do not fill its ID or supply volume from another row. |
| Empty template rows | Every field blank | Exclude as empty records; do not count as non-reporting networks. |

The existing `groupby("supply_id").max()` mixes values from the OTO001 rows. For
example, it pairs Otorohanga's annual supply of 477,689 m³ with Waipa's loss of
137,788 m³. Pandas also drops Albury's missing ID without a visible exclusion
record. These are confirmed transformation defects, not repaired by this audit.

Candidate identity is release + Account ID + Supply ID, with consistent name and
organization required. Account ID must identify the same organization within a
release. Unexpected ID/name conflicts, missing IDs and changes across releases
require explicit review; neither source ordering nor a maximum is a resolution.

## Completeness and water-loss boundaries

These counts use the **268 audit candidates**, after the identity decisions above.
They are diagnostics, not a replacement for the current published totals.

| Operator region grouping | Candidates | Missing supply | Missing loss | Valid supply/loss pairs¹ | Pairs excluding private-side loss² |
|---|---:|---:|---:|---:|---:|
| Auckland | 25 | 3 | 15 | 10 | 10 |
| Canterbury | 97 | 5 | 15 | 77 | 63 |
| Hawke's Bay | 19 | 0 | 6 | 12 | 10 |
| Otago | 45 | 1 | 6 | 37 | 19 |
| Southland | 15 | 0 | 0 | 14 | 0 |
| Waikato | 67 | 1 | 2 | 65 | 35 |
| Total | 268 | 10 | 44 | 215 | 137 |

¹ Positive supply, non-negative loss, loss no greater than supply; boundaries may
still differ. Zero supply is not a usable rate denominator even if reported.
² The same validity checks plus `Includes private water loss? = No`.

Of the candidates, 145 say No, 85 say Yes, and 38 have no private-loss answer.
All 15 Southland candidates say Yes. Consequently, a comparable public-side rate
for Southland would be **unavailable**, not zero. Publish the Yes/unknown cohorts
separately and explain the difference; do not subtract an assumed private loss.

Two Otago records (327 and 331) report loss greater than supply. Exclude them
from comparable rates pending source review; retain their original values and
the exclusion reason. Three non-residential connection values are invalid under
the non-negative rule. The JSON retains these diagnostic counts. A populated
cell alone does not make a metric usable.

Report supply and loss totals with their own coverage. Calculate a loss rate only
over the same valid records and boundary group on both sides of the division.
Missing loss cannot become zero; adding supply from a loss-missing network would
otherwise dilute the rate.

## Geographic assignment and scope

The JSON lists all 34 organization mappings and every unmapped organization.
Mapped operators are grouped into Auckland, Canterbury, Hawke's Bay, Otago,
Southland and Waikato. This is a project grouping, not a verified service-area join.

[Stats NZ's 2025 territorial-authority documentation](https://datafinder.stats.govt.nz/layer/120963-territorial-authority-2025/)
explicitly notes that some districts cross region boundaries, including Taupō
across four regions. The old code comment claiming each territorial authority
belongs to exactly one region has been corrected. Taupō, Waitaki and other
boundary-crossing cases need network geography before exact allocation; this
review does not certify the remaining mappings as exact service boundaries.

Unmapped organizations include national operators such as the Ministry of
Education and New Zealand Defence Force. Their exclusion is not evidence that
they have no supplies in these six regions. Retain their exclusion inventory;
describe the scope as **selected reporting networks**, not all registered supplies.

For the next iteration, retain the existing operator grouping only as a labelled
proxy. Do not use it to claim exact regional network coverage, rank supply zones
or join river sites to a drinking-water supply without explicit linkage evidence.
Network-level geography remains unresolved; do not invent an allocation.

## Transfers and metric definitions

The organization file reports transfers, including Watercare exports of
9,685,474 m³/year and Papakura imports of 8,565,889 m³/year. These are source
values, not proof of a matched transaction between those two operators. A regional
sum of network inputs needs transfer reconciliation before it can represent
unique water supplied across a regional boundary. The audit inventories all
mapped operators' imports and exports, preserving missing separately from zero.

Keep D-EH4 supply, D-RE1 estimated water loss, CARL and residential consumption
distinct. The [data dictionary](DATA-DICTIONARY.md) records source fields, units,
valid-record rules, current calculations and next-stage definitions. ILI and
CARL regional summaries require separate denominator review and are hidden from
the dashboard's popups for now.

## What remains before releasing revised numbers

1. Apply identity quarantine and reviewed-field deduplication in the real loader;
   retain source references, missingness, boundary and confidence flags.
2. Implement paired cohorts, contribution reconciliation, explicit population
   base/target years and a schema version change; test missing/zero values and
   year gaps. Do not call the old JSON the new model.
3. Provide an attributed offline build through the same transform and validation
   path, then update chart values and narrative from validated outputs.
4. Keep unresolved identity/geography/transfer cases visible. Releasing an
   explicitly limited cohort does not require inventing missing information.

No provider contact, source correction or stakeholder validation is implied by
this review. Production deployment is separate from the local changes.

## Local verification

On 2026-10-22, `python -m pytest -q -ra` in the project virtual environment passed
35 tests with no skips, including five source-audit regressions. Re-running
`python3 scripts/audit_nepr.py` exactly reproduced the saved diagnostic
JSON. No production calculations or schema constraints changed in this patch.

Browser checks used the existing local 2026-10-10 site snapshot, not a refreshed
or deployed build. Desktop (1440 px) and mobile (390 px) navigation, map controls,
scenario labels and persistent review notice passed. Chart screenshots were
visually inspected; the mobile table stays within its scroll container. These
checks verify the wording/UI patch, not the pending metric implementation.
