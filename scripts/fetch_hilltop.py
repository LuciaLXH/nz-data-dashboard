"""Fetch river flow time series from council Hilltop servers (no key needed).

W1 (2026-08-30) verified endpoints & behaviour:
  - HBRC  https://data.hbrc.govt.nz/Envirodata/EMAR.hts
      * live telemetry sites (e.g. Ngaruroro River at Fernhill) respond to
        GetData with Measurement=FlowM3S [Water Level] (m3/s, 15-min).
      * the public SiteList exposes HISTORIC stations only (windows ending
        1968–2000) — site discovery via SiteList is therefore useless here;
        we use a curated list of verified live sites.
  - ORC   http://gisdata.orc.govt.nz/hilltop/Global.hts
      * public server serves 2010-12-29 → 2021-04-23 only (no realtime).
        GetData with Measurement=Flow [Water Level] returns cumecs (m3/s).
  - ECan/Southland/Auckland ArcGIS REST expose site metadata only (no public
    time series); Waikato endpoints down — recorded as TBD, see
    docs/W1-data-sources.md. LAWA's internal Umbraco API
    (/umbraco/api/waterquantityservice/flowstats?pageId=…) is a candidate for
    uniform 6-council coverage (W1.5 follow-up), not a stable public contract.

Encoding note: these servers reject ``+``-encoded spaces ("No Measurements
available") — all query params are encoded with %20 (quote).

Output (data/raw/flow/<council>/):
  - <YYYYMMDD>.json — {council, fetched_utc, source, sites:[{site, measurement,
    units, window, series:[[YYYY-MM-DD, daily_mean], ...]}]}
  - _status.json    — per-council run status (ok, sites_fetched, n_points, errors)

The script never hard-fails on a single site/council: failures are recorded in
_status.json so `make data` runs from scratch with graceful degradation.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from statistics import mean
from typing import Iterable

import requests

UTC = timezone.utc

REQUEST_TIMEOUT = 60  # seconds
SLEEP_BETWEEN_REQUESTS = 0.35
MAX_ATTEMPTS = 3

# Verified live/historical flow sites per council.
# (site, request_as measurement, units, window_kind)
#   window_kind "recent"     → last --days days        (HBRC live telemetry)
#   window_kind "historical" → 2010-12-29..2021-04-23  (ORC public server)
CURATED_SITES: dict[str, list[tuple[str, str, str, str]]] = {
    "hbrc": [
        ("Ngaruroro River at Fernhill", "FlowM3S [Water Level]", "m3/s", "recent"),
        ("Tukituki River at Red Bridge", "FlowM3S [Water Level]", "m3/s", "recent"),
        ("Mohaka River at Raupunga", "FlowM3S [Water Level]", "m3/s", "recent"),
    ],
    "orc": [
        ("3 OClock Stream at Lambhill", "Flow [Water Level]", "cumecs (m3/s)", "historical"),
        ("Amisfield Burn at Top Take u/s", "Flow [Water Level]", "cumecs (m3/s)", "historical"),
        ("Arrow at Cornwall street d/s", "Flow [Water Level]", "cumecs (m3/s)", "historical"),
        ("Bannock Burn at Cairnmuir Road 100m upstream", "Flow [Water Level]", "cumecs (m3/s)", "historical"),
        ("Benger burn at Booths", "Flow [Water Level]", "cumecs (m3/s)", "historical"),
        ("Benger burn at SH8", "Flow [Water Level]", "cumecs (m3/s)", "historical"),
        ("Boundary Creek at Top Race u/s", "Flow [Water Level]", "cumecs (m3/s)", "historical"),
        ("Branch Burn at Cardrona Valley", "Flow [Water Level]", "cumecs (m3/s)", "historical"),
    ],
}

LABELS = {
    "hbrc": "Hawke's Bay (HBRC)",
    "orc": "Otago (ORC)",
}
BASES = {
    "hbrc": "https://data.hbrc.govt.nz/Envirodata/EMAR.hts",
    "orc": "http://gisdata.orc.govt.nz/hilltop/Global.hts",
}
ORC_HISTORICAL = ("2010-12-29", "2021-04-23")


# --------------------------------------------------------------------------- #
# Hilltop protocol helpers
# --------------------------------------------------------------------------- #
def _hilltop_get(base: str, params: dict, attempts: int = MAX_ATTEMPTS) -> str:
    """GET a Hilltop request with retry + backoff. Returns response text.

    Params are %20-encoded (quote) — these servers reject "+"-encoded spaces.
    """
    url = f"{base}?{urllib.parse.urlencode(params, quote_via=urllib.parse.quote)}"
    last_err: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            r = requests.get(url, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            return r.text
        except Exception as e:  # noqa: BLE001 — network errors vary by lib version
            last_err = e
            if attempt < attempts:
                time.sleep(0.8 * (2 ** (attempt - 1)))
    raise RuntimeError(f"GET failed after {attempts} attempts: {last_err}")


def hilltop_measurement_windows(base: str, site: str) -> dict[str, list[tuple[str, str, list[str]]]]:
    """MeasurementList → {datasource: [(From, To, [measurement names]), ...]}."""
    xml = _hilltop_get(base, {"Service": "Hilltop", "Request": "MeasurementList", "Site": site})
    root = ET.fromstring(xml)
    err = root.find("Error")
    if err is not None and err.text:
        raise RuntimeError(err.text.strip())
    out: dict[str, list[tuple[str, str, list[str]]]] = {}
    for ds in root.findall("DataSource"):
        name = ds.get("Name", "")
        fr = ds.findtext("From") or ""
        to = ds.findtext("To") or ""
        meas = [m.get("Name", "") for m in ds.findall("Measurement")]
        out.setdefault(name, []).append((fr, to, meas))
    return out


def hilltop_getdata(base: str, site: str, measurement: str, from_: str, to: str) -> list[tuple[str, float]]:
    """Request=GetData → [(ISO timestamp, value), ...]. Raises on <Error>."""
    xml = _hilltop_get(base, {
        "Service": "Hilltop", "Request": "GetData", "Site": site,
        "Measurement": measurement, "From": from_, "To": to,
    })
    root = ET.fromstring(xml)
    err = root.find("Error")
    if err is not None and err.text:
        raise RuntimeError(err.text.strip())
    points: list[tuple[str, float]] = []
    for e in root.iter("E"):
        t = e.findtext("T")
        v = e.findtext("I1")
        if t and v is not None:
            try:
                points.append((t, float(v)))
            except ValueError:
                continue  # skip non-numeric values
    return points


# --------------------------------------------------------------------------- #
# Downsampling
# --------------------------------------------------------------------------- #
def daily_means(points: Iterable[tuple[str, float]]) -> list[tuple[str, float]]:
    """Aggregate sub-daily points to per-day means.

    Hilltop timestamps are local (NZT) YYYY-MM-DDTHH:MM:SS; we bucket by the
    date part. Chunks must be aligned to day boundaries (year chunks are).
    """
    buckets: dict[str, list[float]] = {}
    for ts, value in points:
        day = ts[:10]
        buckets.setdefault(day, []).append(value)
    return [(day, round(mean(vals), 4)) for day, vals in sorted(buckets.items())]


# --------------------------------------------------------------------------- #
# Fetching
# --------------------------------------------------------------------------- #
def _year_chunks(from_: str, to: str) -> list[tuple[str, str]]:
    """Split [from_, to] (YYYY-MM-DD) into year-aligned chunks."""
    f_year, t_year = int(from_[:4]), int(to[:4])
    chunks: list[tuple[str, str]] = []
    for y in range(f_year, t_year + 1):
        start = f"{y}-01-01" if y > f_year else from_
        end = f"{y}-12-31" if y < t_year else to
        chunks.append((start, end))
    return chunks


def fetch_site(base: str, site: str, measurement: str, window_kind: str,
               days: int) -> dict:
    """Fetch + daily-downsample one site. Returns site record (raises on fail)."""
    if window_kind == "historical":
        from_, to = ORC_HISTORICAL
        # respect the site's actual data window if it is narrower
        windows = hilltop_measurement_windows(base, site)
        for fr, to_srv, meas in windows.get("Water Level", []):
            if measurement.split(" [")[0] in meas and fr and to_srv:
                from_, to = fr[:10], to_srv[:10]
                break
        chunks = _year_chunks(from_, to)
    else:  # recent
        now = datetime.now(UTC)
        to = now.strftime("%Y-%m-%d")
        from_ = (now - timedelta(days=days)).strftime("%Y-%m-%d")
        chunks = _year_chunks(from_, to)

    daily: list[tuple[str, float]] = []
    for c_from, c_to in chunks:
        raw = hilltop_getdata(base, site, measurement, c_from, c_to)
        daily.extend(daily_means(raw))
        time.sleep(SLEEP_BETWEEN_REQUESTS)
    # merge duplicate days from chunk boundaries (shouldn't happen, be safe)
    merged: dict[str, float] = {}
    for day, v in daily:
        merged[day] = v
    return {
        "site": site, "measurement": measurement,
        "window": [from_, to], "series": sorted(merged.items()),
    }


def fetch_council(council: str, days: int, out_dir: str) -> dict:
    """Fetch flow for one council; returns a status dict (never raises)."""
    base, label = BASES[council], LABELS[council]
    status: dict = {
        "council": council, "label": label, "source": base,
        "ok": False, "sites_fetched": 0, "n_points": 0, "errors": {},
    }
    all_series: list[dict] = []
    for site, measurement, units, window_kind in CURATED_SITES[council]:
        try:
            rec = fetch_site(base, site, measurement, window_kind, days)
            rec["units"] = units
            all_series.append(rec)
            status["sites_fetched"] += 1
            status["n_points"] += len(rec["series"])
        except Exception as e:  # noqa: BLE001 — per-site degradation
            status["errors"][site] = str(e)[:200]
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    status["ok"] = bool(all_series)
    now = datetime.now(UTC)
    if all_series:
        stamp = now.strftime("%Y%m%d")
        path = os.path.join(out_dir, council, f"{stamp}.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "council": council, "label": label,
                "fetched_utc": now.isoformat(), "source": base,
                "measurement": "daily mean river flow",
                "sites": all_series,
            }, f, ensure_ascii=False, indent=1)
        status["file"] = os.path.relpath(path)
    return status


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--council", choices=["all", "hbrc", "orc"], default="all")
    ap.add_argument("--days", type=int, default=1825,
                    help="recent window for realtime councils (HBRC), in days; "
                         "default 5 years of daily means for the same-week percentile")
    ap.add_argument("--out", default="data/raw/flow")
    args = ap.parse_args(argv)

    councils = list(CURATED_SITES) if args.council == "all" else [args.council]
    statuses: dict[str, dict] = {}
    for council in councils:
        status = fetch_council(council, args.days, args.out)
        statuses[council] = status
        mark = "✅" if status["ok"] else "⚠️"
        print(f"{mark} {status['label']}: sites={status['sites_fetched']} "
              f"points={status['n_points']} errors={len(status['errors'])}")

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "_status.json"), "w", encoding="utf-8") as f:
        json.dump(statuses, f, ensure_ascii=False, indent=1)
    return 0 if all(s["ok"] for s in statuses.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
