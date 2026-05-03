# 📊 GitHub 开源运营仪表盘 / Open Source Operations Dashboard

> **维护人：** Baron（品牌增长官）  
> **创建日期：** 2026-05-03  
> **更新频率：** 每日 20:00 CST 自动刷新  
> **数据来源：** GitHub API (https://api.github.com/repos/ZWISERFIT/*)

---

## 一、核心指标总览 / Core KPIs

| 指标 | ZWISERFIT/ZWISERFIT | ZWISERFIT/zwiserfit-ai-store-manager | 目标 |
|------|:---:|:---:|------|
| ⭐ Stars | `{stars_org}` | `{stars_tech}` | 50+ |
| 🍴 Forks | `{forks_org}` | `{forks_tech}` | 10+ |
| 👀 Weekly Views | `{views_org}` | `{views_tech}` | 500+ |
| 🔍 Unique Visitors | `{uniques_org}` | `{uniques_tech}` | 200+ |
| 📋 Open Issues | `{issues_org}` | `{issues_tech}` | 管理至<5 |
| 🔀 Open PRs | `{prs_org}` | `{prs_tech}` | 管理至<3 |

> `{placeholder}` = 每日自动从 GitHub API 拉取

---

## 二、Issue/PR 解决率 / Resolution Rate

### 本周解决率

| 周期 | 新开 Issue | 已关闭 Issue | 解决率 | 新开 PR | 已合并 PR | 合并率 |
|------|:---:|:---:|:---:|:---:|:---:|:---:|
| 本周 (W18) | — | — | —% | — | — | —% |
| 上周 (W17) | — | — | —% | — | — | —% |
| 累计 | 4 | 0 | 0% | 0 | 0 | —% |

### 标签分布

| 标签 | Issue 数量 | 说明 |
|------|:---:|------|
| `help wanted` | 3 | FACE-001, MAP-001, (FACE-001) |
| `good first issue` | 3 | DATA-001, MAP-001, HALLU-001 |
| `high-priority` | 1 | FACE-001 |
| `hardware` | 1 | FACE-001 |
| `ai-agents` | 2 | DATA-001, HALLU-001 |

---

## 三、贡献者转化漏斗 / Contributor Conversion Funnel

| 阶段 | 人数 | 转化率 | 说明 |
|------|:---:|:---:|------|
| 👀 浏览者 (Weekly Unique Visitors) | `{uniques_sum}` | 100% | 基线 |
| ⭐ Star 用户 | `{stars_sum}` | — | 兴趣信号 |
| 🍴 Fork 用户 | `{forks_sum}` | — | 行动信号 |
| 📋 Issue 提交者 | 0 | 0% | 首次互动 |
| 🔀 PR 提交者 | 0 | 0% | 代码贡献 |
| ✅ 合并贡献者 | 0 | 0% | 最终转化 |
| 🔄 重复贡献者 | 0 | 0% | 社区留存 |

### 新贡献者追踪

| 日期 | GitHub 用户名 | 首次互动 | 互动类型 | 当前状态 | 备注 |
|------|------|------|------|------|------|
| — | — | — | — | — | 暂无外部贡献者 |

---

## 四、社区健康度 / Community Health

| 指标 | 当前值 | 目标 | 状态 |
|------|:---:|------|:---:|
| 平均 Issue 首次响应时间 | — | <48h | ⏳ |
| 平均 PR 审查时间 | — | <72h | ⏳ |
| `good first issue` 有明确技术上下文 | ✅ 4/4 | 100% | 🟢 |
| CONSTITUTION.md 存在 | ✅ | ✅ | 🟢 |
| README 有双语项目状态 | ✅ | ✅ | 🟢 |
| 贡献指南存在 | ❌ | 创建中 | 🔴 |

---

## 五、增长引擎活动 / Growth Engine Activities

### 内容发布日历

| 日期 | 内容 | 平台 | 状态 | 关联 |
|------|------|------|:---:|------|
| 2026-05-04 | 「AI军团的诞生：从东莞到GitHub」Ep.1 | GitHub Discussions + 推特 | 📝 策划中 | Ep.1/5 |
| 2026-05-07 | 「AI军团的诞生」Ep.2: 零代码创始人的技术选型 | 同上 | ⏳ | Ep.2/5 |
| 2026-05-11 | ZWISERFIT Challenge #1 启动 | GitHub Issue | ⏳ | 见挑战赛方案 |
| 2026-05-14 | 「AI军团的诞生」Ep.3: AI数据脑补事故全记录 | 同上 | ⏳ | Ep.3/5 |

### 渠道覆盖

| 平台 | 账号 | 状态 | 最新内容 |
|------|------|:---:|------|
| GitHub | ZWISERFIT | 🟢 | CONSTITUTION.md + 4 Issues |
| 推特/X | @ZWISERFIT | 🔴 未创建 | — |
| 小红书 | — | 🔴 未创建 | — |
| 抖音 | — | 🔴 未创建 | — |
| 企微群 | 惠鑫门店群 | 🟢 | Momo日常运营 |

---

## 六、数据刷新脚本

```bash
#!/bin/bash
# github-dashboard-refresh.sh
# 每日由 cron 触发，刷新本仪表盘

TOKEN=$(cat ~/.openclaw/.env | grep GITHUB_TOKEN | cut -d= -f2)
REPOS=("ZWISERFIT/ZWISERFIT" "ZWISERFIT/zwiserfit-ai-store-manager")

for repo in "${REPOS[@]}"; do
  echo "Refreshing $repo..."
  # Stars, forks, open issues
  DATA=$(curl -s -H "Authorization: token $TOKEN" "https://api.github.com/repos/$repo")
  STARS=$(echo "$DATA" | python3 -c "import sys,json; print(json.load(sys.stdin).get('stargazers_count',0))")
  FORKS=$(echo "$DATA" | python3 -c "import sys,json; print(json.load(sys.stdin).get('forks_count',0))")
  ISSUES=$(echo "$DATA" | python3 -c "import sys,json; print(json.load(sys.stdin).get('open_issues_count',0))")
  
  # Traffic views
  VIEWS=$(curl -s -H "Authorization: token $TOKEN" "https://api.github.com/repos/$repo/traffic/views")
  COUNT=$(echo "$VIEWS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('count',0))")
  UNIQUES=$(echo "$VIEWS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('uniques',0))")
  
  echo "  Stars=$STARS Forks=$FORKS Issues=$ISSUES Views=$COUNT Uniques=$UNIQUES"
done
```

---

> **下次更新：** 2026-05-04 20:00 CST  
> **负责人：** Baron（品牌增长官）  
> *本仪表盘为作战地图，不是装饰品。数据缺失 = 情报缺失。*
