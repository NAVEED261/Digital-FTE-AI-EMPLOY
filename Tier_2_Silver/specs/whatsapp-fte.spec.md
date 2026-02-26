# Specification: WhatsApp FTE Agent (Silver Tier)

## Agent Definition

```yaml
Name: WhatsApp FTE
Tier: Silver
Type: Urgent Messaging Specialist
Status: Ready for Implementation
Dependencies: browser-mcp (Playwright), whatsapp-processor skill, urgency-classifier skill
Timeline: Week 4-5
Success Criteria: 10/10 tests passing, operational 99.5% uptime
```

## Purpose

Real-time WhatsApp monitoring agent that:
- Monitors WhatsApp Web for urgent messages
- Detects payment/urgent keywords
- Auto-acknowledges simple messages
- Escalates urgent items
- Maintains encrypted session state

## Triggers & Perception

**Watcher**: `whatsapp_watcher.py`
- **Interval**: Every 2 minutes
- **Method**: Playwright WhatsApp Web automation
- **Session**: Persistent (encrypted local storage)
- **Query**: Unread messages in chat list
- **Action**: Creates action file in `/Needs_Action` with message metadata

**Message Metadata File**:
```yaml
---
type: whatsapp_message
from: "John Client"
contact_type: known  # known or unknown
received: "2026-02-26T14:30:00Z"
urgency: high  # high, medium, low
keywords: ["payment", "urgent"]
---

# New WhatsApp Message: John Client

## From
John Client (Known contact, 90 days)

## Message Content
"Hi! Can you confirm receipt of payment sent today? Invoice #12345"

## Detected Urgency
HIGH (keywords: payment, confirm)

## Suggested Actions
- [ ] Verify payment received
- [ ] Reply with confirmation (auto-draft)
- [ ] Mark as read
```

## Reasoning Engine

Claude Code processes message with:

1. **Urgency Detection**
   - Keywords: "payment", "urgent", "ASAP", "invoice", "today"
   - Urgency level: high/medium/low
   - Escalation: High urgency → notify user

2. **HITL Evaluation**
   - Simple acknowledgment (known contact) → Auto-reply
   - Payment confirmation → Require approval
   - Unknown sender → Require approval
   - Spam patterns → Auto-discard

3. **Reply Generation**
   - Keep brief (WhatsApp style)
   - Professional tone
   - Include relevant details

4. **Approval Workflow**
   - Low-risk: Send immediately
   - High-risk: Create approval request
   - Urgent: Notify user immediately

## Skills Required

### 1. whatsapp-processor
- **Purpose**: Extract and structure message data
- **Input**: WhatsApp Web page content
- **Output**: Structured JSON with sender, message, attachments
- **HITL**: None (data extraction only)

### 2. urgency-classifier
- **Purpose**: Detect urgent/payment keywords
- **Input**: Message content
- **Output**: Urgency level (high/medium/low), keywords matched
- **HITL**: Low-risk only (keyword matching)

### 3. message-responder (from email-responder, adapted)
- **Purpose**: Draft appropriate message replies
- **Input**: Message structure + urgency + company context
- **Output**: Reply text
- **HITL**: High-risk only (payments, unknown senders)

## MCP Server: browser-mcp

**Playwright-based WhatsApp Web automation**

**Capabilities**:
- `navigate(url)` – Open WhatsApp Web
- `click(selector)` – Click UI elements
- `type_text(selector, text)` – Type message
- `whatsapp_send_message(chat_name, message)` – Send message
- `whatsapp_read_messages(chat_name)` – Read unread messages
- `whatsapp_mark_as_read(chat_name)` – Mark conversation read
- `screenshot()` – Capture current state

**Session Management**:
- Persistent: Keep logged in between runs
- Encryption: Store session in OS Keychain
- Timeout: 30-minute idle timeout with re-login
- Headless: Run in headless mode (no visible window)

## HITL Thresholds (Constitution Section II)

| Scenario | Risk | Action |
|----------|------|--------|
| "Got it" / "Thanks" / "OK" from known contact | Low | Auto-reply |
| Payment-related message | High | Create approval request |
| Unknown sender message | Medium | Create approval request |
| Multiple/bulk messages | Medium | Consolidate + approve once |
| Attachment received | Medium | Flag for manual review |

## Workflow Diagram

```
WhatsApp Web
        ↓
WhatsApp Watcher (2 min)
        ↓
Unread messages detected
        ↓
Action file in /Needs_Action
        ↓
Claude reads + evaluates HITL
        │
        ├─→ Low Risk (simple ack)
        │       ↓
        │   Auto-reply via browser-mcp
        │       ↓
        │   Mark as read
        │       ↓
        │   Log in /Logs
        │       ↓
        │   Move to /Done
        │
        ├─→ Medium Risk
        │       ↓
        │   Create approval request
        │       ↓
        │   User reviews
        │       ↓
        │   If approved: send reply
        │       ↓
        │   Move to /Done
        │
        └─→ High Risk (URGENT)
                ↓
            Create urgent notification
                ↓
            Notify user immediately
                ↓
            Wait for user action
                ↓
            Move to /Done
```

## Metrics & SLOs

| Metric | Target | Monitoring |
|--------|--------|-------------|
| Message detection | <2 minutes | Logs analysis |
| Urgent escalation | <3 minutes | Logs analysis |
| Auto-reply rate | 50%+ (simple acks) | Logs analysis |
| Session uptime | 98%+ (handles disconnects) | Playwright logging |
| Overall uptime | 99.5% | PM2 monitoring |

## Tests Required (10 tests for Silver tier)

1. `test_whatsapp_watcher_detects_messages` – Detects new messages
2. `test_urgency_detection_accurate` – Keyword detection works
3. `test_high_urgency_creates_approval` – Payment messages trigger approval
4. `test_auto_reply_simple_messages` – Simple acks auto-reply
5. `test_whatsapp_send_success` – Messages send successfully
6. `test_session_persistence` – Session survives restarts
7. `test_rate_limiting` – Handles message limits
8. `test_audit_logging_complete` – All messages logged
9. `test_error_recovery` – Handles failures (network, login)
10. `test_uptime_99_5_percent` – Meets uptime SLO

## Dependencies

- playwright==1.41.0
- python-dotenv==1.0.0
- pytest==8.0.0

## Security

- ✅ Session encrypted in OS Keychain
- ✅ No passwords in logs
- ✅ Headless mode (no visible window)
- ✅ Audit log includes sender verification
- ✅ Automatic session refresh

## Known Limitations & Mitigations

| Limitation | Risk | Mitigation |
|-----------|------|-----------|
| WhatsApp Web can disconnect | Medium | Auto-reconnect + retry logic |
| Session expires | Low | Refresh token handling |
| Rate limits on sending | Low | Queue and retry with backoff |
| Cannot access deleted messages | Low | Acceptable (real-time only) |

## Deployment

```bash
# Install Playwright browser
playwright install chromium

# Setup WhatsApp Web login (one-time)
1. Run watcher manually first time
2. Scan QR code with phone
3. Session saved encrypted
4. Automatic login subsequent runs

# Start watcher
pm2 start Tier_2_Silver/src/watchers/whatsapp_watcher.py \
  --name "whatsapp-watcher" \
  -- "/mnt/d/Hackaton-0/AI_Employee_Vault"

# Validate
./scripts/run_validation_gates.sh silver
```

---

**Created**: 2026-02-26 | **Status**: Ready for implementation | **Tier**: Silver
