# Browser test list（浏览器可点击验证清单）

> 目的：人工核对各 council 数据端点是否正常。全部链接**已实测验证**（2026-08-30）。
> 打开方式：Hilltop 必须带 `?Service=Hilltop&Request=...` 参数；ArcGIS 建议加 `?f=pjson` 显示纯 JSON。

## 打开后看到什么算正常？

- **Hilltop**：浏览器显示 **XML 树**（`<HilltopServer>...<Site Name=...>`）—— 这就是数据，不是乱码
- **ArcGIS**：显示 **JSON**（`{"fields":[...],"features":[...]}`）
- **如果看到 `IIS Windows Server` 欢迎页**：说明打开的是**根域名**（如 `data.hbrc.govt.nz/`），数据在具体路径下，属正常现象，不是端点坏了
- **如果看到 `Hilltop Server` 的 HTML 说明页**：说明 `.hts` 没带查询参数，补上参数即可

---

## 1. Hilltop 类

### Otago (ORC) — `gisdata.orc.govt.nz` ✅ 历史取数可用（2026-08-30 下午更新）

> 重要：公共服务器**只提供 2010-12-29 → 2021-04-23** 的历史数据（无实时）。
> 早前 "GetData No data" 是请求了 2026 年窗口所致 —— 用 2020 年窗口即可正常取数。

| 用途 | 链接 |
|---|---|
| 站点列表 | `http://gisdata.orc.govt.nz/hilltop/Global.hts?Service=Hilltop&Request=SiteList` |
| 某站测量项 | `http://gisdata.orc.govt.nz/hilltop/Global.hts?Service=Hilltop&Request=MeasurementList&Site=Arrow%20at%20Cornwall%20street%20d%2Fs` |
| 取数（Flow，cumecs） | `http://gisdata.orc.govt.nz/hilltop/Global.hts?Service=Hilltop&Request=GetData&Site=Arrow%20at%20Cornwall%20street%20d%2Fs&Measurement=Flow%20%5BWater%20Level%5D&From=2020-01-01&To=2020-01-31` |

### Hawke's Bay (HBRC) — `data.hbrc.govt.nz` ✅ 实时取数可用

> 注意：公共 `SiteList` **只列历史站**（数据止于 1968–2000，如 Tukituki at Waipukurau 止于 2000）。
> 实时遥测站（如 `Ngaruroro River at Fernhill`）不在 SiteList 中，但直接 MeasurementList/GetData 可用。

| 用途 | 链接 |
|---|---|
| 站点列表（历史站为主） | `https://data.hbrc.govt.nz/Envirodata/EMAR.hts?Service=Hilltop&Request=SiteList` |
| 某站测量项 | `https://data.hbrc.govt.nz/Envirodata/EMAR.hts?Service=Hilltop&Request=MeasurementList&Site=Ngaruroro%20River%20at%20Fernhill` |
| 取数（流量 m³/s，15 分钟） | `https://data.hbrc.govt.nz/Envirodata/EMAR.hts?Service=Hilltop&Request=GetData&Site=Ngaruroro%20River%20at%20Fernhill&Measurement=FlowM3S%20%5BWater%20Level%5D&From=2026-08-27&To=2026-08-30` |
| 已验证实时站 | `Ngaruroro River at Fernhill`、`Tukituki River at Red Bridge`、`Mohaka River at Raupunga` |

---

## 2. ArcGIS REST 类

> 结构：`服务信息` 页可看图层与字段；`数据查询` 直接返回记录。两者都可加 `&resultRecordCount=5` 限制条数。

### Canterbury (ECan) — `gis1.ecan.govt.nz` ✅

| 用途 | 链接 |
|---|---|
| 服务信息（River Flow and Stage 图层） | `https://gis1.ecan.govt.nz/arcgis/rest/services/Public/Well_Drillers/MapServer/13?f=pjson` |
| 数据查询 | `https://gis1.ecan.govt.nz/arcgis/rest/services/Public/Well_Drillers/MapServer/13/query?where=1%3D1&returnGeometry=false&outFields=*&f=json&resultRecordCount=5` |

### Southland (ES) — `maps.es.govt.nz` ✅

| 用途 | 链接 |
|---|---|
| 服务信息（RiversRainfall） | `https://maps.es.govt.nz/server/rest/services/Public/RiversRainfall/MapServer?f=pjson` |
| 数据查询（图层 0 = Soil Moisture，**非流量**） | `https://maps.es.govt.nz/server/rest/services/Public/RiversRainfall/MapServer/0/query?where=1%3D1&returnGeometry=false&outFields=*&f=json&resultRecordCount=5` |

### Auckland (AC) — `mapspublic.aucklandcouncil.govt.nz` ✅

| 用途 | 链接 |
|---|---|
| 服务信息（LAWA 监测站参考数据） | `https://mapspublic.aucklandcouncil.govt.nz/arcgis3/rest/services/NonCouncil/LAWA/MapServer?f=pjson` |
| 数据查询（图层 0 = MonitoringSiteReferenceData） | `https://mapspublic.aucklandcouncil.govt.nz/arcgis3/rest/services/NonCouncil/LAWA/MapServer/0/query?where=1%3D1&returnGeometry=false&outFields=*&f=json&resultRecordCount=5` |

---

## 3. 待定

- **Waikato (WRC)**：`data.waikatoregion.govt.nz` 当前连接失败，待重试
- **Stats NZ ADE API**：`api.stats.govt.nz` 后端临时 502（2026-08-30），key 有效，待官方修复

---

## 已知问题（W1 记录，2026-08-30 下午更新）

1. ~~**ORC GetData 返回 "No data"**~~ **已解决**：公共 ORC 服务器只提供历史数据
   （2010-12-29 → 2021-04-23，无实时）；请求 2026 年窗口自然返回 No data。
   用 2020 窗口 + `Measurement=Flow [Water Level]`（cumecs）正常。fetch 脚本按
   MeasurementList 的 From/To 自动取实际窗口。
2. **HBRC SiteList 只含历史站**：实时遥测站不在 SiteList（可直接 GetData）。
   脚本用精选站点清单（Fernhill / Tukituki Red Bridge / Mohaka Raupunga）。
3. **站点名必须 URL 编码且用 `%20`**（空格 → `%20`）：HBRC 拒绝 `+` 编码
   （"No Measurements available"）。
4. **Hilltop `Interval=P1D` 无效**（两服务器均忽略）→ 客户端日聚合。
5. **ECan 图层 13 在名为 `Well_Drillers` 的服务下**（历史遗留命名），且只有站点
   元数据无时序（水文时序另在 data.ecan.govt.nz 门户，W1.5 挖）。
