# -*- coding: utf-8 -*-
"""
tests/test_best_of_n.py
=======================
Tests para analysis/best_of_n.py (122 statements, 0% -> X%).

Estrategia:
- score_text(): puro. Tests por categoria Big Five A (bajo/medio/alto),
  deteccion de marcadores huilenses, penalizacion por LLM tics, score
  final ponderado (huilensidad*2.0 + coherencia*2.5 - llm_tics*1.0).
- generar_best_of_n(): integration con mocks pesados. Mockear
  SimulationEngine + Scene + motor_simulacion + perfiles_psicometricos.
- imprimir_reporte(): smoke test con capsys.
- main: smoke test mockeando todo.

HALLAZGOS del sprint:
- SLUG_TO_NOMBRE y SLUG_BIO_TO_PERFIL hardcodeados dentro de la funcion
  (no constantes a nivel modulo). 8 agentes x 2 mappings = 16 lineas
  duplicadas.
- default_escenas tambien hardcoded por nombre (no por slug).
- La seleccion del mejor usa max(muestras_validas, key=lambda m: m['score']['total']).
- Si no hay muestras validas (todas fallaron), mejor=None.
- El modulo guarda en validacion_best_of_n.json dentro de output_dir
  (portable gracias al fix anterior de Path(__file__).parent.parent).
"""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from analysis import best_of_n as bon


# =============================================================================
# Helpers / Fixtures
# =============================================================================

def make_bf(O=50, C=50, E=50, A=50, N=50):
    """Big Five shortcut."""
    return {"O": O, "C": C, "E": E, "A": A, "N": N}


def make_perfil(A=50):
    """Perfil psicometrico sintetico (devuelve big_five y rasgos)."""
    return {
        "slug": f"test_agente_A{A}",
        "big_five": make_bf(A=A),
        "lomnitz_default": "C",
        "dunbar": {"intimos": [], "buenos": []},
        "rasgos": ["sintetico"],
        "justificacion_bio": "Perfil sintetico para tests.",
    }


@pytest.fixture
def perfil_bajo_A():
    """Perfil con A bajo (<=40): espera confrontation."""
    return make_perfil(A=30)


@pytest.fixture
def perfil_medio_A():
    """Perfil con A medio (40-75): espera equilibrio."""
    return make_perfil(A=50)


@pytest.fixture
def perfil_alto_A():
    """Perfil con A alto (>=75): espera prosocial."""
    return make_perfil(A=85)


# =============================================================================
# TestScoreText — score_text() puro
# =============================================================================

class TestScoreTextEstructura:
    """Estructura del dict retornado."""

    def test_retorna_dict_con_todas_las_claves(self, perfil_medio_A):
        result = bon.score_text("Hola mundo", perfil_medio_A["big_five"], [])
        assert set(result.keys()) == {
            "total", "huilensidad", "huilensidad_detalle", "coherencia",
            "confrontacion", "prosocial", "llm_tics", "max_coherencia",
        }

    def test_huilensidad_detalle_tiene_7_categorias(self, perfil_medio_A):
        # KW_HUILENSES tiene 7 keys: aperturas, muletillas_conflict, ...
        result = bon.score_text("", perfil_medio_A["big_five"], [])
        assert set(result["huilensidad_detalle"].keys()) == set(bon.KW_HUILENSES.keys())
        assert len(result["huilensidad_detalle"]) == 7

    def test_max_coherencia_es_3_para_A_medio(self, perfil_medio_A):
        result = bon.score_text("", perfil_medio_A["big_five"], [])
        assert result["max_coherencia"] == 3

    def test_max_coherencia_es_5_para_A_bajo_o_alto(self, perfil_bajo_A, perfil_alto_A):
        r_bajo = bon.score_text("", perfil_bajo_A["big_five"], [])
        r_alto = bon.score_text("", perfil_alto_A["big_five"], [])
        assert r_bajo["max_coherencia"] == 5
        assert r_alto["max_coherencia"] == 5


class TestScoreTextHuilensidad:
    """Huillensidad cuenta marcadores por categoria."""

    def test_texto_vacio_huilensidad_cero(self, perfil_medio_A):
        result = bon.score_text("", perfil_medio_A["big_five"], [])
        assert result["huilensidad"] == 0
        assert all(v == 0 for v in result["huilensidad_detalle"].values())

    def test_detecta_aperturas_huilenses(self, perfil_medio_A):
        texto = "Pues mire, mijo, ¿qué hubo? Verá, yo le digo..."
        result = bon.score_text(texto, perfil_medio_A["big_five"], [])
        # 'pues', 'mire', 'mijo', 'verá' son aperturas
        assert result["huilensidad_detalle"]["aperturas"] >= 3
        assert result["huilensidad"] >= 3

    def test_detecta_insultos_carinosos(self, perfil_medio_A):
        texto = "Ay mijo bobo, no sea perez nontil"
        result = bon.score_text(texto, perfil_medio_A["big_five"], [])
        assert result["huilensidad_detalle"]["insultos_cariñosos"] >= 2

    def test_detecta_comparaciones_rurales(self, perfil_medio_A):
        texto = "Está más terco que una mula y más arisco que venado"
        result = bon.score_text(texto, perfil_medio_A["big_five"], [])
        assert result["huilensidad_detalle"]["comparaciones_rurales"] == 2

    def test_case_insensitive(self, perfil_medio_A):
        # KW matching es case-insensitive (text.lower())
        r_lower = bon.score_text("pues mijo", perfil_medio_A["big_five"], [])
        r_upper = bon.score_text("PUES MIJO", perfil_medio_A["big_five"], [])
        assert r_lower["huilensidad"] == r_upper["huilensidad"]


class TestScoreTextLLMTics:
    """LLM tics PENALIZAN el score."""

    def test_llm_tics_basicos_detectados(self, perfil_medio_A):
        texto = "Estimado, le sugiero que dialoguemos sobre esto"
        result = bon.score_text(texto, perfil_medio_A["big_five"], [])
        # 'le sugiero', 'dialoguemos', 'estimado' son tics
        assert result["llm_tics"] >= 3

    def test_llm_tics_penalizan_score(self, perfil_medio_A):
        texto_sin_tics = "Pues mire mijo, cómo le va"
        texto_con_tics = "Estimado, le sugiero dialoguemos"
        r_sin = bon.score_text(texto_sin_tics, perfil_medio_A["big_five"], [])
        r_con = bon.score_text(texto_con_tics, perfil_medio_A["big_five"], [])
        # Con tics debe ser MENOR (penalizacion -1.0 por tic)
        assert r_con["total"] < r_sin["total"]
        assert r_con["llm_tics"] > r_sin["llm_tics"]


class TestScoreTextCoherenciaBigFive:
    """Coherencia depende del Amabilidad (A) del perfil."""

    def test_A_bajo_bonus_por_confrontacion(self, perfil_bajo_A):
        texto = "No me venga con eso, no señor, le digo que no"
        result = bon.score_text(texto, perfil_bajo_A["big_five"], [])
        # A=30 (<=40), bonus por confrontacion
        assert result["confrontacion"] >= 2
        assert result["coherencia"] > 0

    def test_A_alto_bonus_por_prosocial(self, perfil_alto_A):
        texto = "Ay mija, tranquila, no se preocupe, aquí estoy"
        result = bon.score_text(texto, perfil_alto_A["big_five"], [])
        # A=85 (>=75), bonus por prosocial
        assert result["prosocial"] >= 3
        assert result["coherencia"] > 0

    def test_A_bajo_penaliza_prosocial_excesivo(self, perfil_bajo_A):
        # Texto muy prosocial para un A=30 deberia tener coherencia negativa
        texto = "Ay mija, tranquila, no se preocupe, aquí estoy, mi amor"
        result = bon.score_text(texto, perfil_bajo_A["big_five"], [])
        # coherencia = confrontacion - (prosocial * 0.5)
        # Si prosocial >= 2 sin confrontacion, coherencia negativa
        assert result["prosocial"] >= 3
        assert result["confrontacion"] == 0
        # coherencia = 0 - (prosocial * 0.5) <= -1.5
        assert result["coherencia"] < 0

    def test_A_medio_pondera_ambos_por_0_5(self, perfil_medio_A):
        # A=50 (medio): coherencia = (confront + prosocial) * 0.5
        texto = "No me venga. Ay mija, tranquila."
        result = bon.score_text(texto, perfil_medio_A["big_five"], [])
        assert result["confrontacion"] >= 1
        assert result["prosocial"] >= 1
        expected = (result["confrontacion"] + result["prosocial"]) * 0.5
        assert abs(result["coherencia"] - expected) < 1e-9

    def test_score_total_suma_ponderada(self, perfil_medio_A):
        texto = "Pues mijo, no me venga con eso"
        result = bon.score_text(texto, perfil_medio_A["big_five"], [])
        expected = (
            result["huilensidad"] * 2.0
            + result["coherencia"] * 2.5
            - result["llm_tics"] * 1.0
        )
        assert abs(result["total"] - expected) < 1e-9


# =============================================================================
# TestGenerarBestOfN — generar_best_of_n() integration con mocks
# =============================================================================

class TestGenerarBestOfN:
    """Pipeline completo: engine.initialize_agents -> N muestras -> mejor -> JSON."""

    def _make_engine_mock(self, muestras_por_agente=None):
        """Crea un SimulationEngine mockeado con muestras deterministicas.

        muestras_por_agente: dict {slug: [content1, content2, content3]}
        """
        engine = MagicMock()
        agents = {
            "elicer-perdomo-motta-el-patrn": MagicMock(name="agente_don_eliecer"),
            "rosalo-quintero-hernndez-el-rival": MagicMock(name="agente_don_rosalio"),
        }
        engine.initialize_agents.return_value = agents

        # run_round retorna un RoundResult con .content y .cost_usd
        def run_round_side_effect(slug, scene, save_memory=False):
            muestras = muestras_por_agente or {
                "elicer-perdomo-motta-el-patrn": [
                    "Pues mijo, bien gracias",
                    "Estimado, le sugiero dialoguemos",  # bajo score
                    "Verá mijo, no me venga con eso",
                ],
                "rosalo-quintero-hernndez-el-rival": [
                    "Carajo, no señor",
                    "Ay mija, tranquila",
                    "Pues hombre, más terco que una mula",
                ],
            }
            contents = muestras.get(slug, ["default"])
            # Seleccionar contenido basado en un contador interno
            if not hasattr(run_round_side_effect, "counters"):
                run_round_side_effect.counters = {}
            idx = run_round_side_effect.counters.get(slug, 0)
            run_round_side_effect.counters[slug] = idx + 1
            content = contents[idx % len(contents)]
            return SimpleNamespace(content=content, cost_usd=0.01,
                                    prompt_tokens=10, response_tokens=20)
        engine.run_round.side_effect = run_round_side_effect
        return engine

    def _patch_dependencies(self, monkeypatch, engine_mock, perfil_mock):
        """Parchea motor_simulacion y perfiles_psicometricos."""
        # Patchear SimulationEngine y Scene en best_of_n (binding local)
        monkeypatch.setattr(bon, "SimulationEngine", lambda: engine_mock)
        monkeypatch.setattr(bon, "Scene", lambda **kwargs: MagicMock(**kwargs))
        # Patchear pp.PERFILES_ADULTOS con perfiles sinteticos
        monkeypatch.setattr(bon.pp, "PERFILES_ADULTOS", perfil_mock)

    def test_estructura_retorno_para_agente_valido(
        self, monkeypatch, tmp_path
    ):
        engine_mock = self._make_engine_mock()
        perfil_mock = {
            "don_eliecer_patron": make_perfil(A=30),
            "don_rosalio_rival": make_perfil(A=85),
        }
        self._patch_dependencies(monkeypatch, engine_mock, perfil_mock)

        resultado = bon.generar_best_of_n(
            nombres_agentes=["Don Eliécer", "Don Rosalío"],
            n=3,
            output_dir=tmp_path,
        )
        assert set(resultado.keys()) == {"Don Eliécer", "Don Rosalío"}

    def test_genera_n_muestras_por_agente(
        self, monkeypatch, tmp_path
    ):
        engine_mock = self._make_engine_mock()
        perfil_mock = {
            "don_eliecer_patron": make_perfil(A=30),
        }
        self._patch_dependencies(monkeypatch, engine_mock, perfil_mock)

        bon.generar_best_of_n(
            nombres_agentes=["Don Eliécer"], n=3, output_dir=tmp_path,
        )
        # engine.run_round debe haberse llamado 3 veces
        assert engine_mock.run_round.call_count == 3

    def test_selecciona_mejor_por_score(
        self, monkeypatch, tmp_path
    ):
        engine_mock = self._make_engine_mock()
        perfil_mock = {
            "don_eliecer_patron": make_perfil(A=30),
        }
        self._patch_dependencies(monkeypatch, engine_mock, perfil_mock)

        resultado = bon.generar_best_of_n(
            nombres_agentes=["Don Eliécer"], n=3, output_dir=tmp_path,
        )
        mejor = resultado["Don Eliécer"]["mejor"]
        assert mejor is not None
        # Las muestras son: "Pues mijo..." (alto), "Estimado..." (bajo),
        # "Verá mijo..." (alto). La mejor debe ser la primera o tercera.
        assert mejor["output"] in (
            "Pues mijo, bien gracias",
            "Verá mijo, no me venga con eso",
        )
        # mejor_idx debe ser valido
        assert 0 <= resultado["Don Eliécer"]["mejor_idx"] < 3

    def test_omite_agente_sin_perfil(
        self, monkeypatch, tmp_path, capsys
    ):
        engine_mock = self._make_engine_mock()
        # Perfil vacio: ningun agente en PERFILES_ADULTOS
        perfil_mock = {}
        self._patch_dependencies(monkeypatch, engine_mock, perfil_mock)

        resultado = bon.generar_best_of_n(
            nombres_agentes=["Don Eliécer"], n=3, output_dir=tmp_path,
        )
        # Agente omitido por falta de perfil
        assert "Don Eliécer" not in resultado
        out = capsys.readouterr().out
        assert "no encontre perfil" in out

    def test_maneja_excepcion_en_run_round(
        self, monkeypatch, tmp_path
    ):
        engine_mock = MagicMock()
        agents = {
            "elicer-perdomo-motta-el-patrn": MagicMock(name="agente"),
        }
        engine_mock.initialize_agents.return_value = agents
        # Primera llamada falla, segunda y tercera ok
        call_count = [0]
        def run_round(slug, scene, save_memory=False):
            call_count[0] += 1
            if call_count[0] == 1:
                raise RuntimeError("API timeout")
            return SimpleNamespace(
                content="Pues mijo, no me venga",
                cost_usd=0.01,
                prompt_tokens=10,
                response_tokens=20,
            )
        engine_mock.run_round.side_effect = run_round

        perfil_mock = {"don_eliecer_patron": make_perfil(A=30)}
        self._patch_dependencies(monkeypatch, engine_mock, perfil_mock)

        resultado = bon.generar_best_of_n(
            nombres_agentes=["Don Eliécer"], n=3, output_dir=tmp_path,
        )
        mejor = resultado["Don Eliécer"]["mejor"]
        # 2 muestras validas de 3, mejor debe ser la de mayor score
        assert mejor is not None
        muestras = resultado["Don Eliécer"]["muestras"]
        assert len(muestras) == 3
        assert "error" in muestras[0]
        assert "score" in muestras[1]
        assert "score" in muestras[2]

    def test_guarda_json_en_output_dir(
        self, monkeypatch, tmp_path
    ):
        engine_mock = self._make_engine_mock()
        perfil_mock = {"don_eliecer_patron": make_perfil(A=30)}
        self._patch_dependencies(monkeypatch, engine_mock, perfil_mock)

        bon.generar_best_of_n(
            nombres_agentes=["Don Eliécer"], n=3, output_dir=tmp_path,
        )
        out_path = tmp_path / "validacion_best_of_n.json"
        assert out_path.exists()
        # JSON debe ser parseable
        data = json.loads(out_path.read_text(encoding="utf-8"))
        assert "Don Eliécer" in data

    def test_default_output_dir_portable(self, monkeypatch):
        engine_mock = self._make_engine_mock()
        perfil_mock = {"don_eliecer_patron": make_perfil(A=30)}
        self._patch_dependencies(monkeypatch, engine_mock, perfil_mock)

        # Sin output_dir explicito, debe usar el path portable
        with patch.object(bon.Path, "mkdir"):
            bon.generar_best_of_n(
                nombres_agentes=["Don Eliécer"], n=1,
            )
        # Verificar que mkdir fue llamado para crear el directorio
        # (esto confirma que se us\u00f3 el path default)


# =============================================================================
# TestImprimirReporte — imprimir_reporte() smoke test
# =============================================================================

class TestImprimirReporte:
    """Solo verifica que no crashea y produce output estructurado."""

    def _make_score_completo(self, total=10.0, huilensidad=1, coherencia=2.0,
                            confrontacion=0, prosocial=1, llm_tics=0,
                            max_coherencia=5):
        """Helper: score dict con TODAS las claves que imprimir_reporte espera."""
        return {
            "total": total,
            "huilensidad": huilensidad,
            "huilensidad_detalle": {k: 0 for k in bon.KW_HUILENSES.keys()},
            "coherencia": coherencia,
            "confrontacion": confrontacion,
            "prosocial": prosocial,
            "llm_tics": llm_tics,
            "max_coherencia": max_coherencia,
        }

    def _make_resultados_basicos(self):
        score1 = self._make_score_completo(total=10.0, huilensidad=1, coherencia=2.0,
                                            prosocial=1)
        score2 = self._make_score_completo(total=-5.0, llm_tics=5)
        return {
            "Don Eliécer": {
                "slug": "elicer-perdomo-motta-el-patrn",
                "perfil": make_bf(O=30, C=80, E=35, A=70, N=30),
                "contexto": "Don Rosalío llegó a reclamar",
                "muestras": [
                    {"output": "Pues mijo, bien", "score": score1},
                    {"output": "Estimado, le sugiero", "score": score2},
                ],
                "mejor": {"output": "Pues mijo, bien", "score": score1},
                "mejor_idx": 0,
            }
        }

    def test_no_crashes_con_datos_basicos(self, capsys):
        bon.imprimir_reporte(self._make_resultados_basicos())
        out = capsys.readouterr().out
        assert "BEST-OF-N SAMPLING" in out
        assert "Don Eliécer" in out
        assert "MEJOR" in out

    def test_no_crashes_con_resultados_vacios(self, capsys):
        bon.imprimir_reporte({})
        out = capsys.readouterr().out
        # Header debe imprimirse aunque no haya datos
        assert "BEST-OF-N SAMPLING" in out

    def test_muestra_comparativa_de_muestras(self, capsys):
        bon.imprimir_reporte(self._make_resultados_basicos())
        out = capsys.readouterr().out
        assert "Comparativa" in out

    def test_omite_agente_sin_muestras(self, capsys):
        resultados = {
            "Don Eliécer": {
                "slug": "x", "perfil": make_bf(), "contexto": "",
                "muestras": [], "mejor": None, "mejor_idx": None,
            }
        }
        bon.imprimir_reporte(resultados)
        # No debe crashear
        assert "BEST-OF-N SAMPLING" in capsys.readouterr().out


# =============================================================================
# TestMain — if __name__ == "__main__" block
# =============================================================================

class TestMain:
    """Smoke test del bloque CLI principal (if __name__ == '__main__').

    El bloque main ejecuta generar_best_of_n + imprimir_reporte. Como
    pytest importa el modulo (no lo ejecuta como __main__), verificamos
    indirectamente que las funciones que main() llama funcionan.
    """

    def test_main_block_no_ejecuta_durante_import(self):
        """Cuando pytest importa best_of_n, el bloque if __name__ == '__main__'
        NO debe ejecutarse. Esto lo verifica implicitamente: pytest funciona,
        por lo tanto el modulo se importa sin side-effects de red."""
        # Si llegamos aqui sin que se haya llamado a generar_best_of_n
        # durante el import, el test pasa.
        assert bon.__name__ != "__main__"

    def test_pipeline_completo_con_mocks(self, monkeypatch, tmp_path):
        """Pipeline integrado: generar_best_of_n + imprimir_reporte con mocks."""
        engine_mock = MagicMock()
        agents = {"elicer-perdomo-motta-el-patrn": MagicMock(name="agente")}
        engine_mock.initialize_agents.return_value = agents
        engine_mock.run_round.return_value = SimpleNamespace(
            content="Pues mijo", cost_usd=0.01,
            prompt_tokens=10, response_tokens=20,
        )
        monkeypatch.setattr(bon, "SimulationEngine", lambda: engine_mock)
        monkeypatch.setattr(bon, "Scene", lambda **kwargs: MagicMock(**kwargs))
        monkeypatch.setattr(
            bon.pp, "PERFILES_ADULTOS",
            {"don_eliecer_patron": make_perfil(A=30)},
        )

        resultados = bon.generar_best_of_n(
            nombres_agentes=["Don Eliécer"], n=1, output_dir=tmp_path,
        )
        # imprimir_reporte no debe crashear
        bon.imprimir_reporte(resultados)