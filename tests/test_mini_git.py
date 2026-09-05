"""과제의 핵심 동작과 실패 입력 회귀 검사."""

import ast
from datetime import datetime, timezone
from pathlib import Path
import unittest

from mini_git.algorithms import merge_sort, shortest_path, topological_order
from mini_git.cli import execute
from mini_git.repository import Commit, Repository


class MiniGitTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repository()
        self.repo.initialize("Alice Kim")

    def fork(self):
        root = self.repo.commit("Initial commit")
        self.repo.branch("feature")
        left = self.repo.commit("Add payment feature")
        self.repo.switch("feature")
        right = self.repo.commit("Add login feature")
        return root, left, right

    def test_branch_parent_and_switch(self):
        root, left, right = self.fork()
        self.assertEqual(left.parents, (root.hash,))
        self.assertEqual(right.parents, (root.hash,))
        self.assertEqual(self.repo.branches["main"], left.hash)

    def test_merge_and_topological_log(self):
        root, left, right = self.fork()
        merged = self.repo.commit("merge", merge_branch="main")
        self.assertEqual(merged.parents, (right.hash, left.hash))
        positions = {c.hash: i for i, c in enumerate(self.repo.log())}
        for commit in self.repo.commits.values():
            for parent in commit.parents:
                self.assertLess(positions[parent], positions[commit.hash])
        self.assertEqual({c.hash for c in self.repo.ancestors(merged.hash)}, {root.hash, left.hash, right.hash})

    def test_path_bidirectional_and_same(self):
        root, left, right = self.fork()
        self.assertEqual(self.repo.path(left.hash, right.hash), [left.hash, root.hash, right.hash])
        self.assertEqual(self.repo.path(root.hash, root.hash), [root.hash])

    def test_path_tie_break(self):
        root, left, right = self.fork()
        merged = self.repo.commit("merge", merge_branch="main")
        self.assertEqual(self.repo.path(root.hash, merged.hash), [root.hash, left.hash, merged.hash])
        self.assertEqual(self.repo.path(merged.hash, root.hash), [merged.hash, left.hash, root.hash])

    def test_disconnected_roots(self):
        self.repo.branch("empty")
        first = self.repo.commit("first")
        self.repo.switch("empty")
        second = self.repo.commit("second")
        self.assertIsNone(self.repo.path(first.hash, second.hash))
        self.assertEqual(execute(self.repo, f"PATH {first.hash} {second.hash}"), "No path")

    def test_indexes(self):
        a = self.repo.commit("Login LOGIN feature")
        self.repo.commit("login, only")
        self.assertEqual(self.repo.search("LOGIN"), [a])
        self.assertEqual(self.repo.search("feature login"), [a])
        self.assertEqual(self.repo.search("missing"), [])
        self.assertEqual(len(self.repo.search(author="Alice Kim")), 2)
        self.assertEqual(self.repo.search(author="alice kim"), [])
        self.assertEqual(len(self.repo.keyword_index["login"]), 1)

    def test_search_does_not_scan_commits(self):
        target = self.repo.commit("needle")

        class LookupOnly(dict):
            def __iter__(self):
                raise AssertionError("full scan")

            def values(self):
                raise AssertionError("full scan")

            def items(self):
                raise AssertionError("full scan")

        self.repo.commits = LookupOnly(self.repo.commits)
        self.assertEqual(self.repo.search("needle"), [target])
        self.assertEqual(self.repo.search(author="Alice Kim"), [target])

    def test_stable_sort(self):
        data = [(2, "a"), (1, "b"), (2, "c"), (1, "d")]
        self.assertEqual(merge_sort(data, lambda x: x[0]), [(1, "b"), (1, "d"), (2, "a"), (2, "c")])
        self.assertEqual(data[0], (2, "a"))
        self.assertEqual(merge_sort([]), [])
        self.assertEqual(merge_sort([4, 3, 2, 1]), [1, 2, 3, 4])

    def test_author_and_date_sort(self):
        self.repo.author = "Zoe"
        a = self.repo.commit("a")
        self.repo.author = "Amy"
        b = self.repo.commit("b")
        self.assertEqual(self.repo.log("author"), [b, a])
        self.assertEqual(self.repo.log("date"), [a, b])

    def test_unique_ids_and_deep_history(self):
        for i in range(1200):
            last = self.repo.commit(str(i))
        self.assertEqual(len(self.repo.commits), 1200)
        self.assertEqual(len(self.repo.ancestors(last.hash)), 1199)
        self.assertEqual(len(self.repo.log()), 1200)

    def test_cli_quotes_and_case(self):
        repo = Repository()
        self.assertIn("Alice Kim", execute(repo, 'iNiT "Alice Kim"'))
        self.assertIn("Add login feature", execute(repo, 'CoMmIt "Add login feature"'))
        self.assertIn("Found 1", execute(repo, 'SEARCH --author="Alice Kim"'))
        self.assertIsNone(execute(repo, "quit"))

    def test_cli_errors_and_no_mutation(self):
        for line in ('COMMIT "', "COMMIT", 'COMMIT " "', "LOG --sort-by=bad", "SEARCH --author=", "PATH one", "EXIT extra"):
            with self.subTest(line=line):
                self.assertEqual(execute(self.repo, line), "Invalid args")
        self.assertEqual(execute(self.repo, "SWITCH absent"), "Unknown branch: absent")
        self.assertEqual(execute(self.repo, "ANCESTORS absent"), "Unknown commit: absent")
        self.assertEqual(execute(self.repo, "INIT Bob"), "Already initialized")
        self.assertEqual(execute(Repository(), "LOG"), "Repository not initialized")
        self.assertEqual(self.repo.commits, {})

    def test_empty_and_merge_errors(self):
        self.assertEqual(self.repo.log(), [])
        self.repo.branch("empty")
        self.assertIn("two distinct", execute(self.repo, "MERGE empty"))
        a = self.repo.commit("a")
        self.assertEqual(self.repo.ancestors(a.hash), [])
        self.assertIn("two distinct", execute(self.repo, "MERGE main"))
        self.assertEqual(len(self.repo.commits), 1)

    def test_cycle_detection(self):
        now = datetime.now(timezone.utc)
        commits = {"a": Commit("a", "", "", now, ("b",)), "b": Commit("b", "", "", now, ("a",))}
        with self.assertRaisesRegex(ValueError, "Cycle"):
            topological_order(commits, {"a": ["b"], "b": ["a"]})

    def test_no_builtin_sort_calls(self):
        root = Path(__file__).resolve().parents[1]
        for file in (root / "mini_git").glob("*.py"):
            tree = ast.parse(file.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    self.assertFalse(isinstance(node.func, ast.Name) and node.func.id == "sorted")
                    self.assertFalse(isinstance(node.func, ast.Attribute) and node.func.attr == "sort")


if __name__ == "__main__":
    unittest.main()
