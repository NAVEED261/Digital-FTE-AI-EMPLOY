#!/bin/bash
################################################################################
# Start AI Employee Watchers using PM2
#
# This script:
# 1. Installs Python dependencies
# 2. Starts all watcher processes via PM2
# 3. Configures PM2 auto-restart on boot (optional)
#
# Usage:
#   bash start_watchers.sh
#
# After running:
#   pm2 status                    # Check status
#   pm2 logs filesystem-watcher   # View logs
#   pm2 stop filesystem-watcher   # Stop specific watcher
#   pm2 delete filesystem-watcher # Remove from PM2
################################################################################

set -e  # Exit on error

VAULT_PATH="/mnt/d/Hackaton-0/AI_Employee_Vault"
WATCHERS_DIR="$VAULT_PATH/.watchers"

echo "🚀 Starting AI Employee Watchers"
echo "================================"
echo ""
echo "Vault Path: $VAULT_PATH"
echo "Watchers Directory: $WATCHERS_DIR"
echo ""

# Check if vault exists
if [ ! -d "$VAULT_PATH" ]; then
    echo "❌ Vault not found at $VAULT_PATH"
    exit 1
fi

# Check if .watchers exists
if [ ! -d "$WATCHERS_DIR" ]; then
    echo "❌ Watchers directory not found at $WATCHERS_DIR"
    exit 1
fi

# Change to watchers directory
cd "$WATCHERS_DIR"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install --break-system-packages -q -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "⚠️  requirements.txt not found, skipping pip install"
fi

echo ""

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    echo "❌ PM2 is not installed. Install with: npm install -g pm2"
    exit 1
fi

# Start filesystem watcher
echo "🔧 Starting FileSystem Watcher..."
pm2 start filesystem_watcher.py \
    --name "fs-watcher" \
    --interpreter python3 \
    --log "$VAULT_PATH/Logs/pm2-fs-watcher.log" \
    -- "$VAULT_PATH"

# Short delay for PM2 to register the process
sleep 1

# Show status
echo ""
echo "📊 Current PM2 Status:"
pm2 status

echo ""
echo "✅ Watchers started successfully!"
echo ""
echo "📖 Useful commands:"
echo "   pm2 status                    - Show watcher status"
echo "   pm2 logs fs-watcher           - View real-time logs"
echo "   pm2 logs fs-watcher --tail    - View last 10 lines"
echo "   pm2 stop fs-watcher           - Stop watcher"
echo "   pm2 restart fs-watcher        - Restart watcher"
echo "   pm2 delete fs-watcher         - Remove from PM2"
echo ""

# Optional: Save PM2 configuration and setup auto-restart
read -p "Would you like to save PM2 config and setup auto-restart on boot? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "💾 Saving PM2 configuration..."
    pm2 save

    echo "🔄 Setting up auto-restart on boot (requires sudo)..."
    pm2 startup systemd -u $(whoami) --hp $HOME

    echo "✅ Auto-restart configured"
else
    echo "ℹ️  Skipped auto-restart setup"
fi

echo ""
echo "🎯 Next steps:"
echo "1. Drop a file in $VAULT_PATH/Inbox/"
echo "2. Watch it move to Needs_Action/"
echo "3. Check the logs: pm2 logs fs-watcher"
echo ""
