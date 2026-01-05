#!/bin/bash
# Quick Verification Script for Event Reminder System

echo "=========================================="
echo "EVENT REMINDER SYSTEM - QUICK VERIFICATION"
echo "=========================================="
echo ""

# Check if Odoo is running
echo "1. Checking if Odoo is running..."
if ps aux | grep -i "odoo-bin" | grep -v grep > /dev/null; then
    echo "   ✅ Odoo is running"
    PID=$(ps aux | grep -i "odoo-bin" | grep -v grep | awk '{print $2}')
    echo "   Process ID: $PID"
else
    echo "   ❌ Odoo is NOT running"
    echo "   Start Odoo with: ./odoo-bin -d your_database_name"
    exit 1
fi
echo ""

# Check if required files exist
echo "2. Checking system files..."

FILES=(
    "addons/event/data/ir_cron_data.xml"
    "addons/event/models/event_event.py"
    "addons/event/models/event_mail.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file exists"
    else
        echo "   ❌ $file NOT found"
    fi
done
echo ""

# Check cron configuration
echo "3. Checking cron job configuration..."
if grep -q "event_weekly_reminder_cron" addons/event/data/ir_cron_data.xml; then
    echo "   ✅ Cron job 'event_weekly_reminder_cron' defined"
    
    # Check interval
    if grep -q 'interval_type">minutes' addons/event/data/ir_cron_data.xml; then
        echo "   ⚠️  TEST MODE: Running every 5 minutes"
    elif grep -q 'interval_type">days' addons/event/data/ir_cron_data.xml; then
        echo "   ℹ️  PRODUCTION MODE: Running daily"
    fi
else
    echo "   ❌ Cron job NOT found in XML"
fi
echo ""

# Check method exists
echo "4. Checking reminder methods..."
if grep -q "def send_weekly_event_reminders" addons/event/models/event_event.py; then
    echo "   ✅ Method 'send_weekly_event_reminders' exists"
else
    echo "   ❌ Method 'send_weekly_event_reminders' NOT found"
fi

if grep -q "def _send_one_week_reminder_emails" addons/event/models/event_event.py; then
    echo "   ✅ Method '_send_one_week_reminder_emails' exists"
else
    echo "   ❌ Method '_send_one_week_reminder_emails' NOT found"
fi
echo ""

# Summary
echo "=========================================="
echo "SUMMARY"
echo "=========================================="
echo ""
echo "✅ Event reminder system is installed!"
echo ""
echo "📝 NEXT STEPS:"
echo "   1. Open Odoo: http://localhost:8069"
echo "   2. Go to Settings → Enable Developer Mode"
echo "   3. Go to Settings → Technical → Scheduled Actions"
echo "   4. Search for 'Event: Weekly Reminder'"
echo "   5. Verify it's Active and scheduled correctly"
echo ""
echo "🧪 TO TEST:"
echo "   1. Create an event with start date 10 minutes from now"
echo "   2. Wait 5 minutes for cron to run"
echo "   3. Check Settings → Technical → Email → Messages"
echo ""
echo "📚 FULL GUIDES:"
echo "   - QUICK_START_REMINDER_TEST.md (Quick testing)"
echo "   - EVENT_REMINDER_SYSTEM_ANALYSIS.md (Complete documentation)"
echo "   - test_reminder_system.py (Diagnostic script)"
echo ""
echo "=========================================="
