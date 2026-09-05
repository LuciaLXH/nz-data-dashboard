# 项目检查点 · NZ 数据仪表盘（nz-data-dashboard）

*2026-08-31 更新。恢复方式：直接问「读取 .agents/context_checkpoint.md 恢复我们的工作」。*
*求职（career-ops）相关内容在 CV 工作区：`/Users/liuxiaohan/NZ-Jobseeking/2026 JOB/CV/.agents/context_checkpoint.md`（绝对路径，跨区只读无需权限）。*

## 当前状态速览（2026-08-31）
- **W0–W3 全部完成，站点上线**：`https://lucialxh.github.io/nz-data-dashboard/`（HTTP 200，Data Health 14/14；repo PUBLIC `github.com/LuciaLXH/nz-data-dashboard`）
- **视觉已定稿（用户 2026-08-31 确认"效果先过"）**：河蓝主题 `75d2082`——标题栏渐变 `#003f5f→#0072B2(Okabe-Ito 蓝)→#56B4E9`（无公认「蓝洞色」，以 Okabe-Ito 蓝为锚，色盲安全）；标题字 #eaf3fb；左侧导航字体同色（普通 #0072B2/active #005a8d）；ink #14303e + 淡蓝 tint；语义色红/琥珀/绿未动；demo.gif 已按新主题重录（2.7MB）
- **GitHub 链接已上线（`d8d5d65`，线上验证 2 处）**：Method 顶部 caption + footer（`Built by … · LinkedIn · GitHub`）；Method 名字未改
- **自动化**：`refresh.yml` 已加 push 触发器（`site/**` 与 workflow 改动自动部署，run 33338732307 验证成功）；另 6h 流量 + 月度 cron
- **新增 `docs/STORY-2MIN.md`**：英文口语稿，半技术听众，~290 词≈2 分钟，数字基于已核实事实
- 本地 HEAD = 远程 main = **9ad66f6**，工作树干净（本次会话收尾再提交 2 文件）
- 剩余：**W4**（LinkedIn 曝光 + CV 联动，用户明确不急）；可选 W1.5（见下）；章节 B 水质分析未做

## 项目定位（已定稿，勿改）
- **主线 A**：人口增长下的供水压力 —— 哪些 council 供水区最先出现供需缺口（sql/02 主线 6/6 NEPR；sql/03 流量 = 旁证层 2/6 大区）
- **章节 B**：人口解释不了水质 —— 控制土地利用后（原命题因生态谬误 / n=16 / 混杂被否；**未做**）
- **观众**：区域议会资产规划师、三水分析师；**决策**：未来 5 年哪些供水区最可能供需失衡
- **范围**：6 council —— Auckland · Canterbury · Otago · Hawke's Bay · Southland · Waikato

## 工程决策（评审后定稿）
- Python 仅 IO/编排 + **DuckDB + `sql/` 全部业务逻辑 SQL** + GitHub Actions 定时；`data/processed/` 唯一数据源（JSON+schema+`_runs.jsonl`）→ 静态站（ECharts+Leaflet）；砍 Streamlit
- 数据不进 git（deploy-pages 产物）；`.env`/GH Secrets 第一天就位（防 key 进历史）；keepalive workflow（防 60 天禁用）
- Data Health 面板（last run/行数/空值率/schema ver/近 20 次色条）；schema 校验缺失率**仅记录不硬失败**；UTC 存储 + DST 测试；retry/指数退避/优雅降级（fetch 失败写 _status、transform 读最后快照）

## 数据源与许可（README 许可表为准）
| 源 | 用途 | 许可 | 状态 |
|---|---|---|---|
| **Stats NZ SDMX API**（新 ADE 后端） | 分区人口（年度 2018–2025） | CC BY 4.0 | ✅ `api.data.stats.govt.nz/rest/data/STATSNZ,POPES_SUB_001,1.0/ALL`（旧 opendata 502 已弃用）6×48 区域-年 |
| **Water NZ NPR 2021/22**（最终版） | 人均 L/日/漏损/计量 | Water NZ 版权（非商用+署名） | ✅ 574 行 `data/raw/waternz_npr/` |
| **Taumata Arowai NEPR 2024/25**（NPR 继任者） | 按连接计量（L/conn/d、CARL、ILI、计量%） | **CC BY 3.0 NZ** | ✅ 单位级 CSV 入库（git 放行 `*.csv`+MANIFEST；PDF 20MB 忽略；**年度更新需手动替换 CSV**）+ `data/ref/water_demand.json` |
| HBRC Hilltop | 流量实时 3 站（Fernhill/Tukituki Red Bridge/Mohaka Raupunga） | per-council | ✅ 5 年日流量 |
| ORC Hilltop（gisdata.orc.govt.nz） | 流量历史 2010-12→**2021-04-23**（8 站） | per-council | ✅ ~10 年日流量；公共服务器无实时 |
| ECan/Southland/Auckland/WRC | 流量 | per-council | ⚠️ 无公开时序；W1.5 候选 LAWA Umbraco API |
| LAWA 批量下载（7 xlsx）+ boundaryforNZ | 水质/生态/湖泊/地下水/土地覆盖 + 边界 WKT | CC BY 4.0 | ✅ `data/raw/lawa/`（MANIFEST.md 记 URL/日期/哈希）+ `data/ref/boundaries_regions_simple.geojson` 4.9KB |

## 已核实事实（勿虚构）
- README 落款真实姓名 **Xiaohan (Lucia) Liu**（"Feng Jiang" 是模板）；**Distinction 勿虚构**
- **REGC 代码（官方验证）**：Auckland=02, Waikato=03, Hawke's Bay=06, **Canterbury=13, Otago=14, Southland=15**（旧方案 14/15/16 是**错的**）
- NPR 已终止（止于 2021/22）；继任者 = NEPR 2024/25（CC BY 3.0 NZ，data.govt.nz）
- ORC 公共服务器仅 2010-12-29→2021-04-23 历史（无实时）→ 站点如实标「公共记录止 2021-04」
- HBRC SiteList 只含历史站；实时站需直接 GetData（精选清单）
- Hilltop 编码：拒绝 `+` 空格（"No Measurements available"）必须 `%20`；`Interval=P1D` 无效 → 客户端日聚合
- 站点坐标 `data/ref/flow_sites.json`：8 站有坐标（5 verified=LAWA / 3 approx=riverapp+OSM），3 站无坐标只入表
- **API key 完整值从未进 git 历史**（32 位，旧历史仅 4 字符 redact 前缀；已 log -p 精确比对）

## 关键数字（2026-08-30 run；讲故事/面试用）
- HB **609.7** vs Auckland **269.7** L/p/d（2.3×）；HB 省效 ≈48,800 m³/d ≈ **62% 的 6 区 2030 增长**
- 漏损 **298,671 m³/d = 22.5%**（Canterbury 86,832 m³/d = **3.5× 自身增长** ≈ 110 万人用量）
- 2030 投影 +79,336 m³/d (+6.0%)；Canterbury +8.1% / Waikato +7.2% / Auckland +6.1%（绝对量最大 +29.8k）/ Otago +4.1% / Southland +2.5% / HB +1.1%
- 流量（2026-08-30）：Fernhill 9.5th / Mohaka 31.1th / Tukituki 40.5th 百分位
- 取水许可（context 层，consent=授权非实取）：Canterbury Irrigation 82.5% / Auckland Drinking 62.7% / Southland Stock 38.9%；**Otago 无数据**

## 环境 / 工具
- Python 3.12.2；**`.venv` 虚拟环境**（--system-site-packages；装包用 `.venv/bin/pip`，pip 直装会写 ~/.local 被沙箱拦）；duckdb/openpyxl/pandas/requests/jsonschema/playwright 已装
- mapshaper 0.7.55 在 `tools/`；**gh CLI 2.98.0** 在 `tools/gh/gh_2.98.0_macOS_arm64/bin/`（用前 `export PATH="$PWD/tools/gh/...:$PATH"`；~/.zshrc 不可写未持久化）
- git user.name=xli246 / email=xli246@uclive.ac.nz；GitHub 用户 **LuciaLXH**，repo PUBLIC；`.env` 有 STATS_NZ_API_KEY（gitignored，勿外传）
- 沙箱：项目内写入免审批；项目外（CV 工作区）写入需 danger-full-access 审批

## 关键文档
- 执行计划 `docs/PLAN.md`（W0–W4，前 3 完成）；分析大纲 `ANALYSIS.md`；评审原件 `docs/review/`
- **讲稿**：`docs/STORY-3MIN.md`（3 分钟逐屏脚本）+ **`docs/STORY-2MIN.md`**（2 分钟半技术口语稿，2026-08-31）
- **讲解/面试前重读**：`docs/REVIEW-JOURNEY.md`（思考轨迹、三步验证法、面试要点）
- 数据源实测 `docs/W1-data-sources.md`；浏览器验证 `docs/BROWSER-TESTS.md`
- 完整进度历史见 git checkpoint 提交（477f75c/e016aec/388ba48/9ad66f6 等）与 `docs/demo.gif`

## 测试与验收
- tests/ 6 套件 24 用例（schema/units/region names/DST/missing-value/percentile，SQL 逻辑内联表跑真实 sql/，离线）；`make data` 14/14
- 移动端验收 `scripts/smoke_mobile.py`（390×844）：<3s、无横滚、6 导航、0 console error
- 部署产物 site/data 44KB；demo GIF `make gif` 可重录（playwright+ffmpeg+Pillow）
- 站点本地预览：`python3 -m http.server 8090 -d site`

## W4 · 未启动（用户明确不急）
- LinkedIn 帖子 + 1 张图
- **CV 联动**：更新 career-ops 规则 10（去「无 GitHub 链接」，加 GitHub + 本项目条目 + 量化结果句，如「22.5% of 6-region supply leaks; HB 610 vs Akl 270 L/p/d」）；`master_cv.md` 绝对路径 `/Users/liuxiaohan/NZ-Jobseeking/2026 JOB/CV/master_cv.md`（写需审批）；求职会话恢复用 CV 工作区检查点

## 可选后续（供择时）
- **W1.5 流量补全线索（已实测）**：ORC 当前平台 = AQWebPortal（data.orc.govt.nz，沙箱 DNS 不通）；LAWA Umbraco API：region pageId（Otago=26001）→ `mapservice/SurfacewaterZones?pageId=`（Amisfield=31611/Arrow=31610/Bannock=31605/Benger=31593/Cardrona=31564/Taieri=31355）→ `FlowSites?pageId=` 稀疏 → flowstats/getLatestSample zone 级 null；riverapp 站页有 meta 坐标+实时 ORC 流量
- 章节 B（LAWA 水质 × 土地利用分层相关，方法沿用 PHF 实习思路但数据全公开——**勿混入 PHF 数据**）
