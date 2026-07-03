---
name: playwright-cli
description: "Use for browser automation: navigate pages, click, type, fill forms, take screenshots, test web apps, or extract page data."
allowed-tools: Bash(playwright-cli:*)
---

# Browser Automation with playwright-cli

## Login flows & sandbox (read first)

- **CRITICAL: tasks requiring user login (OAuth, GCP Console, etc.) need the `--headed` flag** — `playwright-cli open "<url>" --headed` opens a visible browser window. Without it the browser is headless (invisible), useless for manual login.
- In Claude Code, playwright-cli needs `dangerouslyDisableSandbox: true` (it talks over Unix sockets the sandbox blocks).
- When done, clean up sessions: `playwright-cli close-all` (or `kill-all` for stale/zombie processes). There is no `session-stop-all` subcommand.

## Quick start

```bash
# open new browser
playwright-cli open
# navigate to a page
playwright-cli goto https://playwright.dev
# interact with the page using refs from the snapshot
playwright-cli click e15
playwright-cli type "page.click"
playwright-cli press Enter
# take a screenshot (rarely used, as snapshot is more common)
playwright-cli screenshot
# close the browser
playwright-cli close
```

## Common commands

Keep the main skill small. Use these for day-to-day browser work; use the
references below for full command families and advanced workflows.

```bash
playwright-cli open https://example.com --headed
playwright-cli goto https://playwright.dev
playwright-cli snapshot
playwright-cli click e15
playwright-cli fill e5 "user@example.com" --submit
playwright-cli press Enter
playwright-cli eval "document.title"
playwright-cli --raw eval "el => el.textContent" e5
playwright-cli screenshot --filename=page.png
playwright-cli console
playwright-cli requests
playwright-cli close
```

Useful current surface:

- Element targeting accepts snapshot refs (`e15`), CSS selectors, and Playwright locators such as `getByRole('button', { name: 'Submit' })`.
- `snapshot` supports `--filename`, element targets, `--depth=<n>`, and `--boxes`.
- `--raw` returns only the command value; `--json` gives structured wrapper output.
- Use `requests` / `request <index>` for network inspection; older docs may call this `network`.
- Use `run-code --filename=script.js` for larger Playwright snippets.
- Use `show --annotate` when the user needs to point at UI or give visual feedback.
- Use `generate-locator e5 --raw` when turning an observed element into a Playwright assertion.
- Use `highlight e5`, `highlight e5 --style="..."`, or `highlight --hide` for persistent page overlays.

## Session and launch notes

```bash
playwright-cli open --browser=chrome
playwright-cli open --persistent
playwright-cli open --profile=/path/to/profile
playwright-cli open --config=my-config.json
playwright-cli attach --extension=chrome
playwright-cli attach --cdp=chrome
playwright-cli attach --cdp=http://localhost:9222
playwright-cli -s=msedge detach
playwright-cli list --json
```

## Snapshots

After each command, playwright-cli provides a snapshot of the current browser state.

```bash
> playwright-cli goto https://example.com
### Page
- Page URL: https://example.com/
- Page Title: Example Domain
### Snapshot
[Snapshot](.playwright-cli/page-2026-02-14T19-22-42-679Z.yml)
```

You can also take a snapshot on demand using `playwright-cli snapshot` command.

If `--filename` is not provided, a new snapshot file is created with a timestamp. Default to automatic file naming, use `--filename=` when artifact is a part of the workflow result.

## Browser Sessions

```bash
# create new browser session named "mysession" with persistent profile
playwright-cli -s=mysession open example.com --persistent
# same with manually specified profile directory (use when requested explicitly)
playwright-cli -s=mysession open example.com --profile=/path/to/profile
playwright-cli -s=mysession click e6
playwright-cli -s=mysession close  # stop a named browser
playwright-cli -s=mysession delete-data  # delete user data for persistent session

playwright-cli list
# Close all browsers
playwright-cli close-all
# Forcefully kill all browser processes
playwright-cli kill-all
```

## Installation fallback

If global `playwright-cli` is not available, check for a local install:

```bash
npx --no-install playwright-cli --version
```

When a local version is available, use `npx playwright-cli` in commands. Do not
upgrade or install packages unless the user asks.

## Example: Form submission

```bash
playwright-cli open https://example.com/form
playwright-cli snapshot

playwright-cli fill e1 "user@example.com"
playwright-cli fill e2 "password123"
playwright-cli click e3
playwright-cli snapshot
playwright-cli close
```

## Specific tasks

* **Running and Debugging Playwright tests** [references/playwright-tests.md](references/playwright-tests.md)
* **Request mocking** [references/request-mocking.md](references/request-mocking.md)
* **Running Playwright code** [references/running-code.md](references/running-code.md)
* **Browser session management** [references/session-management.md](references/session-management.md)
* **Spec-driven testing (plan / generate / heal)** [references/spec-driven-testing.md](references/spec-driven-testing.md)
* **Storage state (cookies, localStorage)** [references/storage-state.md](references/storage-state.md)
* **Test generation** [references/test-generation.md](references/test-generation.md)
* **Tracing** [references/tracing.md](references/tracing.md)
* **Video recording** [references/video-recording.md](references/video-recording.md)
* **Inspecting element attributes** [references/element-attributes.md](references/element-attributes.md)
