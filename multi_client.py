# -*- coding: utf-8 -*-
# Sociedad Opita — Cliente multi-provider (DeepSeek + 4 fallbacks)
# https://sociedad.opitacode.com (proximo)
#
"""
multi_client.py — Cliente multi-provider para simulación Neiva
================================================================
Soporta 5 providers desde auth.json (opencode):
  - deepseek (direct): deepseek-chat ($0.28/$0.42 por 1M tok)
  - openrouter: 341 modelos (Claude, GPT, DeepSeek, Grok, Gemini, Mistral)
  - google: Gemini 2.0/2.5 flash/pro
  - minimax: MiniMax M3 (nosotros)
  - openai: GPT-4o, GPT-4o-mini (via OAuth)

Carga API keys desde auth.json (la fuente real del operador).
Rotación automática de keys con fallback chain.
Tracking de costos por llamada.

Uso:
    from multi_client import MultiClient
    client = MultiClient()
    response = client.chat(
        provider="deepseek",
        model="deepseek-chat",
        messages=[{"role": "user", "content": "Hola"}]
    )
"""

from __future__ import annotations
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

# ============================================================
# Costos por 1M tokens (USD) — para tracking
# ============================================================
COST_PER_1M_USD = {
    # DeepSeek direct — modelos actuales (deepseek-v4-flash / v4-pro)
    # NOTA: deepseek-chat y deepseek-reasoner se deprecan 2026-07-24
    "deepseek:deepseek-chat":            {"input": 0.28, "output": 0.42},
    "deepseek:deepseek-reasoner":        {"input": 0.55, "output": 2.19},  # thinking mode
    # OpenRouter modelos (markup incluido)
    "openrouter:deepseek/deepseek-chat":          {"input": 0.28, "output": 0.42},
    "openrouter:deepseek/deepseek-reasoner":      {"input": 0.55, "output": 2.19},
    "openrouter:anthropic/claude-3.5-haiku":      {"input": 0.80, "output": 4.00},
    "openrouter:anthropic/claude-3.5-sonnet":     {"input": 3.00, "output": 15.00},
    "openrouter:openai/gpt-4o-mini":              {"input": 0.15, "output": 0.60},
    "openrouter:openai/gpt-4o":                   {"input": 2.50, "output": 10.00},
    "openrouter:google/gemini-2.0-flash-exp:free":{"input": 0.00, "output": 0.00},
    "openrouter:google/gemini-2.5-flash":         {"input": 0.30, "output": 2.50},
    "openrouter:x-ai/grok-2":                     {"input": 2.00, "output": 10.00},
    "openrouter:mistralai/mistral-large-latest":  {"input": 2.00, "output": 6.00},
    # Google direct
    "google:gemini-2.0-flash":          {"input": 0.10, "output": 0.40},
    "google:gemini-2.5-flash":          {"input": 0.30, "output": 2.50},
    "google:gemini-1.5-pro":            {"input": 1.25, "output": 5.00},
    # MiniMax
    "minimax:MiniMax-M3":               {"input": 0.20, "output": 0.80},
}

BASE_URL = {
    "deepseek":  "https://api.deepseek.com/v1",
    "openrouter":"https://openrouter.ai/api/v1",
    "google":    "https://generativelanguage.googleapis.com/v1beta",
    "minimax":   "https://api.minimax.io/v1",
    "openai":    "https://api.openai.com/v1",
}


@dataclass
class UsageStats:
    """Acumulado de uso por sesión de simulación."""
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    errors: list = field(default_factory=list)
    by_model: dict = field(default_factory=dict)

    def add(self, model_key: str, in_tok: int, out_tok: int, cost: float):
        self.calls += 1
        self.input_tokens += in_tok
        self.output_tokens += out_tok
        self.cost_usd += cost
        if model_key not in self.by_model:
            self.by_model[model_key] = {"calls": 0, "in_tok": 0, "out_tok": 0, "cost": 0.0}
        b = self.by_model[model_key]
        b["calls"] += 1
        b["in_tok"] += in_tok
        b["out_tok"] += out_tok
        b["cost"] += cost

    def report(self) -> str:
        lines = [f"Total calls: {self.calls} | Tokens: {self.input_tokens} in / {self.output_tokens} out | Cost: ${self.cost_usd:.4f}"]
        for k, v in self.by_model.items():
            lines.append(f"  {k}: {v['calls']} calls, {v['in_tok']}/{v['out_tok']} tok, ${v['cost']:.4f}")
        return "\n".join(lines)


class MultiClient:
    """Cliente multi-provider. Carga auth.json automáticamente."""

    def __init__(self, auth_path: str = None):
        if auth_path is None:
            auth_path = os.path.join(os.environ.get("USERPROFILE", str(Path.home())),
                                     ".local", "share", "opencode", "auth.json")
        self.auth = self._load_auth(auth_path)
        self.stats = UsageStats()
        # Fallback chain por provider preference
        self.fallback_chains = {
            "deepseek":  ["deepseek"],                  # directo es más barato
            "openrouter":["openrouter"],
            "google":    ["google"],
            "minimax":   ["minimax"],
            "openai":    ["openai"],
        }

    def _load_auth(self, path: str) -> dict:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"auth.json not found at {path}")
        return json.loads(p.read_text(encoding="utf-8"))

    def _get_api_key(self, provider: str) -> str | None:
        """Lee API key de auth.json o env vars."""
        env_key = f"{provider.upper()}_API_KEY"
        if env_key in os.environ:
            return os.environ[env_key]
        entry = self.auth.get(provider)
        if entry and entry.get("type") == "api":
            return entry.get("key")
        if entry and entry.get("type") == "oauth":
            # OAuth no se usa directamente — opencode lo maneja
            return None
        return None

    def _call_deepseek_or_openai_compatible(self, provider: str, model_id: str,
                                             messages: list, max_tokens: int,
                                             temperature: float, timeout: int) -> dict:
        """Endpoint /chat/completions estilo OpenAI."""
        api_key = self._get_api_key(provider)
        if not api_key:
            raise ValueError(f"No API key for provider '{provider}'")

        url = BASE_URL[provider].rstrip("/") + "/chat/completions"

        # DeepSeek reasoner: thinking mode habilitado, temperature ignorada
        is_reasoner = (provider == "deepseek" and model_id == "deepseek-reasoner")
        body_dict = {
            "model": model_id,
            "messages": messages,
            "max_tokens": max_tokens,
            "stream": False,
        }
        if not is_reasoner:
            body_dict["temperature"] = temperature

        # Reasoner requiere extra_body para activar thinking mode
        if is_reasoner:
            body_dict["reasoning_effort"] = "high"
            # El thinking toggle se pasa dentro de extra_body en formato OpenAI

        body = json.dumps(body_dict).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        })
        # OpenRouter recomienda headers adicionales
        if provider == "openrouter":
            req.add_header("HTTP-Referer", "https://neiva-sim.local")
            req.add_header("X-Title", "Neiva Simulation")

        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())

    def _call_google(self, model_id: str, messages: list, max_tokens: int,
                      temperature: float, timeout: int) -> dict:
        """Endpoint Gemini generateContent (formato distinto)."""
        api_key = self._get_api_key("google")
        if not api_key:
            raise ValueError("No API key for google")

        # Gemini espera contents[].parts[].text en vez de messages
        system_parts = []
        user_parts = []
        for m in messages:
            if m["role"] == "system":
                system_parts.append(m["content"])
            else:
                user_parts.append({"role": m["role"], "parts": [{"text": m["content"]}]})

        body = {
            "contents": user_parts,
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temperature},
        }
        if system_parts:
            body["systemInstruction"] = {"parts": [{"text": "\n".join(system_parts)}]}

        url = f"{BASE_URL['google']}/models/{model_id}:generateContent?key={api_key}"
        req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers={
            "Content-Type": "application/json",
        })
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
        # Adaptar a formato OpenAI-like
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            usage = data.get("usageMetadata", {})
            return {
                "choices": [{"message": {"role": "assistant", "content": text},
                             "finish_reason": "stop"}],
                "usage": {
                    "prompt_tokens": usage.get("promptTokenCount", 0),
                    "completion_tokens": usage.get("candidatesTokenCount", 0),
                    "total_tokens": usage.get("totalTokenCount", 0),
                },
                "_native": data,
            }
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Unexpected Google response: {data}") from e

    def chat(self, provider: str, model_id: str, messages: list,
             max_tokens: int = 500, temperature: float = 0.8,
             timeout: int = 90) -> dict:
        """
        Llama a un LLM. Retorna dict con:
          - content: str (texto de respuesta)
          - usage: {prompt_tokens, completion_tokens, total_tokens}
          - model_key: str (para tracking de costos)
          - cost_usd: float
        """
        if provider == "google":
            resp = self._call_google(model_id, messages, max_tokens, temperature, timeout)
        else:
            resp = self._call_deepseek_or_openai_compatible(
                provider, model_id, messages, max_tokens, temperature, timeout)

        message = resp["choices"][0]["message"]
        content = message["content"]
        # DeepSeek reasoner expone el razonamiento en reasoning_content.
        # Si está vacío o no existe, lo dejamos como None.
        reasoning_content = message.get("reasoning_content") or None

        usage = resp.get("usage", {})
        in_tok = usage.get("prompt_tokens", 0)
        out_tok = usage.get("completion_tokens", 0)

        model_key = f"{provider}:{model_id}"
        cost_table = COST_PER_1M_USD.get(model_key, {})
        cost = (in_tok * cost_table.get("input", 0) + out_tok * cost_table.get("output", 0)) / 1_000_000

        self.stats.add(model_key, in_tok, out_tok, cost)

        return {
            "content": content,
            "reasoning_content": reasoning_content,
            "usage": {"in": in_tok, "out": out_tok, "total": in_tok + out_tok},
            "model_key": model_key,
            "cost_usd": cost,
        }

    def chat_with_fallback(self, primary: tuple[str, str], messages: list,
                            fallback_chain: list[tuple[str, str]] = None,
                            max_tokens: int = 500, temperature: float = 0.8) -> dict:
        """
        Llama con rotación. primary = (provider, model_id).
        Si falla, intenta fallbacks en orden.
        """
        chain = [primary] + (fallback_chain or [])
        last_err = None
        for prov, mdl in chain:
            try:
                return self.chat(prov, mdl, messages, max_tokens, temperature)
            except Exception as e:
                last_err = e
                self.stats.errors.append(f"{prov}:{mdl} -> {e}")
                continue
        raise RuntimeError(f"All models failed. Last: {last_err}")


# ============================================================
# DEMO
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("MultiClient — demo (sin hacer llamada real)")
    print("=" * 60)
    c = MultiClient()
    print(f"Keys cargadas de: {os.path.join(os.environ.get('USERPROFILE'), '.local', 'share', 'opencode', 'auth.json')}")
    print()
    print("Providers disponibles:")
    for prov in ["deepseek", "openrouter", "google", "minimax", "openai"]:
        k = c._get_api_key(prov)
        if k:
            print(f"  {prov:12s}: {k[:18]}... ({len(k)} chars)")
        else:
            print(f"  {prov:12s}: (no key)")
    print()
    print("Costos por 1M tokens (USD):")
    for k, v in COST_PER_1M_USD.items():
        print(f"  {k:55s} in=${v['input']:.2f}  out=${v['output']:.2f}")