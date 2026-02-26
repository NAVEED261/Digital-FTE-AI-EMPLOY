# 🧪 Silver Tier Manual Testing Guide
**Fatima Zehra Digital FTE - Silver Tier Verification Checklist**

---

## 📋 Table of Contents
1. [Environment Setup Verification](#environment-setup-verification)
2. [Gmail FTE Testing](#gmail-fte-testing)
3. [WhatsApp FTE Testing](#whatsapp-fte-testing)
4. [HITL Workflow Testing](#hitl-workflow-testing)
5. [Obsidian Vault Verification](#obsidian-vault-verification)
6. [Dashboard Verification](#dashboard-verification)
7. [Complete End-to-End Testing](#complete-end-to-end-testing)
8. [Troubleshooting](#troubleshooting)

---

## 🔧 Environment Setup Verification

### Step 1: Check Python Installation
```bash
python3 --version
# Expected: Python 3.12.x or higher

python3 -c "import playwright; print('✅ Playwright installed')"
# Expected: ✅ Playwright installed

python3 -c "import google.auth; print('✅ Google Auth installed')"
# Expected: ✅ Google Auth installed
```

### Step 2: Verify Vault Path
```bash
ls -la /mnt/d/Hackaton-0/AI_Employee_Vault/
# Should show all 9 folders:
# Inbox  Needs_Action  Pending_Approval  Approved  Done  Rejected  Archive  Logs  Plans
```

### Step 3: Check Tier Structure
```bash
ls -la /mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/Tier_2_Silver/src/
# Should show: watchers/  skills/  mcp/

ls -la /mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/Tier_2_Silver/src/watchers/
# Should show: email_processor.py  email_classifier.py  email_responder.py  email_sender.py
#              whatsapp_watcher.py  whatsapp_processor.py  whatsapp_session_integrator.py
```

---

## 📧 Gmail FTE Testing

### Test 1: Email Processor - Extract Email Metadata
```bash
cd /mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/Tier_2_Silver/src/watchers

python3 << 'EOF'
from email_processor import EmailProcessor

processor = EmailProcessor()
print("✅ Email Processor initialized")

# Test with sample email metadata
sample_email = {
    'from': 'client@example.com',
    'subject': 'Invoice for February',
    'timestamp': '2026-02-27T10:30:00Z'
}

metadata = processor.extract_metadata(sample_email)
print(f"✅ Metadata extracted: {metadata}")
EOF
```

**Expected Output:**
```
✅ Email Processor initialized
✅ Metadata extracted: {'from': 'client@example.com', 'subject': 'Invoice for February', ...}
```

---

### Test 2: Email Classifier - Categorize by Priority
```bash
cd /mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/Tier_2_Silver/src/watchers

python3 << 'EOF'
from email_classifier import EmailClassifier

classifier = EmailClassifier()
print("✅ Email Classifier initialized")

# Test classifications
test_cases = [
    {'subject': 'URGENT: Payment Overdue', 'from': 'boss@company.com'},
    {'subject': 'Newsletter', 'from': 'news@example.com'},
    {'subject': 'New invoice received', 'from': 'finance@client.com'},
]

for test in test_cases:
    priority, category = classifier.classify(test)
    print(f"✅ {test['subject'][:20]}... → Priority: {priority}, Category: {category}")
EOF
```

**Expected Output:**
```
✅ Email Classifier initialized
✅ URGENT: Payment Overdue... → Priority: URGENT, Category: PAYMENT
✅ Newsletter → Priority: LOW, Category: NEWSLETTER
✅ New invoice received → Priority: HIGH, Category: INVOICE
```

---

### Test 3: Email Responder - Generate Draft Response
```bash
cd /mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/Tier_2_Silver/src/watchers

python3 << 'EOF'
from email_responder import EmailResponder

responder = EmailResponder()
print("✅ Email Responder initialized")

# Test draft generation
email = {
    'from': 'client@example.com',
    'subject': 'Project Status Update',
    'body': 'Can you provide an update on the project?'
}


draft = responder.generate_draft(email)
print(f"✅ Draft generated:\n{draft}")
EOF
```

**Expected Output:**
```
✅ Email Responder initialized
✅ Draft generated:
Dear Client,

Thank you for your inquiry...
[Complete draft response shown]
```

---

### Test 4: Email Sender - Verify SMTP Connection
```bash
cd /mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/Tier_2_Silver/src/watchers

python3 << 'EOF'
from email_sender import EmailSender

sender = EmailSender()
print("✅ Email Sender initialized")

# Test SMTP connection (without sending)
try:
    sender.verify_connection()
    print("✅ SMTP connection verified")
except Exception as e:
    print(f"❌ SMTP connection failed: {e}")
EOF
```

**Expected Output:**
```
✅ Email Sender initialized
✅ SMTP connection verified
```

---

### Test 5: Send Test Email
```bash
cd /mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/Tier_2_Silver/src/watchers

python3 << 'EOF'
from email_sender import EmailSender

sender = EmailSender()

# Send test email
result = sender.send(
    to='hafiznaveedchuhan@gmail.com',
    subject='Silver Tier Manual Test - Gmail FTE',
    body='This is a manual verification email for Silver Tier testing.\n\nTest Status: MANUAL_VERIFICATION'
)

if result['success']:
    print(f"✅ Email sent successfully!")
    print(f"   Message ID: {result['message_id']}")
else:
    print(f"❌ Email sending failed: {result['error']}")
EOF
```

**Expected Output:**
```
✅ Email sent successfully!
   Message ID: <timestamp>@mail.gmail.com
```

---

### Test 6: Verify Email Logs
```bash
tail -20 /mnt/d/Hackaton-0/AI_Employee_Vault/Logs/email_sender.log

# Should show latest entries like:
# [2026-02-27T10:30:00] EMAIL SENT
# To: hafiznaveedchuhan@gmail.com
# Subject: Silver Tier Manual Test - Gmail FTE
# Status: SUCCESS
```

---

## 💬 WhatsApp FTE Testing

### Test 1: WhatsApp Session Initialization
```bash
cd /mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/Tier_2_Silver/src/watchers

python3 << 'EOF'
import asyncio
from whatsapp_session_integrator import WhatsAppSessionIntegrator

async def test_init():
    integrator = WhatsAppSessionIntegrator(phone_number='03002385209')
    print("✅ WhatsApp Session Integrator initialized")
    print(f"   Phone: {integrator.phone_number}")
    print(f"   Vault Path: {integrator.vault_path}")

asyncio.run(test_init())
EOF
```

**Expected Output:**
```
✅ WhatsApp Session Integrator initialized
   Phone: 03002385209
   Vault Path: /mnt/d/Hackaton-0/AI_Employee_Vault
```

---

### Test 2: Check WhatsApp Backup Files
```bash
ls -lah /mnt/d/Hackaton-0/AI_Employee_Vault/Inbox/ | grep WA_BACKUP

# Should show files like:
# -rw-r--r-- 1 user group  315 Feb 27 15:56 WA_BACKUP_Self_20260227_015657.md
```

---

### Test 3: Verify WhatsApp Backup Format
```bash
cat /mnt/d/Hackaton-0/AI_Employee_Vault/Inbox/WA_BACKUP_Self_*.md

# Should show YAML frontmatter and message content:
# ---
# type: whatsapp_backup
# from: Self
# timestamp: 2026-02-27T01:56:57.280093
# status: backed_up
# ---
#
# # WhatsApp Message Backup
# hello how r u
```

---

### Test 4: Check WhatsApp Sent Messages Log
```bash
tail -20 /mnt/d/Hackaton-0/AI_Employee_Vault/Logs/whatsapp_sent_messages.log

# Should show entries like:
# [2026-02-27T01:56:57.306088] MESSAGE SENT
# To: Self
# Message: hello how r u
# Status: SENT
```

---

### Test 5: WhatsApp Message Processor Test
```bash
cd /mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/Tier_2_Silver/src/watchers

python3 << 'EOF'
from whatsapp_processor import WhatsAppProcessor

processor = WhatsAppProcessor()
print("✅ WhatsApp Processor initialized")

# Test message processing
test_messages = [
    {'sender': 'Self', 'text': 'Hello, how are you?', 'timestamp': '2026-02-27T10:00:00Z'},
    {'sender': 'Mom', 'text': 'URGENT: Please call ASAP', 'timestamp': '2026-02-27T10:05:00Z'},
    {'sender': 'Client', 'text': 'Payment received. Thank you!', 'timestamp': '2026-02-27T10:10:00Z'},
]

for msg in test_messages:
    priority, action = processor.classify(msg)
    print(f"✅ {msg['sender']}: {msg['text'][:20]}... → {priority} | {action}")
EOF
```

**Expected Output:**
```
✅ WhatsApp Processor initialized
✅ Self: Hello, how are you?... → LOW | ACKNOWLEDGE
✅ Mom: URGENT: Please call ASAP... → URGENT | ESCALATE
✅ Client: Payment received. Thank you... → MEDIUM | ACKNOWLEDGE
```

---

## ✋ HITL Workflow Testing

### Test 1: Check Pending Approval Folder
```bash
ls -la /mnt/d/Hackaton-0/AI_Employee_Vault/Pending_Approval/

# Should be empty or contain approval files with checkboxes
# Example file format:
# ---
# type: hitl_approval
# action: send_email
# recipient: new_contact@example.com
# status: pending
# ---
#
# [ ] APPROVE
# [ ] REJECT
# [ ] EDIT
```

---

### Test 2: Create a Test Approval File
```bash
cat > /mnt/d/Hackaton-0/AI_Employee_Vault/Pending_Approval/TEST_APPROVAL_$(date +%s).md << 'EOF'
---
type: hitl_approval
action: send_email
recipient: test@example.com
subject: Test Email
timestamp: $(date -Iseconds)
status: pending
---

# Manual Test - Email Approval Required

**Action:** Send email to test@example.com
**Subject:** Manual Silver Tier Test
**Body:** This is a manual verification test

Please approve or reject:

- [ ] APPROVE - Send the email
- [ ] REJECT - Don't send
- [ ] EDIT - Modify before sending
EOF

echo "✅ Test approval file created in Pending_Approval/"
```

---

### Test 3: Simulate User Approval
```bash
# List pending approvals
ls -1 /mnt/d/Hackaton-0/AI_Employee_Vault/Pending_Approval/

# Move to Approved (simulating user checking APPROVE checkbox)
mv /mnt/d/Hackaton-0/AI_Employee_Vault/Pending_Approval/TEST_APPROVAL_*.md \
   /mnt/d/Hackaton-0/AI_Employee_Vault/Approved/

echo "✅ File moved to Approved folder (simulating user approval)"

# Verify it moved
ls -1 /mnt/d/Hackaton-0/AI_Employee_Vault/Approved/
```

---

### Test 4: Check HITL Workflow Logs
```bash
tail -10 /mnt/d/Hackaton-0/AI_Employee_Vault/Logs/hitl_workflow.log

# Should show entries like:
# [2026-02-27T10:30:00] APPROVAL_CREATED: send_email to test@example.com
# [2026-02-27T10:31:00] APPROVAL_APPROVED: File moved to /Approved
```

---

## 🗂️ Obsidian Vault Verification

### Test 1: Complete Vault Audit
```bash
#!/bin/bash

VAULT="/mnt/d/Hackaton-0/AI_Employee_Vault"

echo "🔍 OBSIDIAN VAULT AUDIT"
echo "======================="
echo ""

# Check all folders
for folder in Inbox Needs_Action Pending_Approval Approved Done Rejected Archive Logs Plans; do
    count=$(find "$VAULT/$folder" -type f 2>/dev/null | wc -l)
    status="✅"
    if [ ! -d "$VAULT/$folder" ]; then
        status="❌"
    fi
    echo "$status $folder: $count files"
done

echo ""
echo "📊 RECENT LOGS:"
for logfile in $VAULT/Logs/*.log; do
    echo ""
    echo "$(basename $logfile):"
    tail -2 "$logfile" | sed 's/^/  /'
done
```

**Run this script:**
```bash
bash /tmp/vault_audit.sh
```

---

### Test 2: Check Vault Dashboard
```bash
cat /mnt/d/Hackaton-0/AI_Employee_Vault/Dashboard.md

# Should show:
# - Last Updated timestamp
# - System Status
# - Pending Actions count
# - Recent Activity
```

---

### Test 3: Verify Company Handbook
```bash
cat /mnt/d/Hackaton-0/AI_Employee_Vault/Company_Handbook.md

# Should contain:
# - Core Principles
# - Response Style Guidelines
# - Priority Levels
# - Approval Thresholds (HITL rules)
```

---

## 📊 Dashboard Verification

### Test 1: Check Dashboard is Running
```bash
# Open another terminal and navigate to dashboard
cd /mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/dashboard

# Start Python HTTP server (if not running)
python3 -m http.server 8080

# Output should show:
# Serving HTTP on 0.0.0.0 port 8080 (http://0.0.0.0:8080/) ...
```

---

### Test 2: Verify Dashboard Data File
```bash
cat /mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/dashboard/api/status.json

# Should show JSON with:
# - watchers.online / watchers.total
# - pending_actions count
# - pending_approvals count
# - recent_activity array
# - fte_metrics (gmail, whatsapp, calendar)
```

---

### Test 3: Manual Dashboard Status Update
```bash
python3 << 'EOF'
import json
from datetime import datetime

status_file = '/mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/dashboard/api/status.json'

# Read current status
with open(status_file, 'r') as f:
    status = json.load(f)

# Update with current counts
import os
vault_path = '/mnt/d/Hackaton-0/AI_Employee_Vault'

status['timestamp'] = datetime.now().isoformat()
status['pending_actions'] = len(os.listdir(f'{vault_path}/Needs_Action'))
status['pending_approvals'] = len(os.listdir(f'{vault_path}/Pending_Approval'))
status['completed_today'] = len(os.listdir(f'{vault_path}/Done'))

# Write back
with open(status_file, 'w') as f:
    json.dump(status, f, indent=2)

print("✅ Dashboard status updated")
print(f"   Timestamp: {status['timestamp']}")
print(f"   Pending Actions: {status['pending_actions']}")
print(f"   Pending Approvals: {status['pending_approvals']}")
print(f"   Completed: {status['completed_today']}")
EOF
```

---

## 🔄 Complete End-to-End Testing

### Full Workflow Test (5-10 minutes)

**Step 1: Create Email in Inbox**
```bash
cat > /mnt/d/Hackaton-0/AI_Employee_Vault/Inbox/E2E_TEST_EMAIL_$(date +%s).md << 'EOF'
---
type: email_inbox
from: client@example.com
subject: Project Inquiry - E2E Test
timestamp: $(date -Iseconds)
status: new
---

# Incoming Email

**From:** client@example.com
**Subject:** Project Inquiry - E2E Test
**Body:** Can you provide an update on the project timeline?
EOF

echo "✅ Step 1: Test email created in Inbox"
```

---

**Step 2: Process Email (Simulate File Movement)**
```bash
# Move to Needs_Action
mv /mnt/d/Hackaton-0/AI_Employee_Vault/Inbox/E2E_TEST_EMAIL_*.md \
   /mnt/d/Hackaton-0/AI_Employee_Vault/Needs_Action/

echo "✅ Step 2: Email moved to Needs_Action (processing queue)"
```

---

**Step 3: Create Approval Request**
```bash
cat > /mnt/d/Hackaton-0/AI_Employee_Vault/Pending_Approval/E2E_TEST_APPROVAL_$(date +%s).md << 'EOF'
---
type: hitl_approval
action: send_email
recipient: client@example.com
subject: Re: Project Inquiry - E2E Test
timestamp: $(date -Iseconds)
status: pending
---

# Email Approval Required

**Draft Response:**

Thank you for your inquiry. Here's the current project status:

The project is proceeding on schedule. We expect completion by March 15th.

---

Please verify this response:

- [ ] APPROVE - Send the email
- [ ] REJECT - Don't send
- [ ] EDIT - Modify the response
EOF

echo "✅ Step 3: Approval request created in Pending_Approval"
```

---

**Step 4: User Approves (Simulate)**
```bash
# Move to Approved
mv /mnt/d/Hackaton-0/AI_Employee_Vault/Pending_Approval/E2E_TEST_APPROVAL_*.md \
   /mnt/d/Hackaton-0/AI_Employee_Vault/Approved/

echo "✅ Step 4: User approved - file moved to Approved"
```

---

**Step 5: Execute Action (Send Email)**
```bash
cd /mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/Tier_2_Silver/src/watchers

python3 << 'EOF'
from email_sender import EmailSender

sender = EmailSender()

result = sender.send(
    to='client@example.com',
    subject='Re: Project Inquiry - E2E Test',
    body='Thank you for your inquiry. Here is the project status:\n\nThe project is proceeding on schedule. We expect completion by March 15th.'
)

if result['success']:
    print(f"✅ Step 5: Email sent successfully (Message ID: {result['message_id']})")
else:
    print(f"❌ Step 5: Email sending failed: {result['error']}")
EOF
```

---

**Step 6: Mark as Done**
```bash
# Move to Done
mv /mnt/d/Hackaton-0/AI_Employee_Vault/Approved/E2E_TEST_APPROVAL_*.md \
   /mnt/d/Hackaton-0/AI_Employee_Vault/Done/

echo "✅ Step 6: Task completed - file moved to Done"
```

---

**Step 7: Verify Complete Workflow**
```bash
echo "✅ E2E TEST COMPLETE!"
echo ""
echo "Verification:"
echo "- Inbox: $(ls /mnt/d/Hackaton-0/AI_Employee_Vault/Inbox/ | wc -l) files"
echo "- Needs_Action: $(ls /mnt/d/Hackaton-0/AI_Employee_Vault/Needs_Action/ | wc -l) files"
echo "- Pending_Approval: $(ls /mnt/d/Hackaton-0/AI_Employee_Vault/Pending_Approval/ | wc -l) files"
echo "- Approved: $(ls /mnt/d/Hackaton-0/AI_Employee_Vault/Approved/ | wc -l) files"
echo "- Done: $(ls /mnt/d/Hackaton-0/AI_Employee_Vault/Done/ | wc -l) files"
echo ""
echo "Latest log entries:"
tail -3 /mnt/d/Hackaton-0/AI_Employee_Vault/Logs/email_sender.log
```

---

## 🐛 Troubleshooting

### Issue: SMTP Authentication Failed
```bash
# Check if App Password is set in .env
cat /mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/Tier_2_Silver/.env | grep GMAIL_APP_PASSWORD

# If missing, set it:
export GMAIL_APP_PASSWORD="your_app_password"

# Test connection
python3 -c "from email_sender import EmailSender; EmailSender().verify_connection()"
```

---

### Issue: Playwright Browser Timeout
```bash
# Check if Playwright browsers are installed
playwright install chromium

# Try running WhatsApp integrator with debug output
python3 -c "import logging; logging.basicConfig(level=logging.DEBUG)" && \
  python3 /mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/Tier_2_Silver/src/watchers/whatsapp_session_integrator.py
```

---

### Issue: Vault Folder Not Found
```bash
# Create missing folders
mkdir -p /mnt/d/Hackaton-0/AI_Employee_Vault/{Inbox,Needs_Action,Pending_Approval,Approved,Done,Rejected,Archive,Logs,Plans}

# Verify creation
ls -la /mnt/d/Hackaton-0/AI_Employee_Vault/
```

---

### Issue: Dashboard Not Loading
```bash
# Check if HTTP server is running
lsof -i :8080

# If not running, start it:
cd /mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/dashboard
python3 -m http.server 8080 &

# Test connection
curl http://localhost:8080
```

---

## ✅ Silver Tier Checklist

Use this checklist to verify everything is working:

- [ ] **Gmail FTE**
  - [ ] Email Processor extracts metadata ✅
  - [ ] Email Classifier categorizes correctly ✅
  - [ ] Email Responder generates drafts ✅
  - [ ] Email Sender connects to SMTP ✅
  - [ ] Test email sent successfully ✅
  - [ ] Email logs updated ✅

- [ ] **WhatsApp FTE**
  - [ ] WhatsApp Integrator initialized ✅
  - [ ] Backup files created in Inbox ✅
  - [ ] Backup format correct (YAML) ✅
  - [ ] Sent messages logged ✅
  - [ ] Message processor classifies correctly ✅

- [ ] **HITL Workflow**
  - [ ] Pending_Approval folder exists ✅
  - [ ] Approval files have checkboxes ✅
  - [ ] Files move to Approved correctly ✅
  - [ ] HITL logs show all actions ✅

- [ ] **Obsidian Vault**
  - [ ] All 9 folders present ✅
  - [ ] All 14 log files exist ✅
  - [ ] Recent activity logged ✅
  - [ ] Dashboard.md readable ✅
  - [ ] Company_Handbook.md accessible ✅

- [ ] **Dashboard UI**
  - [ ] HTML loads at http://localhost:8080 ✅
  - [ ] All 4 status cards display ✅
  - [ ] FTE metrics visible ✅
  - [ ] Recent activity shown ✅
  - [ ] Quick action buttons functional ✅

- [ ] **Complete E2E Workflow**
  - [ ] Email moves through all folders ✅
  - [ ] HITL approval process works ✅
  - [ ] Final execution succeeds ✅
  - [ ] Logs updated throughout ✅

---

## 🎯 Quick Test Commands (Copy & Paste)

**Test Everything in One Go:**
```bash
# 1. Check environment
python3 --version && python3 -c "import playwright; print('✅ Playwright')" && python3 -c "import google.auth; print('✅ Google')"

# 2. Check vault
echo "📁 Vault folders:" && ls -d /mnt/d/Hackaton-0/AI_Employee_Vault/*/

# 3. Check logs
echo "📊 Latest logs:" && tail -1 /mnt/d/Hackaton-0/AI_Employee_Vault/Logs/*.log

# 4. Check dashboard
echo "🌐 Dashboard:" && curl -s http://localhost:8080 | head -20

# 5. Test email
cd /mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/Tier_2_Silver/src/watchers && python3 -c "from email_sender import EmailSender; s = EmailSender(); r = s.verify_connection(); print('✅ Email ready' if r else '❌ Email failed')"
```

---

**Date Created:** 2026-02-27
**Testing Framework:** Manual Terminal-Based Verification
**Status:** Ready for User Testing ✅

