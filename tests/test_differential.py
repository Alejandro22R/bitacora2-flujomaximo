"""Prueba diferencial contra NetworkX (referencia de la tabla), con semilla fija."""

import unittest

import networkx as nx

from _common import to_networkx
from generators import clinic_network, derived_rng, random_network
from maxflow import edmonds_karp, ford_fulkerson, min_cut

SEED = 2026


class TestDifferential(unittest.TestCase):
    def test_redes_aleatorias_contra_networkx(self):
        for k in range(150):
            rng = derived_rng(SEED, k)
            n = rng.randint(5, 60)
            net, s, t = random_network(n, rng.randint(1, 6), rng.choice([1, 5, 100]), rng)
            g = to_networkx(net)
            value, partition = nx.minimum_cut(g, s, t)
            self.assertEqual(nx.maximum_flow_value(g, s, t), value)
            ff, ek = ford_fulkerson(net, s, t), edmonds_karp(net, s, t)
            self.assertEqual(ff.value, value, f"FF distinto en caso {k}")
            self.assertEqual(ek.value, value, f"EK distinto en caso {k}")
            self.assertEqual(min_cut(net, s).capacity, value)

    def test_caso_de_uso_clinica_contra_networkx(self):
        for k in range(30):
            rng = derived_rng(SEED, 10_000 + k)
            net, s, t, _, demand = clinic_network(rng.randint(2, 8), rng)
            value = nx.maximum_flow_value(to_networkx(net), s, t)
            self.assertEqual(edmonds_karp(net, s, t).value, value)
            self.assertLessEqual(value, demand)


if __name__ == "__main__":
    unittest.main()
