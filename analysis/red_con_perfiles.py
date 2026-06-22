# -*- coding: utf-8 -*-
# Sociedad Opita - Analisis de Red + Perfiles Psicometricos
# https://sociedad.opitacode.com (proximo)
#
"""
analysis/red_con_perfiles.py
============================
Cruza las metricas de centralidad de red (red_centralidad.py) con los rasgos
psicometricos Big Five (perfiles_psicometricos.py) para responder:

  - ¿Los super-spreaders estructurales tienen rasgos psicologicos especificos?
  - ¿La centralidad correlaciona con Apertura, Amabilidad, Extraversion?
  - ¿Los perifericos (nodos aislados) son mas Neuroticismo bajo o Amabilidad baja?

OBJETIVO
========
Validar dos hipotesis derivadas de la literatura:

H1 (Christakis & Fowler 2009, *Connected*): los nodos centrales tienden a
   tener Amabilidad ALTA (confianza, cooperacion). Prediccion: r(A, degree) > 0.

H2 (Granovetter 1973, *American Journal of Sociology*): los super-spreaders
   (high betweenness) son "weak ties" que conectan grupos. Prediccion: no
   necesariamente los mas Extraversion altos, sino los que ocupan posicion
   estructural entre comunidades.

H3 (Watson 1988): Extraversion correlaciona con Degree (popularidad).
   Prediccion: r(E, degree) > 0.

METODOLOGIA
===========
1. Construir red (red_centralidad.construir_red)
2. Calcular centralidad (betweenness, degree, closeness, pagerank)
3. Para cada nodo adulto con perfil psicometrico:
   - Obtener Big Five scores
   - Obtener Lomnitz default
   - Obtener rasgos derivados cualitativos
4. Calcular correlacion Pearson entre cada metrica de centralidad y cada
   factor Big Five (solo nodos con perfil, n=24-26)
5. Mann-Whitney U: comparar super-spreaders (top 10%) vs resto
6. Visualizar red coloreada por factor dominante (max Big Five)

USO
===
>>> from analysis.red_con_perfiles import analizar
>>> resultados = analizar()

>>> python analysis/red_con_perfiles.py  # reporte completo en terminal
"""

import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

# perfiles_psicometricos es opcional. Si no esta disponible (ej. CI minima),
# pp.PERFILES_ADULTOS queda como {} y unir_red_con_perfiles() retorna [].
try:
    import perfiles_psicometricos as pp
    _HAVE_PERFILES = True
except ImportError:
    pp = None
    _HAVE_PERFILES = False
from geo_tello import AGENTES_GEO
from analysis.red_centralidad import (
    construir_red, calcular_centralidad, top_super_spreaders
)


FACTORES = ("O", "C", "E", "A", "N")
NOMBRES = {
    "O": "Apertura",
    "C": "Concienzudismo",
    "E": "Extraversion",
    "A": "Amabilidad",
    "N": "Neuroticismo",
}
NOMBRES_CORTOS = {
    "O": "Apertura",
    "C": "Concienz.",
    "E": "Extraver.",
    "A": "Amabil.",
    "N": "Neurotic.",
}


# ============================================================================
# 1. UNION RED + PERFILES
# ============================================================================

def unir_red_con_perfiles(G, metricas):
    """Para cada nodo adulto con perfil, agrega los rasgos Big Five + Lomnitz."""
    nodos_unidos = []
    # Snapshot en tiempo de llamada: respeta monkeypatch de pp.PERFILES_ADULTOS
    perfiles = pp.PERFILES_ADULTOS if pp is not None else {}
    for nodo in G.nodes():
        # Solo adultos con perfil psicometrico
        if G.nodes[nodo].get("tipo") != "adulto":
            continue
        if nodo not in perfiles:
            continue
        perfil = perfiles[nodo]
        centralidad = metricas.get(nodo, {})
        nodos_unidos.append({
            "slug": nodo,
            "big_five": perfil["big_five"].copy(),
            "lomnitz": perfil["lomnitz_default"],
            "rasgos": perfil["rasgos"].copy(),
            "betweenness": centralidad.get("betweenness", 0),
            "degree": centralidad.get("degree", 0),
            "closeness": centralidad.get("closeness", 0),
            "pagerank": centralidad.get("pagerank", 0),
        })
    return nodos_unidos


# ============================================================================
# 2. CORRELACIONES PEARSON
# ============================================================================

def pearson(x, y):
    """Coeficiente de Pearson entre dos listas."""
    if len(x) < 3 or len(x) != len(y):
        return float("nan")
    x_arr = np.array(x, dtype=float)
    y_arr = np.array(y, dtype=float)
    if np.std(x_arr) == 0 or np.std(y_arr) == 0:
        return 0.0
    return float(np.corrcoef(x_arr, y_arr)[0, 1])


def correlaciones_red_perfil(nodos_unidos):
    """Calcula matriz de correlacion Pearson: metricas de red x Big Five."""
    metricas_red = ("betweenness", "degree", "closeness", "pagerank")

    # Construir vectores alineados
    vectores = {m: [n[m] for n in nodos_unidos] for m in metricas_red}
    vectores.update({f: [n["big_five"][f] for n in nodos_unidos] for f in FACTORES})

    # Matriz n_metricas_red x n_factores
    matriz = {}
    for mr in metricas_red:
        matriz[mr] = {}
        for f in FACTORES:
            matriz[mr][f] = pearson(vectores[mr], vectores[f])

    return matriz


# ============================================================================
# 3. MANN-WHITNEY: SUPER-SPREADERS VS RESTO
# ============================================================================

def mann_whitney_u(x, y):
    """Mann-Whitney U con aproximacion normal (sin scipy)."""
    nx, ny = len(x), len(y)
    if nx == 0 or ny == 0:
        return float("nan"), float("nan")
    combined = [(v, "x") for v in x] + [(v, "y") for v in y]
    combined.sort(key=lambda t: t[0])
    ranks = {}
    for i, (v, src) in enumerate(combined, start=1):
        ranks.setdefault(v, []).append(i)
    avg_ranks = {}
    for v, rs in ranks.items():
        avg_ranks[v] = sum(rs) / len(rs)
    rx = sum(avg_ranks[v] for v in x)
    u_x = rx - nx * (nx + 1) / 2
    u_y = nx * ny - u_x
    u = min(u_x, u_y)
    mu_u = nx * ny / 2
    sigma_u = (nx * ny * (nx + ny + 1) / 12) ** 0.5
    if sigma_u == 0:
        return u, 1.0
    z = (u - mu_u) / sigma_u
    from math import erf, sqrt
    phi = 0.5 * (1 + erf(abs(z) / sqrt(2)))
    p = 2 * (1 - phi)
    return u, p


def comparar_super_spreaders(nodos_unidos, top_pct=0.20):
    """Mann-Whitney: top 20% super-spreaders (by betweenness) vs resto.

    H1 (Christakis-Fowler): top 20% tienen A mas alto.
    H3 (Watson): top 20% tienen E mas alto.
    """
    # Ordenar por betweenness
    ordenados = sorted(nodos_unidos, key=lambda n: -n["betweenness"])
    n_top = max(3, int(len(ordenados) * top_pct))
    top = ordenados[:n_top]
    resto = ordenados[n_top:]

    resultados = {}
    for factor in FACTORES:
        scores_top = [n["big_five"][factor] for n in top]
        scores_resto = [n["big_five"][factor] for n in resto]
        u, p = mann_whitney_u(scores_top, scores_resto)
        media_top = np.mean(scores_top)
        media_resto = np.mean(scores_resto)
        resultados[factor] = {
            "media_top": float(media_top),
            "media_resto": float(media_resto),
            "diff": float(media_top - media_resto),
            "u": float(u),
            "p": float(p),
            "n_top": n_top,
            "n_resto": len(resto),
        }
    return resultados, [n["slug"] for n in top]


# ============================================================================
# 4. PERFIL DEL SUPER-SPREADER TIPICO
# ============================================================================

def perfil_tipico_super_spreader(nodos_unidos):
    """Identifica el perfil Big Five del super-spreader promedio."""
    # Medias del top 20% por betweenness
    ordenados = sorted(nodos_unidos, key=lambda n: -n["betweenness"])
    n_top = max(3, int(len(ordenados) * 0.20))
    top = ordenados[:n_top]

    perfil_agregado = {}
    for f in FACTORES:
        scores = [n["big_five"][f] for n in top]
        perfil_agregado[f] = float(np.mean(scores))

    return perfil_agregado, [n["slug"] for n in top]


# ============================================================================
# 5. VISUALIZACION: RED COLOREADA POR FACTOR DOMINANTE
# ============================================================================

def visualizar_red_por_factor(G, nodos_unidos, ruta_png):
    """Genera 5 PNGs: uno por factor Big Five, color del nodo = score.

    Rojo = score alto, Azul = score bajo.
    """
    # Score dict por nodo y factor
    scores_por_factor = {f: {} for f in FACTORES}
    for n in nodos_unidos:
        for f in FACTORES:
            scores_por_factor[f][n["slug"]] = n["big_five"][f]

    pos = nx.get_node_attributes(G, "pos")

    # Tamano por betweenness (mismo en los 5 plots)
    sizes = []
    for nodo in G.nodes():
        betw = 0
        for n in nodos_unidos:
            if n["slug"] == nodo:
                betw = n["betweenness"]
                break
        sizes.append(80 + betw * 5000)

    fig, axes = plt.subplots(2, 3, figsize=(24, 16))
    axes = axes.flatten()

    # Top 5 super-spreaders
    ranking = top_super_spreaders(
        {n["slug"]: {k: n[k] for k in ("betweenness", "degree", "closeness", "pagerank")}
         for n in nodos_unidos}, top_n=5)
    top_names = set(n for n, _ in ranking)

    for i, factor in enumerate(FACTORES):
        ax = axes[i]
        # Color por score
        node_colors = []
        for nodo in G.nodes():
            score = scores_por_factor[factor].get(nodo, None)
            if score is None:
                # Nino o adulto sin perfil: gris
                node_colors.append("#cccccc")
            else:
                # RdYlBu invertido: rojo = alto, azul = bajo
                # Normalizar a 0-1
                t = score / 100.0
                # RdYlBu_r de matplotlib (reversed)
                node_colors.append(plt.cm.RdYlBu_r(t))

        # Aristas tenues
        nx.draw_networkx_edges(G, pos, alpha=0.15, width=0.5, ax=ax)

        # Nodos
        nx.draw_networkx_nodes(
            G, pos, node_color=node_colors, node_size=sizes,
            edgecolors=["black" if n in top_names else "#666666"
                       for n in G.nodes()],
            linewidths=[1.5 if n in top_names else 0.3 for n in G.nodes()],
            ax=ax,
        )

        # Labels para top super-spreaders
        labels = {n: n.replace("_", " ").title()[:12] for n in top_names}
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=7,
                                 font_weight="bold", ax=ax)

        ax.set_title(f"{NOMBRES[factor]} (Big Five)\n"
                     f"Rojo = alto, Azul = bajo | Borde grueso = top-5 super-spreader",
                     fontsize=11, fontweight="bold")
        ax.axis("off")

    # Sexto eje: grado (control)
    ax = axes[5]
    nx.draw_networkx_edges(G, pos, alpha=0.15, width=0.5, ax=ax)
    deg_color = []
    for nodo in G.nodes():
        d = G.degree(nodo)
        deg_color.append(plt.cm.viridis(min(d / 10, 1.0)))
    nx.draw_networkx_nodes(G, pos, node_color=deg_color, node_size=sizes,
                            edgecolors="black", linewidths=0.3, ax=ax)
    labels = {n: n.replace("_", " ").title()[:12] for n in top_names}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=7,
                             font_weight="bold", ax=ax)
    ax.set_title("Grado (numero de conexiones directas)\nControl de referencia",
                 fontsize=11, fontweight="bold")
    ax.axis("off")

    plt.suptitle("TELLO, HUILA — Red social coloreada por rasgos Big Five\n"
                 "Tamano del nodo = betweenness centrality",
                 fontsize=14, fontweight="bold", y=0.99)
    plt.tight_layout()
    plt.savefig(ruta_png, dpi=110, bbox_inches="tight", facecolor="white")
    plt.close()


# ============================================================================
# 6. REPORTE COMPLETO
# ============================================================================

def imprimir_reporte(nodos_unidos, matriz_corr, resultados_ss, top_slugs,
                      perfil_tipico):
    print()
    print("#" * 70)
    print("#" + " RED SOCIAL + PERFILES PSICOMETRICOS ".center(68) + "#")
    print("#" * 70)

    print()
    print("=" * 70)
    print(f"1. UNION RED + PERFILES ({len(nodos_unidos)} nodos adultos con perfil)")
    print("=" * 70)
    print(f"  Total adultos en red: {len([n for n in nodos_unidos if True])}")
    print()

    print("=" * 70)
    print("2. CORRELACION PEARSON: METRICAS DE RED x BIG FIVE")
    print("=" * 70)
    print(f"  H1 (Christakis-Fowler 2009): r(A, degree) > 0 esperado")
    print(f"  H3 (Watson 1988): r(E, degree) > 0 esperado")
    print()
    print(f"{'Metrica':<14}", end="")
    for f in FACTORES:
        print(f"{NOMBRES_CORTOS[f]:>12}", end="")
    print()
    print("-" * 70)
    for mr in ("betweenness", "degree", "closeness", "pagerank"):
        print(f"{mr:<14}", end="")
        for f in FACTORES:
            r = matriz_corr[mr][f]
            sig = "*" if abs(r) > 0.3 else " "
            print(f"{r:>+11.3f}{sig:1}", end=" ")
        print()
    print()
    print("  * = |r| > 0.30 (sugiere asociacion moderada)")
    print()

    print("=" * 70)
    print(f"3. SUPER-SPREADERS (top {resultados_ss['O']['n_top']} por betweenness) vs RESTO")
    print("=" * 70)
    print(f"  Top super-spreaders: {top_slugs}")
    print()
    print(f"{'Factor':<14}{'Media Top':>11}{'Media Resto':>13}{'Diff':>9}{'p (U)':>10}{'Sig':>5}")
    print("-" * 60)
    for factor in FACTORES:
        r = resultados_ss[factor]
        sig = "*" if r["p"] < 0.05 else ""
        print(f"{NOMBRES[factor]:<14}{r['media_top']:>11.1f}{r['media_resto']:>13.1f}"
              f"{r['diff']:>+9.1f}{r['p']:>10.3f}{sig:>5}")
    print()
    print("  * = p < 0.05 (Mann-Whitney U, aproximacion normal)")
    print()

    print("=" * 70)
    print("4. PERFIL TIPICO DEL SUPER-SPREADER (media del top 20%)")
    print("=" * 70)
    print(f"  Top 20% ({len(top_slugs)} nodos): {top_slugs}")
    print()
    for f in FACTORES:
        score = perfil_tipico[f]
        # Comparar contra media global
        media_global = np.mean([n["big_five"][f] for n in nodos_unidos])
        diff = score - media_global
        # Cualitativo
        if score >= 70:
            nivel = "ALTO"
        elif score <= 35:
            nivel = "BAJO"
        else:
            nivel = "medio"
        marca = " <-- MAS ALTO" if diff > 5 else (" <-- MAS BAJO" if diff < -5 else "")
        print(f"    {NOMBRES[f]:<14}: {score:>5.1f}  ({nivel}){marca}")
    print()

    # Hallazgos automaticos
    print("=" * 70)
    print("5. HALLAZGOS CLAVE")
    print("=" * 70)
    print()

    # H1
    r_a_degree = matriz_corr["degree"]["A"]
    h1_ok = r_a_degree > 0
    print(f"  H1 (Christakis-Fowler): super-spreaders tienen A mas alto")
    print(f"      r(A, degree) = {r_a_degree:+.3f} -> "
          f"{'CONFIRMADO' if h1_ok else 'NO CONFIRMADO'}")
    print()

    # H3
    r_e_degree = matriz_corr["degree"]["E"]
    h3_ok = r_e_degree > 0
    print(f"  H3 (Watson 1988): super-spreaders tienen E mas alto")
    print(f"      r(E, degree) = {r_e_degree:+.3f} -> "
          f"{'CONFIRMADO' if h3_ok else 'NO CONFIRMADO'}")
    print()

    # Correlacion mas fuerte
    mejor = max(
        ((mr, f, matriz_corr[mr][f]) for mr in matriz_corr for f in FACTORES),
        key=lambda x: abs(x[2])
    )
    print(f"  Correlacion mas fuerte: {mejor[0]} x {mejor[1]} = {mejor[2]:+.3f}")
    print()

    # Top in-Amabilidad
    amab_sorted = sorted(nodos_unidos, key=lambda n: -n["big_five"]["A"])
    print(f"  Top 5 Amabilidad (los mas pro-sociales):")
    for n in amab_sorted[:5]:
        print(f"      {n['slug']:35s} A={n['big_five']['A']}, "
              f"betweenness={n['betweenness']:.3f}")
    print()

    # Top betweenness
    betw_sorted = sorted(nodos_unidos, key=lambda n: -n["betweenness"])
    print(f"  Top 5 Betweenness (super-spreaders estructurales):")
    for n in betw_sorted[:5]:
        print(f"      {n['slug']:35s} betweenness={n['betweenness']:.3f}, "
              f"A={n['big_five']['A']}, E={n['big_five']['E']}")
    print()

    print("#" * 70)
    print("#" + " FIN DEL REPORTE ".center(68) + "#")
    print("#" * 70)
    print()


# ============================================================================
# MAIN
# ============================================================================

def analizar():
    """Funcion principal: ejecuta todo el analisis."""
    print("Construyendo red social...")
    G = construir_red()
    print(f"  Nodos: {G.number_of_nodes()}, Aristas: {G.number_of_edges()}")

    print("Calculando centralidad...")
    metricas = calcular_centralidad(G)

    print("Uniendolo con perfiles psicometricos...")
    nodos_unidos = unir_red_con_perfiles(G, metricas)
    print(f"  {len(nodos_unidos)} adultos con perfil + centralidad")

    print("Calculando correlaciones Pearson red x Big Five...")
    matriz_corr = correlaciones_red_perfil(nodos_unidos)

    print("Mann-Whitney: super-spreaders vs resto...")
    resultados_ss, top_slugs = comparar_super_spreaders(nodos_unidos, top_pct=0.20)

    print("Calculando perfil tipico del super-spreader...")
    perfil_tipico, _ = perfil_tipico_super_spreader(nodos_unidos)

    return {
        "nodos_unidos": nodos_unidos,
        "matriz_corr": matriz_corr,
        "resultados_ss": resultados_ss,
        "top_slugs": top_slugs,
        "perfil_tipico": perfil_tipico,
    }


def main():
    resultados = analizar()
    imprimir_reporte(
        resultados["nodos_unidos"],
        resultados["matriz_corr"],
        resultados["resultados_ss"],
        resultados["top_slugs"],
        resultados["perfil_tipico"],
    )

    # Generar visualizacion
    print("Generando visualizacion PNG...")
    G = construir_red()
    metricas = calcular_centralidad(G)
    nodos_unidos = unir_red_con_perfiles(G, metricas)
    ruta_png = Path("demo_output/red_con_perfiles.png")
    ruta_png.parent.mkdir(parents=True, exist_ok=True)
    visualizar_red_por_factor(G, nodos_unidos, str(ruta_png))
    print(f"[PNG] {ruta_png}")


if __name__ == "__main__":
    main()