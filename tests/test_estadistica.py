# -*- coding: utf-8 -*-
"""
tests/test_estadistica.py — Tests unitarios para analysis/estadistica.py
==========================================================================

Cubre:
  - estadistica_descriptiva() — media, mediana, std, min, max, IQR
  - distribucion_lomnitz() — conteo por categoría A/B/C
  - distribucion_dunbar() — red social (auto-refs, recíprocos, asimétricos)
  - bootstrap_ci() — confidence interval sobre la media
  - correlacion_pearson() — r=1, r=-1, r=0, NaN con pocos puntos
  - validar_coherencia() — comparación con rangos teóricos
  - comparar_con_base() — comparación con Schmitt 2007
  - comparar_lomnitz() — Mann-Whitney U
  - analizar_perfiles() — composición del output

Mockea `perfiles_psicometricos` con dataset sintético autocontenido.
NO hace red ni filesystem.
"""
from __future__ import annotations

from collections import Counter
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest


# ======================================================================
# Dataset sintético
# ======================================================================

def make_perfiles_sinteticos() -> dict:
    """Crea 10 perfiles sintéticos con cobertura de los 3 grupos Lomnitz
    y variedad en Big Five + Dunbar (auto-refs, recíprocos, asimétricos).

    Estructura idéntica a pp.PERFILES_ADULTOS (mockeable).
    """
    return {
        # Grupo A (simétrica): compadres — amabilidad alta
        "alcalde": {
            "big_five": {"O": 60, "C": 70, "E": 65, "A": 80, "N": 30},
            "lomnitz_default": "A",
            "dunbar": {
                "intimos": ["sacristan", "tendera"],
                "buenos": ["medico", "conductor", "boticario"],
            },
        },
        "sacristan": {
            "big_five": {"O": 55, "C": 75, "E": 50, "A": 85, "N": 25},
            "lomnitz_default": "A",
            "dunbar": {
                "intimos": ["alcalde", "tendera"],  # recíproco con alcalde
                "buenos": ["medico", "panadera", "conductor"],
            },
        },
        "tendera": {
            "big_five": {"O": 70, "C": 60, "E": 75, "A": 78, "N": 35},
            "lomnitz_default": "A",
            "dunbar": {
                "intimos": ["alcalde", "sacristan", "comisaria", "panadera", "panadero_jubilado"],
                "buenos": ["medico", "conductor", "boticario", "agricultor"],
            },
        },
        # Grupo B (generalizada): nivel medio
        "medico": {
            "big_five": {"O": 75, "C": 80, "E": 45, "A": 65, "N": 40},
            "lomnitz_default": "B",
            "dunbar": {
                "intimos": ["esposa_medico", "tendera"],
                "buenos": ["alcalde", "sacristan", "conductor"],
            },
        },
        "conductor": {
            "big_five": {"O": 50, "C": 55, "E": 70, "A": 60, "N": 45},
            "lomnitz_default": "B",
            "dunbar": {
                "intimos": ["comisaria"],
                "buenos": ["alcalde", "sacristan", "tendera", "medico"],
            },
        },
        "comisaria": {
            "big_five": {"O": 65, "C": 72, "E": 60, "A": 62, "N": 38},
            "lomnitz_default": "B",
            "dunbar": {
                "intimos": ["tendera", "conductor"],
                "buenos": ["alcalde", "sacristan", "medico"],
            },
        },
        # Grupo C (negativa): jornaleros — amabilidad baja, neuroticismo alto
        "minero": {
            "big_five": {"O": 35, "C": 30, "E": 55, "A": 25, "N": 75},
            "lomnitz_default": "C",
            "dunbar": {
                "intimos": ["minero"],  # AUTO-REFERENCIA
                "buenos": ["panadero_jubilado", "conductor"],
            },
        },
        "agricultor": {
            "big_five": {"O": 40, "C": 45, "E": 40, "A": 30, "N": 70},
            "lomnitz_default": "C",
            "dunbar": {
                "intimos": ["agricultor"],  # AUTO-REFERENCIA
                "buenos": ["tendera"],
            },
        },
        "panadero_jubilado": {
            "big_five": {"O": 45, "C": 50, "E": 35, "A": 28, "N": 80},
            "lomnitz_default": "C",
            "dunbar": {
                "intimos": ["tendera"],  # asimétrico: tendera tiene panadero_jubilado en intimos, pero panadero no viceversa
                "buenos": ["minero", "conductor", "boticario"],
            },
        },
        "boticario": {
            "big_five": {"O": 65, "C": 68, "E": 50, "A": 55, "N": 42},
            "lomnitz_default": "B",
            "dunbar": {
                "intimos": ["esposa_boticario", "medico"],
                "buenos": ["alcalde", "sacristan", "tendera", "panadero_jubilado"],
            },
        },
    }


@pytest.fixture
def perfiles_sinteticos():
    """Fixture: dict de perfiles sintéticos."""
    return make_perfiles_sinteticos()


@pytest.fixture
def mock_pp(perfiles_sinteticos):
    """Mock del módulo perfiles_psicometricos.

    Crea un SimpleNamespace que expone PERFILES_ADULTOS con el dataset
    sintético. Se inyecta en analysis.estadistica.pp con patch().
    """
    return SimpleNamespace(PERFILES_ADULTOS=perfiles_sinteticos)


# ======================================================================
# Import top-level para que coverage rastree el módulo
# (imports dentro de `with patch(...)` se hacen tarde y coverage los pierde)
# ======================================================================
from analysis.estadistica import (
    BASE_COLOMBIA,
    CORRELACIONES_ESPERADAS,
    FACTORES,
    analizar_perfiles,
    bootstrap_ci,
    comparar_con_base,
    comparar_lomnitz,
    correlacion_pearson,
    distribucion_dunbar,
    distribucion_lomnitz,
    estadistica_descriptiva,
    validar_coherencia,
)


# ======================================================================
# Tests de estadistica_descriptiva()
# ======================================================================

class TestEstadisticaDescriptiva:
    def test_returns_dict_with_all_factors(self, mock_pp):
        with patch("analysis.estadistica.pp", mock_pp):
            result = estadistica_descriptiva()

        assert set(result.keys()) == set(FACTORES)
        assert FACTORES == ("O", "C", "E", "A", "N")

    def test_factor_has_required_fields(self, mock_pp):
        with patch("analysis.estadistica.pp", mock_pp):
            result = estadistica_descriptiva()

        for factor in result:
            r = result[factor]
            for field in ("n", "media", "mediana", "std", "min", "max",
                          "q25", "q75", "iqr", "scores"):
                assert field in r, f"Falta '{field}' en {factor}"

    def test_n_equals_perfil_count(self, mock_pp, perfiles_sinteticos):
        with patch("analysis.estadistica.pp", mock_pp):
            result = estadistica_descriptiva()

        for factor in result:
            assert result[factor]["n"] == len(perfiles_sinteticos)

    def test_mean_min_max_consistent(self, mock_pp):
        with patch("analysis.estadistica.pp", mock_pp):
            result = estadistica_descriptiva()

        for factor in result:
            r = result[factor]
            assert r["min"] <= r["media"] <= r["max"]
            assert r["min"] <= r["mediana"] <= r["max"]

    def test_iqr_equals_q75_minus_q25(self, mock_pp):
        with patch("analysis.estadistica.pp", mock_pp):
            result = estadistica_descriptiva()

        for factor in result:
            r = result[factor]
            assert r["iqr"] == pytest.approx(r["q75"] - r["q25"])

    def test_std_uses_sample_ddof_1(self, mock_pp, perfiles_sinteticos):
        """std usa ddof=1 (sample std). Verificar manualmente."""
        with patch("analysis.estadistica.pp", mock_pp):
            result = estadistica_descriptiva()

        for factor in result:
            scores = [perfiles_sinteticos[s]["big_five"][factor] for s in perfiles_sinteticos]
            expected = float(np.std(scores, ddof=1))
            assert result[factor]["std"] == pytest.approx(expected, rel=1e-6)

    def test_synthetic_a_mean_amabilidad(self, mock_pp):
        """Media de Amabilidad sobre los 10 perfiles sintéticos."""
        with patch("analysis.estadistica.pp", mock_pp):
            result = estadistica_descriptiva()

        # A values across all 10 perfiles: 80,85,78,65,60,62,25,30,28,55 → mean=56.8
        assert result["A"]["media"] == pytest.approx(56.8, abs=0.1)
        assert result["A"]["min"] == 25  # minero
        assert result["A"]["max"] == 85  # sacristan


# ======================================================================
# Tests de distribucion_lomnitz()
# ======================================================================

class TestDistribucionLomnitz:
    def test_returns_three_categories(self, mock_pp):
        with patch("analysis.estadistica.pp", mock_pp):
            result = distribucion_lomnitz()

        assert set(result.keys()) == {"A", "B", "C"}

    def test_counts_match_synthetic(self, mock_pp):
        with patch("analysis.estadistica.pp", mock_pp):
            result = distribucion_lomnitz()

        # Sintético: A=3, B=4, C=3
        assert result["A"]["n"] == 3
        assert result["B"]["n"] == 4
        assert result["C"]["n"] == 3

    def test_percentages_sum_to_100(self, mock_pp):
        with patch("analysis.estadistica.pp", mock_pp):
            result = distribucion_lomnitz()

        total = sum(result[k]["pct"] for k in ["A", "B", "C"])
        assert total == pytest.approx(100.0, abs=0.01)

    def test_empty_distribution_retorna_ceros_sin_crash(self):
        """distribucion_lomnitz() debe manejar n=0 sin division por cero.

        Si PERFILES_ADULTOS esta vacio, retorna las 3 categorias con
        n=0 y pct=0.0. Antes del fix (s1-cimientos), lanzaba ZeroDivisionError.
        """
        mock_empty = SimpleNamespace(PERFILES_ADULTOS={})
        with patch("analysis.estadistica.pp", mock_empty):
            result = distribucion_lomnitz()

        for cat in ("A", "B", "C"):
            assert result[cat]["n"] == 0
            assert result[cat]["pct"] == 0.0


# ======================================================================
# Tests de distribucion_dunbar()
# ======================================================================

class TestDistribucionDunbar:
    def test_returns_n_perfiles(self, mock_pp, perfiles_sinteticos):
        with patch("analysis.estadistica.pp", mock_pp):
            result = distribucion_dunbar()

        assert result["n_perfiles"] == len(perfiles_sinteticos)

    def test_intimos_expected_count(self, mock_pp, perfiles_sinteticos):
        """n_esperado = n_perfiles * 5."""
        with patch("analysis.estadistica.pp", mock_pp):
            result = distribucion_dunbar()

        assert result["intimos"]["n_esperado"] == len(perfiles_sinteticos) * 5

    def test_buenos_expected_count(self, mock_pp, perfiles_sinteticos):
        with patch("analysis.estadistica.pp", mock_pp):
            result = distribucion_dunbar()

        assert result["buenos"]["n_esperado"] == len(perfiles_sinteticos) * 15

    def test_detects_auto_referencias(self, mock_pp):
        """minero y agricultor se tienen a sí mismos en intimos → 2 auto-refs."""
        with patch("analysis.estadistica.pp", mock_pp):
            result = distribucion_dunbar()

        assert result["intimos"]["auto_referencias"] == 2

    def test_detects_reciprocos(self, mock_pp):
        """Cuenta pares recíprocos en intimos.

        En el dataset sintético, los pares donde (a,b) y (b,a) existen:
          - alcalde <-> sacristan
          - alcalde <-> tendera
          - sacristan <-> tendera
          - conductor <-> comisaria
          - tendera <-> panadero_jubilado
          - boticario <-> medico
        = 6 pares
        """
        with patch("analysis.estadistica.pp", mock_pp):
            result = distribucion_dunbar()

        assert result["intimos"]["reciprocos"] == 6

    def test_asimetricos_count_correct(self, mock_pp):
        """asimétricos = total - 2*recíprocos."""
        with patch("analysis.estadistica.pp", mock_pp):
            result = distribucion_dunbar()

        n = result["intimos"]["n_enlaces_dirigidos"]
        reciprocos = result["intimos"]["reciprocos"]
        asimetricos = result["intimos"]["asimetricos"]
        assert asimetricos == n - 2 * reciprocos

    def test_pct_asimetria_range(self, mock_pp):
        """pct_asimetria debe estar entre 0 y 100."""
        with patch("analysis.estadistica.pp", mock_pp):
            result = distribucion_dunbar()

        for capa in ("intimos", "buenos"):
            pct = result[capa]["pct_asimetria"]
            assert 0.0 <= pct <= 100.0


# ======================================================================
# Tests de bootstrap_ci()
# ======================================================================

class TestBootstrapCI:
    def test_returns_required_fields(self):
        scores = [50, 60, 70, 80, 90]
        result = bootstrap_ci(scores, n_boot=100, seed=42)

        for field in ("media", "ci_low", "ci_high", "std_error", "n_boot"):
            assert field in result

    def test_media_matches_array_mean(self):
        scores = [10, 20, 30, 40, 50]
        result = bootstrap_ci(scores, n_boot=100, seed=42)
        assert result["media"] == pytest.approx(30.0)

    def test_ci_contains_mean(self):
        """El CI al 95% debe contener la media del array."""
        scores = list(range(1, 101))  # 1..100
        result = bootstrap_ci(scores, n_boot=2000, seed=42)
        assert result["ci_low"] <= result["media"] <= result["ci_high"]

    def test_ci_wider_with_higher_variance(self):
        """CI es más ancho cuando la población tiene mayor varianza, con n fijo."""
        low_var = [50] * 20          # std = 0
        high_var = list(range(1, 21)) # std ≈ 5.9

        r_low = bootstrap_ci(low_var, n_boot=500, seed=42)
        r_high = bootstrap_ci(high_var, n_boot=500, seed=42)

        width_low = r_low["ci_high"] - r_low["ci_low"]
        width_high = r_high["ci_high"] - r_high["ci_low"]
        assert width_high > width_low

    def test_seed_reproducible(self):
        """Misma seed → mismo resultado (reproducibilidad forense)."""
        scores = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        r1 = bootstrap_ci(scores, n_boot=100, seed=42)
        r2 = bootstrap_ci(scores, n_boot=100, seed=42)
        assert r1["ci_low"] == r2["ci_low"]
        assert r1["ci_high"] == r2["ci_high"]
        assert r1["std_error"] == r2["std_error"]

    def test_different_seeds_different_results(self):
        scores = list(range(1, 51))
        r1 = bootstrap_ci(scores, n_boot=100, seed=1)
        r2 = bootstrap_ci(scores, n_boot=100, seed=2)
        assert r1["ci_low"] != r2["ci_low"] or r1["ci_high"] != r2["ci_high"]

    def test_ci_levels(self):
        """ci=0.99 debe dar un CI más ancho que ci=0.90."""
        scores = list(range(1, 51))
        r_90 = bootstrap_ci(scores, n_boot=200, seed=42, ci=0.90)
        r_99 = bootstrap_ci(scores, n_boot=200, seed=42, ci=0.99)
        width_90 = r_90["ci_high"] - r_90["ci_low"]
        width_99 = r_99["ci_high"] - r_99["ci_low"]
        assert width_99 > width_90


# ======================================================================
# Tests de correlacion_pearson()
# ======================================================================

class TestCorrelacionPearson:
    def test_perfect_positive(self):
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        assert correlacion_pearson(x, y) == pytest.approx(1.0, abs=1e-9)

    def test_perfect_negative(self):
        x = [1, 2, 3, 4, 5]
        y = [10, 8, 6, 4, 2]
        assert correlacion_pearson(x, y) == pytest.approx(-1.0, abs=1e-9)

    def test_uncorrelated_near_zero(self):
        """Dos variables permutadas aleatoriamente deben tener correlación ~0."""
        import random
        x = list(range(100))
        random.seed(42)
        y = random.sample(x, k=len(x))
        r = correlacion_pearson(x, y)
        assert abs(r) < 0.1, f"Esperado |r| < 0.1, obtuve {r}"

    def test_returns_nan_for_short_arrays(self):
        import math
        r = correlacion_pearson([1, 2], [3, 4])
        assert math.isnan(r)

    def test_returns_nan_for_empty(self):
        import math
        r = correlacion_pearson([], [])
        assert math.isnan(r)

    def test_works_with_numpy_arrays(self):
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([5, 4, 3, 2, 1])
        assert correlacion_pearson(x, y) == pytest.approx(-1.0, abs=1e-9)


# ======================================================================
# Tests de validar_coherencia()
# ======================================================================

class TestValidarCoherencia:
    def test_returns_boolean(self, mock_pp, capsys):
        with patch("analysis.estadistica.pp", mock_pp):
            desc = estadistica_descriptiva()
            result = validar_coherencia(desc)
        assert isinstance(result, bool)
        captured = capsys.readouterr()
        assert "VALIDACION DE COHERENCIA" in captured.out
        assert "r_observado" in captured.out

    def test_incoherente_returns_false(self, capsys):
        """Si los perfiles NO correlacionan como la literatura predice, retorna False."""
        incoherente = {
            f"p{i}": {
                "big_five": {
                    "O": 50, "C": i * 10 % 100,
                    "E": 50, "A": 50 - i * 5 % 100,
                    "N": 50,
                },
                "lomnitz_default": "A",
                "dunbar": {"intimos": [], "buenos": []},
            }
            for i in range(10)
        }
        mock_incoh = SimpleNamespace(PERFILES_ADULTOS=incoherente)
        with patch("analysis.estadistica.pp", mock_incoh):
            desc = estadistica_descriptiva()
            result = validar_coherencia(desc)

        assert result is False
        capsys.readouterr()


# ======================================================================
# Tests de comparar_con_base()
# ======================================================================

class TestCompararConBase:
    def test_prints_comparison(self, mock_pp, capsys):
        with patch("analysis.estadistica.pp", mock_pp):
            desc = estadistica_descriptiva()
            comparar_con_base(desc)

        captured = capsys.readouterr()
        assert "COMPARACION CON BASE POBLACIONAL COLOMBIA" in captured.out
        assert "Schmitt 2007" in captured.out
        assert "Apertura" in captured.out
        assert "IC 95%" in captured.out


# ======================================================================
# Tests de comparar_lomnitz() (Mann-Whitney U)
# ======================================================================

class TestMannWhitneyU:
    def test_prints_table(self, mock_pp, capsys):
        with patch("analysis.estadistica.pp", mock_pp):
            desc = estadistica_descriptiva()
            comparar_lomnitz(desc)

        captured = capsys.readouterr()
        assert "LOMNITZ" in captured.out
        assert "A vs B" in captured.out
        assert "Apertura" in captured.out
        assert "Mann-Whitney" in captured.out or "MANN-WHITNEY" in captured.out


# ======================================================================
# Tests de analizar_perfiles()
# ======================================================================

class TestAnalizarPerfiles:
    def test_returns_complete_dict(self, mock_pp):
        with patch("analysis.estadistica.pp", mock_pp):
            result = analizar_perfiles()

        assert "descriptiva" in result
        assert "lomnitz" in result
        assert "dunbar" in result
        assert "bootstrap" in result

    def test_bootstrap_has_all_factors(self, mock_pp):
        with patch("analysis.estadistica.pp", mock_pp):
            result = analizar_perfiles()

        assert set(result["bootstrap"].keys()) == set(FACTORES)
        for factor in result["bootstrap"]:
            for field in ("ci_low", "ci_high", "media"):
                assert field in result["bootstrap"][factor]


# ======================================================================
# Tests de constantes
# ======================================================================

class TestConstants:
    def test_factores_order(self):
        assert FACTORES == ("O", "C", "E", "A", "N")

    def test_base_colombia_has_all_factors(self):
        assert set(BASE_COLOMBIA.keys()) == set(FACTORES)
        for factor in FACTORES:
            assert 0 <= BASE_COLOMBIA[factor] <= 100

    def test_correlaciones_esperadas_have_ranges(self):
        for par, info in CORRELACIONES_ESPERADAS.items():
            assert len(par) == 2
            assert "rango" in info
            r_min, r_max = info["rango"]
            assert r_min <= r_max
            assert -1 <= r_min <= 1
            assert -1 <= r_max <= 1
            assert "fuente" in info
            assert len(info["fuente"]) > 0


# ======================================================================
# Tests de constantes
# ======================================================================

class TestConstants:
    def test_factores_order(self):
        from analysis.estadistica import FACTORES
        assert FACTORES == ("O", "C", "E", "A", "N")

    def test_base_colombia_has_all_factors(self):
        from analysis.estadistica import BASE_COLOMBIA, FACTORES
        assert set(BASE_COLOMBIA.keys()) == set(FACTORES)
        # Schmitt 2007: Colombia scores normalizados 0-100
        for factor in FACTORES:
            assert 0 <= BASE_COLOMBIA[factor] <= 100

    def test_correlaciones_esperadas_have_ranges(self):
        from analysis.estadistica import CORRELACIONES_ESPERADAS
        for par, info in CORRELACIONES_ESPERADAS.items():
            assert len(par) == 2
            assert "rango" in info
            r_min, r_max = info["rango"]
            assert r_min <= r_max
            assert -1 <= r_min <= 1
            assert -1 <= r_max <= 1
            assert "fuente" in info
            assert len(info["fuente"]) > 0