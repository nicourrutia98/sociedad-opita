# -*- coding: utf-8 -*-
# Sociedad Opita — Framework de experimentos forenses
# https://sociedad.opitacode.com (proximo)
"""
experimento.py
==============
Framework de experimentos forenses para simulacion de sociedad Tello.

OBJETIVO FORENSE
================
Convertir la simulacion literaria en EXPERIMENTO CIENTIFICO REPRODUCIBLE.

Componentes:
1. **Escenario**: estado inicial (agentes, lugares, gossip seed, conflictos)
2. **Eventos inyectables**: tupla (t_virtual, tipo, payload)
3. **Motor de tiempo**: delega al Reloj (reloj.py)
4. **Logger**: JSONL append-only con timestamp virtual, agente, evento
5. **Red de gossip**: digraph que registra propagacion
6. **Snapshots**: estado completo del mundo en t arbitrario
7. **Reproducibilidad**: random.seed persistido, version de prompts,
   hash de biografias

METODOLOGIA
===========
- Un experimento se define con `definir_escenario()` que devuelve:
    - t_inicial: datetime del reloj virtual al iniciar
    - duracion: cuanto tiempo virtual debe correr
    - agentes: dict {nombre: perfil}
    - eventos_iniciales: lista de eventos pre-cargados
    - random_seed: int para reproducibilidad
    - hipotesis: string (que se espera observar)

- Eventos inyectables en runtime via `inyectar_evento()`:
    tipos validos: gossip_seed, conflicto_trigger, intervencion,
    observacion_manual, markov_transition

- El log es append-only JSONL. Cada linea:
    {"t": "ISO8601", "agente": "nombre", "evento": "tipo",
     "payload": {...}, "metadata": {...}}

- Red de gossip es un networkx.DiGraph:
    nodes = agentes
    edges = (source, target, topic, t_inicio, propagaciones)

- Export en formato compatible con pandas/JSON:
    - log.jsonl: lineas de eventos
    - gossip_graph.json: edges con metadata
    - snapshots/*.json: estado completo en t arbitrario
    - manifest.json: metadata del experimento (seed, version, etc)

LIMITACIONES
============
- L1: Sin rollback. Si un experimento diverge, hay que re-correr desde
  t0 con el mismo seed.
- L2: El log puede crecer mucho (1 evento cada 5s simulados * 86400s/dia
  = 17280 lineas/dia). Compresion gzip recomendada.
- L3: Sin concurrencia. El framework es single-threaded.

USO BASICO
==========
>>> from experimento import Experimento, Escenario
>>> from datetime import datetime
>>> e = Experimento(
...     nombre="gossip_acueducto_v1",
...     escenario=Escenario(
...         t_inicial=datetime(2026, 6, 19, 6, 0),
...         duracion_segundos=86400,  # 1 dia
...         agentes={...},
...         eventos_iniciales=[],
...         random_seed=42,
...         hipotesis="chisme sobre sobrecostos del acueducto llega al 80% de adultos en 24h",
...     )
... )
>>> e.inyectar_evento(
...     t=datetime(2026, 6, 19, 8, 0),
...     tipo="gossip_seed",
...     payload={"origen": "dona_rosa_tendera",
...              "topic": "Don Fernando se robo la plata del acueducto",
...              "target_audiencia": "todos"}
... )
>>> e.correr()
>>> e.exportar("experimentos/gossip_acueducto_v1/")
"""

import json
import os
import gzip
import random
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any

from reloj import Reloj, EVENTOS_ANCLA_2026


@dataclass
class Escenario:
    """Estado inicial del experimento."""
    t_inicial: datetime
    duracion_segundos: int
    agentes: Dict[str, Any]
    eventos_iniciales: List[Dict[str, Any]] = field(default_factory=list)
    random_seed: int = 42
    hipotesis: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Evento:
    """Evento inyectable al experimento."""
    t: datetime  # tiempo virtual
    tipo: str  # gossip_seed, conflicto_trigger, intervencion, etc.
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "t": self.t.isoformat(),
            "tipo": self.tipo,
            "payload": self.payload,
            "metadata": self.metadata,
        }


class Experimento:
    """Framework de experimento forense reproducible."""

    # Tipos de eventos validos (para validacion)
    EVENTOS_VALIDOS = {
        "gossip_seed",         # sembrar chisme
        "gossip_transmit",     # transmision de chisme (A -> B)
        "conflicto_trigger",   # detonar conflicto latente
        "conflicto_escalar",   # escalar conflicto (de vecinal a institucional)
        "intervencion",        # intervencion externa (alcalde, cura)
        "observacion_manual",  # observacion del operador
        "markov_transition",   # transicion de estado (uso de sustancia, etc)
        "evento_externo",      # evento externo (lluvia, accidente, visita)
        "snapshot",            # capturar estado
        "nota_analitica",      # nota libre del operador
    }

    def __init__(self, nombre, escenario, version_prompt="2.0",
                 directorio_base="experimentos"):
        """
        Args:
            nombre: nombre del experimento (slug, sin espacios).
            escenario: instancia de Escenario.
            version_prompt: version del prompt cultural (para reproducibilidad).
            directorio_base: donde se crean los archivos.
        """
        self.nombre = nombre
        self.escenario = escenario
        self.version_prompt = version_prompt

        # Reloj virtual
        self.reloj = Reloj(t0=escenario.t_inicial, velocidad=1.0)

        # Random state (reproducibilidad)
        self.random_seed = escenario.random_seed
        self._random = random.Random(escenario.random_seed)

        # Log append-only
        self.log: List[Dict[str, Any]] = []

        # Red de gossip
        self.gossip_edges: List[Dict[str, Any]] = []

        # Conflictos activos: {conflicto_id: {estado, historia}}
        self.conflictos: Dict[str, Dict[str, Any]] = {}

        # Snapshots guardados
        self.snapshots: Dict[str, Dict[str, Any]] = {}

        # Cola de eventos (se procesan cuando el reloj llega a su t)
        self.cola_eventos: List[Evento] = []

        # Eventos del escenario (pre-cargados)
        for ev in escenario.eventos_iniciales:
            self.cola_eventos.append(Evento(**ev))

        # Metadata
        self.metadata = {
            "nombre": nombre,
            "version_prompt": version_prompt,
            "random_seed": escenario.random_seed,
            "t_inicial": escenario.t_inicial.isoformat(),
            "duracion_segundos": escenario.duracion_segundos,
            "hipotesis": escenario.hipotesis,
            "n_agentes": len(escenario.agentes),
            "metadata_custom": escenario.metadata,
            "wall_time_inicio": datetime.now().isoformat(),
            "biografias_hash": self._hash_biografias(escenario.agentes),
        }

        self._log("experimento_init", {"metadata": self.metadata})

    def _hash_biografias(self, agentes):
        """Hash de las biografias para reproducibilidad."""
        contenido = json.dumps(agentes, sort_keys=True, default=str)
        return hashlib.sha256(contenido.encode("utf-8", "ignore")).hexdigest()[:16]

    def _log(self, evento, payload=None, agente=None, metadata=None):
        """Append a log entry."""
        entry = {
            "t": self.reloj.timestamp_iso(),
            "wall_t": datetime.now().isoformat(),
            "evento": evento,
            "agente": agente,
            "payload": payload or {},
            "metadata": metadata or {},
        }
        self.log.append(entry)
        return entry

    # ==========================================================
    # INYECCION DE EVENTOS
    # ==========================================================

    def inyectar_evento(self, t, tipo, payload, metadata=None):
        """
        Inyecta un evento en la cola para ser procesado cuando el reloj
        alcance `t`.
        """
        if tipo not in self.EVENTOS_VALIDOS:
            raise ValueError(
                f"Tipo de evento '{tipo}' no valido. "
                f"Validos: {sorted(self.EVENTOS_VALIDOS)}"
            )
        ev = Evento(t=t, tipo=tipo, payload=payload or {}, metadata=metadata or {})
        self.cola_eventos.append(ev)
        self._log("evento_inyectado", {"tipo": tipo, "t": t.isoformat(),
                                       "payload": payload})
        return ev

    def sembrar_gossip(self, t, origen, topic, audiencia="vecinos",
                       veracidad=0.5, intensidad=1.0):
        """
        Atajo: sembrar un chisme en t, originado por `origen`.
        - topic: string (lo que se dice).
        - audiencia: "vecinos", "amigos", "todos", "institucion", etc.
        - veracidad: 0.0 (mentira) a 1.0 (verdad).
        - intensidad: cuanto impacto emocional (1.0 = neutro, 2.0 = escandaloso).
        """
        return self.inyectar_evento(
            t=t, tipo="gossip_seed",
            payload={
                "origen": origen,
                "topic": topic,
                "audiencia": audiencia,
                "veracidad": veracidad,
                "intensidad": intensidad,
            }
        )

    def trigger_conflicto(self, t, conflicto_id, participantes,
                          tipo="escalar"):
        """Atajo: detonar o escalar un conflicto."""
        return self.inyectar_evento(
            t=t, tipo="conflicto_trigger",
            payload={
                "conflicto_id": conflicto_id,
                "participantes": participantes,
                "tipo_accion": tipo,
            }
        )

    def snapshot(self, etiqueta):
        """Captura estado actual del mundo en la etiqueta dada."""
        snap = {
            "t": self.reloj.timestamp_iso(),
            "etiqueta": etiqueta,
            "reloj_estado": self.reloj.estado(),
            "n_log_entries": len(self.log),
            "n_gossip_edges": len(self.gossip_edges),
            "n_conflictos": len(self.conflictos),
            "conflicto_estados": list(self.conflictos.keys()),
        }
        self.snapshots[etiqueta] = snap
        self._log("snapshot", {"etiqueta": etiqueta, "resumen": snap})
        return snap

    def nota(self, texto, metadata=None):
        """Nota libre del operador (etiqueta cualitativa)."""
        return self.inyectar_evento(
            t=self.reloj.ahora(), tipo="nota_analitica",
            payload={"texto": texto}, metadata=metadata or {}
        )

    # ==========================================================
    # MOTOR DE TIEMPO
    # ==========================================================

    def avanzar(self, dt_segundos):
        """Avanza el reloj y procesa eventos cuyo t <= t_actual."""
        self.reloj.avanzar(dt_segundos)
        self._procesar_eventos_pendientes()

    def correr(self, paso_segundos=300):
        """
        Corre el experimento hasta alcanzar la duracion del escenario.
        Por defecto avanza en pasos de 5 minutos virtuales.
        """
        t_fin = self.escenario.t_inicial + timedelta(
            seconds=self.escenario.duracion_segundos
        )
        n_pasos = int(self.escenario.duracion_segundos // paso_segundos)
        for i in range(n_pasos):
            self.avanzar(paso_segundos)
            if self.reloj.ahora() >= t_fin:
                break
        self._log("experimento_fin", {
            "n_eventos_log": len(self.log),
            "n_gossip_edges": len(self.gossip_edges),
            "wall_time_fin": datetime.now().isoformat(),
        })

    def _procesar_eventos_pendientes(self):
        """Procesa eventos cuyo t <= reloj.ahora()."""
        eventos_a_procesar = [e for e in self.cola_eventos
                               if e.t <= self.reloj.ahora()]
        for ev in eventos_a_procesar:
            self._ejecutar_evento(ev)
            self.cola_eventos.remove(ev)

    def _ejecutar_evento(self, ev):
        """Ejecuta un evento (delega a handlers especificos)."""
        handler = getattr(self, f"_handle_{ev.tipo}", None)
        if handler:
            handler(ev)
        else:
            self._log(f"evento_no_implementado",
                      {"tipo": ev.tipo, "payload": ev.payload})

    # Handlers por defecto (pueden ser sobreescritos)
    def _handle_gossip_seed(self, ev):
        """Registra un seed de gossip."""
        edge = {
            "t": self.reloj.timestamp_iso(),
            "origen": ev.payload["origen"],
            "topic": ev.payload["topic"],
            "audiencia": ev.payload.get("audiencia", "vecinos"),
            "veracidad": ev.payload.get("veracidad", 0.5),
            "intensidad": ev.payload.get("intensidad", 1.0),
            "propagado_a": [],
        }
        self.gossip_edges.append(edge)
        self._log("gossip_seeded", edge, agente=ev.payload["origen"])

    def _handle_gossip_transmit(self, ev):
        """Registra transmision de gossip de A a B."""
        edge = {
            "t": self.reloj.timestamp_iso(),
            "topic": ev.payload["topic"],
            "de": ev.payload["de"],
            "a": ev.payload["a"],
            "canal": ev.payload.get("canal", "presencial"),
            "veracidad_percibida": ev.payload.get("veracidad_percibida",
                                                   ev.payload.get("veracidad", 0.5)),
        }
        self.gossip_edges.append(edge)
        self._log("gossip_transmitted", edge,
                  agente=ev.payload["de"])

    def _handle_conflicto_trigger(self, ev):
        """Activa o escala un conflicto."""
        cid = ev.payload["conflicto_id"]
        if cid not in self.conflictos:
            self.conflictos[cid] = {
                "estado": "latente",
                "historia": [],
                "participantes": ev.payload.get("participantes", []),
            }
        tipo = ev.payload.get("tipo_accion", "escalar")
        if tipo == "escalar":
            self.conflictos[cid]["estado"] = "activo"
        elif tipo == "institucionalizar":
            self.conflictos[cid]["estado"] = "institucional"
        self.conflictos[cid]["historia"].append({
            "t": self.reloj.timestamp_iso(),
            "tipo": tipo,
            "payload": ev.payload,
        })
        self._log("conflicto_trigger", ev.payload)

    def _handle_nota_analitica(self, ev):
        """Solo loguea la nota."""
        self._log("nota", {"texto": ev.payload.get("texto", "")})

    def _handle_snapshot(self, ev):
        """Snapshot manual."""
        self.snapshot(ev.payload.get("etiqueta", "manual"))

    # ==========================================================
    # EXPORT
    # ==========================================================

    def exportar(self, ruta=None, comprimir=False):
        """
        Exporta el experimento a un directorio.

        Estructura:
            ruta/
                manifest.json
                log.jsonl (o .jsonl.gz)
                gossip_graph.json
                snapshots.json
                conflictos.json
        """
        if ruta is None:
            ruta = f"experimentos/{self.nombre}"
        ruta_path = Path(ruta)
        ruta_path.mkdir(parents=True, exist_ok=True)

        # Manifest
        manifest = dict(self.metadata)
        manifest["reloj_estado_final"] = self.reloj.estado()
        manifest["reloj_historial_cambios"] = self.reloj.historial_cambios
        with open(ruta_path / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        # Log
        log_path = ruta_path / "log.jsonl"
        if comprimir:
            log_path = ruta_path / "log.jsonl.gz"
            with gzip.open(log_path, "wt", encoding="utf-8") as f:
                for entry in self.log:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        else:
            with open(log_path, "w", encoding="utf-8") as f:
                for entry in self.log:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        # Gossip edges
        with open(ruta_path / "gossip_graph.json", "w", encoding="utf-8") as f:
            json.dump(self.gossip_edges, f, indent=2, ensure_ascii=False)

        # Snapshots
        with open(ruta_path / "snapshots.json", "w", encoding="utf-8") as f:
            json.dump(self.snapshots, f, indent=2, ensure_ascii=False)

        # Conflictos
        with open(ruta_path / "conflictos.json", "w", encoding="utf-8") as f:
            json.dump(self.conflictos, f, indent=2, ensure_ascii=False)

        return str(ruta_path)

    # ==========================================================
    # UTILIDADES
    # ==========================================================

    def resumen(self):
        """Resumen del estado del experimento."""
        return {
            "nombre": self.nombre,
            "t_virtual": self.reloj.timestamp_iso(),
            "velocidad": self.reloj.velocidad,
            "pausado": self.reloj.pausado,
            "n_log_entries": len(self.log),
            "n_gossip_edges": len(self.gossip_edges),
            "n_conflictos": len(self.conflictos),
            "n_eventos_pendientes": len(self.cola_eventos),
            "n_snapshots": len(self.snapshots),
        }


if __name__ == "__main__":
    from datetime import datetime

    print("=" * 60)
    print("DEMO: Framework de experimento forense")
    print("=" * 60)

    agentes_demo = {
        "dona_rosa": {"rol": "tendera", "epicentro_gossip": True},
        "don_sigifredo": {"rol": "inspector"},
        "don_eliecer": {"rol": "ganadero"},
    }

    escenario = Escenario(
        t_inicial=datetime(2026, 6, 19, 6, 0),
        duracion_segundos=86400,  # 1 dia
        agentes=agentes_demo,
        random_seed=42,
        hipotesis="Chisme de sobrecostos llega al 80% en 24h",
    )

    exp = Experimento(nombre="demo_gossip_v1", escenario=escenario)
    print(f"Experimento creado: {exp.nombre}")
    print(f"t_inicial: {exp.reloj.ahora()}")

    # Sembrar gossip a las 8:00
    exp.sembrar_gossip(
        t=datetime(2026, 6, 19, 8, 0),
        origen="dona_rosa",
        topic="Don Fernando se robo la plata del acueducto",
        veracidad=0.2,  # rumor falso
        intensidad=2.0,  # escandaloso
    )
    print(f"Eventos en cola: {len(exp.cola_eventos)}")

    # Trigger conflicto a las 14:00
    exp.trigger_conflicto(
        t=datetime(2026, 6, 19, 14, 0),
        conflicto_id="linderos_eliecer_rosalio",
        participantes=["don_eliecer", "don_rosalio"],
    )

    # Nota del operador
    exp.nota("Inicio del experimento. Operador duerme hasta 14:00.")

    # Correr 1 dia
    exp.correr(paso_segundos=300)

    print()
    print("Resumen final:")
    for k, v in exp.resumen().items():
        print(f"  {k}: {v}")

    # Export
    ruta = exp.exportar("experimentos/demo_gossip_v1", comprimir=True)
    print(f"\nExportado a: {ruta}")

    # Listar archivos exportados
    for f in sorted(Path(ruta).iterdir()):
        size = f.stat().st_size
        print(f"  {f.name} ({size} bytes)")
