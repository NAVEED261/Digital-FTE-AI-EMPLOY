# Specification: Gmail FTE Agent (Silver Tier)

## Agent Definition

```yaml
Name: Gmail FTE
Tier: Silver  
Type: Email Communication Specialist
Status: Ready for Implementation
Dependencies: email-mcp, email-processor skill, email-classifier skill, email-responder skill
Timeline: Week 2-3
Success Criteria: 10/10 tests passing, operational 99.5% uptime
```

## Purpose

Autonomous email management agent that:
- Monitors Gmail for important emails 24/7
- Auto-classifies and prioritizes messages
- Drafts intelligent replies
- Respects HITL boundaries for sensitive emails
- Maintains complete audit trail

## Triggers & Perception

**Watcher**: `gmail_watcher.py`
- **Interval**: Every 5 minutes
- **Scope**: Important labels only (not spam)
- **Query**: `is:important is:unread newer_than:5m`
- **Action**: Creates action file in `/Needs_Action` with email metadata

**Email Metadata File**:
```yaml
---
type: email_notification
subject: "Client asks for invoice"
from: "client@company.com"
received: "2026-02-26T14:30:00Z"
importance: high
category: auto_classify_needed
---

# New Email: Client asks for invoice

## From
client@company.com (Known contact, 120 days)

## Subject
Client asks for invoice

## Preview
"Hi, can you send over the invoice for project X?"

## Suggested Actions
- [ ] Review full email content
- [ ] Check if invoice is ready
- [ ] Draft reply (auto-draft suggested)
- [ ] Approve reply or send manually
```

## Reasoning Engine

Claude Code processes email with:

1. **Category Detection**
   - Invoice requests → high priority
   - General inquiry → medium priority
   - Spam/newsletter → low priority (auto-discard)

2. **HITL Evaluation**
   - Known contact (>30 days) + simple reply → Auto-draft
   - New contact + payment mention → Require approval
   - Sensitive keywords (legal, contract) → Require approval

3. **Draft Generation**
   - Professional tone per Company_Handbook.md
   - Cite relevant information
   - Include clear CTA (call-to-action)

4. **Approval Workflow**
   - Low-risk: Send immediately
   - High-risk: Create `/Pending_Approval/email-draft-X.md`
   - User reviews and approves/rejects

## Skills Required

### 1. email-processor
- **Purpose**: Extract and structure email data
- **Input**: Raw email via Gmail API
- **Output**: Structured JSON with subject, body, sender, attachments
- **HITL**: None (data extraction only)

### 2. email-classifier  
- **Purpose**: Categorize email and determine priority
- **Input**: Email structure
- **Output**: Category (invoice, inquiry, notification, spam), priority (high/medium/low)
- **HITL**: Low-risk only (auto-classify)

### 3. email-responder
- **Purpose**: Draft intelligent email replies
- **Input**: Email structure + category + company context
- **Output**: Draft reply text
- **HITL**: High-risk only (new contacts, payments, sensitive words)

## MCP Server: email-mcp

**Capabilities**:
- `send_email(to, subject, body)` – Send approved email
- `draft_email(to, subject, body)` – Create draft in Gmail
- `search_emails(query)` – Search email archive
- `label_email(email_id, labels)` – Apply labels/flags
- `get_thread(message_id)` – Retrieve full conversation
- `get_attachments(message_id)` – Download attachments

**Error Handling**:
- Rate limits: Exponential backoff (max 10 retries)
- Auth failures: Refresh token + retry
- Network issues: Queue and retry on recovery

## HITL Thresholds (Constitution Section II)

| Scenario | Risk | Action |
|----------|------|--------|
| Reply known contact (>30d) | Low | Auto-draft + send |
| Reply new contact (<30d) | Medium | Create approval request |
| Payment-related email | High | Create approval request |
| New attachment | Medium | Flag for review |
| Sender not in contacts | Medium | Create approval request |
| Sensitive keywords (legal, contract) | High | Create approval request |

## Workflow Diagram

```
Gmail (Important label)
        ↓
Gmail Watcher (5 min)
        ↓
Action file in /Needs_Action
        ↓
Claude reads + evaluates HITL
        │
        ├─→ Low Risk
        │       ↓
        │   Auto-draft + send
        │       ↓
        │   Log in /Logs
        │       ↓
        │   Move to /Done
        │
        └─→ High Risk
                ↓
            Create approval
            in /Pending_Approval
                ↓
            User reviews
                ↓
            /Approved or /Rejected
                ↓
            If approved: send
            If rejected: discard
                ↓
            Log in /Logs
                ↓
            Move to /Done
```

## Metrics & SLOs

| Metric | Target | Monitoring |
|--------|--------|-------------|
| Emails processed/day | 95% of important | Logs analysis |
| Auto-draft rate | 70%+ (low-risk) | Logs analysis |
| Response time (p95) | <30 minutes | Logs analysis |
| False positives | <5% | Weekly review |
| Uptime | 99.5% | PM2 monitoring |

## Tests Required (10 tests for Silver tier)

1. `test_gmail_watcher_detects_emails` – Watcher finds new emails
2. `test_email_classification_accuracy` – Classifier detects categories
3. `test_hitl_new_contact_creates_approval` – New contacts trigger approval
4. `test_auto_draft_known_contact` – Known contacts get auto-draft
5. `test_draft_quality` – Generated drafts are professional
6. `test_email_send_success` – Approved emails sent successfully
7. `test_rate_limit_handling` – Handles Gmail rate limits
8. `test_audit_logging_complete` – All actions logged
9. `test_error_recovery` – Handles failures gracefully
10. `test_uptime_99_5_percent` – Meets uptime SLO

## Dependencies

- google-auth==2.28.0
- google-auth-oauthlib==1.2.0
- google-api-python-client==2.118.0
- pytest==8.0.0
- email-validator==2.1.0

## Security

- ✅ OAuth 2.0 (not password storage)
- ✅ Token refresh automatic
- ✅ No credentials in logs
- ✅ Audit log includes sender verification
- ✅ Rate limit protection

## Deployment

```bash
# Setup Gmail API OAuth
1. Create credentials at https://console.cloud.google.com/
2. Store credentials.json in .env
3. Install dependencies

# Start watcher
pm2 start Tier_2_Silver/src/watchers/gmail_watcher.py \
  --name "gmail-watcher" \
  -- "/mnt/d/Hackaton-0/AI_Employee_Vault"

# Validate
./scripts/run_validation_gates.sh silver
```

---

**Created**: 2026-02-26 | **Status**: Ready for implementation | **Tier**: Silver
