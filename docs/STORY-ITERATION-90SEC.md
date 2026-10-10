# Dashboard 迭代的面试讲解

适合非技术面试官，约 90 秒。重点是如何发现问题、保障信息可信度以及验证改进。实际操作由本人和 AI 助手协作完成；被问到实现细节时，可以说明自己如何审查和验证。

## English spoken version

My dashboard helps compare population growth and water supply pressure across six New Zealand regions.

One iteration started with an automatic update failure. I checked whether the problem was with the data, calculations, or publishing. The data checks passed, but publishing failed.

That prompted a broader review. I found that unavailable data sources could cause old readings to disappear. I also found that a leakage estimate could be mistaken for a measured total, and some text about river conditions did not change with the data.

With an AI assistant, I worked through these issues and reviewed the evidence. We preserved available previous readings, clarified warnings, estimates and dates, and separated data preparation from publishing. Checking the live website then revealed an issue moving the old saved data into the new system, so we corrected that too.

The final update passed 30 automated tests and data and browser checks. Fresh data for two stations could not be retrieved during publication, but all 11 station records remained visible, with clear warnings.

My main lesson was that a useful dashboard needs trustworthy information: readers should understand what the numbers mean, how current they are, and what happens when sources are unavailable.

## 中文讲解要点

先用一句话说明 dashboard 帮谁做什么判断。然后讲一次失败提醒如何促使你检查整个信息交付过程，而不是逐条复述技术报错。

故事顺序是：收到提醒 → 区分数据问题和发布问题 → 找到旧数据丢失和措辞不准确的隐患 → 保留数据并明确限制 → 验证网站和手机体验。

可以概括为：“这次迭代让我从关注图表是否能显示，进一步关注使用者能否正确理解、信任并持续使用这些信息。”

## 面试官可能追问

**What changed for the user?**

They can still see the last available readings if a source is unavailable, with a warning. Estimates and dates are clearer, and the explanations remain readable on a phone.

**How did you know the changes worked?**

We tested unavailable and empty data sources, checked that previous readings stayed available, and checked the displayed warnings and mobile layout. We also verified the updated website after deployment.

**What would you improve next?**

I would separate reported network totals from regional estimates, make the forecast year follow the data year, and reduce unnecessary requests to external data sources.

**What was your role when using AI?**

I set the scope, challenged the meaning of the numbers, and reviewed the proposed changes against the original data and the test results. The AI assistant helped inspect and implement the changes. I would explain the checks I understand and performed, rather than imply I wrote every line unaided.

不要声称已经减少了多少故障、提高了多少决策准确率或节约了多少维护时间：这些仍需要后续运行数据验证。30 项测试是工程验证结果，不是业务影响指标。
