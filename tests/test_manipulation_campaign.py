# -*- coding: utf-8 -*-
"""
tests/test_manipulation_campaign.py
====================================
Tests para experimentos/manipulation_campaign.py (94 statements, 0% -> X%).

Estrategia:
- configurar_campana(): puro, retorna dict segun condicion.
- parsear_args(): tests de defaults + choices validos.
- correr_replica(): mocks de Experimento/Escenario/Dashboard.
  Verifica que cada condicion siembra la cantidad correcta de rumores.
- analizar(): smoke test con mocks.
- main(): pipeline completo con mocks.

HALLAZGO: dashboard_reloj NO COMMITEADO (igual que conflict_escalation).
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from experimentos import manipulation_campaign as mc


def make_args(**kwargs):
    defaults = {
        "target": "don_fernando_alcalde",
        "tipo": "discredito",
        "duracion": 168,
        "replicas": 5,
        "seed_base": 42,
        "export": "experimentos/manipulation_campaign",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture
def mocks(monkeypatch):
    """Mockea Experimento/Escenario/Dashboard."""
    exp_mock = MagicMock()
    exp_mock.nombre = "test_experiment"
    exp_mock.resumen.return_value = {"n_gossip_edges": 5, "n_conflictos": 1}
    exp_mock.conflictos = {}
    exp_mock.exportar = MagicMock(return_value=Path("/tmp/exp.zip"))

    escenario_mock = MagicMock()
    dashboard_mock = MagicMock()
    dashboard_mock.render_png.return_value = "/tmp/dash.png"

    monkeypatch.setattr(mc, "Experimento", MagicMock(return_value=exp_mock))
    monkeypatch.setattr(mc, "Escenario", MagicMock(return_value=escenario_mock))
    monkeypatch.setattr(mc, "Dashboard", MagicMock(return_value=dashboard_mock))
    return exp_mock, escenario_mock, dashboard_mock


class TestParsearArgs:
    def test_defaults_sin_argumentos(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["manipulation_campaign"])
        args = mc.parsear_args()
        assert args.target == "don_fernando_alcalde"
        assert args.tipo == "discredito"
        assert args.duracion == 168
        assert args.replicas == 5
        assert args.seed_base == 42

    def test_target_personalizado(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["mc", "--target", "don_eliecer_patron"])
        args = mc.parsear_args()
        assert args.target == "don_eliecer_patron"

    def test_tipo_personalizado(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["mc", "--tipo", "apoyo"])
        args = mc.parsear_args()
        assert args.tipo == "apoyo"

    def test_tipo_invalido_rechazado(self, monkeypatch):
        # argparse debe rechazar tipos fuera de choices
        monkeypatch.setattr(sys, "argv", ["mc", "--tipo", "hackeo"])
        with pytest.raises(SystemExit):
            mc.parsear_args()


class TestConfigurarCampana:
    """configurar_campana() retorna dict segun condicion."""

    def test_control_sin_recursos(self):
        args = make_args()
        config = mc.configurar_campana(args, "control", seed_offset=1)
        assert config["super_spreaders"] == []
        assert config["rumores_por_dia"] == 0
        assert config["intervenciones"] == []

    def test_bajo_un_super_spreader(self):
        args = make_args()
        config = mc.configurar_campana(args, "bajo", seed_offset=1)
        assert "dona_rosa_tendera" in config["super_spreaders"]
        assert config["rumores_por_dia"] == 1
        assert config["intervenciones"] == []

    def test_medio_tres_super_spreaders(self):
        args = make_args()
        config = mc.configurar_campana(args, "medio", seed_offset=1)
        assert len(config["super_spreaders"]) == 3
        assert config["rumores_por_dia"] == 3
        assert "mesa_redonda_tienda" in config["intervenciones"]

    def test_alto_cinco_super_spreaders(self):
        args = make_args()
        config = mc.configurar_campana(args, "alto", seed_offset=1)
        assert len(config["super_spreaders"]) == 5
        assert config["rumores_por_dia"] == 5
        assert len(config["intervenciones"]) >= 2

    def test_condicion_invalida_retorna_vacio(self):
        args = make_args()
        config = mc.configurar_campana(args, "xyz_invalida", seed_offset=1)
        assert config["super_spreaders"] == []
        assert config["rumores_por_dia"] == 0


class TestCorrerReplica:
    """Verifica siembra de rumores segun condicion."""

    def test_control_no_siembra_rumores(self, mocks):
        exp_mock, _, _ = mocks
        args = make_args()
        mc.correr_replica(args, replica_id=1, condicion="control", seed=42)
        # Sin rumores por dia = 0
        assert exp_mock.sembrar_gossip.call_count == 0

    def test_bajo_siembra_7_rumores_en_7_dias(self, mocks):
        exp_mock, _, _ = mocks
        args = make_args(duracion=168)  # 7 dias * 24h
        mc.correr_replica(args, replica_id=1, condicion="bajo", seed=42)
        # 7 dias * 1 rumor/dia = 7 rumores
        assert exp_mock.sembrar_gossip.call_count == 7

    def test_medio_siembra_21_rumores_en_7_dias(self, mocks):
        exp_mock, _, _ = mocks
        args = make_args(duracion=168)
        mc.correr_replica(args, replica_id=1, condicion="medio", seed=42)
        # 7 dias * 3 rumores/dia = 21
        assert exp_mock.sembrar_gossip.call_count == 21

    def test_alto_siembra_35_rumores_en_7_dias(self, mocks):
        exp_mock, _, _ = mocks
        args = make_args(duracion=168)
        mc.correr_replica(args, replica_id=1, condicion="alto", seed=42)
        # 7 dias * 5 rumores/dia = 35
        assert exp_mock.sembrar_gossip.call_count == 35

    def test_rumor_incluye_target_en_topic(self, mocks):
        exp_mock, _, _ = mocks
        args = make_args(target="don_eliecer_patron", duracion=24)
        mc.correr_replica(args, replica_id=1, condicion="bajo", seed=42)
        call = exp_mock.sembrar_gossip.call_args_list[0]
        topic = call.kwargs["topic"]
        assert "don_eliecer_patron" in topic

    def test_llama_a_exp_correr(self, mocks):
        exp_mock, _, _ = mocks
        args = make_args()
        mc.correr_replica(args, replica_id=1, condicion="control", seed=42)
        exp_mock.correr.assert_called_once()


class TestAnalizar:
    def test_no_crashes_con_multiples_experimentos(self, mocks, capsys):
        exp_mock, _, _ = mocks
        exps = [MagicMock(nombre="manip_target_discredito_control_r1",
                           resumen=MagicMock(return_value={"n_gossip_edges": 0,
                                                            "n_conflictos": 0})),
                MagicMock(nombre="manip_target_discredito_alto_r2",
                           resumen=MagicMock(return_value={"n_gossip_edges": 30,
                                                            "n_conflictos": 2}))]
        mc.analizar(exps, make_args())
        out = capsys.readouterr().out
        assert "ANALISIS" in out
        assert "control_r1" in out
        assert "alto_r2" in out


class TestMain:
    def test_main_usa_4_condiciones(self, mocks, monkeypatch, capsys):
        monkeypatch.setattr(mc, "parsear_args", make_args)
        mc.main()
        out = capsys.readouterr().out
        assert "EXPERIMENTO FORENSE" in out
        assert "EXPERIMENTO COMPLETADO" in out
        assert "control" in out
        assert "bajo" in out
        assert "medio" in out
        assert "alto" in out

    def test_main_ajusta_a_4_condiciones_max(self, mocks, monkeypatch, capsys):
        # Si replicas > 4, se ajusta a 4
        args = make_args(replicas=10)
        monkeypatch.setattr(mc, "parsear_args", lambda: args)
        mc.main()
        # Solo 4 replicas se corren
        exp_mock, _, _ = mocks
        assert exp_mock.correr.call_count == 4

    def test_main_genera_dashboard_por_replica(self, mocks, monkeypatch):
        args = make_args(replicas=2)
        monkeypatch.setattr(mc, "parsear_args", lambda: args)
        mc.main()
        exp_mock, _, dashboard_mock = mocks
        assert dashboard_mock.render_png.call_count == 2