# Tasker + KWGT 接入说明

本方案是临时兜底方案。项目现在已经提供原生 Android Widget，推荐优先使用：

[android-widget.md](android-widget.md)

如果暂时不想构建 APK，可以继续用 `Tasker + KWGT` 快速实现桌面卡片。

## 1. 确认手机能访问 Quota Hub

如果电脑端已经启动：

```bash
python3 -m quota_coach serve --host 0.0.0.0 --port 8765
```

安卓手机和电脑连接同一个 Wi-Fi 后，在手机浏览器打开：

```text
http://电脑局域网IP:8765/quota
```

如果可以看到一段 JSON，说明手机已经能读取额度数据。

也可以打开预览页面：

```text
http://电脑局域网IP:8765/
```

常见问题：

- 如果电脑端用 `--host 127.0.0.1` 启动，手机无法访问。
- 如果手机打不开，检查电脑和手机是否在同一网络。
- 如果使用校园网、公司网或热点隔离，建议改用 Tailscale 这类私有网络。
- 如果系统防火墙拦截，需要允许 `8765` 端口入站访问。

## 2. Tasker 拉取 JSON

创建一个每小时执行的 Task：

1. `Net -> HTTP Request`
2. Method: `GET`
3. URL: `http://你的Hub地址:8765/quota`
4. Output File: Tasker 本地文件，例如：

```text
/sdcard/Download/codex-quota.json
```

如果 Hub 只在局域网可访问，手机需要和 Hub 在同一个网络，或使用 Tailscale 这类私有网络。

## 3. Tasker 拆出变量

推荐让 Tasker 把 JSON 字段拆成几个简单变量，再发送给 KWGT。

在 `HTTP Request` 后添加 `Code -> JavaScriptlet`，代码示例：

```javascript
var data = JSON.parse(http_data);

var updated = data.updatedAt || "";
var updatedText = updated;
if (updated.indexOf("T") > -1) {
  updatedText = updated.split("T")[1].slice(0, 5);
}

setGlobal("CODEX_HEADLINE", data.headline || "暂无额度数据");
setGlobal("CODEX_5H_REMAINING", (data.primary && data.primary.remainingText) || "--");
setGlobal("CODEX_5H_STATUS", (data.primary && data.primary.statusText) || "--");
setGlobal("CODEX_WEEKLY_REMAINING", (data.weekly && data.weekly.remainingText) || "--");
setGlobal("CODEX_WEEKLY_STATUS", (data.weekly && data.weekly.statusText) || "--");
setGlobal("CODEX_UPDATED", updatedText);
setGlobal("CODEX_SOURCE", data.sourceDevice || "--");
```

如果你的 Tasker 版本里 `HTTP Request` 输出变量不是 `http_data`，可以在 HTTP Request 动作里把 `Output Variable` 显式设置为：

```text
%http_data
```

## 4. Tasker 发送变量到 KWGT

在同一个 Task 末尾添加多个插件动作：

```text
Plugin -> Kustom Widget -> Send Variable
```

建议发送这些变量：

| Kustom 变量名 | Tasker 变量 |
| --- | --- |
| `codex_headline` | `%CODEX_HEADLINE` |
| `codex_5h_remaining` | `%CODEX_5H_REMAINING` |
| `codex_5h_status` | `%CODEX_5H_STATUS` |
| `codex_weekly_remaining` | `%CODEX_WEEKLY_REMAINING` |
| `codex_weekly_status` | `%CODEX_WEEKLY_STATUS` |
| `codex_updated` | `%CODEX_UPDATED` |
| `codex_source` | `%CODEX_SOURCE` |

## 5. KWGT 显示字段

在 KWGT 中读取 Tasker 保存的 JSON 文件，建议显示这些字段：

```text
headline
primary.remainingText
primary.statusText
weekly.remainingText
weekly.statusText
updatedAt
sourceDevice
```

建议卡片文案：

```text
Codex

5h       80%   偏慢
Weekly   94%   闲置多

额度闲置偏多
17:34 · laptop-home
```

如果使用 `Kustom Widget -> Send Variable`，KWGT 文本公式可以写：

```text
$br(tasker, codex_headline)$
```

其他字段：

```text
$br(tasker, codex_5h_remaining)$
$br(tasker, codex_5h_status)$
$br(tasker, codex_weekly_remaining)$
$br(tasker, codex_weekly_status)$
$br(tasker, codex_updated)$ · $br(tasker, codex_source)$
```

## 6. Tasker 每小时刷新

创建 Profile：

```text
Profile -> Time
```

建议设置：

```text
From: 00:00
Every: 1 Hour
To: 23:59
```

绑定刚才创建的拉取 Task。

第一次配置完成后，可以手动运行一次 Task，确认 KWGT 卡片立即更新。

## 7. 临时替代方案

如果 KWGT 读取 JSON 不方便，可以先让 Tasker 把 JSON 字段拆成多个变量：

```text
%codex_headline
%codex_5h_remaining
%codex_5h_status
%codex_weekly_remaining
%codex_weekly_status
%codex_source_device
```

再在 KWGT 中直接显示 Tasker 变量。
