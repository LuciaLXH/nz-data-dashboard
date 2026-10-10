"""A partial Hilltop outage must retain each site's last usable series."""
import importlib.util
import json
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "fetch_hilltop", Path(__file__).resolve().parents[1] / "scripts/fetch_hilltop.py"
)
hilltop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hilltop)


def setup_source(monkeypatch, tmp_path, cached=True):
    sites = [(name, "Flow", "m3/s", "recent") for name in ("A", "B")]
    monkeypatch.setitem(hilltop.CURATED_SITES, "hbrc", sites)
    monkeypatch.setattr(hilltop.time, "sleep", lambda _: None)
    if cached:
        folder = tmp_path / "hbrc"
        folder.mkdir()
        (folder / "20200101.json").write_text(json.dumps({
            "sites": [{"site": name, "measurement": "Flow", "units": "m3/s",
                       "window": ["2020-01-01", "2020-01-01"],
                       "series": [["2020-01-01", 10.0]]} for name in ("A", "B")]
        }))


def snapshot(tmp_path):
    paths = sorted((tmp_path / "hbrc").glob("[0-9]*.json"))
    return json.loads(paths[-1].read_text())


@pytest.mark.parametrize("empty", [False, True])
def test_partial_failure_keeps_old_site(monkeypatch, tmp_path, empty):
    setup_source(monkeypatch, tmp_path)
    def fetch(base, site, measurement, window_kind, days):
        if site == "B":
            if empty:
                return {"site": site, "series": []}
            raise RuntimeError("upstream unavailable")
        return {"site": site, "measurement": measurement,
                "window": ["2026-10-10", "2026-10-10"],
                "series": [["2026-10-10", 20.0]]}
    monkeypatch.setattr(hilltop, "fetch_site", fetch)
    status = hilltop.fetch_council("hbrc", 30, str(tmp_path))
    served = {s["site"]: s for s in snapshot(tmp_path)["sites"]}
    assert served["A"]["series"] == [["2026-10-10", 20.0]]
    assert served["B"]["series"] == [["2020-01-01", 10.0]]
    assert status["ok"] is False
    assert status["fallback_sites"] == ["B"]
    assert status["sites_fetched"] == 1
    assert status["sites_served"] == 2


@pytest.mark.parametrize("cached", [False, True])
def test_total_failure_exit_depends_on_cache(monkeypatch, tmp_path, cached):
    setup_source(monkeypatch, tmp_path, cached)
    def fail(*args):
        raise RuntimeError("upstream unavailable")
    monkeypatch.setattr(hilltop, "fetch_site", fail)
    code = hilltop.main(["--council", "hbrc", "--out", str(tmp_path)])
    assert code == (0 if cached else 1)
    if cached:
        assert len(snapshot(tmp_path)["sites"]) == 2


def test_success_replaces_cached_series(monkeypatch, tmp_path):
    setup_source(monkeypatch, tmp_path)
    monkeypatch.setattr(hilltop, "fetch_site", lambda base, site, measurement, kind, days: {
        "site": site, "measurement": measurement,
        "window": ["2026-10-10", "2026-10-10"], "series": [["2026-10-10", 20.0]]
    })
    status = hilltop.fetch_council("hbrc", 30, str(tmp_path))
    assert status["ok"] is True
    assert status["fallback_sites"] == []
    assert all(s["series"] == [["2026-10-10", 20.0]] for s in snapshot(tmp_path)["sites"])


def test_newer_partial_snapshot_does_not_hide_older_good_site(monkeypatch, tmp_path):
    setup_source(monkeypatch, tmp_path)
    (tmp_path / "hbrc" / "20200102.json").write_text(json.dumps({
        "sites": [{"site": "A", "series": [["2020-01-02", 12.0]]},
                  {"site": "B", "series": []}]
    }))
    def fail(*args):
        raise RuntimeError("upstream unavailable")
    monkeypatch.setattr(hilltop, "fetch_site", fail)
    hilltop.fetch_council("hbrc", 30, str(tmp_path))
    served = {s["site"]: s for s in snapshot(tmp_path)["sites"]}
    assert served["A"]["series"] == [["2020-01-02", 12.0]]
    assert served["B"]["series"] == [["2020-01-01", 10.0]]
