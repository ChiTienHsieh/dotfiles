# Property Tracking Sheet Design

## Learner Goal
- Design a property comparison sheet that keeps human decisions prominent, supports agent-maintained evidence, and scales from initial viewing to selective follow-up checks.

## Current Level
- Status: learning
- Last updated: 2026-08-20
- Confidence: medium

## Evidence
- 2026-08-13: Selected an aircraft-cockpit analogy, solid-foundation depth, and Chat Markdown for staged design and implementation.
- 2026-08-13: Chose a separate measurement log with one test per row and the main comparison sheet retaining only a summary.
- 2026-08-13: Chose shortlist plus decision-relevant risk as the default measurement trigger while keeping ad hoc measurement welcome and non-mandatory.
- 2026-08-13: Chose free-text measurement entry without dropdowns, relying on agent-side semantic normalization while preserving original observations.
- 2026-08-13: Named the follow-up measurement sheet `checks` to keep agent communication short and leave room for non-noise checks.
- 2026-08-13: Confirmed the canonical main-sheet decision zone as property, subjective rating, household viewing notes, Codex assessment, map, and total price; applied it without inferring new human notes.
- 2026-08-13: Renamed the assessment owner generically to Agent, migrated prior decision notes, and separated stale properties into a recoverable archive before continuing schema design.
- 2026-08-13: Prioritized actual usable area, layout, location, nearest metro, and walking time immediately after total price.
- 2026-08-13: Prioritized hard-to-fix building and comfort attributes as same-floor exhaust, ERV readiness, window plus acoustic experience, then daylight/orientation/building distance; kept them as concise free-text fields.
- 2026-08-14: Reframed bathroom evaluation around ventilation and drying performance rather than treating an exterior window as a premium requirement; placed it among lower-priority living-equipment fields.
- 2026-08-14: Chose one combined free-text field for same-floor household count and elevator-to-household ratio, preserving useful density context without widening the sheet into separate raw-number columns.
- 2026-08-14: Expanded the existing parking field to cover usability in the same cell, preserving type and price while avoiding a redundant extra column.
- 2026-08-14: Consolidated duplicate usable-area fields into one canonical field, preserving precise values and visibly retaining a conflicting legacy range for later confirmation before deleting the duplicate column.
- 2026-08-20: Ranked the remaining high-value comparison metrics as age, deed area, common-area ratio, unit price, floor, and total floors; explicitly moved age left because it affects renovation risk, financing, maintenance, and resale rather than treating it as minor metadata.

## Known Gaps
- The placement of remaining secondary property attributes and legacy columns is not yet confirmed.
- The order of lower-priority operational and legacy fields after the core comparison metrics is not yet confirmed.

## Teaching Notes
- Use row and column as the primary spreadsheet terms.
- Keep each decision and each spreadsheet edit small, followed by readback verification.

## Next Suggested Levels
- Decide whether separate legacy pros and cons should be merged into the Agent assessment or retained as dedicated columns.
- Remove or consolidate redundant legacy columns before copying the schema to the unchecked sheet.
