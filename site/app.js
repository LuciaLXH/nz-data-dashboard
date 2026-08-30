/* NZ Water × Population — static dashboard (W2)
 * Reads only data/processed/*.json + data/ref copies under site/data/.
 * Charts: ECharts 5 · Map: Leaflet 1.9.
 * UX: left sidebar nav switches one section at a time; the landing view is
 * Title + Key Findings. Colour semantics: red = pressure/warning in BOTH
 * layers (region shading and flow bands). Okabe-Ito palette.
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
const fmt = (n) => _nf0.format(n);
const fmt1 = new Intl.NumberFormat("en-NZ", { maximumFractionDigits: 1 });
const fmt3 = new Intl.NumberFormat("en-NZ", { maximumFractionDigits: 3 });
// pipeline stores UTC; the site displays Pacific/Auckland (browser is DST-aware)
const nzDateFmt = new Intl.DateTimeFormat("en-NZ", { timeZone: "Pacific/Auckland", year: "numeric", month: "short", day: "numeric" });
const nzDtFmt = new Intl.DateTimeFormat("en-NZ", { timeZone: "Pacific/Auckland", year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
const nzDate = (iso) => (iso ? nzDateFmt.format(new Date(iso)) : "—");
const nzDateTime = (iso) => (iso ? nzDtFmt.format(new Date(iso)) : "—");

const BAND = {
  low: { color: "#D55E00", label: "Low flow (dry)" },
  normal: { color: "#E69F00", label: "Near normal" },
  high: { color: "#009E73", label: "High flow" },
  insufficient: { color: "#999999", label: "Insufficient data" },
};
// region shading ramp, light → dark
const RAMP = ["#fef0d9", "#fdd49e", "#fdbb84", "#fc8d59", "#d7301f"];
const METRICS = {
  growth: {
    label: "2030 demand growth", unit: "%", value: (r) => 100 * (r.proj_demand_m3_day / r.daily_demand_m3 - 1),
    buckets: ["<2.5%", "2.5–4%", "4–5.5%", "5.5–7%", "≥7%"],
    idx: (v) => (v >= 7 ? 4 : v >= 5.5 ? 3 : v >= 4 ? 2 : v >= 2.5 ? 1 : 0),
  },
  percap: {
    label: "Per-capita use", unit: " L/p/d", value: (r) => r.l_per_person_day_w,
    buckets: ["<300", "300–360", "360–430", "430–500", "≥500 L/p/d"],
    idx: (v) => (v >= 500 ? 4 : v >= 430 ? 3 : v >= 360 ? 2 : v >= 300 ? 1 : 0),
  },
  leak: {
    label: "Leakage", unit: "%", value: (r) => r.loss_pct_w,
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
const FIG = ["fig1.png", "fig2.png", "fig3.png"];
function buildFindings(supply, flowPct) {
  const rows = supply.rows;
  const totNow = rows.reduce((s, r) => s + r.daily_demand_m3, 0);
  const totProj = rows.reduce((s, r) => s + r.proj_demand_m3_day, 0);
  const totLeak = rows.reduce((s, r) => s + r.leak_m3_day, 0);
  const akl = rows.find((r) => r.region === "auckland");
  const hb = rows.find((r) => r.region === "hawkes_bay");
  const cant = rows.find((r) => r.region === "canterbury");
  const hbFree = (hb.l_per_person_day_w - akl.l_per_person_day_w) * hb.pop_served / 1000;
  const cantRatio = cant.leak_m3_day / (cant.proj_demand_m3_day - cant.daily_demand_m3);
  const leakPeople = (totLeak * 1000) / akl.l_per_person_day_w;
  const hbrc = (flowPct.rows || []).filter((r) => r.council === "hbrc")
    .map((r) => r.pctile_pct).filter((v) => v != null).sort((a, b) => a - b);
  const pctMin = hbrc.length ? hbrc[0] : null;
  const pctMax = hbrc.length ? hbrc[hbrc.length - 1] : null;

  return [
    {
      img: FIG[0], imgAlt: "Per-capita water use, Hawke's Bay vs Auckland — chart",
      headline: "Efficiency is the cheapest new water.",
      num: `${fmt3.format(hb.l_per_person_day_w)} vs ${fmt3.format(akl.l_per_person_day_w)} L/p/d`,
      soWhat: `Matching Auckland's efficiency frees ${fmt(hbFree)} m³/day — ${Math.round((hbFree / (totProj - totNow)) * 100)}% of all 6-region demand growth to 2030.`,
      foot: "Source: NEPR 2024/25 unit-level extract (sql/02) · Stats NZ ERP 2025",
      target: "charts",
    },
    {
      img: FIG[1], imgAlt: "Leaks as a share of daily supply — chart",
      headline: "Fix the pipes before building new plants.",
      num: `${fmt(totLeak)} m³/day (${fmt3.format(100 * totLeak / totNow)}%)`,
      soWhat: `Canterbury leaks ${fmt(cant.leak_m3_day)} m³/day — ${fmt3.format(cantRatio)}× its own projected growth. The leaked volume could serve ${fmt(leakPeople)} people.`,
      foot: "Source: NEPR 2024/25 unit-level extract (sql/02)",
      target: "charts",
    },
    {
      img: FIG[2], imgAlt: "River flow percentiles at monitored sites — map",
      headline: "We can't see the water.",
      num: "2 of 6 councils",
      soWhat: `HBRC is live; ORC's public record froze in 2021. Live HB flows sit at the ${pctMin == null ? "—" : fmt3.format(pctMin)}th–${pctMax == null ? "—" : fmt3.format(pctMax)}th percentile — Fernhill is in its driest 10%.`,
      foot: "Source: council Hilltop servers (sql/03) · see flow caveats",
      target: "map-section",
    },
  ];
}

function renderFindings(cards) {
  el("finding-cards").innerHTML = cards.map((c, i) => `
    <div class="card" data-target="${c.target}" tabindex="0" role="button" aria-label="Jump to evidence for finding ${i + 1}">
      <img class="card-img" src="img/${c.img}" alt="${c.imgAlt}" onerror="this.style.display='none'">
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
    const c = RAMP[m.idx(m.value(r))];
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
    const rows = supply.rows.slice().sort((a, b) => m.value(b) - m.value(a));
    el("region-list").innerHTML = rows.map((r) => {
      const v = m.value(r);
      const c = RAMP[m.idx(v)];
      return `<div class="list-row" data-region="${r.region}">
        <div class="top"><span class="name">${labels[r.region] || r.region}</span>
          <span class="badge" style="background:${c}">${fmt1.format(v)}${m.unit}</span></div>
        <div class="meta">Pop 2025: ${fmt(r.pop_2025)} · demand ${fmt(r.daily_demand_m3)} → ${fmt(r.proj_demand_m3_day)} m³/day</div>
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
    ? '<br><span class="stale">⚠ historical record — public ORC server ended 2021-04-23</span>'
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
      Same-week percentile: <b>${row.pctile_pct == null ? "—" : fmt1.format(row.pctile_pct)}</b>
      (${BAND[row.band] ? BAND[row.band].label : row.band}) · history n=${row.n_history}
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
        · percentile ${row.pctile_pct == null ? "—" : fmt1.format(row.pctile_pct)}
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
  const g = METRICS.growth.value(r);
  return `<b>${regionLabel(regions.regions, r.region)}</b><br>
    Population 2025: ${fmt(r.pop_2025)} · served by public networks: ${fmt1.format(r.coverage_pct)}%<br>
    Supply: ${fmt1.format(r.l_per_person_day_w)} L/person/day · leaks: ${fmt1.format(r.loss_pct_w)}%<br>
    Daily demand: ${fmt(r.daily_demand_m3)} m³ → 2030: <b>${fmt(r.proj_demand_m3_day)} m³</b> (+${fmt1.format(g)}%)<br>
    Leaked: ${fmt(r.leak_m3_day)} m³/day · CARL ${fmt1.format(r.carl_l_conn_day_w)} L/conn/day · ILI ${fmt1.format(r.ili_w)}`;
}

function renderLegend(d) {
  const m = METRICS[ctx.metric];
  const rampHtml = RAMP.slice().reverse().map((c, i) =>
    `<span class="swatch" style="background:${c}"></span>${m.buckets[i]}`).join(" ");
  el("map-legend").innerHTML =
    `<span><b>Region shading = ${m.label}:</b></span> ${rampHtml}` +
    `&nbsp;&nbsp;|&nbsp;&nbsp;<span><b>Flow sites (same-week percentile):</b></span>` +
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
    ? `<p class="caption">${noData.map((r) => r.display).join(", ")}: LAWA publishes no consent-use data for ${noData.length > 1 ? "these regions" : "this region"}.</p>`
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
  const labels = {};
  regions.regions.forEach((r) => { labels[r.region] = r.display.en; });
  const data = supply.rows.map((r) => ({
    value: [r.cagr5_pct, r.l_per_person_day_w, r.daily_demand_m3, r.loss_pct_w],
    name: labels[r.region] || r.region,
  }));
  chart.setOption({
    tooltip: {
      formatter: (p) => `<b>${p.data.name}</b><br>Pop growth (5-yr CAGR): ${fmt1.format(p.data.value[0])}%` +
        `<br>Supply: ${fmt1.format(p.data.value[1])} L/person/day` +
        `<br>Daily demand: ${fmt(p.data.value[2])} m³` +
        `<br>Leakage: ${fmt1.format(p.data.value[3])}% of supply`,
    },
    grid: { left: 46, right: 24, top: 28, bottom: 44 },
    xAxis: { name: "5-yr population growth (CAGR, %)", type: "value" },
    yAxis: { name: "litres / person / day", type: "value" },
    visualMap: [
      { type: "continuous", dimension: 3, min: 15, max: 30, orient: "vertical", right: 0, top: "center",
        text: ["more leakage", "less leakage"], textStyle: { fontSize: 10 }, inRange: { color: ["#009E73", "#E69F00", "#D55E00"] }, itemHeight: 120 },
      { type: "continuous", dimension: 2, min: 50000, max: 500000, show: false, inRange: { symbolSize: [18, 60] } },
    ],
    series: [{
      type: "scatter", data,
      label: { show: true, formatter: (p) => p.data.name, position: "top", fontSize: 10, color: "#14303e" },
      emphasis: { focus: "series" },
    }],
  });
}

function renderDemandChart(supply, regions) {
  const chart = echarts.init(el("chart-demand"));
  ctx.charts.push(chart);
  const labels = {};
  regions.regions.forEach((r) => { labels[r.region] = r.display.en; });
  const rows = supply.rows.slice().sort((a, b) =>
    (b.proj_demand_m3_day / b.daily_demand_m3) - (a.proj_demand_m3_day / a.daily_demand_m3));
  const names = rows.map((r) => labels[r.region] || r.region);
  chart.setOption({
    tooltip: { trigger: "axis", valueFormatter: (v) => `${fmt(v)} m³/day` },
    legend: { top: 0, textStyle: { fontSize: 11 } },
    grid: { left: 52, right: 52, top: 34, bottom: 30 },
    xAxis: { type: "category", data: names, axisLabel: { fontSize: 10.5 } },
    yAxis: [
      { type: "value", name: "m³ / day", nameTextStyle: { fontSize: 10 } },
      { type: "value", name: "leak m³ / day", nameTextStyle: { fontSize: 10 }, splitLine: { show: false } },
    ],
    series: [
      { name: "Daily demand (2025)", type: "bar", data: rows.map((r) => r.daily_demand_m3), itemStyle: { color: "#9ecae1" } },
      { name: "Projected 2030", type: "bar", data: rows.map((r) => r.proj_demand_m3_day), itemStyle: { color: "#3182bd" } },
      { name: "Lost to leaks", type: "line", yAxisIndex: 1, data: rows.map((r) => r.leak_m3_day),
        itemStyle: { color: "#D55E00" }, lineStyle: { width: 2.5 }, symbol: "circle", symbolSize: 7,
        label: { show: true, formatter: (p) => `${fmt(p.value)}`, fontSize: 9, color: "#D55E00", position: "top" } },
    ],
  });
}

/* ------------------------------------------------------------------ */
/* Tables & health                                                     */
/* ------------------------------------------------------------------ */
function renderFlowTable(flowPct, flowSites) {
  const coord = {};
  flowSites.sites.forEach((s) => { coord[s.council + "|" + s.site] = s; });
  const rows = flowPct.rows.map((r) => {
    const c = coord[r.council + "|" + r.site];
    const hasMarker = c && c.lat != null;
    const stale = r.stale_days > 365;
    return `<tr>
      <td>${r.council.toUpperCase()}</td>
      <td>${r.site}</td>
      <td>${r.latest_date}${stale ? ` <span class="stale">(public server ended 2021-04)</span>` : ""}</td>
      <td>${r.latest_flow_m3s}</td>
      <td>${r.pctile_pct == null ? "—" : fmt1.format(r.pctile_pct)}</td>
      <td><span class="badge ${r.band}">${BAND[r.band] ? BAND[r.band].label : r.band}</span></td>
      <td>${r.n_history}</td>
      <td>${hasMarker ? "✓" : "—"}</td>
    </tr>`;
  }).join("");
  el("flow-table").innerHTML = `<thead><tr>
      <th>Council</th><th>Site</th><th>Latest observation</th><th>Flow (m³/s)</th>
      <th>Same-week percentile</th><th>Band</th><th>History (days)</th><th>On map</th>
    </tr></thead><tbody>${rows}</tbody>`;
}

function renderHealth(d) {
  const { runs } = d;
  const last = runs[runs.length - 1] || {};
  const rows = last.rows || {};
  const nulls = last.null_pct || {};
  const lastUtc = last.utc ? new Date(last.utc) : null;
  const paused = !lastUtc || (Date.now() - lastUtc.getTime()) > 31 * 86400e3;

  const parts = [];
  if (paused) parts.push(`<span class="paused"><b>⚠ pipeline paused</b> — showing last good snapshot</span>`);
  if (last.utc) parts.push(
    `<span><b>Last run</b> ${nzDateTime(last.utc)} NZ · ${last.checks_passed}/${last.checks_total} checks · schema v${last.schema_version || 1}</span>`);
  if (rows.supply_per_capita_rows != null) parts.push(
    `<span><b>Rows</b> supply ${rows.supply_per_capita_rows} · growth ${rows.population_growth_rows} · flow sites ${rows.flow_percentile_rows} · pop ${rows.population_region_years}</span>`);
  const sn = nulls.supply_per_capita, fn = nulls.flow_percentile;
  if (sn && sn.l_per_person_day_w != null && fn && fn.pctile_pct != null) parts.push(
    `<span><b>Null rates</b> supply ${sn.l_per_person_day_w}% · flow ${fn.pctile_pct}%</span>`);
  const last20 = runs.slice(-20);
  parts.push(`<span class="run-bars" title="Last ${last20.length} validation runs">` +
    last20.map((r) => {
      const cls = r.checks_passed === r.checks_total ? "ok"
        : r.checks_passed > 0 ? "degraded" : "fail";
      return `<span class="bar ${cls}" title="${(r.utc || "").slice(0, 16)} · ${r.checks_passed}/${r.checks_total}"></span>`;
    }).join("") + `<span class="bars-label">last ${last20.length} runs</span></span>`);
  el("health-strip").innerHTML = parts.join("");
}

function setAsOf(d) {
  el("asof-findings").textContent = `As of ${nzDate(d.supply.processed_utc)} (NEPR 2024/25)`;
  el("asof-map").textContent = `Demand: ${nzDate(d.supply.processed_utc)} · Flow: ${nzDate(d.flowPct.processed_utc)}`;
  el("asof-consents").textContent = `Accessed ${nzDate(d.consents.compiled_utc)}`;
  el("asof-charts").textContent = `As of ${nzDate(d.supply.processed_utc)}`;
  el("asof-flow").textContent = `As of ${nzDate(d.flowPct.processed_utc)}`;
}

/* ------------------------------------------------------------------ */
/* Boot                                                                */
/* ------------------------------------------------------------------ */
window.addEventListener("DOMContentLoaded", async () => {
  try {
    const d = await loadAll();
    window.__metric = ctx.metric;

    initSections();
    renderFindings(buildFindings(d.supply, d.flowPct));
    renderMap(d);
    renderConsents(d.consents, d.regions);
    renderBubbleChart(d.supply, d.regions);
    renderDemandChart(d.supply, d.regions);
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
