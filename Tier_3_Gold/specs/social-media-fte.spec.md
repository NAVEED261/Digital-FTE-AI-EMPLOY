# Specification: Social Media FTE Agent (Gold Tier)

## Agent Definition

```yaml
Name: Social Media FTE
Tier: Gold
Type: Social Media Management Specialist
Status: Ready for Implementation
Dependencies: facebook-mcp, instagram-mcp, twitter-mcp
Platforms: Facebook, Instagram, Twitter/X
Timeline: Week 11+
Success Criteria: 4/15 tests passing (part of Gold validation gate)
```

## Purpose

Autonomous social media management FTE that:
- Drafts posts from business goals
- Schedules posts (with HITL approval)
- Monitors engagement metrics
- Analyzes trending topics
- Auto-replies to messages (with safety limits)

## Triggers & Perception

### Facebook Watcher
- **Interval**: Every 30 minutes
- **Method**: Facebook Graph API
- **Query**: New comments, messages, engagement
- **Action**: Creates action file for engagement or approves auto-reply

### Instagram Watcher
- **Interval**: Every hour
- **Method**: Instagram Graph API
- **Query**: Story analytics, reel engagement, DMs
- **Action**: Creates action file for trending topics

### Twitter Watcher
- **Interval**: Every 15 minutes
- **Method**: Twitter API v2
- **Query**: Mentions, replies, trending hashtags
- **Action**: Creates action file for engagement or auto-reply

## FTE Behaviors

### Content Drafting

**Trigger**: Business goals updated in `Company_Handbook.md`

**Process**:
1. Read weekly business goals
2. Identify content opportunities
3. Draft 3-5 posts for each platform
4. Create variations for A/B testing
5. Move to /Pending_Approval for review

**HITL**: User reviews and approves posts before publishing

### Engagement Monitoring

**Trigger**: Watcher detects new engagement

**Process**:
1. Extract mention/reply/comment
2. Classify sentiment (positive, neutral, negative)
3. Determine response appropriateness
4. For simple acknowledgments: Auto-reply
5. For complex inquiries: Escalate to /Pending_Approval

**HITL**: Complex inquiries require user approval before responding

### Analytics & Trending

**Trigger**: Every 6 hours

**Process**:
1. Fetch analytics from all platforms
2. Calculate engagement metrics
3. Identify trending hashtags
4. Recommend content improvements
5. Update briefing data for CEO summary

## Skills Required

### 1. social-processor
- Extract social media content structure
- Parse posts, stories, reels
- Identify hashtags and mentions
- 100% test coverage required

### 2. content-drafter
- Draft posts from business goals
- Maintain brand voice across platforms
- Generate platform-specific variations (Facebook ≠ Twitter)
- Create A/B testing variations
- 100% test coverage required

### 3. engagement-analyzer
- Calculate engagement rate: (likes + comments + shares) / impressions
- Track trending topics
- Monitor audience growth
- Identify top-performing content types
- 100% test coverage required

## MCP Servers

### facebook-mcp
- `create_post(content, image_urls)` – Create post (requires draft approval)
- `schedule_post(content, image_urls, publish_time)` – Schedule for future
- `get_feed()` – Retrieve feed comments/reactions
- `reply_message(message_id, content)` – Reply to comment/DM
- `get_insights(metric)` – Get analytics (reach, engagement, followers)

### instagram-mcp
- `create_story(image_urls, text_overlay)` – Create story
- `schedule_reel(video_url, caption, publish_time)` – Schedule reel
- `get_feed()` – Retrieve story analytics, DMs
- `reply_dm(user_id, content)` – Reply to DM
- `get_insights()` – Engagement metrics

### twitter-mcp
- `create_tweet(content, image_urls)` – Post tweet (requires draft approval)
- `schedule_tweet(content, image_urls, publish_time)` – Schedule tweet
- `get_mentions()` – Retrieve mentions/replies
- `reply_tweet(tweet_id, content)` – Reply to tweet
- `get_analytics()` – Tweet performance metrics

## Content Approval Workflow

```
Business Goals Updated
        ↓
Social Media FTE detects change
        ↓
Draft 3-5 posts per platform
        ↓
Create variations for A/B testing
        ↓
Move drafts to /Pending_Approval
        ↓
User reviews drafts in /Pending_Approval
        ├─→ APPROVED: Move to /Approved
        │   ↓
        │   Schedule/publish via MCP
        │   ↓
        │   Log to /Logs
        │   ↓
        │   Move to /Done
        │
        └─→ REJECTED: Move to /Done (marked failed)
            User can edit and resubmit
```

## Engagement Response Workflow

```
Comment/Reply/DM Detected
        ↓
Classify sentiment & complexity
        │
        ├─→ SIMPLE ACK (positive, known responder)
        │   ↓
        │   Auto-reply with gratitude
        │   Log action
        │   Done
        │
        ├─→ COMPLEX INQUIRY
        │   ↓
        │   Move to /Pending_Approval
        │   User drafts response
        │   ↓
        │   If approved: Send via MCP
        │   If rejected: Mark as reviewed
        │   Move to /Done
        │
        └─→ NEGATIVE/TROLLING
            ↓
            Classify severity
            ├─→ MINOR: Ignore (no response)
            └─→ MAJOR: Escalate to /Pending_Approval
                User decides action
```

## HITL Thresholds

| Scenario | Risk | Action |
|----------|------|--------|
| Auto-publish scheduled post | Low | Auto-approve |
| Post draft for review | Medium | Require approval |
| Reply to positive comment | Low | Auto-reply |
| Reply to inquiry | Medium | Create approval |
| Reply to complaint | High | Create approval |
| Follow/connect with user | Medium | Require approval |
| Unfollow/block user | High | Require approval |

## Tests Required (4 tests for Gold tier)

1. `test_facebook_post_draft_creation` – Posts drafted correctly
2. `test_twitter_tweet_scheduling` – Tweets scheduled correctly
3. `test_instagram_story_analytics` – Analytics retrieved and calculated
4. `test_social_media_engagement_response` – Auto-replies sent appropriately

## Content Strategy

### Posting Schedule

```
Facebook: 3x per week (Mon, Wed, Fri 9:00 AM)
Instagram: Daily (5:00 PM) + 2 stories (9:00 AM, 6:00 PM)
Twitter: 2-3x per day (9:00 AM, 12:00 PM, 6:00 PM)
```

### Post Types

**Promotional** (40%):
- Product updates
- New features
- Special offers
- Case studies

**Engagement** (35%):
- Behind-the-scenes
- Team highlights
- Industry tips
- Q&A threads

**Trending** (20%):
- News commentary
- Trending hashtags
- Viral opportunities
- Current events

**Community** (5%):
- Thank you posts
- Milestone celebrations
- Partner highlights

### Brand Voice

- **Tone**: Professional + approachable
- **Formality**: Medium (not too casual, not corporate)
- **Authenticity**: Genuine, show personality
- **Responsiveness**: Quick acknowledgment, thoughtful replies

## Analytics & Reporting

**Metrics Tracked**:
- Reach: Number of unique users who saw post
- Impressions: Total views (may include repeats)
- Engagement Rate: (Likes + Comments + Shares) / Impressions × 100
- Click-through Rate: Clicks / Impressions × 100
- Follower Growth: Weekly change in followers
- Sentiment: % positive, neutral, negative comments

**Reporting**:
- Daily: High-performing posts (>5% engagement)
- Weekly: Analytics summary (section of CEO briefing)
- Monthly: Trend analysis and strategy adjustments

## Security & Compliance

- ✅ All posts require drafting (can be auto-approved, but not auto-sent)
- ✅ Brand voice consistency (Claude maintains tone)
- ✅ No false/misleading claims (content must be truthful)
- ✅ No political/controversial posts (unless explicitly approved)
- ✅ GDPR compliance (no user data sharing)
- ✅ Audit logging (all posts, replies, deletions logged)

## Known Limitations

| Issue | Mitigation |
|-------|-----------|
| Can't detect scams/bots | Manual review of unusual followers |
| Rate limits per platform | Queue and retry with backoff |
| Instagram video processing slow | Batch processing overnight |
| Twitter API changes | Monitor API docs, update specs |

## Dependencies

- facebook-sdk, instagrapi, tweepy (Python libraries)
-@anthropic-sdk/sdk, express (Node.js for MCP servers)
- pytest (testing)

---

**Created**: 2026-02-26 | **Status**: Ready for implementation | **Tier**: Gold | **Platforms**: 3 (Facebook, Instagram, Twitter)
