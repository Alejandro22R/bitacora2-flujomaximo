"""Gráficas y cifras derivadas a partir de experiments/results/summary.csv.

Uso:  python experiments/plots.py
Salidas: experiments/figures/fig1_piloto.png y experiments/results/derived.json
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RES, FIG = ROOT / "experiments" / "results", ROOT / "experiments" / "figures"
FIG.mkdir(exist_ok=True)

AZUL, NARANJA = "#2a78d6", "#eb6834"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#dcdad4"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "axes.titlecolor": INK, "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "axes.axisbelow": True, "legend.frameon": False, "figure.dpi": 100,
})

rows = list(csv.DictReader((RES / "summary.csv").open(encoding="utf-8")))


def series(exp, algo):
    pts = sorted((r for r in rows if r["experimento"] == exp and r["algoritmo"] == algo),
                 key=lambda r: (int(r["n"]), int(r["max_cap"])))
    return pts


def arr(pts, key):
    return np.array([float(p[key]) for p in pts])


FF_A, EK_A = series("A_tamano", "ford_fulkerson"), series("A_tamano", "edmonds_karp")
FF_B, EK_B = series("B_capacidad", "ford_fulkerson"), series("B_capacidad", "edmonds_karp")
n = arr(FF_A, "n")

fig, ax = plt.subplots(1, 2, figsize=(9.6, 3.5))

# (a) tiempo frente a n, escala log-log, con la banda mínimo-máximo de las 5 redes
for pts, color, label in ((FF_A, NARANJA, "Ford-Fulkerson (DFS)"), (EK_A, AZUL, "Edmonds-Karp (BFS)")):
    t = arr(pts, "segundos_mediana")
    ax[0].fill_between(n, arr(pts, "segundos_min"), arr(pts, "segundos_max"), color=color, alpha=0.15, linewidth=0)
    ax[0].plot(n, t, "o-", color=color, lw=1.8, ms=4)
    ax[0].annotate(label.replace(" (", "\n("), (n[-1], t[-1]), xytext=(8, 0), textcoords="offset points",
                   ha="left", va="center", color=color, fontsize=8.5)
ax[0].set_xscale("log"); ax[0].set_yscale("log"); ax[0].set_xlim(80, 9000)
ax[0].set_xlabel("Vértices n (m = 5n aristas, capacidades 1 a 100)")
ax[0].set_ylabel("Tiempo (s), mediana y rango")
ax[0].set_xticks(n); ax[0].set_xticklabels([f"{int(v):,}".replace(",", " ") for v in n], fontsize=8)
ax[0].set_title("A. El tiempo crece con el tamaño de la red", loc="left", fontsize=10)

# (b) caminos de aumento frente a la capacidad máxima, n = 800
caps = arr(FF_B, "max_cap")
for pts, color, label in ((FF_B, NARANJA, "Ford-Fulkerson"), (EK_B, AZUL, "Edmonds-Karp")):
    a = arr(pts, "aumentos_mediana")
    ax[1].plot(caps, a, "o-", color=color, lw=1.8, ms=4)
    ax[1].annotate(f"{label}\n{int(a[-1]):,}".replace(",", " "), (caps[-1], a[-1]),
                   xytext=(8, 0), textcoords="offset points", ha="left", va="center",
                   color=color, fontsize=8.5)
ax[1].set_xscale("log"); ax[1].set_yscale("log"); ax[1].set_xlim(0.7, 90000)
ax[1].set_xlabel("Capacidad máxima de las aristas (n = 800)")
ax[1].set_ylabel("Caminos de aumento, mediana")
ax[1].set_xticks(caps); ax[1].set_xticklabels([f"{int(c):,}".replace(",", " ") for c in caps])
ax[1].set_title("B. Solo Ford-Fulkerson depende del flujo f", loc="left", fontsize=10)
fig.tight_layout()
fig.savefig(FIG / "fig1_piloto.png", dpi=200)

# ------------------------------------------------------------ cifras derivadas
def slope(x, y):
    return float(np.polyfit(np.log(x), np.log(y), 1)[0])


derived = {
    "pendiente_tiempo_FF": slope(n, arr(FF_A, "segundos_mediana")),
    "pendiente_tiempo_EK": slope(n, arr(EK_A, "segundos_mediana")),
    "pendiente_aristas_FF": slope(n, arr(FF_A, "aristas_mediana")),
    "pendiente_aristas_EK": slope(n, arr(EK_A, "aristas_mediana")),
    "razon_tiempo_FF_sobre_EK_A": [float(a / b) for a, b in zip(arr(FF_A, "segundos_mediana"), arr(EK_A, "segundos_mediana"))],
    "razon_aristas_FF_sobre_EK_A": [float(a / b) for a, b in zip(arr(FF_A, "aristas_mediana"), arr(EK_A, "aristas_mediana"))],
    "B_aumentos_FF": arr(FF_B, "aumentos_mediana").tolist(), "B_aumentos_EK": arr(EK_B, "aumentos_mediana").tolist(),
    "B_flujo": arr(FF_B, "flujo_mediana").tolist(),
    "B_tiempo_FF": arr(FF_B, "segundos_mediana").tolist(), "B_tiempo_EK": arr(EK_B, "segundos_mediana").tolist(),
    "B_razon_tiempo_cap10000": float(arr(FF_B, "segundos_mediana")[-1] / arr(EK_B, "segundos_mediana")[-1]),
    "B_razon_aristas_cap10000": float(arr(FF_B, "aristas_mediana")[-1] / arr(EK_B, "aristas_mediana")[-1]),
    "cota_VE_sobre_2_n100": float(100 * 496 / 2),
}
raw = list(csv.DictReader((RES / "raw_measurements.csv").open(encoding="utf-8")))
ff = [r for r in raw if r["algoritmo"] == "ford_fulkerson" and r["experimento"] == "A_tamano"]
derived["A_FF_aumentos_sobre_flujo_min_max"] = [min(int(r["aumentos"]) / int(r["flujo"]) for r in ff if int(r["flujo"])),
                                               max(int(r["aumentos"]) / int(r["flujo"]) for r in ff if int(r["flujo"]))]
ek = [r for r in raw if r["algoritmo"] == "edmonds_karp"]
derived["EK_aumentos_min_max_todas"] = [min(int(r["aumentos"]) for r in ek), max(int(r["aumentos"]) for r in ek)]
(RES / "derived.json").write_text(json.dumps(derived, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(derived, indent=1, ensure_ascii=False))
