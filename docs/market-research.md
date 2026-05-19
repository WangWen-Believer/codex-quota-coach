# Codex Quota Coach Lite 竞品调研

调研日期：2026-05-19

## 1. 调研结论

市面上已经存在多款 Codex / Claude Code / Cursor 等 AI coding assistant 的额度监控工具，但它们主要覆盖以下形态：

- macOS 菜单栏工具
- iOS companion app
- Windows 11 Widgets
- Chrome 扩展
- 本机 Web dashboard
- OpenAI API 花费追踪工具

截至本次调研，没有发现一个现成产品能完整满足本项目的目标：

> 安卓桌面卡片 + Codex `5h / Weekly` 会员额度 + 多电脑快照聚合 + 数据过期提示。

因此，`Codex Quota Coach Lite` 仍有实现价值，但需要注意不要重复造已有工具已经覆盖的平台能力。

## 2. 竞品列表

| 产品 | 平台 | 是否覆盖 Codex 5h/Weekly | 是否覆盖安卓桌面卡片 | 结论 |
| --- | --- | --- | --- | --- |
| CodexBar | macOS、iOS companion、CLI | 是 | 否 | macOS/iPhone 用户优先考虑直接使用 |
| MeterBar | macOS | 是，覆盖 OpenAI/Claude/Cursor 额度 | 否 | 适合 Mac 桌面，不覆盖 Android |
| Tally | macOS | 是，覆盖 OpenAI/Codex、Claude、Gemini | 否 | 适合 Mac 菜单栏和历史统计 |
| Wburn | Windows 11 Widgets | 是 | 否 | Windows 用户可直接使用 |
| OpenUsage | 本机 dashboard/CLI | 支持 Codex CLI | 否 | 适合桌面 dashboard，不是手机组件 |
| Codex Quota Monitor | Chrome 扩展 | 是 | 否 | 适合浏览器工具栏，不覆盖安卓桌面 |
| OwlMetric | Web/iOS/Android | 否，偏 API 花费追踪 | 否 | 不适合 Codex 会员额度 |
| OpenAI Usage Dashboard | Web | 官方数据源 | 否 | 可作为人工查看入口，不是组件 |

## 3. 重点产品分析

### 3.1 CodexBar

链接：https://codexbar.app/

CodexBar 是目前最接近本项目的成熟产品之一。它提供：

- Codex usage windows
- credit balances
- reset countdowns
- 多 provider 聚合
- macOS 菜单栏
- WidgetKit widgets
- CLI
- iOS companion
- 多 Mac 同步
- iPhone push notifications

App Store 更新说明中提到，CodexBar iOS 端支持 subscription utilization、multi-Mac sync、Mac 到 iOS 的 push notifications。

适用场景：

- 用户主要使用 Mac
- 手机是 iPhone
- 接受 macOS 菜单栏 + iOS companion 的产品形态

不适用本项目的地方：

- 不支持 Android 桌面卡片
- iOS companion 依赖 Mac 侧数据收集
- 对当前 Android 手机目标不是直接替代品

结论：

如果用户未来换成 iPhone，且主要用 Mac，CodexBar 可以直接替代本项目大部分功能。

### 3.2 MeterBar

链接：https://meterbar.app/

MeterBar 是 macOS 菜单栏工具，定位是显示 Claude、OpenAI、Cursor 的剩余额度，支持：

- macOS menu bar dashboard
- native macOS widgets
- 自动同步
- limit warnings
- 从 CLI 工具读取登录凭据

适用场景：

- Mac 用户
- 只需要桌面端额度提醒

不适用本项目的地方：

- 不支持 Android
- 没有多电脑到安卓卡片的目标形态

### 3.3 Tally

链接：https://tally-bb310.web.app/

Tally 是 macOS menubar app，支持：

- Claude
- OpenAI/Codex
- Gemini
- personal subscription limits
- API spend
- token activity
- session history
- multi-account

它还说明会读取本地 Claude Code 和 Codex session files，用于回填 token usage history。

适用场景：

- Mac 用户
- 希望看历史趋势和多账户统计

不适用本项目的地方：

- 不支持 Android 桌面卡片
- 产品明显比本项目更重

### 3.4 Wburn

链接：https://xakpc.dev/apps/wburn/

Wburn 是 Windows 11 Widgets 工具，明确支持：

- Claude Code
- OpenAI Codex
- Gemini CLI

其中 OpenAI Codex 覆盖：

- 5-hour primary window
- weekly secondary window

它还支持：

- auto-refresh every 5 minutes
- offline caching
- 读取已有 CLI tokens

适用场景：

- Windows 11 用户
- 接受 Windows Widgets 面板作为展示入口

不适用本项目的地方：

- 不支持 Android
- 不是跨设备手机桌面卡片

结论：

如果目标只是 Windows 桌面可见，Wburn 可以直接用，不必自建 Windows 端。

### 3.5 OpenUsage

链接：https://openusage.sh/

OpenUsage 是本机 dashboard/CLI，支持：

- Claude Code
- Codex CLI
- Cursor
- Copilot
- Gemini CLI
- OpenAI API
- Anthropic API
- OpenRouter 等

它强调：

- local by default
- history in local SQLite
- quotas, spend, limits in one view
- 适合多个 coding agents 和 API platforms 的统一 dashboard

适用场景：

- 想要本机 dashboard
- 想统一监控多个 provider
- 不强依赖手机桌面卡片

不适用本项目的地方：

- 没有直接 Android widget 形态
- 对“手机上随时看额度节奏”的目标仍需要额外桥接

### 3.6 Codex Quota Monitor

链接：https://codexquotamonitor.github.io/

Codex Quota Monitor 是 Chrome 扩展，明确支持：

- session usage 5h
- weekly usage
- Codex credits
- auto background refresh
- toolbar badge
- 多语言
- open source

它通过已认证的 ChatGPT session 获取数据，自动每 10 分钟刷新。

适用场景：

- 经常在桌面浏览器查看
- 想避免自己维护 collector
- 接受 Chrome extension 形态

不适用本项目的地方：

- 标准 Android Chrome 不支持普通桌面扩展
- 不是安卓桌面卡片
- 多电脑聚合与数据过期提示不是核心形态

### 3.7 OwlMetric

链接：https://play.google.com/store/apps/details?id=com.abanoubnassem.owlmetric

OwlMetric 是 AI API spending tracker，支持 OpenAI、Anthropic、Google 等 API 花费监控，并有 Android/iOS/Web 入口。

它适合：

- OpenAI API 花费
- 团队预算
- provider/model 成本分析

不适合：

- Codex 会员 `5h / Weekly` 用量窗口
- ChatGPT/Codex 订阅额度剩余

结论：

OwlMetric 是 API 成本工具，不是 Codex 会员额度卡片的替代品。

## 4. 官方入口

OpenAI Help 文档说明，Codex credits 和 recent usage 可以在 ChatGPT web 的 `Codex Settings > Usage Dashboard` 查看。

链接：https://help.openai.com/en/articles/12642688-using-credits-for-flexible-usage-in-chatgpt-free-go-plus-pro

另有第三方文章记录，Codex Cloud analytics 中能看到 five-hour usage limit、weekly usage limit、remaining credits、reset time、auto top-up 和 usage breakdown。

链接：https://column.time7.jp/en/chatgpt/codex-usage-limits-cloud-analytics/

官方入口的优势：

- 数据权威
- 不需要第三方工具

缺点：

- 需要主动打开网页
- 不提供安卓桌面小组件
- 不是持续提醒工具

## 5. 是否继续自建

### 5.1 可以直接用现成工具的情况

如果使用场景变为以下任一项，可以优先用现成工具：

- Mac + iPhone：优先试 CodexBar
- Mac 桌面：试 CodexBar、MeterBar、Tally
- Windows 11 桌面：试 Wburn
- Chrome 浏览器：试 Codex Quota Monitor
- 多 provider 本机 dashboard：试 OpenUsage
- OpenAI API 花费：试 OwlMetric、LLMeter 等 API cost tracker

### 5.2 仍然需要本项目的情况

当前需求仍然需要 `Codex Quota Coach Lite`，因为目标是：

- Android 手机桌面卡片
- Codex 会员 `5h / Weekly` 额度
- 多电脑不同时在线
- 中央最新快照
- 数据过期提示
- 极简状态判断

现有工具没有完整覆盖这个组合。

## 6. 产品策略调整建议

保留当前 MVP，但避免扩大范围。

继续做：

- collector
- Quota Hub
- Android JSON 卡片数据源
- 数据过期提示
- 极简状态判断

不做：

- macOS 菜单栏工具
- Windows Widgets
- 浏览器扩展
- API 成本 dashboard
- 多 provider 聚合
- 历史趋势

原因：

这些方向已有更成熟工具覆盖，自建价值不高。

## 7. 最终建议

短期继续使用当前自建方案，因为它正好覆盖 Android 桌面卡片这一空缺。

同时保留一个替代方案：

- 如果后续改用 iPhone/Mac 生态，迁移到 CodexBar
- 如果只需要 Windows 桌面组件，迁移到 Wburn
- 如果只需要浏览器查看，迁移到 Codex Quota Monitor

因此，本项目不是重复造轮子，而是在现有工具没有覆盖的 Android 手机桌面场景中补齐最后一公里。
