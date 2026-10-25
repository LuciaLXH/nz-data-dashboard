# 暂时恢复个人网站截图对应的旧版

用户提供的截图包含 “Demand & efficiency”、彩色气泡、2030 年需求柱形与漏损折线，
底部标为 schema v1。核对后对应旧代码 `19669bc`。本次恢复公开展示，保留新研究与新版页面开发。

## 修改前后

| 时点 | 桌面 | 手机 |
|---|---|---|
| 修改前：当前线上 schema v2 | [截图](before-charts/desktop.png) | [截图](before-charts/mobile.png) |
| 修改后：本地验证的历史发布快照 schema v1 | [截图](after-local-charts/desktop.png) | [截图](after-local-charts/mobile.png) |
| 发布后：直接打开原网址验证 | [线上截图](after-live/desktop-charts.png) | [线上截图](after-live/mobile-charts.png) |

首页也保留了[修改前](before-home/desktop.png)、[本地修改后](after-local-home/desktop.png)与
[线上发布后](after-live/desktop-home.png)的完整画面，包括新增的历史演示说明；各目录均有手机版。

修改前来自线上成功发布 run `40229179362` 的完整成品。
`before-live-verification.json` 记录当时直接访问线上页面、脚本、样式及供水/河流数据所得的校验值，
与截图使用的成品一致。拍摄发生在本次发布切换之前。

恢复目标来自 run `40053730463`，构建于 2026-10-24，页面代码与 `19669bc` 完全对应。
个人网站截图的构建日期是 10 月 12 日；本次不伪造日期，不把 24 日构建说成 12 日原件。
**前后是两个完整发布版本，数据及指标口径也不同，不是控制相同数据的纯样式比较。**
各目录保留拍摄时的供水、人口、河流、地区数据及哈希。捕获工具的源码 HEAD 来自仍保留的
开发目录 `1c08f5b`，不代表被拍页面的源码；被拍版本以实际 served asset/data 哈希和上述发布来源为准。

旧版恢复后保留其布局，也保留其原有局限：手机上的图例、部分地区标签较拥挤。
本轮没有借回退改写旧图。页面另加历史演示说明，防止将已撤回的旧分析结论误当作最新判断。

## 如何保留新版

没有重置 main，没有删除或覆盖预览分支。公开站点改为发布固定成品，
定时任务也不会自动换回未完成的新界面。原计算管线和已有审核文档继续保留，
中文预览与气候研究留在 `frontend/overview-preview`。
[恢复新版的步骤](../../../PUBLIC-RELEASE.md)说明如何取消这一临时状态。

## 验证

本地旧版成品的全部数据与归档逐字节一致；发布工具核对压缩包及主要资源的 SHA-256，
检查 schema v1 配套，拒绝覆盖输出目录及不安全归档路径。
离线构建和完整测试结果、浏览器检查及上线验证见同目录的验证记录；上线前本地截图不冒充线上结果。

发布提交 `1d187fb` 已通过[部署](https://github.com/LuciaLXH/nz-data-dashboard/actions/runs/40237354178)
和[离线 CI](https://github.com/LuciaLXH/nz-data-dashboard/actions/runs/40237354193)。
直接访问原网址确认 schema v1、历史说明及两柱一折线图；全部发布数据和主要资源哈希与本地待发布成品一致。
线上验证时间、数据校验与截图哈希见 [after-live/manifest.json](after-live/manifest.json)。
