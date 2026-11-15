"""Caso de uso sintético: reparto diario de pacientes entre odontólogos (datos inventados).

Uso: python experiments/caso_clinica.py [--seed 2026] [--dentists 5]
Imprime el flujo máximo (pacientes atendidos), la demanda no atendida y el corte mínimo
con nombres, y guarda lo mismo en experiments/results/caso_clinica.txt.
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from generators import clinic_network, derived_rng  # noqa: E402
from maxflow import max_flow_min_cut, verify_flow  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--seed", type=int, default=2026)
ap.add_argument("--dentists", type=int, default=5)
args = ap.parse_args()

net, s, t, names, demand = clinic_network(args.dentists, derived_rng(args.seed, 1))
res, cut = max_flow_min_cut(net, s, t, "edmonds_karp")
assert verify_flow(net, s, t, res.flows, res.value) == []
lines = [f"Demanda total del día: {demand} pacientes",
         f"Flujo máximo (pacientes atendidos): {res.value}",
         f"Demanda sin atender: {demand - res.value}",
         f"Caminos de aumento: {res.augmentations}",
         f"Capacidad del corte mínimo: {cut.capacity} (igual al flujo máximo)",
         "Aristas del corte mínimo (cuellos de botella):"]
lines += [f"  {names[u]} -> {names[v]}  capacidad {c}" for u, v, c in sorted(cut.edges)]
text = "\n".join(lines)
print(text)
(ROOT / "experiments" / "results" / "caso_clinica.txt").write_text(text + "\n", encoding="utf-8")
