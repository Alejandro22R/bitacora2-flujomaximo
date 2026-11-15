"""Generadores de redes sintéticas reproducibles (semilla explícita)."""

from __future__ import annotations

import random

from maxflow import FlowNetwork


def derived_rng(seed: int, *keys: int) -> random.Random:
    """Generador independiente del orden de ejecución: depende solo de (seed, keys)."""
    x = seed
    for k in keys:
        x = x * 1_000_003 + k
    return random.Random(x)


def random_network(n: int, avg_degree: int, max_cap: int, rng: random.Random):
    """Red aleatoria con n vértices, ~avg_degree*n aristas y capacidades en 1..max_cap.

    La fuente es 0 y el sumidero n-1. Se evitan lazos; puede haber aristas paralelas
    o antiparalelas, que el algoritmo trata como aristas distintas.
    """
    net = FlowNetwork(n)
    for _ in range(avg_degree * n):
        u = rng.randrange(n)
        v = rng.randrange(n)
        if u != v:
            net.add_edge(u, v, rng.randint(1, max_cap))
    return net, 0, n - 1


TREATMENTS = ["limpieza", "obturación", "endodoncia", "extracción",
              "ortodoncia", "prótesis", "periodoncia", "radiografía"]


def clinic_network(n_dentists: int, rng: random.Random, p_qualified: float = 0.4):
    """Caso de uso sintético: reparto diario de pacientes entre odontólogos.

    Vértices: 0 = fuente; 1..G = tipos de tratamiento (demanda del día);
    G+1..G+D = odontólogos (capacidad diaria); G+D+1 = sumidero.
    Una arista tratamiento -> odontólogo existe si el odontólogo puede realizarlo
    (cada tratamiento tiene al menos un odontólogo habilitado).
    Devuelve (red, fuente, sumidero, nombres, demanda_total).
    """
    g = len(TREATMENTS)
    net = FlowNetwork(g + n_dentists + 2)
    s, t = 0, g + n_dentists + 1
    names = {s: "fuente", t: "sumidero"}
    demand = [rng.randint(4, 14) for _ in range(g)]
    for i, tr in enumerate(TREATMENTS, start=1):
        names[i] = f"demanda: {tr}"
        net.add_edge(s, i, demand[i - 1])
    for j in range(n_dentists):
        d = g + 1 + j
        names[d] = f"odontólogo {j + 1}"
        net.add_edge(d, t, rng.randint(6, 12))
    for i in range(1, g + 1):
        qualified = [j for j in range(n_dentists) if rng.random() < p_qualified]
        if not qualified:
            qualified = [rng.randrange(n_dentists)]
        for j in qualified:
            net.add_edge(i, g + 1 + j, demand[i - 1])
    return net, s, t, names, sum(demand)
