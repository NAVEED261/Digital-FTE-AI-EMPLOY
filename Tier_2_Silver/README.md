# Tier 2: Silver (Functional Assistant)

## Status: 📝 PLANNED FOR IMPLEMENTATION

**Objective**: Add external integrations (Gmail, WhatsApp) with MCP servers.

## Overview

Silver tier transforms the Digital FTE from basic file handling to a functional email & messaging assistant with:
- **Gmail FTE Agent**: 24/7 email monitoring, classification, and drafting
- **WhatsApp FTE Agent**: Real-time message monitoring with urgency detection
- **email-mcp Server**: Gmail API integration (send, draft, search, label, threads)
- **browser-mcp Server**: Playwright WhatsApp Web automation
- **4 Agent Skills**: email-processor, email-classifier, email-responder, urgency-classifier

## FTE Agents

### Gmail FTE
- **Domain**: Email communication
- **Triggers**: Every 5 minutes (important labels)
- **Capabilities**:
  - Detect new emails from important senders
  - Auto-classify (invoice, inquiry, notification, spam)
  - Draft intelligent replies
  - Apply HITL thresholds (new contacts require approval)
- **SLO**: Process 95% of important emails within 1 hour
- **Skills**: email-processor, email-classifier, email-responder
- **MCP**: email-mcp (send, draft, search, label, get_thread)

### WhatsApp FTE
- **Domain**: Urgent messaging
- **Triggers**: Every 2 minutes (unread messages)
- **Capabilities**:
  - Detect urgent keywords ("payment", "urgent", "ASAP")
  - Auto-acknowledge simple messages
  - Escalate payment/sensitive items
  - Session persistence (encrypted)
- **SLO**: Respond to urgent messages within 3 minutes
- **Skills**: whatsapp-processor, message-extractor, urgency-classifier
- **MCP**: browser-mcp (Playwright WhatsApp Web automation)

## MCP Servers

### email-mcp
- **Tools**: 
  - `send_email()` – Send approved emails
  - `draft_email()` – Create Gmail drafts
  - `search_emails()` – Search archive
  - `label_email()` – Apply labels/flags
  - `get_thread()` – Retrieve conversations
  - `get_attachments()` – Download attachments
- **Auth**: OAuth 2.0 (Google)
- **Rate Limits**: 300 requests/minute (essentially unlimited)
- **Latency SLO**: <1000ms p95

### browser-mcp
- **Tools**:
  - `navigate()` – Go to URL
  - `click()` – Click elements
  - `type_text()` – Fill forms
  - `whatsapp_send_message()` – Send via WhatsApp Web
  - `whatsapp_read_messages()` – Read unread messages
  - `whatsapp_mark_as_read()` – Mark as read
  - `screenshot()` – Capture page
  - `get_dom_content()` – Extract text
- **Session**: Persistent (encrypted local storage)
- **Browser**: Playwright Chromium (headless)
- **Rate Limits**: 30 sends/minute (WhatsApp limit)
- **Latency SLO**: <2000ms p95

## Agent Skills

### email-processor
- Extract and structure email data
- Parse headers, body, attachments
- 100% test coverage required
- Status: Ready for development

### email-classifier
- Categorize emails (invoice, inquiry, notification, spam)
- Assign priority (high, medium, low)
- Detect sensitive keywords
- 100% test coverage required

### email-responder
- Draft professional email replies
- Use company context (Company_Handbook.md)
- Generate appropriate CTAs
- 100% test coverage required

### urgency-classifier
- Detect urgent/payment keywords
- Classify message priority
- Trigger escalation if needed
- 100% test coverage required

## HITL Thresholds (from Constitution Section II)

**Email Scenarios**:
- Known contact (>30 days) → Auto-draft ✅
- New contact (<30 days) → Require approval 🔒
- Payment mentions → Require approval 🔒
- Sensitive keywords (legal, contract) → Require approval 🔒

**WhatsApp Scenarios**:
- Simple ack ("Got it", "Thanks") → Auto-reply ✅
- Payment confirmation → Require approval 🔒
- Unknown sender → Require approval 🔒

## Implementation Timeline

| Week | Phase | Deliverable |
|------|-------|-------------|
| 2-3 | Gmail FTE | gmail_watcher.py + email-mcp server + skills |
| 4-5 | WhatsApp FTE | whatsapp_watcher.py + browser-mcp server + skills |
| 5 | Integration | Full HITL workflow testing + 7-day stability |

## Validation Gate (10 tests required)

```bash
./scripts/run_validation_gates.sh silver
```

**Tests**:
1. Gmail watcher detects emails
2. Email classification accuracy
3. HITL new contact creates approval
4. Auto-draft known contact
5. Draft quality
6. Email send success
7. Rate limit handling
8. Audit logging complete
9. Error recovery
10. Uptime 99.5%

Plus 10 WhatsApp tests + MCP server tests.

## Security Considerations

- ✅ OAuth 2.0 (not password storage)
- ✅ Session encryption (AES-256)
- ✅ Automatic token refresh
- ✅ No credentials in logs
- ✅ Headless browser (WhatsApp)
- ✅ HTTPS enforced (Gmail API)
- ✅ Audit logging 100%

## Known Limitations

| Issue | Mitigation |
|-------|-----------|
| WhatsApp Web can disconnect | Auto-reconnect + retry |
| Gmail rate limit (429) | Exponential backoff |
| Session expires | Automatic token refresh |
| Attachment handling | Size limits + validation |

## Dependencies

**Gmail**:
- google-auth==2.28.0
- google-auth-oauthlib==1.2.0
- google-api-python-client==2.118.0

**WhatsApp**:
- playwright==1.41.0
- python-dotenv==1.0.0

**Testing**:
- pytest==8.0.0
- pytest-cov==4.1.0

## Specifications

- **Tier_2_Silver/specs/gmail-fte.spec.md** – Gmail FTE agent definition
- **Tier_2_Silver/specs/whatsapp-fte.spec.md** – WhatsApp FTE agent definition
- **Tier_2_Silver/specs/email-mcp.spec.md** – Email MCP server tools
- **Tier_2_Silver/specs/browser-mcp.spec.md** – Browser MCP server tools

## Getting Started

1. **Read specifications** in `specs/` folder
2. **Implement Gmail FTE** (Week 2-3):
   - Write `gmail_watcher.py`
   - Create email-processor, email-classifier, email-responder skills
   - Implement email-mcp server
   - Write tests (10 minimum)
3. **Implement WhatsApp FTE** (Week 4-5):
   - Write `whatsapp_watcher.py`
   - Create urgency-classifier, message-responder skills
   - Implement browser-mcp server
   - Write tests (10 minimum)
4. **Run validation gate**:
   ```bash
   ./scripts/run_validation_gates.sh silver
   ```
5. **Fix failures** until 100% pass rate
6. **Deploy** to production

---

**Last Updated**: 2026-02-26 | **Status**: Specifications Ready | **Tier**: Silver | **Next**: Implementation Week 2-3
