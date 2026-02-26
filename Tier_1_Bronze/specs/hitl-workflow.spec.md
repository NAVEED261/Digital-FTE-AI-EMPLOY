# Specification: Human-in-the-Loop (HITL) Workflow (Bronze Tier)

## Overview

The HITL Workflow implements a file-movement based approval system where sensitive actions require explicit user review before execution.

## Purpose

Maintain human oversight of AI decisions by:
1. Identifying high-risk actions
2. Creating approval request files
3. Waiting for user decision
4. Executing approved actions
5. Logging all decisions

## Workflow Stages

```
┌─────────────────┐
│ /Needs_Action/  │
│   (auto-move)   │
└────────┬────────┘
         │
    Claude reads
         │
    Check HITL Table
         │
    ┌────┴─────┐
    ▼          ▼
 LOW RISK   HIGH RISK
    │          │
EXECUTE    APPROVAL
    │          │
    ▼          ▼
/Pending_   /Pending_
Approval    Approval
    │          │
    │     User Reviews
    │          │
    │    ┌─────┴──────┐
    │    ▼            ▼
    │ /Approved/  /Rejected/
    │    │            │
    │ EXECUTE     DISCARD
    │    │            │
    └─►  ▼            ▼
       /Done/      /Archive/
```

## Decision Table (Constitution Section II)

**20 Scenarios Mapped to HITL Thresholds**:

| Scenario | Risk | Auto-Approve? | Reason |
|----------|------|---------------|--------|
| Email to known contact | Low | ✅ Yes | Routine, low reputation risk |
| Email to new contact | Medium | 🔒 No | Phishing/spoofing risk |
| File move Inbox→Action | Low | ✅ Yes | Reversible, just metadata |
| File delete | High | 🔒 No | Irreversible data loss |
| Payment < $50 | Low | ✅ Yes | Budget threshold |
| Payment ≥ $50 | High | 🔒 No | Significant financial impact |
| Calendar create | Low | ✅ Yes | User can edit after |
| Calendar cancel | Medium | 🔒 No | Affects others' schedules |
| Social media draft | Low | ✅ Yes | Draft, not published |
| Social media post | High | 🔒 No | Public, permanent record |

## File Movement Rules

### Low-Risk Actions (Auto-Approve ✅)

When action meets auto-approve criteria:
1. Claude detects action in task file
2. Checks Constitution Section II HITL table
3. Confirms auto-approve threshold met
4. Executes action directly
5. Logs result in `/Logs/` with reasoning
6. Moves task to `/Done/`

**No user interaction required**

### High-Risk Actions (Require Approval 🔒)

When action requires approval:
1. Claude detects high-risk action
2. Creates approval request file in `/Pending_Approval/`
3. File contains: action description, reasoning, risk level
4. Claude waits for user decision
5. User reviews and decides:
   - Move to `/Approved/` → Claude executes
   - Move to `/Rejected/` → Action discarded
6. Claude executes approved action
7. Logs result in `/Logs/` with user decision

**Requires user review before execution**

## Approval Request File Format

**Example**: `/Pending_Approval/send-email-to-newcontact.approval.md`

```yaml
---
approval_id: 2026-02-26-001
action: email_send
requested_at: 2026-02-26T14:30:00Z
risk_level: high
reasoning: |
  Email to unknown@external.com (new contact - phishing risk per Constitution II)
timeout: 24 hours
---

# Approval Needed: Send Email

## Action
Send email reply to: **unknown@external.com**

## Content
```
Subject: Re: Your Inquiry
Body: Thank you for reaching out...
```

## Risk Assessment
- **Category**: Email to New Contact
- **Risk Level**: Medium (per Constitution Section II)
- **Approval Rule**: Require Approval
- **Rationale**: First-time contact may be phishing; user should verify

## Reasoning
This email is to a new external contact not in your known contact list (added < 30 days). 
Per Constitution Section II HITL Table, new contact emails require approval to mitigate phishing 
and spoofing risks.

## What to Do
- ✅ **Approve**: Move to `/Approved/send-email-to-newcontact.approval.md`
- ❌ **Reject**: Move to `/Rejected/send-email-to-newcontact.approval.md`
- ⏱️ **Timeout**: After 24 hours, action is auto-rejected

## Auto-Approve Future?
To auto-approve future emails from this contact:
1. Add email to your contact list in Gmail
2. Confirm contact is trusted (30+ days)
3. Constitution Section II will auto-approve next time
```

## User Decision Workflow

1. **User reviews** approval request file
2. **Decides**:
   - Move to `/Approved/` folder → Accept action
   - Move to `/Rejected/` folder → Decline action
   - Leave in `/Pending_Approval/` → Defer decision
3. **Claude detects** file movement
4. **Claude executes** or discards based on folder

## Timeout Mechanism

- **Default timeout**: 24 hours
- **Action on timeout**: Auto-reject (conservative)
- **Override**: User can manually move file anytime

## Logging & Audit Trail

Every HITL decision logged in `/Logs/`:

```json
{
  "timestamp": "2026-02-26T14:35:00Z",
  "hitl_decision_id": "2026-02-26-001",
  "action": "email_send",
  "target": "unknown@external.com",
  "risk_level": "high",
  "approval_required": true,
  "user_decision": "approved",
  "decision_made_at": "2026-02-26T14:35:00Z",
  "decision_latency_minutes": 5,
  "reasoning": "User added sender to trusted contacts",
  "executed_at": "2026-02-26T14:35:15Z",
  "result": "success"
}
```

## Customization

**User can override HITL thresholds** via Constitution Amendment (Section VIII):

1. Create amendment file: `/Pending_Approval/constitution-amendment-v1.0.1.md`
2. Propose change (e.g., "Auto-approve emails from new contacts")
3. Include rationale
4. User approves
5. Threshold updated in Constitution Section II

## Testing

Validation tests in `Tier_1_Bronze/tests/test_hitl_workflow.py`:

1. **test_low_risk_auto_executes** – Low-risk action executes immediately
2. **test_high_risk_creates_approval** – High-risk action creates approval file
3. **test_approval_executes** – Approved action executed after move to /Approved/
4. **test_rejection_discards** – Rejected action discarded after move to /Rejected/
5. **test_timeout_auto_rejects** – Unapproved action auto-rejected after 24h

All tests must pass (5/5) before deployment.

## Compliance

✅ Constitution Section I.1: HITL is absolute priority
✅ Constitution Section II: 20-row decision table enforced
✅ Audit Logging: 100% of decisions logged
✅ Error Handling: Timeouts handled gracefully
✅ User Control: Can override thresholds via amendment

---

**Created**: 2026-02-26 | **Status**: ✅ Operational
