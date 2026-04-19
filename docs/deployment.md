# 部署指南

## 环境要求

- Node.js 18+ 或更高版本
- npm 或 yarn 包管理器
- Git
- OpenClaw 环境（可选，用于AI代理功能）

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/zwiserfit/zwiserfit-ai-store-manager.git
cd zwiserfit-ai-store-manager
```

### 2. 安装依赖

```bash
npm install
# 或
yarn install
```

### 3. 配置环境变量

复制示例环境文件并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，根据实际情况设置以下变量：
- `OPENCLAW_API_KEY`: OpenClaw API密钥（如需AI功能）
- `DATABASE_URL`: 数据库连接字符串
- `PORT`: 服务端口（默认3000）

### 4. 初始化数据库

```bash
npm run db:migrate
npm run db:seed
```

### 5. 启动服务

开发模式：
```bash
npm run dev
```

生产模式：
```bash
npm run build
npm start
```

## Docker 部署

### 使用 Docker Compose

```bash
docker-compose up -d
```

### 构建自定义镜像

```bash
docker build -t zwiserfit-ai-store-manager .
docker run -p 3000:3000 --env-file .env zwiserfit-ai-store-manager
```

## 配置说明

### AI 代理配置

如需启用AI店铺管理功能，确保配置正确的OpenClaw设置：

1. 在 OpenClaw 控制台创建应用
2. 获取 API 密钥
3. 配置代理身份文件（AGENTS.md, SOUL.md）

### 店铺数据同步

配置第三方平台API密钥以同步店铺数据：
- 电商平台API（淘宝、京东、拼多多等）
- 支付接口
- 物流接口

## 故障排除

### 常见问题

1. **服务无法启动**
   - 检查端口是否被占用
   - 验证环境变量配置

2. **数据库连接失败**
   - 确认数据库服务运行状态
   - 检查连接字符串格式

3. **AI功能不可用**
   - 验证OpenClaw API密钥
   - 检查网络连接

### 日志查看

```bash
# 查看服务日志
npm run logs

# Docker容器日志
docker logs zwiserfit-ai-store-manager
```

## 更新与维护

### 更新到最新版本

```bash
git pull origin main
npm install
npm run db:migrate
npm restart
```

### 备份数据

定期备份数据库和配置文件：

```bash
# 数据库备份
npm run db:backup

# 配置文件备份
tar -czf config-backup.tar.gz .env AGENTS.md SOUL.md
```

## 支持与贡献

- 问题反馈：GitHub Issues
- 功能请求：GitHub Discussions
- 贡献代码：提交Pull Request

---

*最后更新：2026-04-19*