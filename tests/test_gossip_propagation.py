# -*- coding: utf-8 -*-
"""
tests/test_gossip_propagation.py
================================
Tests para experimentos/gossip_propagation.py (101 statements, 0% -> X%).

Mismo patron que conflict_escalation, manipulation_campaign, empathy_roleplay.
Ademas incluye tests para cargar_agentes_tello() y generar_escena_gossip().
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from experimentos import gossip_propagation as gp


def make_args(**kwargs):
    defaults = {
        "origen": "dona_rosa_tendera",
        "topic": "Don Fernando se robo la plata",
        "veracidad": 0.5,
        "intensidad": 1.0,
        "t_seed": "2026-06-19 08:00",
        "duracion": 24,
        "replicas": 3,
        "export": "experimentos/gossip_propagation",
        "seed_base": 42,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture
def mocks(monkeypatch):
    exp_mock = MagicMock()
    exp_mock.nombre = "test_experiment"
    exp_mock.resumen.return_value = {
        "n_log_entries": 10, "n_gossip_edges": 5, "n_conflictos": 1,
    }
    exp_mock.exportar = MagicMock(return_value=Path("/tmp/exp.zip"))

    escenario_mock = MagicMock()
    dashboard_mock = MagicMock()
    dashboard_mock.render_png.return_value = "/tmp/dash.png"

    monkeypatch.setattr(gp, "Experimento", MagicMock(return_value=exp_mock))
    monkeypatch.setattr(gp, "Escenario", MagicMock(return_value=escenario_mock))
    monkeypatch.setattr(gp, "Dashboard", MagicMock(return_value=dashboard_mock))
    return exp_mock, escenario_mock, dashboard_mock


class TestParsearArgs:
    def test_defaults_sin_argumentos(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["gossip_propagation"])
        args = gp.parsear_args()
        assert args.origen == "dona_rosa_tendera"
        assert args.topic == "Don Fernando se robo la plata"
        assert args.veracidad == 0.5
        assert args.intensidad == 1.0
        assert args.t_seed == "2026-06-19 08:00"
        assert args.duracion == 24
        assert args.replicas == 3

    def test_veracidad_e_intensidad_personalizadas(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", [
            "gp", "--veracidad", "0.8", "--intensidad", "2.5",
        ])
        args = gp.parsear_args()
        assert args.veracidad == 0.8
        assert args.intensidad == 2.5

    def test_topic_personalizado(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["gp", "--topic", "Otro rumor"])
        args = gp.parsear_args()
        assert args.topic == "Otro rumor"


class TestCargarAgentesTello:
    """cargar_agentes_tello() importa geo_tello con fallback."""

    def test_retorna_agentes_y_edificios(self, monkeypatch):
        import geo_tello
        monkeypatch.setattr(geo_tello, "AGENTES_GEO", {"a": {"casa_coords": (0, 0)}})
        monkeypatch.setattr(geo_tello, "EDIFICIOS", {"e1": {"coords": (1, 1)}})
        agentes, edificios = gp.cargar_agentes_tello()
        assert agentes == {"a": {"casa_coords": (0, 0)}}
        assert edificios == {"e1": {"coords": (1, 1)}}

    def test_fallback_si_geo_tello_no_disponible(self, capsys):
        # geo_tello existe, pero podemos forzar el fallback importando
        # un modulo que no existe
        with patch.dict(sys.modules, {"geo_tello": None}):
            agentes, edificios = gp.cargar_agentes_tello()
        assert agentes == {}
        assert edificios == {}
        out = capsys.readouterr().out
        assert "geo_tello.py no disponible" in out


class TestGenerarEscenaGossip:
    """Placeholder — retorna lista vacia hasta integrar con motor."""

    def test_retorna_lista_vacia(self):
        escenas = gp.generar_escena_gossip(
            exp=MagicMock(),
            agentes={},
            edificios={},
            topico="cualquier rumor",
        )
        assert escenas == []


class TestCorrerReplica:
    """Verifica siembra de rumor + metadata."""

    def test_siembra_un_gossip(self, mocks):
        exp_mock, _, _ = mocks
        args = make_args()
        gp.correr_replica(args, replica_id=1, seed=42)
        assert exp_mock.sembrar_gossip.call_count == 1

    def test_gossip_con_args_correctos(self, mocks):
        exp_mock, _, _ = mocks
        args = make_args(origen="dona_prudencia_partera",
                          topic="Rumor X", veracidad=0.7, intensidad=2.0)
        gp.correr_replica(args, replica_id=1, seed=42)
        call = exp_mock.sembrar_gossip.call_args
        assert call.kwargs["origen"] == "dona_prudencia_partera"
        assert call.kwargs["topic"] == "Rumor X"
        assert call.kwargs["veracidad"] == 0.7
        assert call.kwargs["intensidad"] == 2.0
        assert call.kwargs["audiencia"] == "vecinos"

    def test_t_seed_se_interpreta_correctamente(self, mocks):
        exp_mock, _, _ = mocks
        args = make_args(t_seed="2026-06-19 08:00")
        gp.correr_replica(args, replica_id=1, seed=42)
        call = exp_mock.sembrar_gossip.call_args
        assert call.kwargs["t"] == datetime(2026, 6, 19, 8, 0)

    def test_no_inyecta_gossip_transmit(self, mocks):
        # generar_escena_gossip retorna lista vacia -> no hay transmisiones
        exp_mock, _, _ = mocks
        args = make_args()
        gp.correr_replica(args, replica_id=1, seed=42)
        # inyectar_evento NO debe llamarse para gossip_transmit
        gossip_transmit_calls = [
            c for c in exp_mock.inyectar_evento.call_args_list
            if c.kwargs.get("tipo") == "gossip_transmit"
        ]
        assert len(gossip_transmit_calls) == 0

    def test_llama_a_exp_correr(self, mocks):
        exp_mock, _, _ = mocks
        args = make_args()
        gp.correr_replica(args, replica_id=1, seed=42)
        exp_mock.correr.assert_called_once_with(paso_segundos=300)

    def test_metadata_incluye_veracidad_e_intensidad(self, mocks):
        _, _, _ = mocks
        args = make_args(veracidad=0.7, intensidad=2.0)
        gp.correr_replica(args, replica_id=2, seed=1000)
        escenario_call = gp.Escenario.call_args
        metadata = escenario_call.kwargs["metadata"]
        assert metadata["tipo"] == "gossip_propagation"
        assert metadata["veracidad"] == 0.7
        assert metadata["intensidad"] == 2.0
        assert metadata["replica_id"] == 2
        assert metadata["seed"] == 1000

    def test_nombre_experimento_incluye_seed(self, mocks):
        _, _, _ = mocks
        args = make_args()
        gp.correr_replica(args, replica_id=1, seed=42)
        exp_call = gp.Experimento.call_args
        nombre = exp_call.kwargs["nombre"]
        assert "gossip_r1" in nombre


class TestAnalizarResultados:
    def test_no_crashes_con_experimentos(self, mocks, capsys):
        exps = [MagicMock(nombre="gossip_r1", resumen=MagicMock(return_value={
            "n_log_entries": 10, "n_gossip_edges": 5, "n_conflictos": 1,
        }))]
        gp.analizar_resultados(exps)
        out = capsys.readouterr().out
        assert "ANALISIS DE RESULTADOS" in out
        assert "TABLA COMPARATIVA" in out
        assert "gossip_r1" in out
        assert "log entries: 10" in out
        assert "gossip edges: 5" in out


class TestMain:
    def test_main_ejecuta_sin_crash(self, mocks, monkeypatch, capsys):
        monkeypatch.setattr(gp, "parsear_args", make_args)
        gp.main()
        out = capsys.readouterr().out
        assert "EXPERIMENTO FORENSE" in out
        assert "GOSSIP" in out or "CHISME" in out
        assert "EXPERIMENTO COMPLETADO" in out

    def test_main_respeta_replicas(self, mocks, monkeypatch):
        args = make_args(replicas=2)
        monkeypatch.setattr(gp, "parsear_args", lambda: args)
        gp.main()
        exp_mock, _, _ = mocks
        assert exp_mock.correr.call_count == 2

    def test_main_genera_dashboards(self, mocks, monkeypatch):
        args = make_args(replicas=2)
        monkeypatch.setattr(gp, "parsear_args", lambda: args)
        gp.main()
        _, _, dashboard_mock = mocks
        assert dashboard_mock.render_png.call_count == 2