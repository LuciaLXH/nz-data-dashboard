# W1 · Data source registry（2026-08-30 实测）

> 所有端点均为本次会话**实测验证**（curl，2026-08-30）。标注 ✅ = 返回有效数据。

## 河流流量 / 水位（实时）

> 2026-08-30 下午实测更新：**HBRC + ORC 时序取数全链路打通**（`scripts/fetch_hilltop.py`），
> 其余 council 公开端点无时序（记录如下）。详细行为见 [BROWSER-TESTS.md](BROWSER-TESTS.md)。

| Council | 系统 | 端点（已验证） | 状态 | 备注 |
|---|---|---|---|---|
| Hawke's Bay (HBRC) | Hilltop | `https://data.hbrc.govt.nz/Envirodata/EMAR.hts` | ✅ 实时取数 | `SiteList` **只列历史站**（数据止于 1968–2000）；实时遥测站（如 `Ngaruroro River at Fernhill`）**不在 SiteList** 但可直接 `MeasurementList`/`GetData`。取数：`Measurement=FlowM3S [Water Level]`（m³/s，15 分钟） |
| Otago (ORC) | Hilltop | `http://gisdata.orc.govt.nz/hilltop/Global.hts` | ✅ 历史取数 | 公共服务器**只提供 2010-12-29 → 2021-04-23**（无实时）。`Measurement=Flow [Water Level]`（cumecs=m³/s，5 分钟）。早前 "No data" 是请求了错误时间窗（2026 年）——已解决 |
| Canterbury (ECan) | ArcGIS REST | `https://gis1.ecan.govt.nz/arcgis/rest/services/Public/Well_Drillers/MapServer/13` | ⚠️ 仅站点元数据 | 图层 13 是 River Flow and Stage 站点属性（SITE/SITENUMBER/TELEMETERED…），**无时序**。官方数据门户 `data.ecan.govt.nz` 为 JS 应用，含 "Water permit use" 等数据集（可取水许可侧，W2 供需分析候选）；水文时序 API 待 W1.5 挖 |
| Southland (ES) | ArcGIS REST | `https://maps.es.govt.nz/server/rest/services/Public/` | ⚠️ 无流量时序 | `RiversRainfall/0` = Soil Moisture（有 Site/Date/Value 时序）；`WaterAndLand/2` = Water Quantity 是**流域多边形**（如 'Waiau Catchment'）；`EnvData` = 站点元数据。真实流量时序未在公开服务中找到 |
| Auckland (AC) | ArcGIS REST | `https://mapspublic.aucklandcouncil.govt.nz/arcgis3/rest/services/NonCouncil/LAWA/MapServer` | ⚠️ 仅参考数据 | 图层 0 = MonitoringSiteReferenceData（站点参考），无流量时序 |
| Waikato (WRC) | Hilltop? | 候选均失败：`data.waikatoregion.govt.nz` 连接失败；`www.waikatoregion.govt.nz/Envirodata/EMAR.hts` 返回 HTML 错误页 | ❌ TBD | 不影响 MVP 启动 |

**流量覆盖结论（W1）**：程序化时序 = **HBRC（实时）+ ORC（历史）**，脚本已落地
（HBRC 3 站 × 5 年日流量、ORC 8 站 × ~10 年日流量，2026-08-30 实测 0 错误）。
ECan/Southland/Auckland/Waikato 待 W1.5 补（候选：LAWA 内部 Umbraco API）。

### LAWA water quantity 内部 API（W1.5 候选，非稳定公共契约）

水量探索器（lawa.org.nz/explore-data/water-quantity/，Angular + Umbraco）暴露：
- `/umbraco/api/mapservice/FlowSites?pageId=…` — 某区域流量站点（pageId 见页面 `init('25991','region')`）
- `/umbraco/api/waterquantityservice/flowstats?pageId=…` — 流量统计
- `/umbraco/api/waterquantityservice/wateravailable|waterusage` — 可用/用水量（供需分析直接可用）
- `/umbraco/api/mapservice/boundaryforNZ` — **全部区域边界（WKT）** ✅ 已用于边界简化
若 W1.5 打通 flowstats，可统一覆盖 6 council（CC BY 4.0）。
- 另发现 `waterquantityservice/wateravailable?pageId=<region>` 返回**区域尺度降雨/径流**（如 HB：降雨 19.7 Bm³/年、径流 11 Bm³/年，源自 NIWA）——W2 供应侧可作补充信号；`waterusage?pageId=<region>` 返回 null（需 zone 页 id）。

**region_map 实测验证（2026-08-30）**：`data/ref/region_map.json` 的 aliases 与 LAWA 河流水质 State Quartile 表（11,004 行）逐一比对 —— 6 council 5,954 行**全部精确匹配**（auckland 401 / canterbury 1616 / hawkes_bay 928 / otago 1017 / southland 761 / waikato 1231），其余 11 区域正确未匹配（含 macron 变体 manawatū-whanganui），无错配无遗漏。

## 人口（年度）

| Source | 端点 | 状态 | 备注 |
|---|---|---|---|
| Stats NZ ADE API | `https://api.stats.govt.nz/opendata/v1/` | ⏸️ **后端 502** | 2026-08-30 实测：DNS/TLS 正常，Azure 网关后端故障（不带 key 也 502，非 key 问题）。订阅 `Lucia-NZ-DA-API-Key` 已激活。**稍后重试**；key 已在本地 `.env`，勿提交 |

## 水质（年度快照，手动下载）

LAWA 批量下载（[download-data](https://www.lawa.org.nz/download-data)，2026-08-30 确认可访问）：
- 河流水质 state & trend：`lawa-river-water-quality-state-and-trend-results_30oct2025.xlsx`
- 河流生态：`lawa-river-ecology-monitoring-data_16dec2025.xlsx` / `lawa-river-ecology-state-and-trend-results_30oct2025.xlsx`
- 湖泊：`lawa-lake-quality-dataset__16dec2025.xlsx`
- 地下水：`lawa-groundwater-quality-dataset_17oct2025.xlsx`
- 休闲/游泳水质：`lawa-recreational-water-quality-monitoring-data-20019-2025_6march2026.xlsx`
- 土地覆盖：`lawa-land-cover-data_oct2025.xlsx`

> **W1 状态（2026-08-30）：7 个文件已全部下载 ✅** → `data/raw/lawa/`（共 ~45MB，SHA-256 + 来源 URL 见 [`data/raw/lawa/MANIFEST.md`](../data/raw/lawa/MANIFEST.md)，README 许可表已引用下载日期）。
>
> 结构速览（openpyxl 实测）：
> - 河流水质（state-and-trend）：`State Quartile Results`（11,005 行：Region/Agency/Catchment/LawaSiteID/SiteID/Latitude/Longitude/WFSLanduse/WFSAltitude/RECLandCover/SedimentClass/Indicator/Median/Quartile_AllSites/Quartile_SameLandUse/...）、`State Attribute Band`（8,282）、`Trend`（43,781：TrendScore/TrendDescription，如 "Likely degrading"）。Region 为小写（`auckland`）→ 归一到 6 council 需映射表
> - 河流生态：`River Ecology State`（4,989：Year/Median/NPSFM Attribute Band）、`River Ecology Trend`（10,406）
> - 土地覆盖：`Regional/Catchment Broad|Medium|Detailed`（Area 1996–2018 ha，含区域/流域两粒度）—— 章节 B 用
> - 湖泊/地下水/休闲水质：结构待 W1 剩余步骤抽查（不影响 MVP 主线）

## W1 待办状态（2026-08-30 下午更新）

- [x] Hilltop/流量端点验证 + **取数脚本落地**（HBRC 3 站实时 + ORC 8 站历史，`scripts/fetch_hilltop.py`，日流量聚合）
- [x] LAWA 批量下载源确认 + 7 个 xlsx 快照已落盘（MANIFEST.md）
- [x] 边界几何简化 ✅ → `data/processed/boundaries_regions_simple.geojson`（**4.9 KB**，远低于 500KB；来源为 LAWA `mapservice/boundaryforNZ` WKT，CC BY 4.0，替代 Stats NZ GDS 因 datafinder 需 JS 交互；LAWA 边界源自 Stats NZ 区域议会边界）
- [x] 区域名归一化映射表 ✅ → `data/ref/region_map.json`（REGC ↔ council ↔ LAWA zone + macron 别名；REGC 代码待 ADE 恢复后确认）
- [ ] Stats NZ ADE API 跑通（仍 502；`fetch_population.py` 已实现重试+优雅降级）
- [ ] Water NZ NPR 提取（研究中）
- [ ] `make data` 一条命令产出 processed JSON（W1 最小版管线已接，见下）

## 已知问题（补充，2026-08-30 下午）

- **ORC GetData "No data" 已解决**：原因 = 公共服务器只提供 **2010-12-29 → 2021-04-23** 的历史数据（无实时），早前用 2026 年窗口请求自然无数据。`Measurement=Flow [Water Level]`（cumecs）正常工作。脚本按站点 MeasurementList 的 From/To 自动取窗口。
- **HBRC SiteList 只含历史站**：实时遥测站（Fernhill / Tukituki Red Bridge / Mohaka Raupunga）不在 SiteList，但直接 MeasurementList/GetData 可用。脚本用精选站点清单。
- **Hilltop 拒绝 `+` 空格编码**（"No Measurements available"），必须 `%20`（urllib `quote_via=quote`）。
- **Hilltop `Interval=P1D` 无效**：HBRC/ORC 都忽略日聚合参数 → 客户端日聚合（`daily_means()`）。
