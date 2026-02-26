# Specification: Calendar FTE Agent (Gold Tier)

## Agent Definition

```yaml
Name: Calendar FTE
Tier: Gold
Type: Scheduling & Time Management Specialist
Status: Ready for Implementation
Dependencies: calendar-mcp (Google Calendar), odoo-mcp (business context)
Timeline: Week 7-8
Success Criteria: 5/15 tests passing (part of Gold validation gate)
```

## Purpose

Intelligent calendar management agent that:
- Monitors calendar for conflicts and overlaps
- Auto-resolves low-priority conflicts
- Generates weekly briefings
- Blocks focus time based on goals
- Integrates business events with financial data (Odoo)

## Triggers & Perception

**Watcher**: `calendar_watcher.py`
- **Interval**: Every 10 minutes
- **Method**: Google Calendar API (OAuth 2.0)
- **Query**: All events for the day + upcoming 7 days
- **Action**: Creates action file in `/Needs_Action` when conflict detected

**Conflict Metadata File**:
```yaml
---
type: calendar_conflict
severity: high  # high, medium, low
events:
  - id: event1
    title: "Client meeting"
    time: "2026-02-26 14:00-15:00"
    priority: high
  - id: event2
    title: "Team standup"
    time: "2026-02-26 14:30-15:00"
    priority: low
detected: "2026-02-26T13:45:00Z"
resolution_suggested: "reschedule standup to 15:00"
---

# Calendar Conflict Detected

## Conflicting Events
- Client meeting (2026-02-26 14:00-15:00, HIGH priority)
- Team standup (2026-02-26 14:30-15:00, LOW priority)

## Suggested Resolution
Automatically reschedule standup to 15:00 (after client meeting)

## Actions
- [ ] Accept automatic rescheduling (low-risk)
- [ ] Manual resolution needed (approve specific action)
- [ ] Escalate for user decision
```

## Skills Required

### 1. calendar-processor
- Extract and structure calendar data
- Parse Google Calendar events
- Identify overlaps and conflicts
- Extract attendees, duration, priority

### 2. conflict-resolver
- Detect conflicting time slots
- Suggest resolution strategies
- Auto-reschedule lower priority items
- Respect "focus time" blocks
- HITL: High-priority conflicts require approval

### 3. briefing-generator
- Analyze week's calendar
- Summarize events completed
- Identify trends and patterns
- Generate CEO briefing section

## MCP Server: calendar-mcp

**Tools**:
- `get_events(date_range, attendees)` – Retrieve calendar events
- `create_event(title, start, end, attendees, description)` – Add event
- `update_event(event_id, fields)` – Modify event
- `delete_event(event_id)` – Remove event
- `find_conflicts(date_range)` – Detect overlapping events

**Error Handling**:
- Rate limited (429): Exponential backoff
- Auth failed (401): Token refresh
- Not found (404): Return helpful error
- Invalid input (400): Validation error

**Latency SLO**: <500ms p95

## HITL Thresholds (Constitution Section II)

| Scenario | Risk | Action |
|----------|------|--------|
| Auto-reschedule low priority (<1 hour) | Low | Auto-resolve |
| Reschedule high priority event | High | Create approval request |
| Create focus time block | Medium | Ask user first |
| Delete event (>30 days old) | Low | Auto-approve |
| Modify attendees (add new external) | High | Require approval |
| Create recurring event | Medium | Require approval |

## Workflow Diagram

```
Google Calendar
        ↓
Calendar Watcher (10 min)
        ↓
Conflict detected?
        ├─→ NO: Sleep 10 min
        │
        └─→ YES: Create action file
                ↓
        Claude processes file
                ↓
        Analyze conflict
                ├─→ Low risk: Auto-resolve
                │       ↓
                │   Update calendar via calendar-mcp
                │       ↓
                │   Log action
                │       ↓
                │   Move to /Done
                │
                └─→ High risk: Create approval
                        ↓
                    Move to /Pending_Approval
                        ↓
                    User reviews
                        ↓
                    If approved: Execute
                    If rejected: Notify stakeholders
                        ↓
                    Move to /Done
```

## Metrics & SLOs

| Metric | Target | Monitoring |
|--------|--------|-----------|
| Conflict detection | <5 minutes | Logs analysis |
| Resolution time | <30 minutes (auto), <1 hour (approval) | Logs analysis |
| Calendar uptime | 99.5% | API monitoring |
| Accuracy | 95%+ | Weekly review |

## Tests Required (5 tests for Gold tier)

1. `test_calendar_watcher_detects_conflicts` – Detects overlapping events
2. `test_conflict_resolution_automatic` – Auto-reschedules low priority
3. `test_conflict_requires_approval` – High-priority conflicts escalate
4. `test_calendar_mcp_crud_operations` – All CRUD operations work
5. `test_calendar_briefing_generation` – Weekly briefing generated correctly

## Dependencies

- google-auth, google-auth-oauthlib (OAuth 2.0)
- google-api-python-client (Calendar API)
- pytest (testing)

## Security

- ✅ OAuth 2.0 (no password storage)
- ✅ Token auto-refresh
- ✅ Scoped permissions (calendar.events only)
- ✅ No credentials in logs
- ✅ HTTPS enforced
- ✅ Audit logging 100%

---

**Created**: 2026-02-26 | **Status**: Ready for implementation | **Tier**: Gold
