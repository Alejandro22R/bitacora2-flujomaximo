from __future__ import annotations

import argparse
import csv
import gc
import json
import os
import platform
import statistics
import sys
import time
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import networkx as nx

from _common import to_networkx
from generators import derived_rng, random_network 
from maxflow import edmonds_karp, ford_fulkerson

RESULTS = ROOT / "experiments" / "results"
REPS = 5
AVG_DEGREE = 5
SIZES_A = [100, 200, 400, 800, 1600, 3200]
CAP_A = 100
N_B = 800
CAPS_B = [1, 100, 10_000]
ALGOS = {"ford_fulkerson": ford_fulkerson, "edmonds_karp": edmonds_karp}


def timed(fn, net, s, t):
    gc.collect()
    gc.disable()
    try:
        t0 = time.perf_counter_ns()
        res = fn(net, s, t)
        t1 = time.perf_counter_ns()
    finally:
        gc.enable()
    return (t1 - t0) / 1e9, res


def run(seed: int):
    plan = [("A_tamano", n, CAP_A) for n in SIZES_A] + [("B_capacidad", N_B, c) for c in CAPS_B]
    rows = []
    for exp, n, max_cap in plan:
        for rep in range(REPS):
            net, s, t = random_network(n, AVG_DEGREE, max_cap, derived_rng(seed, n, max_cap, rep))
            expected = nx.maximum_flow_value(to_networkx(net), s, t)
            for name, algo in ALGOS.items():
                algo(net, s, t)
                secs, res = timed(algo, net, s, t)
                if res.value != expected:
                    raise AssertionError(f"{name} n={n} rep={rep}: {res.value} != {expected}")
                rows.append(dict(experimento=exp, algoritmo=name, n=n, m=len(net.to) // 2,
                                 max_cap=max_cap, rep=rep, flujo=res.value,
                                 aumentos=res.augmentations, aristas_examinadas=res.scans,
                                 segundos=secs))
            print(f"{exp} n={n} cap={max_cap} rep={rep} f={expected}", flush=True)
    return rows


def summarize(rows):
    keys = sorted({(r["experimento"], r["algoritmo"], r["n"], r["max_cap"]) for r in rows},
                  key=lambda k: (k[0], k[1], k[2], k[3]))
    out = []
    for exp, algo, n, cap in keys:
        grp = [r for r in rows if (r["experimento"], r["algoritmo"], r["n"], r["max_cap"]) == (exp, algo, n, cap)]
        med = lambda f: statistics.median(r[f] for r in grp)
        times = [r["segundos"] for r in grp]
        out.append(dict(experimento=exp, algoritmo=algo, n=n, m=grp[0]["m"], max_cap=cap,
                        reps=len(grp), flujo_mediana=med("flujo"), aumentos_mediana=med("aumentos"),
                        aristas_mediana=med("aristas_examinadas"),
                        segundos_mediana=statistics.median(times),
                        segundos_min=min(times), segundos_max=max(times)))
    return out


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def environment(seed: int) -> dict:
    def cpu():
        try:
            for line in Path("/proc/cpuinfo").read_text().splitlines():
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
        except OSError:
            pass
        return platform.processor() or "desconocido"

    def ram_gb():
        try:
            for line in Path("/proc/meminfo").read_text().splitlines():
                if line.startswith("MemTotal"):
                    return round(int(line.split()[1]) / 1024 / 1024, 1)
        except OSError:
            pass
        return None

    return dict(python=sys.version.split()[0], implementacion=platform.python_implementation(),
                sistema=platform.platform(), cpu=cpu(), nucleos_logicos=os.cpu_count(), ram_gb=ram_gb(),
                networkx=metadata.version("networkx"), semilla=seed, repeticiones=REPS,
                grado_medio=AVG_DEGREE, fecha=time.strftime("%Y-%m-%d"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    raw = run(args.seed)
    write_csv(RESULTS / "raw_measurements.csv", raw)
    write_csv(RESULTS / "summary.csv", summarize(raw))
    (RESULTS / "environment.json").write_text(json.dumps(environment(args.seed), indent=2, ensure_ascii=False), encoding="utf-8")
    print("listo: resultados en", RESULTS)
