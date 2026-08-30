# 项目检查点 · NZ 数据仪表盘（nz-data-dashboard）

*生成于 2026-08-30（下午更新）。本文件供「以项目目录为工作区」的会话恢复上下文（直接问「读取 .agents/context_checkpoint.md 恢复我们的工作」）。*
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
| Stats NZ ADE API | 分区人口（年度） | CC BY 4.0 | ⏸️ 仍 502/403（网关不稳），key 有效（`.env`）；`fetch_population.py` 重试+优雅降级已实现 |
| Water NZ NPR | 人均 L/日/漏损/计量 | 逐项确认 | 🔄 子代理研究中 |
| HBRC Hilltop（data.hbrc.govt.nz） | 流量实时（3 站：Fernhill/Tukituki Red Bridge/Mohaka Raupunga） | per-council 公开 | ✅ 已落地（5 年日流量） |
| ORC Hilltop（gisdata.orc.govt.nz） | 流量历史 2010-12→2021-04（8 站，cumecs） | per-council 公开 | ✅ 已落地（~10 年日流量） |
| ECan/Southland/Auckland/WRC | 流量 | per-council | ⚠️ 公开端点无时序；**W1.5 候选：LAWA 内部 Umbraco API**（flowstats/wateravailable/waterusage，CC BY 4.0） |
| LAWA 批量下载 | 水质/生态/湖泊/地下水/土地覆盖 | CC BY 4.0 | ✅ 已完成（2026-08-30，7 xlsx） |
| LAWA boundaryforNZ | 区域边界（WKT） | CC BY 4.0 | ✅ 已简化 → `data/ref/boundaries_regions_simple.geojson` 4.9KB（替代 Stats NZ GDS——datafinder 需 JS 交互） |
| ~~Stats NZ GDS~~ | 边界 | — | 绕过：LAWA 边界源自 Stats NZ |

## 进度
- **W0 ✅**：脚手架就位（README.md / ANALYSIS.md / Makefile / .gitignore / .env.example / .github/workflows/{refresh,keepalive}.yml / sql/01-03 / scripts 骨架 / docs/PLAN.md / 评审原件 docs/review/）
- **W1 进行中**（2026-08-30 下午大推进）：
  - ✅ **`make data` 从零跑通**（11 流量站 + 6 区域 + 人口降级记录，**8/8 校验含 JSON Schema**，exit 0）
  - ✅ **JSON Schema**：`schemas/{flow,regions,population}.schema.json`，validate.py 用 jsonschema 校验（W3 的 6 测试将扩展）
  - ✅ **流量取数脚本** `scripts/fetch_hilltop.py`：HBRC 3 站实时（FlowM3S [Water Level]，m³/s）+ ORC 8 站历史（Flow [Water Level]，cumecs）→ 客户端日聚合 → `data/raw/flow/<council>/<date>.json` + `_status.json`
  - ✅ **区域映射表** `data/ref/region_map.json`（REGC 02/03/06/14/15/16 ↔ council ↔ LAWA zone + macron；REGC 标记 verified:false，待 ADE 恢复确认）
  - ✅ **边界** `data/ref/boundaries_regions.geojson`（66KB 全精度）+ `_simple`（4.9KB）
  - ✅ **git 提交** c1f8f2f / 2abc21c / 663b81d（本地 main 分支；.env/data.raw/data.processed/tools/.venv 全排除）
  - ✅ **建仓脚本** `scripts/create_github_repo.py`（PAT 走 env `GH_TOKEN`，libsodium 加密 Actions secret，pynacl 装在 `.venv`）
  - ⏸️ Stats NZ ADE：根路径仍 502（整会话未恢复）；fetch_population.py 重试(403/429/5xx)+指数退避+优雅降级已实现
  - 🔄 Water NZ NPR 提取：子代理研究结果待收（已跑 ~50min）
  - ⬜ **W1 剩余**：① GitHub 私有 repo + Secrets（**等用户 PAT**，脚本已就绪；repo 名 `nz-data-dashboard`）② NPR 落地 ③ ADE 恢复后跑通人口查询（数据集名待确认为 SubnationalPopulationEstimates）④ （W1.5）LAWA flowstats API 补 ECan/Southland/Auckland/WRC 流量——SurfacewaterZones?pageId=25991 可返回 zone（Id=29298 等），但 FlowSites/flowstats?pageId=<zoneId> 仍返回 []，待更深入逆向
- **W2**：DuckDB 接入、sql/01-03 实现、Leaflet 地图 + 2 图、**3 条书面发现**（数字+图+so what）、ANALYSIS.md、Limitations/非因果章节 —— 验收 = **能讲 3 分钟故事**
- **W3**：工程+包装（_runs.jsonl/Data Health/6 测试/Attribution/15s GIF/转公开开 Pages/验证 key 不进历史）—— 验收 = 移动端 <3s 无横滚
- **W4**：LinkedIn 曝光 + **CV 联动**（见下）

## 已核实事实（勿虚构）
- 评审修正项：README 落款已是真实姓名 **Xiaohan (Lucia) Liu**（"Feng Jiang" 是模板）；**Distinction 勿虚构**；Southland 700L 示例数字需 W1 复核
- 数据快照全部来源 URL / 日期 / 哈希记录于 MANIFEST.md
- **ORC "No data" 谜团已解**：公共服务器只提供 2010-12-29→2021-04-23 历史数据（无实时）；2026 窗口自然无数据
- **HBRC SiteList 只含历史站**（1968–2000）；实时站需直接 GetData（精选清单）
- **Hilltop 编码**：拒绝 `+` 空格（"No Measurements available"），必须 `%20`；`Interval=P1D` 无效 → 客户端日聚合

## 环境
- Python 3.12.2；openpyxl 3.1.5；pandas 2.2.3；requests 2.32.3；jsonschema 4.23.0；**duckdb 未安装**（W2 需要时 `pip install duckdb`）
- **`.venv` 项目虚拟环境**（--system-site-packages，gitignored）：pynacl 已装（建仓脚本用）；pip 直接装包会写 ~/.local 被沙箱拦，**以后装包用 `.venv/bin/pip`**
- mapshaper 0.7.55 装在 `tools/`（npm --prefix，gitignored）
- git：user.name=xli246，email=xli246@uclive.ac.nz；本地分支 main（提交 c1f8f2f/2abc21c/663b81d）；**无 gh CLI/ssh key/GH_TOKEN**（建 repo 等用户 PAT）
- `.env`：`STATS_NZ_API_KEY=3c67...`（gitignored，勿外传勿提交；建 repo 后存 GH Secret）
- 沙箱注意：本目录为会话工作区时，**项目内写入免审批**；项目外（如 CV 工作区）写入需 danger-full-access 审批

## W4 CV 联动备忘
- 项目完成后更新 career-ops 规则 10（去掉「无 GitHub 链接」，加 GitHub + 本项目条目 + 一句量化结果）
- `master_cv.md` 绝对路径：`/Users/liuxiaohan/NZ-Jobseeking/2026 JOB/CV/master_cv.md`
- 求职会话恢复：用 CV 工作区的 `.agents/context_checkpoint.md`

## 关键文档
- 执行计划：`docs/PLAN.md`（W0–W4 清单，W1 进度已更新）
- 数据源注册表/实测：`docs/W1-data-sources.md`；浏览器验证：`docs/BROWSER-TESTS.md`
- 评审原件：`docs/review/`；分析大纲：`ANALYSIS.md`
- 流量取数实测结论：HBRC 3 站 × 5 年日流量、ORC 8 站 × ~10 年日流量（2026-08-30，0 错误）
