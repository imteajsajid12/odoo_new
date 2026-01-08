#!/bin/bash
#
# Event Reminder System - Quick Test Script
# This script helps verify the reminder cron system is working
#

echo "=================================================="
echo "   EVENT REMINDER SYSTEM - VERIFICATION SCRIPT"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Database configuration
DB_NAME=${1:-"your_database_name"}

if [ "$DB_NAME" == "your_database_name" ]; then
    echo -e "${YELLOW}⚠️  Warning: Using default database name${NC}"
    echo "Usage: $0 <database_name>"
    echo ""
    read -p "Enter your database name: " DB_NAME
fi

echo "Database: $DB_NAME"
echo ""

# Function to run SQL query
run_query() {
    psql -d "$DB_NAME" -t -A -c "$1" 2>/dev/null
}

# Check 1: Verify no 'numbercall' field references
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ CHECK 1: Verify code fix (no 'numbercall' references)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if grep -q "numbercall" addons/event/models/event_event.py; then
    echo -e "${RED}❌ FAILED: 'numbercall' still found in code!${NC}"
    echo "Run: grep -n 'numbercall' addons/event/models/event_event.py"
else
    echo -e "${GREEN}✅ PASSED: No 'numbercall' references found${NC}"
fi
echo ""

# Check 2: Count active event reminder crons
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ CHECK 2: Active Event Reminder Crons"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ACTIVE_CRONS=$(run_query "SELECT COUNT(*) FROM ir_cron WHERE name LIKE 'Event Reminder:%' AND active = true;")
INACTIVE_CRONS=$(run_query "SELECT COUNT(*) FROM ir_cron WHERE name LIKE 'Event Reminder:%' AND active = false;")

echo "Active reminder crons: ${ACTIVE_CRONS:-0}"
echo "Inactive reminder crons (already executed): ${INACTIVE_CRONS:-0}"

if [ "${ACTIVE_CRONS:-0}" -gt 0 ]; then
    echo ""
    echo "Active crons details:"
    psql -d "$DB_NAME" -c "
        SELECT
            id,
            cron_name,
            active,
            nextcall,
            EXTRACT(EPOCH FROM (nextcall - NOW())) AS seconds_until_exec
        FROM ir_cron
        WHERE name LIKE 'Event Reminder:%' AND active = true
        ORDER BY nextcall;
    " 2>/dev/null
fi
echo ""

# Check 3: Recent events with reminders
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ CHECK 3: Recent Events with Reminders"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

psql -d "$DB_NAME" -c "
    SELECT
        e.id,
        e.name,
        e.is_reminder_sent,
        e.reminder_cron_id,
        c.active AS cron_active,
        c.nextcall AS cron_nextcall
    FROM event_event e
    LEFT JOIN ir_cron c ON e.reminder_cron_id = c.id
    WHERE e.create_date > NOW() - INTERVAL '1 day'
    ORDER BY e.id DESC
    LIMIT 10;
" 2>/dev/null
echo ""

# Check 4: Recent reminder emails
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ CHECK 4: Recent Reminder Emails"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

EMAIL_COUNT=$(run_query "SELECT COUNT(*) FROM mail_mail WHERE subject LIKE '%Reminder:%' AND create_date > NOW() - INTERVAL '1 day';")
echo "Reminder emails sent in last 24h: ${EMAIL_COUNT:-0}"

if [ "${EMAIL_COUNT:-0}" -gt 0 ]; then
    echo ""
    echo "Recent reminder emails:"
    psql -d "$DB_NAME" -c "
        SELECT
            id,
            subject,
            email_to,
            state,
            create_date
        FROM mail_mail
        WHERE subject LIKE '%Reminder:%'
        AND create_date > NOW() - INTERVAL '1 day'
        ORDER BY id DESC
        LIMIT 10;
    " 2>/dev/null
fi
echo ""

# Check 5: Odoo cron worker status
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ CHECK 5: Odoo Cron Worker Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ps aux | grep -v grep | grep odoo-bin > /dev/null; then
    echo -e "${GREEN}✅ Odoo process is running${NC}"

    # Check for cron threads
    if ps aux | grep -v grep | grep odoo-bin | grep -q "max-cron-threads"; then
        echo -e "${GREEN}✅ Cron worker threads configured${NC}"
    else
        echo -e "${YELLOW}⚠️  Warning: Cannot detect cron worker configuration${NC}"
        echo "Make sure Odoo is started with --max-cron-threads=2 or higher"
    fi

    echo ""
    echo "Odoo process info:"
    ps aux | grep -v grep | grep odoo-bin | head -1
else
    echo -e "${RED}❌ Odoo is NOT running!${NC}"
    echo "Start Odoo with: python3 odoo-bin -c config.conf --max-cron-threads=2"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   SUMMARY & NEXT STEPS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To test the reminder system:"
echo ""
echo "1. Make sure Odoo is running with cron workers enabled"
echo "2. Create a test event in the Odoo UI (Events module)"
echo "3. Watch logs: tail -f odoo.log | grep -i reminder"
echo "4. Wait 2 minutes (test mode)"
echo "5. Verify emails sent and cron deactivated"
echo ""
echo "For detailed testing guide, see:"
echo "  📄 EVENT_REMINDER_TEST_GUIDE.md"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
