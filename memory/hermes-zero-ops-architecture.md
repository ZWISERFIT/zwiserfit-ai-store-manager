# Hermes Dashboard Zero-Ops 访问架构

**日期：** 2026-05-01
**架构师：** Tristan（企业IT架构师）
**状态：** ✅ 已实施验证

---

## 方案评估

### 方案一：Tailscale 子域名服务 ❌（不可行）

**评估过程：**
1. Tailscale Serve 绑定到机器 FQDN `vm-0-11-ubuntu.tail80182d.ts.net`，不支持任意子域名
2. `--set-path` 选项（如 `tailscale serve --bg --set-path /hermes 127.0.0.1:9119`）虽然可用，但铁律十六禁止在已有 Tailscale Serve 上添加子路径
3. 即使尝试不同的方案，所有 Tailscale Serve 方案都与现有 OpenClaw 服务共享 443 端口

**结论：** Tailscale 方案因架构限制（无子域名支持）和铁律十六（禁止子路径）双重约束导致不可行。

### 方案二：Nginx 反向代理 ✅（已实施）

**架构设计：**
- Nginx 监听 8443 端口（独立端口，不与 Tailscale 443 冲突）
- 使用 `tailscale cert` 签发的有效 TLS 证书（Tailscale 原生信任）
- 反向代理到 `http://127.0.0.1:9119`（Hermes Dashboard）
- Hermes Dashboard 由 `hermes-dashboard.service` systemd 服务管理

**验证结果：**
| 检查项 | 结果 |
|--------|------|
| 主页面 (/) | ✅ HTTP 200 |
| JS 资源 /assets/*.js | ✅ HTTP 200, 正确 MIME type |
| CSS 资源 /assets/*.css | ✅ HTTP 200, 正确 MIME type |
| API 端点 /api/status | ✅ 返回 JSON, Hermes v0.9.0 |
| TLS 证书 | ✅ Tailscale 签发, 有效期至 2026-07-26 |
| 服务重启恢复 | ✅ Hermes + Nginx 均自动恢复正常 |
| OpenClaw 冲突 | ✅ 未受影响, 继续可用 |

---

## 已实施的配置

### 1. Nginx 配置 (`/etc/nginx/sites-available/hermes-dashboard`)

```nginx
server {
    listen 8443 ssl http2;
    listen [::]:8443 ssl http2;

    server_name vm-0-11-ubuntu.tail80182d.ts.net hermes-dashboard;

    ssl_certificate /etc/nginx/hermes-cert.pem;
    ssl_certificate_key /etc/nginx/hermes-key.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:9119;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 2. TLS 证书续期脚本 (`/etc/cron.weekly/tailscale-cert-renew`)

```bash
#!/bin/bash
tailscale cert --cert-file /etc/nginx/hermes-cert.pem \
    --key-file /etc/nginx/hermes-key.pem \
    vm-0-11-ubuntu.tail80182d.ts.net
nginx -t && nginx -s reload
```

### 3. 系统服务

- **hermes-dashboard.service** — 已启用、自动启动
- **nginx** — 已启用、自动启动

---

## 访问方式

| 方式 | 地址 | 说明 |
|------|------|------|
| **推荐** | `https://vm-0-11-ubuntu.tail80182d.ts.net:8443/` | Tailscale 主机名，需要安装 Tailscale |
| 备选 | `https://100.99.243.119:8443/` | Tailscale IP，稳定但 IP 可能变化 |
| 回退 | SSH 隧道 `localhost:9119` | 传统方式，仍可用 |

所有地址：
- ✅ 无需在浏览器输入 SSH 命令
- ✅ 自动 HTTPS 证书（浏览器信任）
- ✅ 服务器重启后自动恢复（无需人工干预）
- ✅ 与现有 OpenClaw 服务无冲突

---

## 铁律十六遵守声明

本方案**完全遵守铁律十六**：
- ❌ 未使用 `tailscale serve --set-path /hermes`（禁止的子路径方式）
- ✅ 使用独立 Nginx 进程 + 独立端口 8443
- ✅ 每个服务独立运行，互不依赖
- ✅ 使用 `tailscale cert` 获取有效 TLS 证书在 8443 端口中止

---

*文档供 Stella 审计使用。*
