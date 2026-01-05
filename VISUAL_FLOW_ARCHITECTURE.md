# 📊 Event Reminder System - Visual Flow & Architecture

## 🔄 COMPLETE SYSTEM FLOW

```
┌─────────────────────────────────────────────────────────────────┐
│                    EVENT REMINDER SYSTEM                        │
│                      (Test Mode Active)                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Event Creation                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User creates event via Odoo UI:                               │
│  ┌────────────────────────────────┐                            │
│  │ Event Name: "Training Session" │                            │
│  │ Start Date: Today + 10 minutes │                            │
│  │ Responsible: John Doe          │                            │
│  │ Trainer Tags: Python, Docker   │                            │
│  └────────────────────────────────┘                            │
│                  ↓                                               │
│  Database record created:                                       │
│  - is_reminder_sent = False                                    │
│  - date_begin = 2026-01-05 12:10:00                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Cron Job Execution (Every 5 Minutes)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Timer: ⏰ 5 minutes                                            │
│                  ↓                                               │
│  Cron triggers:                                                 │
│  ┌──────────────────────────────────────────┐                  │
│  │ model.send_weekly_event_reminders()     │                  │
│  └──────────────────────────────────────────┘                  │
│                  ↓                                               │
│  Searches for events:                                           │
│  ┌──────────────────────────────────────────┐                  │
│  │ WHERE:                                    │                  │
│  │ - date_begin = now + 10 min (±5 min)    │                  │
│  │ - is_reminder_sent = False               │                  │
│  │ - kanban_state != 'cancel'               │                  │
│  └──────────────────────────────────────────┘                  │
│                  ↓                                               │
│  Found: 1 event (Training Session)                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Email Preparation                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  For each found event:                                          │
│  ┌──────────────────────────────────────────┐                  │
│  │ event._send_one_week_reminder_emails()  │                  │
│  └──────────────────────────────────────────┘                  │
│                  ↓                                               │
│  Generates HTML email:                                          │
│  ┌──────────────────────────────────────────┐                  │
│  │ _prepare_one_week_reminder_email_body() │                  │
│  └──────────────────────────────────────────┘                  │
│                  ↓                                               │
│  Email contains:                                                │
│  - Event name                                                   │
│  - Date/Time                                                    │
│  - Location                                                     │
│  - Registration count                                           │
│  - Direct link to event                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Email Distribution                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Recipients identified:                                         │
│                                                                  │
│  A) Trainers (with matching tags)                              │
│     ┌──────────────────────────┐                               │
│     │ trainer1@example.com     │ ← Has "Python" tag            │
│     │ trainer2@example.com     │ ← Has "Docker" tag            │
│     └──────────────────────────┘                               │
│                  ↓                                               │
│  B) Responsible User                                            │
│     ┌──────────────────────────┐                               │
│     │ john.doe@example.com     │                               │
│     └──────────────────────────┘                               │
│                  ↓                                               │
│  Email queued via:                                              │
│  ┌──────────────────────────────────────────┐                  │
│  │ env['mail.mail'].sudo().create({...})   │                  │
│  └──────────────────────────────────────────┘                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Status Update                                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Database updated:                                              │
│  ┌──────────────────────────────────────────┐                  │
│  │ event.is_reminder_sent = True            │                  │
│  │ event.trainer_notified = True            │                  │
│  │ event.responsible_notified = True        │                  │
│  └──────────────────────────────────────────┘                  │
│                  ↓                                               │
│  Logged to console:                                             │
│  "✅ Reminder sent for: Training Session"                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: Email Delivery                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Odoo Mail Server processes queue:                             │
│  ┌──────────────────────────────────────────┐                  │
│  │  SMTP Server                             │                  │
│  │  ├── To: trainer1@example.com            │                  │
│  │  │   Status: Sent ✅                     │                  │
│  │  ├── To: trainer2@example.com            │                  │
│  │  │   Status: Sent ✅                     │                  │
│  │  └── To: john.doe@example.com            │                  │
│  │      Status: Sent ✅                     │                  │
│  └──────────────────────────────────────────┘                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                         ↓
                    ✅ COMPLETE!
```

---

## 🏗️ SYSTEM ARCHITECTURE

```
┌───────────────────────────────────────────────────────────────────┐
│                         ODOO SERVER                               │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ CRON WORKER (Background Process)                        │    │
│  │                                                           │    │
│  │  ┌───────────────────────────────────────────────┐      │    │
│  │  │ Event Mail Scheduler                          │      │    │
│  │  │ - Runs: Every 24 hours                        │      │    │
│  │  │ - Handles: General event communications      │      │    │
│  │  └───────────────────────────────────────────────┘      │    │
│  │                                                           │    │
│  │  ┌───────────────────────────────────────────────┐      │    │
│  │  │ Event Weekly Reminder Scheduler (YOUR FEATURE)│      │    │
│  │  │ - Runs: Every 5 minutes (TEST MODE)          │      │    │
│  │  │ - Calls: send_weekly_event_reminders()       │      │    │
│  │  │ - Purpose: Send reminder emails               │      │    │
│  │  └───────────────────────────────────────────────┘      │    │
│  │                                                           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           ↓                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ EVENT MODEL (event.event)                               │    │
│  │                                                           │    │
│  │  Methods:                                                │    │
│  │  ├── send_weekly_event_reminders() ← Cron entry point  │    │
│  │  ├── _send_one_week_reminder_emails() ← Per event      │    │
│  │  ├── _prepare_one_week_reminder_email_body()           │    │
│  │  └── _create_reminder_scheduled_action()               │    │
│  │                                                           │    │
│  │  Fields:                                                 │    │
│  │  ├── is_reminder_sent (Boolean)                        │    │
│  │  ├── reminder_cron_id (Many2one to ir.cron)           │    │
│  │  ├── trainer_notified (Boolean)                        │    │
│  │  └── responsible_notified (Boolean)                    │    │
│  │                                                           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           ↓                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ MAIL SYSTEM (mail.mail)                                 │    │
│  │                                                           │    │
│  │  ├── Create email records                               │    │
│  │  ├── Queue for sending                                  │    │
│  │  ├── Process via SMTP                                   │    │
│  │  └── Update delivery status                             │    │
│  │                                                           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           ↓                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ DATABASE (PostgreSQL)                                    │    │
│  │                                                           │    │
│  │  Tables:                                                 │    │
│  │  ├── event_event (Events)                              │    │
│  │  ├── ir_cron (Scheduled Actions)                       │    │
│  │  ├── mail_mail (Email Queue)                           │    │
│  │  └── res_partner (Contacts/Trainers)                   │    │
│  │                                                           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
                           ↓
              ┌─────────────────────────┐
              │    SMTP SERVER          │
              │  (Email Delivery)       │
              └─────────────────────────┘
                           ↓
              ┌─────────────────────────┐
              │   RECIPIENTS            │
              │  - Trainers             │
              │  - Responsible User     │
              └─────────────────────────┘
```

---

## 🎨 TEST MODE vs PRODUCTION MODE

```
┌─────────────────────────────────────────────────────────────────┐
│                         TEST MODE (CURRENT)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Timing:                                                        │
│  ┌──────────────┐                                              │
│  │ Cron: 5 min  │ → Checks every 5 minutes                    │
│  └──────────────┘                                              │
│  ┌──────────────┐                                              │
│  │ Window: ±5   │ → Finds events 10 min from now (±5 min)    │
│  └──────────────┘                                              │
│                                                                  │
│  Example Timeline:                                              │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ 12:00 → Create event (start: 12:10)                     │  │
│  │ 12:05 → Cron runs, finds event, sends reminder          │  │
│  │ 12:10 → Event starts                                     │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Purpose: Quick testing and verification                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      PRODUCTION MODE (TARGET)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Timing:                                                        │
│  ┌──────────────┐                                              │
│  │ Cron: 1 day  │ → Checks daily (e.g., midnight)            │
│  └──────────────┘                                              │
│  ┌──────────────┐                                              │
│  │ Window: 7d   │ → Finds events exactly 7 days away         │
│  └──────────────┘                                              │
│                                                                  │
│  Example Timeline:                                              │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Jan 1  → Create event (start: Jan 15)                   │  │
│  │ Jan 8  → Cron runs (7 days before)                      │  │
│  │          Sends reminder to trainers & responsible        │  │
│  │ Jan 15 → Event starts                                    │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Purpose: Real-world event reminder system                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📧 EMAIL TEMPLATE STRUCTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                      REMINDER EMAIL                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  From: noreply@yourdomain.com                                   │
│  To: trainer@example.com                                        │
│  Subject: Reminder: Training Session - One Week to Go!          │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Dear John,                                                     │
│                                                                  │
│  ⚠️ Reminder: The event "Training Session" is happening        │
│  in one week!                                                   │
│                                                                  │
│  📅 Event Details:                                              │
│  • Name: Training Session                                      │
│  • Date: January 15, 2026                                      │
│  • Time: 14:00 - 16:00                                         │
│  • Location: Conference Room A                                 │
│  • Confirmed Registrations: 15                                 │
│                                                                  │
│  🔗 View Event in Odoo:                                         │
│  [Click Here] → http://localhost:8069/web#id=123&model=...    │
│                                                                  │
│  Please ensure you are prepared for this event.                │
│                                                                  │
│  Best regards,                                                  │
│  Odoo Event Management System                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 LOGGING & MONITORING

```
┌─────────────────────────────────────────────────────────────────┐
│                      SYSTEM LOGS                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [INFO] Starting weekly event reminder cron job                │
│  [INFO] TEST MODE: Looking for events between                  │
│         2026-01-05 12:05:00 and 2026-01-05 12:15:00           │
│  [INFO] TEST MODE: Found 1 events requiring reminders          │
│  [INFO] Processing reminder for event: Training (ID: 123)      │
│  [INFO] Event Training: Sending reminder emails                │
│  [INFO] Event Training: Sent to trainer1@example.com           │
│  [INFO] Event Training: Sent to trainer2@example.com           │
│  [INFO] Event Training: Sent to john.doe@example.com           │
│  [INFO] Event Training: Marked is_reminder_sent = True         │
│  [INFO] Completed reminder cron. Processed 1 events            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Monitoring Points:
├── Odoo Logs (Real-time)
├── Database (is_reminder_sent field)
├── Email Queue (Settings → Technical → Email)
└── Cron Execution History (Scheduled Actions)
```

---

## 🎯 DECISION TREE: When Reminders Are Sent

```
                    ┌─────────────┐
                    │ Cron Runs   │
                    └──────┬──────┘
                           │
                           ↓
                  ┌────────────────┐
                  │ Search Events  │
                  └────────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                  ↓
┌───────────────┐  ┌──────────────┐  ┌──────────────┐
│ date_begin in │  │ reminder not │  │ not cancelled│
│ time window?  │  │ sent yet?    │  │              │
└───────┬───────┘  └──────┬───────┘  └──────┬───────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ↓
                    ┌──────────────┐
                    │ ALL YES?     │
                    └──────┬───────┘
                           │
                ┌──────────┴──────────┐
                ↓                     ↓
         ┌──────────┐          ┌──────────┐
         │   YES    │          │    NO    │
         │ Send     │          │  Skip    │
         │ Reminder │          │  Event   │
         └──────────┘          └──────────┘
```

---

## 📊 DATABASE SCHEMA

```
┌─────────────────────────────────────────────────────────────────┐
│ event_event (Main Event Table)                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ id                    │ INTEGER (PK)                     │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ name                  │ VARCHAR (Event Name)             │   │
│  │ date_begin            │ TIMESTAMP (Start Date/Time)      │   │
│  │ date_end              │ TIMESTAMP (End Date/Time)        │   │
│  │ user_id               │ INTEGER (FK: res_users)          │   │
│  │ kanban_state          │ VARCHAR (normal/done/cancel)     │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ is_reminder_sent      │ BOOLEAN ← NEW FIELD              │   │
│  │ trainer_notified      │ BOOLEAN ← NEW FIELD              │   │
│  │ responsible_notified  │ BOOLEAN ← NEW FIELD              │   │
│  │ reminder_cron_id      │ INTEGER (FK: ir_cron) ← NEW      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ ir_cron (Scheduled Actions)                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ id                    │ INTEGER (PK)                     │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ name                  │ VARCHAR                          │   │
│  │ model_id              │ INTEGER (FK: ir_model)           │   │
│  │ code                  │ TEXT (Python code to execute)    │   │
│  │ interval_number       │ INTEGER (5 or 1)                 │   │
│  │ interval_type         │ VARCHAR (minutes or days)        │   │
│  │ active                │ BOOLEAN                          │   │
│  │ nextcall              │ TIMESTAMP                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚦 STATUS INDICATORS

```
Event Reminder Status:

┌──────────────────────────────────────────────────────────┐
│  ⏳ PENDING                                              │
│  - is_reminder_sent = False                             │
│  - date_begin in future                                 │
│  - Waiting for cron to process                          │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  📧 PROCESSING                                           │
│  - Cron found the event                                 │
│  - Generating emails                                    │
│  - Sending to recipients                                │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  ✅ SENT                                                 │
│  - is_reminder_sent = True                              │
│  - trainer_notified = True                              │
│  - responsible_notified = True                          │
│  - Emails delivered                                     │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  ⏭️  SKIPPED                                             │
│  - Already sent (is_reminder_sent = True)               │
│  - Cancelled (kanban_state = 'cancel')                  │
│  - Outside time window                                  │
└──────────────────────────────────────────────────────────┘
```

---

## 🎓 LEARNING RESOURCES

```
Documentation Structure:
├── REMINDER_SYSTEM_SUMMARY.md ← Start Here (Overview)
├── QUICK_START_REMINDER_TEST.md ← Testing Guide
├── EVENT_REMINDER_SYSTEM_ANALYSIS.md ← Deep Dive
├── VISUAL_FLOW_ARCHITECTURE.md ← This Document
└── test_reminder_system.py ← Diagnostic Tool
```

---

**This visual guide shows exactly how your event reminder system works!**

**Key Takeaways:**
- ✅ System is fully functional
- ⚡ Test mode: 5-minute cycles
- 📧 Sends to trainers + responsible user
- 🔄 Production ready with simple switch
- 📊 Comprehensive logging & tracking

**Ready to test? Follow the flow above!** 🚀
