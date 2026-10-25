# Temporary public release — 2026-10-26

The author asked to restore the public website to the version shown in their
portfolio while the new design and research remain in development. The URL stays
`https://lucialxh.github.io/nz-data-dashboard/`.

## What is being published

The public payload is the last successful schema-v1 artifact before the audited
release: [run 40053730463](https://github.com/LuciaLXH/nz-data-dashboard/actions/runs/40053730463),
source commit `19669bc653bb007a64958b88f683f55beb40407d`, built 24 October 2026.
Its index, JavaScript and stylesheet were byte-compared with that commit.
It has the portfolio's “Demand & efficiency” bubble chart and demand/leakage chart.
The supplied portfolio screenshot says 12 October: this restores the same code,
not that exact day's build timestamp or a claim that every historical value matches.

The downloaded artifact is preserved, compressed without changing its contained
files, under `releases/legacy-19669bc/site.tar.gz`. The adjacent manifest records
its original run, original tar checksum, compressed checksum and asset hashes.
It contains the previously public static site and datasets, no credentials or raw
API caches. Original source attribution remains in the site and repository.

`prepare_public_release.py` verifies the archive, rejects unsafe archive entries,
checks schema-v1 inputs, and adds a visible historical-demo note. Dataset bytes
are unchanged. `release.json` exposes publication provenance at the public URL.
The old methodology and conclusions are not reinstated as verified findings;
the audited definitions and their limitations remain in the repository.

## Separation from development

`main` retains the audited pipeline from `533b527`; this is a publication change,
not a reset or deletion of analytical work. The bilingual preview and climate
feasibility audit remain at `1c08f5b` on `frontend/overview-preview`.

The refresh workflow sets `PUBLIC_SITE_MODE: legacy_snapshot`. Scheduled runs
republish the same archive and skip API fetching, transforms and cache writes.
Cache restores remain enabled to keep existing recovery inputs accessed during
the pause; they do not affect the frozen public payload. Independent offline CI
continues validating the current pipeline and publication tests.

## Resume the revised site

1. Integrate and review the desired preview changes. Retain paired screenshots.
2. Change `PUBLIC_SITE_MODE` in `.github/workflows/refresh.yml` to `current`.
3. Push the reviewed change to main. The normal source fetch, transform, tests,
   build and publication path runs again; no legacy context is added in this mode.
4. Verify the deployment, `/release.json`, displayed data/schema and screenshots.

Do not just redeploy an old run: the next scheduled main run would overwrite it.
Do not copy the old UI onto the schema-v2 payload: their field contracts differ.

For a local snapshot preview, from the repo root:

```sh
python scripts/prepare_public_release.py --mode legacy_snapshot --output .tmp/legacy-preview
```

The output must not already exist. This command starts no server. Port 8000 stays
closed unless explicitly started later. See [before/after evidence](changes/2026-10-26/01-restore-legacy/README.md).
