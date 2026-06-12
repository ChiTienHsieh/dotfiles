---
name: gcal
description: "Add an event to the user's configured Google Calendar bridge. Use when the user wants to add calendar events, reminders, or schedule meetings from Claude Code."
allowed-tools: Bash
---

Add a Google Calendar event through the user's locally configured calendar bridge.

Machine-specific hostnames, account names, calendar labels, and bridge commands must live in local machine notes, not in this tracked public dotfiles repo.

Before running anything, read the local machine notes for the calendar bridge command and required defaults:

- `~/.codex/machine.md`
- `~/.claude/machine.md` if present

If no calendar bridge command is documented locally, stop and ask the user to add one to machine notes. Do not invent SSH hosts, account names, calendar IDs, or invitees.

**Rules:**
- Times are in Asia/Taipei timezone
- ISO format: `2026-04-26T09:00:00`
- If user doesn't specify end time, default to start + 30 minutes
- If user gives a vague time like "next Tuesday 3pm", calculate the actual ISO datetime
- Use only the invite/calendar defaults documented in local machine notes
- After creating, confirm with the event link

**Examples:**
- User: "add a reminder to renew X on April 26 at 9am"
- User: "schedule a review meeting next Friday 2-3pm"
- User: "remind me to check gu-log deploy on Feb 10"

$ARGUMENTS
