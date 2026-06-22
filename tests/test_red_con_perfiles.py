# -*- coding: utf-8 -*-
"""
tests/test_red_con_perfiles.py
==============================
Tests para analysis/red_con_perfiles.py (260 statements, 0% -> X%).

Estrategia:
- Funciones puras (pearson, mann_whitney_u): tests directos.
- Funciones con dependencias externas (pp, plt):
  monkeypatch sobre red_con_perfiles.pp y mock de plt.savefig.
- analizar() / main(): integration tests con todo mockeado.

Descubrimientos del sprint:
- pp.PERFILES_ADULTOS es dict (26 entradas) con big_five/lomnitz_default
  (letra)/dunbar/rasgos/justificacion_bio.
- lomnitz_default es STRING ('C'), NO lista como en otros lados del repo.
- red_con_perfiles.py depende de perfiles_psicometricos.py (NO COMMITEADO),
  por lo que monkeypatch es la unica forma de testearlo en CI.
"""

import math
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import matplotlib
matplotlib.use("Agg")  # headless: no requiere DISPLAY

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pytest

from analysis import red_con_perfiles as rcp


# =============================================================================
# Helpers / Fixtures
# =============================================================================

def make_perfil(slug, O=50, C=50, E=50, A=50, N=50, lomnitz="C"):
    """Crea un perfil psicometrico sintetico compatible con pp.PERFILES_ADULTOS."""
    return {
        "slug": slug,
        "big_five": {"O": O, "C": C, "E": E, "A": A, "N": N},
        "lomnitz_default": lomnitz,
        "dunbar": {"intimos": 3, "amigos": 5, "conocidos": 12, "saludos": 30},
        "rasgos": ["sintetico"],
        "justificacion_bio": f"Perfil sintetico para tests ({slug}).",
    }


def make_grafo(nodos_con_pos=True):
    """Grafo de 5 nodos con posiciones geograficas ficticias (Tello)."""
    G = nx.Graph()
    nodos = [
        ("don_eliecer_patron", {"tipo": "adulto", "pos": (0.0, 0.0)}),
        ("dona_prudencia_partera", {"tipo": "adulto", "pos": (0.1, 0.1)}),
        ("don_rosalio_rival", {"tipo": "adulto", "pos": (0.2, 0.2)}),
        ("padre_cecilio_cura", {"tipo": "adulto", "pos": (0.3, 0.3)}),
        ("nino_tello_01", {"tipo": "nino", "pos": (0.15, 0.15)}),
    ]
    for slug, attrs in nodos:
        G.add_node(slug, **attrs)
    # Aristas: adultos forman un cuadrado, nino conectado a uno
    G.add_edge("don_eliecer_patron", "dona_prudencia_partera")
    G.add_edge("dona_prudencia_partera", "don_rosalio_rival")
    G.add_edge("don_rosalio_rival", "padre_cecilio_cura")
    G.add_edge("padre_cecilio_cura", "don_eliecer_patron")
    G.add_edge("nino_tello_01", "don_eliecer_patron")
    return G


def make_metricas():
    """Metricas de centralidad sinteticas para los 5 nodos del grafo mock."""
    return {
        "don_eliecer_patron": {
            "betweenness": 0.5, "degree": 4, "closeness": 0.8, "pagerank": 0.4,
        },
        "dona_prudencia_partera": {
            "betweenness": 0.2, "degree": 3, "closeness": 0.7, "pagerank": 0.25,
        },
        "don_rosalio_rival": {
            "betweenness": 0.3, "degree": 3, "closeness": 0.7, "pagerank": 0.25,
        },
        "padre_cecilio_cura": {
            "betweenness": 0.2, "degree": 3, "closeness": 0.7, "pagerank": 0.25,
        },
        # Nino intencionalmente sin metricas para forzar default 0
    }


def make_perfiles_mock():
    """5 perfiles para los 4 adultos del grafo mock + 1 adulto 'huérfano' (sin nodo en G)."""
    return {
        "don_eliecer_patron": make_perfil("don_eliecer_patron", O=30, C=80, E=35, A=70, N=30),
        "dona_prudencia_partera": make_perfil("dona_prudencia_partera", O=75, C=70, E=80, A=85, N=40),
        "don_rosalio_rival": make_perfil("don_rosalio_rival", O=40, C=60, E=50, A=25, N=70),
        "padre_cecilio_cura": make_perfil("padre_cecilio_cura", O=60, C=90, E=55, A=75, N=25),
        "adulto_huerfano": make_perfil("adulto_huerfano"),  # tiene perfil, no aparece en G
    }


def make_nodos_unidos(n=8, seed=42):
    """Genera n nodos_unidos sinteticos para tests de correlacion/MW."""
    rng = np.random.default_rng(seed)
    # 4 con A alto (super-spreaders candidatos) + 4 con A bajo
    nodos = []
    for i in range(n):
        nodos.append({
            "slug": f"agente_{i:02d}",
            "big_five": {
                "O": int(rng.integers(20, 90)),
                "C": int(rng.integers(20, 90)),
                "E": int(rng.integers(20, 90)),
                "A": int(rng.integers(20, 90)),
                "N": int(rng.integers(20, 90)),
            },
            "lomnitz": "C",
            "rasgos": ["sintetico"],
            "betweenness": float(rng.uniform(0, 0.5)),
            "degree": int(rng.integers(1, 10)),
            "closeness": float(rng.uniform(0.3, 0.9)),
            "pagerank": float(rng.uniform(0, 0.4)),
        })
    return nodos


@pytest.fixture
def grafo_mock():
    return make_grafo()


@pytest.fixture
def metricas_mock():
    return make_metricas()


@pytest.fixture
def perfiles_mock(monkeypatch):
    """Inyecta PERFILES_ADULTOS sintéticos en el módulo bajo test."""
    data = make_perfiles_mock()
    monkeypatch.setattr(rcp.pp, "PERFILES_ADULTOS", data)
    return data


@pytest.fixture
def nodos_unidos_mock():
    return make_nodos_unidos(n=10, seed=123)


# =============================================================================
# TestPearson — pearson() puro
# =============================================================================

class TestPearson:
    """Pearson debe manejar 6 casos: nan/empty/mismatch/zero-std/perfect/no-corr."""

    def test_menos_de_3_puntos_retorna_nan(self):
        assert math.isnan(rcp.pearson([1, 2], [3, 4]))

    def test_listas_vacias_retorna_nan(self):
        assert math.isnan(rcp.pearson([], []))

    def test_listas_longitud_distinta_retorna_nan(self):
        assert math.isnan(rcp.pearson([1, 2, 3], [4, 5]))

    def test_desviacion_estandar_cero_en_x_retorna_cero(self):
        # x constante, y variable -> std(x)==0 -> 0.0 (no NaN)
        result = rcp.pearson([5, 5, 5, 5], [1, 2, 3, 4])
        assert result == 0.0

    def test_desviacion_estandar_cero_en_y_retorna_cero(self):
        result = rcp.pearson([1, 2, 3, 4], [5, 5, 5, 5])
        assert result == 0.0

    def test_correlacion_perfecta_positiva(self):
        # r(x, 2x) == 1.0
        result = rcp.pearson([1, 2, 3, 4, 5], [2, 4, 6, 8, 10])
        assert abs(result - 1.0) < 1e-9

    def test_correlacion_perfecta_negativa(self):
        result = rcp.pearson([1, 2, 3, 4, 5], [10, 8, 6, 4, 2])
        assert abs(result - (-1.0)) < 1e-9

    def test_sin_correlacion(self):
        # Vector aleatorio: correlacion debe estar cerca de 0 pero no exacto
        rng = np.random.default_rng(0)
        x = rng.normal(size=100)
        y = rng.normal(size=100)
        result = rcp.pearson(x.tolist(), y.tolist())
        assert abs(result) < 0.3  # estadísticamente casi cero


# =============================================================================
# TestMannWhitneyU — mann_whitney_u() puro
# =============================================================================

class TestMannWhitneyU:
    """Mann-Whitney sin scipy. Casos: vacíos, idénticos, muy diferentes, empates."""

    def test_x_vacio_retorna_nan_nan(self):
        u, p = rcp.mann_whitney_u([], [1, 2, 3])
        assert math.isnan(u)
        assert math.isnan(p)

    def test_y_vacio_retorna_nan_nan(self):
        u, p = rcp.mann_whitney_u([1, 2, 3], [])
        assert math.isnan(u)
        assert math.isnan(p)

    def test_ambos_vacios_retorna_nan_nan(self):
        u, p = rcp.mann_whitney_u([], [])
        assert math.isnan(u) and math.isnan(p)

    def test_identicos_p_es_alto(self):
        # Si x == y, no hay diferencia significativa -> p cerca de 1.0
        u, p = rcp.mann_whitney_u([1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
        assert p > 0.5

    def test_muy_diferentes_p_es_bajo(self):
        # x mucho mayor que y -> diferencia significativa -> p < 0.05
        u, p = rcp.mann_whitney_u([100, 101, 102, 103, 104], [1, 2, 3, 4, 5])
        assert p < 0.05

    def test_empates_manejados_correctamente(self):
        # Empate entre x e y no debe crashear
        u, p = rcp.mann_whitney_u([5, 5, 5, 5], [5, 5, 5, 5])
        # sigma_u puede ser 0 -> p = 1.0
        assert p == 1.0 or p > 0.5

    def test_grupos_pequenos_no_crashes(self):
        # n=1, m=1 no debe dividir por cero
        u, p = rcp.mann_whitney_u([5], [10])
        # resultado puede ser NaN/1.0; lo importante es no crashear
        assert isinstance(u, float) and isinstance(p, float)


# =============================================================================
# TestUnirRedConPerfiles — unir_red_con_perfiles()
# =============================================================================

class TestUnirRedConPerfiles:
    """Filtra adultos del grafo, les pega rasgos Big Five + métricas de red."""

    def test_grafo_vacio_retorna_lista_vacia(self, grafo_mock, metricas_mock, perfiles_mock):
        G = nx.Graph()
        resultado = rcp.unir_red_con_perfiles(G, metricas_mock)
        assert resultado == []

    def test_grafo_sin_adultos_retorna_vacio(self, perfiles_mock):
        G = nx.Graph()
        G.add_node("nino_01", tipo="nino", pos=(0, 0))
        resultado = rcp.unir_red_con_perfiles(G, {})
        assert resultado == []

    def test_adultos_sin_perfil_son_filtrados(self, grafo_mock, metricas_mock, monkeypatch):
        # pp.PERFILES_ADULTOS vacío -> ningún adulto tiene perfil
        monkeypatch.setattr(rcp.pp, "PERFILES_ADULTOS", {})
        resultado = rcp.unir_red_con_perfiles(grafo_mock, metricas_mock)
        assert resultado == []

    def test_adultos_con_perfil_incluidos(self, grafo_mock, metricas_mock, perfiles_mock):
        resultado = rcp.unir_red_con_perfiles(grafo_mock, metricas_mock)
        # 4 adultos en el grafo mock, todos tienen perfil
        slugs = {n["slug"] for n in resultado}
        assert slugs == {
            "don_eliecer_patron", "dona_prudencia_partera",
            "don_rosalio_rival", "padre_cecilio_cura",
        }
        assert "nino_tello_01" not in slugs

    def test_nodo_unido_contiene_todas_las_claves(self, grafo_mock, metricas_mock, perfiles_mock):
        resultado = rcp.unir_red_con_perfiles(grafo_mock, metricas_mock)
        nodo = resultado[0]
        assert set(nodo.keys()) == {
            "slug", "big_five", "lomnitz", "rasgos",
            "betweenness", "degree", "closeness", "pagerank",
        }

    def test_big_five_es_copia_no_referencia(self, grafo_mock, metricas_mock, perfiles_mock):
        # Mutaciones al resultado NO deben afectar pp.PERFILES_ADULTOS original
        resultado = rcp.unir_red_con_perfiles(grafo_mock, metricas_mock)
        resultado[0]["big_five"]["O"] = 999
        # Re-leer de pp debe ser el valor original
        assert rcp.pp.PERFILES_ADULTOS[resultado[0]["slug"]]["big_five"]["O"] != 999

    def test_adulto_sin_metricas_toma_defaults_cero(self, grafo_mock, perfiles_mock):
        # Sin métricas para padre_cecilio_cura -> defaults a 0
        metricas_incompletas = {
            "don_eliecer_patron": {"betweenness": 0.5, "degree": 4, "closeness": 0.8, "pagerank": 0.4},
            "dona_prudencia_partera": {"betweenness": 0.2, "degree": 3, "closeness": 0.7, "pagerank": 0.25},
            "don_rosalio_rival": {"betweenness": 0.3, "degree": 3, "closeness": 0.7, "pagerank": 0.25},
            # padre_cecilio_cura ausente
        }
        resultado = rcp.unir_red_con_perfiles(grafo_mock, metricas_incompletas)
        cecilio = next(n for n in resultado if n["slug"] == "padre_cecilio_cura")
        assert cecilio["betweenness"] == 0
        assert cecilio["degree"] == 0

    def test_adulto_huerfano_en_pp_no_aparece_en_resultado(
        self, grafo_mock, metricas_mock, perfiles_mock
    ):
        # adulto_huerfano tiene perfil pero no está en G -> filtrado
        resultado = rcp.unir_red_con_perfiles(grafo_mock, metricas_mock)
        assert "adulto_huerfano" not in {n["slug"] for n in resultado}


# =============================================================================
# TestCorrelacionesRedPerfil — correlaciones_red_perfil()
# =============================================================================

class TestCorrelacionesRedPerfil:
    """Matriz 4x5 (red x Big Five). Casos: vacío, 1 nodo, correlación perfecta."""

    def test_estructura_matriz_4_metricas_por_5_factores(self, nodos_unidos_mock):
        matriz = rcp.correlaciones_red_perfil(nodos_unidos_mock)
        assert set(matriz.keys()) == {"betweenness", "degree", "closeness", "pagerank"}
        for mr in matriz:
            assert set(matriz[mr].keys()) == {"O", "C", "E", "A", "N"}

    def test_nodos_vacios_produce_nans(self):
        matriz = rcp.correlaciones_red_perfil([])
        # Con 0 nodos, pearson([],[]) -> nan
        for mr in matriz:
            for f in matriz[mr]:
                assert math.isnan(matriz[mr][f]), f"{mr}/{f} no es nan: {matriz[mr][f]}"

    def test_un_solo_nodo_produce_nans(self):
        nodos = [{
            "slug": "solo", "big_five": {"O": 50, "C": 50, "E": 50, "A": 50, "N": 50},
            "lomnitz": "C", "rasgos": [], "betweenness": 0.0, "degree": 0,
            "closeness": 0.0, "pagerank": 0.0,
        }]
        matriz = rcp.correlaciones_red_perfil(nodos)
        # len < 3 -> nan
        for mr in matriz:
            for f in matriz[mr]:
                assert math.isnan(matriz[mr][f]), f"{mr}/{f} no es nan: {matriz[mr][f]}"

    def test_correlacion_perfecta_positiva_detectada(self):
        # big_five.A perfectamente correlacionado con betweenness
        nodos = [
            {
                "slug": f"n{i}", "lomnitz": "C", "rasgos": [],
                "big_five": {"O": 50, "C": 50, "E": 50, "A": 10 + i * 10, "N": 50},
                "betweenness": float(i), "degree": i, "closeness": float(i),
                "pagerank": float(i),
            }
            for i in range(1, 6)  # i=1..5
        ]
        matriz = rcp.correlaciones_red_perfil(nodos)
        assert abs(matriz["betweenness"]["A"] - 1.0) < 1e-9
        # O, C, E, N son constantes (std=0) -> r=0 por rama zero-std
        assert matriz["betweenness"]["O"] == 0.0
        assert matriz["betweenness"]["N"] == 0.0

    def test_desviacion_cero_en_factor_retorna_cero(self):
        # Todos los nodos tienen A=50 -> std=0 -> r=0
        nodos = [
            {
                "slug": f"n{i}", "lomnitz": "C", "rasgos": [],
                "big_five": {"O": 50, "C": 50, "E": 50, "A": 50, "N": 50 + i},
                "betweenness": float(i) / 10, "degree": i, "closeness": 0.5,
                "pagerank": 0.1,
            }
            for i in range(1, 6)
        ]
        matriz = rcp.correlaciones_red_perfil(nodos)
        # Para entre degree y N: ambos crecientes -> r > 0
        # Para A: constante -> r = 0
        assert matriz["betweenness"]["A"] == 0.0
        assert matriz["degree"]["A"] == 0.0


# =============================================================================
# TestCompararSuperSpreaders — comparar_super_spreaders()
# =============================================================================

class TestCompararSuperSpreaders:
    """Mann-Whitney por factor, top_n >= 3 siempre."""

    def test_estructura_resultados_por_factor(self, nodos_unidos_mock):
        resultados, top_slugs = rcp.comparar_super_spreaders(nodos_unidos_mock)
        assert set(resultados.keys()) == {"O", "C", "E", "A", "N"}
        for f, r in resultados.items():
            assert set(r.keys()) == {
                "media_top", "media_resto", "diff", "u", "p", "n_top", "n_resto",
            }

    def test_n_top_es_minimo_3(self):
        # Con solo 5 nodos y top_pct=0.20 -> n_top = max(3, int(5*0.20)) = max(3, 1) = 3
        nodos = make_nodos_unidos(n=5, seed=1)
        resultados, _ = rcp.comparar_super_spreaders(nodos, top_pct=0.20)
        assert resultados["O"]["n_top"] == 3
        assert resultados["O"]["n_resto"] == 2

    def test_diff_es_media_top_menos_media_resto(self, nodos_unidos_mock):
        resultados, _ = rcp.comparar_super_spreaders(nodos_unidos_mock)
        for f, r in resultados.items():
            assert abs(r["diff"] - (r["media_top"] - r["media_resto"])) < 1e-9

    def test_top_slugs_ordenados_por_betweenness_descendente(self, nodos_unidos_mock):
        _, top_slugs = rcp.comparar_super_spreaders(nodos_unidos_mock)
        # Recuperar betweenness de cada top_slug en el mismo orden
        betweenness_por_slug = {n["slug"]: n["betweenness"] for n in nodos_unidos_mock}
        for i in range(len(top_slugs) - 1):
            assert betweenness_por_slug[top_slugs[i]] >= betweenness_por_slug[top_slugs[i + 1]]

    def test_lista_vacia_retorna_manualmente(self):
        resultados, top_slugs = rcp.comparar_super_spreaders([])
        # Con 0 nodos, n_top = max(3, 0) = 3, pero ordenados[:3] = []
        assert resultados["O"]["n_top"] == 3
        assert resultados["O"]["n_resto"] == 0
        assert top_slugs == []


# =============================================================================
# TestPerfilTipicoSuperSpreader — perfil_tipico_super_spreader()
# =============================================================================

class TestPerfilTipicoSuperSpreader:
    """Media Big Five del top 20% por betweenness."""

    def test_devuelve_dict_con_5_factores(self, nodos_unidos_mock):
        perfil, _ = rcp.perfil_tipico_super_spreader(nodos_unidos_mock)
        assert set(perfil.keys()) == {"O", "C", "E", "A", "N"}

    def test_valor_es_media_de_top_20pct(self, nodos_unidos_mock):
        perfil, top_slugs = rcp.perfil_tipico_super_spreader(nodos_unidos_mock)
        # Recalcular media esperada
        n_top = max(3, int(len(nodos_unidos_mock) * 0.20))
        ordenados = sorted(nodos_unidos_mock, key=lambda n: -n["betweenness"])
        top = ordenados[:n_top]
        for f in ("O", "C", "E", "A", "N"):
            expected = float(np.mean([n["big_five"][f] for n in top]))
            assert abs(perfil[f] - expected) < 1e-9

    def test_top_slugs_coincide_con_entre_20pct(self, nodos_unidos_mock):
        _, top_slugs = rcp.perfil_tipico_super_spreader(nodos_unidos_mock)
        n_top = max(3, int(len(nodos_unidos_mock) * 0.20))
        assert len(top_slugs) == n_top


# =============================================================================
# TestVisualizarRedPorFactor — visualizar_red_por_factor()
# =============================================================================

class TestVisualizarRedPorFactor:
    """Genera PNG 2x3 grid (5 factores + grado). Testeamos side-effects."""

    def test_genera_png_en_ruta_especificada(self, grafo_mock, nodos_unidos_mock, tmp_path):
        ruta = tmp_path / "test_red.png"
        # Mockear todo networkx drawing para evitar KeyError en labels
        with patch.object(rcp.nx, "draw_networkx_edges"), \
             patch.object(rcp.nx, "draw_networkx_nodes"), \
             patch.object(rcp.nx, "draw_networkx_labels"), \
             patch.object(rcp.plt, "savefig") as mock_savefig, \
             patch.object(rcp.plt, "close"):
            rcp.visualizar_red_por_factor(grafo_mock, nodos_unidos_mock, str(ruta))
        mock_savefig.assert_called_once()
        args, kwargs = mock_savefig.call_args
        assert args[0] == str(ruta)
        assert kwargs.get("dpi") == 110

    def test_genera_2x3_axes(self, grafo_mock, nodos_unidos_mock, tmp_path):
        ruta = tmp_path / "test_red.png"
        with patch.object(rcp.plt, "subplots") as mock_subplots, \
             patch.object(rcp.nx, "draw_networkx_edges"), \
             patch.object(rcp.nx, "draw_networkx_nodes"), \
             patch.object(rcp.nx, "draw_networkx_labels"), \
             patch.object(rcp.plt, "close"):
            mock_fig = MagicMock()
            mock_axes = np.empty((2, 3), dtype=object)
            for i in range(6):
                mock_axes.flat[i] = MagicMock()
            mock_subplots.return_value = (mock_fig, mock_axes)
            rcp.visualizar_red_por_factor(grafo_mock, nodos_unidos_mock, str(ruta))
        mock_subplots.assert_called_once()
        _, kwargs = mock_subplots.call_args
        assert kwargs.get("figsize") == (24, 16)


# =============================================================================
# TestImprimirReporte — imprimir_reporte()
# =============================================================================

class TestImprimirReporte:
    """Solo verificamos que no crashea y produce output estructurado."""

    def _args_basicos(self, nodos_unidos_mock):
        matriz = rcp.correlaciones_red_perfil(nodos_unidos_mock)
        resultados, top_slugs = rcp.comparar_super_spreaders(nodos_unidos_mock)
        perfil_tipico, _ = rcp.perfil_tipico_super_spreader(nodos_unidos_mock)
        return nodos_unidos_mock, matriz, resultados, top_slugs, perfil_tipico

    def test_imprime_sin_crash(self, nodos_unidos_mock, capsys):
        args = self._args_basicos(nodos_unidos_mock)
        rcp.imprimir_reporte(*args)
        captured = capsys.readouterr()
        # Debe contener headers clave
        assert "RED SOCIAL + PERFILES" in captured.out
        assert "CORRELACION PEARSON" in captured.out
        assert "HALLAZGOS CLAVE" in captured.out

    def test_imprime_h1_y_h3(self, nodos_unidos_mock, capsys):
        args = self._args_basicos(nodos_unidos_mock)
        rcp.imprimir_reporte(*args)
        out = capsys.readouterr().out
        assert "H1 (Christakis-Fowler" in out
        assert "H3 (Watson 1988" in out

    def test_imprime_top_amabilidad_y_betweenness(self, nodos_unidos_mock, capsys):
        args = self._args_basicos(nodos_unidos_mock)
        rcp.imprimir_reporte(*args)
        out = capsys.readouterr().out
        assert "Top 5 Amabilidad" in out
        assert "Top 5 Betweenness" in out


# =============================================================================
# TestAnalizar — analizar() integration
# =============================================================================

class TestAnalizar:
    """Pipeline completo: red -> centralidad -> union -> corr -> MW -> perfil."""

    def test_devuelve_las_5_claves_esperadas(self, monkeypatch):
        # Mockear construir_red, calcular_centralidad, unir_red_con_perfiles
        # para evitar construir la red real (que necesita geo_tello no commiteado en CI)
        G_mock = make_grafo()
        metricas_mock = make_metricas()
        nodos_unidos_mock = make_nodos_unidos(n=5, seed=7)

        monkeypatch.setattr(rcp, "construir_red", lambda: G_mock)
        monkeypatch.setattr(rcp, "calcular_centralidad", lambda G: metricas_mock)
        monkeypatch.setattr(rcp.pp, "PERFILES_ADULTOS", make_perfiles_mock())
        monkeypatch.setattr(
            rcp, "unir_red_con_perfiles",
            lambda G, m: [n for n in nodos_unidos_mock if n["slug"] in {nd for nd in G.nodes()}],
        )

        resultado = rcp.analizar()
        assert set(resultado.keys()) == {
            "nodos_unidos", "matriz_corr", "resultados_ss", "top_slugs", "perfil_tipico",
        }

    def test_ejecucion_real_con_red_y_perfiles_reales(self, capsys):
        # Test de humo: la red real (de red_centralidad) + perfiles reales
        # debe ejecutarse sin crashear
        resultado = rcp.analizar()
        # Debe haber >=10 adultos con perfil (de los ~24-26 esperados)
        assert len(resultado["nodos_unidos"]) >= 10
        # matriz_corr debe tener 4 métricas x 5 factores
        assert len(resultado["matriz_corr"]) == 4
        for mr in resultado["matriz_corr"]:
            assert len(resultado["matriz_corr"][mr]) == 5


# =============================================================================
# TestMain — main() CLI
# =============================================================================

class TestMain:
    """main() ejecuta analizar + imprimir_reporte + generar PNG."""

    def test_main_ejecuta_sin_crash_y_genera_png(self, tmp_path, monkeypatch, capsys):
        # Cambiar cwd a tmp_path para que el PNG se genere allí
        monkeypatch.chdir(tmp_path)
        # Evitar ejecutar analizar() dos veces (lo hace tanto main como implícitamente
        # el reporte). Mockeamos visualizar_red_por_factor para no escribir PNG real.
        with patch.object(rcp, "visualizar_red_por_factor") as mock_viz:
            rcp.main()
        mock_viz.assert_called_once()
        # Debe haber impreso el reporte
        out = capsys.readouterr().out
        assert "RED SOCIAL + PERFILES" in out