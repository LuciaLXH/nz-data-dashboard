#!/usr/bin/env python3
"""Inspect downloaded climate samples; never refresh or modify dashboard data.

Standard library only. No network calls. GHCN samples are optional and kept local
pending clarification of the originating agencies' redistribution conditions.
"""
import argparse
import calendar
from collections import Counter
from datetime import date, timedelta
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def ghcn_coverage(text):
    """Conservative screening, not a WMO climatological-normal certification."""
    accepted, complete, seen = [], [], set()
    flags = Counter()
    for line in text.splitlines():
        if line[17:21] != "PRCP":
            continue
        if len(line) < 269:
            raise ValueError("Truncated GHCN record")
        year, month = int(line[11:15]), int(line[15:17])
        if (year, month) in seen:
            raise ValueError("Duplicate precipitation month")
        seen.add((year, month))
        days = calendar.monthrange(year, month)[1]
        valid = 0
        for day in range(1, days + 1):
            cell = line[21 + (day - 1) * 8:29 + (day - 1) * 8]
            value, measurement, quality = int(cell[:5]), cell[5], cell[6]
            if value != -9999:
                flags[measurement] += 1
            # A/C/E can represent less than a full day; H/I/P involve uncertain
            # or presumed amounts. Trace T is accepted as the supplied zero.
            if value >= 0 and quality == " " and measurement not in "ACEHIP":
                accepted.append(date(year, month, day).isoformat())
                valid += 1
        if valid == days:
            complete.append((year, month))
    baseline = [sum(1991 <= y <= 2020 and m == month for y, m in complete)
                for month in range(1, 13)]
    return {
        "first_accepted_day": min(accepted) if accepted else None,
        "last_accepted_day": max(accepted) if accepted else None,
        "accepted_days": len(accepted),
        "measurement_flags_on_nonmissing_days": dict(sorted(flags.items())),
        "complete_baseline_months_jan_to_dec": baseline,
        "passes_proposed_25_of_30_years_each_month": min(baseline) >= 25,
        "complete_months_2023_2024": sum(y in (2023, 2024) for y, m in complete),
    }


def era5_coverage(points):
    output = []
    first, last = date(1991, 1, 1), date(2025, 12, 31)
    expected = [(first + timedelta(days=i)).isoformat()
                for i in range((last - first).days + 1)]
    for point in points:
        daily = point["daily"]
        times, values = daily["time"], daily["precipitation_sum"]
        if times != expected or len(values) != len(expected):
            raise ValueError("ERA5 dates missing, duplicated, unordered or outside requested window")
        if point["daily_units"]["precipitation_sum"] != "mm":
            raise ValueError("Unexpected precipitation unit")
        if any(v is not None and v < 0 for v in values):
            raise ValueError("Negative precipitation")
        output.append({
            "returned_latitude": point["latitude"],
            "returned_longitude": point["longitude"],
            "timezone": point["timezone"],
            "first_day": times[0], "last_day": times[-1],
            "days": len(times), "missing_values": sum(v is None for v in values),
        })
    return output


def audit(root, flow_root=None, ghcn_dir=None):
    roni = [line.split() for line in (root / "roni.txt").read_text().splitlines()[1:]
            if line.strip()]
    if not roni:
        raise ValueError("Empty RONI file")
    for season, year, value in roni:
        int(year)
        float(value)
    metadata = ET.parse(root / "hbrc-rain-metadata-encoded.xml").getroot()
    rain = next(x for x in metadata.findall("DataSource") if x.get("Name") == "Rainfall")
    sample = ET.parse(root / "hbrc-rain-dec2023.xml").getroot()
    events = sample.findall(".//Data/E")
    quality = ET.parse(root / "hbrc-rain-quality.xml").getroot()
    result = {
        "scope": "Feasibility only; no ENSO effect estimate or dashboard update",
        "roni": {"rows": len(roni), "first_season": roni[0][:2], "last_season": roni[-1][:2]},
        "era5": era5_coverage(json.loads((root / "era5-two-points.json").read_text())),
        "hbrc": {
            "site": rain.get("Site"), "metadata_from": rain.findtext("From"),
            "metadata_to": rain.findtext("To"), "sample_entries": len(events),
            "sample_first_timestamp": events[0].findtext("T") if events else None,
            "sample_last_timestamp": events[-1].findtext("T") if events else None,
            "quality_entries": len(quality.findall(".//Data/E")),
            "status": "Raw sample only; daily interval convention and quality unresolved",
        },
    }
    if ghcn_dir is not None:
        files = sorted(ghcn_dir.glob("*.dly"))
        if not files:
            raise ValueError("No GHCN samples found")
        result["ghcn"] = {p.stem: ghcn_coverage(p.read_text()) for p in files}
    if flow_root is not None:
        result["existing_flow"] = []
        for council in ("hbrc", "orc"):
            path = flow_root / council / "20260830.json"
            data = json.loads(path.read_text())
            for site in data["sites"]:
                dates = [row[0] for row in site["series"] if row[1] is not None]
                result["existing_flow"].append({
                    "council": council, "site": site["site"], "days": len(dates),
                    "first_day": min(dates), "last_day": max(dates),
                    "source_file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                })
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--ghcn-dir", type=Path)
    parser.add_argument("--flow-root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(audit(args.input_dir, args.flow_root, args.ghcn_dir), indent=2) + "\n"
    if args.output:
        with args.output.open("x") as stream:
            stream.write(result)
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
