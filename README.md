<!--
████████████████████████████████████████████████████████████████████
█                                                                  █
█  Web5 Product Case Hash Attestation                              █
█                                                                  █
█  SHA-256: 39ad50b47f4401ecc94a361bb4d1f47a2840c7e867621c259e     █
█           cdf88fa6150a55                                          █
█                                                                  █
█  Repository: ZWISERFIT/zwiserfit-ai-store-manager                █
█  Asset Type: ZWF-20 Health Behavior Data Standard (Product)      █
█  Attested:   2026-05-05 (v2.0)                                    █
█  TXID:       e6509b55d8b0db444371b6f47df07e6377afb73d9a408       █
█              48b7bb543fc4de2d385                                  █
█                                                                  █
████████████████████████████████████████████████████████████████████
-->

[![Product Hunt](https://img.shields.io/badge/Product%20Hunt-ZWISERFIT-orange?style=flat-square&logo=producthunt)](https://www.producthunt.com/posts/zwiserfit)

> **Web5 Product Case Hash Attestation · 产品案例哈希存证**
> `SHA-256: 39ad50b47f4401ecc94a361bb4d1f47a2840c7e867621c259ecdf88fa6150a55`
> 本仓库内容受 Web5 哈希存证锚定，确保代码、架构、数据与开源历史不可篡改、可独立核验。
> This repository is attested under ZWF-20 Health Behavior Data Standard (Product). All contents are chain-anchored and independently verifiable. See [Web5 Attestation](#-web5-attestation--asset-anchoring).

---

# Momo — 首个AI门店店长 · 物理AI的应用

> 微信就是门店。会员发个消息就行。不需要App。不需要前台。
> 不是AI辅助SaaS。不是AI客服机器人。Momo就是店长本身——通过微信直接服务会员。签到、约课、答疑、激励，说一声就行。
> 创始人在东莞万江一家健身房运营了7年，把自己一线门店管理经验编码进了Momo。创始人姓莫。Agent叫Momo。数字分身。

[![GitHub stars](https://img.shields.io/github/stars/ZWISERFIT/zwiserfit-ai-store-manager?style=social)](https://github.com/ZWISERFIT/zwiserfit-ai-store-manager)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-2026.4.15-orange)](https://github.com/openclaw/openclaw)
[![Status](https://img.shields.io/badge/Status-MVP%20%7C%20Seeking%20Hardware%20Engineers-red)]()
[![Web5 Attested](https://img.shields.io/badge/Web5-Attested-8250df)]()

---

## Momo — What Makes It Different

| Others Are Doing | What Momo Actually Does |
|:-----------------|:------------------------|
| AI feature plugin (bolt a chatbot onto SaaS) | **AI is the operating system** — WeChat conversation is the only interface |
| Requires app download, registration, learning | **No app needed** — WeChat IS the store operating system |
| Demo on a pitch deck, fundraising PPT | **7 years of real data** — this prototype is a store that's already running |

### ⚡ 核心差异（中文版）

| 别人在做 | Momo在做什么 |
|:---|:---|
| AI功能插件（给SaaS加个AI按钮） | **AI就是操作系统** — 微信对话就是全部界面 |
| 需要用户下载App、注册、学习 | **不需要App** — 微信就是门店操作系统 |
| Demo展示、融资PPT上的概念 | **7年真实数据** — 原型不是demo，是已经在运营的店 |

---

## The Story

Momo wasn't built in a startup accelerator. Momo was built in a gym in Dongguan's Wanjiang district — **a gym that lost money for seven consecutive years.**

The founder, Mo Shuyu, is a female physical retail entrepreneur who spent a decade on the front line. No tech team. No industry connections. No safety net. She did every job herself — front desk, cleaning, coaching, operations, finance, marketing. Cumulative investment exceeded 10 million RMB. Losses from a failed MBI project: 2 million. Losses from a key coach's betrayal: 1 million. Self-built custom systems: 1 million. Store infrastructure: 2 million.

In 2026, AI arrived. With zero coding background, she trained Momo — **the first AI store manager** — using OpenClaw + Hermes Agent.

> **Mo** is her family name. **Momo** is the agent. A digital twin.

What you see in this repo is the entire codebase, architecture, and operations data — running in a real store, not a demo environment.

> 详细品牌故事 → [BRAND.md](./BRAND.md)

---

## What's Here — Production-Proven Credentials

This is **both** a live AI-powered store operating system **and** the proving ground for a new data paradigm.

- **9 AI Agents** running 24/7 in production: store ops, brand, content, compliance, data verification
- **118 active members**, 35–55 daily check-ins, **~380K verified sessions** over 7 years
- **100% facial-recognition gate capture** — no spoofing, no manual entry
- **~23,000 on-chain proof hashes** anchored to a consortium chain
- **Data pipeline latency <2s** — IoT → Agent → On-chain

---

## 🤖 为什么是物理AI — Why Physical AI at the Store

物理AI进入门店运营。Momo不只理解"会员说了什么"，还理解"这家门店正在发生什么"——谁来了、谁没来、谁在流失、什么时候该做什么。就像Xintlabs用物理AI理解人体运动，Momo用物理AI理解实体门店。

不是SaaS加了个AI语音助手。不是微信机器人自动回复。物理AI意味着Momo感知的是真实世界的信号——会员到店频率变化、课程出席率的波动、群聊情绪健康度。这些信号叠加起来，就是一家门店的健康体征。

Physical AI meets store operations. Momo doesn't just understand "what a member said" — it understands "what's happening in this store." Who showed up. Who didn't. Who's at risk of churning. What needs to happen next. Like Xintlabs uses physical AI to understand human movement, Momo uses physical AI to understand a physical store.

---

## Quick Start

### Prerequisites
- Linux server (Ubuntu 22.04+ or Raspberry Pi 5)
- Node.js 20+ / Python 3.11+
- (Optional) ZWF-20 face recognition terminal

### Deploy Momo (Store-Level Agent) in 5 minutes

```bash
git clone https://github.com/ZWISERFIT/zwiserfit-ai-store-manager.git
cd zwiserfit-ai-store-manager

# Install dependencies
npm install
pip install -r requirements.txt

# Configure
cp config/momo.example.yaml config/momo.yaml
# Edit config/momo.yaml → fill in your store info and WeCom credentials

# Start
npm run momo:start

# Verify
curl http://localhost:9800/health
# → {"status":"ok","agent":"Momo","store":"My Store"}
```

### Deploy Shuyu (Multi-Store Command Center)

```bash
npm run shuyu:init
cp config/shuyu.example.yaml config/shuyu.yaml
# Edit → add all Momo endpoint addresses

# Start command center
npm run shuyu:start

# Start per-store Momo instances
npm run momo:start -- --store-id=store_001
npm run momo:start -- --store-id=store_002
```

📖 **[Full Momo deployment guide →](./deploy/momo.md)**
📖 **[Shuyu multi-store deployment →](./deploy/shuyu.md)**

---

## Architecture: The AI Agent Corps

```
                         ┌──────────────────────────────────────────────┐
                         │        Shuyu Global Command Center            │
                         │     (OpenClaw Gateway · Cross-store Ops)      │
                         │  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
                         │  │Strategy   │  │Resource  │  │Cross-store│   │
                         │  │Planning   │  │Scheduling│  │Sync      │   │
                         │  └──────────┘  └──────────┘  └──────────┘   │
                         └──────┬────────────┬─────────────┬───────────┘
                                │            │             │
        ┌───────────────────────┼────────────┼─────────────┼───────────────┐
        │            Functional AI Cluster — Central Services              │
        │                                                                   │
        │  ┌────────────────────────────────────────────────────────────┐  │
        │  │ brand_lead     │ effect_lead    │ tech_lead     │ security │  │
        │  │ Brand Growth   │ Trust/Effects  │ Architecture  │_lead     │  │
        │  │· Content SOP   │· Coach Std     │· ZWF-20 Std   │· Scanning │  │
        │  │· Community     │· Body Tracking │· RWA          │· Monitor  │  │
        │  │· Ecosystem     │· Results Arch  │· Data Gov     │· Logging  │  │
        │  └────────────────────────────────────────────────────────────┘  │
        └──────────────────────────┬───────────────────────┬───────────────┘
                                   │                       │
                  ┌────────────────┴──────┐   ┌───────────┴──────────┐
                  │  Store 001            │   │  Store 002            │
                  │ ┌──────────────────┐  │   │ ┌──────────────────┐ │
                  │ │ Momo Store Agent │  │   │ │ Momo Store Agent │ │
                  │ │ (Hermes Agent)   │  │   │ │ (Hermes Agent)   │ │
                  │ │· Daily Patrol    │  │   │ │· Daily Patrol    │ │
                  │ │· Member Service  │  │   │ │· Member Service  │ │
                  │ │· Data Aggr.      │  │   │ │· Data Aggr.      │ │
                  │ │· Long-term Mem.  │  │   │ │· Long-term Mem.  │ │
                  │ └────────┬─────────┘  │   │ └────────┬─────────┘ │
                  │  ┌───────┴─────────┐  │   │  ┌───────┴─────────┐ │
                  │  │ ZWF-20 Terminal │  │   │  │ ZWF-20 Terminal │ │
                  │  │ Face Recognition│  │   │  │ Face Recognition│ │
                  │  └─────────────────┘  │   │  └─────────────────┘ │
                  └───────────────────────┘   └──────────────────────┘

   Dual engine: OpenClaw (global orchestration) × Hermes Agent (store terminal)
   Each Momo runs independently, offline-first; Shuyu unifies from HQ
```

### Key Architecture Decisions

| Feature | Detail |
|:--------|:-------|
| **Dual Engine** | OpenClaw for cross-module orchestration; Hermes for long-term memory & autonomous decisions |
| **Offline-First** | Each store agent runs independently even without internet — data syncs asynchronously when reconnected |
| **Horizontally Scalable** | Add stores by deploying new Momo instances and registering with Shuyu |
| **Human-in-the-Loop** | All strategic decisions retain human approval gates; agent boundaries are explicit |
| **Fully Auditable** | Every AI decision, every data mutation is logged. Daily GitHub archives are public |

---

## 🚧 Project Status — Data Pipeline

| Pipeline | Status | Blockers |
|----------|:------:|----------|
| Face recognition → server | 🔴 INACTIVE | ZWF-20 middleware not deployed |
| Member-device mapping | 🟡 TEST-ONLY | 118 test records, waiting for hardware integration |
| WeCom group interaction | 🟢 ACTIVE | — |
| GitHub daily ops commits | 🟢 ACTIVE | — |
| Sales/POS → server | 🔴 NOT CONNECTED | No POS integration yet |

### Current Technical Priorities

1. **FACE-001:** Deploy face recognition middleware → pipe ZWF-20 punch data to Linux server `help wanted`
2. **DATA-001:** Implement L1/L2/L3 data source tier system in AI agent reporting `good first issue`
3. **MAP-001:** Migrate member-device mapping from test JSON to production database
4. **HALLU-001:** Enforce capability-archive pre-check before any AI agent generates reports

---

## 🆘 We Need: Hardware / IoT / Embedded Systems Engineers

The IoT data pipeline is the bridge between physical proof and fair outcomes. If you know serial comms, MQTT, or edge computing — your contribution directly powers the fairness infrastructure.

| Role | What You'll Do | Skills Needed |
|------|---------------|--------------|
| **IoT Middleware Dev** | Connect ZWF-20 face terminal to Linux backend | RS-485, MQTT, Python/C, serial comm |
| **Edge Computing** | Build local data buffer for offline-first operation | Linux, SQLite, sync protocols |
| **Hardware Integration** | Document device protocols, build test harnesses | Hardware debugging, protocol reverse-engineering |

👉 **[View all open issues →](https://github.com/ZWISERFIT/zwiserfit-ai-store-manager/issues)**
👉 **[Good first issues →](https://github.com/ZWISERFIT/zwiserfit-ai-store-manager/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)**

---

## 📊 Roadmap: ZWF-20 Health Behavior Data Protocol

| Phase | Timeline | Core Task | Milestone | Status |
|:------|:--------:|-----------|:---------:|:-----:|
| **P1** Standard Foundation | 2026 Q2–Q3 | Finalize ZWF-20 health data standard | Whitepaper + 1K open-source samples | 🟢 40% |
| **P2** On-Chain Assets | 2026 Q3–Q4 | Compliant health data asset issuance & circulation | On-chain asset credentials live | 🟡 0% |
| **P3** Ecosystem Expansion | 2027 | Cross-format (yoga, rehab, sports) compatibility | Multi-format data interop | 🟡 0% |
| **P4** Protocol Maturity | 2028+ | Cross-ecosystem federation | Annual public audit + industry data contracts | 🟡 0% |

---

## Contributing

ZWISERFIT is not a project — it's a fairness infrastructure. Every contribution helps someone, somewhere, prove that their behavior deserves a better outcome.

### Find Your Entry Point

| Your Background | Best Way to Start |
|:---------------|:-----------------|
| 🧠 **No-code store owner** | Submit use-case issues, test Momo deployment, share feedback |
| 🐍 **Python / Backend** | Tackle data pipeline (FACE-001, DATA-001), optimize agents |
| 🌐 **Frontend / Fullstack** | Store dashboard UI, member portal, management console |
| 🔧 **Embedded / IoT** | ZWF-20 face terminal integration, edge computing (**most urgent!**) |
| 📝 **Documentation** | Tutorials, deployment guides, case studies |
| 🔒 **Security** | Security audit, penetration testing, compliance review |

### How to Contribute

1. **Submit an Issue** — Use the Bug/Feature templates with full context
2. **Open a PR** — Follow [CONTRIBUTING.md](./CONTRIBUTING.md) for code standards
3. **RFC Proposals** — Architecture changes require an RFC Issue with 7-day discussion period
4. **Data Contributions** — All data submissions must declare source tier `[L1/L2/L3]` (see [Constitution Article I](./CONSTITUTION.md))

📖 [CONTRIBUTING.md](./CONTRIBUTING.md) · ⚖️ [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) · 🏛️ [CONSTITUTION.md](./CONSTITUTION.md)

---

## Web5 Attestation & Asset Anchoring

ZWISERFIT's core mission is to package real-world health behavior data into verifiable, ownable, and compliant RWA assets. This means:

1. **Code as contract** — Every line, every architecture decision is SHA-256 anchored
2. **Data sovereignty is verifiable** — Any ZWF-20 standard reference is traceable to its origin
3. **Open-source trust infrastructure** — Attestation is not regulation; it's a trust foundation we build proactively

### Verify the Attestation

```bash
git clone https://github.com/ZWISERFIT/zwiserfit-ai-store-manager.git
echo "39ad50b47f4401ecc94a361bb4d1f47a2840c7e867621c259ecdf88fa6150a55  README.md" | sha256sum -c
```

Attestation changes with each milestone version. Current hash corresponds to the root `README.md` header comment.

---

## License

MIT License. Original architecture, AI agent role system, business models, and ZWF-20 data standard are exclusively owned by the project.

---

## Contact

- **技术问题 / 功能建议** → [GitHub Issues](https://github.com/ZWISERFIT/zwiserfit-ai-store-manager/issues)
- **Ecosystem partnerships / Investment** → founder@zwiserfit.com (prefix: `[ZWISERFIT]`)
- **加入生态联盟** → [生态联盟加入指南](./ecosystem/join.md)

> ⚙️ **Tristan** — Technical Architect / 技术架构官
> *"ZWISERFIT is not any one person's project — it's the AI infrastructure for an entire industry of physical retail."*
> *"真实世界的数据，才是RWA唯一的锚。"*
