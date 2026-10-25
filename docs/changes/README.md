# 修改前后快照

从 2026-10-23 起，每个能独立说明的改动都保留“修改前”和“修改后”。
目的不是只证明页面能打开，而是让不了解代码的人也能看出改变了什么、为什么改变。

- [2026-10-23：河流季节窗口、历史覆盖与样本不足提示](2026-10-23/README.md)

- [2026-10-26：暂时恢复个人网站截图对应的旧版](2026-10-26/01-restore-legacy/README.md)

## 每次怎样保存

1. **先拍再改。** 选定受影响的页面，保存修改前的桌面和手机截图、当时的结果数据及文件校验记录。
2. **一次讲清一个改动。** 按可独立解释的工作单元编号，不把每次按键或每个文件当成一步。
   本轮分为“日期窗口”和“历史覆盖与显示规则”。
3. **检查后再拍。** 用相同输入数据、计算时点、页面位置、尺寸和浏览器拍修改后的截图。
   若必须换数据，明确说明，不能把数据刷新造成的变化说成代码效果。
4. **追加说明。** 用普通语言写清之前怎样、之后怎样、数字为什么变、怎样验证、还有什么限制。
5. **保留原件。** 每次使用新目录，工具拒绝覆盖已有快照。截图不重绘、不修饰。
   缺少修改前截图时如实注明，不把事后还原的画面冒充现场记录。

这些快照保存在仓库的 `docs/changes/`，不放在会被忽略的临时目录里。
旧阶段没有完整配对截图，暂不补造。阶段一、二的历史说明仍见[中文修改记录](../CHANGELOG.zh-CN.md)。

## 给维护者的操作入口

可选截图依赖与数据处理依赖分开：

```bash
.venv/bin/python -m pip install -r requirements-review.txt
.venv/bin/python -m playwright install chromium
# 在功能修改前，当前 site/data 必须已构建完成：
.venv/bin/python scripts/capture_change.py \
  --section flow-section \
  --out docs/changes/YYYY-MM-DD/01-description/before
# 修改、验证并用同一数据和时点构建后：
.venv/bin/python scripts/capture_change.py \
  --site .tmp/comparison/site --section flow-section \
  --out docs/changes/YYYY-MM-DD/01-description/after
```

`--site` 可以指向独立构建目录。数据比较可调用现有的
`transform.build(..., processed_utc=<修改前时点>)` 固定计算日期；保留同一人口、流量及 NEPR 输入。
`capture_change.py` 只拍已有页面，不抓取或重建数据。截图依赖网页的外部图表库；普通离线数据测试
不需要安装 Playwright。该工具默认截取选定页面区域，而不是把整个网站标题重复拍进每张图。

每个快照目录包含：

| 文件 | 用途 |
|---|---|
| `desktop.png` / `mobile.png` | 1440×1000 / 390×844 视口下的真实页面区域截图；区域高度可随内容变化 |
| `flow_percentile.json` | 当时的河流结果，包括参与比较的数量；非 UI 改动也能对账 |
| `manifest.json` | 实际拍摄时间、数据计算时点、浏览器版本、关键源文件及页面资源校验值 |

Git 提交编号只是背景信息：快照包含未提交的本地修改，不能仅用 HEAD 代表截图版本。
应结合清单中的校验值和保存的数据辨认状态。当前脚本针对本项目河流改动保存数据；
后续涉及其他指标时，也应保存相应结果与输入出处。
