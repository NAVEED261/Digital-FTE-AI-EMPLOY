# Digital FTE Architecture

## System Design Overview

The Digital FTE system is built on a Constitution-First, Tier-Based, Multi-Agent architecture that enables autonomous operation of specialized AI agents coordinated through a shared Obsidian vault.

### Core Components

**1. Perception Layer (Python Watchers)**
- Filesystem watcher: Monitors `/Inbox` (1-second intervals)
- Gmail watcher: Checks important emails (5-minute intervals) – Silver tier
- WhatsApp watcher: Checks messages (2-minute intervals) – Silver tier  
- Calendar watcher: Monitors events (10-minute intervals) – Gold tier

**2. Storage Layer (Obsidian Vault)**
- `/Inbox` – Drop zone for new items
- `/Needs_Action` – Items awaiting processing
- `/Plans` – Claude-generated action plans
- `/Done` – Completed tasks
- `/Pending_Approval` – Items requiring HITL review
- `/Approved` – Approved items ready for execution
- `/Rejected` – Declined items
- `/Logs` – 100% audit trail (JSON format)
- `/Archive` – Historical records

**3. Reasoning Layer (Claude Code)**
- Reads tasks from vault
- Applies Constitution governance rules
- Invokes Agent Skills for actions
- Respects HITL thresholds
- Logs all decisions

**4. Action Layer (MCP Servers)**
- email-mcp: Gmail integration (send, draft, search, label)
- browser-mcp: Playwright automation (WhatsApp Web)
- calendar-mcp: Google Calendar integration – Gold tier
- odoo-mcp: Business context (invoices, payments) – Gold tier

## Tier-Based Organization

### Bronze Tier ✅ COMPLETE (Foundation)
- **Scope**: Filesystem automation + HITL workflow
- **Components**: base_watcher.py, filesystem_watcher.py, file-processor skill
- **Tests**: 5/5 tests passing (100% coverage)
- **Status**: Operational via PM2 (24/7)

### Silver Tier 📝 PLANNED (Email + WhatsApp)
- **Scope**: Gmail FTE + WhatsApp FTE agents
- **Components**: Gmail/WhatsApp watchers, email-mcp, browser-mcp, 4 skills
- **Tests**: 10/10 target
- **Timeline**: Week 2-5

### Gold Tier 🔒 FUTURE (Full Autonomy)
- **Scope**: Calendar FTE, Ralph Wiggum loop, CEO briefing, Odoo
- **Components**: Calendar watcher, Odoo integration, workflow engine
- **Tests**: 15/15 target
- **Timeline**: Week 6-10

### Platinum Tier 🔮 VISION (Cloud+Local)
- **Scope**: Cloud VM, work-zone specialization, vault sync
- **Components**: Cloud agent, local agent, A2A messaging
- **Tests**: 20/20 target
- **Timeline**: Month 2-3+

## Data Flow

1. **Event Source** → New email, WhatsApp message, or file
2. **Watcher Detection** → Python script detects and creates action file
3. **Vault Move** → Action file written to `/Needs_Action`
4. **Claude Processing** → Reads task, evaluates HITL rules
5. **Decision Point**:
   - ✅ Low-risk action → Execute immediately
   - 🔒 High-risk action → Create approval request in `/Pending_Approval`
6. **Execution** → Invoke MCP server or Agent Skill
7. **Logging** → Record action in `/Logs` with reasoning
8. **Completion** → Move task to `/Done`

## Constitution-Driven Governance

**Governing Document**: `.specify/memory/constitution.md` (v1.0.0)

**HITL Decision Table** (20 scenarios):
- Email to known contact → Auto-approve ✅
- Email to new contact → Require approval 🔒
- Payment < $50 → Auto-approve ✅
- Payment ≥ $50 → Require approval 🔒
- Social media draft → Auto-approve ✅
- Social media publish → Require approval 🔒
- And 14 more...

**Enforcement**:
- Violations treated as critical bugs
- Automatic detection via validation gates
- Immediate incident response
- Quarterly compliance audits

## Agent Skill Architecture

Every automation packaged as reusable Agent Skill:

```
Tier_X_Silver/src/skills/[skill-name]/
├── SKILL.md              # Documentation
├── __init__.py          # Implementation
├── requirements.txt     # Dependencies  
└── tests/
    ├── test_skill.py    # 100% test coverage (REQUIRED)
    └── verify.py        # Validation gate script
```

**Quality Gates**:
- ✅ 100% test coverage (blocking)
- ✅ SKILL.md documentation (blocking)
- ✅ verify.py validation (blocking)
- ✅ Type hints + docstrings (required)
- ✅ PEP 8 compliance (required)

## Security Architecture

**Secret Management Hierarchy**:
1. **Tier 1** (Most Secure): OS Keychain for OAuth tokens
2. **Tier 2**: Environment variables from `.env` (gitignored)
3. **Tier 3** (Avoid): Configuration files
4. **Never**: Committed to git, stored in vault, hardcoded

**Audit Logging**:
- **Format**: JSON, append-only, one action per line
- **Location**: `/Logs/` with daily rotation
- **Retention**: 90 days minimum
- **Fields**: timestamp, agent, action, target, result, reasoning, approval_status

**Network Isolation**:
- MCP servers accessible locally only (localhost:port)
- HTTPS for external APIs
- VPN recommended for remote access

## Process Management

**PM2 Configuration**:
```javascript
module.exports = {
  apps: [
    {
      name: 'filesystem-watcher',
      script: './Tier_1_Bronze/src/watchers/filesystem_watcher.py',
      interpreter: 'python3',
      watch: true,
      max_memory_restart: '500M',
      autorestart: true,
      max_restarts: 10
    }
    // Additional watchers for Silver/Gold tiers
  ]
};
```

**Health Monitoring**:
- Uptime tracking (target 99.5%)
- Crash detection + auto-restart
- Hourly validation gate runs
- Weekly audit log review

## Ralph Wiggum Loop (Gold Tier)

**Pattern**: File-movement persistence for multi-step workflows

```
WHILE task.status != "DONE" AND iterations < 10:
  1. Read from /Needs_Action
  2. Create plan in /Plans
  3. Execute actions
  4. IF success → Move to /Done (exit)
  5. IF blocked → Create subtask (continue)
  6. IF needs approval → Move to /Pending_Approval (pause)
  7. Log iteration + reasoning
```

**Safety Mechanisms**:
- Max 10 iterations per task
- 30-minute timeout per iteration
- Kill switch: User moves to `/Rejected/`
- Full audit trail

## Performance Targets

**Bronze Tier SLOs**:
- Uptime: 99.5%
- File processing latency: <1 second
- Audit logging: 100% of actions

**Silver Tier SLOs**:
- Email processing: 95% within 1 hour
- WhatsApp response: <3 minutes urgent
- Approval turnaround: <2 hours median

**Gold Tier SLOs**:
- Conflict detection: <15 minutes
- System uptime: 99.5%
- CEO briefing: Generated by 8 AM Monday

## Scalability Considerations

- **Watcher Intervals**: Configurable per use case
- **Batch Processing**: For high-volume scenarios
- **Caching**: Reduce API calls where safe
- **Async Processing**: For blocking operations
- **Cloud Agent**: Offload non-sensitive computation

---

**Last Updated**: 2026-02-26 | **Version**: 1.0.0 | **Status**: Active
