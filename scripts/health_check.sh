#!/bin/bash
# Health check script for Digital FTE watchers
# Run manually or via cron: 0 * * * * /path/to/health_check.sh

VAULT_PATH="/mnt/d/Hackaton-0/AI_Employee_Vault"
LOG_FILE="/var/log/fte-health.log"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🔍 Digital FTE Health Check - $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"

# Check PM2 processes
echo -e "\n${GREEN}📊 PM2 Process Status:${NC}" | tee -a "$LOG_FILE"
if command -v pm2 &> /dev/null; then
    pm2 status 2>&1 | tee -a "$LOG_FILE"
else
    echo -e "${RED}❌ PM2 not installed${NC}" | tee -a "$LOG_FILE"
fi

# Check disk space
echo -e "\n${GREEN}💾 Disk Space:${NC}" | tee -a "$LOG_FILE"
df -h /mnt/d/Hackaton-0 | tail -1 | tee -a "$LOG_FILE"

# Check vault folder sizes
echo -e "\n${GREEN}📁 Vault Folder Sizes:${NC}" | tee -a "$LOG_FILE"
if [ -d "$VAULT_PATH" ]; then
    du -sh "$VAULT_PATH"/* 2>/dev/null | sort -h | tee -a "$LOG_FILE"
else
    echo -e "${RED}❌ Vault path not found: $VAULT_PATH${NC}" | tee -a "$LOG_FILE"
fi

# Check recent activity
echo -e "\n${GREEN}📝 Recent Activity (last 3):${NC}" | tee -a "$LOG_FILE"
if [ -d "$VAULT_PATH/Logs" ]; then
    tail -3 "$VAULT_PATH"/Logs/*.log 2>/dev/null || echo "No logs found" | tee -a "$LOG_FILE"
else
    echo -e "${YELLOW}⚠️  Logs folder not found${NC}" | tee -a "$LOG_FILE"
fi

# Check pending actions
echo -e "\n${GREEN}📋 Pending Items:${NC}" | tee -a "$LOG_FILE"
NEEDS_ACTION=0
PENDING_APPROVAL=0

if [ -d "$VAULT_PATH/Needs_Action" ]; then
    NEEDS_ACTION=$(find "$VAULT_PATH/Needs_Action" -type f | wc -l)
fi

if [ -d "$VAULT_PATH/Pending_Approval" ]; then
    PENDING_APPROVAL=$(find "$VAULT_PATH/Pending_Approval" -type f | wc -l)
fi

echo "  📌 Needs_Action: $NEEDS_ACTION files" | tee -a "$LOG_FILE"
echo "  ✅ Pending_Approval: $PENDING_APPROVAL files" | tee -a "$LOG_FILE"

# Summary
echo -e "\n${GREEN}✅ Health check complete${NC}" | tee -a "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
