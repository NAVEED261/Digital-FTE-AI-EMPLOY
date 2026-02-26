# Quick Start Guide - AI Employee Bronze Tier

**Start here if you're new to the Digital FTE system.**

---

## 60-Second Setup

### Step 1: Start the Watcher
```bash
cd /mnt/d/Hackaton-0/AI_Employee_Vault
bash .watchers/start_watchers.sh
```

Output should show:
```
✅ Dependencies installed
🔧 Starting FileSystem Watcher...
📊 Current PM2 Status:
  fs-watcher  online  ...
✅ Watchers started successfully!
```

### Step 2: Test It Works
```bash
# Drop a file in Inbox
echo "Hello, AI Employee!" > /mnt/d/Hackaton-0/AI_Employee_Vault/Inbox/hello.txt

# Wait 5 seconds, then check Needs_Action
ls /mnt/d/Hackaton-0/AI_Employee_Vault/Needs_Action/
# Should show: hello.txt and hello_meta.txt
```

### Step 3: Ask Claude to Process It
```bash
claude "Please review the files in /Needs_Action/hello_meta.txt and tell me what Claude Code should do next"
```

---

## Daily Workflow

### Morning: Check Dashboard
```bash
# Open in your favorite editor
cat /mnt/d/Hackaton-0/AI_Employee_Vault/Dashboard.md

# You'll see:
# - System Status (watchers running?)
# - Today's Summary (tasks completed)
# - Needs Attention (pending items)
# - Recent Activity (what happened)
```

### Work: Drop Files for Processing
```bash
# Put any file in /Inbox for the AI Employee to handle
cp important_document.pdf /mnt/d/Hackaton-0/AI_Employee_Vault/Inbox/

# The watcher automatically moves it to /Needs_Action with metadata

# Ask Claude to process it:
claude "Process all files in /Needs_Action using the /file-processor skill"
```

### Decision: Review Pending Approvals
```bash
# Check what needs your approval
ls /mnt/d/Hackaton-0/AI_Employee_Vault/Pending_Approval/

# If you approve:
mv /mnt/d/Hackaton-0/AI_Employee_Vault/Pending_Approval/action.md \
   /mnt/d/Hackaton-0/AI_Employee_Vault/Approved/

# If you reject:
mv /mnt/d/Hackaton-0/AI_Employee_Vault/Pending_Approval/action.md \
   /mnt/d/Hackaton-0/AI_Employee_Vault/Rejected/
```

### Evening: Archive & Review
```bash
# Check what was completed today
ls /mnt/d/Hackaton-0/AI_Employee_Vault/Done/

# Archive old items (move to /Archive)
mv /mnt/d/Hackaton-0/AI_Employee_Vault/Done/*.md \
   /mnt/d/Hackaton-0/AI_Employee_Vault/Archive/

# Review logs for any issues
tail /mnt/d/Hackaton-0/AI_Employee_Vault/Logs/FileSystemWatcher.log
```

---

## Key Concepts

### The Five Folders (Core Workflow)

| Folder | What | When |
|--------|------|------|
| **Inbox** | User drops files here | Manual drop (one-time) |
| **Needs_Action** | Watcher moves files here | Auto (5s after drop) |
| **Pending_Approval** | Claude puts things here for you to decide | Auto (when needs HITL) |
| **Approved** | You approve Claude's actions | Manual (you move file) |
| **Done** | Completed tasks live here | Auto (after approval/execution) |

### Decision Flow

```
You drop file in /Inbox
                 ↓
Watcher moves to /Needs_Action (auto, 5 seconds)
                 ↓
Claude reads metadata file
                 ↓
Claude makes decision...
                 ├─ Low risk? → Move to /Done (auto)
                 └─ High risk? → Move to /Pending_Approval (ask you)
                                        ↓
                                  You review and:
                                  ├─ Approve → Move to /Approved
                                  └─ Reject → Move to /Rejected
```

### What Gets Auto-Approved?

See **Company_Handbook.md** section "Approval Thresholds":

✅ **Auto-Execute (no approval needed):**
- Email to known contact
- Text files < 1MB from known sources
- Payment < $50
- Data files with clear structure

🔒 **Requires Your Approval:**
- Email to new contact
- Payment ≥ $50
- Executable files
- Files from unknown sources

---

## Common Tasks

### ❓ How do I tell the AI Employee to do something?

**Option 1: Drop a file (simple)**
```bash
echo "Todo: Send invoice to client@example.com" > \
  /mnt/d/Hackaton-0/AI_Employee_Vault/Inbox/task.txt
```

**Option 2: Ask Claude directly (complex)**
```bash
claude "Process all files in /Needs_Action using /file-processor skill"
```

**Option 3: Add to Business_Goals.md (strategy)**
```bash
# Edit Business_Goals.md with new KPI
# Claude reads this file during weekly briefing (Gold tier)
```

### 🔍 How do I check what's pending?

```bash
# Quick check
ls /mnt/d/Hackaton-0/AI_Employee_Vault/Needs_Action/
ls /mnt/d/Hackaton-0/AI_Employee_Vault/Pending_Approval/

# Full view
claude "Summarize Dashboard.md and list all pending items"
```

### 📊 How do I see what the AI Employee did?

```bash
# Today's activity
ls -lt /mnt/d/Hackaton-0/AI_Employee_Vault/Done/ | head -5

# Full audit trail (JSON format)
cat /mnt/d/Hackaton-0/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json

# Recent log entries
tail -20 /mnt/d/Hackaton-0/AI_Employee_Vault/Logs/FileSystemWatcher.log
```

### ❌ Something went wrong. How do I fix it?

**Watcher crashed?**
```bash
# Restart it
pm2 restart fs-watcher

# Check status
pm2 status

# View error logs
pm2 logs fs-watcher --lines 50
```

**File stuck in /Needs_Action?**
```bash
# Move it manually to /Done when complete
mv /mnt/d/Hackaton-0/AI_Employee_Vault/Needs_Action/stuck_file.md \
   /mnt/d/Hackaton-0/AI_Employee_Vault/Done/

# Update Dashboard.md to reflect completion
```

**Not sure what happened?**
```bash
# Check logs
cat /mnt/d/Hackaton-0/AI_Employee_Vault/Logs/FileSystemWatcher.log | tail -50

# Ask Claude
claude "Analyze /Logs/FileSystemWatcher.log and tell me what went wrong"
```

---

## Important Rules

### ✅ DO:
- Drop files in /Inbox for the AI Employee to process
- Move files to /Approved when you want Claude to act
- Review /Logs regularly for anomalies
- Update Dashboard.md after major milestones
- Use /Rejected folder to decline actions

### ❌ DON'T:
- Edit /Needs_Action files directly (Claude owns this)
- Put API keys in anything that goes to git
- Skip approval for sensitive actions (email, payments)
- Delete /Logs files (keep 90-day retention)
- Run executable files without approval

---

## File Reference

| File | Purpose | Read | Write |
|------|---------|------|-------|
| Dashboard.md | System status | You | Claude (after actions) |
| Company_Handbook.md | AI behavior rules | Claude (before actions) | You (update rules) |
| Business_Goals.md | Revenue/KPI targets | Claude (monthly) | You (set goals) |
| README.md | Full documentation | You (reference) | Admin (rarely) |
| BRONZE_TIER_CHECKLIST.md | Acceptance criteria | You (verification) | Admin (rarely) |

---

## Keyboard Shortcuts (If Using Claude Code CLI)

```bash
# Check vault status
claude "Show Dashboard.md"

# Process files
claude "Run /file-processor on /Needs_Action"

# Move file to Done
claude "Move $FILE to /Done after processing"

# Start watcher
pm2 start fs-watcher

# View logs
pm2 logs fs-watcher --follow
```

---

## Next Steps After Bronze

### What's possible right now (Bronze):
- ✅ Monitor /Inbox 24/7
- ✅ Auto-generate processing plans
- ✅ Route to approval/done based on rules
- ✅ Full audit trail

### What's coming (Silver):
- 📧 Gmail watcher (auto-detect important emails)
- 💬 WhatsApp watcher (keyword detection)
- ✉️ Email MCP server (send/draft/search)
- 📆 Scheduled daily briefing
- 🤝 LinkedIn auto-posting

### What's possible later (Gold):
- 💰 Odoo accounting integration
- 📊 Weekly CEO briefing
- 🔄 Ralph Wiggum loop (multi-step persistence)
- 📱 Social media integration (Facebook, Instagram, Twitter)

---

## Support

**Not working?**
1. Check `/Logs/FileSystemWatcher.log`
2. Run `pm2 status`
3. Try: `pm2 restart fs-watcher`
4. Ask Claude: `claude "Debug: Why isn't the watcher working?"`

**Questions?**
- Drop in `/Inbox/question-{{date}}.md`
- Review `Company_Handbook.md` for behavior rules
- Check `README.md` for detailed docs

**Feature request?**
- Add to `/Inbox/feature-{{date}}.md`
- Discuss in `Dashboard.md` notes

---

## Success Metrics

After 1 week of using Bronze tier:
- [ ] Watcher running 24/7 without crashes
- [ ] At least 5 files processed successfully
- [ ] Dashboard updated with latest metrics
- [ ] No unexpected approvals needed
- [ ] Logs reviewed and no errors found

---

**Ready to use?** Start with Step 1 above!
**Need more?** Read `README.md` for complete guide.
**Ready for Silver?** Check `BRONZE_TIER_CHECKLIST.md` for completion status.

---

**Version:** 1.0 (Bronze Tier)
**Last Updated:** 2026-02-16
**Status:** ✅ Ready to use! 🚀
