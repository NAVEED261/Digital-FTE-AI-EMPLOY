# Specification: email-mcp Server (Silver Tier)

## MCP Server Definition

```yaml
Name: email-mcp
Type: Model Context Protocol Server
Language: TypeScript (Node.js)
Status: Ready for Implementation
Dependencies: Google Gmail API, google-auth-library
Timeline: Week 2-3
SLO: 99.5% uptime, <1000ms latency p95
```

## Purpose

MCP server that exposes Gmail API capabilities as tools callable by Claude Code:
- Send emails
- Draft emails in Gmail
- Search email archive
- Apply labels/flags
- Retrieve full conversation threads
- Manage attachments

## Architecture

```
Claude Code (Client)
        ↓
email-mcp Server (localhost:3000)
        ↓
Gmail API (Google)
```

## Tools

### 1. send_email

**Purpose**: Send an email immediately

**Inputs**:
- `to` (string, required): Recipient email address
- `subject` (string, required): Email subject line
- `body` (string, required): Email body (supports HTML)
- `cc` (string[], optional): CC recipients
- `bcc` (string[], optional): BCC recipients
- `in_reply_to` (string, optional): Message ID of email being replied to

**Output**:
```json
{
  "status": "sent",
  "message_id": "abc123def456",
  "timestamp": "2026-02-26T14:30:00Z"
}
```

**HITL Integration**: Called AFTER user approval from `/Pending_Approval`

**Error Handling**:
- Rate limited (429): Exponential backoff
- Auth failed (401): Refresh token + retry
- Invalid recipient (400): Return error with suggestion

### 2. draft_email

**Purpose**: Create email draft (not sent)

**Inputs**:
- `to` (string, required): Recipient
- `subject` (string, required): Subject line
- `body` (string, required): Body content
- `cc` (string[], optional): CC recipients

**Output**:
```json
{
  "status": "drafted",
  "draft_id": "xyz789",
  "url": "https://mail.google.com/mail/u/0/#drafts?compose=xyz789"
}
```

**HITL Integration**: User can review in Gmail before sending

### 3. search_emails

**Purpose**: Search email archive

**Inputs**:
- `query` (string, required): Gmail search query (supports operators like "from:", "to:", "has:attachment")
- `limit` (number, optional): Max results (default 20, max 100)
- `after_date` (string, optional): ISO date (e.g., "2026-02-01")

**Output**:
```json
{
  "status": "success",
  "count": 5,
  "results": [
    {
      "id": "abc123",
      "from": "client@company.com",
      "subject": "Invoice #12345",
      "date": "2026-02-26T10:00:00Z",
      "snippet": "Here is the invoice for project X..."
    }
  ]
}
```

**Use Cases**:
- Find previous invoices from sender
- Locate related conversations
- Verify payment history

### 4. label_email

**Purpose**: Apply labels/flags to emails

**Inputs**:
- `message_id` (string, required): Email ID
- `labels` (string[], required): Label names
- `remove` (boolean, optional): Remove instead of add

**Output**:
```json
{
  "status": "success",
  "message_id": "abc123",
  "labels_applied": ["Important", "Follow-up"]
}
```

**Use Cases**:
- Mark for follow-up
- Apply project labels
- Auto-categorize

### 5. get_thread

**Purpose**: Retrieve full email conversation

**Inputs**:
- `message_id` (string, required): Initial message ID
- `include_raw` (boolean, optional): Include raw RFC822 format

**Output**:
```json
{
  "status": "success",
  "thread_id": "abc123thread",
  "message_count": 5,
  "messages": [
    {
      "id": "msg1",
      "from": "client@company.com",
      "to": "me@example.com",
      "subject": "Project update",
      "date": "2026-02-20T10:00:00Z",
      "body": "Full email content..."
    }
  ]
}
```

**Use Cases**:
- Understand conversation history
- Provide context for reply
- Verify previous agreements

### 6. get_attachments

**Purpose**: Download email attachments

**Inputs**:
- `message_id` (string, required): Email ID
- `save_to` (string, optional): File path to save

**Output**:
```json
{
  "status": "success",
  "attachments": [
    {
      "filename": "invoice.pdf",
      "mime_type": "application/pdf",
      "size_bytes": 102400,
      "data": "base64-encoded content (if requested)"
    }
  ]
}
```

## Error Codes

| Code | Meaning | Recovery |
|------|---------|----------|
| 429 | Rate limited | Exponential backoff |
| 401 | Auth failed | Refresh token |
| 400 | Invalid input | Return error message |
| 404 | Message not found | Clarify search |
| 500 | Gmail API error | Retry with backoff |

## Rate Limiting

- **Quota**: 500 million requests/day (essentially unlimited)
- **Per-user quota**: 300 requests/minute
- **Burst**: 600 requests in 1-minute window
- **Strategy**: Exponential backoff on 429 errors (max 10 retries)

## Authentication

**OAuth 2.0 Flow**:
1. User authorizes app at Google Cloud Console
2. Get refresh token (stored encrypted in .env)
3. MCP server obtains access token from refresh token
4. Token auto-refreshes on expiry

**Scopes Required**:
- `https://www.googleapis.com/auth/gmail.send` (send)
- `https://www.googleapis.com/auth/gmail.readonly` (read)
- `https://www.googleapis.com/auth/gmail.modify` (labels)

## Logging & Auditing

**Every call logged in `/Logs/`**:
```json
{
  "timestamp": "2026-02-26T14:30:00Z",
  "tool": "send_email",
  "request": {
    "to": "client@company.com",
    "subject": "Invoice payment"
  },
  "response": {
    "status": "sent",
    "message_id": "abc123"
  },
  "latency_ms": 250,
  "error": null
}
```

## Security

- ✅ OAuth 2.0 (not password storage)
- ✅ Token refresh automatic (no manual intervention)
- ✅ No credentials in logs
- ✅ HTTPS only (Gmail API enforces)
- ✅ Scoped permissions (minimal required)
- ✅ Rate limiting protects quota

## Tests Required (part of 10 Silver tests)

1. `test_send_email_success` – Email sends
2. `test_draft_email_creates_draft` – Draft created
3. `test_search_emails_finds_results` – Search works
4. `test_label_email_applies_labels` – Labels applied
5. `test_get_thread_retrieves_conversation` – Thread retrieved
6. `test_rate_limit_handling` – 429 handled gracefully
7. `test_auth_refresh` – Token refresh works
8. `test_error_messages_clear` – Error messages helpful
9. `test_audit_logging_complete` – All calls logged
10. `test_latency_under_1000ms` – Performance met

## Deployment

```bash
# Install dependencies
npm install @anthropic-sdk/sdk @google-cloud/gmail-api express

# Configure .env
GMAIL_OAUTH_CLIENT_ID=xxxxx
GMAIL_OAUTH_CLIENT_SECRET=xxxxx
GMAIL_OAUTH_REFRESH_TOKEN=xxxxx

# Start server
node Tier_2_Silver/src/mcp/email-mcp/index.js

# Verify
curl -X POST http://localhost:3000/tools/send_email \
  -H "Content-Type: application/json" \
  -d '{"to":"test@example.com","subject":"Test","body":"Hello"}'
```

## Configuration in Claude Code

**mcp.json**:
```json
{
  "mcpServers": {
    "email-mcp": {
      "command": "node",
      "args": ["./Tier_2_Silver/src/mcp/email-mcp/index.js"],
      "env": {
        "GMAIL_OAUTH_REFRESH_TOKEN": "${GMAIL_OAUTH_REFRESH_TOKEN}"
      },
      "description": "Gmail API integration for sending and searching emails"
    }
  }
}
```

---

**Created**: 2026-02-26 | **Status**: Ready for implementation | **Tier**: Silver
