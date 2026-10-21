"""Verify the ChatGPT share payload resolver without fetching external content."""
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fetch_chatgpt_share",
    ROOT / "skills/shared/fetch-known-url/scripts/fetch_chatgpt_share.py",
)
helper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(helper)


class ResolveRefTests(unittest.TestCase):
    def test_plain_refs_resolve(self):
        payload = helper.ReactRouterPayload(["name", "Alice", {"_0": 1}, [2, 1]])
        self.assertEqual(payload.resolve_ref(3), [{"name": "Alice"}, "Alice"])

    def test_parent_child_cycle_terminates(self):
        # Node 2 lists node 5 as a child; node 5 points back to node 2 as parent.
        payload = helper.ReactRouterPayload(
            ["children", "parent", {"_0": 3}, [4], 5, {"_1": 2}]
        )
        self.assertEqual(payload.resolve_ref(2), {"children": [{"parent": None}]})

    def test_shared_ref_is_not_mistaken_for_cycle(self):
        payload = helper.ReactRouterPayload(["a", "b", "x", {"_0": 2, "_1": 2}])
        self.assertEqual(payload.resolve_ref(3), {"a": "x", "b": "x"})


if __name__ == "__main__":
    unittest.main()
