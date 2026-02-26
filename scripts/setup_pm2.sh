#!/bin/bash
# Setup PM2 for 24/7 watcher uptime
# Digital FTE - Bronze Tier Process Management

set -e

VAULT_PATH="/mnt/d/Hackaton-0/AI_Employee_Vault"
TIER_1_SRC="/mnt/d/Hackaton-0/DEGITAL-FTE-EMPLOY/Tier_1_Bronze/src/watchers"

echo "🚀 Setting up PM2 for Digital FTE..."

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    echo "📦 Installing PM2 globally..."
    npm install -g pm2
fi

# Stop and delete all existing PM2 processes
echo "🛑 Stopping existing PM2 processes..."
pm2 delete all 2>/dev/null || true

# Start Filesystem Watcher (Bronze Tier)
echo "📁 Starting filesystem watcher..."
pm2 start "$TIER_1_SRC/filesystem_watcher.py" \
    --name "filesystem-watcher" \
    --interpreter python3 \
    --watch \
    --ignore-watch="*.log,*.md" \
    --max-memory-restart 500M \
    -- "$VAULT_PATH" || {
    echo "❌ Failed to start filesystem watcher"
    exit 1
}

# Save PM2 configuration
echo "💾 Saving PM2 configuration..."
pm2 save

# Setup PM2 to start on system boot
echo "⚙️  Configuring PM2 startup script..."
pm2 startup 2>/dev/null || true

echo ""
echo "✅ PM2 Configuration Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Check status:        pm2 status"
echo "📝 View logs:           pm2 logs filesystem-watcher"
echo "🔄 Restart watcher:     pm2 restart filesystem-watcher"
echo "🛑 Stop watcher:        pm2 stop filesystem-watcher"
echo "📈 Monitor in realtime: pm2 monit"
echo ""
echo "ℹ️  To remove on system boot: pm2 unstartup"
echo ""
