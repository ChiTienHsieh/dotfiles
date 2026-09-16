---
name: html-artifacts
description: 製作單檔 HTML 工作文件。使用者要求 HTML／互動文件，或同意將 Markdown 改成瀏覽器文件時使用；HTML 教學頁用 html-explainer。
---

# HTML Artifacts

## Overview

Create a single-file `.html` artifact when the work needs a browser-native surface: layout, navigation, tables, diagrams, controls, copy/export buttons, or lightweight interaction.

Default to **Ask Before HTML** unless the user explicitly asks for HTML. The skill should improve the human review loop, not turn every answer into a tiny website with opinions.

## Decision

Use HTML directly when the user requests HTML, an interactive document, or a
browser-openable artifact. A request for a report, diagram, or plan alone does
not select HTML; use Markdown or suggest HTML when its interaction would help.

Suggest HTML first when:

- Markdown would flatten side-by-side comparison, spatial structure, state, or interaction
- the output needs multiple views over the same data
- the user needs to inspect, rank, filter, annotate, or copy structured output back to the agent
- the answer is long enough that navigation and progressive disclosure would change its usability

Stay in Markdown when:

- the answer is short, conversational, code-only, or mostly command instructions
- the output is intended to be a frequently edited source file
- a real application, package, or hosted frontend is the actual deliverable
- HTML would only be decoration

Unless the request is explicitly a teaching one, do not add quizzes, teaching analogies, or micro-worlds — route teaching requests to the html-explainer skill.

## Artifact Requirements

Build the artifact as a single `.html` file unless the user asks for a larger app.

- Include all CSS and JavaScript inline.
- Avoid external CDNs, fonts, images, or build steps unless the task truly needs them.
- Use semantic HTML, keyboard-friendly controls, accessible labels, sufficient contrast, and responsive layout.
- Prefer useful affordances: tabs, filters, search, sortable tables, accordions, copy buttons, export-to-Markdown/JSON, and lightweight local state.
- Preserve the artifact's job: help the user decide, inspect, understand, compare, or continue work.
- Put the main content on the first screen. Avoid landing-page hero treatment unless the user asks for a presentation or public-facing page.

## Workflow

1. Identify the artifact's job: review, plan, compare, explain, prototype, diagram, report, or edit.
2. Choose the smallest interaction model that helps that job.
3. Draft the data model before the markup when the artifact has repeated entities, filters, or export behavior.
4. Create a self-contained `.html` file in the task-appropriate location.
5. Verify the file opens locally when practical; use browser verification for UI-heavy artifacts.
6. Summarize where the file is and what workflow it supports.

## Pattern Reference

Read `references/patterns.md` when choosing artifact structure, interaction patterns, or a starting layout. It includes planning, code review, design, prototype, diagram, deck, research, report, and custom-editor patterns.

## Anti-Patterns

- Do not produce HTML just because it would look nicer than Markdown.
- Do not bury the useful output behind decorative chrome.
- Do not make card soup: repeated cards are fine for repeated items, but dense operational information often belongs in tables, split panes, timelines, or diagrams.
- Do not use generic gradient hero pages, emoji section labels, or ornamental SVGs unless they serve the artifact.
- Do not assume the artifact is a durable product. If the user needs a maintained app, build an app instead.

## Upstream Inspiration

This skill follows the idea demonstrated by Thariq Shihipar's HTML effectiveness examples and the public `dogum/html-artifacts` skill. Treat those as inspiration and pattern vocabulary; do not copy large text verbatim into generated artifacts.
