import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import networkx as nx

from maxflow import FlowNetwork


def to_networkx(net: FlowNetwork) -> nx.DiGraph:
    """Convierte la red a DiGraph sumando capacidades de aristas paralelas."""
    g = nx.DiGraph()
    g.add_nodes_from(range(net.n))
    for _, u, v, c in net.edges():
        if g.has_edge(u, v):
            g[u][v]["capacity"] += c
        else:
            g.add_edge(u, v, capacity=c)
    return g


def build(n, edges):
    net = FlowNetwork(n)
    for u, v, c in edges:
        net.add_edge(u, v, c)
    return net


CLRS_EDGES = [(0, 1, 16), (0, 2, 13), (1, 2, 10), (2, 1, 4), (1, 3, 12), (3, 2, 9),
              (2, 4, 14), (4, 3, 7), (3, 5, 20), (4, 5, 4)]
