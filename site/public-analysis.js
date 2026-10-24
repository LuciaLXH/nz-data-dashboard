/* Evidence-led views over the existing v2 outputs. No regression or causal model. */
"use strict";
function shortRegion(key) {
  return names[key] ? say(names[key][0],names[key][1]) : escapeHTML(key);
}
function renderAnalysis(water,flow) {
  const rows=water.rows;
  const a=rows.find(r=>r.region==="auckland"), h=rows.find(r=>r.region==="hawkes_bay");
  const example=water.input_mode==="offline_example";
  const valid=rows.filter(r=>r.cagr5_pct!=null&&r.supply_l_person_day!=null);
  const pair=!example&&a&&h&&a.supply_l_person_day>0&&h.supply_l_person_day!=null&&a.cagr5_pct!=null&&h.cagr5_pct!=null;
  const ratio=pair ? h.supply_l_person_day/a.supply_l_person_day : null;
  const growthTitle=pair
    ? say(`Hawke’s Bay reports ${number(ratio)} times Auckland’s supply per person`, `霍克斯湾报告的人均供水，约为奥克兰的 ${number(ratio)} 倍`)
    : say("Population growth alongside network supply", "把人口增长与网络供水放在一起看");
  const growthText=pair
    ? say(`Hawke’s Bay reports ${number(h.supply_l_person_day)} litres per served person per day, against Auckland’s ${number(a.supply_l_person_day)}. Its ${h.cagr_start_year}–${h.cagr_end_year} average annual population growth was ${pct(h.cagr5_pct)}, compared with ${pct(a.cagr5_pct)} in Auckland (${a.cagr_start_year}–${a.cagr_end_year}). That contrast is a reason to investigate what the supply figures include, rather than attribute the difference to population growth.`, `霍克斯湾每位供水服务人口对应每天 ${number(h.supply_l_person_day)} 升，奥克兰为 ${number(a.supply_l_person_day)} 升。霍克斯湾在 ${h.cagr_start_year}—${h.cagr_end_year} 年的人口年均增速是 ${pct(h.cagr5_pct)}，奥克兰在 ${a.cagr_start_year}—${a.cagr_end_year} 年为 ${pct(a.cagr5_pct)}。这个反差值得继续查供水包含哪些用途，不能直接把差异归因于人口增长。`)
    : say("Compare the two recorded measures for each region. Missing pairs are omitted. Example values are not regional findings.", "对照每个地区的两项记录。缺失任一指标时不绘点，示例数据不作为地区结论。");
  document.getElementById("analysis-stories").innerHTML=`
  <section id="growth-story" class="story-section" aria-labelledby="growth-title">
   <div class="story-heading"><p class="kicker">${say("POPULATION & SUPPLY", "人口与供水")}</p><h2 id="growth-title">${growthTitle}</h2><p>${growthText}</p></div>
   <div class="evidence-layout"><figure class="plot-panel"><figcaption>${say("Each point is one regional grouping", "每个点代表一个地区归组")}</figcaption>
    <div class="scatter-scroll" tabindex="0" aria-label="${say("Population and supply plot; scroll horizontally on narrow screens", "人口与供水关系图，窄屏可横向滚动")}">${scatterSVG(valid)}</div>
    <p class="small">${say("Select a labelled point to highlight that region throughout the page. Source: Stats NZ and NEPR 2024/25; historical population periods are in each point’s description. No trend line is fitted to these six groupings.", "点击带名称的点，可在全页突出该地区。来源：Stats NZ 与 NEPR 2024/25；各点的说明附人口年份。这里只比较六个地区，没有拟合趋势线。")}</p>
   </figure><aside class="analysis-aside"><h3>${say("Why the gap needs more explanation", "这个差距，还缺哪些解释？")}</h3>
    <p>${say("The water measure includes non-household uses and losses. The population underneath it is the number served by the reporting networks, not the whole regional population used in the growth measure.", "供水量里有非家庭用途和水损。它除以的是报告网络服务的人口；人口增长率则来自整个地区，两个指标的人口范围不同。")}</p>
    <p>${say("The gap does not show that a Hawke’s Bay resident uses this much more water at home. Customer mix, network conditions and reporting coverage would need to be examined before explaining why.", "这个差距并不说明霍克斯湾居民在家用了这么多水。要解释原因，还需要核对用户构成、网络条件和报告范围。")}</p>
    <details><summary>${say("Read the plotted numbers", "展开图中数值")}</summary><table><thead><tr><th>${say("Region", "地区")}</th><th>${say("Growth/year", "年均增长")}</th><th>${say("L/person/day", "升/人/天")}</th></tr></thead><tbody>${valid.map(r=>`<tr><td>${shortRegion(r.region)}</td><td>${pct(r.cagr5_pct)}</td><td>${number(r.supply_l_person_day)}</td></tr>`).join("")}</tbody></table></details>
   </aside></div>
  </section>
  <section id="loss-story" class="story-section loss-story" aria-labelledby="loss-title">
   <div class="story-heading"><p class="kicker">${say("REPORTED LOSS & THE RECORDS BEHIND IT", "水损率背后，哪些记录参与了计算")}</p><h2 id="loss-title">${say("Similar loss rates can cover very different amounts of water", "水损率接近，资料覆盖的范围可能相差很远")}</h2><p id="loss-finding"></p></div>
   <div class="loss-control"><label for="story-boundary">${say("Compare the same reporting boundary", "先统一比较范围")}</label><select id="story-boundary"><option value="No">${say("Private-property losses excluded", "不含私人地块内损失")}</option><option value="Yes">${say("Private-property losses included", "包含私人地块内损失")}</option><option value="unknown">${say("Boundary not specified", "报告范围不明")}</option></select></div>
   <p class="small">${say("Switching boundaries selects different groups of networks. It does not add or subtract private losses from the same networks.", "切换范围会选择不同的一批网络，并不是在同一批网络上加减私人地块内的水损。")}</p>
   <div class="coverage-chart" id="loss-coverage-chart"></div>
   <div class="takeaway"><strong>${say("What to check when you see a loss-rate comparison", "下次看到水损率排名时，可以先问")}</strong><p>${say("Does it compare the same reporting boundary, and how much of each region’s reported supply is represented? A low rate based on a narrow subset cannot establish the loss rate for the whole region.", "是否使用相同的报告范围？参与计算的网络覆盖多少报告供水量？一小部分网络的较低水损率，不能代表整个地区的水损状况。")}</p></div>
  </section>`;
  const boundary=document.getElementById("story-boundary");
  boundary.addEventListener("change",()=>{renderLossEvidence(rows,boundary.value,example);wireRegionPoints();});
  renderLossEvidence(rows,"No",example);
  renderRiverProfile(flow);
  wireRegionPoints();
}
function scatterSVG(rows) {
 const xMin=Math.min(0,...rows.map(r=>Math.floor(r.cagr5_pct*2)/2));
 const xMax=Math.max(.5,...rows.map(r=>Math.ceil(r.cagr5_pct*2)/2));
 const yMax=Math.max(100,...rows.map(r=>Math.ceil(r.supply_l_person_day/100)*100));
 const x=v=>76+(v-xMin)/(xMax-xMin)*600, y=v=>326-v/yMax*256;
 let grid="";
 for(let v=0;v<=yMax;v+=100)grid+=`<line x1="76" x2="676" y1="${y(v)}" y2="${y(v)}" class="grid-line"/><text x="64" y="${y(v)+4}" text-anchor="end" class="axis-text">${v}</text>`;
 for(let v=xMin;v<=xMax+.001;v+=.5)grid+=`<text x="${x(v)}" y="350" text-anchor="middle" class="axis-text">${number(v)}%</text>`;
 const points=rows.map(r=>{
  const dx=r.region==="waikato" ? -11 : 11;
  const dy=r.region==="waikato" ? 27 : -15;
  const description=`${shortRegion(r.region)}: ${r.cagr_start_year}–${r.cagr_end_year}, ${pct(r.cagr5_pct)}; ${number(r.supply_l_person_day)} ${say("L/person/day", "升/人/天")}`;
  return `<g class="scatter-point" tabindex="0" role="button" aria-label="${escapeHTML(description)}" data-select-region="${escapeHTML(r.region)}"><title>${description}</title><circle cx="${x(r.cagr5_pct)}" cy="${y(r.supply_l_person_day)}" r="9"/><text x="${x(r.cagr5_pct)+dx}" y="${y(r.supply_l_person_day)+dy}" text-anchor="${dx<0 ? "end" : "start"}">${shortRegion(r.region)}</text></g>`;
 }).join("");
 return `<svg viewBox="0 0 740 390" class="scatter" role="group" aria-label="${say("Population growth on the horizontal axis; supply per served person on the vertical axis", "横轴为人口年均增长率，纵轴为每位服务人口对应的供水量")}"><text x="12" y="25" class="axis-title">${say("Network supply · litres per served person per day", "网络供水量 · 升/服务人口/天")}</text>${grid}<line x1="76" x2="676" y1="326" y2="326" class="axis-line"/>${points}<text x="376" y="382" text-anchor="middle" class="axis-title">${say("Historical average annual population growth", "历史人口年均增长率")}</text></svg>`;
}
function renderLossEvidence(rows,boundary,example) {
 const a=rows.find(r=>r.region==="auckland")?.loss_cohorts.find(c=>c.boundary===boundary);
 const w=rows.find(r=>r.region==="waikato")?.loss_cohorts.find(c=>c.boundary===boundary);
 document.getElementById("loss-finding").textContent=!example&&boundary==="No"&&a?.paired_loss_pct!=null&&w?.paired_loss_pct!=null
  ? say(`Auckland reports ${pct(a.paired_loss_pct)} and Waikato ${pct(w.paired_loss_pct)}. But the networks used represent ${pct(a.paired_supply_coverage_pct)} and ${pct(w.paired_supply_coverage_pct)} of their respective reported supply (rounded). The percentages alone hide that difference.`, `奥克兰为 ${pct(a.paired_loss_pct)}，怀卡托为 ${pct(w.paired_loss_pct)}；但参与计算的网络，分别覆盖各自约 ${pct(a.paired_supply_coverage_pct)} 和 ${pct(w.paired_supply_coverage_pct)} 的报告供水量。只看水损率，会漏掉这个差别。`)
  : say("Read the loss rate alongside the supply coverage for the selected group of networks. Gaps mean no comparable rate is available in this boundary.", "把当前这批网络的水损率和供水覆盖范围一起读。出现空缺，表示该范围内没有可比水损率。");
 document.getElementById("loss-coverage-chart").innerHTML=`<div class="coverage-head"><span>${say("Region · valid networks", "地区 · 有效网络")}</span><span>${say("Reported loss rate", "报告水损率")}</span><span>${say("Share of all reported supply represented", "覆盖全部报告供水量的比例")}</span></div>`+rows.map(r=>{
  const c=r.loss_cohorts.find(c=>c.boundary===boundary);
  const loss=c?.paired_loss_pct??null, coverage=c?.paired_supply_coverage_pct??null;
  const meter=(v,type)=>`<div class="evidence-meter ${type}"><span class="meter-label">${type==="loss-meter"?say("Loss", "水损率"):say("Coverage", "覆盖比例")}</span><span class="meter-track" aria-hidden="true">${v==null?"":`<span style="width:${v}%"></span>`}</span><strong>${v==null ? say("Unavailable", "无可比值") : pct(v)}</strong></div>`;
  return `<div class="coverage-row"><button type="button" class="region-link" data-select-region="${r.region}">${shortRegion(r.region)}<small>${c?.paired_networks??0}/${r.candidate_networks} ${say("networks", "个网络")}</small></button>${meter(loss,"loss-meter")}${meter(coverage,"coverage-meter")}</div>`;
 }).join("")+`<p class="small">${say("Both bars use a 0–100% scale; percentages are rounded to one decimal. Coverage uses all valid reported supply in the operator grouping as its denominator, not all water or residents in a region. Network counts use this project’s candidate records. Source: NEPR 2024/25.", "两条横条都使用 0—100% 刻度，比例按一位小数四舍五入。覆盖比例的分母是运营单位归组中的全部有效报告供水量，不是全地区所有水量或人口；网络计数的分母是本项目的候选记录。来源：NEPR 2024/25。")}</p>`;
}
function wireRegionPoints() {
 document.querySelectorAll('[data-select-region]').forEach(target=>{
  const go=()=>{document.getElementById("region-select").value=target.dataset.selectRegion;renderRegion();};
  target.onclick=go;
  if(target.tagName.toLowerCase()!=="button")target.onkeydown=event=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();go();}};
  const chosen=target.dataset.selectRegion===document.getElementById("region-select").value;
  target.classList.toggle("chosen",chosen);target.setAttribute("aria-pressed",String(chosen));
 });
}
function renderRiverProfile(flow) {
 document.getElementById("river-profile").innerHTML=`<figure class="river-figure"><figcaption>${say("Latest saved reading, compared with that site’s earlier seasons", "保存的最近观测，与该站过去同季节相比")}</figcaption><div class="river-scale"><span>0</span><span>${say("Position in historical daily readings", "在历史日读数中的位置")}</span><span>100</span></div>${flow.rows.map(r=>`<div class="river-profile-row"><div><strong>${escapeHTML(r.site)}</strong><small>${escapeHTML(r.latest_date)} · ${escapeHTML(r.council.toUpperCase())}${r.council==="orc" ? ` · ${say("historical", "历史资料")}`:""}</small></div><div class="river-position">${r.history_status==="sufficient" ? `<span class="position-track" aria-hidden="true"><i style="left:${r.pctile_pct}%"></i></span><strong>${number(r.pctile_pct)}</strong>` : `<span class="unranked">${say("Not enough history", "历史资料不足")}</span>`}</div></div>`).join("")}<p class="small">${say("Dots describe each site’s own history; they do not compare available water between rivers. Grey rows are unranked. Read the date with the dot.", "每个点只描述该站自身的历史位置，不能比较不同河流能供多少水。资料不足的站点不排名。请把点和日期一起读。")}</p></figure>`;
}
