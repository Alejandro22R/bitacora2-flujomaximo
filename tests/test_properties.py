import unittest

from hypothesis import given, settings, strategies as st

from _common import build, to_networkx
from maxflow import edmonds_karp, ford_fulkerson, min_cut, verify_flow
import networkx as nx


@st.composite
def networks(draw):
    n = draw(st.integers(min_value=2, max_value=9))
    edge = st.tuples(st.integers(0, n - 1), st.integers(0, n - 1), st.integers(0, 12))
    edges = [e for e in draw(st.lists(edge, max_size=30)) if e[0] != e[1]]
    return build(n, edges), n


SETTINGS = dict(max_examples=300, derandomize=True, deadline=None)


class TestProperties(unittest.TestCase):
    @settings(**SETTINGS)
    @given(networks(), st.data())
    def test_flujo_valido_y_dualidad(self, built, data):
        """Capacidad y conservación; flujo = corte mínimo; ningún corte arbitrario lo baja."""
        net, n = built
        s, t = 0, n - 1
        for algo in (ford_fulkerson, edmonds_karp):
            r = algo(net, s, t)
            self.assertEqual(verify_flow(net, s, t, r.flows, r.value), [])
            cut = min_cut(net, s)
            self.assertEqual(cut.capacity, r.value)
            self.assertIn(s, cut.source_side)
            self.assertNotIn(t, cut.source_side)
            others = [v for v in range(n) if v not in (s, t)]
            chosen = data.draw(st.sets(st.sampled_from(others))) if others else set()
            side = chosen | {s}
            capacity = sum(c for _, u, v, c in net.edges() if u in side and v not in side)
            self.assertGreaterEqual(capacity, r.value)

    @settings(**SETTINGS)
    @given(networks())
    def test_ambos_algoritmos_coinciden_con_networkx(self, built):
        net, n = built
        expected = nx.maximum_flow_value(to_networkx(net), 0, n - 1)
        self.assertEqual(ford_fulkerson(net, 0, n - 1).value, expected)
        self.assertEqual(edmonds_karp(net, 0, n - 1).value, expected)


if __name__ == "__main__":
    unittest.main()
