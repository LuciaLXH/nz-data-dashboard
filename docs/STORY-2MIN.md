# 2-minute spoken story (semi-technical audience)

> For planners / PMs / clients. Read aloud once against the live site before
> any conversation. ~290 words ≈ 2 min at a relaxed pace; the numbers are from
> the 2026-08-30 run. Tech is kept to one sentence — the story is the findings.

---

**(0:00 — Hook, ~20 s)**

"New Zealand's population is growing, and every council has to supply water
for the people who arrive. My question was simple: **which of six councils
will feel that pressure first** — Auckland, Waikato, Hawke's Bay, Canterbury,
Otago, Southland? So I built a dashboard that combines official population
figures with every registered water supply in those regions, and ranks the
pressure."

**(0:20 — Finding 1, ~35 s)**

"The first thing it shows: how efficiently regions use water is not
remotely the same. **Auckland serves 1.7 million people at 270 litres per
person per day. Hawke's Bay uses 610.** That's a two-and-a-bit times gap. If
Hawke's Bay simply matched Auckland's efficiency, it would free up almost
49,000 cubic metres a day — **62% of the entire six-region demand growth we
expect by 2030**. In other words: before anyone builds a new dam, there's a
demand-side lever worth one to two years of regional growth, sitting in
efficiency and metering."

**(0:55 — Finding 2, ~35 s)**

"Second: **22.5% of everything the six networks put in is lost to leaks** —
about 299,000 cubic metres a day, enough for over a million people. Look at
Canterbury: it leaks **3.5 times its own projected growth** to 2030. Its
leaks alone would swallow a decade of its demand growth. Fixing pipes buys
growth headroom that doesn't wait for population — that's a planning lever,
not a forecast."

**(1:30 — Finding 3 + honesty, ~30 s)**

"Third, and honestly the most interesting: when I went looking for river
flows — the source-water side — **only 2 of the 6 councils publish open flow
time series at all**. Where they do, late-August flows this year sat in the
driest ~10% of recent records. So the demand ranking is solid on 6 of 6
regions, but source availability is only locally observable — that's the
data gap, and the pipeline is built to say exactly that, rather than pretend
otherwise."

**(2:00 — Close, ~15 s)**

"Every number on the dashboard is traceable to a public source — Stats NZ,
NEPR, LAWA — and the whole thing re-runs automatically. **Bottom line: the
regions to watch first are Canterbury and Waikato on demand, and the 
cheapest fix isn't new supply — it's efficiency and leaks.**"

---

## If you're short on time (cut order)
1. Cut the Fernhill percentile detail in the third beat (keep "only 2 of 6
   publish flows" — that's the point).
2. Cut the "1.1 million people" figure in Finding 2 (keep the 3.5× line).

## One-sentence tech (only if asked)
"Stats NZ population API × Taumata Arowai NEPR unit-level network data, all
business logic in SQL on DuckDB, refreshed automatically, static site on
GitHub Pages."
