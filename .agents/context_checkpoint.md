# 项目检查点 · NZ 数据仪表盘（nz-data-dashboard）

*生成于 2026-08-30（晚更新：**W2 完成，进入 W3**）。本文件供「以项目目录为工作区」的会话恢复上下文（直接问「读取 .agents/context_checkpoint.md 恢复我们的工作」）。*
*求职（career-ops）相关内容在 CV 工作区：`/Users/liuxiaohan/NZ-Jobseeking/2026 JOB/CV/.agents/context_checkpoint.md`（绝对路径，需要时跨区读取，无需写权限）。*

## 项目定位（已定稿，勿改）
- **主线 A**：人口增长下的供水压力 —— 哪些 council 供水区最先出现供需缺口
- **章节 B**：人口解释不了水质 —— 控制土地利用后（原「人口塑造水质」命题因生态谬误 / n=16 / 混杂被否）
- **观众**：区域议会资产规划师、三水分析师；**决策**：未来 5 年哪些供水区最可能供需失衡
- **范围**：6 council —— Auckland · Canterbury · Otago · Hawke's Bay · Southland · Waikato；深度优先于全国覆盖

## 工程决策（评审后定稿）
- Python 仅 IO/编排 + **DuckDB + `sql/` 全部业务逻辑 SQL** + GitHub Actions 定时
- `data/processed/` 唯一数据源（JSON + schema + `_runs.jsonl`）→ 静态站（ECharts + Leaflet）
- **砍掉 Streamlit 双前端**（远期可选）；私有开发 → 转公开 → GitHub Pages
- 数据不进 git（deploy-pages 产物）；`.env`/GH Secrets 第一天就位（防 key 进历史）；keepalive workflow（防 60 天无 commit 禁用）
- 诚实时间戳 + **Data Health 面板**（last run/行数/空值率/schema ver/近 20 次色条）
- 刷新节奏：流量 24h 起步 → 6h；人口/水质月度（分区人口是年度数据，月度检查）；schema 校验缺失率仅记录不硬失败；UTC 存储 + DST 测试；retry/指数退避/优雅降级

## 数据源与许可（README 许可表为准）
| 源 | 用途 | 许可 | 状态 |
|---|---|---|---|
| **Stats NZ SDMX API**（新 ADE 后端） | 分区人口（年度，2018–2025） | CC BY 4.0 | ✅ **已跑通**：`api.data.stats.govt.nz/rest/data/STATSNZ,POPES_SUB_001,1.0/ALL`（旧 opendata 502 整会话，已弃用）。6 council × 48 区域-年落盘 |
| **Water NZ NPR 2021/22**（最终版） | 人均 L/日/漏损/计量 | Water NZ 版权（非商用+署名） | ✅ 全量 574 行落盘 `data/raw/waternz_npr/`（公开 Tableau 提取） |
| **Taumata Arowai NEPR 2024/25**（NPR 继任者） | 按连接计量（L/conn/d、CARL、ILI、计量%） | **CC BY 3.0 NZ** | ✅ 单位级 CSV + PDF 落盘 `data/raw/taumata_nepr/` |
| HBRC Hilltop（data.hbrc.govt.nz） | 流量实时（3 站：Fernhill/Tukituki Red Bridge/Mohaka Raupunga） | per-council 公开 | ✅ 已落地（5 年日流量） |
| ORC Hilltop（gisdata.orc.govt.nz） | 流量历史 2010-12→2021-04（8 站，cumecs） | per-council 公开 | ✅ 已落地（~10 年日流量） |
| ECan/Southland/Auckland/WRC | 流量 | per-council | ⚠️ 公开端点无时序；**W1.5 候选：LAWA 内部 Umbraco API**（flowstats/wateravailable/waterusage） |
| LAWA 批量下载 | 水质/生态/湖泊/地下水/土地覆盖 | CC BY 4.0 | ✅ 已完成（2026-08-30，7 xlsx） |
| LAWA boundaryforNZ | 区域边界（WKT） | CC BY 4.0 | ✅ 已简化 → `data/ref/boundaries_regions_simple.geojson` 4.9KB |
| ~~Stats NZ GDS~~ | 边界 | — | 绕过：LAWA 边界源自 Stats NZ |

## 进度
- **W0 ✅**：脚手架就位（README.md / ANALYSIS.md / Makefile / .gitignore / .env.example / .github/workflows/{refresh,keepalive}.yml / sql/01-03 / scripts 骨架 / docs/PLAN.md / 评审原件 docs/review/）
- **W1 基本完成 ✅**（2026-08-30 晚）：
  - ✅ **人口数据落地**：`fetch_population.py` 切到新 SDMX API（`api.data.stats.govt.nz/rest`），6 council × 2018–2025 完整（Auckland 165.5万→181.6万等）；REGC 代码**官方验证**：02/03/06/**13/14/15**（Canterbury=13 非 14！）
  - ✅ **NPR/NEPR 提取完成**：`data/ref/water_demand.json`（NEPR 2024/25 主表 9 供应商 + NPR 2021/22 表 + 全国背景）；原始数据 `data/raw/waternz_npr/` + `data/raw/taumata_nepr/`（gitignored）；报告 `docs/NPR-research.md` + `docs/W1-water-demand-dunedin-invercargill.md`
  - ✅ **`make data` 全绿**（8/8 含 schema；流量 11 站 + 人口 6 区域 + 区域 6）
  - ✅ **GitHub repo 已建并推送**：`github.com/LuciaLXH/nz-data-dashboard`（private）+ `STATS_NZ_API_KEY` secret 已配置；**8 个提交已推送**（HEAD=49de94d）；已扫描确认 key/token 从未进入 git 历史
  - ✅ **W1 全部完成**（2026-08-30）：流量（HBRC+ORC）、人口（6 council×2018–2025）、NPR/NEPR（water_demand.json）、区域映射（官方 REGC 验证）、边界 4.9KB、`make data` 8/8
  - ⏳ W1.5：LAWA flowstats API 补 ECan/Southland/Auckland/WRC 流量（SurfacewaterZones?pageId=25991 返回 zone Id=29298 等，但 FlowSites/flowstats?pageId=<zone> 仍返回 []；**ORC 当前平台=A QWebPortal** data.orc.govt.nz）
- **W2 ✅ 完成**（2026-08-30 晚）：DuckDB + sql/01-03 + 静态站（地图/2 图/consents/发现卡）+ 3 条发现 + STORY-3MIN.md；定位调整（sql/03=旁证层，主线 6/6 NEPR）；本地提交 **45f06e8 → bde5ab8 → 3498ca1**（HEAD=3498ca1，含 3 轮视觉迭代，详见 W2 进度）
- **W3 ⏳（当前）**：工程+包装 —— 见下方「W3 清单」
- **W4**：LinkedIn 曝光 + **CV 联动**（见下）

## 已核实事实（勿虚构）
- 评审修正项：README 落款已是真实姓名 **Xiaohan (Lucia) Liu**（"Feng Jiang" 是模板）；**Distinction 勿虚构**；Southland 700L 示例数字需 W1 复核
- 数据快照全部来源 URL / 日期 / 哈希记录于 MANIFEST.md
- **REGC 代码（官方 API 验证）**：Auckland=02, Waikato=03, Hawke's Bay=06, **Canterbury=13, Otago=14, Southland=15**（注意与旧 REGC 方案不同——旧方案 Canterbury=14/Otago=15/Southland=16 是**错的**，勿再使用）
- **NPR 已终止**：Water NZ NPR 止于 2021/22；继任者 = Taumata Arowai NEPR（最新 2024/25，CC BY 3.0 NZ 单位级 CSV 在 data.govt.nz）
- **ORC "No data" 谜团已解**：公共服务器只提供 2010-12-29→2021-04-23 历史数据（无实时）；2026 窗口自然无数据
- **HBRC SiteList 只含历史站**（1968–2000）；实时站需直接 GetData（精选清单）
- **Hilltop 编码**：拒绝 `+` 空格（"No Measurements available"），必须 `%20`；`Interval=P1D` 无效 → 客户端日聚合

## 环境
- Python 3.12.2；openpyxl 3.1.5；pandas 2.2.3；requests 2.32.3；jsonschema 4.23.0；**duckdb 已装（.venv）**
- **`.venv` 项目虚拟环境**（--system-site-packages，gitignored）：pynacl 已装（建仓脚本用）；pip 直接装包会写 ~/.local 被沙箱拦，**以后装包用 `.venv/bin/pip`**
- mapshaper 0.7.55 装在 `tools/`（npm --prefix，gitignored）
- git：user.name=xli246，email=xli246@uclive.ac.nz；本地分支 main（**HEAD=3498ca1**，13 提交；45f06e8/bde5ab8/3498ca1 为 W2 三连，**推送需 GH token，尚未推送**）；**GitHub 用户 = LuciaLXH**，repo 私有 + secret 已配（2026-08-30）；token 用完即 revoke
- `.env`：`STATS_NZ_API_KEY`（gitignored，勿外传勿提交；已存 GH Secret，**key 值从未出现在 git 历史**）
- 沙箱注意：本目录为会话工作区时，**项目内写入免审批**；项目外（如 CV 工作区）写入需 danger-full-access 审批

## W4 CV 联动备忘
- 项目完成后更新 career-ops 规则 10（去掉「无 GitHub 链接」，加 GitHub + 本项目条目 + 一句量化结果）
- `master_cv.md` 绝对路径：`/Users/liuxiaohan/NZ-Jobseeking/2026 JOB/CV/master_cv.md`
- 求职会话恢复：用 CV 工作区的 `.agents/context_checkpoint.md`

## 关键文档
- 执行计划：`docs/PLAN.md`（W0–W4 清单，**W1/W2 完成、W3 进行中**）
- 数据源注册表/实测：`docs/W1-data-sources.md`；浏览器验证：`docs/BROWSER-TESTS.md`
- **审查复盘/讲解素材：`docs/REVIEW-JOURNEY.md`**（用户问题与思考轨迹、三步验证法、面试要点——讲解项目/简历/面试前重读）
- 评审原件：`docs/review/`；分析大纲：`ANALYSIS.md`
- 流量取数实测结论：HBRC 3 站 × 5 年日流量、ORC 8 站 × ~10 年日流量（2026-08-30，0 错误）

## W2 完成（2026-08-30 晚；HEAD=3498ca1）
- ✅ DuckDB 接入；sql/01 人口增长；sql/02 供需压力（**全量 NEPR 269 系统**，覆盖 68–96%；计量 % 不在 NEPR 单位数据，见 water_demand.json）；ORG_REGION 映射数值验证
- ✅ sql/03 流量同期百分位（11 站；窗口跨年按月-日对齐 `dayofyear(date_trunc('year',l.d)+(f.d-date_trunc('year',f.d)))`，排除最新测量；pandas 交叉验证一致；`stale_days` 标记 ORC）
- ✅ **定位（用户拍板）**：sql/03 = 旁证层（2/6 大区精选站）；主线 = 6/6 NEPR 需求侧。ORC 如实标「公共记录止 2021-04」
- ✅ 站点坐标 `data/ref/flow_sites.json`（8 站有坐标：5 verified=LAWA xlsx / 3 approx=riverapp+OSM；3 站无坐标只入表）
- ✅ **取水许可** `data/ref/water_consents.json`（LAWA `waterusage?pageId=<region>&type=region`，CC BY 4.0；Canterbury Irrigation 82.48% / Auckland Drinking 62.7% / Southland Stock 38.9%；**Otago 无数据**；consent=授权非实取；API 无数据年份）
- ✅ 静态站 `site/`（无构建步；`make site` 复制 data→site/data/，gitignored）：左侧导航（透明+绿色字，标题栏下方，sticky）；板块切换（初始仅标题+Findings）；地图双栏（choropleth 指标切换 2030增长/人均/漏损 + 区域/站点列表联动）；**配色语义统一红=警惕**（Okabe-Ito 红/琥珀/绿，色盲安全）；consents 100% 堆叠条 + LAWA 链接；发现卡（484px 正方形 auto-fit 3/2/1 列，悬停 1.2 倍+邻卡变淡，字号 1.1 倍居中，≤10 词总结句，图片位 `site/img/fig1-3.png` 作背景图）；Method details 折叠；页脚 Data Health 细条；as-of 时间戳
- ✅ 3 条发现（ANALYSIS.md + README TL;DR + site）；`docs/STORY-3MIN.md`（3 分钟故事脚本）
- ✅ 校验 **14/14**；提交 **45f06e8**（W2 主体）→ **bde5ab8**（布局 v3+发现卡）→ **3498ca1**（484px 方卡+亮银标题）；**未推送**
- **关键数字（2026-08-30 run）**：HB 609.7 vs Auckland 269.7 L/p/d（2.3×；HB 省效≈48,800 m³/d≈62% 6 区 2030 增长）；漏损 298,671 m³/d=22.5%（Canterbury 86,832 m³/d=3.5× 自身增长；≈110 万人用量）；2030 投影 +79,336 m³/d (+6.0%)；Canterbury +8.1%/Waikato +7.2%/Auckland +6.1%（绝对量最大 +29.8k）/Otago +4.1%/Southland +2.5%/HB +1.1%；流量 Fernhill 9.5th/Mohaka 31.1th/Tukituki 40.5th（2026-08-30）
- ⏳ **视觉待办（用户明确"后面再慢慢调整"，不阻塞 W3）**：用户补图 `site/img/fig1-3.png`（发现卡背景图，命名对即可显示）；其余微调意见随时回来改
- ⏳ **W1.5 线索（已实测，供后续）**：ORC 当前平台 = AQWebPortal（data.orc.govt.nz，本沙箱 DNS 不通）；LAWA Umbraco API：region pageId（Otago=26001）→ `mapservice/SurfacewaterZones?pageId=`（Amisfield=31611/Arrow=31610/Bannock=31605/Benger=31593/Cardrona=31564/Taieri=31355）→ `FlowSites?pageId=<zone>` 稀疏 → `waterquantityservice/flowstats`/`sensorservice/getLatestSample` zone 级 null；riverapp 站页有 meta 坐标+实时 ORC 流量

## W3 进度（2026-08-30 晚；HEAD=7066540）
- ✅ tests/：**6 套件 24 用例**（schema/units/region names/DST/missing-value/percentile；SQL 逻辑测试用内联表跑真实 sql/；离线）
- ✅ validate.py：_runs.jsonl 增 rows/null_pct；站点 Data Health 面板（last run NZ 时间/行数/空值率/schema ver/**近 20 次色条** + >31 天显示 pipeline paused）
- ✅ 时间：存储 UTC、站点 Pacific/Auckland 显示（Intl）；tests/test_dst.py 钉死 NZ DST 边界（2026-04-04 14:00 UTC 转 NZST、2026-09-26 14:00 UTC 转 NZDT）
- ✅ fetch_population 补 retry+指数退避；Hilltop 原有；失败写 _status、transform 读最后快照（cache last success）
- ✅ refresh.yml：flow cron `0 */6 * * *` + 月度；configure/upload/deploy-pages（permissions+concurrency）；Makefile 拆 `site-data`（仅复制，CI 用）与 `site`
- ✅ **15s demo GIF 已自动生成** `docs/demo.gif`（2.5MB，560px/8fps/64 色，13s 脚本化导览）：`scripts/make_demo_gif.py` = playwright headless chromium 录屏（缓存浏览器）+ ffmpeg 抽帧 + Pillow 组装（Playwright 精简 ffmpeg 无 GIF/palette 过滤器）；`make gif` 可重录
- ✅ **部署产物瘦身**：site-data 只复制站点实际消费的文件（原误带 1.3MB flow.json + population.json）→ site/data **44KB**（移动端 <3s 目标）
- ✅ **端到端验证**：完整 `make data`（真实 key）通过 —— Stats NZ 6×48 区域年、HBRC 3 站 5332 点、ORC 8 站 20201 点、transform 11 站百分位、validate 14/14 == CI 行为
- ✅ **key 验证：完整 API key 值（32 位）从未进 git 历史**（git log -p 精确比对；旧历史仅 4 字符 redact 前缀）
- ✅ **CI 两次失败已修复并部署成功（2026-08-30）**：
  1. `ab3b4df`：NEPR 2024/25 CSV 提取（1.7MB，CC BY 3.0 NZ）入库 —— transform/sql/02 唯一静态输入，CI 无法重抓；.gitignore 仅放行 `data/raw/taumata_nepr/*.csv` + MANIFEST（PDF 20MB 仍忽略；NEPR 年度更新时需手动替换 CSV）
  2. `1efeff0`：validate 的 flow_percentile 站点数检查改**记录不硬失败**（HBRC 瞬时抓取失败导致 10/11 站时流水线崩掉，违背「缺失率仅记录」决策）；现在仅 0 站才硬失败，数量记录在 _runs.jsonl + Data Health
- ✅ **GitHub Pages 已上线**：`https://lucialxh.github.io/nz-data-dashboard/`（HTTP 200；页面/数据/app.js/badge 全部验证；线上 _runs.jsonl = 14/14、11 站）；repo 已公开（LuciaLXH）；`gh` CLI 2.98.0 装在 `tools/gh/gh_2.98.0_macOS_arm64/bin/`（gitignored；用户终端用 `export PATH=...` 会话级可用，`~/.zshrc` 不可写所以没持久化）
- ✅ **移动端验收程序化通过**（`scripts/smoke_mobile.py`，390×844）：首屏 513ms（<3s）、无横向滚动、6 导航切换全通、0 控制台错误（排除 fig 图 404 预期项）== 验收标准
- ✅ README 占位符 USER/REPO → LuciaLXH/nz-data-dashboard（badges/live 链接/clone 命令）；workflow YAML 解析验证（6h+月度 cron、deploy perms）
- 本地提交：… → c507422 → a138e54 → 7066540 → 7f2004b → 629c5ec → d960c28 → c299bfe → 11bc32f → **ab3b4df** → **1efeff0**（**已推送 GitHub main**，线上运行 33305916729 成功）
