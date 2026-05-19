# systemd user 后台服务

如果这台电脑常开，可以用 systemd user 托管三件事：

- `codex-quota-hub.service`：本机 Quota Hub 常驻
- `codex-quota-cloudflared.service`：Cloudflare Tunnel 常驻
- `codex-quota-submit.timer`：每 5 分钟提交一次最新 Codex snapshot

手机 Widget 只会读取 Hub 缓存，不会直接读取电脑上的 Codex 日志；因此电脑端必须持续 `submit`，否则手机刷新仍会显示旧 snapshot。

以下示例假设项目目录为：

```text
/opt/codex-quota-coach
```

## 1. 本机密钥文件

systemd 服务从这个文件读取 token：

```text
~/.config/codex-quota-coach/env
```

内容格式：

```ini
PROJECT_DIR=/opt/codex-quota-coach
QUOTA_HUB_PORT=8765
QUOTA_HUB_TOKEN=your-hub-token
CLOUDFLARED_TUNNEL_TOKEN=your-cloudflare-tunnel-token
```

权限应为仅当前用户可读写：

```bash
chmod 600 ~/.config/codex-quota-coach/env
```

## 2. 安装服务

项目模板位置：

```text
deploy/systemd-user/codex-quota-hub.service
deploy/systemd-user/codex-quota-cloudflared.service
deploy/systemd-user/codex-quota-submit.service
deploy/systemd-user/codex-quota-submit.timer
```

安装到当前用户：

```bash
mkdir -p ~/.config/systemd/user
cp deploy/systemd-user/codex-quota-hub.service ~/.config/systemd/user/
cp deploy/systemd-user/codex-quota-cloudflared.service ~/.config/systemd/user/
cp deploy/systemd-user/codex-quota-submit.service ~/.config/systemd/user/
cp deploy/systemd-user/codex-quota-submit.timer ~/.config/systemd/user/
systemctl --user daemon-reload
```

## 3. 启动

```bash
systemctl --user enable --now codex-quota-hub.service
systemctl --user enable --now codex-quota-cloudflared.service
systemctl --user enable --now codex-quota-submit.timer
systemctl --user start codex-quota-submit.service
```

如果希望用户服务在未登录图形桌面时也能运行，可以开启 linger：

```bash
loginctl enable-linger "$USER"
```

是否已开启可以检查：

```bash
loginctl show-user "$USER" -p Linger
```

## 4. 查看状态

```bash
systemctl --user status codex-quota-hub.service
systemctl --user status codex-quota-cloudflared.service
systemctl --user list-timers codex-quota-submit.timer
journalctl --user -u codex-quota-submit.service -n 50
```

## 5. 验证

本机：

```bash
curl -H "Authorization: Bearer $QUOTA_HUB_TOKEN" http://127.0.0.1:8765/quota
```

公网：

```bash
curl https://quota.example.com/health
curl -H "Authorization: Bearer $QUOTA_HUB_TOKEN" https://quota.example.com/quota
```
