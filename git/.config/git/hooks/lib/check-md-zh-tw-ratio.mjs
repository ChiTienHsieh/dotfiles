#!/usr/bin/env node

import path from "node:path";
import os from "node:os";
import {
  git,
  isIgnored,
  loadIgnoreRules,
  mergeParentRefs,
  readIfExists,
  unchangedFromAnyParent,
} from "./staged-files.mjs";

const DEFAULT_THRESHOLD = 0.8;
const DEFAULT_MIN_CHARS = 30;

const DEFAULT_ALLOWED_TERMS = new Set(
  [
    "ai",
    "api",
    "astro",
    "auto",
    "actor",
    "actors",
    "agent",
    "agents",
    "allowlist",
    "and",
    "alternative",
    "alternatives",
    "administration",
    "backend",
    "base",
    "branch",
    "broad",
    "bypass",
    "bun",
    "cd",
    "check",
    "checks",
    "change",
    "ci",
    "cli",
    "clawd",
    "clawd-vm",
    "claude",
    "codeql",
    "codex",
    "command",
    "commands",
    "content",
    "commit",
    "compatibility",
    "config",
    "credential",
    "credentials",
    "css",
    "date",
    "decision",
    "decisions",
    "default",
    "deletion",
    "deterministic",
    "draft",
    "dotfiles",
    "en",
    "evidence",
    "eslint",
    "fastapi",
    "file",
    "frontend",
    "frontmatter",
    "given",
    "git",
    "github",
    "glossary",
    "gpt",
    "gu",
    "gu-log",
    "guard",
    "head",
    "html",
    "human",
    "http",
    "https",
    "i18n",
    "id",
    "json",
    "lab",
    "lane",
    "legacy",
    "llm",
    "local",
    "local-only",
    "mac-cdx",
    "machine",
    "may",
    "markdown",
    "md",
    "mdx",
    "merge",
    "mergeable",
    "memory",
    "model",
    "must",
    "note",
    "notes",
    "node",
    "not",
    "npm",
    "openai",
    "openspec",
    "operator",
    "or",
    "org",
    "organization",
    "packet",
    "path",
    "paths",
    "people",
    "pnpm",
    "pr",
    "private",
    "policy",
    "provider",
    "prettier",
    "protection",
    "pull",
    "push",
    "python",
    "readme",
    "read",
    "record",
    "rejected",
    "repo",
    "repository",
    "request",
    "required",
    "requirement",
    "review",
    "rubric",
    "rules",
    "ruleset",
    "rulesets",
    "runtime",
    "scenario",
    "scope",
    "secret",
    "secrets",
    "selected",
    "selected-repo",
    "shall",
    "shroomdog",
    "should",
    "skipped",
    "smoke",
    "sp-pipeline",
    "source",
    "stash",
    "state",
    "status",
    "success",
    "summary",
    "ssh",
    "target",
    "test",
    "tests",
    "then",
    "ticketid",
    "title",
    "token",
    "tokens",
    "toml",
    "tribunal",
    "typescript",
    "ui",
    "uri",
    "url",
    "uv",
    "ux",
    "vercel",
    "value",
    "values",
    "vm",
    "workflow",
    "workflows",
    "when",
    "write",
    "yaml",
    "yml",
    "zh",
    "zh-tw",
  ].map(normalizeTerm),
);

function normalizeTerm(term) {
  return String(term).trim().toLowerCase().replace(/^[-_./]+|[-_./]+$/g, "");
}

function parsePolicy(repoRoot) {
  const policy = {
    enabled: true,
    threshold: DEFAULT_THRESHOLD,
    minChars: DEFAULT_MIN_CHARS,
  };
  const policyText = readIfExists(path.join(repoRoot, ".md-zh-tw-policy"));
  for (const rawLine of policyText.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    const match = line.match(/^([A-Za-z][A-Za-z0-9_-]*)\s*[:=]\s*(.+)$/);
    if (!match) continue;
    const key = match[1].toLowerCase();
    const value = match[2].trim().replace(/^["']|["']$/g, "");
    if (key === "enabled") {
      policy.enabled = !["false", "0", "no", "off"].includes(value.toLowerCase());
    }
    if (key === "threshold") {
      const threshold = Number(value);
      if (Number.isFinite(threshold) && threshold >= 0 && threshold <= 1) {
        policy.threshold = threshold;
      }
    }
    if (key === "minchars" || key === "min_chars") {
      const minChars = Number.parseInt(value, 10);
      if (Number.isFinite(minChars) && minChars >= 0) {
        policy.minChars = minChars;
      }
    }
  }
  return policy;
}

function addAllowedTermsFromFile(allowed, file) {
  const text = readIfExists(file);
  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    allowed.add(normalizeTerm(line));
  }
}

function loadAllowedTerms(repoRoot) {
  const allowed = new Set(DEFAULT_ALLOWED_TERMS);
  const globalAllowFiles = [
    path.join(os.homedir(), ".config", "git", "md-zh-tw-allow"),
    path.join(os.homedir(), ".md-zh-tw-allow"),
  ];
  for (const file of globalAllowFiles) {
    addAllowedTermsFromFile(allowed, file);
  }
  addAllowedTermsFromFile(allowed, path.join(repoRoot, ".md-zh-tw-allow"));
  return allowed;
}

function stagedMarkdownFiles() {
  // -z / NUL keeps paths with spaces or newlines intact; do not trim.
  const out = git(["diff", "-z", "--cached", "--name-only", "--diff-filter=ACM"]);
  return out
    .split("\0")
    .filter((line) => line.length > 0 && line.endsWith(".md"));
}

function stagedContent(file) {
  return git(["show", `:${file}`]);
}

function hasFileOptOut(raw) {
  return (
    /<!--\s*md-zh-tw:\s*(ignore|off|false)\s*-->/i.test(raw) ||
    /^mdZhTw:\s*false\s*$/im.test(raw) ||
    /^zhTwRatio:\s*false\s*$/im.test(raw)
  );
}

function stripMarkdown(raw) {
  let text = raw.replace(/\r\n/g, "\n");
  text = text.replace(/^---\n[\s\S]*?\n---\n?/, "\n");
  text = text.replace(/^```[\s\S]*?^```\s*/gm, "\n");
  text = text.replace(/^~~~[\s\S]*?^~~~\s*/gm, "\n");
  text = text.replace(/^(?: {4}|\t).+$/gm, "\n");
  text = text.replace(/<!--[\s\S]*?-->/g, "\n");
  text = text.replace(/!\[([^\]]*)\]\([^)]+\)/g, "$1");
  text = text.replace(/\[([^\]]+)\]\([^)]+\)/g, "$1");
  text = text.replace(/`[^`]*`/g, " ");
  text = text.replace(/https?:\/\/\S+/g, " ");
  text = text.replace(/<https?:\/\/[^>]+>/g, " ");
  text = text.replace(/^\s*[-*]\s+\[[ xX]\]\s*/gm, " ");
  text = text.replace(/[>#*_~|[\](){}]/g, " ");
  return text;
}

function score(text, allowedTerms) {
  const zhMatches = text.match(/[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]/gu) || [];
  const tokens = text.match(/[A-Za-z][A-Za-z0-9_.+#/-]*/g) || [];
  let latinPenalty = 0;
  const offenders = new Map();
  for (const token of tokens) {
    const normalized = normalizeTerm(token);
    if (!normalized) continue;
    if (allowedTerms.has(normalized)) continue;
    if (/^\d+$/.test(normalized)) continue;
    const letters = (normalized.match(/[a-z]/g) || []).length;
    if (letters === 0) continue;
    latinPenalty += 1;
    offenders.set(normalized, (offenders.get(normalized) || 0) + 1);
  }
  const zh = zhMatches.length;
  const total = zh + latinPenalty;
  const ratio = total === 0 ? 1 : zh / total;
  const topOffenders = [...offenders.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([term, count]) => `${term}×${count}`);
  return { zh, latinPenalty, total, ratio, topOffenders };
}

function main() {
  const repoRoot = git(["rev-parse", "--show-toplevel"]).trim();
  const policy = parsePolicy(repoRoot);
  if (!policy.enabled) return;

  let files = stagedMarkdownFiles();
  if (files.length === 0) return;

  const mergeParents = mergeParentRefs();
  if (mergeParents.length > 0) {
    files = files.filter((file) => !unchangedFromAnyParent(file, mergeParents));
  }
  if (files.length === 0) return;

  const ignoreRules = loadIgnoreRules(repoRoot, ".md-zh-tw-ignore");
  const allowedTerms = loadAllowedTerms(repoRoot);
  const failures = [];

  for (const file of files) {
    if (isIgnored(file, ignoreRules)) continue;
    const raw = stagedContent(file);
    if (hasFileOptOut(raw)) continue;
    const prose = stripMarkdown(raw);
    const result = score(prose, allowedTerms);
    if (result.total < policy.minChars) continue;
    if (result.ratio < policy.threshold) {
      failures.push({ file, ...result });
    }
  }

  if (failures.length === 0) return;

  console.error("");
  console.error("❌ Markdown zh-tw ratio check failed");
  console.error(
    `   預設規則：staged .md prose 的繁中文字元比例需 >= ${(policy.threshold * 100).toFixed(0)}%`,
  );
  console.error("");
  for (const failure of failures) {
    console.error(
      `  - ${failure.file}: ${(failure.ratio * 100).toFixed(1)}% zh-tw ` +
        `(zh=${failure.zh}, englishPenalty=${failure.latinPenalty})`,
    );
    if (failure.topOffenders.length > 0) {
      console.error(`    English terms counted: ${failure.topOffenders.join(", ")}`);
    }
  }
  console.error("");
  console.error("   可用這些方式 opt out：");
  console.error("   - repo 關閉：.md-zh-tw-policy 內寫 enabled=false");
  console.error("   - 路徑排除：.md-zh-tw-ignore 內寫 gitignore-like pattern");
  console.error("   - 單檔排除：檔案內寫 <!-- md-zh-tw: ignore -->");
  console.error("   - 專案術語放行：.md-zh-tw-allow 一行一個 English term");
  console.error("");
  process.exit(1);
}

main();
