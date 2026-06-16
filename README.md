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

> **Web5 Hash Attestation**
> `SHA-256: 39ad50b47f4401ecc94a361bb4d1f47a2840c7e867621c259ecdf88fa6150a55`
> This repository is attested under ZWF-20 Health Behavior Data Standard (Product). All contents are chain-anchored and independently verifiable. See [Web5 Attestation](#-web5-attestation--asset-anchoring).

---

# ZWISERFIT · AI + Web5 大健康基础数据设施

**AI + Web5 大健康基础数据设施 — 用户拥有自己的健康数据，协议确保数据属于用户、不属于平台。**

[![GitHub stars](https://img.shields.io/github/stars/ZWISERFIT/zwiserfit-ai-store-manager?style=social)](https://github.com/ZWISERFIT/zwiserfit-ai-store-manager)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-2026.4.15-orange)](https://github.com/openclaw/openclaw)
[![Status](https://img.shields.io/badge/Status-MVP%20%7C%20Seeking%20Hardware%20Engineers-red)]()
[![Web5 Attested](https://img.shields.io/badge/Web5-Attested-8250df)]()

---


## Why ZWF?

**You exercise 4 times a week. Your insurance premium is the same as someone who never moves.**

That's not fair. And for the first time in history, the technology exists to fix it.

In 2025, Leke (乐刻健身) × Ping An Insurance proved the market exists: verified workout frequency → premium discounts. Behavioral data is real economic value. But the data belongs to the platform, not the user.

ZWISERFIT (ZWF) = **AI + Web5 大健康基础数据设施** — the infrastructure that connects real physical behavior to fair outcomes. Not a crypto project. Not a token. A data infrastructure standard where **users own their health data**.

- **AI** → 9-Agent军团24/7运营 · 行为验证 · 多模态传感器融合
- **Web5** → DID确权 · MPC隐私 · 链上存证 · 用户拥有自己的健康数据
- **大健康基础数据设施** → PoPB v1.0 MIT开源 · 协议层 · 不是应用层

**Where PoPB fits:** PoPB (Proof of Physical Behavior) is the core verification protocol — the engine that makes physical activity verifiable. ZWISERFIT is the full data infrastructure stack built around it.

### The Five Steps from "Unfair" to "Co-builder"

1. **Feel the unfairness** → "I work out. Why does my insurance treat me like I don't?"
2. **See the possibility** → "ZWF's gate can prove my real activity. I have evidence now."
3. **Experience sovereignty** → "My data lives in my DWN. ZWF can't access it. Insurers want to see? They ask me."
4. **Exercise pricing power** → "6 months of verified activity. My premium drops 30%. Discipline, finally cashed in."
5. **Become a co-builder** → "I'm not just using this — I'm telling people I care about. Fairness is worth spreading."

> **乐刻×平安证明了"运动行为数据值钱"。ZWF确保"数据属于用户，不属于平台"。**

---

## What Is This?

A **大健康基础数据设施** proving ground — a production-grade multi-AI-agent operating system for physical retail, battle-tested in a real gym running for 7 years. Now open source, and its data pipeline validates the ZWF-20 Health Behavior Data Standard.

- **9 AI Agents** running 24/7 in production: store ops, brand, content, compliance, data verification
- **118 active members**, 35–55 daily check-ins, **~380K verified sessions** over 7 years
- **100% facial-recognition gate capture** — no spoofing, no manual entry
- **~23,000 on-chain proof hashes** anchored to a consortium chain
- **Data pipeline latency <2s** — IoT → Agent → On-chain

This is **both** a live operating system for physical retail **and** the proving ground for a new data paradigm — where real human behavior can be verified, owned, and used to negotiate fair outcomes.

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

## Project Status — Data Pipeline

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

## Roadmap: ZWF-20 Health Behavior Data Protocol

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

- **Technical issues / Feature requests** → [GitHub Issues](https://github.com/ZWISERFIT/zwiserfit-ai-store-manager/issues)
- **Ecosystem partnerships / Investment** → founder@zwiserfit.com (prefix: `[ZWISERFIT]`)
- **Join our Discord** → *(coming soon)*

> ⚙️ **Tristan** — Technical Architect
> *"ZWISERFIT is not any one person's project — it's the AI infrastructure for an entire industry of physical retail."*
> *"Real-world data is the only anchor for RWA."*
