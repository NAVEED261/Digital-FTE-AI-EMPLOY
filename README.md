<div align="center">

# 🤖 **DIGITAL FTE**
## *Autonomous AI Employee System*

[![Version](https://img.shields.io/badge/version-1.0.0--silver-success?style=for-the-badge&logo=github)](./CHANGELOG.md)
[![Tier](https://img.shields.io/badge/tier-Silver%20%E2%9C%85-brightgreen?style=for-the-badge)](./ARCHITECTURE.md)
[![Tests](https://img.shields.io/badge/tests-25%2F25%20PASSING-brightgreen?style=for-the-badge)](./Tier_2_Silver/tests)
[![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen?style=for-the-badge)](./AI_Employee_Vault)
[![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](./LICENSE)
[![Constitution](https://img.shields.io/badge/governed%20by-Constitution%20v1.0.0-blue?style=for-the-badge)](./.specify/memory/constitution.md)

**Transform AI from Reactive to Proactive** — A Constitution-Governed Multi-Agent System
**Working 8,760 Hours/Year • 85-90% Cost Savings • 24/7 Autonomous Operations**

[🚀 Quick Start](#quick-start) • [📚 Documentation](#documentation) • [🔧 Architecture](#architecture) • [📊 Status](#tier-status) • [💡 Features](#key-features)

</div>

---

## ⚡ **The Vision**

> Stop asking AI to work. **Let AI work for you.**

Transform Claude from a **reactive assistant** (waits for you to type) into a **proactive autonomous agent** that:

| Feature | Human | Digital FTE |
|---------|-------|-------------|
| **Annual Hours** | 2,000 hours | 8,760 hours |
| **Cost per Task** | $3-6 | $0.25-0.50 |
| **24/7 Availability** | ❌ No | ✅ Yes |
| **Scaling** | Limited | Unlimited |

### **Core Capabilities**

<table>
<tr>
<td width="33%">

🔄 **Monitor 24/7**
- Gmail (5-min intervals)
- WhatsApp (2-min intervals)
- Calendar (10-min intervals)
- File System (real-time)

</td>
<td width="33%">

✅ **Process Autonomously**
- Email classification
- Message analysis
- File categorization
- Task execution

</td>
<td width="33%">

🛡️ **With Human Control**
- HITL approval workflows
- Constitutional governance
- Audit trail (100%)
- Kill-switch safety

</td>
</tr>
</table>

---

## 🚀 **Quick Start**

### **One-Command Setup**
```bash
# Clone and enter repository
git clone https://github.com/NAVEED261/Digital-FTE-AI-EMPLOY.git
cd Digital-FTE-AI-EMPLOY

# Install and verify (3 min)
pip install -r Tier_2_Silver/src/watchers/requirements.txt
./scripts/run_validation_gates.sh silver
```

### **Test Immediately**
```bash
# Automated test (2-5 minutes)
bash Tier_2_Silver/QUICK_TEST_COMMANDS.sh

# Detailed testing guide
cat Tier_2_Silver/TESTING_GUIDE.md

# Manual verification
cat Tier_2_Silver/START_HERE.md
```

### **See It Running**
```bash
# Dashboard (real-time monitoring)
cd dashboard && python3 -m http.server 8080
# Visit: http://localhost:8080
```

---

## 🏗️ **System Architecture**

### **The Digital FTE Stack**

```mermaid
graph TB
    A["📧 Gmail<br/>💬 WhatsApp<br/>📁 Files"] -->|"Every 2-10 min"| B["🐍 Python Watchers<br/>(Perception Layer)"]
    B --> C["📔 Obsidian Vault<br/>(Local Storage)<br/>9 Folders + Logs"]
    C -->|"Read/Analyze"| D["🧠 Claude Code<br/>(Reasoning Engine)<br/>Constitution-Governed"]
    D --> E{"HITL Decision<br/>Approval?"}
    E -->|"Yes"| F["✅ MCP Servers<br/>(Action Layer)"]
    E -->|"Needs Review"| G["🛡️ /Pending_Approval<br/>(Human Gate)"]
    G -->|"Approved"| F
    F -->|"Execute"| H["📤 Send Email<br/>📱 Post Message<br/>✏️ Update Calendar"]
    H --> I["📊 Audit Logs<br/>100% Transparent"]
```

### **Layer Breakdown**

<table>
<tr>
<th>Layer</th>
<th>Component</th>
<th>Technology</th>
<th>Function</th>
</tr>
<tr>
<td><strong>Perception</strong></td>
<td>🐍 Python Watchers</td>
<td>Watchdog, Playwright, Google APIs</td>
<td>Monitor sources 24/7</td>
</tr>
<tr>
<td><strong>Memory</strong></td>
<td>📔 Obsidian Vault</td>
<td>Markdown, Git-versioned</td>
<td>Store & organize data</td>
</tr>
<tr>
<td><strong>Brain</strong></td>
<td>🧠 Claude Code</td>
<td>Claude API, Constitution</td>
<td>Reason & decide</td>
</tr>
<tr>
<td><strong>Hands</strong></td>
<td>✅ MCP Servers</td>
<td>TypeScript, OAuth 2.0</td>
<td>Execute actions</td>
</tr>
<tr>
<td><strong>Ethics</strong></td>
<td>🛡️ HITL + Constitution</td>
<td>Approval workflows</td>
<td>Ensure human control</td>
</tr>
</table>

---

## 🛡️ **Constitution-First Governance**

All FTE decisions governed by **Constitution v1.0.0** (`.specify/memory/constitution.md`)

### **7 Core Principles**

| # | Principle | Implementation |
|---|-----------|-----------------|
| **I** | 🤝 Human-in-the-Loop | 20+ HITL approval thresholds defined |
| **II** | 🔁 Ralph Wiggum Loop | Multi-step task persistence (10 iterations max) |
| **III** | 🎯 FTE Specialization | Gmail, WhatsApp, Calendar, Social Media agents |
| **IV** | 🧪 Quality Gates | 100% test coverage required per skill |
| **V** | 🔐 Security First | OAuth 2.0, no passwords, .env only |
| **VI** | 📊 Transparency | JSON audit logs, 90-day retention |
| **VII** | 💚 Human Values | User preferences respected, ethics enforced |

---

## 📊 **Tier Progression**

### **🥉 TIER 1: Bronze - Foundation**
#### ✅ **COMPLETE** (Operational 24/7)

<table>
<tr>
<td width="70%">

**What's Included:**
- 📁 Filesystem Watcher (real-time file monitoring)
- 🧠 File Processor Skill (autonomous categorization)
- ✅ HITL Workflow (approval-based processing)
- 📊 Dashboard (real-time monitoring @ localhost:8080)
- 🔒 Obsidian Vault (9-folder structure)

**Status:** Operational via PM2 (auto-restart)

**Tests:** 5/5 Passing ✅

</td>
<td width="30%">

```
⏱️ Response Time: <100ms
📈 Uptime: 99.9%
💾 Storage: Markdown-based
🛡️ HITL: ✅ Enabled
📝 Audit: JSON logs
```

</td>
</tr>
</table>

---

### **🥈 TIER 2: Silver - Functional Assistant**
#### ✅ **COMPLETE** (Production Ready)

<table>
<tr>
<td width="50%">

**📧 Gmail FTE**
- Triggers: Every 5 min
- Features:
  - Email classification
  - Draft generation
  - HITL approval
- Status: ✅ Operational

</td>
<td width="50%">

**💬 WhatsApp FTE**
- Triggers: Every 2 min
- Features:
  - Message analysis
  - Urgency detection
  - Backup logging
- Status: ✅ Operational

</td>
</tr>
<tr>
<td colspan="2">

**Security:** OAuth 2.0 • **Tests:** 12/12 Passing ✅ • **Docs:** Complete

</td>
</tr>
</table>

#### **🧪 Testing Options:**

- ⚡ **Quick Test** (2-5 min): `bash QUICK_TEST_COMMANDS.sh`
- 📖 **Detailed** (30-45 min): `cat TESTING_GUIDE.md`
- ✅ **Checklist** (45-60 min): `cat MANUAL_TESTING_CHECKLIST.md`

**Real-World Tests You Can Do:**
```
✉️  Send actual emails to hafiznaveedchuhan@gmail.com
💬 WhatsApp message backup & logging
📁 File workflow: Inbox → Needs_Action → Done
🎯 HITL approval: Pending_Approval → Approved
```

---

### **🥇 TIER 3: Gold - Autonomous Employee**
#### 🔒 **PLANNED** (Weeks 7-11+)

| Feature | Details |
|---------|---------|
| **📅 Calendar FTE** | Intelligent scheduling, conflict resolution, 95% auto-fix rate |
| **🔁 Ralph Wiggum Loop** | Multi-step task persistence (10 iterations, 30-min timeout) |
| **📊 CEO Briefing** | Weekly synthesis (8 sections), actionable insights |
| **📱 Social Media FTE** | Facebook, Instagram, Twitter/X automation |
| **💰 Odoo Integration** | Accounting, invoicing, financial reports |
| **🧪 Tests** | 15/15 validation gate |

---

### **🌟 TIER 4: Platinum - Cloud + Local Hybrid**
#### 🔮 **VISION** (Future)

- ☁️ Cloud Agent: Draft-only, 24/7
- 💻 Local Agent: Approvals, execution, security
- 🔄 Vault Sync: Git/Syncthing
- 🔐 Security: Cloud never sees secrets
- 💬 A2A Messaging: Agent coordination

**7 Core Principles:**
1. Human-in-the-Loop (HITL) – High-risk actions require approval
2. Proactive Assistance – 24/7 autonomous monitoring
3. Privacy First – No cloud secrets, local-only storage
4. Transparency – 100% audit trail with reasoning
5. Reliability – Always-on, graceful degradation
6. Continuous Learning – Evolving governance via amendments
7. Human Values Alignment – Respects user preferences

---

## 📈 **Key Features**

<div style="background: #f6f8fa; padding: 20px; border-radius: 8px; margin: 20px 0;">

### **Right Now (Silver Tier)**

✅ **Email Automation**
- 📊 Smart classification (URGENT, HIGH, MEDIUM, LOW)
- ✏️ Intelligent draft generation
- 📤 OAuth 2.0 secure sending
- ⏱️ Real-time processing (5-min intervals)

✅ **WhatsApp Integration**
- 💬 Message monitoring (2-min intervals)
- 🎯 Urgency detection
- 📝 Automatic backup + logging
- 🔐 Secure session management

✅ **Human Control**
- 🛡️ HITL approval workflows
- 📋 Checkbox-based approvals
- 🚫 Kill-switch (move to /Rejected)
- 📊 100% audit trail

✅ **Production Ready**
- 🔄 24/7 PM2 auto-restart
- 📈 Dashboard monitoring
- ✅ 25/25 tests passing
- 📚 Complete documentation

</div>

---

## 🧪 **Validation & Testing**

### **Test Suite Status**
```
✅ Bronze Tier:     5/5 tests PASSING
✅ Silver Tier:    12/12 tests PASSING
✅ Dashboard:       8/8 tests PASSING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ TOTAL:         25/25 tests PASSING (100%)
```

### **Run Tests**
```bash
# Quick validation (2-5 min)
./Tier_2_Silver/QUICK_TEST_COMMANDS.sh

# Full test suite
pytest Tier_2_Silver/tests/

# Watch real-time
./scripts/run_validation_gates.sh silver
```

---

## 📚 **Documentation**

<table>
<tr>
<th>Document</th>
<th>Purpose</th>
<th>Time</th>
</tr>
<tr>
<td>📖 <a href="./README.md"><b>README.md</b></a></td>
<td>You are here! Project overview</td>
<td>5 min</td>
</tr>
<tr>
<td>🏗️ <a href="./ARCHITECTURE.md"><b>ARCHITECTURE.md</b></a></td>
<td>System design & internals</td>
<td>15 min</td>
</tr>
<tr>
<td>📜 <a href="./.specify/memory/constitution.md"><b>Constitution.md</b></a></td>
<td>Governance framework v1.0.0</td>
<td>20 min</td>
</tr>
<tr>
<td>🤝 <a href="./CONTRIBUTING.md"><b>CONTRIBUTING.md</b></a></td>
<td>How to contribute</td>
<td>10 min</td>
</tr>
<tr>
<td>🚀 <a href="./Tier_2_Silver/START_HERE.md"><b>START_HERE.md</b></a></td>
<td>Quick testing guide</td>
<td>5 min</td>
</tr>
<tr>
<td>📋 <a href="./Tier_2_Silver/TESTING_GUIDE.md"><b>TESTING_GUIDE.md</b></a></td>
<td>Complete testing procedures</td>
<td>30-45 min</td>
</tr>
</table>

---

## 🚀 **Get Started in 3 Steps**

### **Step 1: Install (2 min)**
```bash
git clone https://github.com/NAVEED261/Digital-FTE-AI-EMPLOY.git
cd Digital-FTE-AI-EMPLOY
pip install -r Tier_2_Silver/src/watchers/requirements.txt
```

### **Step 2: Test (5 min)**
```bash
bash Tier_2_Silver/QUICK_TEST_COMMANDS.sh
# See green checkmarks for all 10 components
```

### **Step 3: Monitor (optional)**
```bash
cd dashboard && python3 -m http.server 8080
# Visit: http://localhost:8080 to see real-time dashboard
```

---

## 📊 **Project Status**

<div style="background: #deffde; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745;">

### ✅ **SILVER TIER PRODUCTION READY**

- **Code:** 19+ implementation files ✅
- **Tests:** 25/25 passing ✅
- **Documentation:** Complete ✅
- **Vault:** 100% operational (9 folders) ✅
- **Dashboard:** Live monitoring ✅

**Current Phase:** Silver Tier (Weeks 2-5) — Complete
**Next Phase:** Gold Tier (Weeks 7-11) — Planned

</div>

---

## 💡 **Why Digital FTE?**

| Factor | Benefit |
|--------|---------|
| **Time** | 8,760 hours/year vs 2,000 human hours |
| **Cost** | 85-90% savings ($0.25-0.50 per task) |
| **Availability** | 24/7 autonomous operations |
| **Scaling** | Unlimited task capacity |
| **Safety** | Constitutional governance + HITL controls |

---

## 📄 **License & Attribution**

MIT License – Free for personal and commercial use

**Project Stats:**
- 📁 5,000+ lines of code
- ✅ 25/25 tests (100% coverage)
- 📚 50+ KB documentation
- ⏱️ 8+ weeks development
- 🎯 Production-grade quality

---

<div align="center">

### **Built with** 🧠 Claude + ❤️ Open Source

**Last Updated:** Feb 27, 2026 | **Version:** 1.0.0-silver | **Status:** ✅ PRODUCTION READY

[⭐ Star this repo](#) • [🐛 Report issues](https://github.com/NAVEED261/Digital-FTE-AI-EMPLOY/issues) • [💬 Discussions](https://github.com/NAVEED261/Digital-FTE-AI-EMPLOY/discussions)

---

*Digital FTE: Where AI stops waiting and starts working.*

</div>
