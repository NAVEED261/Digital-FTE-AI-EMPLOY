# Specification: Weekly CEO Briefing (Gold Tier)

## Overview

Autonomous weekly business intelligence briefing generated every Sunday at 8:00 PM, synthesizing data from all FTE agents and external systems.

## Schedule

- **Frequency**: Weekly (every Sunday)
- **Time**: 8:00 PM UTC
- **Duration**: 5-10 minutes to generate
- **Output**: `AI_Employee_Vault/Plans/Monday_Briefing_<YYYY-MM-DD>.md`

## Content Structure

### 1. Executive Summary (Top 3 Items)

```markdown
## Executive Summary

🎯 **Key Wins This Week**:
- Revenue: $48,500 (↑12% from last week)
- Email auto-draft rate: 87% (Gmail FTE improvement)
- Calendar conflicts resolved: 23 (97% auto-resolved)

⚠️ **Concerns**:
- Pending approvals: 5 items awaiting review
- WhatsApp urgent messages: 3 payment-related

📈 **Next Week**:
- 12 scheduled client meetings
- $125K in pending invoices
- Launch new product announcement (scheduled for Tuesday)
```

### 2. Revenue & Financial Summary

```markdown
## 💰 Financial Performance

**This Week**:
- Total revenue: $48,500
- Average order value: $2,425
- Number of invoices: 20
- Paid: $42,000 (86%)
- Pending: $6,500 (14%)

**Month to Date**:
- Total: $186,750
- Target: $200,000 (93% achieved)
- Projection: On track

**Trend**:
📊 3-week moving average: $47,250 (stable)

**Top Customers**:
1. Acme Corp: $15,000
2. TechStart Inc: $12,500
3. Global Solutions: $10,000

**Invoices Needing Action**:
- Invoice #2401: $5,000 (due 2026-02-28)
- Invoice #2402: $1,500 (overdue 5 days)
```

### 3. Email Performance (Gmail FTE)

```markdown
## 📧 Email Management

**Volume**:
- Received: 124 emails
- Processed: 121 (98%)
- Pending: 3

**FTE Performance**:
- Auto-drafted: 105 (87% rate)
- Approved without change: 16 (94% accuracy)
- Rejected/redrafted: 2 (quality issues)
- Response time: avg 12 minutes

**HITL Approvals**:
- New contact emails: 4 (all approved)
- Sensitive keywords: 2 (legal-related, escalated)

**Engagement**:
- Clients with <2hr response: 89%
- Clients with >4hr response: 2 (followed up by SMS)
```

### 4. Messaging Performance (WhatsApp FTE)

```markdown
## 💬 WhatsApp Messages

**Volume**:
- Received: 34 messages
- Processed: 33 (97%)
- Auto-replied: 28 (82%)
- Escalated: 5 (payment-related)

**Urgency Classification**:
- High: 5 (payment, urgent)
- Medium: 8 (inquiries, requests)
- Low: 21 (general, updates)

**Response Time**:
- Urgent items: avg 4.2 minutes ✓ (SLO: <3 min)
- Other items: avg 18 minutes

**Issues**:
- ⚠️ Payment request #PY-203 awaiting approval (4 hours)
- ⚠️ Unknown sender from new vendor (awaiting classification)
```

### 5. Calendar & Scheduling (Calendar FTE)

```markdown
## 📅 Calendar Management

**This Week**:
- Events created: 8
- Conflicts detected: 12
- Auto-resolved: 12 (100%)
- Manual interventions: 0

**Conflict Examples Resolved**:
- Monday: Rescheduled team standup (moved 30min later)
- Tuesday: Rescheduled internal meeting (moved to Wednesday)
- Wednesday: Consolidated 3 overlapping calls into 2

**Next Week Schedule**:
- Client meetings: 12
- Internal meetings: 8
- Focus time blocks: 3
- Available slots: 4

**High-Priority Events**:
- 2026-02-28: Board meeting (2 hours, 10 attendees)
- 2026-03-01: Product launch event (half-day)
- 2026-03-03: Customer conference (attend virtually)
```

### 6. Social Media Summary

```markdown
## 📱 Social Media Performance

**Facebook**:
- Posts published: 3
- Engagement: 2.4K impressions, 156 interactions (6.5% rate)
- Top post: Product update (892 impressions)

**Instagram**:
- Stories posted: 7
- Reels: 2 (4.1K views, 312 likes)
- Engagement rate: 8.2% (above 5% target)

**Twitter/X**:
- Tweets: 12
- Impressions: 8.4K
- Engagement: 4.2% (replies + retweets)
- Trending: #YourTopic reached local trending at #7

**Opportunities**:
- Content A/B test: Version B outperformed by 34%
- Suggested topics: 3 trending hashtags align with products
```

### 7. Bottlenecks & Suggested Actions

```markdown
## 🚨 Bottlenecks & Recommendations

**Critical** 🔴:
1. Invoice #2402 overdue 5 days
   - Action: Send payment reminder today
   - Estimated impact: $1,500 recovered

2. Pending approval backlog: 5 items waiting
   - Action: Review /Pending_Approval folder (15 min)
   - Impact: Unblock 5 workflows

**High** 🟠:
3. WhatsApp payment request #PY-203 (4 hours pending)
   - Action: Approve payment or request more info
   - Impact: Customer satisfaction + cash flow

4. Email from new vendor (awaiting classification)
   - Action: Classify as vendor/supplier or spam
   - Impact: Establish relationship or block

**Medium** 🟡:
5. Product announcement scheduling
   - Suggestion: Publish Tuesday morning for max engagement
   - Timing: Aligned with 3 scheduled meetings that day

**Opportunities** 💡:
- Content strategy: Invest more in Reels (8.2% engagement)
- Customer outreach: Follow up with top 3 customers (monthly check-in)
- Automation: Create template for payment reminders (save 5 min/week)
```

### 8. Next Week Preview

```markdown
## 📋 Next Week (March 3-9, 2026)

**Key Events**:
- Monday (Mar 3): Weekly planning meeting
- Tuesday (Mar 4): Product launch event
- Wednesday (Mar 5): Customer conference (virtual)
- Friday (Mar 7): Board review meeting

**Pending Items to Address**:
- 3 approvals from this week (still pending)
- 2 overdue invoices (follow up)
- 1 new vendor relationship (verify legitimacy)

**Goals**:
- Launch product by Tuesday EOD
- Achieve 95%+ email response rate
- Maintain 99.5% uptime for all watchers
- Resolve 100% of urgent WhatsApp items

**Resource Allocation**:
- Time blocked for launch: 8 hours (Tuesday)
- Time blocked for conference: 4 hours (Wednesday)
- Expected free time: 14 hours (for other work)
```

## Implementation

### Schedule (Cron)

```bash
# Sunday 8:00 PM UTC
0 20 * * 0 /path/to/ceo-briefing.py >> /var/log/ceo-briefing.log 2>&1
```

### Data Sources

| Section | Source | API/Tool | Update Frequency |
|---------|--------|----------|-----------------|
| Revenue | Odoo | odoo-mcp | Real-time |
| Emails | Gmail | email-mcp | Real-time from logs |
| Messages | WhatsApp | browser-mcp | Real-time from logs |
| Calendar | Google Calendar | calendar-mcp | Real-time |
| Social Media | APIs | facebook-mcp, instagram-mcp, twitter-mcp | Real-time |

### Data Collection Logic

```python
def generate_ceo_briefing():
    """
    Generate weekly briefing from all FTE data sources.
    Runs every Sunday 8:00 PM UTC.
    """

    # 1. Gather data from last 7 days
    week_start = datetime.now() - timedelta(days=7)
    week_end = datetime.now()

    # 2. Revenue & Financial (from Odoo)
    revenue_data = odoo_mcp.get_revenue(week_start, week_end)
    invoices = odoo_mcp.get_invoices(status='all')

    # 3. Email Performance (from logs)
    email_logs = parse_logs(f'Logs/*gmail*.json', week_start, week_end)
    email_stats = aggregate_email_metrics(email_logs)

    # 4. WhatsApp Performance (from logs)
    whatsapp_logs = parse_logs(f'Logs/*whatsapp*.json', week_start, week_end)
    whatsapp_stats = aggregate_whatsapp_metrics(whatsapp_logs)

    # 5. Calendar Performance (from logs)
    calendar_logs = parse_logs(f'Logs/*calendar*.json', week_start, week_end)
    calendar_stats = aggregate_calendar_metrics(calendar_logs)

    # 6. Social Media (from MCP APIs)
    facebook_stats = facebook_mcp.get_analytics(week_start, week_end)
    instagram_stats = instagram_mcp.get_analytics(week_start, week_end)
    twitter_stats = twitter_mcp.get_analytics(week_start, week_end)

    # 7. Generate bottleneck analysis
    bottlenecks = identify_bottlenecks({
        'revenue': revenue_data,
        'emails': email_stats,
        'messages': whatsapp_stats,
        'calendar': calendar_stats,
        'social': [facebook_stats, instagram_stats, twitter_stats]
    })

    # 8. Create markdown briefing
    briefing_md = create_briefing_markdown({
        'summary': create_executive_summary(...),
        'financial': revenue_data,
        'email': email_stats,
        'whatsapp': whatsapp_stats,
        'calendar': calendar_stats,
        'social': [facebook_stats, instagram_stats, twitter_stats],
        'bottlenecks': bottlenecks,
        'next_week': forecast_next_week(...)
    })

    # 9. Save to vault
    briefing_path = vault_path / 'Plans' / f'Monday_Briefing_{date.today()}.md'
    briefing_path.write_text(briefing_md)

    # 10. Log generation
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': 'ceo_briefing_generated',
        'sections': 8,
        'data_sources': 6,
        'bottlenecks_identified': len(bottlenecks),
        'output': str(briefing_path)
    }
    append_audit_log(log_entry)

    return briefing_path
```

## Tests Required (3 tests for Gold tier)

1. `test_ceo_briefing_generation_completes`
   - Run briefing generator manually
   - Verify output file created
   - Verify file is readable markdown
   - Verify timestamp is current

2. `test_ceo_briefing_includes_all_sections`
   - Verify all 8 sections present
   - Verify headers match expected format
   - Verify no placeholder text remains
   - Verify metrics are numbers (not "pending")

3. `test_ceo_briefing_data_accuracy`
   - Compare briefing metrics with source systems
   - Revenue must match Odoo within 0.1%
   - Email count must match Gmail logs
   - WhatsApp count must match watcher logs
   - Calendar conflicts must match calendar API

## Security

- ✅ Read-only access to all APIs (no modifications)
- ✅ Data aggregation only (no sensitive details exposed)
- ✅ Audit log entry created for each generation
- ✅ Output file readable only by user (chmod 600)
- ✅ No credentials in briefing (only summary metrics)

## Monitoring

**Success Criteria**:
- File created by 8:15 PM every Sunday
- File size > 2 KB (meaningful content)
- No errors in generation log
- All 8 sections present and populated

**Alerts**:
- ⚠️ Warning: Generation takes >10 minutes
- ❌ Error: File not created by 8:30 PM
- ❌ Error: Missing data from >1 source
- ❌ Error: Invalid markdown syntax

---

**Created**: 2026-02-26 | **Status**: Ready for implementation | **Tier**: Gold | **Automation**: Sunday 8:00 PM UTC
