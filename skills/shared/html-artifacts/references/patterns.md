# HTML Artifact Patterns

Use this reference when an HTML artifact would be more useful than Markdown. Pick the smallest pattern that makes the work easier to review, compare, manipulate, or send back to Codex.

This catalog is inspired by Thariq Shihipar's HTML effectiveness examples and the public `dogum/html-artifacts` skill. Use it as pattern guidance, not as a requirement to make every output elaborate.

## Planning And Exploration

Use when the user needs to compare options, choose a path, or inspect tradeoffs.

- **Implementation plan**: sections for goal, constraints, phases, risks, test plan, and open questions; add status toggles only if the artifact will be revisited.
- **Decision matrix**: sortable table with criteria, weights, score, rationale, and recommended option.
- **Architecture explorer**: split-pane diagram plus details panel for components, data flow, ownership, and failure modes.
- **Roadmap board**: grouped columns for now/next/later or milestone-based delivery; include copyable task lists.

Useful controls: tabs, filters, priority chips, expandable rationale, copy-as-Markdown.

## Code Review And Understanding

Use when Markdown would hide relationships between files, risks, and suggested fixes.

- **Review dashboard**: findings by severity, affected area, status, and test coverage; keep the highest-risk issue visible first.
- **Diff review walkthrough**: file list on the left, selected explanation on the right; use this for conceptual review, not as a replacement for real diffs.
- **Module map**: nodes for modules and edges for imports, data flow, or ownership; link each node to key files.
- **Risk register**: table for behavior risk, blast radius, mitigation, owner, and verification.

Useful controls: severity filters, file filters, copy finding, collapse resolved items.

## Design Systems And Prototypes

Use when visual comparison or interaction is the point of the deliverable.

- **Token sheet**: colors, typography, spacing, radii, shadows, and component examples in one responsive page.
- **Component variants**: grid of states, sizes, empty/error/loading variants, and accessibility notes.
- **Clickable flow**: simple state machine with screens, transitions, and realistic copy.
- **Animation sandbox**: controls for duration, easing, delay, density, and reduced-motion behavior.

Useful controls: theme switcher, state toggles, viewport preview, copy CSS variables.

## Diagrams And Decks

Use when spatial arrangement carries meaning.

- **Inline SVG diagram**: best for flows, sequence diagrams, system maps, and lifecycle views.
- **Timeline**: best for incidents, migrations, launch plans, or research chronology.
- **Slide deck**: full-screen sections with keyboard navigation when the user needs a presentation-like artifact.
- **Comparison wall**: side-by-side panels for vendors, APIs, frameworks, or product options.

Useful controls: fit-to-screen, section nav, keyboard arrows, export speaker notes.

## Research And Reports

Use when the user needs a readable synthesis with source grouping, confidence, or multiple lenses.

- **Research synthesis**: summary, key claims, evidence, caveats, and source list.
- **Status report**: current state, milestones, blockers, risks, and next actions.
- **Incident report**: timeline, impact, detection, root cause, remediation, and follow-ups.
- **Knowledge map**: topics, relationships, unresolved questions, and recommended reading order.

Useful controls: section nav, confidence filters, copy citation block, print-friendly mode.

## Custom Editors

Use when the user needs to manipulate structured data before bringing it back to Codex or another tool.

- **Triage board**: edit priority, owner, label, status, and notes; export Markdown or JSON.
- **Prompt tuner**: edit variables, compare prompt variants, and copy the selected prompt.
- **Feature flag editor**: toggle flags, variants, rollout notes, and export config.
- **Content planner**: reorder sections, edit titles, and export outline.

Useful controls: local-only state, reset, import JSON, export JSON, copy Markdown.

## Practical Checks

- Make the artifact useful before making it pretty.
- Keep content visible and scannable on mobile and desktop.
- Keep interactions obvious; hidden magic is just documentation debt wearing a nice jacket.
- Provide copy/export when the artifact is part of an agent loop.
- Use tables for dense comparable data, not cards.
- Use cards only for repeated items where each item has mixed content.
- Prefer native browser APIs over dependencies.
