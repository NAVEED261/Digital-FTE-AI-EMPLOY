# ✅ Silver Tier Manual Testing Checklist
**Fatima Zehra Digital FTE - Print This & Check Off As You Test**

---

## 📋 Master Checklist - Mark Your Progress

```
SILVER TIER READINESS:
☐ Environment setup verified
☐ Vault structure complete
☐ Gmail FTE operational
☐ WhatsApp FTE operational
☐ HITL workflow tested
☐ Dashboard confirmed working
☐ Complete E2E test passed
☐ All logs verified
```

---

## 🔧 PHASE 1: Environment Setup (5 minutes)

### Check 1.1: Python & Dependencies
```bash
python3 --version
# Expected: Python 3.12.x ✅
# Status: [ ]

# Check Playwright
python3 -c "import playwright; print('✅ Playwright')"
# Expected: ✅ Playwright ✅
# Status: [ ]

# Check Google Auth
python3 -c "import google.auth; print('✅ Google Auth')"
# Expected: ✅ Google Auth ✅
# Status: [ ]
```

### Check 1.2: Directory Structure
```bash
ls -la /mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/Tier_2_Silver/
# Expected: src/  specs/  tests/  .env
# Status: [ ]
```

---

## 📧 PHASE 2: Gmail FTE Testing (10-15 minutes)

### Check 2.1: Email Processor Module
```bash
cd /mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/Tier_2_Silver/src/watchers
python3 << 'EOF'
from email_processor import EmailProcessor
processor = EmailProcessor()
print("✅ Email Processor initialized")
EOF
```
- **Expected:** ✅ Email Processor initialized
- **Status:** [ ]
- **Timestamp:** _________

### Check 2.2: Email Classifier
```bash
python3 << 'EOF'
from email_classifier import EmailClassifier
classifier = EmailClassifier()
priority, category = classifier.classify({
    'subject': 'URGENT: Invoice',
    'from': 'finance@client.com'
})
print(f"Priority: {priority}, Category: {category}")
EOF
```
- **Expected:** Priority: URGENT, Category: INVOICE
- **Status:** [ ]
- **Notes:** _________

### Check 2.3: Email Responder
```bash
python3 << 'EOF'
from email_responder import EmailResponder
responder = EmailResponder()
draft = responder.generate_draft({
    'from': 'client@example.com',
    'subject': 'Project Status'
})
print("✅ Draft generated")
EOF
```
- **Expected:** ✅ Draft generated
- **Status:** [ ]

### Check 2.4: SMTP Connection Verify
```bash
python3 << 'EOF'
from email_sender import EmailSender
sender = EmailSender()
try:
    sender.verify_connection()
    print("✅ SMTP connection verified")
except Exception as e:
    print(f"❌ SMTP failed: {e}")
EOF
```
- **Expected:** ✅ SMTP connection verified
- **Status:** [ ]
- **Timestamp:** _________

### Check 2.5: Send Live Test Email
```bash
python3 << 'EOF'
from email_sender import EmailSender
sender = EmailSender()
result = sender.send(
    to='hafiznaveedchuhan@gmail.com',
    subject='Silver Tier Manual Test - Verification',
    body='This is a manual verification email.\n\nTest Status: PASSING'
)
if result['success']:
    print(f"✅ Email sent! Message ID: {result['message_id']}")
else:
    print(f"❌ Failed: {result['error']}")
EOF
```
- **Expected:** ✅ Email sent!
- **Status:** [ ]
- **Actual Message ID:** _________
- **Email Check:** Check your inbox at hafiznaveedchuhan@gmail.com [ ]

### Check 2.6: Email Logs Verification
```bash
tail -5 /mnt/d/Hackaton-0/AI_Employee_Vault/Logs/email_sender.log
```
- **Expected:** Recent entries showing EMAIL SENT
- **Status:** [ ]
- **Latest Entry:** _________________________

---

## 💬 PHASE 3: WhatsApp FTE Testing (10-15 minutes)

### Check 3.1: WhatsApp Integrator Module
```bash
python3 << 'EOF'
import asyncio
from whatsapp_session_integrator import WhatsAppSessionIntegrator

async def test():
    integrator = WhatsAppSessionIntegrator(phone_number='03002385209')
    print("✅ WhatsApp integrator initialized")

asyncio.run(test())
EOF
```
- **Expected:** ✅ WhatsApp integrator initialized
- **Status:** [ ]

### Check 3.2: WhatsApp Backup Files
```bash
ls -lah /mnt/d/Hackaton-0/AI_Employee_Vault/Inbox/WA_BACKUP_*
```
- **Expected:** WA_BACKUP_Self_*.md files
- **Count:** _____ files
- **Status:** [ ]

### Check 3.3: Backup File Format
```bash
cat /mnt/d/Hackaton-0/AI_Employee_Vault/Inbox/WA_BACKUP_Self_*.md
```
- **Expected:** YAML frontmatter + message content
- **Has YAML:** [ ]
- **Has Message:** [ ]
- **Valid Format:** [ ]

### Check 3.4: WhatsApp Processor
```bash
python3 << 'EOF'
from whatsapp_processor import WhatsAppProcessor
processor = WhatsAppProcessor()
priority, action = processor.classify({
    'sender': 'Mom',
    'text': 'URGENT: Please call ASAP'
})
print(f"Priority: {priority}, Action: {action}")
EOF
```
- **Expected:** Priority: URGENT, Action: ESCALATE
- **Status:** [ ]

### Check 3.5: Sent Messages Log
```bash
tail -5 /mnt/d/Hackaton-0/AI_Employee_Vault/Logs/whatsapp_sent_messages.log
```
- **Expected:** Recent MESSAGE SENT entries
- **Status:** [ ]
- **Latest:** _________________________

---

## ✋ PHASE 4: HITL Workflow Testing (15-20 minutes)

### Check 4.1: Create Approval File
```bash
cat > /mnt/d/Hackaton-0/AI_Employee_Vault/Pending_Approval/MANUAL_TEST_APPROVAL_$(date +%s).md << 'EOF'
---
type: hitl_approval
action: send_email
recipient: hafiznaveedchuhan@gmail.com
subject: Manual HITL Test
timestamp: 2026-02-27
status: pending
---

# Manual HITL Test

Please approve this test email:

- [ ] APPROVE
- [ ] REJECT
- [ ] EDIT
EOF

echo "✅ Approval file created"
ls /mnt/d/Hackaton-0/AI_Employee_Vault/Pending_Approval/ | wc -l
```
- **Expected:** ✅ Approval file created
- **Files in Pending_Approval:** _____
- **Status:** [ ]

### Check 4.2: Simulate User Approval
```bash
# Move file from Pending_Approval to Approved
file=$(ls /mnt/d/Hackaton-0/AI_Employee_Vault/Pending_Approval/MANUAL_TEST_*.md | head -1)
mv "$file" /mnt/d/Hackaton-0/AI_Employee_Vault/Approved/

echo "✅ File moved to Approved"
```
- **Expected:** ✅ File moved to Approved
- **Status:** [ ]

### Check 4.3: Verify File Moved
```bash
echo "Pending_Approval count:"
ls /mnt/d/Hackaton-0/AI_Employee_Vault/Pending_Approval/ | wc -l

echo "Approved count:"
ls /mnt/d/Hackaton-0/AI_Employee_Vault/Approved/ | wc -l
```
- **Expected:** Pending=0, Approved≥1
- **Pending Count:** _____
- **Approved Count:** _____
- **Status:** [ ]

### Check 4.4: Check HITL Logs
```bash
tail -10 /mnt/d/Hackaton-0/AI_Employee_Vault/Logs/hitl_workflow.log
```
- **Expected:** Log entries showing approval workflow
- **Has Entries:** [ ]
- **Latest Action:** _________________________

---

## 🗂️ PHASE 5: Obsidian Vault Verification (10 minutes)

### Check 5.1: All Folders Present
```bash
for folder in Inbox Needs_Action Pending_Approval Approved Done Rejected Archive Logs Plans; do
    [ -d "/mnt/d/Hackaton-0/AI_Employee_Vault/$folder" ] && echo "✅ $folder" || echo "❌ $folder"
done
```

| Folder | Status |
|--------|--------|
| Inbox | [ ] |
| Needs_Action | [ ] |
| Pending_Approval | [ ] |
| Approved | [ ] |
| Done | [ ] |
| Rejected | [ ] |
| Archive | [ ] |
| Logs | [ ] |
| Plans | [ ] |

### Check 5.2: File Counts
```bash
VAULT="/mnt/d/Hackaton-0/AI_Employee_Vault"
echo "Inbox: $(ls -1 $VAULT/Inbox | wc -l)"
echo "Needs_Action: $(ls -1 $VAULT/Needs_Action | wc -l)"
echo "Done: $(ls -1 $VAULT/Done | wc -l)"
echo "Logs: $(ls -1 $VAULT/Logs | wc -l)"
```

| Folder | Count | Status |
|--------|-------|--------|
| Inbox | _____ | [ ] |
| Needs_Action | _____ | [ ] |
| Done | _____ | [ ] |
| Logs | _____ (14+) | [ ] |

### Check 5.3: Dashboard.md Readable
```bash
head -20 /mnt/d/Hackaton-0/AI_Employee_Vault/Dashboard.md
```
- **Readable:** [ ]
- **Has Status:** [ ]
- **Has Pending Count:** [ ]

### Check 5.4: Company Handbook Present
```bash
head -10 /mnt/d/Hackaton-0/AI_Employee_Vault/Company_Handbook.md
```
- **File Exists:** [ ]
- **Has Core Principles:** [ ]
- **Has Approval Thresholds:** [ ]

---

## 📊 PHASE 6: Dashboard UI Verification (5 minutes)

### Check 6.1: Dashboard Loads
```bash
curl -s http://localhost:8080 | head -1
# Should show HTML header
```
- **Loads Successfully:** [ ]
- **HTTP Status:** _____

### Check 6.2: Status Cards Display
**Visit:** http://localhost:8080 in browser

- [ ] Watchers card visible (showing 1/3)
- [ ] Pending Actions card visible (showing 0)
- [ ] Approvals Needed card visible (showing 0)
- [ ] Completed Today card visible (showing 0)

### Check 6.3: FTE Metrics Visible
- [ ] Gmail FTE section visible
- [ ] WhatsApp FTE section visible
- [ ] Calendar FTE section visible
- [ ] Metrics values display (0 expected for new data)

### Check 6.4: Recent Activity Timeline
- [ ] Timeline section visible
- [ ] At least 3 entries shown
- [ ] Timestamps correct

### Check 6.5: Quick Action Buttons
- [ ] "Restart All Watchers" button present
- [ ] "View Pending Approvals" button present
- [ ] "Generate CEO Briefing" button present
- [ ] "View Constitution" button present

---

## 🔄 PHASE 7: Complete End-to-End Test (20-30 minutes)

### E2E Test Steps:

**Step 1: Create Test Email**
```bash
cat > /mnt/d/Hackaton-0/AI_Employee_Vault/Inbox/E2E_TEST_$(date +%s).md << 'EOF'
---
type: email_test
from: e2e.test@example.com
subject: End-to-End Test Email
---
Test email for complete workflow
EOF
echo "✅ Created"
```
- **Status:** [ ] Created
- **Timestamp:** _________

**Step 2: Move to Needs_Action**
```bash
file=$(ls /mnt/d/Hackaton-0/AI_Employee_Vault/Inbox/E2E_TEST_*.md | head -1)
mv "$file" /mnt/d/Hackaton-0/AI_Employee_Vault/Needs_Action/
echo "✅ Moved to Needs_Action"
```
- **Status:** [ ] Moved
- **Timestamp:** _________

**Step 3: Create Approval**
```bash
cat > /mnt/d/Hackaton-0/AI_Employee_Vault/Pending_Approval/E2E_APPROVAL_$(date +%s).md << 'EOF'
---
type: hitl_approval
action: send_email
recipient: e2e.test@example.com
---
- [ ] APPROVE
- [ ] REJECT
EOF
echo "✅ Approval created"
```
- **Status:** [ ] Created
- **Timestamp:** _________

**Step 4: Approve (Simulate User)**
```bash
file=$(ls /mnt/d/Hackaton-0/AI_Employee_Vault/Pending_Approval/E2E_APPROVAL_*.md | head -1)
mv "$file" /mnt/d/Hackaton-0/AI_Employee_Vault/Approved/
echo "✅ Approved"
```
- **Status:** [ ] Approved
- **Timestamp:** _________

**Step 5: Execute (Send Email)**
```bash
cd /mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/Tier_2_Silver/src/watchers
python3 << 'EOF'
from email_sender import EmailSender
sender = EmailSender()
result = sender.send(
    to='e2e.test@example.com',
    subject='End-to-End Test - Manual Verification',
    body='E2E test email sent successfully'
)
print("✅ Email sent" if result['success'] else f"❌ Failed: {result['error']}")
EOF
```
- **Status:** [ ] Sent
- **Timestamp:** _________

**Step 6: Move to Done**
```bash
file=$(ls /mnt/d/Hackaton-0/AI_Employee_Vault/Approved/E2E_APPROVAL_*.md | head -1)
mv "$file" /mnt/d/Hackaton-0/AI_Employee_Vault/Done/
echo "✅ Moved to Done"
```
- **Status:** [ ] Done
- **Timestamp:** _________

**Step 7: Verify Complete Flow**
```bash
echo "Inbox: $(ls -1 /mnt/d/Hackaton-0/AI_Employee_Vault/Inbox | wc -l)"
echo "Needs_Action: $(ls -1 /mnt/d/Hackaton-0/AI_Employee_Vault/Needs_Action | wc -l)"
echo "Pending_Approval: $(ls -1 /mnt/d/Hackaton-0/AI_Employee_Vault/Pending_Approval | wc -l)"
echo "Approved: $(ls -1 /mnt/d/Hackaton-0/AI_Employee_Vault/Approved | wc -l)"
echo "Done: $(ls -1 /mnt/d/Hackaton-0/AI_Employee_Vault/Done | wc -l)"
```

| Stage | Files | Status |
|-------|-------|--------|
| Inbox | _____ | [ ] |
| Needs_Action | _____ | [ ] |
| Pending_Approval | _____ | [ ] |
| Approved | _____ | [ ] |
| Done | _____ (≥1) | [ ] |

---

## 📝 Final Summary

### Overall Status
```
Total Checks Completed: _____ / 50

Gmail FTE Status: ☐ PASSING ☐ PARTIAL ☐ FAILING
WhatsApp FTE Status: ☐ PASSING ☐ PARTIAL ☐ FAILING
HITL Workflow Status: ☐ PASSING ☐ PARTIAL ☐ FAILING
Vault Status: ☐ PASSING ☐ PARTIAL ☐ FAILING
Dashboard Status: ☐ PASSING ☐ PARTIAL ☐ FAILING
```

### Issues Found:
1. _________________________________________________________
2. _________________________________________________________
3. _________________________________________________________

### Notes:
_________________________________________________________________

_________________________________________________________________

### Tester Info:
- **Name:** _________________
- **Date:** _________________
- **Time Taken:** ____________
- **Final Result:** ☐ 100% PASS ☐ PARTIAL PASS ☐ NEEDS WORK

---

**Aap is checklist ko print kr sakte ho, pencil se mark kr sakte ho, aur har cheez manually verify kr sakte ho!** 🎯

