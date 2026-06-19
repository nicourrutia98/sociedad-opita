# -*- coding: utf-8 -*-
# Sociedad Opita - Analisis de Red Social
# https://sociedad.opitacode.com (proximo)
#
"""
analysis/red_centralidad.py
============================
Calculo de centralidad de la red social de Tello.

OBJETIVO
========
Identificar los actores estructuralmente mas importantes de la red social
(super-spreaders teoricos) usando metricas de centralidad de grafos.

METODOLOGIA
===========
Tres metricas complementarias:

1. **Betweenness centrality** (Freeman 1977):
   Cuantas veces un nodo aparece en el camino mas corto entre otros dos.
   Mide: capacidad de mediar informacion entre grupos.
   Interpretation: super-spreaders de gossip entre comunidades.

2. **Degree centrality**:
   Numero de conexiones directas.
   Mide: "popularidad" inmediata.
   Interpretation: nodos conocidos por todos.

3. **Closeness centrality**:
   Distancia promedio a todos los demas nodos.
   Mide: acceso rapido a la red completa.
   Interpretation: nodos que se enteran de todo primero.

USO
===
>>> from analysis.red_centralidad import construir_red, calcular_centralidad
>>> G = construir_red()
>>> df = calcular_centralidad(G)
>>> print(df.sort_values('betweenness', ascending=False).head(10))

>>> python analysis/red_centralidad.py  # genera reporte + visualizacion
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import Counter

from geo_tello import AGENTES_GEO

try:
    from ninos_tello import NINOS
    HAVE_NINOS = True
except ImportError:
    HAVE_NINOS = False


# ===========================================================================
# RED SOCIAL DE TELLO (de biografias + analisis manual)
# ===========================================================================
# Cada arista tiene: tipo (familia/compadres/amistad/etc.) y peso
# (frecuencia de interaccion). Datos validados por nativo huilense.

RELACIONES = [
    # Familias (padre-hijo, abuelo-nieto, hermanos)
    ("don_eliecer_patron", "jhon_eliecer_hijo_patron", "familia", 0.9),
    ("don_eliecer_patron", "maria_camila_perdomo", "familia", 0.7),
    ("dona_prudencia_partera", "juan_esteban_quintero", "familia", 0.85),
    ("dona_rosa_tendera", "edilma_secretaria", "familia", 0.5),  # primas
    ("aurora_maestra", "mateo_losada_pinilla", "familia", 0.9),
    ("dona_mercedes_panadera", "valentina_pinilla", "familia", 0.9),
    ("don_emigdio_jubilado", "samuel_suarez_trujillo", "familia", 0.7),
    ("don_emigdio_jubilado", "yulieth_andrea_suarez", "familia", 0.7),
    ("don_sigifredo_inspector", "laura_valentina_trujillo", "familia", 0.9),
    ("don_rosalio_rival", "michael_steven_quintero", "familia", 0.9),
    ("caliche_minero", "sofia_vargas_trujillo", "familia", 0.85),
    ("caliche_minero", "andres_felipe_vargas", "familia", 0.85),
    ("laura_reina", "camila_andrea_meneses", "familia", 0.7),  # tia-sobrina
    ("sofia_vargas_trujillo", "andres_felipe_vargas", "familia", 0.8),  # hermanos
    ("sofia_vargas_trujillo", "brayan_stiven_vargas", "familia", 0.7),  # primos
    ("andres_felipe_vargas", "brayan_stiven_vargas", "pandilla", 0.85),
    ("brayan_stiven_vargas", "yulieth_andrea_suarez", "novios", 0.7),

    # Compadres (vinculo bautizo/matrimonio, altisima confianza)
    ("don_eliecer_patron", "padre_cecilio_cura", "compadres", 0.95),
    ("don_eliecer_patron", "jhon_jairo_sacristan", "compadres", 0.85),
    ("don_eliecer_patron", "don_sigifredo_inspector", "compadres", 0.9),
    ("don_eliecer_patron", "dona_mercedes_panadera", "compadres", 0.8),
    ("don_eliecer_patron", "don_rosalio_rival", "rivales", 0.6),

    # Amistad / alianza cotidiana (epicentro de chisme)
    ("dona_rosa_tendera", "don_sigifredo_inspector", "amistad", 0.7),
    ("dona_rosa_tendera", "dona_prudencia_partera", "amistad", 0.85),
    ("dona_rosa_tendera", "padre_cecilio_cura", "amistad", 0.7),
    ("dona_rosa_tendera", "dona_mercedes_panadera", "amistad", 0.7),
    ("dona_rosa_tendera", "edilma_secretaria", "amistad", 0.6),
    ("dona_rosa_tendera", "don_eliseo_boticario", "amistad", 0.6),
    ("dona_rosa_tendera", "beatriz_personera", "amistad", 0.5),
    ("dona_rosa_tendera", "patricia_comisaria", "amistad", 0.5),
    ("dona_rosa_tendera", "don_fernando_alcalde", "amistad", 0.4),

    # Trabajo / institucional
    ("padre_cecilio_cura", "jhon_jairo_sacristan", "laboral", 0.95),
    ("capitan_hernan_policia", "don_abelardo_conductor", "laboral", 0.95),
    ("capitan_hernan_policia", "subintendente_saavedra", "laboral", 0.9),
    ("don_fernando_alcalde", "edilma_secretaria", "laboral", 0.95),
    ("don_fernando_alcalde", "valentina_secretaria_joven", "laboral", 0.95),
    ("beatriz_personera", "patricia_comisaria", "laboral", 0.7),
    ("beatriz_personera", "don_fernando_alcalde", "laboral", 0.7),
    ("don_octavio_medico", "don_eliseo_boticario", "laboral", 0.6),

    # Vecindad geografica (co-presencia frecuente)
    ("dona_rosa_tendera", "don_sigifredo_inspector", "vecindad", 0.9),
    ("dona_rosa_tendera", "patricia_comisaria", "vecindad", 0.8),
    ("don_sigifredo_inspector", "patricia_comisaria", "vecindad", 0.7),

    # Ninos: pandilla, amigos, novios
    ("daniela_ramirez_perdomo", "camila_andrea_meneses", "amistad", 0.8),
    ("daniela_ramirez_perdomo", "sofia_vargas_trujillo", "amistad", 0.7),
    ("daniela_ramirez_perdomo", "laura_valentina_trujillo", "amistad", 0.7),
    ("sofia_vargas_trujillo", "valentina_pinilla", "amistad", 0.7),
    ("mateo_losada_pinilla", "samuel_suarez_trujillo", "amistad", 0.6),
    ("michael_steven_quintero", "jhonatan_perdomo", "rivales", 0.7),
    ("michael_steven_quintero", "yulieth_andrea_suarez", "rivales", 0.6),
    ("karol_tatiana_losada", "laura_valentina_trujillo", "amistad", 0.6),
]


def construir_red():
    """Construye el grafo NetworkX con las relaciones de Tello."""
    G = nx.Graph()

    # Agregar nodos adultos
    for slug, ag in AGENTES_GEO.items():
        x, y = ag["casa_coords"]
        G.add_node(slug, pos=(x, y),
                   tipo="adulto",
                   generacion=ag.get("generacion", "adulto"))

    # Agregar nodos niños
    if HAVE_NINOS:
        for slug, n in NINOS.items():
            x, y = n["casa_coords"]
            G.add_node(slug, pos=(x, y),
                       tipo="nino",
                       etapa=n["etapa_piaget"])

    # Agregar aristas (sin duplicados, conservar el peso maximo)
    aristas = {}
    for a, b, tipo, peso in RELACIONES:
        if a in G.nodes and b in G.nodes:
            key = tuple(sorted([a, b]))
            if key not in aristas or peso > aristas[key][1]:
                aristas[key] = (tipo, peso)

    for (a, b), (tipo, peso) in aristas.items():
        G.add_edge(a, b, tipo=tipo, peso=peso)

    return G


def calcular_centralidad(G):
    """Calcula multiple metricas de centralidad para cada nodo."""
    metricas = {}

    # Betweenness centrality (con peso: aristas con peso mayor son mas cortas)
    # Invertir pesos para que pesos altos = aristas mas cortas = mas "facil" pasar
    for u, v, d in G.edges(data=True):
        d["inv_peso"] = 1.0 / max(d["peso"], 0.01)

    betweenness = nx.betweenness_centrality(G, weight="inv_peso", normalized=True)
    degree = nx.degree_centrality(G)
    closeness = nx.closeness_centrality(G, distance="inv_peso")
    pagerank = nx.pagerank(G, weight="peso")

    for nodo in G.nodes():
        metricas[nodo] = {
            "betweenness": betweenness.get(nodo, 0),
            "degree": degree.get(nodo, 0),
            "closeness": closeness.get(nodo, 0),
            "pagerank": pagerank.get(nodo, 0),
        }

    return metricas


def top_super_spreaders(metricas, top_n=10):
    """Identifica los nodos con mayor potencial de difusion."""
    # Score compuesto: betweenness (0.4) + pagerank (0.3) +
    # degree (0.2) + closeness (0.1)
    score = {}
    for nodo, m in metricas.items():
        score[nodo] = (
            0.4 * m["betweenness"]
            + 0.3 * m["pagerank"]
            + 0.2 * m["degree"]
            + 0.1 * m["closeness"]
        )

    ranking = sorted(score.items(), key=lambda x: -x[1])
    return ranking[:top_n]


def generar_reporte(G, metricas):
    """Genera reporte en texto con los hallazgos."""
    print("=" * 70)
    print(" ANALISIS DE CENTRALIDAD - RED SOCIAL DE TELLO")
    print("=" * 70)
    print()
    print(f"Total nodos: {G.number_of_nodes()}")
    print(f"Total aristas: {G.number_of_edges()}")
    print(f"Densidad: {nx.density(G):.3f}")
    print()

    print("-" * 70)
    print("TOP 10 SUPER-SPREADERS ESTRUCTURALES")
    print("-" * 70)
    print()
    print(f"{'#':<4}{'Nodo':<35}{'Score':<10}{'Between':<10}{'PageRank':<10}{'Degree':<10}")
    print("-" * 70)

    ranking = top_super_spreaders(metricas, top_n=10)
    for i, (nodo, score) in enumerate(ranking, 1):
        m = metricas[nodo]
        # Formatear nombre
        alias = nodo.replace("_", " ").title()[:32]
        print(f"{i:<4}{alias:<35}{score:.3f}{'':<6}{m['betweenness']:.3f}{'':<6}"
              f"{m['pagerank']:.3f}{'':<6}{m['degree']:.3f}")

    print()
    print("-" * 70)
    print("HALLAZGOS CLAVE")
    print("-" * 70)
    print()

    # Top 3 super-spreaders
    top_3 = [r[0] for r in ranking[:3]]
    print(f"1. Los 3 nodos mas centrales estructuralmente son:")
    for i, nodo in enumerate(top_3, 1):
        alias = nodo.replace("_", " ").title()
        print(f"   {i}. {alias} (betweenness={metricas[nodo]['betweenness']:.3f})")
    print()

    # Distancia promedio
    if nx.is_connected(G):
        avg_path = nx.average_shortest_path_length(G)
        print(f"2. Distancia promedio en la red: {avg_path:.2f} saltos")
        print(f"   (Interpretacion: cualquier persona esta a ~{avg_path:.0f} intermediarios de otra)")
    print()

    # Nodos aislados o periféricos
    periferia = [n for n in G.nodes() if metricas[n]["betweenness"] < 0.01]
    print(f"3. Nodos perifericos (betweenness < 0.01): {len(periferia)}/{G.number_of_nodes()}")
    for nodo in periferia[:5]:
        alias = nodo.replace("_", " ").title()
        print(f"   - {alias}")

    print()
    print("=" * 70)
    print("INTERPRETACION FORENSE")
    print("=" * 70)
    print()
    print("Los super-spreaders estructurales son nodos que controlan el flujo de")
    print("informacion entre comunidades. Un chisme que pase por ellos llega a")
    print("todos los grupos sociales. Un agente externo que quiera difundir")
    print("informacion deberia apuntar a estos nodos primero.")
    print()
    print("Si un nodo periferico quiere ser oido, debe pasar por un super-spreader")
    print("o crear vinculo directo con multiples nodos (estrategia costosa).")
    print()
    print("Esta es la 'geometria del poder' de Tello: no la personalidad, no la")
    print("riqueza, sino quien esta conectado a quien.")


def visualizar(G, metricas, ruta_png):
    """Visualiza la red con nodos dimensionados por centralidad."""
    fig, ax = plt.subplots(figsize=(18, 14))

    pos = nx.get_node_attributes(G, "pos")
    if not pos:
        # Layout spring si no hay coords
        pos = nx.spring_layout(G, k=1, seed=42)

    # Tamano por betweenness
    sizes = []
    for nodo in G.nodes():
        betw = metricas[nodo]["betweenness"]
        # Escalar: 100 a 1000 puntos
        sizes.append(100 + betw * 5000)

    # Color por generacion/tipo
    colors = []
    color_map = {
        "anciano": "#ff9896",
        "adulto": "#aec7e8",
        "joven": "#98df8a",
    }
    color_ninos_map = {
        "preoperacional": "#ffbb78",
        "operacional_concreto": "#ff7f0e",
        "operacional_concreto_final": "#d62728",
        "operacional_formal_inicial": "#9467bd",
        "operacional_formal": "#8c564b",
    }
    for nodo in G.nodes():
        gen = G.nodes[nodo].get("generacion", "")
        etapa = G.nodes[nodo].get("etapa", "")
        if G.nodes[nodo].get("tipo") == "nino":
            colors.append(color_ninos_map.get(etapa, "#888"))
        else:
            colors.append(color_map.get(gen, "#888"))

    # Aristas por tipo
    tipo_color = {
        "familia": "#d62728",
        "compadres": "#ff7f0e",
        "amistad": "#2ca02c",
        "laboral": "#1f77b4",
        "institucional": "#9467bd",
        "rivales": "#000000",
        "novios": "#e377c2",
        "pandilla": "#8c564b",
        "vecindad": "#17becf",
    }

    for tipo, color in tipo_color.items():
        edges = [(u, v) for u, v, d in G.edges(data=True) if d["tipo"] == tipo]
        if edges:
            style = "dashed" if tipo == "rivales" else "solid"
            nx.draw_networkx_edges(
                G, pos, edgelist=edges, edge_color=color,
                width=1.2, alpha=0.5, style=style, ax=ax,
            )

    # Dibujar nodos (tamano segun betweenness)
    nx.draw_networkx_nodes(
        G, pos, node_color=colors, node_size=sizes,
        edgecolors="black", linewidths=0.8, ax=ax,
    )

    # Labels para top super-spreaders solamente
    ranking = top_super_spreaders(metricas, top_n=10)
    top_names = {n: G.nodes[n].get("generacion", "") for n, _ in ranking}
    labels = {n: n.replace("_", " ").title()[:14] for n, _ in ranking}
    nx.draw_networkx_labels(
        G, pos, labels=labels, font_size=8, font_weight="bold", ax=ax,
    )

    # Leyenda
    legend_elements = [
        plt.Line2D([0], [0], color=c, linewidth=2, label=t)
        for t, c in tipo_color.items()
    ]
    legend_elements += [
        plt.Line2D([0], [0], marker="o", color="w",
                   markerfacecolor=color_map.get("anciano", "#f88"),
                   markersize=10, label="Anciano"),
        plt.Line2D([0], [0], marker="o", color="w",
                   markerfacecolor=color_map.get("adulto", "#aef"),
                   markersize=10, label="Adulto"),
        plt.Line2D([0], [0], marker="o", color="w",
                   markerfacecolor=color_map.get("joven", "#aea"),
                   markersize=10, label="Joven"),
        plt.Line2D([0], [0], marker="o", color="w",
                   markerfacecolor="#888", markersize=10,
                   label="(tamano = betweenness)"),
    ]
    ax.legend(handles=legend_elements, loc="upper left",
              bbox_to_anchor=(1.02, 1), fontsize=8)

    ax.set_title(f"TELLO, HUILA — Red Social con Centralidad\n"
                 f"Tamano del nodo = betweenness centrality | "
                 f"Top 10 super-spreaders etiquetados",
                 fontsize=14, fontweight="bold", pad=20)
    ax.text(0.5, -0.04,
            f"Total: {G.number_of_nodes()} agentes, "
            f"{G.number_of_edges()} relaciones",
            transform=ax.transAxes, ha="center", fontsize=10,
            style="italic", color="gray")

    plt.tight_layout()
    plt.savefig(ruta_png, dpi=120, bbox_inches="tight", facecolor="white")
    plt.close()


def main():
    print("Construyendo red social...")
    G = construir_red()
    print(f"  Nodos: {G.number_of_nodes()}")
    print(f"  Aristas: {G.number_of_edges()}")

    print("\nCalculando centralidad...")
    metricas = calcular_centralidad(G)

    print("\nGenerando reporte...")
    generar_reporte(G, metricas)

    # Guardar reporte como texto
    ruta_reporte = Path("demo_output/centralidad_reporte.txt")
    ruta_reporte.parent.mkdir(parents=True, exist_ok=True)

    import io
    import sys
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    generar_reporte(G, metricas)
    sys.stdout = old_stdout
    ruta_reporte.write_text(buffer.getvalue(), encoding="utf-8")
    print(f"\n[REPORTE] {ruta_reporte}")

    # Visualizar
    ruta_png = Path("demo_output/red_centralidad.png")
    ruta_png.parent.mkdir(parents=True, exist_ok=True)
    visualizar(G, metricas, ruta_png)
    print(f"[PNG]      {ruta_png}")


if __name__ == "__main__":
    main()
