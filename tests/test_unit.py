import unittest

from _common import CLRS_EDGES, build
from maxflow import (FlowNetwork, edmonds_karp, ford_fulkerson, max_flow_min_cut, min_cut,
                     verify_flow)

ALGOS = [ford_fulkerson, edmonds_karp]


class TestMaxFlow(unittest.TestCase):
    def test_red_de_clrs_vale_23(self):
        for algo in ALGOS:
            net = build(6, CLRS_EDGES)
            r = algo(net, 0, 5)
            self.assertEqual(r.value, 23, algo.__name__)
            self.assertEqual(verify_flow(net, 0, 5, r.flows, r.value), [])

    def test_una_sola_arista(self):
        for algo in ALGOS:
            self.assertEqual(algo(build(2, [(0, 1, 7)]), 0, 1).value, 7)

    def test_sin_camino_da_cero_y_corte_vacio(self):
        for algo in ALGOS:
            net = build(4, [(0, 1, 5), (2, 3, 5)])
            r = algo(net, 0, 3)
            self.assertEqual(r.value, 0)
            self.assertEqual(r.augmentations, 0)
            self.assertEqual(min_cut(net, 0).capacity, 0)

    def test_capacidad_cero_no_aporta(self):
        for algo in ALGOS:
            self.assertEqual(algo(build(3, [(0, 1, 0), (1, 2, 9)]), 0, 2).value, 0)

    def test_aristas_paralelas_se_suman(self):
        for algo in ALGOS:
            self.assertEqual(algo(build(2, [(0, 1, 3), (0, 1, 4)]), 0, 1).value, 7)

    def test_aristas_antiparalelas(self):
        for algo in ALGOS:
            net = build(3, [(0, 1, 5), (1, 0, 5), (1, 2, 3)])
            self.assertEqual(algo(net, 0, 2).value, 3)

    def test_cuello_de_botella_en_serie(self):
        for algo in ALGOS:
            net = build(4, [(0, 1, 10), (1, 2, 2), (2, 3, 10)])
            self.assertEqual(algo(net, 0, 3).value, 2)

    def test_se_puede_ejecutar_dos_veces_sobre_la_misma_red(self):
        net = build(6, CLRS_EDGES)
        self.assertEqual(ford_fulkerson(net, 0, 5).value, edmonds_karp(net, 0, 5).value)

    def test_validaciones_de_entrada(self):
        net = FlowNetwork(3)
        with self.assertRaises(ValueError):
            net.add_edge(0, 1, -1)
        with self.assertRaises(ValueError):
            net.add_edge(0, 0, 1)
        with self.assertRaises(ValueError):
            net.add_edge(0, 5, 1)
        with self.assertRaises(ValueError):
            net.add_edge(0, 1, 1.5)
        with self.assertRaises(ValueError):
            edmonds_karp(net, 1, 1)
        with self.assertRaises(ValueError):
            FlowNetwork(1)


class TestMinCut(unittest.TestCase):
    def test_corte_de_clrs(self):
        net = build(6, CLRS_EDGES)
        r, cut = max_flow_min_cut(net, 0, 5)
        self.assertEqual(cut.capacity, r.value)
        self.assertEqual(sorted(cut.edges), [(1, 3, 12), (4, 3, 7), (4, 5, 4)])
        self.assertIn(0, cut.source_side)
        self.assertNotIn(5, cut.source_side)

    def test_corte_por_arista_cuello_de_botella(self):
        net = build(4, [(0, 1, 10), (1, 2, 2), (2, 3, 10)])
        _, cut = max_flow_min_cut(net, 0, 3, method="ford_fulkerson")
        self.assertEqual(cut.edges, [(1, 2, 2)])

    def test_verify_detecta_flujos_invalidos(self):
        net = build(3, [(0, 1, 5), (1, 2, 5)])
        self.assertTrue(verify_flow(net, 0, 2, [6, 6], 6))
        self.assertTrue(verify_flow(net, 0, 2, [5, 3], 3))


if __name__ == "__main__":
    unittest.main()
