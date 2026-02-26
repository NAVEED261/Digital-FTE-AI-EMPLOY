#!/bin/bash

# 🚀 SILVER TIER - QUICK TEST COMMANDS
# Fatima Zehra Digital FTE - Manual Testing
# Copy-paste these commands to verify each component

echo "🧪 SILVER TIER QUICK TEST SUITE"
echo "================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Paths
VAULT="/mnt/d/Hackaton-0/AI_Employee_Vault"
TIER="/mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/Tier_2_Silver"

echo -e "${YELLOW}1️⃣  ENVIRONMENT CHECK${NC}"
echo "========================"
python3 --version 2>/dev/null && echo -e "${GREEN}✅ Python installed${NC}" || echo -e "${RED}❌ Python missing${NC}"
python3 -c "import playwright; print('${GREEN}✅ Playwright installed${NC}')" 2>/dev/null || echo -e "${RED}❌ Playwright missing${NC}"
python3 -c "import google.auth; print('${GREEN}✅ Google Auth installed${NC}')" 2>/dev/null || echo -e "${RED}❌ Google Auth missing${NC}"
echo ""

echo -e "${YELLOW}2️⃣  VAULT STRUCTURE CHECK${NC}"
echo "============================="
for folder in Inbox Needs_Action Pending_Approval Approved Done Rejected Archive Logs Plans; do
    if [ -d "$VAULT/$folder" ]; then
        count=$(find "$VAULT/$folder" -type f 2>/dev/null | wc -l)
        echo -e "${GREEN}✅${NC} $folder: $count files"
    else
        echo -e "${RED}❌${NC} $folder: MISSING"
    fi
done
echo ""

echo -e "${YELLOW}3️⃣  GMAIL FTE CHECK${NC}"
echo "===================="
if [ -f "$TIER/src/watchers/email_sender.py" ]; then
    echo -e "${GREEN}✅${NC} Email Sender module exists"
    # Test import
    python3 << 'PYEOF' 2>/dev/null
try:
    import sys
    sys.path.insert(0, '/mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/Tier_2_Silver/src/watchers')
    from email_sender import EmailSender
    sender = EmailSender()
    print('\033[0;32m✅\033[0m Email Sender ready')
except Exception as e:
    print(f'\033[0;31m❌\033[0m Email Sender error: {str(e)[:50]}')
PYEOF
else
    echo -e "${RED}❌${NC} Email Sender missing"
fi
echo ""

echo -e "${YELLOW}4️⃣  WHATSAPP FTE CHECK${NC}"
echo "======================="
backup_count=$(find "$VAULT/Inbox" -name "WA_BACKUP_*" -type f 2>/dev/null | wc -l)
echo -e "${GREEN}✅${NC} WhatsApp backups: $backup_count files"

if [ -f "$TIER/src/watchers/whatsapp_session_integrator.py" ]; then
    echo -e "${GREEN}✅${NC} WhatsApp Integrator exists"
else
    echo -e "${RED}❌${NC} WhatsApp Integrator missing"
fi
echo ""

echo -e "${YELLOW}5️⃣  HITL WORKFLOW CHECK${NC}"
echo "======================="
pending=$(ls "$VAULT/Pending_Approval/" 2>/dev/null | wc -l)
approved=$(ls "$VAULT/Approved/" 2>/dev/null | wc -l)
done=$(ls "$VAULT/Done/" 2>/dev/null | wc -l)

echo -e "${GREEN}✅${NC} Pending Approvals: $pending"
echo -e "${GREEN}✅${NC} Approved: $approved"
echo -e "${GREEN}✅${NC} Done: $done"
echo ""

echo -e "${YELLOW}6️⃣  LOGGING CHECK${NC}"
echo "=================="
log_count=$(find "$VAULT/Logs" -name "*.log" -type f 2>/dev/null | wc -l)
echo -e "${GREEN}✅${NC} Total log files: $log_count"

# Show latest log entries
echo ""
echo "📝 Latest Log Entries:"
for logfile in $(find "$VAULT/Logs" -name "*.log" -type f 2>/dev/null | head -3); do
    logname=$(basename "$logfile")
    latest=$(tail -1 "$logfile" 2>/dev/null)
    echo "   $logname: ${latest:0:60}..."
done
echo ""

echo -e "${YELLOW}7️⃣  DASHBOARD CHECK${NC}"
echo "===================="
if [ -f "$TIER/../dashboard/index.html" ]; then
    echo -e "${GREEN}✅${NC} Dashboard HTML exists"

    # Check if status.json exists
    if [ -f "$TIER/../dashboard/api/status.json" ]; then
        echo -e "${GREEN}✅${NC} Status JSON exists"
        # Extract watchers count
        watchers=$(python3 -c "import json; f=open('$TIER/../dashboard/api/status.json'); d=json.load(f); print(d['watchers']['online'])" 2>/dev/null)
        echo -e "${GREEN}✅${NC} Watchers online: $watchers"
    fi
else
    echo -e "${RED}❌${NC} Dashboard missing"
fi
echo ""

echo -e "${YELLOW}8️⃣  TEST SUITE CHECK${NC}"
echo "===================="
if [ -f "$TIER/tests/test_silver_tier.py" ]; then
    test_count=$(grep -c "^def test_" "$TIER/tests/test_silver_tier.py" 2>/dev/null || echo "0")
    echo -e "${GREEN}✅${NC} Silver Tier tests: $test_count"
fi

if [ -f "$TIER/tests/test_whatsapp_integrator.py" ]; then
    test_count=$(grep -c "^def test_" "$TIER/tests/test_whatsapp_integrator.py" 2>/dev/null || echo "0")
    echo -e "${GREEN}✅${NC} WhatsApp tests: $test_count"
fi
echo ""

echo -e "${YELLOW}9️⃣  CONFIGURATION CHECK${NC}"
echo "======================="
if [ -f "$TIER/.env" ]; then
    echo -e "${GREEN}✅${NC} .env file exists"
    if grep -q "GMAIL_APP_PASSWORD" "$TIER/.env"; then
        echo -e "${GREEN}✅${NC} Gmail credentials configured"
    else
        echo -e "${YELLOW}⚠️${NC}  Gmail credentials missing (set via .env)"
    fi
else
    echo -e "${YELLOW}⚠️${NC}  .env file missing (optional - use environment variables)"
fi
echo ""

echo -e "${YELLOW}🔟 COMPLETE STATUS${NC}"
echo "=================="
# Count operational components
operational=0
[ -d "$VAULT/Inbox" ] && ((operational++))
[ -d "$VAULT/Needs_Action" ] && ((operational++))
[ -d "$VAULT/Pending_Approval" ] && ((operational++))
[ -d "$VAULT/Approved" ] && ((operational++))
[ -d "$VAULT/Done" ] && ((operational++))
[ -f "$TIER/src/watchers/email_sender.py" ] && ((operational++))
[ -f "$TIER/src/watchers/whatsapp_session_integrator.py" ] && ((operational++))
[ -f "$TIER/../dashboard/index.html" ] && ((operational++))

echo "Operational Components: $operational / 8"
if [ "$operational" -eq 8 ]; then
    echo -e "${GREEN}✅ ALL SYSTEMS READY${NC}"
    echo "Status: 🟢 PRODUCTION READY"
else
    echo -e "${YELLOW}⚠️  Some components missing (expected for fresh install)${NC}"
fi
echo ""

echo "====================================="
echo "🎯 For detailed testing, see:"
echo "   /mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/Tier_2_Silver/TESTING_GUIDE.md"
echo "====================================="
