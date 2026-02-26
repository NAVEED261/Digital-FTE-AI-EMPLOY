# Tier 3: Gold (Autonomous Employee)

## Status: 📝 PLANNED FOR IMPLEMENTATION

**Objective**: Add cross-domain autonomy with Calendar FTE, business intelligence, and multi-step workflows.

## Overview

Gold tier transforms the Digital FTE from functional assistant to truly autonomous employee with:
- **Calendar FTE Agent**: Intelligent scheduling with conflict resolution
- **Ralph Wiggum Loop**: Multi-step task completion without human intervention
- **CEO Briefing**: Weekly autonomous business intelligence summary
- **Social Media Integration**: Facebook, Instagram, Twitter automation
- **Odoo Accounting**: Business financial tracking and reporting

## FTE Agents

### Calendar FTE
- **Domain**: Scheduling & time management
- **Triggers**: Every 10 minutes (Google Calendar API)
- **Capabilities**:
  - Detect calendar conflicts
  - Auto-resolve (reschedule lower priority)
  - Block focus time based on goals
  - Generate meeting summaries
  - Create calendar blocks from business events
- **SLO**: Resolve 95% of conflicts within 30 minutes
- **Skills**: calendar-processor, conflict-resolver, briefing-generator
- **MCP**: calendar-mcp, odoo-mcp

### Social Media FTE
- **Domain**: Social media presence management
- **Triggers**:
  - Facebook: Every 30 minutes (new posts, engagement)
  - Instagram: Every hour (stories, reels)
  - Twitter/X: Every 15 minutes (trending, mentions)
- **Capabilities**:
  - Draft posts from business goals
  - Schedule posts (require approval)
  - Monitor engagement metrics
  - Generate engagement summaries
  - Auto-reply to messages (with HITL)
- **SLO**: 99.5% uptime, respond to inquiries within 1 hour
- **Skills**: social-processor, content-drafter, engagement-analyzer
- **MCP**: facebook-mcp, instagram-mcp, twitter-mcp

## Ralph Wiggum Loop Pattern

The "Ralph Wiggum Loop" is a persistence pattern for complex multi-step tasks:

```
┌─────────────────────────────────────────────┐
│  Task in /Needs_Action                      │
│  Example: "Prepare Q1 financial report"     │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  Claude reads task, creates plan            │
│  Identifies subtasks:                       │
│  - Gather financial data from Odoo         │
│  - Calculate metrics                        │
│  - Generate charts                          │
│  - Create report PDF                        │
└──────────────┬──────────────────────────────┘
               │
      ┌────────┴────────┐
      ▼                 ▼
   Success          Blocked/Approval
      │                 │
      │    ┌────────────┘
      │    │
      │    ▼
      │  Move to /Pending_Approval
      │  Await user decision
      │    │
      │    ├─→ User moves to /Approved
      │    │   Continue loop
      │    │
      │    └─→ User moves to /Rejected
      │        Move to /Done (failed)
      │
      │  (Wait for approval - LOOP PAUSES)
      │
      ▼
  Move to /Done (complete)
  Loop exits (file no longer in /Needs_Action)
```

**Rules**:
- Max iterations: 10 (prevents infinite loops)
- Timeout per iteration: 30 minutes
- Kill switch: User moves file to /Rejected
- State persistence: Task remains in /Needs_Action until complete
- Blocking: Move to /Pending_Approval when approval needed

## MCP Servers

### calendar-mcp
- Tools: get_events, create_event, update_event, delete_event, find_conflicts
- Authentication: OAuth 2.0 (Google Calendar)
- Rate Limits: 500 requests/minute
- Latency SLO: <500ms p95

### facebook-mcp
- Tools: create_post, schedule_post, get_insights, get_feed, reply_message
- Authentication: OAuth 2.0 (Facebook Graph API)
- Rate Limits: 200 requests/minute
- Latency SLO: <1000ms p95

### instagram-mcp
- Tools: create_story, schedule_reel, get_insights, get_feed, reply_dm
- Authentication: OAuth 2.0 (Instagram Graph API)
- Rate Limits: 200 requests/minute
- Latency SLO: <1000ms p95

### twitter-mcp
- Tools: create_tweet, schedule_tweet, get_mentions, reply_tweet, get_analytics
- Authentication: OAuth 2.0 (Twitter API v2)
- Rate Limits: 300 requests/15min
- Latency SLO: <1000ms p95

### odoo-mcp
- Tools: create_invoice, get_balance, get_expenses, get_customers, generate_report
- Authentication: Odoo JSON-RPC API (self-hosted)
- Rate Limits: 1000 requests/minute
- Latency SLO: <1000ms p95

## Agent Skills

### calendar-processor
- Extract and structure calendar data
- Detect overlapping events
- Identify free time slots
- 100% test coverage required

### conflict-resolver
- Auto-reschedule lower priority items
- Suggest alternative times
- Respect focus time blocks
- 100% test coverage required

### briefing-generator
- Summarize week's events
- Analyze calendar trends
- Generate Monday CEO briefing
- 100% test coverage required

### social-processor
- Extract social media content
- Detect engagement patterns
- Identify trending topics
- 100% test coverage required

### content-drafter
- Draft posts from business goals
- Maintain brand voice
- Generate variations for A/B testing
- 100% test coverage required

### engagement-analyzer
- Calculate engagement metrics
- Track follower growth
- Identify top performers
- Generate trend reports
- 100% test coverage required

## Weekly CEO Briefing

**Schedule**: Every Sunday 8:00 PM (automated)

**Contents**:
1. **Revenue Summary**
   - Total revenue this week (from Odoo)
   - Average order value
   - Payment status summary
2. **Calendar & Meetings**
   - Events completed
   - Conflicts resolved
   - Key dates next week
3. **Email Performance**
   - Emails processed (Gmail FTE)
   - Auto-draft rate
   - Approval rate
4. **Messages**
   - WhatsApp messages handled
   - Urgent items escalated
5. **Social Media**
   - Posts published
   - Engagement metrics
   - Top performers
6. **Bottlenecks & Suggestions**
   - Identified issues
   - Recommended actions
   - Opportunities for automation
7. **Next Week Preview**
   - Scheduled events
   - Pending approvals
   - Goals and targets

**Output**: `AI_Employee_Vault/Plans/Monday_Briefing_<date>.md`

## Tests Required (15 tests)

1. `test_calendar_watcher_detects_events` – Events detected
2. `test_conflict_resolution_automatic` – Conflicts auto-resolved
3. `test_conflict_approval_required` – Complex conflicts require approval
4. `test_calendar_mcp_crud_operations` – CRUD operations work
5. `test_odoo_invoice_retrieval` – Financial data retrieved
6. `test_odoo_mcp_calculations` – Metrics calculated correctly
7. `test_ceo_briefing_generation` – Briefing generated
8. `test_ceo_briefing_includes_all_sections` – All 7 sections present
9. `test_facebook_post_draft` – Posts drafted
10. `test_twitter_tweet_schedule` – Tweets scheduled
11. `test_instagram_story_creation` – Stories created
12. `test_ralph_wiggum_loop_completion` – Multi-step task completes
13. `test_ralph_wiggum_loop_timeout` – Max iterations enforced
14. `test_ralph_wiggum_loop_kill_switch` – Kill switch works
15. `test_uptime_99_5_percent` – Meets uptime SLO

## Security Considerations

- ✅ All OAuth 2.0 (no password storage)
- ✅ Session encryption (AES-256)
- ✅ Token auto-refresh
- ✅ No credentials in logs
- ✅ HTTPS enforced
- ✅ Audit logging 100%
- ✅ HITL for sensitive actions (social post publishing)

## Known Limitations & Mitigations

| Issue | Mitigation |
|-------|-----------|
| Calendar API can be slow | Cache frequently accessed data |
| Social media rate limits | Queue posts and retry with backoff |
| Odoo network failures | Implement circuit breaker pattern |
| Ralph Wiggum loop runaway | Max iterations (10) + timeout (30min) |
| Task state loss | Immutable file-based state in vault |

## Dependencies

**Python**:
- google-auth, google-auth-oauthlib, google-api-python-client (Calendar)
- facebook-sdk, instagrapi, tweepy (Social media)
- odoorpc (Odoo)
- pytest==8.0.0

**Node.js** (for MCP servers):
- @anthropic-sdk/sdk, express, cors, compression
- google-calendar-api, facebook-graph-api, twitter-api-v2, odoorpc

## Timeline

| Week | Phase | Deliverable |
|------|-------|------------|
| 7-8 | Calendar FTE | calendar_watcher.py + calendar-mcp + skills |
| 9 | Ralph Wiggum | State machine implementation + 5 tests |
| 10 | CEO Briefing | briefing-generator skill + Odoo integration |
| 11+ | Social Media | Facebook, Instagram, Twitter FTEs + skills |

## Validation Gate (15 tests required)

```bash
./scripts/run_validation_gates.sh gold
```

**Passing Criteria**: 15/15 tests passing, 99.5% uptime achieved

## Specifications

- **Tier_3_Gold/specs/calendar-fte.spec.md** – Calendar FTE agent definition
- **Tier_3_Gold/specs/ralph-wiggum-loop.spec.md** – Multi-step workflow pattern
- **Tier_3_Gold/specs/ceo-briefing.spec.md** – Weekly briefing automation
- **Tier_3_Gold/specs/social-media-fte.spec.md** – Social media FTE definition
- **Tier_3_Gold/specs/odoo-integration.spec.md** – Odoo MCP server specification

## Getting Started

1. **Read specifications** in `specs/` folder
2. **Implement Calendar FTE** (Weeks 7-8):
   - Write `calendar_watcher.py`
   - Create calendar-processor, conflict-resolver skills
   - Implement calendar-mcp server
   - Write tests (5 minimum)
3. **Implement Ralph Wiggum Loop** (Week 9):
   - State machine for multi-step tasks
   - Integration with /Needs_Action → /Done workflow
   - Kill switch and timeout mechanisms
   - Write tests (3 minimum)
4. **Implement CEO Briefing** (Week 10):
   - Weekly scheduled task (Sunday 8 PM)
   - Gather data from Gmail, WhatsApp, Calendar, Odoo FTEs
   - Generate markdown briefing
   - Write tests (3 minimum)
5. **Implement Social Media FTEs** (Weeks 11+):
   - Facebook, Instagram, Twitter watchers
   - Content drafting skills
   - Engagement analysis
   - Write tests (4 minimum)
6. **Run validation gate**:
   ```bash
   ./scripts/run_validation_gates.sh gold
   ```
7. **Fix failures** until 100% pass rate
8. **Deploy** to production

---

**Last Updated**: 2026-02-26 | **Status**: Specifications Ready | **Tier**: Gold | **Next**: Implementation Week 7-8
