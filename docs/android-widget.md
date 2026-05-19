# 原生 Android Widget 使用说明

`Codex Quota Coach` 原生 Android Widget 是推荐的安卓端方案。它不依赖 Tasker 或 KWGT，安装 APK 后即可在桌面添加 Codex 额度卡片。

## 1. 前置条件

电脑端需要先启动 Quota Hub：

```bash
cd /path/to/codex-quota-coach
python3 -m quota_coach serve --host 0.0.0.0 --port 8765
```

手机需要能访问 Hub：

```text
http://电脑IP:8765/quota
```

如果手机浏览器能看到 JSON，说明网络链路正常。

## 2. 构建安装

当前工程在：

```text
codex-quota-coach/android/
```

如果本机有项目内工具链，脚本会自动使用：

```text
codex-quota-coach/.tools/
```

命令行构建 Debug APK：

```bash
cd /path/to/codex-quota-coach/android
./build-local.sh
```

产物位置：

```text
app/build/outputs/apk/debug/app-debug.apk
```

连接安卓手机并开启 USB 调试后，安装到手机：

```bash
cd /path/to/codex-quota-coach/android
./install-local.sh
```

也可以用 Android Studio 操作：

1. 打开 Android Studio
2. 选择 `Open`
3. 打开 `codex-quota-coach/android/`
4. 等待 Gradle Sync 完成
5. 连接安卓手机并开启 USB 调试
6. 点击 Run，安装到手机

## 3. App 配置

打开手机上的 `Codex Quota Coach` App。

填写：

```text
Hub URL: http://电脑IP:8765
Bearer Token optional: 留空或填写 Hub token
```

局域网示例：

```text
http://192.168.1.20:8765
```

如果走 Cloudflare Tunnel 公网方案，则填写：

```text
https://quota.example.com
```

并在 `Bearer Token optional` 中填写 `QUOTA_HUB_TOKEN`。

点击：

```text
保存
测试连接
刷新
```

测试成功后，App 会保存最近一次 quota snapshot。

## 4. 添加桌面 Widget

在安卓桌面：

1. 长按空白处
2. 选择 `Widgets` / `小组件`
3. 找到 `Codex Quota`
4. 拖到桌面

Widget 会显示：

```text
Codex

5h       80%   偏慢
Weekly   94%   闲置多

额度闲置偏多
17:34 · laptop-home
```

右上角刷新按钮可以手动触发一次刷新。

## 5. 刷新机制

Widget 使用 Android WorkManager：

- 后台每 1 小时刷新一次
- 点击刷新按钮会立即触发一次刷新
- 打开 App 后会注册周期刷新
- 添加 Widget 后会立即渲染缓存并触发刷新

如果刷新失败：

- 保留上次成功数据
- headline 显示 `数据待刷新`
- footer 显示失败摘要

## 6. 网络说明

首版默认支持明文 HTTP：

```text
http://IP:8765
```

App Manifest 已开启：

```text
usesCleartextTraffic=true
```

长期使用建议：

- 局域网使用时，确保手机和电脑在同一网络
- 跨网络使用时，优先用 Tailscale
- 公网访问时，推荐用 Cloudflare Tunnel：`docs/cloudflare-tunnel.md`
- 如果开启 Hub token，App 会发送：

```text
Authorization: Bearer <token>
```

## 7. 常见问题

### 手机打不开 Hub

检查电脑端是否用 `0.0.0.0` 启动：

```bash
python3 -m quota_coach serve --host 0.0.0.0 --port 8765
```

如果用了 `127.0.0.1`，只能电脑本机访问，手机访问不到。

### Widget 一直显示配置提示

打开 App，填写 Hub URL，点击 `测试连接`。成功后再回桌面刷新 Widget。

### Widget 显示数据待刷新

通常是：

- Hub 没启动
- 手机不在同一网络
- IP 变化
- token 不匹配
- 电脑防火墙拦截 8765 端口

### 后台刷新不准时

Android 省电策略可能延后 WorkManager 的周期任务。桌面刷新按钮仍可以手动触发。

## 8. 设计边界

首版只做：

- 单一 Hub URL 配置
- 所有 Widget 共用同一配置
- 5h / Weekly 展示
- 每小时刷新
- 手动刷新
- 失败保留上次数据

首版不做：

- 多账号
- 多 Widget 独立配置
- 二维码导入
- HTTPS 证书配置
- 通知栏常驻卡片
- Wear OS
