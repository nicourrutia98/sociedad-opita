# -*- coding: utf-8 -*-
"""
tests/test_conflict_escalation.py
==================================
Tests para experimentos/conflict_escalation.py (91 statements, 0% -> X%).

Estrategia:
- parsear_args(): tests de defaults via sys.argv mocking.
- ESTADOS / TRANSICIONES: tests de integridad de las constantes.
- correr_replica(): mocks de Experimento/Escenario/Dashboard.
  Verifica que cada condicion inyecta los eventos esperados.
- analizar(): smoke test con mocks de exp.resumen() y exp.conflictos.
- main(): pipeline completo con mocks.

HALLAZGO: dashboard_reloj NO COMMITEADO pero conflict_escalation.py si.
Misma deuda arquitectonica que red_con_perfiles.py y red_centralidad.py.
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from experimentos import conflict_escalation as ce


# =============================================================================
# Helpers / Fixtures
# =============================================================================

def make_args(**kwargs):
    """Crea un Namespace similar a argparse con defaults del experimento."""
    defaults = {
        "conflicto_id": "linderos_eliecer_rosalio",
        "participantes": "don_eliecer_patron,don_rosalio_rival",
        "duracion": 72,
        "replicas": 4,
        "condiciones": "control,mediacion_cura,gossip_previo,intervencion_institucional",
        "seed_base": 42,
        "export": "experimentos/conflict_escalation",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture
def mock_experimento(monkeypatch):
    """Mockea Experimento y Escenario para no ejecutar simulacion real.

    Retorna una tupla (exp_mock, escenario_mock, dashboard_mock) para que
    los tests puedan inspeccionar el call history de cada uno.

    Usa MagicMock(return_value=...) en vez de lambda, porque el lambda NO
    registra historial de llamadas; MagicMock sí.

    Tambien pre-configura exp_mock.nombre y exp_mock.resumen() para que
    analizar() no falle al formatear strings (ver MagicMock.__format__).
    """
    exp_mock = MagicMock()
    exp_mock.nombre = "test_experiment"
    exp_mock.resumen.return_value = {"n_log_entries": 10}
    exp_mock.conflictos = {}
    exp_mock.exportar = MagicMock(return_value=Path("/tmp/exp.zip"))

    escenario_mock = MagicMock()
    dashboard_mock = MagicMock()
    dashboard_mock.render_png.return_value = "/tmp/dashboard.png"

    monkeypatch.setattr(ce, "Experimento", MagicMock(return_value=exp_mock))
    monkeypatch.setattr(ce, "Escenario", MagicMock(return_value=escenario_mock))
    monkeypatch.setattr(
        ce, "Dashboard", MagicMock(return_value=dashboard_mock),
    )
    return exp_mock, escenario_mock, dashboard_mock


# =============================================================================
# TestConstantes — ESTADOS / TRANSICIONES
# =============================================================================

class TestConstantes:
    def test_estados_tiene_7_items(self):
        assert len(ce.ESTADOS) == 7
        assert set(ce.ESTADOS) == {
            "latente", "incidente", "escalado", "mediado",
            "institucional", "resuelto", "congelado",
        }

    def test_transiciones_cubre_todos_los_estados(self):
        # Cada estado debe tener al menos una transicion definida
        for estado in ce.ESTADOS:
            assert estado in ce.TRANSICIONES, f"Estado '{estado}' sin transiciones"
            assert len(ce.TRANSICIONES[estado]) > 0

    def test_transiciones_destinos_son_estados_validos(self):
        # Cada destino en TRANSICIONES debe ser un ESTADO valido
        for origen, destinos in ce.TRANSICIONES.items():
            for destino in destinos:
                assert destino in ce.ESTADOS, (
                    f"Transicion invalida: {origen} -> {destino}"
                )


# =============================================================================
# TestParsearArgs — parsear_args()
# =============================================================================

class TestParsearArgs:
    """Tests del parser CLI. Mockeamos sys.argv."""

    def test_defaults_sin_argumentos(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["conflict_escalation"])
        args = ce.parsear_args()
        assert args.conflicto_id == "linderos_eliecer_rosalio"
        assert args.duracion == 72
        assert args.replicas == 4
        assert args.seed_base == 42

    def test_conflicto_id_personalizado(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", [
            "conflict_escalation", "--conflicto_id", "otro_conflicto_99",
        ])
        args = ce.parsear_args()
        assert args.conflicto_id == "otro_conflicto_99"

    def test_duracion_personalizada(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", [
            "conflict_escalation", "--duracion", "168",
        ])
        args = ce.parsear_args()
        assert args.duracion == 168

    def test_replicas_personalizadas(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", [
            "conflict_escalation", "--replicas", "10",
        ])
        args = ce.parsear_args()
        assert args.replicas == 10

    def test_condiciones_personalizadas(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", [
            "conflict_escalation",
            "--condiciones", "control,intervencion_institucional",
        ])
        args = ce.parsear_args()
        assert args.condiciones == "control,intervencion_institucional"


# =============================================================================
# TestCorrerReplica — correr_replica() integration con mocks
# =============================================================================

class TestCorrerReplica:
    """Verifica inyeccion de eventos por condicion."""

    def test_condicion_control_inyecta_trigger_24h(self, mock_experimento):
        exp_mock, _, _ = mock_experimento
        args = make_args()
        ce.correr_replica(args, replica_id=1, condicion="control", seed=42)
        # 1 evento: conflicto_trigger a las 24h
        assert exp_mock.inyectar_evento.call_count == 1
        call = exp_mock.inyectar_evento.call_args
        assert call.kwargs["tipo"] == "conflicto_trigger"
        # t debe ser 24h despues de t_inicio
        expected_t = datetime(2026, 6, 19, 6, 0) + timedelta(hours=24)
        assert call.kwargs["t"] == expected_t
        assert call.kwargs["payload"]["disparador"] == "encuentro casual en la tienda"

    def test_condicion_mediacion_inyecta_2_eventos(self, mock_experimento):
        exp_mock, _, _ = mock_experimento
        args = make_args()
        ce.correr_replica(args, replica_id=1, condicion="mediacion_cura", seed=42)
        # 2 eventos: conflicto_trigger (2h) + intervencion (6h)
        assert exp_mock.inyectar_evento.call_count == 2
        calls = exp_mock.inyectar_evento.call_args_list
        tipos = [c.kwargs["tipo"] for c in calls]
        assert "conflicto_trigger" in tipos
        assert "intervencion" in tipos
        # Mediacion del cura
        intervencion = next(c for c in calls if c.kwargs["tipo"] == "intervencion")
        assert intervencion.kwargs["payload"]["intermediario"] == "padre_cecilio_cura"
        assert intervencion.kwargs["payload"]["metodo"] == "dialogo pastoral"

    def test_condicion_gossip_previo_inyecta_gossip_y_trigger(self, mock_experimento):
        exp_mock, _, _ = mock_experimento
        args = make_args()
        ce.correr_replica(args, replica_id=1, condicion="gossip_previo", seed=42)
        # 1 sembrar_gossip + 1 inyectar_evento
        assert exp_mock.sembrar_gossip.call_count == 1
        assert exp_mock.inyectar_evento.call_count == 1
        # El gossip es de dona_rosa_tendera
        gossip_call = exp_mock.sembrar_gossip.call_args
        assert gossip_call.kwargs["origen"] == "dona_rosa_tendera"
        assert "Don Rosalío" in gossip_call.kwargs["topic"]
        assert gossip_call.kwargs["veracidad"] == 0.5
        assert gossip_call.kwargs["intensidad"] == 2.0

    def test_condicion_intervencion_institucional_inyecta_inspector(self, mock_experimento):
        exp_mock, _, _ = mock_experimento
        args = make_args()
        ce.correr_replica(
            args, replica_id=1, condicion="intervencion_institucional", seed=42
        )
        assert exp_mock.inyectar_evento.call_count == 2
        calls = exp_mock.inyectar_evento.call_args_list
        intervencion = next(c for c in calls if c.kwargs["tipo"] == "intervencion")
        assert intervencion.kwargs["payload"]["intermediario"] == "don_sigifredo_inspector"
        assert intervencion.kwargs["payload"]["metodo"] == "acta de inspeccion"

    def test_condicion_desconocida_no_inyecta_eventos(self, mock_experimento):
        exp_mock, _, _ = mock_experimento
        args = make_args()
        ce.correr_replica(args, replica_id=1, condicion="xyz_invalida", seed=42)
        assert exp_mock.inyectar_evento.call_count == 0

    def test_correr_llama_a_exp_correr(self, mock_experimento):
        exp_mock, _, _ = mock_experimento
        args = make_args()
        ce.correr_replica(args, replica_id=1, condicion="control", seed=42)
        exp_mock.correr.assert_called_once_with(paso_segundos=300)

    def test_metadata_incluye_tipo_conflicto(self, mock_experimento):
        # El mock de Escenario es MagicMock(return_value=escenario_mock).
        # Las llamadas se registran en el OUTER mock (ce.Escenario), no en
        # el return_value. Accedemos al OUTER mock via monkeypatch getter.
        _, _, _ = mock_experimento
        args = make_args()
        ce.correr_replica(args, replica_id=1, condicion="control", seed=42)
        escenario_call = ce.Escenario.call_args
        assert escenario_call is not None
        metadata = escenario_call.kwargs["metadata"]
        assert metadata["tipo"] == "conflict_escalation"
        assert metadata["conflicto_id"] == "linderos_eliecer_rosalio"
        assert metadata["condicion"] == "control"
        assert metadata["seed"] == 42

    def test_nombre_experimento_incluye_condicion_y_replica(self, mock_experimento):
        _, _, _ = mock_experimento
        args = make_args()
        ce.correr_replica(args, replica_id=3, condicion="mediacion_cura", seed=1000)
        exp_call = ce.Experimento.call_args
        assert exp_call is not None
        nombre = exp_call.kwargs["nombre"]
        assert "conflict_" in nombre
        assert "linderos_eliecer_rosalio" in nombre
        assert "mediacion_cura" in nombre
        assert "_r3" in nombre


# =============================================================================
# TestAnalizar — analizar() smoke test
# =============================================================================

class TestAnalizar:
    """Verifica formato del output de analisis cruzado."""

    def _make_experimentos_mock(self):
        exp1 = MagicMock()
        exp1.nombre = "conflict_test_control_r1"
        exp1.resumen.return_value = {"n_log_entries": 42}
        exp1.conflictos = {
            "linderos_eliecer_rosalio": {"estado": "escalado"},
        }
        exp2 = MagicMock()
        exp2.nombre = "conflict_test_mediacion_cura_r2"
        exp2.resumen.return_value = {"n_log_entries": 38}
        exp2.conflictos = {
            "linderos_eliecer_rosalio": {"estado": "mediado"},
        }
        return [exp1, exp2]

    def test_no_crashes_con_multiples_experimentos(self, capsys):
        ce.analizar(self._make_experimentos_mock())
        out = capsys.readouterr().out
        assert "ANALISIS: ESCALADA DE CONFLICTO" in out
        assert "control_r1" in out
        assert "mediacion_cura_r2" in out
        # Muestra el estado final
        assert "escalado" in out
        assert "mediado" in out

    def test_experimento_sin_conflictos_muestra_placeholder(self, capsys):
        exp = MagicMock()
        exp.nombre = "test_sin_conflictos"
        exp.resumen.return_value = {"n_log_entries": 10}
        exp.conflictos = {}
        ce.analizar([exp])
        out = capsys.readouterr().out
        assert "sin conflictos" in out

    def test_analizar_lista_vacia_no_crashes(self, capsys):
        ce.analizar([])
        out = capsys.readouterr().out
        assert "ANALISIS: ESCALADA DE CONFLICTO" in out


# =============================================================================
# TestMain — main() CLI pipeline
# =============================================================================

class TestMain:
    """Smoke test del pipeline completo con mocks pesados."""

    def test_main_ejecuta_sin_crash_y_exporta(
        self, mock_experimento, monkeypatch, capsys
    ):
        exp_mock, _, _ = mock_experimento
        # Mockear parsear_args para no depender de sys.argv real
        monkeypatch.setattr(ce, "parsear_args", make_args)

        ce.main()
        out = capsys.readouterr().out
        assert "EXPERIMENTO FORENSE" in out
        assert "EXPERIMENTO COMPLETADO" in out

    def test_main_ajusta_replicas_si_hay_menos_condiciones(
        self, mock_experimento, monkeypatch, capsys
    ):
        exp_mock, _, _ = mock_experimento
        # 2 condiciones, 5 replicas -> solo 2 se corren
        args = make_args(replicas=5, condiciones="control,mediacion_cura")
        monkeypatch.setattr(ce, "parsear_args", lambda: args)

        ce.main()
        # Solo se corren 2 replicas (min de 5 y 2)
        assert exp_mock.correr.call_count == 2
        out = capsys.readouterr().out
        assert "[WARN]" in out
        # El mensaje contiene el numero 5 (de las 5 replicas pedidas)
        assert "5 replicas" in out.replace("á", "a") or "5 r\u00e9plicas" in out

    def test_main_genera_dashboards_para_cada_replica(
        self, mock_experimento, monkeypatch, capsys
    ):
        exp_mock, _, dashboard_mock = mock_experimento
        args = make_args(replicas=2, condiciones="control,mediacion_cura")
        monkeypatch.setattr(ce, "parsear_args", lambda: args)

        ce.main()
        # render_png se llam\u00f3 2 veces (una por replica)
        assert dashboard_mock.render_png.call_count == 2
        out = capsys.readouterr().out
        assert "Dashboard:" in out