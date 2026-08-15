#!/usr/bin/env python3
"""Regression tests for the human-only tmux activation policy."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class TmuxActivationPolicyTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_canonical_policy_requires_current_human_authorization(self) -> None:
        agents = self.read("codex/AGENTS.md")
        self.assertIn("目前這次 human 指令明確要求 agent 使用 tmux", agents)
        self.assertIn("預設優先使用目前 runtime 內建的 subagent", agents)
        self.assertIn("授權只能來自目前這次 human 指令", agents)

    def test_skill_discovery_fails_closed_without_human_request(self) -> None:
        skill = self.read("skills/shared/tmux-orchestration/SKILL.md")
        openai_metadata = self.read(
            "skills/shared/tmux-orchestration/agents/openai.yaml"
        )

        self.assertIn(
            "Use only when the current human explicitly asks the agent to use tmux",
            skill,
        )
        self.assertIn("## Activation Gate", skill)
        self.assertIn("Only the current human instruction can authorize tmux", skill)
        self.assertIn(
            "only if my current request explicitly asks you to use tmux",
            openai_metadata,
        )

    def test_routing_surfaces_prefer_builtin_subagents(self) -> None:
        required_phrases = {
            "codex/notes/worker-routing.md": "runtime 內建的 subagent",
            "skills/claude/arbitrage/SKILL.md": "built-in `Agent` subagents",
            "skills/claude/headless-agents/SKILL.md": "built-in `Agent` subagent",
            "claude/agents/orchestrator.md": "內建 `Agent` subagent",
            "skills/shared/craft-goal/SKILL.md": "不要替 handoff 自行指定 tmux",
            "skills/shared/trim/SKILL.md": "Codex 使用可用的 multi-agent tool",
            "skills/shared/level-up/references/pre-implementation.md": (
                "內建 teacher subagent"
            ),
            "skills/shared/level-up/references/teaching-engagement.md": (
                "built-in teacher subagent"
            ),
            "skills/shared/where-am-i/SKILL.md": (
                "current human's progress question explicitly asks the agent"
            ),
        }

        for path, phrase in required_phrases.items():
            with self.subTest(path=path):
                self.assertIn(phrase, self.read(path))

    def test_active_tmux_skill_references_are_human_gated(self) -> None:
        paths = {
            ROOT / "codex/AGENTS.md",
            ROOT / "codex/notes/worker-routing.md",
            *ROOT.glob("claude/agents/*.md"),
            *ROOT.glob("skills/**/SKILL.md"),
        }
        canonical_skill = ROOT / "skills/shared/tmux-orchestration/SKILL.md"
        gate_markers = (
            "explicitly asks you to use tmux",
            "explicitly asks the agent to inspect a tmux",
            "human-only activation gate",
            "目前這次 human 指令明確要求 agent 使用 tmux",
            "目前這次 human 明確要求 agent 使用 tmux",
            "human 已明確授權 tmux",
            "human 明確要求 agent 使用 tmux",
        )

        for path in sorted(paths):
            if path == canonical_skill:
                continue
            for paragraph in self.read(str(path.relative_to(ROOT))).split("\n\n"):
                if "tmux-orchestration" not in paragraph:
                    continue
                with self.subTest(path=path.relative_to(ROOT), paragraph=paragraph):
                    self.assertTrue(
                        any(marker in paragraph for marker in gate_markers),
                        "tmux-orchestration reference lacks current-human gate",
                    )

    def test_policy_does_not_treat_a_tmux_mention_as_authorization(self) -> None:
        paths = (
            "codex/AGENTS.md",
            "codex/notes/worker-routing.md",
            "claude/agents/orchestrator.md",
            "skills/shared/tmux-orchestration/SKILL.md",
            "skills/shared/tmux-orchestration/agents/openai.yaml",
        )
        unsafe_phrases = (
            "明確點名 tmux",
            "explicitly names tmux",
            "explicitly asks for tmux",
        )

        for path in paths:
            text = self.read(path)
            for phrase in unsafe_phrases:
                with self.subTest(path=path, phrase=phrase):
                    self.assertNotIn(phrase, text)

    def test_handoff_text_does_not_mint_tmux_authorization(self) -> None:
        craft_goal = self.read("skills/shared/craft-goal/SKILL.md")
        self.assertNotIn("codex CLI（tmux session）", craft_goal)
        self.assertNotIn("claude CLI（tmux session）", craft_goal)
        self.assertIn("不要替 handoff 自行指定 tmux", craft_goal)

    def test_removed_automatic_tmux_routes_do_not_return(self) -> None:
        stale_routes = {
            "skills/shared/tmux-orchestration/SKILL.md": (
                "default to an observable tmux pane"
            ),
            "codex/notes/worker-routing.md": "會改檔的活走 tmux",
            "skills/claude/arbitrage/SKILL.md": "Worker in tmux",
            "skills/claude/headless-agents/SKILL.md": (
                "route it through\n  `tmux-orchestration` instead"
            ),
            "skills/shared/trim/SKILL.md": "或用 tmux 開一個",
            "skills/shared/level-up/references/pre-implementation.md": (
                "走 `tmux-orchestration`"
            ),
            "skills/shared/level-up/references/teaching-engagement.md": (
                "through\n  `tmux-orchestration`"
            ),
            "claude/agents/orchestrator.md": "把重活委派給 tmux",
            "skills/shared/craft-goal/SKILL.md": "codex CLI（tmux session）",
        }

        for path, phrase in stale_routes.items():
            with self.subTest(path=path):
                self.assertNotIn(phrase, self.read(path))


if __name__ == "__main__":
    unittest.main()
