# Bitácora 2: flujo máximo y corte mínimo (Equipo 4)

Maestría en Tecnologías de la Información, Cohorte X, 2026-III. Análisis y Diseño de Algoritmos, Profa. Msc. Sosa. Proyecto, Parte 1, línea 4 (Flujo y corte).

Integrantes: Dulce Pérez, Ramón Maita, Ingrid Martínez y Rafael Berroterán.

Este repositorio contiene la implementación de Ford-Fulkerson (búsqueda en profundidad) y Edmonds-Karp (búsqueda en anchura) con extracción del corte mínimo, sus pruebas, la medición piloto y la gráfica del informe `Equipo_4_Bitacora2.pdf`. Los datos del caso de uso (una clínica odontológica) son sintéticos y no contienen información real ni personal.

## Requisitos y versiones

| Componente | Versión usada en la corrida original |
|---|---|
| Python (CPython) | 3.13.18 |
| networkx | 3.7 |
| hypothesis | 6.170.14 |
| matplotlib | 3.11.2 |
| numpy | 2.5.3 |
| Sistema | Linux 6.18.44 x86_64, Intel Xeon 2,30 GHz, 2 núcleos lógicos, 7,8 GB de RAM |

Los algoritmos (`src/`) usan solo la biblioteca estándar. NetworkX se usa en la prueba diferencial y para validar cada red del experimento, Hypothesis en las pruebas por propiedades, y matplotlib y numpy solo en las gráficas.

## Comandos exactos

Desde la carpeta raíz del proyecto:

```bash
python -m venv .venv
source .venv/bin/activate          # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python experiments/pilot.py --seed 2026
python experiments/plots.py
python experiments/caso_clinica.py
```

* `python -m unittest discover -s tests -v` ejecuta 16 pruebas (12 unitarias, 2 por propiedades con Hypothesis y 2 diferenciales contra NetworkX); deben pasar todas y tardan cerca de 1 segundo.
* `python experiments/pilot.py --seed 2026` tarda cerca de 75 segundos en el equipo original (casi todo es Ford-Fulkerson con capacidades de hasta 10 000) y escribe `experiments/results/raw_measurements.csv`, `summary.csv` y `environment.json`. Se detiene con un error si algún flujo difiere del de NetworkX.
* `python experiments/plots.py` lee `summary.csv` y escribe `experiments/figures/fig1_piloto.png` y `experiments/results/derived.json` (las cifras derivadas que cita el informe).
* `python experiments/caso_clinica.py` imprime el reparto de pacientes de la clínica sintética y su corte mínimo, y lo guarda en `experiments/results/caso_clinica.txt`.

## Semillas

* Experimento y caso de uso: semilla 2026. Cada red usa `derived_rng(semilla, ...)`, que depende solo de sus parámetros (tamaño, capacidad máxima y repetición) y no del orden de ejecución.
* Prueba diferencial: semilla 2026 con `derived_rng`.
* Hypothesis: `derandomize=True`, con 300 ejemplos por propiedad.

## Qué debería reproducir otra máquina

Con la misma versión de Python, las redes, los valores de flujo, el número de caminos de aumento y las aristas examinadas son idénticos. Los tiempos en segundos cambian con la máquina; lo que debe mantenerse es la forma de los resultados: Ford-Fulkerson hace casi un aumento por unidad de flujo y Edmonds-Karp unas pocas decenas, y por eso la diferencia de tiempo crece con la capacidad máxima de las aristas (experimento B).

## Estructura

```
src/maxflow.py            FlowNetwork, ford_fulkerson, edmonds_karp, min_cut, verify_flow
src/generators.py         redes aleatorias y red de la clínica (semilla explícita)
tests/                    pruebas unitarias, por propiedades y diferenciales
experiments/pilot.py      medición piloto (experimentos A y B, 5 repeticiones, mediana)
experiments/plots.py      figura y cifras derivadas
experiments/caso_clinica.py   caso de uso sintético
experiments/results/      datos crudos, resumen, entorno, cifras derivadas y caso de uso
experiments/figures/      gráfica del informe
```

Correspondencia con el informe: la Tabla 1 sale de `summary.csv` (experimento A) y la Figura 1 es `fig1_piloto.png`.
