// Helpers shared by the global pre-commit checkers: git calls, per-repo
// gitignore-like path rules, and the merge-commit exemption.

import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";

export function git(args, options = {}) {
  return execFileSync("git", args, {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
    ...options,
  });
}

export function readIfExists(file) {
  try {
    return fs.readFileSync(file, "utf8");
  } catch {
    return "";
  }
}

export function globToRegExp(pattern) {
  const anchored = pattern.startsWith("/");
  let source = anchored ? pattern.slice(1) : pattern;
  const dirPattern = source.endsWith("/");
  if (dirPattern) {
    source = `${source}**`;
  }

  let regex = "";
  for (let i = 0; i < source.length; i += 1) {
    const char = source[i];
    const next = source[i + 1];
    if (char === "*" && next === "*") {
      regex += ".*";
      i += 1;
    } else if (char === "*") {
      regex += "[^/]*";
    } else if (char === "?") {
      regex += "[^/]";
    } else if (/[.+^${}()|[\]\\]/.test(char)) {
      regex += `\\${char}`;
    } else {
      regex += char;
    }
  }

  if (!anchored && !source.includes("/")) {
    regex = `(^|.*/)${regex}$`;
  } else {
    regex = `^${regex}$`;
  }
  return new RegExp(regex);
}

export function parseIgnoreRules(text) {
  const rules = [];
  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    const negated = line.startsWith("!");
    const pattern = negated ? line.slice(1) : line;
    rules.push({ negated, re: globToRegExp(pattern) });
  }
  return rules;
}

export function loadIgnoreRules(repoRoot, fileName) {
  return parseIgnoreRules(readIfExists(path.join(repoRoot, fileName)));
}

export function isIgnored(file, rules) {
  let ignored = false;
  for (const rule of rules) {
    if (rule.re.test(file)) ignored = !rule.negated;
  }
  return ignored;
}

// During a merge commit, `git diff --cached` lists every file the other
// branch brings in — including files this branch never touched, which
// already passed the checks on their own commits/PRs. Flagging those is a
// false positive (observed 2026-07-06: merges blocked on unchanged files
// from main). A file is exempt when its staged blob is byte-identical to
// the blob in ANY merge parent; conflict resolutions and genuinely edited
// files differ from every parent and are still checked.
export function mergeParentRefs() {
  try {
    const mergeHeadPath = git(["rev-parse", "--git-path", "MERGE_HEAD"]).trim();
    return readIfExists(mergeHeadPath)
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter(Boolean);
  } catch {
    return [];
  }
}

function blobOid(spec) {
  try {
    return git(["rev-parse", "--verify", "--quiet", spec]).trim() || null;
  } catch {
    return null;
  }
}

export function unchangedFromAnyParent(file, parents) {
  const staged = blobOid(`:${file}`);
  if (!staged) return false;
  return parents.some((parent) => blobOid(`${parent}:${file}`) === staged);
}
