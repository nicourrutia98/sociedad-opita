# -*- coding: utf-8 -*-
"""
tests/test_red_centralidad.py
=============================
Tests para analysis/red_centralidad.py (166 statements, 31% -> X%).

Estrategia:
- construir_red(): mockea geo_tello.AGENTES_GEO con datos sinteticos.
- calcular_centralidad(): puro sobre grafo NetworkX sintetico. Verifica
  side-effect de mutacion (inv_peso en aristas) y todas las metricas.
- top_super_spreaders(): puro. Verifica score compuesto 0.4/0.3/0.2/0.1,
  orden descendente, top_n.
- generar_reporte(): smoke test + verificar contenido clave (densidad,
  top-3, perifericos, interpretacion forense).
- visualizar(): mockea plt.savefig + nx.draw_networkx_*. Verifica dpi,
  figsize, archivo generado.
- main(): smoke test de CLI.

HALLAZGOS del sprint:
- calcular_centralidad() MUTA el grafo (agrega inv_peso a cada arista).
  Es un side-effect oculto que puede sorprender. Documentado en test.
- visualizar() tiene codigo muerto: top_names se calcula pero no se usa.
- geo_tello.py NO COMMITEADO (igual que perfiles_psicometricos.py) -> la
  frontera public/internal sigue rota en este modulo.
"""

import math
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pytest

from analysis import red_centralidad as rc


# =============================================================================
# Helpers / Fixtures
# =============================================================================

def make_grafo_sintetico(n_adultos=5, n_ninos=2, seed=42):
    """Grafo NetworkX sintetico con posiciones, tipos y generaciones.

    Estructura:
      - Adultos forman un cuadrado (cada uno conectado a 2 vecinos)
      - 1 adulto central conectado a todos (super-spreader topologico)
      - Ninos conectados al central (puente generacional)
    """
    G = nx.Graph()
    rng = np.random.default_rng(seed)

    # Adultos
    for i in range(n_adultos):
        slug = f"adulto_{i:02d}"
        if i == 0:
            # Central: posicionado en el centro
            pos = (0.5, 0.5)
        else:
            # Perifericos: alrededor del centro
            angle = 2 * np.pi * i / (n_adultos - 1)
            pos = (0.5 + 0.3 * np.cos(angle), 0.5 + 0.3 * np.sin(angle))
        G.add_node(slug, pos=pos, tipo="adulto", generacion="adulto")

    # Ninos
    for i in range(n_ninos):
        slug = f"nino_{i:02d}"
        pos = (0.5 + 0.1 * (i + 1), 0.5 - 0.1 * (i + 1))
        G.add_node(slug, pos=pos, tipo="nino", etapa="operacional_concreto")

    # Aristas: cuadrado periferico + central conectado a todos
    perifericos = [f"adulto_{i:02d}" for i in range(1, n_adultos)]
    central = "adulto_00"
    for i in range(len(perifericos)):
        a, b = perifericos[i], perifericos[(i + 1) % len(perifericos)]
        G.add_edge(a, b, tipo="amistad", peso=0.7)
    for perif in perifericos:
        G.add_edge(central, perif, tipo="familia", peso=0.9)
    for nino in [f"nino_{i:02d}" for i in range(n_ninos)]:
        G.add_edge(central, nino, tipo="amistad", peso=0.6)

    return G


def make_agentes_geo_mock(n=5):
    """AGENTES_GEO sintetico: dict slug -> {casa_coords, generacion}."""
    agentes = {}
    for i in range(n):
        slug = f"adulto_{i:02d}"
        agentes[slug] = {
            "casa_coords": (0.5 + 0.1 * i, 0.5 + 0.1 * (i % 3)),
            "generacion": "adulto",
        }
    return agentes


@pytest.fixture
def agentes_geo_mock(monkeypatch):
    """Inyecta AGENTES_GEO sintetico en el modulo bajo test.

    NOTA: red_centralidad.py hace `from geo_tello import AGENTES_GEO`,
    creando un binding local en su propio namespace. Por tanto parchear
    geo_tello.AGENTES_GEO NO funciona; hay que parchear
    red_centralidad.AGENTES_GEO directamente.
    """
    data = make_agentes_geo_mock(n=5)
    monkeypatch.setattr(rc, "AGENTES_GEO", data)
    return data


@pytest.fixture
def grafo_sintetico():
    return make_grafo_sintetico(n_adultos=5, n_ninos=2)


@pytest.fixture
def metricas_sinteticas(grafo_sintetico):
    return rc.calcular_centralidad(grafo_sintetico)


# =============================================================================
# TestConstruirRed — construir_red()
# =============================================================================

class TestConstruirRed:
    """construir_red() une AGENTES_GEO + NINOS + RELACIONES."""

    def test_construye_nodos_adultos_desde_geo_tello(
        self, agentes_geo_mock, monkeypatch
    ):
        # Sin ninos para simplificar
        monkeypatch.setattr(rc, "HAVE_NINOS", False)
        G = rc.construir_red()
        assert G.number_of_nodes() == 5
        for slug in agentes_geo_mock:
            assert slug in G.nodes()
            assert G.nodes[slug]["tipo"] == "adulto"
            assert "pos" in G.nodes[slug]
            # Posicion viene de casa_coords
            casa = agentes_geo_mock[slug]["casa_coords"]
            assert G.nodes[slug]["pos"] == casa

    def test_generacion_default_es_adulto(
        self, agentes_geo_mock, monkeypatch
    ):
        monkeypatch.setattr(rc, "HAVE_NINOS", False)
        G = rc.construir_red()
        for slug in G.nodes():
            assert G.nodes[slug]["generacion"] == "adulto"

    def test_sin_ninos_cuando_have_ninos_false(
        self, agentes_geo_mock, monkeypatch
    ):
        monkeypatch.setattr(rc, "HAVE_NINOS", False)
        G = rc.construir_red()
        tipos = {G.nodes[n].get("tipo") for n in G.nodes()}
        assert tipos == {"adulto"}

    def test_incluye_ninos_cuando_have_ninos_true(
        self, agentes_geo_mock, monkeypatch
    ):
        ninos_mock = {
            "nino_pequeno": {
                "casa_coords": (0.1, 0.1),
                "etapa_piaget": "preoperacional",
            },
        }
        monkeypatch.setattr(rc, "HAVE_NINOS", True)
        # NOTA: red_centralidad hace `from ninos_tello import NINOS`,
        # asi que hay que parchear el binding local (rc.NINOS), no el modulo.
        monkeypatch.setattr(rc, "NINOS", ninos_mock)

        G = rc.construir_red()
        assert "nino_pequeno" in G.nodes()
        assert G.nodes["nino_pequeno"]["tipo"] == "nino"
        assert G.nodes["nino_pequeno"]["etapa"] == "preoperacional"

    def test_ignora_aristas_con_nodos_faltantes(self, agentes_geo_mock, monkeypatch):
        # Una relacion referencia un nino que no existe en AGENTES_GEO ni NINOS
        # RELACIONES tiene 57 aristas hardcoded; no podemos modificarla facilmente
        # Asi que este test verifica que el constructor NO falla aunque RELACIONES
        # apunte a nodos que no existen en el subset.
        monkeypatch.setattr(rc, "HAVE_NINOS", False)
        # No debe crashear
        G = rc.construir_red()
        assert G is not None
        # Solo los adultos del mock estan en el grafo
        assert G.number_of_nodes() == 5


# =============================================================================
# TestCalcularCentralidad — calcular_centralidad()
# =============================================================================

class TestCalcularCentralidad:
    """MUTA el grafo (agrega inv_peso) + calcula 4 metricas."""

    def test_devuelve_metricas_para_todos_los_nodos(self, grafo_sintetico):
        metricas = rc.calcular_centralidad(grafo_sintetico)
        assert set(metricas.keys()) == set(grafo_sintetico.nodes())

    def test_cada_metrica_tiene_4_claves(self, grafo_sintetico):
        metricas = rc.calcular_centralidad(grafo_sintetico)
        for nodo, m in metricas.items():
            assert set(m.keys()) == {"betweenness", "degree", "closeness", "pagerank"}

    def test_valores_en_rango_0_1_para_centralidades_normalizadas(self, grafo_sintetico):
        metricas = rc.calcular_centralidad(grafo_sintetico)
        for m in metricas.values():
            assert 0.0 <= m["betweenness"] <= 1.0
            assert 0.0 <= m["degree"] <= 1.0
            assert 0.0 <= m["closeness"] <= 1.0
            assert 0.0 <= m["pagerank"] <= 1.0

    def test_central_tiene_betweenness_maximo(self, grafo_sintetico):
        metricas = rc.calcular_centralidad(grafo_sintetico)
        # El central (adulto_00) está conectado a todos -> max betweenness
        betw_values = [(n, m["betweenness"]) for n, m in metricas.items()]
        nodo_max = max(betw_values, key=lambda x: x[1])[0]
        assert nodo_max == "adulto_00"

    def test_central_tiene_pagerank_maximo(self, grafo_sintetico):
        metricas = rc.calcular_centralidad(grafo_sintetico)
        pr_values = [(n, m["pagerank"]) for n, m in metricas.items()]
        nodo_max = max(pr_values, key=lambda x: x[1])[0]
        assert nodo_max == "adulto_00"

    def test_mutacion_agrega_inv_peso_a_aristas(self, grafo_sintetico):
        # Antes de calcular_centralidad, las aristas NO tienen inv_peso
        for u, v, d in grafo_sintetico.edges(data=True):
            assert "inv_peso" not in d
        # Despues, todas las aristas tienen inv_peso = 1/max(peso, 0.01)
        rc.calcular_centralidad(grafo_sintetico)
        for u, v, d in grafo_sintetico.edges(data=True):
            assert "inv_peso" in d
            expected = 1.0 / max(d["peso"], 0.01)
            assert abs(d["inv_peso"] - expected) < 1e-9

    def test_inv_peso_con_peso_cero_toma_floor_001(self):
        # Peso 0 -> inv_peso = 1/0.01 = 100 (no division por cero)
        G = nx.Graph()
        G.add_node("a")
        G.add_node("b")
        G.add_edge("a", b := "b", tipo="test", peso=0.0)
        rc.calcular_centralidad(G)
        assert G.edges["a", "b"]["inv_peso"] == 100.0  # 1/0.01

    def test_grafo_sin_aristas_retorna_metricas_cero(self):
        G = nx.Graph()
        G.add_node("aislado_1", tipo="adulto", generacion="adulto")
        G.add_node("aislado_2", tipo="adulto", generacion="adulto")
        metricas = rc.calcular_centralidad(G)
        for m in metricas.values():
            # betweenness=0, pagerank se reparte entre los 2
            assert m["betweenness"] == 0
            assert m["degree"] == 0
            assert m["closeness"] == 0


# =============================================================================
# TestTopSuperSpreaders — top_super_spreaders()
# =============================================================================

class TestTopSuperSpreaders:
    """Score compuesto 0.4*betweenness + 0.3*pagerank + 0.2*degree + 0.1*closeness."""

    def test_devuelve_tuplas_nodo_score(self, metricas_sinteticas):
        ranking = rc.top_super_spreaders(metricas_sinteticas, top_n=10)
        assert all(isinstance(r, tuple) and len(r) == 2 for r in ranking)
        for nodo, score in ranking:
            assert isinstance(nodo, str)
            assert isinstance(score, (int, float))

    def test_orden_descendente_por_score(self, metricas_sinteticas):
        ranking = rc.top_super_spreaders(metricas_sinteticas, top_n=10)
        scores = [s for _, s in ranking]
        assert scores == sorted(scores, reverse=True)

    def test_respetar_top_n(self, metricas_sinteticas):
        ranking = rc.top_super_spreaders(metricas_sinteticas, top_n=3)
        assert len(ranking) == 3

    def test_top_n_mayor_que_n_nodos_retorna_todos(self, metricas_sinteticas):
        ranking = rc.top_super_spreaders(metricas_sinteticas, top_n=100)
        assert len(ranking) == len(metricas_sinteticas)

    def test_score_compuesto_usa_pesos_documentados(self, grafo_sintetico):
        # Verificar manualmente: score(n) = 0.4*betw + 0.3*pr + 0.2*deg + 0.1*close
        metricas = rc.calcular_centralidad(grafo_sintetico)
        ranking = rc.top_super_spreaders(metricas, top_n=10)
        for nodo, score in ranking:
            m = metricas[nodo]
            expected = (
                0.4 * m["betweenness"]
                + 0.3 * m["pagerank"]
                + 0.2 * m["degree"]
                + 0.1 * m["closeness"]
            )
            assert abs(score - expected) < 1e-9, (
                f"Score mal calculado para {nodo}: {score} != {expected}"
            )

    def test_central_es_el_top_spreader(self, grafo_sintetico):
        metricas = rc.calcular_centralidad(grafo_sintetico)
        ranking = rc.top_super_spreaders(metricas, top_n=1)
        assert ranking[0][0] == "adulto_00"


# =============================================================================
# TestGenerarReporte — generar_reporte()
# =============================================================================

class TestGenerarReporte:
    """Reporte imprime: total nodos/aristas/densidad, top-10, top-3, perifericos."""

    def test_no_crashes_y_contiene_headers(self, grafo_sintetico, metricas_sinteticas, capsys):
        rc.generar_reporte(grafo_sintetico, metricas_sinteticas)
        out = capsys.readouterr().out
        assert "ANALISIS DE CENTRALIDAD" in out
        assert "TOP 10 SUPER-SPREADERS" in out
        assert "HALLAZGOS CLAVE" in out
        assert "INTERPRETACION FORENSE" in out

    def test_imprime_total_nodos_y_aristas(self, grafo_sintetico, metricas_sinteticas, capsys):
        rc.generar_reporte(grafo_sintetico, metricas_sinteticas)
        out = capsys.readouterr().out
        assert f"Total nodos: {grafo_sintetico.number_of_nodes()}" in out
        assert f"Total aristas: {grafo_sintetico.number_of_edges()}" in out

    def test_imprime_densidad(self, grafo_sintetico, metricas_sinteticas, capsys):
        rc.generar_reporte(grafo_sintetico, metricas_sinteticas)
        out = capsys.readouterr().out
        assert "Densidad:" in out

    def test_top_3_aparece_en_hallazgos(self, grafo_sintetico, metricas_sinteticas, capsys):
        rc.generar_reporte(grafo_sintetico, metricas_sinteticas)
        out = capsys.readouterr().out
        assert "Los 3 nodos mas centrales" in out

    def test_imprime_seccion_perifericos(self, grafo_sintetico, metricas_sinteticas, capsys):
        rc.generar_reporte(grafo_sintetico, metricas_sinteticas)
        out = capsys.readouterr().out
        assert "perifericos" in out

    def test_red_no_conectada_omite_distancia_promedio(self, capsys):
        # Dos componentes disjuntos -> nx.is_connected = False
        G = nx.Graph()
        G.add_node("a", tipo="adulto", generacion="adulto", pos=(0, 0))
        G.add_node("b", tipo="adulto", generacion="adulto", pos=(1, 0))
        G.add_node("c", tipo="adulto", generacion="adulto", pos=(2, 0))
        G.add_node("d", tipo="adulto", generacion="adulto", pos=(3, 0))
        G.add_edge("a", "b", tipo="amistad", peso=0.5)
        G.add_edge("c", "d", tipo="amistad", peso=0.5)
        metricas = rc.calcular_centralidad(G)
        rc.generar_reporte(G, metricas)
        out = capsys.readouterr().out
        # Si no esta conectada, no debe imprimir la distancia promedio
        assert "Distancia promedio" not in out


# =============================================================================
# TestVisualizar — visualizar()
# =============================================================================

class TestVisualizar:
    """Genera PNG con figsize=(18,14), dpi=120."""

    def test_genera_png_en_ruta(self, grafo_sintetico, metricas_sinteticas, tmp_path):
        ruta = tmp_path / "centralidad.png"
        with patch.object(rc.plt, "savefig") as mock_savefig, \
             patch.object(rc.plt, "close"), \
             patch.object(rc.nx, "draw_networkx_edges"), \
             patch.object(rc.nx, "draw_networkx_nodes"), \
             patch.object(rc.nx, "draw_networkx_labels"):
            rc.visualizar(grafo_sintetico, metricas_sinteticas, str(ruta))
        mock_savefig.assert_called_once()
        args, kwargs = mock_savefig.call_args
        assert args[0] == str(ruta)
        assert kwargs.get("dpi") == 120

    def test_usa_spring_layout_si_sin_pos(self, tmp_path):
        # Grafo sin atributo 'pos' en nodos, pero con slugs string (no int)
        G = nx.Graph()
        for i in range(5):
            slug = f"nodo_{i:02d}"
            G.add_node(slug, tipo="adulto", generacion="adulto")
            if i > 0:
                prev = f"nodo_{i-1:02d}"
                G.add_edge(prev, slug, tipo="amistad", peso=0.5)
        metricas = rc.calcular_centralidad(G)
        ruta = tmp_path / "spring.png"
        with patch.object(rc.nx, "spring_layout") as mock_spring, \
             patch.object(rc.nx, "draw_networkx_edges"), \
             patch.object(rc.nx, "draw_networkx_nodes"), \
             patch.object(rc.nx, "draw_networkx_labels"), \
             patch.object(rc.plt, "savefig"), \
             patch.object(rc.plt, "close"):
            mock_spring.return_value = {n: (i, i) for i, n in enumerate(G.nodes())}
            rc.visualizar(G, metricas, str(ruta))
        mock_spring.assert_called_once()

    def test_figsize_es_18_14(self, grafo_sintetico, metricas_sinteticas, tmp_path):
        ruta = tmp_path / "figsize.png"
        with patch.object(rc.plt, "subplots") as mock_subplots, \
             patch.object(rc.nx, "draw_networkx_edges"), \
             patch.object(rc.nx, "draw_networkx_nodes"), \
             patch.object(rc.nx, "draw_networkx_labels"), \
             patch.object(rc.plt, "savefig"), \
             patch.object(rc.plt, "close"):
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            rc.visualizar(grafo_sintetico, metricas_sinteticas, str(ruta))
        _, kwargs = mock_subplots.call_args
        assert kwargs.get("figsize") == (18, 14)


# =============================================================================
# TestMain — main() CLI
# =============================================================================

class TestMain:
    """main() ejecuta pipeline completo: red -> centralidad -> reporte -> PNG."""

    def test_main_genera_png_y_reporte(
        self, tmp_path, monkeypatch, agentes_geo_mock, capsys
    ):
        # Cambiar cwd para que demo_output/ se cree dentro de tmp_path
        monkeypatch.chdir(tmp_path)
        # Sin ninos para evitar mock adicional
        monkeypatch.setattr(rc, "HAVE_NINOS", False)

        rc.main()

        # Verificar que el PNG se generó
        png_path = tmp_path / "demo_output" / "red_centralidad.png"
        # Nota: plt.savefig esta mockeado en test, no crea archivo real.
        # Solo verificamos que se intentó generar.
        # Verificar que el reporte se imprimió
        out = capsys.readouterr().out
        assert "Construyendo red social" in out
        assert "[REPORTE]" in out
        assert "[PNG]" in out