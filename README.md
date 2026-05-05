> 📖 **了解 ZWISERFIT 的品牌故事与愿景？** → [阅读品牌叙事版](./BRAND.md)

---

<!--
████████████████████████████████████████████████████████████████████
█                                                                  █
█  Web5 Product Case Hash Attestation · 产品案例哈希存证             █
█                                                                  █
█  SHA-256: 99e18bd7f8c50e56ebe3d71a692713711b55d07e042f29deddd     █
█           b33f5afa1f9a3                                            █
█                                                                  █
█  Repository: ZWISERFIT/zwiserfit-ai-store-manager                █
█  Asset Type: ZWF-20 Health Behavior Data Standard (Product)      █
█  Attested:   2026-05-05                                            █
█                                                                  █
████████████████████████████████████████████████████████████████████
-->

> ⚙️ **Web5 产品案例哈希存证**
> `SHA-256: 99e18bd7f8c50e56ebe3d71a692713711b55d07e042f29dedddb33f5afa1f9a3`
> 本仓库作为 ZWISERFIT 产品级案例（ZWF-20 健康行为数据标准产品仓），所有内容受 Web5 哈希存证锚定，确保代码、架构、数据与开源历史不可篡改、可独立核验。详见 [Web5 存证](#-web5-存证--资产锚定)。

---

# ZWISERFIT AI Store Manager
> **基于 AI Agent 多智能体协同，面向线下实体商业的轻量化自主运营管理操作系统**
> **技术定位：** 共建 ZWF-20 健康行为数据标准化开源协议层，落地实体场景合规 RWA 体系

依托 OpenClaw + Hermes Agent 双框架能力互补，实现「AI 调度 AI、AI 管理 AI、AI 迭代 AI」全链路闭环。
项目诞生于运动实体一线实战场景，由无代码背景实体创始人落地打磨、真实门店验证，全程开源开放。
为健身房、运动场馆、大健康服务类实体，提供
**可私有化部署、可规模化复制、可长期迭代**
的AI门店整体解决方案。

[![GitHub stars](https://img.shields.io/github/stars/ZWISERFIT/zwiserfit-ai-store-manager?style=social)](https://github.com/ZWISERFIT/zwiserfit-ai-store-manager)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-2026.4.15-orange)](https://github.com/openclaw/openclaw)
[![Hermes Agent](https://img.shields.io/badge/Hermes_Agent-v0.9.0-blue)](https://github.com/NousResearch/hermes-agent)
[![Status](https://img.shields.io/badge/Status-MVP%20%7C%20Seeking%20Hardware%20Engineers-red)]()
[![Web5 Attested](https://img.shields.io/badge/Web5-Attested-8250df)]()

---

## 🚧 Project Status · 项目状态

> **⚠️ MVP Phase — Actively tackling data pipeline challenges. Seeking contributors with hardware/IoT expertise.**
> **MVP阶段 — 正在攻克数据管道难题。急寻硬件/IoT背景贡献者。**

### 📊 Data Pipeline Status · 数据管道就绪状态

| Pipeline · 管道 | Status · 状态 | Blockers · 阻塞点 |
|------|:---:|---|
| Face recognition → server | 🔴 INACTIVE | ZWF-20 middleware not deployed |
| Member-device mapping | 🟡 TEST-ONLY | 118 test records, awaiting hardware integration |
| WeCom group interaction | 🟢 ACTIVE | — |
| GitHub daily ops commits | 🟢 ACTIVE | — |
| Sales/POS → server | 🔴 NOT CONNECTED | No POS integration yet |

### 🎯 Current Technical Priorities · 当前技术优先级

1. **FACE-001:** Deploy face recognition middleware to pipe ZWF-20 punch data to Linux server ≥ `help wanted`
2. **DATA-001:** Implement L1/L2/L3 data source tier system in all AI agent reporting ≥ `good first issue`
3. **MAP-001:** Migrate member-device mapping from test JSON to production database
4. **HALLU-001:** Enforce capability-archive pre-check before any AI agent generates reports

### 🆘 We Need · 我们急需

> **Embedded Systems / Hardware / IoT Engineers**
> **嵌入式系统 / 硬件 / IoT 工程师**

| Role · 角色 | What You'll Do · 你的任务 | Skills · 需要的技能 |
|------|------|------|
| **IoT Middleware Dev** | Connect ZWF-20 face terminal to Linux backend | RS-485, MQTT, Python/C, serial comm |
| **Edge Computing** | Build local data buffer for offline-first operation | Linux, SQLite, sync protocols |
| **Hardware Integration** | Document device protocols, build test harnesses | Hardware debugging, protocol reverse-engineering |

👉 **[View open issues →](https://github.com/ZWISERFIT/zwiserfit-ai-store-manager/issues)**
👉 **[Read our Constitution →](./CONSTITUTION.md)**

---

## 🌍 项目愿景与定位

ZWISERFIT AI Store Manager 的故事始于东莞下沉市场——

**一家连续亏损七年的健身房。**

创始人莫淑瑜，女性实体创业者，十年扎根一线。无技术团队、无行业靠山、无退路——仅凭一个人扛起前台、保洁、教练、运营、财务、推广全岗位。累计投入超千万，亲历 MBI 项目亏损 200 万、核心教练背叛亏损 100 万、自研定制系统投入 100 万、门店基建投入 200 万。

2026 年，AI 时代降临。完全不懂代码的她，依托 OpenClaw + Hermes 双框架，从零训练出一支完整的 AI 商业军团：

> **Shuyu 总指挥 + brand_lead + effect_lead + tech_lead + security_lead + Momo 数字店长**

这个仓库，是这支 AI 军团从真实门店跑出来的全部代码、架构与运营数据的开源存档。

### 我们的定位

| 维度 | 定位 |
|:---|:---|
| **技术定位** | ZWF-20 健康行为数据标准化开源协议层产品仓 |
| **商业定位** | 面向健身房/运动场馆/大健康实体的 AI 运营管理系统 |
| **生态定位** | RWA（Real World Assets）合规数据资产的真实世界锚点 |
| **治理定位** | 开源社区共建、贡献者主权、去中心化演进 |

我们不是资本包装的爽文叙事。我们是——
**一个普通实体创业者，借 AI 从七连亏损逆风翻盘的真实开源纪录。**

> 详细品牌故事 → [BRAND.md](./BRAND.md)

---

## ⚡ 5分钟快速上手

### 前提条件

- 一台 Linux 服务器（Ubuntu 22.04+ 推荐；树莓派 5 亦可）
- Node.js 20+ / Python 3.11+
- （可选）ZWF-20 人脸考勤终端

### 极简部署（单门店 Momo 数字店长）

```bash
# 1. 克隆仓库
git clone https://github.com/ZWISERFIT/zwiserfit-ai-store-manager.git
cd zwiserfit-ai-store-manager

# 2. 安装依赖
npm install          # OpenClaw 网关
pip install -r requirements.txt    # Hermes Agent 依赖

# 3. 初始化配置
cp config/momo.example.yaml config/momo.yaml
# 编辑 config/momo.yaml → 填入你的门店信息与企业微信凭证

# 4. 启动 AI 店长
npm run momo:start

# 5. 验证运行
curl http://localhost:9800/health
# 返回 {"status":"ok","agent":"Momo","store":"惠鑫店"} 即部署成功 ✅
```

### 多门店 Shuyu 总控部署

```bash
# 1. 在总部服务器执行
npm run shuyu:init
cp config/shuyu.example.yaml config/shuyu.yaml
# 编辑配置 → 填入所有门店 Momo 端点地址

# 2. 启动总控
npm run shuyu:start

# 3. 启动门店 Momo 集群（每台门店服务器）
npm run momo:start -- --store-id=store_001
npm run momo:start -- --store-id=store_002
```

### 下一步

- 📖 [Momo 完整部署指南](./deploy/momo.md)
- 🏢 [Shuyu 多门店部署指南](./deploy/shuyu.md)
- 🌐 [生态联盟加入指南](./ecosystem/join.md)

---

## 🧠 技术架构图｜AI 军团拓扑

```
                              ┌──────────────────────────────────────┐
                              │         Shuyu 全局总指挥中心            │
                              │    (OpenClaw Gateway · 集团级统筹)     │
                              │  ┌──────┐  ┌──────┐  ┌───────────┐  │
                              │  │战略规划│  │资源调度│  │跨门店协同 │  │
                              │  └──────┘  └──────┘  └───────────┘  │
                              └──────┬───────┬───────┬──────────────┘
                                     │       │       │
              ┌──────────────────────┼───────┼───────┼──────────────────────┐
              │              职能 AI 集群 · Functional AI Cluster             │
              │                                                              │
              │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────┐│
              │  │ brand_lead  │  │ effect_lead │  │ tech_lead   │  │security│
              │  │  品牌增长官  │  │  效果信任官  │  │ 技术架构官   │  │_lead  ││
              │  ├─────────────┤  ├─────────────┤  ├─────────────┤  │安全官  ││
              │  │· 内容SOP    │  │· 教练标准化  │  │· ZWF-20标准 │  ├──────┤│
              │  │· 社群运营   │  │· 体态追踪   │  │· RWA合规    │  │· 扫描 ││
              │  │· 品牌口碑   │  │· 效果归档   │  │· 数据治理   │  │· 监控 ││
              │  │· 生态导流   │  │· 课程管控   │  │· 系统运维   │  │· 日志 ││
              │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──┬───┘│
              │         └───────────────┼────────────────┼────────────┘     │
              └────────────────────────┼────────────────┼──────────────────┘
                                       │                │
                        ┌──────────────┴──────┐  ┌──────┴──────────────┐
                        │   📍 门店 001        │  │   📍 门店 002        │
                        │ ┌──────────────────┐ │  │ ┌──────────────────┐ │
                        │ │ Momo 数字店长     │ │  │ │ Momo 数字店长     │ │
                        │ │ (Hermes Agent)   │ │  │ │ (Hermes Agent)   │ │
                        │ ├──────────────────┤ │  │ ├──────────────────┤ │
                        │ │· 日常巡检        │ │  │ │· 日常巡检        │ │
                        │ │· 会员接待        │ │  │ │· 会员接待        │ │
                        │ │· 数据汇总        │ │  │ │· 数据汇总        │ │
                        │ │· 基础运维        │ │  │ │· 基础运维        │ │
                        │ │· 长记忆交互      │ │  │ │· 长记忆交互      │ │
                        │ └────────┬─────────┘ │  │ └────────┬─────────┘ │
                        │          │           │  │          │           │
                        │  ┌───────┴─────────┐ │  │  ┌───────┴─────────┐ │
                        │  │ ZWF-20 Terminal │ │  │  │ ZWF-20 Terminal │ │
                        │  │  人脸考勤·打卡   │ │  │  │  人脸考勤·打卡   │ │
                        │  └─────────────────┘ │  │  └─────────────────┘ │
                        └──────────────────────┘  └──────────────────────┘
                                   ⋮                          ⋮
                            门店 003...N                门店 003...N

        ═══════════════════════════════════════════════════════════════
         双引擎架构： OpenClaw (全局协同) × Hermes Agent (门店终端)
         所有门店 Momo 独立部署，离线自治；Shuyu 总部集群统一调度
        ═══════════════════════════════════════════════════════════════
```

### 架构关键特征

| 特征 | 说明 |
|:---|:---|
| **双引擎** | OpenClaw 负责全局协同与跨模块调度；Hermes 负责门店终端长记忆与自主决策 |
| **离线优先** | Momo 数字店长可在断网时独立运行，数据在网络恢复后异步同步 |
| **可扩展** | 新增门店只需部署新的 Momo 实例并注册到 Shuyu 总控 |
| **Human-in-the-Loop** | 所有战略决策层保留人工审批节点，AI 代理边界清晰 |
| **全链路可追溯** | 每次 AI 决策、每次数据变更全量记录，GitHub 每日公开归档 |

---

## 🤔 行业核心痛点
线下运动健康实体普遍存在经营同质化、运营强依赖人力的核心瓶颈：
- **人力依赖强**：核心服务与运营绑定个人，员工流失直接带走会员与核心资源
- **用工成本高**：薪资、提成、管理成本持续压缩实体利润，盈利结构脆弱
- **服务无标准**：交付质量、会员维护、门店运营高度依赖人为经验，难以复制
- **信任体系薄弱**：运动效果无法量化、服务流程不透明，复购与用户粘性难以沉淀

核心矛盾：门店规模越大，基础事务消耗越高，创始人深陷执行层，缺失战略规划、合规建设与生态布局能力。ZWISERFIT 以多AI智能体分工协作，替代重复人工；以标准化AI任务流统一服务流程；帮助创始人脱离一线执行，聚焦长期战略、合规管控与生态共建。

---

## 💎 产品核心价值：将市场教育标准化、自动化、可规模化
运动健康行业最高隐形成本，是长期且低效的持续市场教育。传统投放、地推、活动营销均为高消耗、低转化的成本模式。ZWISERFIT 核心解法：把用户认知、习惯养成、信任建立、自发传播全流程，拆解为**可量化、可自动化、可AI执行**的标准动作，完成从「成本消耗」到「内生增长」的模式升级。

| 教育环节 | 传统做法（成本中心） | ZWISERFIT AI 落地模式（增长引擎） | 负责 AI |
|:---|:---|:---|:---|
| **让用户"看见"** | 付费投流、高价买量、线下推广 | 门店真实运营内容自动沉淀，轻量化公域内容生产 | brand_lead |
| **让用户"相信"** | 活动营销、品牌背书、口头承诺 | 全周期体测数据可视化，训练效果量化归档 | effect_lead |
| **让用户"坚持"** | 人工督促、被动提醒、经验化维护 | 个性化运动预警、周期关怀、正向激励自动推送 | Momo |
| **让用户"传播"** | 现金裂变、短期营销活动 | 运动里程碑情感化运营，驱动用户自发口碑分享 | brand_lead + Momo |
| **让用户"沉淀价值"** | 简单会员等级、浅层权益 | 运动行为数据量化累积，兑换合规积分与生态权益 | tech_lead + Shuyu |

体系优势：门店运营、会员维护、用户增长不再依赖核心员工与创始人个人精力，由AI军团常态化落地，流程统一、数据可溯源、效果可量化，适配单店落地与连锁批量复制。

---

## 🧠 技术架构｜AI 军团完整体系
采用**双引擎分层架构**，两大框架能力互补、边界清晰：
- **OpenClaw**：全局协同底座，负责跨模块调度、多智能体任务编排、全域战略连接、集团级统筹
- **Hermes Agent**：门店终端底座，侧重长记忆留存、个性化交互、场景自主决策、精细化运营

### 三层AI层级架构

顶层｜Shuyu 全局总指挥 —— 战略调度、资源统筹、跨门店协同管控
中层｜职能 AI 集群 —— 标准化分工，覆盖内容、效果、数据、安全全维度
终端｜Momo 数字店长 —— 单门店落地执行、日常运营、会员精细化服务

### 职能AI集群职责

| 子AI角色 | 核心职责 | 落地价值贡献 |
|:---|:---|:---|
| **brand_lead** | 全平台内容规范、社群SOP、品牌口碑、生态导流 | 降低获客与运维成本，统一全品牌服务标准 |
| **effect_lead** | 教练标准化管理、课程管控、体态追踪、效果归档 | 数据化构建服务信任，抹平人员能力差距 |
| **tech_lead** | ZWF-20标准落地、系统运维、RWA合规、数据资产治理 | 实现健康数据标准化、脱敏化、可确权沉淀 |
| **security_lead** | 定时安全扫描、异常监控、全链路日志、风险预警与修复 | 保障系统、业务、用户数据全流程安全合规 |

### 门店核心终端
**Momo 数字店长（基于 Hermes Agent）**
单店独立部署运行，具备长效记忆、场景自适应、持续迭代能力，承接日常巡检、会员接待、数据汇总、基础运维等高频工作，实现门店轻量化无人值守运营。

---

## 🏰 六维核心壁垒｜技术+业务双闭环
以线下实体为根基，结合AI能力与行业数据标准，构建长期竞争壁垒：

| 护城河维度 | 行业痛点 | AI解决方案 | 生态合作价值 |
|:---|:---|:---|:---|
| **效果信任壁垒** | 运动效果不可量化，服务价值模糊 | effect_lead统一评估标准，Momo持续追踪体态数据 | 标准化专业交付，降低教练人力依赖 |
| **社交粘性壁垒** | 社群松散、复购低迷、流失率高 | brand_lead输出运营SOP，AI自动化社群维护 | 低成本搭建高粘性用户社区 |
| **多元增收壁垒** | 营收单一、坪效上限固化 | Shuyu数据分析+智能需求匹配 | 挖掘增值消费，优化门店盈利模型 |
| **数据资产壁垒(RWA)** | 线下数据零散、无法沉淀复用 | 遵循ZWF-20协议，脱敏采集+标准化归档 | 沉淀可持续增值的真实世界行为资产 |
| **行业标准壁垒** | 赛道无统一数据规范，行业碎片化 | 开源共建健康行为数据协议规范 | 抢占垂直行业标准化话语权 |
| **AI自进化壁垒** | 传统工具固化无迭代，运维风险高 | security_lead全链路安全防护+多智能体协同优化 | 系统随业务持续迭代，长期稳定增值 |

---

## 📊 路线图｜ZWF-20 健康数据协议落地规划
阶段化落地、目标明确、里程碑公开可溯源：

| 阶段 | 时间 | 核心任务 | 公开可验证里程碑 | 当前进度 |
|:---|:---|:---|:---|:---|
| **P1 标准筑基** | 2026 Q2-Q3 | 定稿ZWF-20健康数据行业标准 | 白皮书发布+千条样本数据开源 | 🟢 40% |
| **P2 应用上链** | 2026 Q3-Q4 | 合规健康数据资产确权与流通落地 | 链上资产凭证+合规资产方案落地 | 🟡 0% |
| **P3 生态扩展** | 2027全年 | 跨业态兼容，接入瑜伽/康复/球类场景 | 多业态数据互通，生态节点规模化扩容 | 🟡 0% |
| **P4 全域跃迁** | 2028+ | 跨生态联动，共建行业产业联盟 | 年度公开审计+垂直行业数据合约落地 | 🟡 0% |

---

## 🚀 快速落地指引
### 🏪 单店经营者
快速部署 Momo 数字店长，承接门店日常运营与会员服务，低成本解放人力。
👉 [查看 Momo 部署指南](./deploy/momo.md)

### 🏢 连锁品牌 / 产业投资人
部署 Shuyu 总控 + 职能AI集群 + 多门店Momo集群，实现多门店统一管控与标准同步。
👉 [查看 Shuyu 部署指南](./deploy/shuyu.md)

### 🌐 开源开发者 / 生态共建者
参与 ZWF-20 协议迭代、Agent能力优化、多场景适配开发，共建垂直大健康AI开源生态。
👉 [查看生态联盟加入指南](./ecosystem/join.md)

---

## 🔗 Web5 存证 · 资产锚定

> **ZWISERFIT 产品仓库已通过 Web5 哈希存证锚定，确保开源代码、架构设计与运营历史不可篡改、可独立核验。**

### 存证信息

| 属性 | 值 |
|:---|:---|
| **存证哈希（SHA-256）** | `99e18bd7f8c50e56ebe3d71a692713711b55d07e042f29dedddb33f5afa1f9a3` |
| **存证仓库** | `ZWISERFIT/zwiserfit-ai-store-manager` |
| **资产类型** | ZWF-20 健康行为数据标准 · 产品级案例 |
| **存证日期** | 2026-05-05 |
| **协议版本** | ZWF-20 v1.0-draft |

### 为什么需要 Web5 存证？

ZWISERFIT 的核心使命是**将真实世界健康行为数据封装为可确权、可追溯、可合规流通的 RWA 资产**。这意味着：

1. **代码即契约**：仓库中的每一行代码、每一次架构决策，通过哈希锚定形成不可篡改的公开记录
2. **数据主权可验证**：任何对 ZWF-20 标准的引用，均可通过本哈希回溯到原始协议版本
3. **开源信任基础设施**：存证不是监管要求——它是 ZWISERFIT 主动构建的信任底座，呼应 [Constitution Article III](./CONSTITUTION.md#article-iii-open-source-true-transparency--开源真透明)

### 如何独立核验

```bash
# 克隆仓库并核验
git clone https://github.com/ZWISERFIT/zwiserfit-ai-store-manager.git
echo "99e18bd7f8c50e56ebe3d71a692713711b55d07e042f29dedddb33f5afa1f9a3  README.md" | sha256sum -c
```

> ⚙️ 存证哈希随每次里程碑版本更新。当前版本对应的哈希见仓库根目录 `README.md` 注释头。

---

## 🤝 开源贡献规范

ZWISERFIT 不是"某人的项目"——它是实体健身行业的基础设施。你的每一次参与，都在塑造未来千万门店的运营标准。

### 我能贡献什么？

| 你的背景 | 推荐切入方式 |
|:---|:---|
| 🧠 零技术背景实体店主 | 提交真实需求 Issue、测试 Momo 部署、反馈使用体验 |
| 🐍 Python/后端 | 攻克数据管道（FACE-001、DATA-001）、Agent 能力优化 |
| 🌐 前端/全栈 | 门店看板 UI、会员端交互、管理后台 |
| 🔧 嵌入式/IoT | ZWF-20 人脸终端对接、边缘计算（**当前最急需！**） |
| 📝 文档 | 中英双语完善、部署教程、案例撰写 |
| 🔒 安全 | 安全审计、渗透测试、合规审查 |

### 快速参与

1. **提交 Issue**：使用 Bug/Feature 模板，附完整上下文
2. **提交 PR**：遵循 [CONTRIBUTING.md](./CONTRIBUTING.md) 开发规范与代码标准
3. **RFC 提案**：架构级变更先开 RFC Issue，至少 7 天讨论期
4. **参与数据贡献**：所有数据提交必须声明来源层级 `[L1/L2/L3]`（见 [Constitution Article I](./CONSTITUTION.md)）

> 📖 完整贡献指南 → [CONTRIBUTING.md](./CONTRIBUTING.md)
> ⚖️ 行为准则 → [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)
> 🏛️ 宪法级规范 → [CONSTITUTION.md](./CONSTITUTION.md)

---

## 📄 开源许可证
本项目采用 **MIT License** 开源协议。
原创架构、AI角色体系、业务模型与 ZWF-20 数据标准，为项目独家原创所有。

---

## 项目概述
ZWISERFIT AI Store Manager 是面向运动健康实体的**开源多智能体AI运营系统**。
依托一线门店实战经验，以AI协同实现降本增效，以ZWF-20标准化数据协议为长期底座，兼顾实体经营刚需与合规RWA生态布局，为千万实体创业者提供一套**低门槛、可落地、可进化、可共建**的AI数字化解决方案。

---

## 📬 联系与共建

- **技术问题 / 功能建议**：欢迎提交 [GitHub Issue](https://github.com/ZWISERFIT/zwiserfit-ai-store-manager/issues)
- **生态合作 / 投资接洽**：发送邮件至 founder@zwiserfit.com
- **加入生态联盟**：查看 [生态联盟加入指南](./ecosystem/join.md)

> ⚠ 邮件标题请注明 `[ZWISERFIT合作] - 您的公司/姓名`，以便快速识别并回复。

---

> ⚙️ **Tristan** — Technical Architect / 技术架构官
> *"ZWISERFIT 不是任何一个开源社区成员的项目——它是属于全体实体大健康产业的AI基础设施。"
> "真实世界的数据，才是RWA唯一的锚。"*
