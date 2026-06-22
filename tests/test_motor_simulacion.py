# -*- coding: utf-8 -*-
"""
tests/test_motor_simulacion.py — Tests unitarios para motor_simulacion.py
===========================================================================

Cubre:
  - Scene dataclass (defaults)
  - RoundResult dataclass
  - SimulationEngine.__init__ (defaults + inyección de dependencias)
  - SimulationEngine.choose_model (deepseek-chat por defecto, reasoner si usa_reasoner)
  - SimulationEngine.initialize_agents (búsqueda por substring)
  - SimulationEngine.run_round con todo mockeado (PromptBuilder, MultiClient, EngramStore)
  - SimulationEngine.dialogue_round (alterna agentes)

NO hace llamadas reales. Todo está mockeado con unittest.mock.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from motor_simulacion import RoundResult, Scene, SimulationEngine


# ======================================================================
# Tests de dataclasses
# ======================================================================

class TestSceneDataclass:
    def test_minimal_scene(self):
        s = Scene(time="07:00", place="Parque")
        assert s.time == "07:00"
        assert s.place == "Parque"
        assert s.weather == "26°C"  # default
        assert s.people == []  # default
        assert s.context == ""  # default

    def test_full_scene(self):
        s = Scene(
            time="18:30",
            place="Casa del patrón",
            weather="28°C",
            people=["Alcalde", "Subintendente"],
            context="Hace 5 días se rompió la tubería",
        )
        assert s.people == ["Alcalde", "Subintendente"]
        assert "5 días" in s.context


class TestRoundResultDataclass:
    def test_round_result_fields(self):
        scene = Scene(time="07:00", place="X")
        r = RoundResult(
            agent_name="Don Eliécer",
            scene=scene,
            prompt_tokens=100,
            response_tokens=50,
            cost_usd=0.0001,
            content="Hola",
        )
        assert r.agent_name == "Don Eliécer"
        assert r.scene is scene
        assert r.prompt_tokens == 100
        assert r.response_tokens == 50
        assert r.cost_usd == 0.0001
        assert r.content == "Hola"


# ======================================================================
# Helpers: agentes sintéticos y mocks
# ======================================================================

def make_agent(slug: str, name: str, usa_reasoner: bool = False) -> MagicMock:
    """Crea un mock de Agent con los atributos que SimulationEngine necesita."""
    a = MagicMock()
    a.name = name
    a.slug.return_value = slug
    a.topic_identity.return_value = f"agent/{slug}/identity"
    a.raw_bio = f"Bio de {name}"
    a.usa_reasoner = usa_reasoner
    return a


def make_mock_client(content: str = "Respuesta mock", in_tok: int = 100, out_tok: int = 50,
                     cost: float = 0.0001) -> MagicMock:
    """Crea un MultiClient mock que retorna una respuesta fija."""
    client = MagicMock()
    client.chat.return_value = {
        "content": content,
        "reasoning_content": None,
        "usage": {"in": in_tok, "out": out_tok, "total": in_tok + out_tok},
        "model_key": "deepseek:deepseek-chat",
        "cost_usd": cost,
    }
    client.stats.report.return_value = "[mock] usage stats"
    return client


def make_mock_engram() -> MagicMock:
    """EngramStore mockeado — no toca SQLite real."""
    engram = MagicMock()
    engram.db_path = ":memory:"
    engram.save_memory.return_value = None
    engram.search_memories.return_value = []
    return engram


def make_mock_pb(agents: dict[str, MagicMock]) -> MagicMock:
    """PromptBuilder mockeado — retorna prompts vacíos."""
    pb = MagicMock()
    pb.parse_agents.return_value = agents
    pb.build_agent_prompt.return_value = {
        "system": "[system prompt]",
        "user": "[user prompt]",
    }
    return pb


# ======================================================================
# Tests de SimulationEngine.__init__
# ======================================================================

class TestInit:
    def test_defaults_create_real_instances(self):
        """Sin inyeccion, SimulationEngine crea MultiClient, EngramStore y PromptBuilder."""
        # Para no tocar red ni SQLite real, mockeamos las clases externas
        with patch("motor_simulacion.MultiClient") as MockClient, \
             patch("motor_simulacion.PromptBuilder") as MockPB, \
             patch("motor_simulacion.EngramStore") as MockEngram:
            engine = SimulationEngine()
        assert engine.client is MockClient.return_value
        assert engine.engram is MockEngram.return_value
        assert engine.pb is MockPB.return_value
        assert engine.log == []
        assert engine.active_agents == {}

    def test_dependency_injection(self):
        """Si se pasan dependencias, el engine las usa directamente."""
        client = MagicMock()
        engram = MagicMock()
        pb = MagicMock()
        engine = SimulationEngine(client=client, engram=engram, pb=pb, session_id="test-1")
        assert engine.client is client
        assert engine.engram is engram
        assert engine.pb is pb
        assert engine.session_id == "test-1"

    def test_session_id_default_format(self):
        with patch("motor_simulacion.MultiClient"), \
             patch("motor_simulacion.PromptBuilder"), \
             patch("motor_simulacion.EngramStore"):
            engine = SimulationEngine()
        # default = "neiva-sim-<YYYY-MM-DD>"
        assert engine.session_id.startswith("neiva-sim-")
        assert len(engine.session_id) == len("neiva-sim-") + 10  # ISO date


# ======================================================================
# Tests de choose_model()
# ======================================================================

class TestChooseModel:
    def test_default_returns_deepseek_chat(self):
        with patch("motor_simulacion.MultiClient"), \
             patch("motor_simulacion.PromptBuilder"), \
             patch("motor_simulacion.EngramStore"):
            engine = SimulationEngine()
        agent = make_agent("don_eliecer", "Don Eliécer", usa_reasoner=False)
        prov, model = engine.choose_model(agent)
        assert prov == "deepseek"
        assert model == "deepseek-chat"

    def test_reasoner_when_usa_reasoner_true(self):
        with patch("motor_simulacion.MultiClient"), \
             patch("motor_simulacion.PromptBuilder"), \
             patch("motor_simulacion.EngramStore"):
            engine = SimulationEngine()
        agent = make_agent("patricia", "Patricia Losada", usa_reasoner=True)
        prov, model = engine.choose_model(agent)
        assert prov == "deepseek"
        assert model == "deepseek-reasoner"

    def test_missing_usa_reasoner_attr_defaults_false(self):
        """Si el agente no tiene usa_reasoner (no es MagicMock con el attr), debe usar chat."""
        with patch("motor_simulacion.MultiClient"), \
             patch("motor_simulacion.PromptBuilder"), \
             patch("motor_simulacion.EngramStore"):
            engine = SimulationEngine()
        # Agent real sin usa_reasoner
        agent = MagicMock(spec=["name", "slug", "topic_identity", "raw_bio"])
        agent.name = "Test"
        agent.slug.return_value = "test"
        agent.topic_identity.return_value = "agent/test/identity"
        agent.raw_bio = "bio"
        # No tiene usa_reasoner → getattr con default False → deepseek-chat
        prov, model = engine.choose_model(agent)
        assert model == "deepseek-chat"


# ======================================================================
# Tests de initialize_agents()
# ======================================================================

class TestInitializeAgents:
    def test_searches_by_substring(self):
        agent1 = make_agent("don_eliecer_patron", "Don Eliécer")
        agent2 = make_agent("dona_rosa_tendera", "Doña Rosa")
        client = make_mock_client()
        engram = make_mock_engram()
        pb = make_mock_pb({"don_eliecer_patron": agent1, "dona_rosa_tendera": agent2})

        engine = SimulationEngine(client=client, engram=engram, pb=pb)
        # Mockear _save_agent_identity para evitar sqlite real
        engine._save_agent_identity = MagicMock()
        result = engine.initialize_agents(["Don Eliécer", "Doña Rosa"])

        assert "don_eliecer_patron" in result
        assert "dona_rosa_tendera" in result
        assert len(result) == 2
        # _save_agent_identity fue llamado 2 veces (uno por agente)
        assert engine._save_agent_identity.call_count == 2

    def test_warns_on_unknown_agent(self, capsys):
        agent1 = make_agent("don_eliecer_patron", "Don Eliécer")
        pb = make_mock_pb({"don_eliecer_patron": agent1})

        engine = SimulationEngine(
            client=make_mock_client(),
            engram=make_mock_engram(),
            pb=pb,
        )
        engine._save_agent_identity = MagicMock()
        engine.initialize_agents(["Don Eliécer", "Fulano de Tal"])
        captured = capsys.readouterr()
        assert "Fulano de Tal" in captured.out
        assert "[warn]" in captured.out

    def test_saves_identity_on_first_init(self):
        agent1 = make_agent("don_eliecer_patron", "Don Eliécer")
        pb = make_mock_pb({"don_eliecer_patron": agent1})

        engine = SimulationEngine(
            client=make_mock_client(),
            engram=make_mock_engram(),
            pb=pb,
        )
        engine._save_agent_identity = MagicMock()
        engine.initialize_agents(["Don Eliécer"])
        # _save_agent_identity debe haber sido llamado
        engine._save_agent_identity.assert_called_once_with(agent1)
        assert "don_eliecer_patron" in engine.active_agents


# ======================================================================
# Tests de run_round()
# ======================================================================

class TestRunRound:
    def _setup_engine_with_agents(self, agents_dict):
        client = make_mock_client(content="Respuesta mock", in_tok=200, out_tok=100)
        engram = make_mock_engram()
        pb = make_mock_pb(agents_dict)
        engine = SimulationEngine(client=client, engram=engram, pb=pb)
        for slug, agent in agents_dict.items():
            engine.active_agents[slug] = agent
        return engine

    def test_run_round_returns_round_result(self):
        agent = make_agent("don_eliecer_patron", "Don Eliécer")
        engine = self._setup_engine_with_agents({"don_eliecer_patron": agent})

        scene = Scene(time="07:00", place="Finca", weather="26°C",
                      people=["Mayordomo"], context="Después de misa")
        result = engine.run_round("don_eliecer_patron", scene)

        assert isinstance(result, RoundResult)
        assert result.agent_name == "Don Eliécer"
        assert result.content == "Respuesta mock"
        assert result.prompt_tokens == 200
        assert result.response_tokens == 100

    def test_run_round_calls_client_chat_with_correct_args(self):
        agent = make_agent("don_eliecer_patron", "Don Eliécer")
        engine = self._setup_engine_with_agents({"don_eliecer_patron": agent})
        client = engine.client  # el cliente que realmente usa el engine

        scene = Scene(time="07:00", place="X")
        engine.run_round("don_eliecer_patron", scene)

        client.chat.assert_called_once()
        call_kwargs = client.chat.call_args.kwargs
        assert call_kwargs["provider"] == "deepseek"
        assert call_kwargs["model_id"] == "deepseek-chat"
        assert call_kwargs["max_tokens"] == 180  # no reasoner
        assert call_kwargs["temperature"] == 1.3
        # messages es [system, user]
        msgs = call_kwargs["messages"]
        assert len(msgs) == 2
        assert msgs[0]["role"] == "system"
        assert msgs[1]["role"] == "user"

    def test_run_round_uses_reasoner_max_tokens(self):
        """Si el agente usa reasoner, max_tokens debe ser 800."""
        agent = make_agent("patricia", "Patricia", usa_reasoner=True)
        engine = self._setup_engine_with_agents({"patricia": agent})
        client = engine.client

        scene = Scene(time="07:00", place="X")
        engine.run_round("patricia", scene)

        assert client.chat.call_args.kwargs["max_tokens"] == 800

    def test_run_round_appends_to_log(self):
        agent = make_agent("don_eliecer_patron", "Don Eliécer")
        engine = self._setup_engine_with_agents({"don_eliecer_patron": agent})

        scene = Scene(time="07:00", place="Finca")
        assert len(engine.log) == 0
        engine.run_round("don_eliecer_patron", scene)
        assert len(engine.log) == 1
        assert engine.log[0]["agent"] == "Don Eliécer"
        assert "07:00 Finca" in engine.log[0]["scene"]
        assert engine.log[0]["tokens"] == 300  # 200 + 100

    def test_run_round_unknown_agent_raises(self):
        engine = self._setup_engine_with_agents({})
        scene = Scene(time="07:00", place="X")
        with pytest.raises(ValueError, match="not initialized"):
            engine.run_round("nonexistent", scene)

    def test_run_round_saves_memory_by_default(self):
        agent = make_agent("don_eliecer_patron", "Don Eliécer")
        engine = self._setup_engine_with_agents({"don_eliecer_patron": agent})

        scene = Scene(time="07:00", place="Finca")
        engine.run_round("don_eliecer_patron", scene)

        engine.engram.save_memory.assert_called_once()
        call_args = engine.engram.save_memory.call_args
        assert call_args[0][0] is agent  # agent
        assert "07:00 Finca" in call_args[0][1]  # title
        assert "memory" in call_args.kwargs.get("type_", "") or \
               (len(call_args[0]) > 3 and call_args[0][3] == "memory")

    def test_run_round_save_memory_false_skips_save(self):
        agent = make_agent("don_eliecer_patron", "Don Eliécer")
        engine = self._setup_engine_with_agents({"don_eliecer_patron": agent})

        scene = Scene(time="07:00", place="Finca")
        engine.run_round("don_eliecer_patron", scene, save_memory=False)

        engine.engram.save_memory.assert_not_called()


# ======================================================================
# Tests de dialogue_round()
# ======================================================================

class TestDialogueRound:
    def test_dialogue_alternates_agents(self):
        agent_a = make_agent("don_eliecer_patron", "Don Eliécer")
        agent_b = make_agent("dona_rosa_tendera", "Doña Rosa")
        engine = SimulationEngine(
            client=make_mock_client(),
            engram=make_mock_engram(),
            pb=make_mock_pb({"don_eliecer_patron": agent_a, "dona_rosa_tendera": agent_b}),
        )
        engine.active_agents = {
            "don_eliecer_patron": agent_a,
            "dona_rosa_tendera": agent_b,
        }

        scene = Scene(time="07:00", place="Tienda")
        results = engine.dialogue_round("don_eliecer_patron", "dona_rosa_tendera", scene, n_exchanges=2)

        # 2 exchanges × 2 agentes = 4 resultados
        assert len(results) == 4
        # Alternancia: A, B, A, B
        assert results[0].agent_name == "Don Eliécer"
        assert results[1].agent_name == "Doña Rosa"
        assert results[2].agent_name == "Don Eliécer"
        assert results[3].agent_name == "Doña Rosa"

    def test_dialogue_saves_shared_memory_at_end(self):
        agent_a = make_agent("don_eliecer_patron", "Don Eliécer")
        agent_b = make_agent("dona_rosa_tendera", "Doña Rosa")
        engine = SimulationEngine(
            client=make_mock_client(),
            engram=make_mock_engram(),
            pb=make_mock_pb({"don_eliecer_patron": agent_a, "dona_rosa_tendera": agent_b}),
        )
        engine.active_agents = {
            "don_eliecer_patron": agent_a,
            "dona_rosa_tendera": agent_b,
        }

        scene = Scene(time="07:00", place="Tienda")
        engine.dialogue_round("don_eliecer_patron", "dona_rosa_tendera", scene, n_exchanges=1)

        # save_memory debe ser llamado 2 veces (uno por agente) con type_="dialogue"
        assert engine.engram.save_memory.call_count == 2
        for call in engine.engram.save_memory.call_args_list:
            # El último arg posicional o el kwarg type_ debe ser "dialogue"
            args, kwargs = call
            assert kwargs.get("type_") == "dialogue" or \
                   (len(args) >= 4 and args[3] == "dialogue")

    def test_dialogue_includes_previous_response_in_context(self):
        """El context de B debe incluir lo que dijo A en su turno anterior."""
        agent_a = make_agent("don_eliecer_patron", "Don Eliécer")
        agent_b = make_agent("dona_rosa_tendera", "Doña Rosa")

        # client.chat retorna contenido distinto por llamada
        client = MagicMock()
        client.chat.side_effect = [
            {"content": "Turno A1", "usage": {"in": 10, "out": 5},
             "model_key": "deepseek:deepseek-chat", "cost_usd": 0.0001, "reasoning_content": None},
            {"content": "Turno B1", "usage": {"in": 10, "out": 5},
             "model_key": "deepseek:deepseek-chat", "cost_usd": 0.0001, "reasoning_content": None},
        ]
        client.stats.report.return_value = "[mock]"

        pb = MagicMock()
        pb.build_agent_prompt.return_value = {"system": "s", "user": "u"}
        engram = make_mock_engram()

        engine = SimulationEngine(client=client, engram=engram, pb=pb)
        engine.active_agents = {"don_eliecer_patron": agent_a, "dona_rosa_tendera": agent_b}

        scene = Scene(time="07:00", place="Tienda", context="Contexto inicial")
        engine.dialogue_round("don_eliecer_patron", "dona_rosa_tendera", scene, n_exchanges=1)

        # pb.build_agent_prompt es llamado 2 veces (1 por turno)
        assert pb.build_agent_prompt.call_count == 2
        # Primera llamada (turno A): ctx contiene nombre de B (con quien A conversa)
        first_call_kwargs = pb.build_agent_prompt.call_args_list[0].kwargs
        assert "Turno A1" not in first_call_kwargs["scene_context"]
        # Segunda llamada (turno B): ctx contiene lo que dijo A en su turno previo
        second_call_kwargs = pb.build_agent_prompt.call_args_list[1].kwargs
        assert "Turno A1" in second_call_kwargs["scene_context"]
        # El scene_context del turno B menciona a A (no a sí mismo) — el código pone
        # `Conversando con {other_agent.name}`, así que aparece Don Eliécer
        assert "Eliécer" in second_call_kwargs["scene_context"]


# ======================================================================
# Tests de usage_report()
# ======================================================================

class TestUsageReport:
    def test_delegates_to_client_stats(self):
        client = make_mock_client()
        engine = SimulationEngine(
            client=client,
            engram=make_mock_engram(),
            pb=make_mock_pb({}),
        )
        report = engine.usage_report()
        client.stats.report.assert_called_once()
        assert report == "[mock] usage stats"