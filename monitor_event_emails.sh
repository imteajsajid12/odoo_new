#!/bin/bash

# Monitor Odoo logs for event email notifications
# This script filters and displays relevant log entries

echo "=========================================="
echo "EVENT EMAIL NOTIFICATION MONITOR"
echo "=========================================="
echo ""
echo "Monitoring Odoo logs for event-related emails..."
echo "Press Ctrl+C to stop"
echo ""
echo "Looking for:"
echo "  - Event creation"
echo "  - Email sending"
echo "  - Scheduled actions"
echo ""
echo "=========================================="
echo ""

# Follow the log file and filter for relevant entries
tail -f odoo.log | grep --line-buffered -E "(Event.*:|email|mail|_send_|reminder|cron)" | \
    grep --line-buffered -v "mail.channel" | \
    grep --line-buffered -v "mail.message" | \
    while IFS= read -r line; do
        # Color code different types of messages
        if echo "$line" | grep -q "ERROR"; then
            echo -e "\033[0;31m$line\033[0m"  # Red for errors
        elif echo "$line" | grep -q "WARNING"; then
            echo -e "\033[0;33m$line\033[0m"  # Yellow for warnings
        elif echo "$line" | grep -q "successfully sent"; then
            echo -e "\033[0;32m$line\033[0m"  # Green for successful sends
        elif echo "$line" | grep -q "EventEvent.create"; then
            echo -e "\033[0;36m$line\033[0m"  # Cyan for event creation
        elif echo "$line" | grep -q "reminder"; then
            echo -e "\033[0;35m$line\033[0m"  # Magenta for reminders
        else
            echo "$line"
        fi
    done

