"""Regression tests for graph_executor.SuperGraph — the render pipeline state machine.

The engine ALLOWS loops, so it must terminate: a condition_func that never routes to END
(a cycle) must hit the step cap and abort with an error, not hang the unattended render.
Also covers normal DAG execution, both conditional branches, and unknown-node failure.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import graph_executor as ge  # noqa: E402


def _g():
    return ge.SuperGraph()


class SuperGraphTests(unittest.TestCase):
    def test_linear_dag_runs_all_nodes(self):
        g = _g()
        g.add_node("A", lambda s: {**s, "a": 1})
        g.add_node("B", lambda s: {**s, "b": 2})
        g.set_entry_point("A")
        g.add_edge("A", "B")
        g.add_edge("B", "END")
        r = g.compile().invoke({})
        self.assertEqual((r.get("a"), r.get("b")), (1, 2))
        self.assertNotIn("error", r)

    def test_conditional_routes_both_ways(self):
        def build(branch):
            g = _g()
            g.add_node("A", lambda s: s)
            g.add_node("PASS", lambda s: {**s, "out": "pass"})
            g.add_node("FAIL", lambda s: {**s, "out": "fail"})
            g.set_entry_point("A")
            g.add_conditional_edge("A", lambda s: branch)
            g.add_edge("PASS", "END")
            g.add_edge("FAIL", "END")
            return g.compile().invoke({})
        self.assertEqual(build("PASS")["out"], "pass")
        self.assertEqual(build("FAIL")["out"], "fail")

    def test_non_terminating_loop_is_capped(self):
        g = _g()
        g.add_node("X", lambda s: {**s, "n": s.get("n", 0) + 1})
        g.set_entry_point("X")
        g.add_conditional_edge("X", lambda s: "X")   # never routes to END
        r = g.compile().invoke({})
        self.assertIn("error", r)
        self.assertIn("step", r["error"].lower())
        self.assertLessEqual(r["n"], 201)            # bounded, did not hang

    def test_unknown_node_raises(self):
        g = _g()
        g.add_node("A", lambda s: s)
        g.set_entry_point("A")
        g.add_edge("A", "DOES_NOT_EXIST")
        with self.assertRaises(ValueError):
            g.compile().invoke({})

    def test_compile_without_entry_raises(self):
        with self.assertRaises(ValueError):
            _g().compile()


if __name__ == "__main__":
    unittest.main()
