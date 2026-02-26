# Specification: browser-mcp Server (Silver Tier)

## MCP Server Definition

```yaml
Name: browser-mcp
Type: Model Context Protocol Server (Playwright-based)
Language: TypeScript (Node.js)
Status: Ready for Implementation
Dependencies: Playwright, @anthropic-sdk/sdk
Timeline: Week 4-5
SLO: 99.5% uptime, <2000ms latency p95
```

## Purpose

MCP server that exposes Playwright capabilities for browser automation:
- Navigate web pages
- Click UI elements
- Fill forms
- Interact with WhatsApp Web
- Take screenshots
- Extract DOM content

## Architecture

```
Claude Code (Client)
        ↓
browser-mcp Server (localhost:3001)
        ↓
Playwright Engine
        ↓
Chromium Browser (Headless)
```

## Tools

### 1. navigate

**Purpose**: Navigate to a URL

**Inputs**:
- `url` (string, required): Full URL (must include https://)
- `wait_for` (string, optional): CSS selector to wait for before returning

**Output**:
```json
{
  "status": "success",
  "url": "https://web.whatsapp.com/",
  "title": "WhatsApp"
}
```

### 2. click

**Purpose**: Click an element

**Inputs**:
- `selector` (string, required): CSS selector
- `wait_for` (string, optional): Selector to wait for after click

**Output**:
```json
{
  "status": "success",
  "element": "button.send",
  "message": "Clicked element"
}
```

### 3. type_text

**Purpose**: Type text into input field

**Inputs**:
- `selector` (string, required): Input field selector
- `text` (string, required): Text to type
- `delay_ms` (number, optional): Delay between keystrokes

**Output**:
```json
{
  "status": "success",
  "selector": "input[type='text']",
  "text_entered": "Hello World"
}
```

### 4. whatsapp_send_message

**Purpose**: Send WhatsApp message to contact

**Inputs**:
- `contact_name` (string, required): Contact name in chat list
- `message` (string, required): Message content
- `wait_for_send` (boolean, optional): Wait for checkmarks (default true)

**Output**:
```json
{
  "status": "sent",
  "contact": "John Client",
  "message": "Payment confirmed",
  "timestamp": "2026-02-26T14:30:00Z"
}
```

**HITL Integration**: Called AFTER user approves message

**Error Handling**:
- Contact not found: Return list of available contacts
- Network error: Retry with exponential backoff
- Rate limited: Queue and retry later

### 5. whatsapp_read_messages

**Purpose**: Read unread messages from contact

**Inputs**:
- `contact_name` (string, required): Contact name
- `max_messages` (number, optional): How many to read (default 20)

**Output**:
```json
{
  "status": "success",
  "contact": "John Client",
  "messages": [
    {
      "timestamp": "2026-02-26T14:30:00Z",
      "text": "Hi! Can you confirm payment?",
      "is_unread": true
    }
  ]
}
```

### 6. whatsapp_mark_as_read

**Purpose**: Mark conversation as read

**Inputs**:
- `contact_name` (string, required): Contact name

**Output**:
```json
{
  "status": "success",
  "contact": "John Client",
  "messages_marked": 3
}
```

### 7. screenshot

**Purpose**: Capture current page screenshot

**Inputs**:
- `save_to` (string, optional): File path to save
- `full_page` (boolean, optional): Full page vs viewport

**Output**:
```json
{
  "status": "success",
  "file": "/tmp/screenshot-2026-02-26-143000.png",
  "size_bytes": 45600
}
```

### 8. get_dom_content

**Purpose**: Extract text from page or selector

**Inputs**:
- `selector` (string, optional): CSS selector (if null, gets full body)
- `format` (string, optional): "text" or "html"

**Output**:
```json
{
  "status": "success",
  "content": "Full conversation history text...",
  "length_chars": 1234
}
```

## Session Management

**Persistent WhatsApp Web Session**:
- Browser context saved locally (encrypted)
- Auto-login on subsequent runs
- 30-minute idle timeout with re-auth
- Handles WhatsApp Web disconnects gracefully

**Storage**:
```
~/.claude/whatsapp-session/
├── cookies.json (encrypted)
├── localStorage.json (encrypted)
└── sessionStorage.json (encrypted)
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Element not found | Return available selectors |
| Navigation timeout | Retry + increase timeout |
| Contact not found | List available contacts |
| Network disconnected | Queue and retry on recovery |
| WhatsApp Web crash | Restart browser + re-login |

## Rate Limiting

- **Sends per minute**: 30 (WhatsApp limit)
- **Message reads per minute**: Unlimited
- **Strategy**: Queue messages if exceeding 30/min

## Logging & Auditing

**Every call logged**:
```json
{
  "timestamp": "2026-02-26T14:30:00Z",
  "tool": "whatsapp_send_message",
  "contact": "John Client",
  "message_preview": "Payment confirmed...",
  "status": "sent",
  "latency_ms": 1200,
  "error": null
}
```

## Security

- ✅ Session encryption (AES-256)
- ✅ Headless mode (no visible window)
- ✅ No credentials in logs
- ✅ Automatic session cleanup
- ✅ MITM protection (HTTPS)

## Tests Required (part of 10 Silver tests)

1. `test_whatsapp_send_message_success` – Message sends
2. `test_whatsapp_read_unread_messages` – Messages read
3. `test_contact_not_found_error` – Graceful error
4. `test_rate_limiting_queues` – Queuing works
5. `test_session_persists` – Session saved/restored
6. `test_reconnection_after_disconnect` – Auto-reconnect
7. `test_screenshot_captures_page` – Screenshot works
8. `test_get_dom_content_extracts` – DOM extraction
9. `test_audit_logging_complete` – All logged
10. `test_latency_under_2000ms` – Performance met

## Deployment

```bash
# Install Playwright
npx playwright install chromium

# Configure .env
PLAYWRIGHT_HEADLESS=true

# Start server
node Tier_2_Silver/src/mcp/browser-mcp/index.js

# First time: scan QR code in console
# Subsequent runs: auto-login

# Verify
curl -X POST http://localhost:3001/tools/whatsapp_read_messages \
  -H "Content-Type: application/json" \
  -d '{"contact_name":"John Client"}'
```

## Configuration in Claude Code

**mcp.json**:
```json
{
  "mcpServers": {
    "browser-mcp": {
      "command": "node",
      "args": ["./Tier_2_Silver/src/mcp/browser-mcp/index.js"],
      "description": "Playwright browser automation for WhatsApp Web and web scraping"
    }
  }
}
```

---

**Created**: 2026-02-26 | **Status**: Ready for implementation | **Tier**: Silver
