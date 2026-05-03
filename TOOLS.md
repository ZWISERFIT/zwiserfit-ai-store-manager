# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

### Hermes Dashboard Zero-Ops Access (Tristan 2026-05-01)

- **方案：** Nginx HTTPS 反向代理 + systemd 自动启动
- **访问地址：** `https://vm-0-11-ubuntu.tail80182d.ts.net:8443/`
- **备选地址：** `https://100.99.243.119:8443/`（Tailscale IP）
- **后端：** `127.0.0.1:9119`（Hermes Dashboard Web 服务）
- **Nginx 配置：** `/etc/nginx/sites-available/hermes-dashboard`
- **SSL 证书：** 由 `tailscale cert` 签发，存于 `/etc/nginx/hermes-*.pem`
- **证书续期：** `/etc/cron.weekly/tailscale-cert-renew`（每周自动续签）
- **Hermes 系统服务：** `hermes-dashboard.service`（已启用，自动启动）
- **铁律十六遵守：** 未使用 Tailscale Serve 的子路径代理，所有代理由独立 Nginx 端口（8443）完成

**恢复命令：**
- 查看服务状态：`systemctl status hermes-dashboard.service`
- 查看 Nginx 状态：`systemctl status nginx`
- 手动续期证书：`sudo /etc/cron.weekly/tailscale-cert-renew`
