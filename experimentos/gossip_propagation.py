# -*- coding: utf-8 -*-
"""
experimentos/gossip_propagation.py
====================================
Template de experimento forense: PROPAGACION DE CHISME.

OBJETIVO FORENSE
================
Medir como se propaga un rumor plantado en la sociedad simulada de Tello.

Variables independientes:
  - origen del rumor (quien lo dice primero)
  - veracidad (0.0 a 1.0)
  - intensidad emocional (1.0 a 3.0)
  - topico (string, ej: "Don Fernando se robo la plata del acueducto")

Variables dependientes:
  - cobertura: % de adultos que recibieron el rumor en t+T
  - velocidad: tiempo hasta 50% de cobertura
  - distorsion: cuanto cambia el topico en cada transmision
  - super-spreaders: top 5 agentes que mas transmitieron
  - escépticos: agentes que recibieron pero no retransmitieron

DISENO EXPERIMENTAL
===================
Replica 1 (control):    rumor veraz (v=0.9), intensidad neutra (i=1.0)
Replica 2 (tratamiento): rumor falso (v=0.2), intensidad alta (i=2.0)
Replica 3 (tratamiento): rumor neutro (v=0.5), intensidad alta (i=2.5)
Replica 4 (tratamiento): rumor veraz (v=0.9), intensidad alta (i=2.5)

Cada replica corre 24h simuladas con semilla random variable.
N=10 replicas por condicion para estadistica (240 simulaciones totales).

METODOLOGIA
===========
1. Inicializar experimento con escenario base
2. Plantar gossip seed (origen, topico, veracidad, intensidad)
3. En cada tick (5 min simulados):
   a. Determinar que agentes estan co-presentes (en mismo lugar)
   b. Para cada par co-presente con relacion existente:
      - probabilidad de hablar (cercania, rol, horario)
      - si hablan, probabilidad de mencionar el topico
      - si mencionan, generar dialogo via LLM
      - logear transmision
4. Al final: analizar cobertura, velocidad, distorsion

USO
===
>>> python experimentos/gossip_propagation.py \
        --origen dona_rosa_tendera \
        --topic "Don Fernando se robo la plata del acueducto" \
        --veracidad 0.2 \
        --intensidad 2.0 \
        --duracion 24 \
        --replicas 5 \
        --export experimentos/gossip_v1
"""

import argparse
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from reloj import Reloj, formatear_dia, formatear_hora
from experimento import Experimento, Escenario
try:
    from dashboard_reloj import Dashboard
    _HAVE_DASHBOARD = True
except ImportError:
    Dashboard = None
    _HAVE_DASHBOARD = False


def parsear_args():
    p = argparse.ArgumentParser(
        description="Experimento forense: propagacion de chisme en Tello."
    )
    p.add_argument("--origen", default="dona_rosa_tendera",
                   help="Agente origen del rumor.")
    p.add_argument("--topic", default="Don Fernando se robo la plata",
                   help="Topico del rumor.")
    p.add_argument("--veracidad", type=float, default=0.5,
                   help="Veracidad del rumor (0.0 a 1.0).")
    p.add_argument("--intensidad", type=float, default=1.0,
                   help="Intensidad emocional (1.0 neutro, 3.0 escandaloso).")
    p.add_argument("--t_seed", default="2026-06-19 08:00",
                   help="Timestamp virtual para sembrar el rumor.")
    p.add_argument("--duracion", type=int, default=24,
                   help="Duracion en horas simuladas.")
    p.add_argument("--replicas", type=int, default=3,
                   help="Numero de replicas (semillas random distintas).")
    p.add_argument("--export", default="experimentos/gossip_propagation",
                   help="Directorio base de exportacion.")
    p.add_argument("--seed_base", type=int, default=42,
                   help="Semilla base para reproducibilidad.")
    return p.parse_args()


def cargar_agentes_tello():
    """Carga los agentes de geo_tello.py."""
    try:
        from geo_tello import AGENTES_GEO, EDIFICIOS
        return AGENTES_GEO, EDIFICIOS
    except ImportError:
        print("[WARN] geo_tello.py no disponible, usando placeholder.")
        return {}, {}


def generar_escena_gossip(exp, agentes, edificios, topico,
                           tiempo_ventana_min=15):
    """
    Genera una lista de escenas donde agentes podrian transmitir el rumor.

    Una "escena gossip" es: (A, B, lugar, t_inicio, t_fin)
    donde A tiene el rumor, B no lo tiene, y estan co-presentes en
    lugar durante el intervalo.

    Returns: lista de tuplas (agente_con, agente_sin, lugar, t).
    """
    escenas = []
    return escenas  # placeholder — integrar con motor_simulacion


def correr_replica(args, replica_id, seed):
    """Corre una replica del experimento."""
    t_seed = datetime.strptime(args.t_seed, "%Y-%m-%d %H:%M")
    t_inicio = t_seed - timedelta(hours=2)  # warm-up
    t_fin = t_seed + timedelta(hours=args.duracion)

    # Escenario
    agentes, edificios = cargar_agentes_tello()
    escenario = Escenario(
        t_inicial=t_inicio,
        duracion_segundos=(t_fin - t_inicio).total_seconds(),
        agentes=agentes,
        random_seed=seed,
        hipotesis=(
            f"Rumor '{args.topic}' (v={args.veracidad}, "
            f"i={args.intensidad}) plantado por {args.origen} en {args.t_seed}. "
            f"Replicas: {args.replicas}."
        ),
        metadata={
            "tipo": "gossip_propagation",
            "replica_id": replica_id,
            "seed": seed,
            "topico": args.topic,
            "veracidad": args.veracidad,
            "intensidad": args.intensidad,
            "origen": args.origen,
            "t_seed": args.t_seed,
        },
    )

    exp = Experimento(
        nombre=f"gossip_r{replica_id}_v{args.veracidad}_i{args.intensidad}",
        escenario=escenario,
        version_prompt="2.0",
        directorio_base=args.export,
    )

    exp.nota(f"Replica {replica_id} iniciada. Seed={seed}.")

    # Plantar rumor en t_seed
    exp.sembrar_gossip(
        t=t_seed,
        origen=args.origen,
        topic=args.topic,
        audiencia="vecinos",
        veracidad=args.veracidad,
        intensidad=args.intensidad,
    )
    exp.nota(f"Rumor plantado: origen={args.origen}, veracidad={args.veracidad}, "
             f"intensidad={args.intensidad}, topico='{args.topic}'")

    # Generar escenas de propagacion (mock por ahora — integrar con motor)
    escenas = generar_escena_gossip(exp, agentes, edificios, args.topic)

    # Por cada escena, registrar intento de transmision (sin LLM real en v1)
    for ag_a, ag_b, lugar, t in escenas:
        exp.inyectar_evento(
            t=t, tipo="gossip_transmit",
            payload={
                "de": ag_a, "a": ag_b,
                "topic": args.topic, "canal": "presencial",
                "lugar": lugar,
            }
        )

    # Correr la simulacion
    exp.correr(paso_segundos=300)

    exp.nota(f"Replica {replica_id} finalizada.")
    return exp


def analizar_resultados(experimentos):
    """Analisis cruzado de replicas."""
    print()
    print("=" * 70)
    print(" ANALISIS DE RESULTADOS")
    print("=" * 70)

    for exp in experimentos:
        res = exp.resumen()
        print(f"\n[{exp.nombre}]")
        print(f"  - log entries: {res['n_log_entries']}")
        print(f"  - gossip edges: {res['n_gossip_edges']}")
        print(f"  - conflictos: {res['n_conflictos']}")

    # Tabla comparativa
    print()
    print("=" * 70)
    print(" TABLA COMPARATIVA")
    print("=" * 70)
    print(f"{'Replica':<12} {'Gossip':<10} {'Conflictos':<12} {'Log':<8}")
    print("-" * 70)
    for exp in experimentos:
        res = exp.resumen()
        print(f"{exp.nombre:<12} {res['n_gossip_edges']:<10} "
              f"{res['n_conflictos']:<12} {res['n_log_entries']:<8}")


def main():
    args = parsear_args()

    print("=" * 70)
    print(" EXPERIMENTO FORENSE: PROPAGACION DE CHISME — TELLO, HUILA")
    print("=" * 70)
    print(f"Topico:     '{args.topic}'")
    print(f"Origen:     {args.origen}")
    print(f"Veracidad:  {args.veracidad}")
    print(f"Intensidad: {args.intensidad}")
    print(f"Duracion:   {args.duracion}h")
    print(f"Replicas:   {args.replicas}")
    print(f"Seed base:  {args.seed_base}")
    print()

    experimentos = []
    for i in range(args.replicas):
        seed = args.seed_base + i * 1000  # semillas espaciadas
        print(f"\n>>> Corriendo replica {i+1}/{args.replicas} (seed={seed})...")
        exp = correr_replica(args, replica_id=i+1, seed=seed)
        experimentos.append(exp)

    # Analisis
    analizar_resultados(experimentos)

    # Export
    for exp in experimentos:
        ruta = exp.exportar(comprimir=True)
        print(f"\n[EXPORT] {ruta}")

        # Renderizar dashboard PNG
        d = Dashboard(exp) if _HAVE_DASHBOARD and Dashboard is not None else None
        if d is not None:
            ruta_png = d.render_png()
            if ruta_png:
                print(f"  Dashboard PNG: {ruta_png}")
        else:
            print("  Dashboard PNG: [skip] dashboard_reloj no disponible")

    print()
    print("=" * 70)
    print(" EXPERIMENTO COMPLETADO")
    print("=" * 70)
    print(f"Resultados en: {args.export}/")


if __name__ == "__main__":
    main()
