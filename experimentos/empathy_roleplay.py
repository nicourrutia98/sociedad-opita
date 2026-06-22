# -*- coding: utf-8 -*-
"""
experimentos/empathy_roleplay.py
=================================
Template de experimento forense: EMPATIA Y PERSPECTIVA.

OBJETIVO FORENSE
================
Medir la capacidad empatica de los agentes simulados frente a dilemas
sociales del contexto Tello.

Caso de estudio:
  Dilema: Don Rosalío (ganadero rival) sufre una inundacion. Su ganado se
  muere. Don Elieceer (patron rival) tiene que decidir si ayuda o no.
  
Pregunta forense:
  - Cuanto pesa la relacion previa (rivalidad) vs la norma social?
  - Quien media (cura, personera, vecinos)?
  - Como cambia la percepcion del conflicto por terceros?
  - Hay "switching" de bandos despues del dilema?

DISENO EXPERIMENTAL
===================
Replica 1 (control): sin evento, status quo
Replica 2 (tratamiento): inundacion leve (5 animales muertos)
Replica 3 (tratamiento): inundacion severa (todo el ganado)
Replica 4 (tratamiento): inundacion + presion social explicita (cura)

Outcome:
  - Comportamiento de Elieceer: ayuda / no ayuda / ambivalente
  - Cambio en la red social: edges nuevos / edges rotos
  - Dialogos de terceros: como reaccionan

USO
===
>>> python experimentos/empathy_roleplay.py \
        --dilema inundacion_rosalio \
        --sujeto don_eliecer_patron \
        --objeto don_rosalio_rival \
        --duracion 96 \
        --replicas 4
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from experimento import Experimento, Escenario
try:
    from dashboard_reloj import Dashboard
    _HAVE_DASHBOARD = True
except ImportError:
    Dashboard = None
    _HAVE_DASHBOARD = False


def parsear_args():
    p = argparse.ArgumentParser(
        description="Experimento forense: empatia y perspectiva."
    )
    p.add_argument("--dilema", default="inundacion_rosalio",
                   help="Tipo de dilema moral a presentar.")
    p.add_argument("--sujeto", default="don_eliecer_patron",
                   help="Agente sujeto del dilema.")
    p.add_argument("--objeto", default="don_rosalio_rival",
                   help="Agente victima del evento.")
    p.add_argument("--duracion", type=int, default=96,
                   help="Duracion en horas (default: 4 dias).")
    p.add_argument("--replicas", type=int, default=4)
    p.add_argument("--seed_base", type=int, default=42)
    p.add_argument("--export", default="experimentos/empathy_roleplay")
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
            f"Dilema '{args.dilema}' en condicion '{condicion}': "
            f"{args.sujeto} decide TBD hacia {args.objeto}."
        ),
        metadata={
            "tipo": "empathy_roleplay",
            "dilema": args.dilema,
            "sujeto": args.sujeto,
            "objeto": args.objeto,
            "condicion": condicion,
            "seed": seed,
        },
    )

    exp = Experimento(
        nombre=f"empathy_{args.dilema}_{args.sujeto}_{condicion}_r{replica_id}",
        escenario=escenario,
        directorio_base=args.export,
    )

    exp.nota(f"Replica {replica_id}: dilema '{args.dilema}', condicion='{condicion}'")

    # Configurar condicion
    if condicion == "control":
        exp.nota("CONDICION: control. Sin evento adverso.")
        exp.snapshot("pre_dilema")

    elif condicion == "inundacion_leve":
        exp.nota("CONDICION: inundacion leve. 5 animales mueren.")
        # Sembrar rumor del evento
        exp.sembrar_gossip(
            t=t_inicio + timedelta(hours=12),
            origen="dona_rosa_tendera",
            topic="Se le murieron 5 animales a Don Rosalío",
            veracidad=0.9,
            intensidad=1.5,
        )
        # Observar reaccion del sujeto (placeholder: nota)
        exp.inyectar_evento(
            t=t_inicio + timedelta(hours=24),
            tipo="observacion_manual",
            payload={
                "observador": args.sujeto,
                "sujeto_observado": args.objeto,
                "evento": "ganado muerto",
                "reaccion_esperada": "ambivalente o ayuda limitada",
            }
        )

    elif condicion == "inundacion_severa":
        exp.nota("CONDICION: inundacion severa. Todo el ganado muere.")
        exp.sembrar_gossip(
            t=t_inicio + timedelta(hours=12),
            origen="dona_rosa_tendera",
            topic="Don Rosalío perdió todo el ganado en la creciente",
            veracidad=0.95,
            intensidad=2.5,
        )
        exp.inyectar_evento(
            t=t_inicio + timedelta(hours=24),
            tipo="observacion_manual",
            payload={
                "observador": args.sujeto,
                "sujeto_observado": args.objeto,
                "evento": "perdida total del ganado",
                "reaccion_esperada": "posible reconciliacion o solidaridad",
            }
        )

    elif condicion == "presion_social":
        exp.nota("CONDICION: presion social explicita (cura + personera).")
        # Sembrar rumor
        exp.sembrar_gossip(
            t=t_inicio + timedelta(hours=12),
            origen="dona_rosa_tendera",
            topic="Don Rosalío perdió todo el ganado en la creciente",
            veracidad=0.95,
            intensidad=2.5,
        )
        # Presion social explicita del cura
        exp.inyectar_evento(
            t=t_inicio + timedelta(hours=18),
            tipo="intervencion",
            payload={
                "intermediario": "padre_cecilio_cura",
                "metodo": "predica domingo sobre solidaridad",
                "target_audiencia": "comunidad",
                "mensaje": "ayudar al projimo es ley de Dios",
            }
        )
        # Presion de la personera
        exp.inyectar_evento(
            t=t_inicio + timedelta(hours=20),
            tipo="intervencion",
            payload={
                "intermediario": "beatriz_personera",
                "metodo": "reunion comunitaria",
                "target_audiencia": "adultos varones",
            }
        )

    exp.snapshot("pre_dilema")
    exp.correr(paso_segundos=600)
    exp.snapshot("post_dilema")

    exp.nota(f"Replica {replica_id} finalizada.")
    return exp


def analizar(experimentos, args):
    """Analisis cruzado."""
    print()
    print("=" * 70)
    print(f" ANALISIS: EMPATIA - DILEMA '{args.dilema}'")
    print("=" * 70)
    print(f"Sujeto:  {args.sujeto}")
    print(f"Objeto:  {args.objeto}")
    print("-" * 90)
    print(f"{'Replica':<60} {'Rumores':<10}")
    print("-" * 90)
    for exp in experimentos:
        res = exp.resumen()
        print(f"{exp.nombre:<60} {res['n_gossip_edges']:<10}")


def main():
    args = parsear_args()

    print("=" * 70)
    print(" EXPERIMENTO FORENSE: EMPATIA Y PERSPECTIVA")
    print("=" * 70)
    print(f"Dilema:     {args.dilema}")
    print(f"Sujeto:     {args.sujeto}")
    print(f"Objeto:     {args.objeto}")
    print(f"Duracion:   {args.duracion}h ({args.duracion // 24}d)")
    print()

    condiciones = ["control", "inundacion_leve", "inundacion_severa", "presion_social"]
    n_efectivo = min(args.replicas, len(condiciones))

    experimentos = []
    for i in range(n_efectivo):
        cond = condiciones[i]
        seed = args.seed_base + i * 1000
        print(f"\n>>> Replica {i+1}/{n_efectivo}: condicion={cond} (seed={seed})")
        exp = correr_replica(args, replica_id=i+1, condicion=cond, seed=seed)
        experimentos.append(exp)

    analizar(experimentos, args)

    for exp in experimentos:
        ruta = exp.exportar(comprimir=True)
        print(f"[EXPORT] {ruta}")
        d = Dashboard(exp) if _HAVE_DASHBOARD and Dashboard is not None else None
        if d is not None:
            ruta_png = d.render_png()
            if ruta_png:
                print(f"  Dashboard: {ruta_png}")
        else:
            print("  Dashboard: [skip] dashboard_reloj no disponible")

    print()
    print("EXPERIMENTO COMPLETADO.")


if __name__ == "__main__":
    main()
