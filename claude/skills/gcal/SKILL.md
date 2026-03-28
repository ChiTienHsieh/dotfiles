---
name: gcal
description: "Add event to Clawd Co-ops Google Calendar via VM. Use when user wants to add calendar events, reminders, or schedule meetings."
allowed-tools: Bash
---

Add a Google Calendar event to the "Clawd Co-ops" shared calendar. This calendar is shared between Sprin (chitienhsieh@gmail.com) and Clawd (shroomclawd@gmail.com).

The user will provide event details. Parse them and run the following SSH command:

```
ssh moltbot@5.78.134.208 "python3 ~/clawd/scripts/google_calendar_add.py '<SUMMARY>' '<START_ISO>' '<END_ISO>' --description '<DESCRIPTION>'"
```

**Rules:**
- Always use `dangerouslyDisableSandbox: true` for the SSH command
- Times are in Asia/Taipei timezone
- ISO format: `2026-04-26T09:00:00`
- If user doesn't specify end time, default to start + 30 minutes
- If user gives a vague time like "next Tuesday 3pm", calculate the actual ISO datetime
- Default invite goes to chitienhsieh@gmail.com (already set in script)
- After creating, confirm with the event link

**Examples:**
- User: "add a reminder to renew X on April 26 at 9am"
- User: "schedule a review meeting next Friday 2-3pm"
- User: "remind me to check gu-log deploy on Feb 10"

$ARGUMENTS
