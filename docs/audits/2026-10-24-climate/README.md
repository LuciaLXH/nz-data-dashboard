# 2026-10-24 气候研究可行性证据

核查从预览分支 `77585f3` 开始；[manifest.json](manifest.json)记录完整基线提交、
页面资源和存档输入的 SHA-256。[requests.json](requests.json)保留请求、响应状态及失败尝试，
[coverage.json](coverage.json)保存核查结果；[中文报告](../../CLIMATE-FEASIBILITY-2026-10-24.zh-CN.md)解释用途。

本次没有页面改动，因此没有新增前后页面截图。既有页面快照保留于
[上一轮记录](../../changes/2026-10-24/03-analysis-led/README.md)。本目录是新增的数据核查快照，不能冒充页面截图。
第一次 ERA5 请求因两个地点只传一个 elevation 参数返回 400；重试改为 `nan,nan` 成功。
HBRC 站名的空格编码为 `+` 时返回“无测量”，改成 `%20` 后返回元数据；
质量请求虽是 HTTP 200，但没有质量记录，不能视为通过。均保留在请求记录中。
初始三项请求未记录精确 UTC 时刻，只能追溯核查日期；其余使用脚本记录时刻。

## 已存档的公开输入

- `inputs/roni.txt`：NOAA Climate Prediction Center RONI 原始文本，未改值。
  [来源](https://www.cpc.ncep.noaa.gov/data/indices/RONI.ascii.txt)；
  [解释](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/)；
  [NWS 使用声明](https://www.weather.gov/disclaimer)。不暗示 NOAA 为本项目背书。
- `inputs/era5-two-points.json`：Open-Meteo API 的原始响应，未改值；
  weather data by [Open-Meteo](https://open-meteo.com/)，包含
  [Copernicus C3S ERA5](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=overview) 资料。
  API 数据采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，见
  [提供方许可与底层许可链接](https://open-meteo.com/en/licence)。请求参数见 requests.json。
  请求坐标为 (-37.0, 174.8)、(-42.717, 170.983)，返回格点分别为
  (-37.0, 174.75)、(-42.75, 171.0)，不能称为机场实测或地区平均。
  请求使用 `Pacific/Auckland`；未来与雨量站比较前须核对观测日边界，不能据响应的单个 UTC offset 推断多年所有日期偏移。
- 三个 `inputs/hbrc-*.xml`：HBRC Te Haroto Climate 原始响应，未改值；
  [来源与 CC BY 4.0 许可](https://www.hbrc.govt.nz/our-council/open-data/time-series-data/)。
  原始雨量仅用于可用性检查；没有质量记录不等于雨量经过质量核验。

GHCN 的七个原始站文件留在本机 `.tmp/climate-feasibility/`，未随 Git 分发；
coverage.json 只记录日期、完整性与标记计数。ORC 门户 HTML 含会话表单值，也未存入仓库。
本次未保留任何外部账户凭证，未创建账户或发送数据申请。
存档保留供应方原始换行（HBRC 元数据混有 CRLF）；本目录 Git 属性禁止自动转换输入字节，确保校验值稳定。

## 重算与校验

在仓库根目录执行，Python 标准库即可，无网络、无 API key：

```sh
python scripts/audit_climate_feasibility.py \
  --input-dir docs/audits/2026-10-24-climate/inputs
```

这会重算存档中的 RONI、ERA5、HBRC 部分。完整 coverage.json 还包含已有本地河流缓存和 GHCN 样本：

```sh
python scripts/audit_climate_feasibility.py \
  --input-dir docs/audits/2026-10-24-climate/inputs \
  --ghcn-dir .tmp/climate-feasibility \
  --flow-root data/raw/flow
```

缺少 GHCN 原始文件时可按 requests.json 的七个 `.dly` URL 下载作本地核查，
先核对 SHA-256；供应方可能修订历史，下载的新版本不得冒充本次输入。
河流原始缓存哈希在 coverage.json 每站记录中。未取得这些输入时，只能复算公开存档部分，不能声称完整离线重现。
脚本只打印结果；`--output` 可写入一个**尚不存在**的路径，拒绝覆盖历史快照。

专用检查：`python -m pytest tests/test_climate_feasibility.py -q`。
合成测试覆盖闰日、缺测、质量失败、部分日雨量、推定零值、微量降水、重复月份、截断记录和日期异常。
