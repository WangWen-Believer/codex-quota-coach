# Cloudflare Tunnel 公网访问方案

目标地址：

```text
https://quota.example.com
```

这条路径用于手机不在同一局域网时访问 Quota Hub。Cloudflare Tunnel 不要求家庭宽带有公网 IP，也不需要路由器端口转发。

## 1. 前置条件

- 你的域名已添加到 Cloudflare
- 域名 NS 已切到 Cloudflare
- 电脑能正常访问互联网
- 本机 Quota Hub 能正常读取 Codex snapshot

项目内已经安装：

```text
.tools/cloudflared/cloudflared
```

检查版本：

```bash
cd /path/to/codex-quota-coach
.tools/cloudflared/cloudflared --version
```

## 2. 准备两个 token

这里有两个 token，含义不同，不要混用：

| 名称 | 用途 | 放在哪里 |
| --- | --- | --- |
| `QUOTA_HUB_TOKEN` | 保护 `/quota` 和 `/snapshot` | Hub、submit、Android App |
| `CLOUDFLARED_TUNNEL_TOKEN` | 让本机连接 Cloudflare Tunnel | 只放在电脑端 |

生成一个 Hub token：

```bash
openssl rand -hex 24
```

后续用这个值替换示例里的 `your-hub-token`。

## 3. 启动带保护的 Hub

公网模式下 Hub 只绑定本机回环地址，让外部只能经过 Cloudflare Tunnel 访问：

```bash
cd /path/to/codex-quota-coach
export QUOTA_HUB_TOKEN="your-hub-token"
./scripts/run-hub-public.sh
```

另开一个终端，提交一次本机 snapshot：

```bash
cd /path/to/codex-quota-coach
export QUOTA_HUB_TOKEN="your-hub-token"
./scripts/submit-local.sh
```

本机验证：

```bash
curl -H "Authorization: Bearer $QUOTA_HUB_TOKEN" http://127.0.0.1:8765/quota
```

## 4. 在 Cloudflare 创建 Tunnel

在 Cloudflare Dashboard 中：

1. 进入 `Zero Trust`
2. 打开 `Networks` / `Tunnels`
3. 选择 `Create a tunnel`
4. Connector 类型选择 `Cloudflared`
5. 名称填写：

```text
codex-quota-coach
```

创建后，Cloudflare 会给出一条安装或运行命令，里面包含一段很长的 tunnel token。保存这个 token，作为：

```text
CLOUDFLARED_TUNNEL_TOKEN
```

## 5. 配置 Public Hostname

在刚创建的 Tunnel 里添加 route：

```text
Subdomain: quota
Domain: example.com
Service Type: HTTP
Service URL: localhost:8765
```

最终公开地址就是：

```text
https://quota.example.com
```

## 6. 启动 Tunnel

在电脑端运行：

```bash
cd /path/to/codex-quota-coach
export CLOUDFLARED_TUNNEL_TOKEN="your-cloudflare-tunnel-token"
./scripts/run-cloudflare-tunnel.sh
```

验证公网健康检查：

```bash
curl https://quota.example.com/health
```

验证受保护的 quota：

```bash
curl -H "Authorization: Bearer $QUOTA_HUB_TOKEN" https://quota.example.com/quota
```

如果不带 token 访问 `/quota`，应该返回：

```json
{
  "ok": false,
  "error": "Unauthorized"
}
```

## 7. Android App 配置

手机端 App 填：

```text
Hub URL: https://quota.example.com
Bearer Token optional: your-hub-token
```

注意这里填的是 `QUOTA_HUB_TOKEN`，不是 Cloudflare Tunnel token。

## 8. 长期运行建议

首轮测试可以手动开两个终端：

1. `./scripts/run-hub-public.sh`
2. `./scripts/run-cloudflare-tunnel.sh`

确认稳定后，使用 systemd user 托管：

```text
codex-quota-hub.service
codex-quota-cloudflared.service
codex-quota-submit.timer
```

维护方式见：

```text
docs/systemd-user.md
```

## 9. 故障排查

### `/health` 能访问，`/quota` 返回 Unauthorized

Android App 没填 token，或 token 填错。

### `/quota` 返回 No snapshot stored yet

Hub 里还没有快照，运行：

```bash
export QUOTA_HUB_TOKEN="your-hub-token"
./scripts/submit-local.sh
```

### Cloudflare 显示 502 / Bad Gateway

通常是本机 Hub 没启动，或 Cloudflare route 的 Service URL 不是 `localhost:8765`。

### 手机端一直刷新失败

先用手机浏览器打开：

```text
https://quota.example.com/health
```

能看到 `{"ok": true}` 后，再检查 App 里的 Hub URL 和 token。
