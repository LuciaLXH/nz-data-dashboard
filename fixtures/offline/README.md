# Attributed offline examples

These are **small public-source excerpts**, not representative water totals for
six regions. No values have been invented or corrected. `MANIFEST.json` records
original files, SHA-256 hashes, URLs, licences, selection rules, and the mapping
from this CSV's record numbers back to the original extract (header = record 1).
Population retains all 48 POP observations; water retains 41 source records;
flow retains 15 observations at two sites. Synthetic edge cases live only in tests.

After installing `requirements.txt`, run `make offline` and `make serve-offline`.
The real normalization, SQL, schemas, reconciliation and site packaging run
without API keys, source fetches, raw caches or production outputs. Output goes
to `.tmp/offline/`; the browser displays an example banner. The fixed calculation
date is in the manifest. Validation logs record the actual test run time.

The browser's chart libraries, map tiles and outbound source links still require
internet access. “Offline” here describes the data build and tests. A production
snapshot is built separately with `make data` and packaged with `make site-data`.

When changing an excerpt, retain exact source values, update its selection and
record mapping, and update file hashes. Do not label sample totals as findings.
