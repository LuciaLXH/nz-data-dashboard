/* Public reading view: shared audited data, bilingual explanations, no new metric model. */
"use strict";
const params = new URLSearchParams(location.search);
const zh = params.get("lang") !== "en";
const say = (en, cn) => zh ? cn : en;
const escapeHTML = (value) => String(value).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const nf = new Intl.NumberFormat(zh ? "zh-CN" : "en-NZ", {maximumFractionDigits:1});
const number = n => n == null ? say("Unavailable", "暂无可比数据") : nf.format(n);
const pct = n => n == null ? number(n) : `${number(n)}%`;
const date = value => value ? new Intl.DateTimeFormat(zh ? "zh-CN" : "en-NZ", {timeZone:"Pacific/Auckland", year:"numeric", month:"short", day:"numeric"}).format(new Date(value)) : "—";
const sources = {
  outlook:"https://niwa.co.nz/climate-and-weather/seasonal-climate-outlook/seasonal-climate-outlook-october-december-2026",
  y2024:"https://niwa.co.nz/climate-and-weather/annual/annual-climate-summary-2024",
  y2025:"https://niwa.co.nz/sites/default/files/2026-01/2025_Annual_Climate_Summary_ESNZ-web.pdf",
  enso:"https://niwa.co.nz/news/el-nino-2026-what-you-need-know",
  watercare:"https://www.watercare.co.nz/home/about-us/latest-news-and-media/Auckland-enters-summer-with-healthy-water-supplies-and-updated-drought-plan",
  rural:"https://www.tasman.govt.nz/my-region/tasman-rural-hub-2/el-nino-weather-conditions",
  latest:"https://niwa.co.nz/climate-and-weather/seasonal-climate-outlook",
};
const link = (url, label) => `<a href="${url}">${label}</a>`;
const names = {
 auckland:["Auckland","奥克兰"], waikato:["Waikato","怀卡托"], hawkes_bay:["Hawke’s Bay","霍克斯湾"],
 canterbury:["Canterbury","坎特伯雷"], otago:["Otago","奥塔哥"], southland:["Southland","南地"],
};
const regionName = key => names[key] ? say(names[key][0], `${names[key][1]} · ${names[key][0]}`) : escapeHTML(key);
const languageURL = lang => { const u = new URL(location.href); u.searchParams.set("lang",lang); return u.pathname+u.search+u.hash; };
document.documentElement.lang = zh ? "zh-CN" : "en-NZ";
document.title = say("NZ Water Explained — a guide for everyday readers", "读懂新西兰的水｜面向普通读者");
document.getElementById("public-content").innerHTML = `
<a class="skip" href="#regional">${say("Skip to the data", "跳到地区数据")}</a>
<header class="topbar"><div class="wrap">
 <a class="brand" href="public.html?lang=${zh ? "zh" : "en"}">${say("NZ WATER / EXPLAINED", "读懂新西兰的水")}</a>
 <nav class="languages" aria-label="${say("Language", "语言")}">
  <a id="lang-zh" href="${escapeHTML(languageURL("zh"))}" lang="zh-CN" ${zh ? 'aria-current="page"' : ""}>中文</a>
  <a id="lang-en" href="${escapeHTML(languageURL("en"))}" lang="en" ${!zh ? 'aria-current="page"' : ""}>English</a>
 </nav>
</div></header>
<main class="wrap">
 <div class="hero" id="public-overview">
  <p class="kicker">${say("WATER, PEOPLE & EVERYDAY LIFE", "供水、人口与日常生活")}</p>
  <h1>${say("What can the numbers tell us about our water?", "我们用的水，数据能告诉我们什么？")}</h1>
  <p class="intro">${say("Dry weather makes water a practical concern. Start with your region: explore how population, reported network supply and water loss differ, then see what river records can add.", "天气变干，用水就成了身边的问题。从你关心的地区出发，了解人口、供水和报告水损的差异，再看看河流记录能提供哪些线索。")}</p>
  <p class="scope">${say("This guide covers six regions. It helps you understand published records; it cannot tell whether your home will lose supply or whether restrictions apply today.", "本页涵盖六个地区，帮助你读懂公开记录。它不能判断你家是否会停水，也不提供今天的限水状态。")}</p>
  <nav class="nav" aria-label="${say("On this page", "本页导航")}">
   <a href="#regional">${say("Explore a region", "先看一个地区")}</a>
   <a href="#background">${say("Why El Niño matters", "为什么关注厄尔尼诺")}</a>
   <a href="#rivers">${say("Read river records", "看懂河流记录")}</a>
   <a href="#next">${say("Where to go next", "下一步去哪里查")}</a>
  </nav>
 </div>
 <aside id="example-banner" class="notice" hidden>${say("Offline example: small source excerpts for demonstrating calculations. These values do not represent regional totals or current river conditions.", "离线示例：这里只使用少量来源记录演示计算，不能代表地区总体情况或当前河流状态。")}</aside>
 <p id="load-status" role="status">${say("Loading the saved data…", "正在读取保存的数据……")}</p>
 <section id="regional" aria-labelledby="region-title">
  <div class="section-head"><div><p class="kicker">01 / ${say("YOUR REGION", "你关心的地区")}</p><h2 id="region-title">${say("Three numbers, three different questions", "三个数字，回答三个不同的问题")}</h2></div>
   <div><label for="region-select">${say("Choose a region", "选择地区（不是自动定位）")}</label><select id="region-select" disabled></select></div></div>
  <p>${say("Water records are grouped by operator. Coverage varies and may cross regional boundaries, so these figures are a starting point for questions, not a league table of water efficiency.", "供水记录按运营单位归组，覆盖范围不同，也可能跨越地区边界。这些数字帮助我们提出问题，不能用来给地区的用水效率排名。")}</p>
  <div id="region-results" aria-live="polite"></div>
  <div class="panel" id="comparison-panel" hidden>
   <label for="measure-select">${say("Compare the same measure across regions", "把同一个指标放在一起比较")}</label>
   <select id="measure-select"><option value="supply">${say("Network supply per served person", "每位供水服务人口对应的供水量")}</option><option value="loss">${say("Reported water-loss rate", "报告水损率")}</option><option value="growth">${say("Average annual population growth", "人口年均增长率")}</option></select>
   <p id="comparison-note" class="small"></p><ul class="comparison" id="comparison-bars" aria-label="${say("Regional comparison", "地区比较")}"></ul>
   <p class="small">${say("Each bar starts at zero. A longer bar means a larger reported value, not a higher risk of running out of water. The selected region is darker. Missing values have no bar.", "条形从零开始。条形越长只表示该指标数值越大，不代表越容易缺水。深色表示你选中的地区；没有可比数据时不画条形。")}</p>
  </div>
 </section>
 <section id="background" aria-labelledby="background-title">
  <p class="kicker">02 / ${say("THE REASON FOR THIS PROJECT", "为什么做这个项目")}</p>
  <h2 id="background-title">${say("Changing weather brings water into everyday decisions", "天气变化，让用水成为日常生活中的问题")}</h2>
  <p>${say("I started this project to understand the water questions behind dry-weather headlines. El Niño is a Pacific climate pattern that can shift New Zealand’s winds and rainfall. Its strength alone does not determine the impact in your town.", "我做这个项目，是想读懂干燥天气新闻背后的用水问题。厄尔尼诺是一种发生在太平洋的气候现象，会影响新西兰的风和降雨；它有多强，并不能直接决定你所在城镇受到多大影响。")}
   ${link(sources.enso,say("ESNZ explanation", "ESNZ 科普说明"))}</p>
  <p class="small">${say("Background checked on 24 October 2026. This is a dated explanation, not a live weather bulletin.", "背景资料核对日期：2026 年 10 月 24 日。这是注明日期的背景说明，不是实时天气播报。")}</p>
  <ol class="timeline">
   <li><strong>2024</strong><p>${say("El Niño weakened; neutral conditions prevailed from June to December.", "厄尔尼诺减弱，6—12 月处于中性状态。")}</p>${link(sources.y2024,say("2024 annual summary", "2024 年气候总结"))}</li>
   <li><strong>2025</strong><p>${say("Mostly neutral, followed by a transition to La Niña in October.", "大部分时间处于中性状态，10 月转为拉尼娜。")}</p>${link(sources.y2025,say("2025 annual summary (PDF)", "2025 年气候总结（PDF）"))}</li>
   <li><strong>${say("October 2026", "2026 年 10 月")}</strong><p>${say("The 1 October outlook described very strong El Niño conditions and expected further strengthening. Drier conditions were favoured in the north and east of the North Island, with wetter conditions favoured in the west of the South Island.", "10 月 1 日展望描述为很强的厄尔尼诺，预计继续增强；北岛北部和东部偏干的可能性较大，南岛西部则更可能偏湿。")}</p>${link(sources.outlook,say("October–December outlook", "10—12 月季节展望"))}</li>
  </ol>
  <p>${say("The sequence is not two years of continuously worsening El Niño. A seasonal outlook describes probabilities, not a promise that every place will experience drought.", "因此，不宜把它写成“近两年厄尔尼诺持续加重”。季节展望说的是概率，并不意味着每个地方都会发生干旱。")}</p>
  <div class="metric-grid">
   <article class="metric"><h3>${say("At home", "家里：留意用水与供水通知")}</h3><p>${say("Hot, dry days can raise water demand. Garden watering and household leaks are practical things to pay attention to; restriction decisions depend on the local supply system.", "炎热干燥的天气可能增加用水需求。浇花和家中漏水都是可以关注的日常环节；是否限水，要看当地供水情况。")}</p>${link(sources.watercare,say("Watercare’s dated example", "Watercare 的供水与节水说明"))}</article>
   <article class="metric"><h3>${say("On farms and rural properties", "乡村：关注灌溉与牲畜用水")}</h3><p>${say("Dry soils and stronger winds can add pressure to irrigation, pasture and stock-water planning. The effects differ by location.", "土壤变干和风力增强，可能增加灌溉、牧草和牲畜用水安排的压力；不同地点受到的影响并不相同。")}</p>${link(sources.rural,say("Tasman’s rural guidance", "塔斯曼地区的乡村指南"))}</article>
   <article class="metric"><h3>${say("What this dashboard can add", "本项目能补充什么")}</h3><p>${say("Explore reported supply and population together, and read river observations with their dates. This project does not model rainfall, reservoir storage or household shortages, and cannot attribute these numbers to El Niño.", "把报告供水量和人口放在一起读，再结合日期查看河流记录。本项目没有降雨、水库蓄水或家庭缺水模型，不能证明这些数字由厄尔尼诺造成。")}</p></article>
  </div>
 </section>
 <section id="rivers" aria-labelledby="river-title">
  <p class="kicker">03 / ${say("RIVER RECORDS", "河流记录")}</p><h2 id="river-title">${say("Was this river reading low for that time of year?", "这次河流读数，在当年的这个季节算低吗？")}</h2>
  <p>${say("Compare each site only with its own past seasonal records. A value of 30 means about 30% of the comparable historical daily readings were lower. It does not mean 30% of water remains, and it is not a drought alert.", "每个站点只和它自己过去同一季节的记录比较。例如数值为 30，表示约 30% 的可比历史日读数比这次低；它不是“还剩 30% 的水”，也不是干旱警报。")}</p>
  <p class="notice">${say("These are the latest observations in the saved dataset, not necessarily today’s conditions. ORC records are historical. Check every observation date before interpreting a number.", "这里是保存数据中的最近观测，不一定是今天的情况。ORC 记录属于历史资料；请先看每一行的观测日期，再读数字。")}</p>
  <p id="river-dates" class="small"></p>
  <div class="table-wrap" tabindex="0" aria-label="${say("River records; scroll horizontally on small screens", "河流记录，手机可横向滚动")}"><table><caption>${say("Selected HBRC and ORC sites; names retained for source lookup", "选取的 HBRC 与 ORC 站点；保留原名便于查找来源")}</caption><thead><tr><th>${say("Site", "站点")}</th><th>${say("Observed on", "观测日期")}</th><th>${say("Flow (m³/s)", "流量（立方米/秒）")}</th><th>${say("Position in past readings (0–100)", "在历史读数中的位置（0—100）")}</th><th>${say("History available", "历史资料覆盖")}</th></tr></thead><tbody id="river-rows"></tbody></table></div>
  <details><summary>${say("How this comparison is made", "这个比较怎么算？")}</summary><p id="history-rule"></p><p>${say("The observation’s unfinished season is excluded. Valid days from earlier windows are pooled, so years with more records contribute more. February 29 uses February 28 in non-leap years. These are project display rules, not a hydrological standard or a long-term climate normal.", "观测所属的未结束季节不参与比较。之前各季节的有效日值合并计算，记录较多的年份占比也更大。2 月 29 日在非闰年对应 2 月 28 日。这些是本项目的展示规则，不是水文学标准，也不代表长期气候常态。")}</p></details>
 </section>
 <section id="next" aria-labelledby="next-title"><p class="kicker">04 / ${say("YOUR NEXT STEP", "接下来可以做什么")}</p><h2 id="next-title">${say("Use the right source for the question", "带着问题，找到合适的信息来源")}</h2>
  <ul class="next-links"><li>${say("For today’s water restrictions or outages, check the provider on your water bill or your local council’s notices. This dashboard does not monitor them.", "想知道今天是否限水或停水：查看水费账单上的供水单位或当地议会通知。本页没有接入这些实时通知。")}</li>
  <li>${link(sources.latest,say("Read the latest official seasonal outlook", "查看最新官方季节展望"))} — ${say("check its issue date and regional coverage.", "注意发布日期和适用地区。")}</li>
  <li>${link("index.html",say("Open the detailed explorer (English)", "打开详细分析页（英文）"))} — ${say("maps, water consents, reporting boundaries and full tables.", "查看地图、取水许可、不同报告范围和完整表格。")}</li></ul>
  <details id="sources"><summary>${say("Sources, definitions and data downloads", "来源、指标解释和数据下载")}</summary>
   <p>${say("Population: Stats NZ (CC BY 4.0). Water networks: selected Taumata Arowai NEPR 2024/25 records (CC BY 3.0 NZ). River flow: selected council Hilltop records from HBRC and ORC, under their respective terms. Reporting dates differ across sources.", "人口：Stats NZ（CC BY 4.0）。供水网络：选取的 Taumata Arowai NEPR 2024/25 记录（CC BY 3.0 NZ）。河流：HBRC 和 ORC 的部分 Hilltop 站点记录，遵循各来源条款。不同来源的资料日期不同。")}</p>
   <p>${link("data/supply_per_capita.json",say("Water results (JSON)", "供水结果（JSON）"))} · ${link("data/flow_percentile.json",say("River results (JSON)", "河流结果（JSON）"))} · ${link("data/network_records.json",say("Network contributions (JSON)", "逐网络来源记录（JSON）"))}</p>
   <p>${link("https://github.com/LuciaLXH/nz-data-dashboard/blob/frontend/overview-preview/docs/DATA-DICTIONARY.md",say("Data dictionary (English)", "数据字典（英文）"))} · ${link("https://github.com/LuciaLXH/nz-data-dashboard/blob/frontend/overview-preview/docs/CHANGELOG.zh-CN.md",say("Change log (Chinese)", "中文修改记录"))}</p>
  </details>
 </section>
</main><footer><div class="wrap">${say("Created by", "作者")} Xiaohan (Lucia) Liu · ${say("Public reading preview · Technical details remain in the English explorer", "公众阅读版预览 · 技术细节保留在英文详细分析页")}</div></footer>`;

const measureInfo = {
 supply:{field:"supply_l_person_day",unit:say("L/person/day", "升/人/天"),note:say("NEPR 2024/25. Only networks reporting both supply and served population enter this measure. Includes household use, other uses and losses; not the average household’s consumption.", "NEPR 2024/25。只使用同时报告供水量与服务人口的网络。包括家庭、其他用途和损失，不等于居民在家实际用掉的水。")},
 loss:{field:"paired_loss_pct",unit:"%",note:say("NEPR 2024/25. Private-property losses excluded. Divide total reported loss by total supply for the same valid networks. Loss is estimated, not all physical leakage or recoverable water.", "NEPR 2024/25，排除私人地块内损失。同一批有效网络的报告水损总量除以供水总量。水损是估计值，不全是管道漏水，也不全能回收。")},
 growth:{field:"cagr5_pct",unit:"%",note:say("Average annual population growth over each region’s stated historical period (shown beside its bar). This is past growth, not a forecast of future water demand.", "各地区标注的历史期间内，人口平均每年增长多少（年份见各条形旁）。它描述过去，不预测未来用水。")},
};
let waterData;
function renderRegion() {
 const key = document.getElementById("region-select").value;
 const r = waterData.rows.find(row => row.region === key);
 const result = document.getElementById("region-results");
 const counts = (n,total) => `${n}/${total}`;
 result.innerHTML = `<h3>${regionName(key)}</h3><div class="metric-grid">
  <article class="metric"><h3>${say("Has the population grown?", "人口增长了多少？")}</h3><div class="value">${pct(r.cagr5_pct)} <small>${say("per year", "年均")}</small></div><p>${r.cagr_start_year}–${r.cagr_end_year} · ${say("Average annual growth, not a forecast.", "历史年均增长，不是预测。")}</p><p class="coverage">${say("Regional population in", "地区人口年份")} ${r.population_base_year}：${number(r.population_base)} ${say("people", "人")}</p></article>
  <article class="metric"><h3>${say("How much water enters the networks?", "平均对应多少供水？")}</h3><div class="value">${number(r.supply_l_person_day)} <small>${say("L/person/day", "升/人/天")}</small></div><p>${say("Daily network supply divided by the population those same networks serve. It includes other uses and losses, so it is not your personal water use.", "每天的网络供水量除以同一批网络服务的人口。它包括其他用途和损失，不是你个人每天的用水量。")}</p><p class="coverage">2024/25 · ${say("Matched networks", "供水与人口均有效的网络")} ${counts(r.supply_population_networks,r.candidate_networks)} · ${say("Share of reported supply", "覆盖报告供水量")} ${pct(r.supply_population_supply_coverage_pct)}</p></article>
  <article class="metric"><h3>${say("What share is reported as lost?", "报告的水损占多少？")}</h3><div class="value">${pct(r.paired_loss_pct)}</div><p>${say("Estimated water loss, excluding losses on private property. It is not all physical leakage and does not tell us how much repairs could recover.", "不含私人地块内损失的估计水损。它不全是物理漏水，也不能直接告诉我们维修能收回多少水。")}</p><p class="coverage">2024/25 · ${say("Comparable networks", "可比较网络")} ${counts(r.paired_networks,r.candidate_networks)} · ${say("Share of reported supply", "覆盖报告供水量")} ${pct(r.paired_supply_coverage_pct)}</p></article>
 </div><p class="small">${say("The network counts use this project’s candidate records after identity checks, not every network or resident in the region. “Unavailable” means the data do not support this comparison, not zero.", "网络数量以本项目核对身份后的候选记录为分母，不代表全地区所有网络或居民。“暂无可比数据”不是零。")}</p>
 <details><summary>${say("What is included, and when were the data processed?", "哪些数据参与计算？资料是什么时候处理的？")}</summary>
 <p>${say("Water reporting period", "供水报告期")}：${escapeHTML(waterData.source_period)} · ${say("Data processed", "数据处理日期")}：${date(waterData.processed_utc)}. ${say("Processing time is not the observation date.", "处理日期不等于观测日期。")}</p>
 <p>${say("Supply per person matches water and population within the same networks. Loss rates match loss and supply, excluding missing values, non-positive supply and losses above supply. Transfers between networks have not been reconciled; the figures cannot establish unique regional supply or water available for future growth.", "人均供水只配对同一批网络的供水与服务人口。水损率只配对有效水损和供水，排除缺失、供水非正数和水损超过供水的记录。网络间调水尚未抵消，不能把这些数字当作全地区不重复的供水量或未来增长可用余量。")}</p></details>`;
 renderComparison();
 const u = new URL(location.href);u.searchParams.set("region",key);history.replaceState(null,"",u);
 document.getElementById("lang-zh").href=languageURL("zh");document.getElementById("lang-en").href=languageURL("en");
}
function renderComparison() {
 const chosen = document.getElementById("measure-select").value;
 const m = measureInfo[chosen];
 const max = Math.max(1,...waterData.rows.map(r=>Math.abs(r[m.field] ?? 0)));
 document.getElementById("comparison-note").textContent=m.note;
 document.getElementById("comparison-bars").innerHTML=waterData.rows.map(r=>{
  const v=r[m.field], selected=r.region===document.getElementById("region-select").value;
  // Negative growth is printed explicitly rather than drawn as a positive-length bar.
  return `<li class="${selected ? "selected" : ""}"><span>${regionName(r.region)}${chosen==="growth" ? `<br><small>${r.cagr_start_year}–${r.cagr_end_year}</small>` : ""}</span><span class="track" aria-hidden="true">${v != null && v >= 0 ? `<span class="fill" style="width:${100*v/max}%"></span>` : ""}</span><span class="bar-value">${number(v)}${v==null ? "" : `<span class="bar-unit">${m.unit}</span>`}${v!=null&&v<0 ? ` (${say("decline", "下降")})` : ""}</span></li>`;
 }).join("");
}
function renderRivers(flow) {
 document.getElementById("river-dates").textContent=`${say("Data processed", "数据处理日期")}：${date(flow.processed_utc)} · ${say("Flow means cubic metres passing a point each second. One cubic metre is 1,000 litres.", "流量表示每秒流过多少立方米的水；1 立方米等于 1,000 升。")}`;
 document.getElementById("river-rows").innerHTML=flow.rows.map(r=>`<tr><td>${escapeHTML(r.site)}<br><small>${escapeHTML(r.council.toUpperCase())}</small></td><td>${escapeHTML(r.latest_date)}${r.council==="orc"||r.stale_days>365 ? `<br><span class="badge">${say("Historical record", "历史记录")}</span>` : ""}</td><td>${number(r.latest_flow_m3s)}</td><td>${r.history_status==="sufficient" ? number(r.pctile_pct) : say("Not enough history to compare", "历史资料不足，暂不比较")}</td><td>${r.n_history_years} ${say("seasons with data", "个季节有记录")}<br>${pct(r.history_coverage_pct)} ${say("of possible daily records", "的季节日记录可用")}</td></tr>`).join("");
 const p=flow.policy;
 document.getElementById("history-rule").textContent=say(`For each earlier year, use the same calendar date plus or minus ${p.window_radius_days} days. Show a position only if at least ${p.min_history_years} earlier seasons each contain at least ${p.min_days_per_year} daily observations. Coverage includes missing seasons in the source span and does not measure station uptime.`, `在往年取相同月日的前后 ${p.window_radius_days} 天。至少 ${p.min_history_years} 个历史季节、每季至少 ${p.min_days_per_year} 天有效观测，才显示比较位置。覆盖率包括资料跨度中整季缺失的年份，不等于站点正常运行率。`);
}
async function bootPublic() {
 const status=document.getElementById("load-status");
 try {
  const get=async file=>{const response=await fetch(`data/${file}.json`);if(!response.ok)throw new Error(`HTTP ${response.status}`);return response.json();};
  const [water,flow]=await Promise.all([get("supply_per_capita"),get("flow_percentile")]);
  if(water.schema_version!==2||flow.schema_version!==2||!water.rows.length)throw new Error("Unsupported data");
  waterData=water;
  document.getElementById("example-banner").hidden=water.input_mode!=="offline_example";
  const select=document.getElementById("region-select");
  select.innerHTML=water.rows.map(r=>`<option value="${escapeHTML(r.region)}">${regionName(r.region)}</option>`).join("");
  if(water.rows.some(r=>r.region===params.get("region")))select.value=params.get("region");
  else if(water.rows.some(r=>r.region==="auckland"))select.value="auckland";
  select.disabled=false;
  select.addEventListener("change",renderRegion);
  document.getElementById("measure-select").addEventListener("change",renderComparison);
  renderRegion();renderRivers(flow);
  document.getElementById("comparison-panel").hidden=false;
  status.textContent=say("Saved records loaded. Check the reporting years and observation dates below.", "已载入保存记录。请留意下方的报告年份与观测日期。");
  status.className="small";
  document.body.dataset.ready="true";
 } catch(error) {
  status.setAttribute("role","alert");status.className="notice";
  status.textContent=say("The saved data could not be loaded. Please retry later. Background information and source links remain available; no missing values have been replaced with zero.", "暂时无法读取保存的数据，请稍后重试。背景说明和来源链接仍可查看；没有把读取失败的数值显示为零。");
  console.error(error);
 }
}
bootPublic();
