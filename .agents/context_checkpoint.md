# 项目检查点 · NZ 数据仪表盘（nz-data-dashboard）

*生成于 2026-08-30。本文件供「以项目目录为工作区」的会话恢复上下文（直接问「读取 .agents/context_checkpoint.md 恢复我们的工作」）。*
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
| Stats NZ ADE API | 分区人口（年度） | CC BY 4.0 | ⏸️ 502 待重试，key 有效（`.env`） |
| Water NZ NPR | 人均 L/日/漏损/计量 | 逐项确认 | ⬜ 未提取 |
| council Hilltop/ArcGIS | 流量/水位 | per-council | ✅ 5/6（WRC 待定） |
| LAWA 批量下载 | 水质/生态/湖泊/地下水/土地覆盖 | CC BY 4.0 | ✅ 已完成（2026-08-30） |
| Stats NZ GDS/LINZ | 边界 | CC BY 4.0 | ⬜ 待简化（mapshaper <500KB） |
| ~~NIWA/CliFlo~~ | — | — | **避开**：2025-07-01 并入 Earth Sciences NZ |

## 进度
- **W0 ✅**：脚手架就位（README.md / ANALYSIS.md / Makefile / .gitignore / .env.example / .github/workflows/{refresh,keepalive}.yml / sql/01-03 / scripts 骨架 / docs/PLAN.md / 评审原件 docs/review/）
- **W1 进行中**：
  - ✅ 流量端点 **5/6**：ORC（gisdata.orc.govt.nz Hilltop）、HBRC（data.hbrc.govt.nz/Envirodata/EMAR.hts）、ECan（gis1.ecan.govt.nz ArcGIS 图层 13）、Southland（maps.es.govt.nz ArcGIS）、Auckland（mapspublic.aucklandcouncil.govt.nz LAWA MapServer）
  - ✅ **HBRC GetData 全链路**（Adye / Rainfall Daily / 1998）
  - ⚠️ **ORC GetData 异常**：SiteList/MeasurementList 通，GetData+Water Level 返回 "No data"（试过站点/测量名/日期格式）→ 推测公共服务器未实时接入水位；对策：fetch 组合验证或 ORC 降级，**ECan ArcGIS 做流量主力**（详见 docs/BROWSER-TESTS.md）
  - ✅ **LAWA 快照 7 xlsx**（~45MB → `data/raw/lawa/`，SHA-256 与来源 URL 见 `data/raw/lawa/MANIFEST.md`；结构实测：河流水质 State Quartile 11k 行 / Trend 43.8k 行，Region 为小写需映射；土地覆盖按区域/流域 × 1996–2018）
  - ⏸️ **Stats NZ ADE 后端 502**（Azure 网关故障，DNS/TLS 正常；key 已激活，写于 `.env`，勿提交）
  - ⬜ **W1 剩余**：① 流量抓取脚本（`fetch_hilltop.py`，HBRC/ECan 已验证）② Stats NZ ADE 重试 ③ Water NZ NPR 提取 ④ 区域名归一化映射表（REGC ↔ council ↔ LAWA zone，macron）⑤ 边界简化 ⑥ 建 GitHub repo（私有 + GH Secrets：STATS_NZ_API_KEY）⑦ `make data` 从零跑通
- **W2**：DuckDB 接入、sql/01-03 实现、Leaflet 地图 + 2 图、**3 条书面发现**（数字+图+so what）、ANALYSIS.md、Limitations/非因果章节 —— 验收 = **能讲 3 分钟故事**
- **W3**：工程+包装（_runs.jsonl/Data Health/6 测试/Attribution/15s GIF/转公开开 Pages/验证 key 不进历史）—— 验收 = 移动端 <3s 无横滚
- **W4**：LinkedIn 曝光 + **CV 联动**（见下）

## 已核实事实（勿虚构）
- 评审修正项：README 落款已是真实姓名 **Xiaohan (Lucia) Liu**（"Feng Jiang" 是模板）；**Distinction 勿虚构**；Southland 700L 示例数字需 W1 复核
- 数据快照全部来源 URL / 日期 / 哈希记录于 MANIFEST.md

## 环境
- Python 3.12.2；openpyxl 3.1.5；pandas 2.2.3；**duckdb 未安装**（W2 需要时 `pip install duckdb`）
- `.env`：`STATS_NZ_API_KEY=3c67...`（gitignored，勿外传勿提交；建 repo 后存 GH Secret）
- 沙箱注意：本目录为会话工作区时，**项目内写入免审批**；项目外（如 CV 工作区）写入需 danger-full-access 审批

## W4 CV 联动备忘
- 项目完成后更新 career-ops 规则 10（去掉「无 GitHub 链接」，加 GitHub + 本项目条目 + 一句量化结果）
- `master_cv.md` 绝对路径：`/Users/liuxiaohan/NZ-Jobseeking/2026 JOB/CV/master_cv.md`
- 求职会话恢复：用 CV 工作区的 `.agents/context_checkpoint.md`

## 关键文档
- 执行计划：`docs/PLAN.md`（W0–W4 清单）
- 数据源注册表/实测：`docs/W1-data-sources.md`；浏览器验证：`docs/BROWSER-TESTS.md`
- 评审原件：`docs/review/`；分析大纲：`ANALYSIS.md`
