# -*- coding: utf-8 -*-
"""
tests/test_multi_client.py — Tests unitarios para multi_client.py
=================================================================

Cubre:
  - UsageStats dataclass (acumulación + reporte)
  - MultiClient carga auth.json
  - MultiClient._get_api_key (env > auth.json)
  - MultiClient.chat() con DeepSeek / OpenAI-compatible mockeado
  - MultiClient.chat() con Google mockeado
  - MultiClient.chat() calcula costo correctamente
  - MultiClient.chat_with_fallback() rota en error
  - MultiClient maneja provider desconocido

NO hace llamadas reales. Todo el HTTP está mockeado con unittest.mock.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from multi_client import (
    BASE_URL,
    COST_PER_1M_USD,
    MultiClient,
    UsageStats,
)


# ======================================================================
# Fixtures
# ======================================================================

@pytest.fixture
def auth_json(tmp_path: Path) -> Path:
    """Crea un auth.json sintético con keys para DeepSeek y Google."""
    p = tmp_path / "auth.json"
    p.write_text(json.dumps({
        "deepseek": {"type": "api", "key": "sk-test-deepseek-1234567890"},
        "google": {"type": "api", "key": "AIza-test-google-1234567890"},
        "openrouter": {"type": "oauth"},  # oauth no debe leerse como key
        "minimax": None,  # provider sin entry
    }), encoding="utf-8")
    return p


@pytest.fixture
def client(auth_json: Path) -> MultiClient:
    return MultiClient(auth_path=str(auth_json))


# ======================================================================
# Tests de UsageStats (dataclass sin red)
# ======================================================================

class TestUsageStats:
    def test_empty_stats(self):
        s = UsageStats()
        assert s.calls == 0
        assert s.input_tokens == 0
        assert s.output_tokens == 0
        assert s.cost_usd == 0.0
        assert s.errors == []
        assert s.by_model == {}

    def test_add_accumulates(self):
        s = UsageStats()
        s.add("deepseek:deepseek-chat", in_tok=1000, out_tok=500, cost=0.001)
        s.add("deepseek:deepseek-chat", in_tok=2000, out_tok=1000, cost=0.002)
        assert s.calls == 2
        assert s.input_tokens == 3000
        assert s.output_tokens == 1500
        assert s.cost_usd == pytest.approx(0.003)

    def test_add_groups_by_model(self):
        s = UsageStats()
        s.add("deepseek:deepseek-chat", 100, 50, 0.001)
        s.add("google:gemini-2.5-flash", 200, 100, 0.002)
        assert "deepseek:deepseek-chat" in s.by_model
        assert "google:gemini-2.5-flash" in s.by_model
        assert s.by_model["deepseek:deepseek-chat"]["calls"] == 1
        assert s.by_model["google:gemini-2.5-flash"]["calls"] == 1

    def test_report_includes_totals_and_breakdown(self):
        s = UsageStats()
        s.add("deepseek:deepseek-chat", 1000, 500, 0.001)
        report = s.report()
        assert "Total calls: 1" in report
        assert "1000 in" in report
        assert "500 out" in report
        assert "deepseek:deepseek-chat" in report


# ======================================================================
# Tests de carga de auth.json
# ======================================================================

class TestLoadAuth:
    def test_loads_valid_json(self, auth_json: Path):
        client = MultiClient(auth_path=str(auth_json))
        assert "deepseek" in client.auth
        assert client.auth["deepseek"]["key"] == "sk-test-deepseek-1234567890"

    def test_raises_when_auth_missing(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError, match="auth.json not found"):
            MultiClient(auth_path=str(tmp_path / "nope.json"))


# ======================================================================
# Tests de _get_api_key
# ======================================================================

class TestGetApiKey:
    def test_reads_from_auth_json(self, client: MultiClient, monkeypatch):
        # Limpiar env vars para que el test lea de auth.json
        for var in ["DEEPSEEK_API_KEY", "GOOGLE_API_KEY", "OPENROUTER_API_KEY", "MINIMAX_API_KEY"]:
            monkeypatch.delenv(var, raising=False)
        assert client._get_api_key("deepseek") == "sk-test-deepseek-1234567890"

    def test_env_var_takes_precedence(self, client: MultiClient, monkeypatch):
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-from-env-9999")
        assert client._get_api_key("deepseek") == "sk-from-env-9999"

    def test_returns_none_for_unknown_provider(self, client: MultiClient, monkeypatch):
        monkeypatch.delenv("NONEXISTENT_PROVIDER_API_KEY", raising=False)
        assert client._get_api_key("nonexistent_provider") is None

    def test_oauth_returns_none(self, client: MultiClient, monkeypatch):
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        # openrouter tiene type=oauth, no debe retornar key usable
        assert client._get_api_key("openrouter") is None

    def test_null_entry_returns_none(self, client: MultiClient, monkeypatch):
        monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
        assert client._get_api_key("minimax") is None


# ======================================================================
# Tests de chat() con DeepSeek (mock HTTP)
# ======================================================================

class TestChatDeepSeek:
    def _deepseek_response(self, content: str = "Hola", in_tok: int = 100, out_tok: int = 50):
        return {
            "choices": [{"message": {"role": "assistant", "content": content}}],
            "usage": {
                "prompt_tokens": in_tok,
                "completion_tokens": out_tok,
                "total_tokens": in_tok + out_tok,
            },
        }

    def test_chat_returns_content_and_cost(self, client: MultiClient):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(
            self._deepseek_response("Hola, ¿qué tal?", 100, 50)
        ).encode("utf-8")
        mock_resp.__enter__ = lambda self_: mock_resp
        mock_resp.__exit__ = lambda self_, *args: None

        with patch("multi_client.urllib.request.urlopen", return_value=mock_resp):
            r = client.chat(
                provider="deepseek",
                model_id="deepseek-chat",
                messages=[{"role": "user", "content": "Hola"}],
            )

        assert r["content"] == "Hola, ¿qué tal?"
        # deepseek-chat: $0.28/1M in, $0.42/1M out
        # 100 * 0.28 / 1e6 + 50 * 0.42 / 1e6 = 4.9e-5
        assert r["cost_usd"] == pytest.approx(
            100 * 0.28 / 1_000_000 + 50 * 0.42 / 1_000_000
        )
        assert r["usage"]["in"] == 100
        assert r["usage"]["out"] == 50
        assert r["model_key"] == "deepseek:deepseek-chat"

    def test_chat_updates_stats(self, client: MultiClient):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(
            self._deepseek_response("Hola", 200, 100)
        ).encode("utf-8")
        mock_resp.__enter__ = lambda self_: mock_resp
        mock_resp.__exit__ = lambda self_, *args: None

        with patch("multi_client.urllib.request.urlopen", return_value=mock_resp):
            client.chat("deepseek", "deepseek-chat",
                        messages=[{"role": "user", "content": "x"}])

        assert client.stats.calls == 1
        assert client.stats.input_tokens == 200
        assert client.stats.output_tokens == 100

    def test_chat_without_api_key_raises(self, client: MultiClient, monkeypatch):
        # Forzar que deepseek no tenga key
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        client.auth.pop("deepseek", None)
        with pytest.raises(ValueError, match="No API key"):
            client.chat("deepseek", "deepseek-chat", messages=[])

    def test_chat_uses_openai_compatible_endpoint(self, client: MultiClient):
        """Verifica que el URL es el de DeepSeek (no Google)."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(
            self._deepseek_response()
        ).encode("utf-8")
        mock_resp.__enter__ = lambda self_: mock_resp
        mock_resp.__exit__ = lambda self_, *args: None

        with patch("multi_client.urllib.request.urlopen", return_value=mock_resp) as m:
            client.chat("deepseek", "deepseek-chat", messages=[])
            called_url = m.call_args[0][0].full_url
        assert called_url.startswith("https://api.deepseek.com/v1/chat/completions")

    def test_chat_reasoner_sets_extra_body(self, client: MultiClient):
        """deepseek-reasoner debe activar reasoning_effort='high' y NO temperature."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(self._deepseek_response()).encode("utf-8")
        mock_resp.__enter__ = lambda self_: mock_resp
        mock_resp.__exit__ = lambda self_, *args: None

        with patch("multi_client.urllib.request.urlopen", return_value=mock_resp) as m:
            client.chat("deepseek", "deepseek-reasoner",
                        messages=[{"role": "user", "content": "x"}],
                        temperature=0.5)
            # Inspeccionar el body enviado
            request_obj = m.call_args[0][0]
            body = json.loads(request_obj.data.decode("utf-8"))
            assert body["model"] == "deepseek-reasoner"
            assert body["reasoning_effort"] == "high"
            assert "temperature" not in body  # ignorada en reasoner

    def test_chat_openai_compatible(self, auth_json: Path, monkeypatch):
        """Un provider openai-compatible (openrouter) debe usar el mismo path."""
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        # Agregar key de openrouter al auth y recrear el cliente
        auth_data = json.loads(auth_json.read_text())
        auth_data["openrouter"] = {"type": "api", "key": "sk-or-test-xxx"}
        auth_json.write_text(json.dumps(auth_data))
        client = MultiClient(auth_path=str(auth_json))

        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(
            self._deepseek_response()
        ).encode("utf-8")
        mock_resp.__enter__ = lambda self_: mock_resp
        mock_resp.__exit__ = lambda self_, *args: None

        with patch("multi_client.urllib.request.urlopen", return_value=mock_resp) as m:
            client.chat("openrouter", "openai/gpt-4o-mini",
                        messages=[{"role": "user", "content": "x"}])
            called_url = m.call_args[0][0].full_url
        assert called_url.startswith("https://openrouter.ai/api/v1/")


# ======================================================================
# Tests de chat() con Google (formato Gemini)
# ======================================================================

class TestChatGoogle:
    def _google_response(self, text: str = "Respuesta", in_tok: int = 50, out_tok: int = 25):
        return {
            "candidates": [
                {"content": {"parts": [{"text": text}], "role": "model"}}
            ],
            "usageMetadata": {
                "promptTokenCount": in_tok,
                "candidatesTokenCount": out_tok,
                "totalTokenCount": in_tok + out_tok,
            },
        }

    def test_chat_google_adapts_response(self, client: MultiClient):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(
            self._google_response("Hola desde Gemini", 80, 40)
        ).encode("utf-8")
        mock_resp.__enter__ = lambda self_: mock_resp
        mock_resp.__exit__ = lambda self_, *args: None

        with patch("multi_client.urllib.request.urlopen", return_value=mock_resp) as m:
            r = client.chat("google", "gemini-2.5-flash",
                            messages=[
                                {"role": "system", "content": "Eres un asistente"},
                                {"role": "user", "content": "Hola"},
                            ])

        assert r["content"] == "Hola desde Gemini"
        assert r["usage"]["in"] == 80
        assert r["usage"]["out"] == 40
        # gemini-2.5-flash: $0.30/1M in, $2.50/1M out
        assert r["cost_usd"] == pytest.approx(
            80 * 0.30 / 1_000_000 + 40 * 2.50 / 1_000_000
        )

    def test_chat_google_splits_system_messages(self, client: MultiClient):
        """Verifica que system messages se envían como systemInstruction, contents solo user."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(self._google_response()).encode("utf-8")
        mock_resp.__enter__ = lambda self_: mock_resp
        mock_resp.__exit__ = lambda self_, *args: None

        with patch("multi_client.urllib.request.urlopen", return_value=mock_resp) as m:
            client.chat("google", "gemini-2.0-flash", messages=[
                {"role": "system", "content": "Prompt del sistema"},
                {"role": "user", "content": "Pregunta"},
            ])
            body = json.loads(m.call_args[0][0].data.decode("utf-8"))

        assert "systemInstruction" in body
        assert "Prompt del sistema" in body["systemInstruction"]["parts"][0]["text"]
        # user messages van como contents
        assert len(body["contents"]) == 1
        assert body["contents"][0]["parts"][0]["text"] == "Pregunta"

    def test_chat_google_unexpected_response_raises(self, client: MultiClient):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"unexpected": "shape"}).encode("utf-8")
        mock_resp.__enter__ = lambda self_: mock_resp
        mock_resp.__exit__ = lambda self_, *args: None

        with patch("multi_client.urllib.request.urlopen", return_value=mock_resp):
            with pytest.raises(RuntimeError, match="Unexpected Google response"):
                client.chat("google", "gemini-2.5-flash", messages=[])


# ======================================================================
# Tests de chat_with_fallback()
# ======================================================================

class TestChatWithFallback:
    def test_returns_primary_when_succeeds(self, client: MultiClient):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "choices": [{"message": {"role": "assistant", "content": "primary"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        }).encode("utf-8")
        mock_resp.__enter__ = lambda self_: mock_resp
        mock_resp.__exit__ = lambda self_, *args: None

        with patch("multi_client.urllib.request.urlopen", return_value=mock_resp):
            r = client.chat_with_fallback(
                primary=("deepseek", "deepseek-chat"),
                messages=[{"role": "user", "content": "x"}],
            )
        assert r["content"] == "primary"

    def test_falls_back_on_error(self, client: MultiClient):
        """Si primary falla, debe intentar el fallback y reintentar."""
        # Mockear _get_api_key para que ambos providers tengan key
        client.auth["openrouter"] = {"type": "api", "key": "sk-or-test"}

        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "choices": [{"message": {"role": "assistant", "content": "fallback"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        }).encode("utf-8")
        mock_resp.__enter__ = lambda self_: mock_resp
        mock_resp.__exit__ = lambda self_, *args: None

        call_count = {"n": 0}

        def fake_urlopen(req, **kwargs):
            call_count["n"] += 1
            if "deepseek" in req.full_url:
                raise RuntimeError("deepseek rate limit")
            return mock_resp

        with patch("multi_client.urllib.request.urlopen", side_effect=fake_urlopen):
            r = client.chat_with_fallback(
                primary=("deepseek", "deepseek-chat"),
                fallback_chain=[("openrouter", "openai/gpt-4o-mini")],
                messages=[{"role": "user", "content": "x"}],
            )

        assert r["content"] == "fallback"
        assert call_count["n"] == 2  # primary failed, fallback succeeded

    def test_all_fail_raises(self, client: MultiClient):
        with patch("multi_client.urllib.request.urlopen",
                   side_effect=RuntimeError("network error")):
            with pytest.raises(RuntimeError, match="All models failed"):
                client.chat_with_fallback(
                    primary=("deepseek", "deepseek-chat"),
                    fallback_chain=[("openrouter", "openai/gpt-4o-mini")],
                    messages=[{"role": "user", "content": "x"}],
                )
        # El error queda registrado en stats
        assert any("deepseek" in e for e in client.stats.errors)


# ======================================================================
# Tests de configuración (constantes)
# ======================================================================

class TestConstants:
    def test_cost_table_has_all_providers(self):
        """Las keys de COST_PER_1M_USD deben matchear el formato provider:model."""
        for key in COST_PER_1M_USD:
            assert ":" in key, f"Key '{key}' debe tener formato provider:model"
            assert "input" in COST_PER_1M_USD[key]
            assert "output" in COST_PER_1M_USD[key]

    def test_base_url_has_all_providers(self):
        for prov in ["deepseek", "openrouter", "google", "minimax", "openai"]:
            assert prov in BASE_URL
            assert BASE_URL[prov].startswith("https://")

    def test_google_models_use_free_tier_if_specified(self):
        """Gemini 2.0 flash exp free debe tener costo 0."""
        key = "openrouter:google/gemini-2.0-flash-exp:free"
        assert key in COST_PER_1M_USD
        assert COST_PER_1M_USD[key]["input"] == 0.0
        assert COST_PER_1M_USD[key]["output"] == 0.0