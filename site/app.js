/* NZ Water × Population — static dashboard (W2)
 * Reads only data/processed/*.json + data/ref copies under site/data/.
 * Charts: ECharts 5 · Map: Leaflet 1.9.
 * UX: left sidebar nav switches one section at a time; the landing view is
 * Title + overview. Region colours show metric values; flow colours show
 * positions in each site's historical sample, not a shortage-risk rating.
 */
"use strict";

const DATA = {
  supply: "data/supply_per_capita.json",
  growth: "data/population_growth.json",
  flowPct: "data/flow_percentile.json",
  regions: "data/regions.json",
  boundaries: "data/boundaries.geojson",
  flowSites: "data/flow_sites.json",
  consents: "data/water_consents.json",
  runs: "data/_runs.jsonl",
};

const _nf0 = new Intl.NumberFormat("en-NZ", { maximumFractionDigits: 0 });
const fmt = (n) => n == null ? "Unavailable" : _nf0.format(n);
const number1 = (n) => n == null ? "Unavailable" : fmt1.format(n);
const percent = (n) => n == null ? "Unavailable" : `${fmt1.format(n)}%`;
const fmt1 = new Intl.NumberFormat("en-NZ", { maximumFractionDigits: 1 });
const fmt3 = new Intl.NumberFormat("en-NZ", { maximumFractionDigits: 3 });
// pipeline stores UTC; the site displays Pacific/Auckland (browser is DST-aware)
const nzDateFmt = new Intl.DateTimeFormat("en-NZ", { timeZone: "Pacific/Auckland", year: "numeric", month: "short", day: "numeric" });
const nzDtFmt = new Intl.DateTimeFormat("en-NZ", { timeZone: "Pacific/Auckland", year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
const nzDate = (iso) => (iso ? nzDateFmt.format(new Date(iso)) : "—");
const nzDateTime = (iso) => (iso ? nzDtFmt.format(new Date(iso)) : "—");

const BAND = {
  low: { color: "#D55E00", label: "Below 25th percentile" },
  normal: { color: "#E69F00", label: "25th–75th percentile" },
  high: { color: "#009E73", label: "Above 75th percentile" },
  insufficient: { color: "#999999", label: "Insufficient history" },
};
// region shading ramp, light → dark
const RAMP = ["#fef0d9", "#fdd49e", "#fdbb84", "#fc8d59", "#d7301f"];
const METRICS = {
  growth: {
    label: "Five-year scenario growth", unit: "%", value: (r) => r.scenario_growth_pct,
    buckets: ["<2.5%", "2.5–4%", "4–5.5%", "5.5–7%", "≥7%"],
    idx: (v) => (v >= 7 ? 4 : v >= 5.5 ? 3 : v >= 4 ? 2 : v >= 2.5 ? 1 : 0),
  },
  percap: {
    label: "Supply per served person", unit: " L/p/d", value: (r) => r.supply_l_person_day,
    buckets: ["<300", "300–360", "360–430", "430–500", "≥500 L/p/d"],
    idx: (v) => (v >= 500 ? 4 : v >= 430 ? 3 : v >= 360 ? 2 : v >= 300 ? 1 : 0),
  },
  leak: {
    label: "Paired water loss (private losses excluded)", unit: "%", value: (r) => r.paired_loss_pct,
    buckets: ["<18%", "18–21%", "21–24%", "24–27%", "≥27%"],
    idx: (v) => (v >= 27 ? 4 : v >= 24 ? 3 : v >= 21 ? 2 : v >= 18 ? 1 : 0),
  },
};

function regionLabel(regionsList, key) {
  const r = (regionsList || []).find((x) => x.region === key);
  return r && r.display && r.display.en ? r.display.en : key;
}
function el(id) { return document.getElementById(id); }
function shortDate(iso) { return iso ? iso.slice(0, 10) : "—"; }

/* ------------------------------------------------------------------ */
/* Section switching (sidebar nav)                                     */
/* ------------------------------------------------------------------ */
const ctx = { metric: "growth", map: null, charts: [] };
const RESIZE_HOOKS = {
  "map-section": () => { if (ctx.map) setTimeout(() => ctx.map.invalidateSize(), 60); },
  "charts": () => ctx.charts.forEach((c) => c.resize()),
  "consents-section": () => ctx.charts.forEach((c) => c.resize()),
};

function showSection(name) {
  document.querySelectorAll("main section").forEach((s) => { s.hidden = s.id !== name; });
  document.querySelectorAll("#sidenav a").forEach((a) =>
    a.classList.toggle("active", a.dataset.section === name));
  const sec = document.getElementById(name);
  if (sec) sec.scrollIntoView({ behavior: "smooth", block: "start" });
  if (RESIZE_HOOKS[name]) RESIZE_HOOKS[name]();
}

function initSections() {
  document.querySelectorAll("#sidenav a[data-section]").forEach((a) => {
    a.addEventListener("click", (e) => {
      e.preventDefault();
      showSection(a.dataset.section);
    });
  });
}

/* ------------------------------------------------------------------ */
/* Data load                                                           */
/* ------------------------------------------------------------------ */
async function loadAll() {
  const j = (u) => fetch(u).then((r) => { if (!r.ok) throw new Error(u + " -> " + r.status); return r.json(); });
  const txt = (u) => fetch(u).then((r) => { if (!r.ok) throw new Error(u + " -> " + r.status); return r.text(); });
  const [supply, growth, flowPct, regions, boundaries, flowSites, consents, runsTxt] = await Promise.all([
    j(DATA.supply), j(DATA.growth), j(DATA.flowPct), j(DATA.regions),
    j(DATA.boundaries), j(DATA.flowSites), j(DATA.consents), txt(DATA.runs),
  ]);
  const runs = runsTxt.trim().split("\n").filter(Boolean).map((l) => {
    try { return JSON.parse(l); } catch (e) { return null; }
  }).filter(Boolean);
  return { supply, growth, flowPct, regions, boundaries, flowSites, consents, runs };
}

/* ------------------------------------------------------------------ */
/* Findings (landing)                                                  */
/* ------------------------------------------------------------------ */
function buildFindings() {
  return [
    {
      img: "fig1.png",
      headline: "Compare network supply.",
      num: "Six regions",
      soWhat: "Supply per served person includes household use, other uses and water losses. Differences identify questions to investigate; they do not establish achievable savings.",
      foot: "Selected NEPR 2024/25 networks · metric-specific coverage",
      target: "charts",
    },
    {
      img: "fig2.png",
      headline: "Check what water loss includes.",
      num: "Reporting scope matters",
      soWhat: "Providers estimate water loss and may use different boundaries. Reported loss is not the volume that repairs could recover. Check missing values and private-side losses before comparing networks.",
      foot: "Definitions and source review are available in Method",
      target: "method",
    },
    {
      headline: "Read each observation date.",
      num: "Selected river sites",
      soWhat: "This dashboard integrates HBRC telemetry and historical ORC records. A site's latest available reading may be old. These observations do not measure a region's drinking-water capacity.",
      foot: "River coverage is limited to the sites included in this project",
      target: "flow-section",
    },
  ];
}

function renderFindings(cards) {
  el("finding-cards").innerHTML = cards.map((c, i) => `
    <div class="card" data-target="${c.target}" tabindex="0" role="button" aria-label="Jump to evidence for finding ${i + 1}">
      ${c.img ? `<img class="card-img" src="img/${c.img}" alt="" onerror="this.style.display='none'">` : ""}
      <div class="card-body">
        <div class="headline">${c.headline}</div>
        <div class="num">${c.num}</div>
        <p class="so-what">${c.soWhat}</p>
        <div class="foot">${c.foot}</div>
      </div>
    </div>`).join("");
  document.querySelectorAll(".card[data-target]").forEach((card) => {
    const go = () => {
      showSection(card.dataset.target);
      card.classList.add("flash");
      setTimeout(() => card.classList.remove("flash"), 1600);
    };
    card.addEventListener("click", go);
    card.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); } });
  });
}

/* ------------------------------------------------------------------ */
/* Map                                                                 */
/* ------------------------------------------------------------------ */
function renderMap(d) {
  const { supply, boundaries, flowPct, flowSites, regions } = d;
  const map = L.map("map", { scrollWheelZoom: false }).setView([-42.5, 172.5], 6);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 12, attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);
  ctx.map = map;

  const supplyByRegion = {};
  supply.rows.forEach((r) => { supplyByRegion[r.region] = r; });

  const regionLayers = [];   // {layer, region, supply, bounds}
  L.geoJSON(boundaries, {
    style: () => styleRegion(null),
    onEachFeature: (f, layer) => {
      const r = supplyByRegion[f.properties.region];
      if (!r) return;
      regionLayers.push({ layer, region: f.properties.region, supply: r, bounds: layer.getBounds() });
      layer.bindPopup(regionPopup(r, regions));
      layer.on("mouseover", () => layer.setStyle({ weight: 2.5, color: "#14303e" }));
      layer.on("mouseout", () => layer.setStyle(styleRegion(r)));
    },
  }).addTo(map);

  function styleRegion(r) {
    if (!r) return { fillColor: "#e5e5e5", weight: 1.2, color: "#36544d", fillOpacity: 0.75 };
    const m = METRICS[ctx.metric];
    const c = m.value(r) == null ? "#b8c0c5" : RAMP[m.idx(m.value(r))];
    return { fillColor: c, weight: 1.2, color: "#36544d", fillOpacity: 0.75 };
  }
  function applyMetric() {
    regionLayers.forEach(({ layer, supply: r }) => layer.setStyle(styleRegion(r)));
    renderLegend(d);
    renderRegionList(d, regionLayers, map);
  }

  // region list (default side panel)
  function renderRegionList() {
    const labels = {};
    regions.regions.forEach((r) => { labels[r.region] = r.display.en; });
    const m = METRICS[ctx.metric];
    const rows = supply.rows.slice().sort((a, b) => (m.value(b) ?? -Infinity) - (m.value(a) ?? -Infinity));
    el("region-list").innerHTML = rows.map((r) => {
      const v = m.value(r);
      const c = v == null ? "#b8c0c5" : RAMP[m.idx(v)];
      return `<div class="list-row" data-region="${r.region}">
        <div class="top"><span class="name">${labels[r.region] || r.region}</span>
          <span class="badge" style="background:${c}">${v == null ? "Unavailable" : number1(v) + m.unit}</span></div>
        <div class="meta">Population ${r.population_base_year}: ${fmt(r.population_base)} · ${r.reported_supply_networks}/${r.candidate_networks} networks report supply · scenario ${r.population_base_year}–${r.projection_year}</div>
      </div>`;
    }).join("");
    el("region-list").querySelectorAll(".list-row").forEach((row) => {
      row.addEventListener("click", () => {
        const hit = regionLayers.find((x) => x.region === row.dataset.region);
        if (hit) map.fitBounds(hit.bounds, { padding: [24, 24] });
        el("region-list").querySelectorAll(".list-row").forEach((r) => r.classList.toggle("active", r === row));
      });
    });
  }

  // flow site markers (only where coordinates exist)
  const siteCoords = {};
  flowSites.sites.forEach((s) => { siteCoords[s.council + "|" + s.site] = s; });
  const markers = {};
  const staleNote = (days) => days > 365
    ? '<br><span class="stale">⚠ historical observation — check the date above</span>'
    : "";
  flowPct.rows.forEach((row) => {
    const coord = siteCoords[row.council + "|" + row.site];
    if (!coord || coord.lat == null || coord.lon == null) return;
    const radius = Math.max(5, Math.min(14, 4 * Math.sqrt(Math.max(row.latest_flow_m3s, 0.1))));
    const key = row.council + "|" + row.site;
    const marker = L.circleMarker([coord.lat, coord.lon], {
      radius, color: "#14303e", weight: 1.2,
      fillColor: BAND[row.band] ? BAND[row.band].color : "#999",
      fillOpacity: 0.85,
    }).addTo(map);
    marker.bindPopup(`
      <b>${row.site}</b> (${row.council.toUpperCase()})<br>
      ${row.latest_date} · ${row.latest_flow_m3s} m³/s<br>
      Seasonal percentile: <b>${number1(row.pctile_pct)}</b>
      (${BAND[row.band] ? BAND[row.band].label : row.band}) · ${row.n_history} days across ${row.n_history_years} prior seasons<br>
      ${row.n_qualified_years} seasons meet the history rule; seasonal day coverage ${percent(row.history_coverage_pct)}
      ${staleNote(row.stale_days)}<br>
      <span style="color:#5c6f6a;font-size:.85em">location: ${coord.precision || "n/a"} (${coord.source || "—"})</span>`);
    marker.on("click", () => highlightSiteRow(key));
    markers[key] = marker;
  });

  // flow site list (second panel)
  el("flow-site-list").innerHTML = flowPct.rows.map((row) => {
    const key = row.council + "|" + row.site;
    const c = siteCoords[key];
    const onMap = c && c.lat != null;
    const stale = row.stale_days > 365;
    return `<div class="list-row" data-key="${key}" ${onMap ? "" : 'style="opacity:.65"'}>
      <div class="top"><span class="name">${row.site}</span>
        <span class="badge ${row.band}">${BAND[row.band] ? BAND[row.band].label : row.band}</span></div>
      <div class="meta">${row.council.toUpperCase()} · ${row.latest_date} · ${row.latest_flow_m3s} m³/s
        · percentile ${number1(row.pctile_pct)}<br>
        ${row.n_history} days · ${row.n_history_years} prior seasons · ${row.n_qualified_years} meet the history rule
        ${stale ? '<span class="stale">(historical)</span>' : ""}
        ${onMap ? "" : " · no public coords"}</div>
    </div>`;
  }).join("");

  function highlightSiteRow(key) {
    el("flow-site-list").querySelectorAll(".list-row").forEach((r) => r.classList.toggle("active", r.dataset.key === key));
    const row = el("flow-site-list").querySelector(`.list-row[data-key="${key}"]`);
    if (row) row.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }
  el("flow-site-list").querySelectorAll(".list-row").forEach((row) => {
    row.addEventListener("click", () => {
      const m = markers[row.dataset.key];
      if (m) {
        map.flyTo(m.getLatLng(), 9, { duration: 0.6 });
        setTimeout(() => m.openPopup(), 650);
      }
      highlightSiteRow(row.dataset.key);
    });
  });

  // side panel toggle: regions | flow sites
  document.querySelectorAll("#panel-toggle button").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("#panel-toggle button").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const showSites = btn.dataset.panel === "sites";
      el("region-list").hidden = showSites;
      el("flow-site-list").hidden = !showSites;
    });
  });

  ctx.applyMetric = applyMetric;
  applyMetric();
}

function regionPopup(r, regions) {
  return `<b>${regionLabel(regions.regions, r.region)}</b><br>
    Population (${r.population_base_year}): ${fmt(r.population_base)}<br>
    Reported supply (2024/25): ${fmt(r.reported_supply_m3_year)} m³/year · ${r.reported_supply_networks}/${r.candidate_networks} candidate networks<br>
    Supply: ${number1(r.supply_l_person_day)} L/served person/day · ${r.supply_population_networks} matched networks<br>
    Paired water loss, private losses excluded: ${percent(r.paired_loss_pct)}<br>
    Loss coverage: ${r.paired_networks}/${r.candidate_networks} networks · ${percent(r.paired_supply_coverage_pct)} of reported supply<br>
    <em>Operator grouping is approximate. Network inputs can include transfers; losses are not recoverable savings.</em>`;
}

function renderLegend(d) {
  const m = METRICS[ctx.metric];
  const rampHtml = RAMP.map((c, i) =>
    `<span class="swatch" style="background:${c}"></span>${m.buckets[i]}`).join(" ");
  el("map-legend").innerHTML =
    `<span><b>Region shading = ${m.label}:</b></span> ${rampHtml} <span class="swatch" style="background:#b8c0c5"></span>Unavailable` +
    `&nbsp;&nbsp;|&nbsp;&nbsp;<span><b>Flow sites (seasonal percentile):</b></span>` +
    Object.values(BAND).map((b) => `<span class="dot" style="background:${b.color}"></span>${b.label}`).join(" ");
}

/* ------------------------------------------------------------------ */
/* Consents (LAWA water usage)                                         */
/* ------------------------------------------------------------------ */
const CONSENT_ORDER = ["Irrigation", "Drinking", "Industrial", "Stock", "Other"];
const CONSENT_COLORS = { Irrigation: "#D55E00", Drinking: "#0072B2", Industrial: "#E69F00", Stock: "#009E73", Other: "#999999" };

function renderConsents(consents, regions) {
  const hasData = (r) => r.activities && CONSENT_ORDER.some((c) => (r.activities[c] && r.activities[c].share_pct) > 0);
  const rows = consents.regions.filter(hasData)
    .sort((a, b) => (b.activities.Irrigation.share_pct || 0) - (a.activities.Irrigation.share_pct || 0));
  const names = rows.map((r) => r.display);
  const chart = echarts.init(el("chart-consents"));
  ctx.charts.push(chart);
  const series = CONSENT_ORDER.map((cat) => ({
    name: cat,
    type: "bar",
    stack: "c",
    barWidth: 26,
    itemStyle: { color: CONSENT_COLORS[cat] },
    emphasis: { focus: "series" },
    data: rows.map((r) => r.activities[cat] ? r.activities[cat].share_pct : 0),
    label: cat === "Irrigation"
      ? { show: true, position: "insideRight", formatter: (p) => (p.value >= 5 ? p.value + "%" : ""), color: "#fff", fontSize: 10 }
      : { show: false },
  }));
  chart.setOption({
    tooltip: {
      trigger: "axis", axisPointer: { type: "shadow" },
      formatter: (ps) => {
        const r = rows[ps[0].dataIndex];
        const lines = ps.map((p) => {
          const act = r.activities[p.seriesName];
          const vol = act && act.volume ? act.volume : "";
          const cons = act && act.consents ? act.consents : "";
          return `${p.marker}${p.seriesName}: <b>${p.value}%</b>${cons ? ` · ${cons} consents` : ""}${vol ? ` · ${vol}` : ""}`;
        }).join("<br>");
        return `<b>${r.display}</b><br>${lines}`;
      },
    },
    grid: { left: 90, right: 30, top: 10, bottom: 30 },
    xAxis: { type: "value", max: 100, axisLabel: { formatter: "{value}%" }, name: "share of consented volume" },
    yAxis: { type: "category", data: names },
    legend: { bottom: 0, textStyle: { fontSize: 11 } },
    series,
  });

  // Otago note + per-region LAWA links
  const noData = consents.regions.filter((r) => !hasData(r));
  const links = consents.regions.map((r) =>
    `<a href="${r.lawa_url}" target="_blank" rel="noopener">${r.display}</a>`).join(" · ");
  const note = noData.length
    ? `<p class="caption">${noData.map((r) => r.display).join(", ")}: no consent breakdown is included in this project's snapshot.</p>`
    : "";
  el("consents-section").insertAdjacentHTML("beforeend",
    note + `<p class="caption">View the source on LAWA (Water consents: How is water used?): ${links}</p>`);
}

/* ------------------------------------------------------------------ */
/* Charts                                                              */
/* ------------------------------------------------------------------ */
function renderBubbleChart(supply, regions) {
  const chart = echarts.init(el("chart-bubble"));
  ctx.charts.push(chart);
  const data = supply.rows.filter((r) => r.cagr5_pct != null && r.supply_l_person_day != null).map((r) => ({
    value: [r.cagr5_pct, r.supply_l_person_day, r.reported_supply_m3_day],
    name: regionLabel(regions.regions, r.region), record: r,
  }));
  chart.setOption({
    tooltip: {
      confine: true,
      formatter: (p) => {
        const r = p.data.record;
        return `<b>${p.data.name}</b><br>Population CAGR (${r.cagr_start_year}–${r.cagr_end_year}): ${percent(r.cagr5_pct)}` +
          `<br>Supply: ${number1(r.supply_l_person_day)} L/served person/day` +
          `<br>Matched population/supply: ${r.supply_population_networks}/${r.candidate_networks} networks` +
          `<br>Supply coverage: ${percent(r.supply_population_supply_coverage_pct)}` +
          `<br>Reported supply: ${fmt(r.reported_supply_m3_day)} m³/day`;
      },
    },
    grid: { left: 64, right: 30, top: 24, bottom: 65 },
    xAxis: { name: "Population CAGR (%)", nameLocation: "middle", nameGap: 30, type: "value" },
    yAxis: { name: "Supply (L / served person / day)", nameLocation: "middle", nameGap: 44, type: "value" },
    series: [{
      type: "scatter", data, itemStyle: { color: "#0072B2", opacity: 0.75 },
      symbolSize: (v) => Math.max(12, Math.min(60, Math.sqrt(v[2] || 0) / 12)),
      label: { show: true, formatter: (p) => p.data.name, position: "top", fontSize: 10, color: "#14303e" },
      labelLayout: { hideOverlap: true }, emphasis: { focus: "series" },
    }],
  });
}

function renderDemandChart(supply, regions) {
  const chart = echarts.init(el("chart-demand"));
  ctx.charts.push(chart);
  const rows = supply.rows.slice().sort((a,b) => (b.reported_supply_m3_day ?? -1) - (a.reported_supply_m3_day ?? -1));
  chart.setOption({
    tooltip: { trigger: "axis", confine: true, formatter: (ps) => {
      const r=rows[ps[0].dataIndex];
      return `<b>${regionLabel(regions.regions,r.region)}</b><br>${fmt(r.reported_supply_m3_day)} m³/day` +
        `<br>${fmt(r.reported_supply_m3_year)} m³ in 2024/25<br>${r.reported_supply_networks}/${r.candidate_networks} candidate networks report supply`;
    } },
    grid: { left: 70, right: 24, top: 38, bottom: 68 },
    xAxis: { type: "category", data: rows.map((r) => regionLabel(regions.regions,r.region)), axisLabel: { fontSize: 10, interval: 0, rotate: 30 } },
    yAxis: { type: "value", name: "Reported supply m³/day", nameTextStyle: { fontSize: 10 } },
    series: [{ name: "Reported network inputs", type: "bar", data: rows.map((r) => r.reported_supply_m3_day), itemStyle: { color: "#3182bd" } }],
  });
}

function renderWaterTables(supply, regions) {
  const label = (r) => regionLabel(regions.regions,r.region);
  const boundaries = {No: "Excluded", Yes: "Included", unknown: "Unknown"};
  el("supply-table").innerHTML = `<thead><tr><th>Operator region</th><th>Reported supply (m³/year)</th><th>Supply networks / candidates</th><th>Supply per served person (L/day)</th><th>Matched supply + population networks</th><th>Matched share of reported supply</th></tr></thead><tbody>` +
    supply.rows.map((r) => `<tr><td>${label(r)}</td><td>${fmt(r.reported_supply_m3_year)}</td><td>${r.reported_supply_networks} / ${r.candidate_networks}</td><td>${number1(r.supply_l_person_day)}</td><td>${r.supply_population_networks} / ${r.candidate_networks}</td><td>${percent(r.supply_population_supply_coverage_pct)}</td></tr>`).join("") + `</tbody>`;
  function losses() {
    const boundary=el("loss-boundary").value;
    el("loss-table").innerHTML = `<thead><tr><th>Operator region</th><th>Private loss</th><th>Reported loss (m³/year)</th><th>Networks reporting loss</th><th>Paired loss / supply (m³/year)</th><th>Paired loss rate</th><th>Paired networks / all candidates</th><th>Paired share of reported supply</th></tr></thead><tbody>` +
      supply.rows.map((r) => {
        const c=r.loss_cohorts.find((v) => v.boundary===boundary);
        return `<tr><td>${label(r)}</td><td>${boundaries[boundary]}</td><td>${fmt(c.reported_loss_m3_year)}</td><td>${c.reported_loss_networks} / ${c.boundary_candidate_networks} in this boundary</td><td>${fmt(c.paired_loss_m3_year)} / ${fmt(c.paired_supply_m3_year)}</td><td>${percent(c.paired_loss_pct)}</td><td>${c.paired_networks} / ${r.candidate_networks}</td><td>${percent(c.paired_supply_coverage_pct)}</td></tr>`;
      }).join("") + `</tbody>`;
  }
  el("loss-boundary").addEventListener("change",losses); losses();
  el("scenario-table").innerHTML = `<thead><tr><th>Region</th><th>Population base</th><th>Historical CAGR years</th><th>Base scenario (m³/day)</th><th>Target year</th><th>Future scenario (m³/day)</th><th>Scenario growth</th></tr></thead><tbody>` +
    supply.rows.map((r) => `<tr><td>${label(r)}</td><td>${r.population_base_year}: ${fmt(r.population_base)}</td><td>${r.cagr_start_year}–${r.cagr_end_year}</td><td>${fmt(r.scenario_base_supply_m3_day)}</td><td>${r.projection_year}</td><td>${fmt(r.scenario_projected_supply_m3_day)}</td><td>${percent(r.scenario_growth_pct)}</td></tr>`).join("") + `</tbody>`;
  el("water-period").textContent = `Water reporting period: ${supply.period_start} to ${supply.period_end} (${supply.period_days} days); released ${supply.source_release}.`;
}

/* ------------------------------------------------------------------ */
/* Tables & health                                                     */
/* ------------------------------------------------------------------ */
function renderFlowTable(flowPct, flowSites) {
  const policy = flowPct.policy;
  const expected = policy.window_radius_days * 2 + 1;
  const ranked = flowPct.rows.filter((r) => r.history_status === "sufficient").length;
  el("flow-history-summary").textContent = `${ranked} of ${flowPct.rows.length} sites meet the history rule. ` +
    `A percentile is shown only with at least ${policy.min_history_years} prior seasons, each with at least ${policy.min_days_per_year} of ${expected} daily observations. ` +
    `Other sites retain their latest flow but have no rank. This is a project display rule, not a hydrological standard.`;
  const coord = {};
  flowSites.sites.forEach((s) => { coord[s.council + "|" + s.site] = s; });
  const rows = flowPct.rows.map((r) => {
    const c = coord[r.council + "|" + r.site];
    const hasMarker = c && c.lat != null;
    const years = r.history_years.map((y) =>
      `<li>${y.season_year}: ${y.observed_days}/${y.expected_days} days${y.qualifies ? " · meets rule" : " · below rule"}</li>`).join("");
    const coverage = r.n_history_seasons ? `<details class="history-detail"><summary>${percent(r.history_coverage_pct)} · view years</summary>
      <p>${r.n_history}/${r.expected_history_days} possible daily slots. Seasons are named by their centre year.</p>
      <ul>${years}</ul></details>` : "No prior seasonal window";
    return `<tr>
      <td><strong>${r.site}</strong><br>${r.council.toUpperCase()}</td>
      <td>${r.latest_date}${r.stale_days > 365 ? '<br><span class="stale">Historical observation</span>' : ""}</td>
      <td>${fmt3.format(r.latest_flow_m3s)}</td>
      <td>${number1(r.pctile_pct)}<br><span class="badge ${r.band}">${BAND[r.band].label}</span></td>
      <td>${r.n_history} days · ${r.n_history_years} seasons<br>${r.n_qualified_years} seasons meet rule</td>
      <td>${coverage}</td>
      <td>${hasMarker ? "✓" : "—"}</td>
    </tr>`;
  }).join("");
  el("flow-table").innerHTML = `<thead><tr>
      <th>Site / council</th><th>Latest observation</th><th>Flow (m³/s)</th>
      <th>Seasonal percentile</th><th>Prior history</th><th>Seasonal day coverage</th><th>On map</th>
    </tr></thead><tbody>${rows}</tbody>`;
}

function renderHealth(d) {
  const { runs } = d;
  const last = runs[runs.length - 1] || {};
  const rows = last.rows || {};
  const nulls = last.null_pct || {};
  const lastUtc = last.utc ? new Date(last.utc) : null;
  const paused = d.supply.input_mode !== "offline_example" && (!lastUtc || (Date.now() - lastUtc.getTime()) > 31 * 86400e3);

  const parts = [];
  if (paused) parts.push(`<span class="paused"><b>⚠ pipeline paused</b> — showing last good snapshot</span>`);
  // A council whose live server was unreachable this run (fetch recorded in
  // _status.json) — the site shows its last good snapshot, flagged degraded.
  const degraded = (last.flow_degraded_councils || []).filter(Boolean);
  if (degraded.length) parts.push(
    `<span class="paused"><b>⚠ degraded</b> — ${degraded.map((c) => c.toUpperCase()).join(", ")} flow from last good snapshot</span>`);
  if (last.population_ok === false) parts.push(
    `<span class="paused"><b>⚠ degraded</b> — population from last good snapshot</span>`);
  if (last.flow_excluded_observations) parts.push(`<span><b>Flow quality</b> ${last.flow_excluded_observations} invalid observations excluded from percentiles; raw values retained</span>`);
  if (last.utc) parts.push(
    `<span><b>Last run</b> ${nzDateTime(last.utc)} NZ · ${last.checks_passed}/${last.checks_total} checks · schema v${last.schema_version || 1}</span>`);
  if (rows.supply_per_capita_rows != null) parts.push(
    `<span><b>Rows</b> supply ${rows.supply_per_capita_rows} · growth ${rows.population_growth_rows} · flow sites ${rows.flow_percentile_rows} · pop ${rows.population_region_years}</span>`);
  const sn = nulls.supply_per_capita, fn = nulls.flow_percentile;
  if (sn && sn.supply_l_person_day != null && fn && fn.pctile_pct != null) parts.push(
    `<span><b>Null rates</b> supply ${sn.supply_l_person_day}% · flow ${fn.pctile_pct}%</span>`);
  const last20 = runs.slice(-20);
  parts.push(`<span class="run-bars" title="Last ${last20.length} validation runs">` +
    last20.map((r) => {
      const cls = r.checks_passed === r.checks_total
        ? ((r.flow_degraded_councils || []).length || r.population_ok === false ? "degraded" : "ok")
        : r.checks_passed > 0 ? "degraded" : "fail";
      return `<span class="bar ${cls}" title="${(r.utc || "").slice(0, 16)} · ${r.checks_passed}/${r.checks_total}"></span>`;
    }).join("") + `<span class="bars-label">last ${last20.length} runs</span></span>`);
  el("health-strip").innerHTML = parts.join("");
}

function setAsOf(d) {
  el("asof-findings").textContent = `NEPR 2024/25 · built ${nzDate(d.supply.processed_utc)}`;
  el("asof-map").textContent = `Built: supply ${nzDate(d.supply.processed_utc)} · flow ${nzDate(d.flowPct.processed_utc)}`;
  el("asof-consents").textContent = `Accessed ${nzDate(d.consents.compiled_utc)}`;
  el("asof-charts").textContent = `NEPR ${d.supply.source_period} · built ${nzDate(d.supply.processed_utc)}`;
  el("asof-flow").textContent = `Processed ${nzDate(d.flowPct.processed_utc)} · observation dates below`;
}

/* ------------------------------------------------------------------ */
/* Boot                                                                */
/* ------------------------------------------------------------------ */
window.addEventListener("DOMContentLoaded", async () => {
  try {
    const d = await loadAll();
    if (d.flowPct.schema_version !== 2) throw new Error("Flow data need a rebuild for seasonal history v2");
    if (d.supply.schema_version !== 2) throw new Error("Water data need a rebuild for schema v2");
    window.__metric = ctx.metric;

    initSections();
    renderFindings(buildFindings());
    renderMap(d);
    renderConsents(d.consents, d.regions);
    renderBubbleChart(d.supply, d.regions);
    renderDemandChart(d.supply, d.regions);
    renderWaterTables(d.supply, d.regions);
    if (d.supply.input_mode === "offline_example") {
      el("example-note").hidden = false;
    }
    renderFlowTable(d.flowPct, d.flowSites);
    renderHealth(d);
    setAsOf(d);

    // choropleth metric toggle
    document.querySelectorAll("#metric-buttons button").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll("#metric-buttons button").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        ctx.metric = btn.dataset.metric;
        window.__metric = ctx.metric;
        ctx.applyMetric();
      });
    });
  } catch (e) {
    const msg = `Failed to load data: ${e.message}.<br>` +
      `Run <code>make site</code> first (copies data/processed + data/ref into site/data/), then serve <code>site/</code>.`;
    document.querySelector("main").insertAdjacentHTML("afterbegin",
      `<section style="background:#fdecea;border:1px solid #e0b4b4;border-radius:10px;padding:1rem">${msg}</section>`);
    console.error(e);
  }
});
