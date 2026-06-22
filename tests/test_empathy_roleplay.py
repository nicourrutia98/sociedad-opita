# -*- coding: utf-8 -*-
"""
tests/test_empathy_roleplay.py
==============================
Tests para experimentos/empathy_roleplay.py (86 statements, 0% -> X%).

Mismo patron que conflict_escalation y manipulation_campaign.
"""

import argparse
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from experimentos import empathy_roleplay as er


def make_args(**kwargs):
    defaults = {
        "dilema": "inundacion_rosalio",
        "sujeto": "don_eliecer_patron",
        "objeto": "don_rosalio_rival",
        "duracion": 96,
        "replicas": 4,
        "seed_base": 42,
        "export": "experimentos/empathy_roleplay",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture
def mocks(monkeypatch):
    exp_mock = MagicMock()
    exp_mock.nombre = "test_experiment"
    exp_mock.resumen.return_value = {"n_gossip_edges": 3}
    exp_mock.conflictos = {}
    exp_mock.exportar = MagicMock(return_value=Path("/tmp/exp.zip"))

    escenario_mock = MagicMock()
    dashboard_mock = MagicMock()
    dashboard_mock.render_png.return_value = "/tmp/dash.png"

    monkeypatch.setattr(er, "Experimento", MagicMock(return_value=exp_mock))
    monkeypatch.setattr(er, "Escenario", MagicMock(return_value=escenario_mock))
    monkeypatch.setattr(er, "Dashboard", MagicMock(return_value=dashboard_mock))
    return exp_mock, escenario_mock, dashboard_mock


class TestParsearArgs:
    def test_defaults_sin_argumentos(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["empathy_roleplay"])
        args = er.parsear_args()
        assert args.dilema == "inundacion_rosalio"
        assert args.sujeto == "don_eliecer_patron"
        assert args.objeto == "don_rosalio_rival"
        assert args.duracion == 96
        assert args.replicas == 4

    def test_dilema_personalizado(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["er", "--dilema", "muerte_familiar"])
        args = er.parsear_args()
        assert args.dilema == "muerte_familiar"

    def test_sujeto_personalizado(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["er", "--sujeto", "dona_prudencia_partera"])
        args = er.parsear_args()
        assert args.sujeto == "dona_prudencia_partera"


class TestCorrerReplica:
    """Verifica inyeccion de eventos segun condicion."""

    def test_control_solo_snapshot(self, mocks):
        exp_mock, _, _ = mocks
        args = make_args()
        er.correr_replica(args, replica_id=1, condicion="control", seed=42)
        # Solo snapshots, sin rumores ni eventos
        assert exp_mock.sembrar_gossip.call_count == 0
        assert exp_mock.inyectar_evento.call_count == 0

    def test_inundacion_leve_1_rumor_1_evento(self, mocks):
        exp_mock, _, _ = mocks
        args = make_args()
        er.correr_replica(args, replica_id=1, condicion="inundacion_leve", seed=42)
        assert exp_mock.sembrar_gossip.call_count == 1
        assert exp_mock.inyectar_evento.call_count == 1

    def test_inundacion_severa_1_rumor_1_evento(self, mocks):
        exp_mock, _, _ = mocks
        args = make_args()
        er.correr_replica(args, replica_id=1, condicion="inundacion_severa", seed=42)
        assert exp_mock.sembrar_gossip.call_count == 1
        assert exp_mock.inyectar_evento.call_count == 1

    def test_presion_social_1_rumor_2_intervenciones(self, mocks):
        exp_mock, _, _ = mocks
        args = make_args()
        er.correr_replica(args, replica_id=1, condicion="presion_social", seed=42)
        assert exp_mock.sembrar_gossip.call_count == 1
        assert exp_mock.inyectar_evento.call_count == 2
        # Verificar que los 2 intermediarios son cura + personera
        calls = exp_mock.inyectar_evento.call_args_list
        intermediarios = [c.kwargs["payload"]["intermediario"] for c in calls]
        assert "padre_cecilio_cura" in intermediarios
        assert "beatriz_personera" in intermediarios

    def test_condicion_invalida_solo_snapshots(self, mocks):
        exp_mock, _, _ = mocks
        args = make_args()
        er.correr_replica(args, replica_id=1, condicion="xyz", seed=42)
        assert exp_mock.sembrar_gossip.call_count == 0
        assert exp_mock.inyectar_evento.call_count == 0

    def test_rumor_incluye_objeto(self, mocks):
        exp_mock, _, _ = mocks
        args = make_args(objeto="don_rosalio_rival")
        er.correr_replica(args, replica_id=1, condicion="inundacion_leve", seed=42)
        call = exp_mock.sembrar_gossip.call_args
        topic = call.kwargs["topic"]
        assert "Rosalío" in topic

    def test_llama_correr_con_paso_600(self, mocks):
        exp_mock, _, _ = mocks
        args = make_args()
        er.correr_replica(args, replica_id=1, condicion="control", seed=42)
        exp_mock.correr.assert_called_once_with(paso_segundos=600)

    def test_metadata_tipo_empathy(self, mocks):
        _, _, _ = mocks
        args = make_args()
        er.correr_replica(args, replica_id=1, condicion="control", seed=42)
        escenario_call = er.Escenario.call_args
        metadata = escenario_call.kwargs["metadata"]
        assert metadata["tipo"] == "empathy_roleplay"
        assert metadata["dilema"] == "inundacion_rosalio"
        assert metadata["sujeto"] == "don_eliecer_patron"
        assert metadata["objeto"] == "don_rosalio_rival"


class TestAnalizar:
    def test_no_crashes_con_experimentos(self, mocks, capsys):
        args = make_args()
        exps = [MagicMock(nombre="empathy_test_r1",
                           resumen=MagicMock(return_value={"n_gossip_edges": 5}))]
        er.analizar(exps, args)
        out = capsys.readouterr().out
        assert "ANALISIS" in out
        assert "EMPATIA" in out
        assert "inundacion_rosalio" in out


class TestMain:
    def test_main_ejecuta_sin_crash(self, mocks, monkeypatch, capsys):
        monkeypatch.setattr(er, "parsear_args", make_args)
        er.main()
        out = capsys.readouterr().out
        assert "EXPERIMENTO FORENSE" in out
        assert "EMPATIA" in out
        assert "EXPERIMENTO COMPLETADO" in out

    def test_main_respeta_replicas(self, mocks, monkeypatch):
        args = make_args(replicas=3)
        monkeypatch.setattr(er, "parsear_args", lambda: args)
        er.main()
        exp_mock, _, _ = mocks
        assert exp_mock.correr.call_count == 3

    def test_main_genera_dashboards(self, mocks, monkeypatch):
        args = make_args(replicas=2)
        monkeypatch.setattr(er, "parsear_args", lambda: args)
        er.main()
        _, _, dashboard_mock = mocks
        assert dashboard_mock.render_png.call_count == 2