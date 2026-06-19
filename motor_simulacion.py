# -*- coding: utf-8 -*-
# Sociedad Opita — Motor LLM con max_tokens=180, temp=0.7
# https://sociedad.opitacode.com (proximo)
#
"""
motor_simulacion.py — Motor de simulación de Neiva
===================================================
Orquesta el ciclo diario de los agentes. Cada agente:
  1. Construye su prompt (prompt_builder)
  2. Llama al LLM (multi_client)
  3. Recibe acción/diálogo
  4. Guarda recuerdo en engram

Ciclo diario:
  06:00 DESPERTAR → 07:00 TINTO → 09:00 TRABAJO → 12:00 ALMUERZO
  → 15:00 ONCES → 18:00 TERTULIA → 22:00 REFLEXIÓN

Uso:
    from motor_simulacion import SimulationEngine, Scene
    engine = SimulationEngine()
    engine.initialize_agents(["Don Fabio", "Jhon Fredy"])
    engine.run_round(scene=Scene(time="07:00", place="Parque Santander", weather="26°C"))
"""

from __future__ import annotations
import datetime
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from multi_client import MultiClient
from prompt_builder import PromptBuilder, Agent, EngramStore

ENGRAM_PROJECT = "generative"


@dataclass
class Scene:
    time: str              # "07:00", "12:00", etc.
    place: str             # "Parque Santander"
    weather: str = "26°C"  # clima
    people: list[str] = field(default_factory=list)
    context: str = ""      # contexto adicional


@dataclass
class RoundResult:
    agent_name: str
    scene: Scene
    prompt_tokens: int
    response_tokens: int
    cost_usd: float
    content: str


class SimulationEngine:
    def __init__(self,
                 client: MultiClient = None,
                 engram: EngramStore = None,
                 pb: PromptBuilder = None,
                 session_id: str = None):
        self.client = client or MultiClient()
        self.engram = engram or EngramStore()
        self.pb = pb or PromptBuilder(self.engram)
        self.session_id = session_id or f"neiva-sim-{datetime.date.today().isoformat()}"
        self.log: list[dict] = []
        self.active_agents: dict[str, Agent] = {}

    def initialize_agents(self, agent_names: list[str]) -> dict[str, Agent]:
        """Inicializa los agentes activos. Carga en cache y guarda identity en engram."""
        all_agents = self.pb.parse_agents()
        for name in agent_names:
            agent = None
            for a in all_agents.values():
                if name.lower() in a.name.lower() or a.name.lower() in name.lower():
                    agent = a
                    break
            if not agent:
                print(f"[warn] agente '{name}' no encontrado en biografías")
                continue
            self.active_agents[agent.slug()] = agent
            # guardar identity en engram (topic_key = agent/{slug}/identity)
            self._save_agent_identity(agent)
        print(f"[ok] {len(self.active_agents)} agentes inicializados")
        return self.active_agents

    def _save_agent_identity(self, agent: Agent):
        """Persiste la identidad del agente en engram (idempotente)."""
        con = self._conn()
        try:
            existing = con.execute("""
                SELECT id FROM observations
                WHERE project = ? AND topic_key = ? AND deleted_at IS NULL
                LIMIT 1
            """, (ENGRAM_PROJECT, agent.topic_identity())).fetchone()
            if existing:
                return
            import datetime
            now = datetime.datetime.utcnow().isoformat() + "Z"
            sync_id = f"obs-identity-{agent.slug()}"
            con.execute("""
                INSERT INTO observations
                  (sync_id, session_id, type, title, content, project, scope,
                   topic_key, created_at, updated_at, last_seen_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (sync_id, self.session_id, "identity", f"Identidad de {agent.name}",
                  agent.raw_bio, ENGRAM_PROJECT, "project",
                  agent.topic_identity(), now, now, now))
            con.commit()
        finally:
            con.close()

    def _conn(self):
        return __import__("sqlite3").connect(self.engram.db_path)

    def choose_model(self, agent: Agent) -> tuple[str, str]:
        """Elige provider/model para el agente.

        Política v2: deepseek-chat por defecto (rápido, barato).
        Si agent.usa_reasoner es True o si la simulación requiere thinking,
        usar deepseek-reasoner (más caro pero más reflexivo).
        """
        # Política v2: todos usan DeepSeek Chat por defecto
        # Para experimentar con deepseek-reasoner, pasar
        # agent.usa_reasoner = True antes de initialize_agents()
        usar_reasoner = getattr(agent, 'usa_reasoner', False)
        if usar_reasoner:
            return ("deepseek", "deepseek-reasoner")
        return ("deepseek", "deepseek-chat")

    def run_round(self, agent_slug: str, scene: Scene,
                  memory_query: str = "",
                  scene_context_override: str = None,
                  save_memory: bool = True) -> RoundResult:
        """Ejecuta una ronda: el agente percibe la escena y responde."""
        agent = self.active_agents.get(agent_slug)
        if not agent:
            raise ValueError(f"Agent '{agent_slug}' not initialized")

        scene_context = scene_context_override or scene.context
        prompt = self.pb.build_agent_prompt(
            agent_name=agent.name,
            scene={"hora": scene.time, "lugar": scene.place,
                   "clima": scene.weather,
                   "personas_presentes": scene.people},
            scene_context=scene_context,
            memory_query=memory_query,
            n_memories=5,
        )

        provider, model_id = self.choose_model(agent)
        messages = [
            {"role": "system", "content": prompt["system"]},
            {"role": "user", "content": prompt["user"]},
        ]
        resp = self.client.chat(
            provider=provider, model_id=model_id,
            messages=messages,
            # Reasoning mode (deepseek-reasoner) gasta tokens pensando.
            # Damos 800 para que tenga espacio de razonamiento + respuesta.
            # Non-reasoning mode solo usa los 180 que necesitamos para
            # respuesta corta al estilo WhatsApp.
            max_tokens=800 if model_id == "deepseek-reasoner" else 180,
            temperature=1.3,
        )

        result = RoundResult(
            agent_name=agent.name,
            scene=scene,
            prompt_tokens=resp["usage"]["in"],
            response_tokens=resp["usage"]["out"],
            cost_usd=resp["cost_usd"],
            content=resp["content"],
        )

        if save_memory:
            self._save_round_memory(agent, scene, result)

        self.log.append({
            "ts": datetime.datetime.utcnow().isoformat(),
            "agent": agent.name,
            "scene": scene.time + " " + scene.place,
            "tokens": result.prompt_tokens + result.response_tokens,
            "cost": result.cost_usd,
            "content_preview": result.content[:80],
        })
        return result

    def _save_round_memory(self, agent: Agent, scene: Scene, result: RoundResult):
        """Guarda el recuerdo de esta ronda en engram."""
        title = f"{scene.time} {scene.place} - {agent.name}"
        content = (
            f"**What**: Estuve en {scene.place} a las {scene.time}.\n"
            f"**What happened**: {result.content}\n"
            f"**Why**: Ronda de simulación Neiva.\n"
            f"**Where**: {scene.place}, Neiva"
        )
        self.engram.save_memory(agent, title, content, type_="memory")

    def dialogue_round(self, slug_a: str, slug_b: str, scene: Scene,
                       n_exchanges: int = 3) -> list[RoundResult]:
        """Hace que dos agentes dialoguen n_exchanges veces."""
        results = []
        prev_response = scene.context
        for i in range(n_exchanges):
            # turno A
            ctx_a = f"Conversando con {self.active_agents[slug_b].name}. Él/ella dijo antes: \"{prev_response}\""
            r = self.run_round(slug_a, scene, scene_context_override=ctx_a, save_memory=False)
            results.append(r)
            prev_response = r.content
            # turno B
            ctx_b = f"Conversando con {self.active_agents[slug_a].name}. Él/ella dijo antes: \"{prev_response}\""
            r2 = self.run_round(slug_b, scene, scene_context_override=ctx_b, save_memory=False)
            results.append(r2)
            prev_response = r2.content
        # guardar la conversación completa como memoria compartida
        conv = "\n".join([f"{r.agent_name}: {r.content}" for r in results])
        for slug in [slug_a, slug_b]:
            agent = self.active_agents[slug]
            other = slug_b if slug == slug_a else slug_a
            self.engram.save_memory(
                agent,
                f"Conversación con {self.active_agents[other].name} en {scene.place}",
                f"**What**: Conversé con {self.active_agents[other].name} en {scene.place} a las {scene.time}.\n\n{conv}\n\n**Why**: Diálogo de ronda de simulación.",
                type_="dialogue",
            )
        return results

    def usage_report(self) -> str:
        return self.client.stats.report()


# ============================================================
# HELLO WORLD
# ============================================================
def hello_world():
    print("=" * 70)
    print("HELLO WORLD — Simulación Neiva")
    print("=" * 70)
    print()

    engine = SimulationEngine()
    # Sociedad pequeña de Tello: 4 agentes para hello world
    agents = engine.initialize_agents(["Don Eliécer", "Doña Rosa", "Don Rosalío", "Padre Cecilio"])
    print(f"Slugs activos: {list(agents.keys())}")

    print()
    print("=" * 70)
    print("RONDA 1: Don Eliécer en Finca Matarredonda (07:00) - después de la misa")
    print("=" * 70)
    scene1 = Scene(
        time="07:00", place="Finca Matarredonda (vereda, casa del patrón)",
        weather="26°C",
        people=["Mayordomo (jornalero de confianza)"],
        context="Don Eliécer volvió de la misa de 6am oficiada por el Padre Cecilio. "
                "El mayordomo le espera con tinto. Revisa los animales.",
    )
    r1 = engine.run_round("elicer-perdomo-el-ganadero-patrn", scene1)
    print(f"\n>>> Don Eliécer:")
    print(r1.content)
    print(f"  (tokens: {r1.prompt_tokens}/{r1.response_tokens}, cost: ${r1.cost_usd:.6f})")

    print()
    print("=" * 70)
    print("RONDA 2: Doña Rosa en su Tienda (07:15) - abriendo el día")
    print("=" * 70)
    scene2 = Scene(
        time="07:15", place="Tienda de Doña Rosa (esquina NW, Calle 5 con Carrera 6)",
        weather="26°C",
        people=["Una vecina (comprando leche fiada)"],
        context="Doña Rosa abrió la tienda. Está organizando la mercancía. "
                "La vecina llegó sin plata, le va a fiar.",
    )
    r2 = engine.run_round("rosa-elvira-trujillo-la-tendera-de-la-esquina", scene2)
    print(f"\n>>> Doña Rosa:")
    print(r2.content)
    print(f"  (tokens: {r2.prompt_tokens}/{r2.response_tokens}, cost: ${r2.cost_usd:.6f})")

    print()
    print("=" * 70)
    print("RONDA 3: Diálogo Padre Cecilio <-> Don Rosalío (tensión política)")
    print("=" * 70)
    scene3 = Scene(
        time="07:30", place="Atrio de la iglesia (parque principal)",
        weather="27°C",
        people=["Padre Cecilio (párroco)"],
        context="Don Rosalío salió de misa rápido. El Padre Cecilio lo intercepta "
                "para pedirle que vuelva, que hace 3 domingos que no se acerca a comulgar. "
                "Don Rosalío es 'liberal ateo' según el cura.",
    )
    results = engine.dialogue_round("cecilio-ramrez-el-prroco", "rosalo-quintero-el-ganadero-rival", scene3, n_exchanges=2)
    for r in results:
        print(f"\n>>> {r.agent_name}:")
        print(r.content)
        print(f"  (tokens: {r.prompt_tokens}/{r.prompt_tokens}, cost: ${r.cost_usd:.6f})")

    print()
    print("=" * 70)
    print("USO TOTAL")
    print("=" * 70)
    print(engine.usage_report())

    print()
    print("=" * 70)
    print("MEMORIAS GUARDADAS EN ENGRAM")
    print("=" * 70)
    for slug, agent in engine.active_agents.items():
        mems = engine.engram.search_memories(agent, limit=5)
        print(f"\n--- {agent.name} ({len(mems)} memorias) ---")
        for m in mems:
            print(f"  [{m['type']}] {m['title']}")


if __name__ == "__main__":
    hello_world()