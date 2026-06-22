# -*- coding: utf-8 -*-
"""
experimentos/conflict_escalation.py
====================================
Template de experimento forense: ESCALADA DE CONFLICTO.

OBJETIVO FORENSE
================
Medir la dinamica de escalada de un conflicto latente entre dos actores.

Conflicto de linderos Elieceer-Rosalio (estudiado en biografias):
  - Disputa desde 2018 sobre alambrado
  - Estado actual: latente (no institucional)
  - Intermediarios naturales: padre Cecilio, dona Rosa

Pregunta forense:
  - Cuanto tarda en escalar de vecinal a institucional?
  - Cual es el disparador? (un evento externo? un encuentro casual?)
  - Quien interviene primero? (el cura, la tienda, la inspeccion?)
  - Como termina? (mediacion, institucionalizacion, suspension?)

DISENO EXPERIMENTAL
===================
Replica 1 (control): conflicto sin intervencion externa
Replica 2 (tratamiento): con mediacion temprana del cura
Replica 3 (tratamiento): con rumor previo (semilla gossip inflamatorio)
Replica 4 (tratamiento): con intervencion institucional (inspector)

Cada replica: 72h simuladas.

ESTADOS DEL CONFLICTO
=====================
  - LATENTE:       sin incidente reciente, rumores de fondo
  - INCIDENTE:     encuentro hostil, sin agresion fisica
  - ESCALADO:      agresion verbal o fisica, testigos
  - MEDIADO:       intervencion de tercero (cura, personera)
  - INSTITUCIONAL: derivacion a inspeccion/comisaria/policia
  - RESUELTO:      acuerdo o suspension temporal
  - CONGELADO:     tension pero sin accion (ej. durante Festival)

USO
===
>>> python experimentos/conflict_escalation.py \
        --conflicto_id linderos_eliecer_rosalio \
        --participantes "don_eliecer,don_rosalio" \
        --duracion 72 \
        --replicas 4
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from reloj import formatear_dia, formatear_hora
from experimento import Experimento, Escenario
try:
    from dashboard_reloj import Dashboard
    _HAVE_DASHBOARD = True
except ImportError:
    Dashboard = None
    _HAVE_DASHBOARD = False


# Estados del conflicto
ESTADOS = ["latente", "incidente", "escalado", "mediado",
          "institucional", "resuelto", "congelado"]

# Transiciones validas (estado_origen -> lista de estados_destino)
TRANSICIONES = {
    "latente": ["incidente", "congelado"],
    "incidente": ["escalado", "mediado", "latente"],
    "escalado": ["mediado", "institucional", "congelado"],
    "mediado": ["resuelto", "escalado", "latente"],
    "institucional": ["resuelto", "congelado"],
    "resuelto": ["latente", "congelado"],
    "congelado": ["latente", "incidente"],
}


def parsear_args():
    p = argparse.ArgumentParser(
        description="Experimento forense: escalada de conflicto."
    )
    p.add_argument("--conflicto_id", default="linderos_eliecer_rosalio",
                   help="ID del conflicto a estudiar.")
    p.add_argument("--participantes", default="don_eliecer_patron,don_rosalio_rival",
                   help="Participantes principales (separados por coma).")
    p.add_argument("--duracion", type=int, default=72,
                   help="Duracion en horas.")
    p.add_argument("--replicas", type=int, default=4,
                   help="Replicas (una por condicion).")
    p.add_argument("--condiciones", default="control,mediacion_cura,gossip_previo,intervencion_institucional",
                   help="Condiciones experimentales (separadas por coma).")
    p.add_argument("--seed_base", type=int, default=42)
    p.add_argument("--export", default="experimentos/conflict_escalation")
    return p.parse_args()


def correr_replica(args, replica_id, condicion, seed):
    """Corre una replica con la condicion dada."""
    t_inicio = datetime(2026, 6, 19, 6, 0)

    escenario = Escenario(
        t_inicial=t_inicio,
        duracion_segundos=args.duracion * 3600,
        agentes={"placeholder": {}},
        random_seed=seed,
        hipotesis=(
            f"Conflicto {args.conflicto_id} bajo condicion '{condicion}' "
            f"termina en estado: TBD"
        ),
        metadata={
            "tipo": "conflict_escalation",
            "conflicto_id": args.conflicto_id,
            "participantes": args.participantes.split(","),
            "condicion": condicion,
            "seed": seed,
        },
    )

    exp = Experimento(
        nombre=f"conflict_{args.conflicto_id}_{condicion}_r{replica_id}",
        escenario=escenario,
        directorio_base=args.export,
    )

    exp.nota(f"Replica {replica_id} iniciada. Condicion: {condicion}.")

    # Inyectar condicion experimental
    if condicion == "control":
        # Sin intervencion. Conflicto escala naturalmente si hay encuentro.
        exp.nota("CONDICION: control. Sin intervencion externa.")
        # Simular encuentro casual a las 24h
        exp.inyectar_evento(
            t=t_inicio + timedelta(hours=24),
            tipo="conflicto_trigger",
            payload={
                "conflicto_id": args.conflicto_id,
                "participantes": args.participantes.split(","),
                "tipo_accion": "escalar",
                "disparador": "encuentro casual en la tienda",
            }
        )

    elif condicion == "mediacion_cura":
        exp.nota("CONDICION: mediacion temprana del cura.")
        exp.inyectar_evento(
            t=t_inicio + timedelta(hours=2),
            tipo="conflicto_trigger",
            payload={
                "conflicto_id": args.conflicto_id,
                "participantes": args.participantes.split(","),
                "tipo_accion": "escalar",
            }
        )
        # Mediacion del cura a las 6h
        exp.inyectar_evento(
            t=t_inicio + timedelta(hours=6),
            tipo="intervencion",
            payload={
                "intermediario": "padre_cecilio_cura",
                "metodo": "dialogo pastoral",
                "conflicto_id": args.conflicto_id,
            }
        )

    elif condicion == "gossip_previo":
        exp.nota("CONDICION: rumor inflamatorio previo.")
        # Sembrar rumor inflamatorio a las 4h
        exp.sembrar_gossip(
            t=t_inicio + timedelta(hours=4),
            origen="dona_rosa_tendera",
            topic="Don Rosalío movio el alambre otra vez",
            veracidad=0.5,
            intensidad=2.0,
        )
        # Conflicto escala a las 8h
        exp.inyectar_evento(
            t=t_inicio + timedelta(hours=8),
            tipo="conflicto_trigger",
            payload={
                "conflicto_id": args.conflicto_id,
                "participantes": args.participantes.split(","),
                "tipo_accion": "escalar",
                "disparador": "rumor escuch en la tienda",
            }
        )

    elif condicion == "intervencion_institucional":
        exp.nota("CONDICION: intervencion institucional directa.")
        exp.inyectar_evento(
            t=t_inicio + timedelta(hours=12),
            tipo="conflicto_trigger",
            payload={
                "conflicto_id": args.conflicto_id,
                "participantes": args.participantes.split(","),
                "tipo_accion": "escalar",
            }
        )
        # Intervencion institucional a las 14h
        exp.inyectar_evento(
            t=t_inicio + timedelta(hours=14),
            tipo="intervencion",
            payload={
                "intermediario": "don_sigifredo_inspector",
                "metodo": "acta de inspeccion",
                "conflicto_id": args.conflicto_id,
            }
        )

    # Correr la simulacion
    exp.correr(paso_segundos=300)
    exp.nota(f"Replica {replica_id} finalizada.")
    return exp


def analizar(experimentos):
    """Analisis cruzado de replicas."""
    print()
    print("=" * 70)
    print(" ANALISIS: ESCALADA DE CONFLICTO")
    print("=" * 70)
    print(f"{'Replica':<55} {'Estado final':<20} {'Log':<8}")
    print("-" * 90)
    for exp in experimentos:
        res = exp.resumen()
        # Estado final del conflicto (si existe)
        conflictos_estado = ""
        for cid, c in exp.conflictos.items():
            conflictos_estado += f"{cid}={c['estado']} "
        if not conflictos_estado:
            conflictos_estado = "(sin conflictos)"
        print(f"{exp.nombre:<55} {conflictos_estado:<20} {res['n_log_entries']:<8}")


def main():
    args = parsear_args()

    print("=" * 70)
    print(" EXPERIMENTO FORENSE: ESCALADA DE CONFLICTO")
    print("=" * 70)
    print(f"Conflicto:    {args.conflicto_id}")
    print(f"Participantes: {args.participantes}")
    print(f"Duracion:     {args.duracion}h")
    print(f"Condiciones:  {args.condiciones}")
    print()

    condiciones = args.condiciones.split(",")
    if len(condiciones) != args.replicas:
        print(f"[WARN] {len(condiciones)} condiciones != {args.replicas} replicas.")
        print(f"       Usando {min(len(condiciones), args.replicas)} replicas.")
        args.replicas = min(len(condiciones), args.replicas)

    experimentos = []
    for i in range(args.replicas):
        seed = args.seed_base + i * 1000
        cond = condiciones[i] if i < len(condiciones) else "control"
        print(f"\n>>> Replica {i+1}/{args.replicas}: condicion={cond} (seed={seed})")
        exp = correr_replica(args, replica_id=i+1, condicion=cond, seed=seed)
        experimentos.append(exp)

    analizar(experimentos)

    # Export
    for exp in experimentos:
        ruta = exp.exportar(comprimir=True)
        print(f"[EXPORT] {ruta}")

        # Dashboard PNG (opcional — requiere dashboard_reloj)
        if _HAVE_DASHBOARD and Dashboard is not None:
            d = Dashboard(exp)
            ruta_png = d.render_png()
            if ruta_png:
                print(f"  Dashboard: {ruta_png}")
        else:
            print("  Dashboard: [skip] dashboard_reloj no disponible")

    print()
    print("EXPERIMENTO COMPLETADO.")


if __name__ == "__main__":
    main()
