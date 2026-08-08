# HTML Lesson Presentation

Load this reference only after the learner selects `h`, approves an adaptive
switch to HTML, or the lesson is being handed to a renderer.

## Medium Boundary

- `m`: keep lesson content and the authoritative MCQ in Chat Markdown.
- `h`: render each lesson as self-contained HTML; keep the authoritative MCQ in
  chat.
- `a`: start in chat. Before switching, explain the concrete benefit for the
  upcoming level and get approval.

Follow the shared `html-explainer` skill for artifact requirements. Its embedded
quiz is practice only; only the chat MCQ controls progression. In chat, provide
only a short introduction and the absolute file path, ask the learner to read
the artifact, then present the authoritative MCQ.

Use plain zh-tw, mobile-friendly layout, and expand every unfamiliar English
acronym on first use. If several acronyms appear, add a short glossary box.

## Default Visual System

Match the learner's gu-log Solarized Light theme:

- Background `#fdf6e3`; cards `#eee8d5`; hover `#e5dfc9`; borders `#d3cbb7`.
- Body `#556b73`; headings/muted `#4a5a5e`.
- Emphasis `#955330`; links/labels `#1c679b`; positive `#1d6a5c`.
- Never color bold body text red. Reserve amber `#c47a00` on `#fff3cd` for real
  warning callouts only.
- Cards use the surface background, 1px border, optional 3–4px accent left
  border, and 8–18px radius.
- Use `Inter`, `Noto Sans TC`; zh body line-height 1.8 and headings 1.3.

The learner may override the theme per session. For a requested Dracula variant,
use background `#282a36`, text `#cecdda`, and accent `#ff79c6` unless the learner
specifies different tokens.

## Renderer Handoff

When a side agent renders HTML:

1. The orchestrator writes the complete per-level content spec in zh-tw.
2. The renderer does not invent lesson content.
3. Tell the renderer to read the `level-up` skill and
   `examples/level2-eav.html`, the tone/layout gold standard.
4. The orchestrator need not open the example; it only routes the renderer to
   it.
