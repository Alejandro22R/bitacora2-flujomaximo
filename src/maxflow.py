"""Flujo máximo y corte mínimo: Ford-Fulkerson (DFS) y Edmonds-Karp (BFS).

Representación
    Cada arista (u, v, c) se guarda junto con su arista inversa (v, u, 0) en
    posiciones consecutivas (e, e ^ 1) de tres listas paralelas: ``to`` (destino),
    ``cap`` (capacidad residual) y ``orig`` (capacidad original). Así la arista
    inversa de ``e`` es siempre ``e ^ 1`` y el flujo sobre una arista directa ``e``
    (índice par) es ``cap[e ^ 1]``.

Contadores (independientes de la máquina)
    augmentations : caminos de aumento usados.
    scans         : aristas examinadas durante las búsquedas de camino.

Las capacidades deben ser enteros no negativos; con capacidades enteras
Ford-Fulkerson termina porque cada aumento suma al menos 1 unidad de flujo.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


class FlowNetwork:
    """Red de flujo dirigida con vértices 0..n-1."""

    def __init__(self, n: int) -> None:
        if n < 2:
            raise ValueError("la red necesita al menos 2 vértices")
        self.n = n
        self.adj: list[list[int]] = [[] for _ in range(n)]
        self.to: list[int] = []
        self.cap: list[int] = []
        self.orig: list[int] = []

    def add_edge(self, u: int, v: int, c: int) -> int:
        """Agrega la arista u -> v con capacidad c y devuelve su índice (par)."""
        if not (0 <= u < self.n and 0 <= v < self.n):
            raise ValueError("vértice fuera de rango")
        if u == v:
            raise ValueError("no se permiten lazos (u == v)")
        if not isinstance(c, int) or isinstance(c, bool) or c < 0:
            raise ValueError("la capacidad debe ser un entero no negativo")
        e = len(self.to)
        self.to += [v, u]
        self.cap += [c, 0]
        self.orig += [c, 0]
        self.adj[u].append(e)
        self.adj[v].append(e + 1)
        return e

    def reset(self) -> None:
        """Restaura las capacidades residuales (flujo cero)."""
        self.cap[:] = self.orig

    def edges(self):
        """Itera las aristas directas como (índice, u, v, capacidad)."""
        for e in range(0, len(self.to), 2):
            yield e, self.to[e ^ 1], self.to[e], self.orig[e]

    def flows(self) -> list[int]:
        """Flujo sobre cada arista directa, en el orden de ``edges()``."""
        return [self.cap[e ^ 1] for e in range(0, len(self.to), 2)]


@dataclass
class FlowResult:
    value: int
    augmentations: int
    scans: int
    flows: list[int] = field(default_factory=list)


@dataclass
class MinCut:
    source_side: set[int]
    edges: list[tuple[int, int, int]]  # (u, v, capacidad)
    capacity: int


def _check_terminals(net: FlowNetwork, s: int, t: int) -> None:
    if not (0 <= s < net.n and 0 <= t < net.n):
        raise ValueError("fuente o sumidero fuera de rango")
    if s == t:
        raise ValueError("la fuente y el sumidero deben ser distintos")


def _augment(net: FlowNetwork, parent_edge: list[int], s: int, t: int) -> int:
    """Empuja el cuello de botella por el camino s -> t guardado en parent_edge."""
    path, v, b = [], t, None
    while v != s:
        e = parent_edge[v]
        path.append(e)
        b = net.cap[e] if b is None else min(b, net.cap[e])
        v = net.to[e ^ 1]
    for e in path:
        net.cap[e] -= b
        net.cap[e ^ 1] += b
    return b


def _find_path_dfs(net: FlowNetwork, s: int, t: int, counter: list[int]):
    """Busca un camino s -> t con DFS iterativo sobre la red residual."""
    visited = [False] * net.n
    parent_edge = [-1] * net.n
    ptr = [0] * net.n
    visited[s] = True
    stack = [s]
    while stack:
        u = stack[-1]
        if u == t:
            return parent_edge
        advanced = False
        while ptr[u] < len(net.adj[u]):
            e = net.adj[u][ptr[u]]
            ptr[u] += 1
            counter[0] += 1
            v = net.to[e]
            if net.cap[e] > 0 and not visited[v]:
                visited[v] = True
                parent_edge[v] = e
                stack.append(v)
                advanced = True
                break
        if not advanced:
            stack.pop()
    return None


def _find_path_bfs(net: FlowNetwork, s: int, t: int, counter: list[int]):
    """Busca un camino más corto s -> t (en aristas) con BFS sobre la red residual."""
    visited = [False] * net.n
    parent_edge = [-1] * net.n
    visited[s] = True
    queue = deque([s])
    while queue:
        u = queue.popleft()
        for e in net.adj[u]:
            counter[0] += 1
            v = net.to[e]
            if net.cap[e] > 0 and not visited[v]:
                visited[v] = True
                parent_edge[v] = e
                if v == t:
                    return parent_edge
                queue.append(v)
    return None


def _run(net: FlowNetwork, s: int, t: int, finder) -> FlowResult:
    _check_terminals(net, s, t)
    net.reset()
    value, augmentations, counter = 0, 0, [0]
    while True:
        parent_edge = finder(net, s, t, counter)
        if parent_edge is None:
            break
        value += _augment(net, parent_edge, s, t)
        augmentations += 1
    return FlowResult(value, augmentations, counter[0], net.flows())


def ford_fulkerson(net: FlowNetwork, s: int, t: int) -> FlowResult:
    """Ford-Fulkerson con búsqueda en profundidad. Costo O(E * f) con f el flujo máximo."""
    return _run(net, s, t, _find_path_dfs)


def edmonds_karp(net: FlowNetwork, s: int, t: int) -> FlowResult:
    """Edmonds-Karp (Ford-Fulkerson con BFS). Costo O(V * E^2), independiente de f."""
    return _run(net, s, t, _find_path_bfs)


def min_cut(net: FlowNetwork, s: int) -> MinCut:
    """Corte mínimo a partir de la red residual de un flujo máximo ya calculado.

    S = vértices alcanzables desde s con capacidad residual positiva. Las aristas
    que salen de S hacia fuera de S están saturadas y su capacidad suma el flujo máximo.
    """
    seen = [False] * net.n
    seen[s] = True
    queue = deque([s])
    while queue:
        u = queue.popleft()
        for e in net.adj[u]:
            v = net.to[e]
            if net.cap[e] > 0 and not seen[v]:
                seen[v] = True
                queue.append(v)
    side = {v for v in range(net.n) if seen[v]}
    cut = [(u, v, c) for _, u, v, c in net.edges() if u in side and v not in side]
    return MinCut(side, cut, sum(c for _, _, c in cut))


def max_flow_min_cut(net: FlowNetwork, s: int, t: int, method: str = "edmonds_karp"):
    """Calcula el flujo máximo con el método indicado y devuelve (FlowResult, MinCut)."""
    algo = {"edmonds_karp": edmonds_karp, "ford_fulkerson": ford_fulkerson}[method]
    result = algo(net, s, t)
    return result, min_cut(net, s)


def verify_flow(net: FlowNetwork, s: int, t: int, flows: list[int], value: int) -> list[str]:
    """Comprueba capacidad y conservación; devuelve la lista de violaciones (vacía si es válido)."""
    problems: list[str] = []
    balance = [0] * net.n  # entrada - salida
    for (e, u, v, c), f in zip(net.edges(), flows):
        if not 0 <= f <= c:
            problems.append(f"capacidad violada en {u}->{v}: flujo {f}, capacidad {c}")
        balance[v] += f
        balance[u] -= f
    for v in range(net.n):
        if v not in (s, t) and balance[v] != 0:
            problems.append(f"conservación violada en el vértice {v}: {balance[v]}")
    if balance[t] != value or balance[s] != -value:
        problems.append("el valor no coincide con el flujo neto de la fuente y del sumidero")
    return problems
