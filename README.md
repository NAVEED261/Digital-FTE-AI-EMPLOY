# 🤖 Digital FTE (Full-Time Equivalent)

**Autonomous AI Employee System for Personal & Business Affairs**

[![Version](https://img.shields.io/badge/version-0.1.0--bronze-brightgreen)](./CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
[![Bronze Tier](https://img.shields.io/badge/tier-Bronze%20✅-brightgreen)](./ARCHITECTURE.md)
[![Status](https://img.shields.io/badge/status-Operational-brightgreen)](./history/prompts/constitution/)

## 🎯 Vision

Transform Claude from a **reactive assistant** into a **proactive autonomous agent** that works 8,760 hours/year vs human's 2,000 hours, delivering 85-90% cost savings.

- 🔄 Monitors Gmail, WhatsApp, Calendar 24/7
- ✅ Processes files, emails, and messages autonomously
- 🛡️ Respects human-in-the-loop approval boundaries
- 📊 Maintains complete audit trail of all decisions
- 🚀 Scales from foundation (Bronze) to full automation (Platinum)

## 📦 Quick Start

```bash
# Install dependencies
pip install -r Tier_1_Bronze/src/watchers/requirements.txt

# Setup PM2
./scripts/setup_pm2.sh

# Verify installation
./scripts/run_validation_gates.sh bronze
```

## 🏗️ Architecture

```
Files/Gmail/WhatsApp (Sources)
            ↓
   Python Watchers (Perception)
            ↓
   Obsidian Vault (Storage)
            ↓
   Claude Code (Reasoning)
       ↙        ↘
   HITL     MCP Servers
  Approval   (Actions)
```

## 🛡️ Constitution-First Architecture

All decisions governed by **Constitution v1.0.0** at `.specify/memory/constitution.md` with:
- ✅ HITL approval thresholds for 20+ scenarios
- ✅ Ralph Wiggum loop persistence pattern for multi-step tasks
- ✅ FTE specialization rules (Gmail, WhatsApp, Calendar, Social Media)
- ✅ Agent skill quality gates (100% test coverage required)
- ✅ Security-first credential handling (OAuth 2.0, no password storage)
- ✅ Audit logging (JSON format, 90-day retention)

## 📋 Tier Progression

### Tier 1️⃣ Bronze - Foundation ✅ COMPLETE

**Status**: Operational (24/7 via PM2)

**Components**:
- 📁 **Filesystem Watcher**: Monitor /Inbox, move files to /Needs_Action
- 📄 **File Processor Skill**: Categorize and process files autonomously
- ✅ **HITL Workflow**: /Needs_Action → /Pending_Approval → /Approved → /Done
- 📊 **Validation Gate**: 5/5 tests passing (45+ test cases)
- 📈 **Dashboard**: Real-time status monitoring at http://localhost:8080

**FTE Agent**: None (foundation only)

**Tests**: 45+ cases covering file detection, processing, HITL workflow, PM2 integration, audit logging

**Next**: Silver Tier (Weeks 2-5)

---

### Tier 2️⃣ Silver - Functional Assistant 📝 SPECIFIED

**Status**: Specifications complete, ready for implementation (Weeks 2-5)

**Components**:
- 📧 **Gmail FTE Agent**: Auto-classify emails, draft replies, apply HITL rules
  - Triggers: Every 5 minutes
  - Skills: email-processor, email-classifier, email-responder
  - MCP: email-mcp server (send, draft, search, label, get_thread)
  - Metrics: 95% of important emails processed within 1 hour

- 💬 **WhatsApp FTE Agent**: Urgent messaging specialist with keyword detection
  - Triggers: Every 2 minutes
  - Skills: whatsapp-processor, message-extractor, urgency-classifier
  - MCP: browser-mcp server (Playwright WhatsApp Web automation)
  - Metrics: Respond to urgent messages within 3 minutes

- 🔐 **OAuth 2.0 Authentication**: Secure credential handling for both services

- 📝 **Validation Gate**: 10/10 tests (Gmail + WhatsApp + MCP servers)

**Tests**: 10 test cases per FTE + MCP server tests

**Next**: Gold Tier (Weeks 7+)

---

### Tier 3️⃣ Gold - Autonomous Employee 📋 SPECIFIED

**Status**: Specifications complete, ready for implementation (Weeks 7-11+)

**Components**:
- 📅 **Calendar FTE Agent**: Intelligent scheduling with conflict auto-resolution
  - Triggers: Every 10 minutes
  - Skills: calendar-processor, conflict-resolver, briefing-generator
  - MCP: calendar-mcp server (Google Calendar API)
  - Auto-resolves 95% of conflicts
  - SLO: Resolve conflicts within 30 minutes

- 🔁 **Ralph Wiggum Loop**: Multi-step task persistence pattern
  - Autonomous task completion without human intervention per step
  - Max iterations: 10, Timeout: 30 min/iteration
  - Kill switch: User moves file to /Rejected
  - HITL: Pause for approvals, resume when approved
  - Perfect for: Financial reports, complex workflows, batch processing

- 📊 **Weekly CEO Briefing**: Synthesizes all FTE data (Sunday 8:00 PM UTC)
  - 8 sections: Executive summary, financials, email, messages, calendar, social, bottlenecks, next week
  - Data sources: Odoo (accounting), Gmail, WhatsApp, Calendar, Facebook, Instagram, Twitter
  - Intelligence: Identifies bottlenecks and recommends actions
  - Output: `AI_Employee_Vault/Plans/Monday_Briefing_<date>.md`

- 📱 **Social Media FTE Agent**: Multi-platform social management
  - Platforms: Facebook, Instagram, Twitter/X
  - Capabilities: Draft posts, schedule (with approval), monitor engagement, analyze trends
  - Triggers: Facebook (30 min), Instagram (hourly), Twitter (15 min)
  - Skills: social-processor, content-drafter, engagement-analyzer
  - MCP: facebook-mcp, instagram-mcp, twitter-mcp servers

- 💰 **Odoo Integration**: Self-hosted accounting system
  - 7 MCP tools: get_invoices, get_customers, get_revenue, get_expenses, create_invoice, get_balance, generate_report
  - Odoo Community Edition (self-hosted)
  - Foundation for CEO briefing financial section
  - Supports invoice creation, financial reporting, cash flow forecasting

- 🧪 **Validation Gate**: 15/15 tests (all FTEs + Ralph Wiggum + CEO briefing)

**Tests**: 15 test cases covering calendar conflicts, Ralph Wiggum patterns, briefing accuracy, social media responses

**Next**: Platinum Tier (future, cloud + local hybrid)

---

### Tier 4️⃣ Platinum - Production Cloud + Local 🔮 PLANNED

**Status**: Design phase only (future)

**Concepts**:
- ☁️ **Cloud Agent**: Runs 24/7 on cloud VM, handles draft-only work (email, social)
- 💻 **Local Agent**: Handles approvals, WhatsApp, payments, final execution
- 🔄 **Vault Sync**: Git or Syncthing for state synchronization
- 🔐 **Security Rule**: Cloud never sees secrets (.env, WhatsApp sessions, banking creds)
- 💬 **A2A Messaging**: Agent-to-agent communication for coordination

**Estimated**: Months 2-3

**7 Core Principles:**
1. Human-in-the-Loop (HITL) – High-risk actions require approval
2. Proactive Assistance – 24/7 autonomous monitoring
3. Privacy First – No cloud secrets, local-only storage
4. Transparency – 100% audit trail with reasoning
5. Reliability – Always-on, graceful degradation
6. Continuous Learning – Evolving governance via amendments
7. Human Values Alignment – Respects user preferences

## 📈 Status

| Tier | Status | Scope |
|------|--------|-------|
| **Bronze** | ✅ COMPLETE | Filesystem watcher, file-processor skill, HITL workflow |
| **Silver** | 📝 PLANNED | Gmail FTE, WhatsApp FTE, email-mcp, browser-mcp |
| **Gold** | 🔒 FUTURE | Calendar FTE, Ralph Wiggum loop, CEO briefing, Odoo |
| **Platinum** | 🔮 VISION | Cloud VM, work-zone specialization, vault sync |

## 🧪 Validation Gates

```bash
# Run Bronze tier tests
./scripts/run_validation_gates.sh bronze
```

## 📚 Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** – Detailed system design
- **[Constitution](`.specify/memory/constitution.md`)** – Governance framework
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** – Development guidelines

## 📄 License

MIT License – see [LICENSE](./LICENSE)

---

**Last Updated:** 2026-02-26 | **Version:** 0.1.0-bronze | **Tier Status:** ✅ COMPLETE

🚀 Ready for Silver Tier implementation
