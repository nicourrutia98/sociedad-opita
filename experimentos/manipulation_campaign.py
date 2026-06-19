# -*- coding: utf-8 -*-
"""
experimentos/manipulation_campaign.py
=======================================
Template de experimento forense: CAMPANA DE MANIPULACION SOCIAL.

OBJETIVO FORENSE
================
Simular una campana de manipulacion social controlada sobre la sociedad
de Tello y medir su efecto.

Caso de estudio:
  Manipulacion para discredito del alcalde Don Fernando Solano Gomez
  durante la semana previa al Festival del Bambuco.

Pregunta forense:
  - Cuantos agentes son necesarios para que una campana tenga efecto?
  - Cual es la velocidad de propagacion?
  - Cual es la tasa de aceptacion (vs rechazo/escepticismo)?
  - Cual es el efecto final (cambio en actitud agregada)?

DISENO EXPERIMENTAL
===================
Condiciones:
  1. CONTROL: sin campana, solo eventos naturales del Festival
  2. TRATAMIENTO BAJO: 1 super-spreader (dona_rosa), 1 rumor/dia
  3. TRATAMIENTO MEDIO: 3 super-spreaders (rosa, cura, inspector), 3 rumores/dia
  4. TRATAMIENTO ALTO: 5 super-spreaders + rumores variados + intervenciones

Outcome: cambio en "indice de apoyo al alcalde" antes vs despues.
  Indice = % de adultos que mencionan al alcalde positivamente
  Medido en dialogos generados por LLM al final del experimento.

USO
===
>>> python experimentos/manipulation_campaign.py \
        --target don_fernando_alcalde \
        --tipo discredito \
        --duracion 168 \
        --replicas 5
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from reloj import formatear_dia, formatear_hora
from experimento import Experimento, Escenario
from dashboard_reloj import Dashboard


# Banco de rumores (en espanol, ASCII-safe donde sea posible)
# Temas adaptados al contexto de Tello 2026.
RUMORES_DISPONIBLES = [
    "Don Fernando se robo la plata del acueducto",
    "El alcalde esta tomando con el Caliche el minero ilegal",
    "Don Fernando tiene una hija escondida en Neiva",
    "El Festival se lo robaron, todo para los amigos",
    "El alcalde le dio contrato a su cuñado por 200 millones",
    "Fernando le pego a su señora y por eso se separaron",
    "Don Fernando anda en moto nueva, dizque de la Contraloria",
    "El alcalde le mintio al Personero sobre el acueducto",
    "Fernando se reunio con los disidencias en Cerro Neiva",
    "Don Fernando no pago la seguridad social del pueblo",
]

SUPER_SPREADERS_CABECERA = [
    "dona_rosa_tendera",      # epicentral, +100 personas/dia
    "padre_cecilio_cura",      # reuniones morales
    "dona_mercedes_panadera",  # amas de casa, manana
    "don_sigifredo_inspector", # institucional, intermediario
    "dona_prudencia_partera",  # mujeres mayores, partos
    "don_eliseo_boticario",    # enfermos y visitas
    "don_emigdio_jubilado",    # taberna, hombres ociosos
    "capitan_hernan_policia",  # autoridad, fuerza publica
    "jhon_jairo_sacristan",    # iglesia, informante
    "taberna_la_mocha",        # lugar, no persona
]

SUPER_SPREADERS_INSTITUCIONAL = [
    "don_sigifredo_inspector",
    "capitan_hernan_policia",
    "beatriz_personera",
]


def parsear_args():
    p = argparse.ArgumentParser(
        description="Experimento forense: campana de manipulacion social."
    )
    p.add_argument("--target", default="don_fernando_alcalde",
                   help="Agente objetivo de la campana.")
    p.add_argument("--tipo", default="discredito",
                   choices=["discredito", "apoyo", "dividir", "reconciliar"],
                   help="Tipo de campana.")
    p.add_argument("--duracion", type=int, default=168,
                   help="Duracion en horas (default: 1 semana).")
    p.add_argument("--replicas", type=int, default=5,
                   help="Replicas por condicion.")
    p.add_argument("--seed_base", type=int, default=42)
    p.add_argument("--export", default="experimentos/manipulation_campaign")
    return p.parse_args()


def configurar_campana(args, condicion, seed_offset):
    """Genera la configuracion de campana segun condicion."""
    if condicion == "control":
        return {
            "super_spreaders": [],
            "rumores_por_dia": 0,
            "intervenciones": [],
        }
    elif condicion == "bajo":
        return {
            "super_spreaders": ["dona_rosa_tendera"],
            "rumores_por_dia": 1,
            "intervenciones": [],
        }
    elif condicion == "medio":
        return {
            "super_spreaders": [
                "dona_rosa_tendera",
                "padre_cecilio_cura",
                "don_sigifredo_inspector",
            ],
            "rumores_por_dia": 3,
            "intervenciones": ["mesa_redonda_tienda"],
        }
    elif condicion == "alto":
        return {
            "super_spreaders": [
                "dona_rosa_tendera",
                "padre_cecilio_cura",
                "don_sigifredo_inspector",
                "dona_mercedes_panadera",
                "taberna_la_mocha",
            ],
            "rumores_por_dia": 5,
            "intervenciones": [
                "mesa_redonda_tienda",
                "predica_domingo",
                "comentario_inspeccion",
            ],
        }
    else:
        return {"super_spreaders": [], "rumores_por_dia": 0}


def correr_replica(args, replica_id, condicion, seed):
    """Corre una replica con la condicion dada."""
    t_inicio = datetime(2026, 6, 22, 6, 0)  # lunes antes del Festival
    t_fin = t_inicio + timedelta(hours=args.duracion)

    escenario = Escenario(
        t_inicial=t_inicio,
        duracion_segundos=(t_fin - t_inicio).total_seconds(),
        agentes={"placeholder": {}},
        random_seed=seed,
        hipotesis=(
            f"Campana '{args.tipo}' contra {args.target} bajo condicion "
            f"'{condicion}' reduce el indice de apoyo en TBD puntos."
        ),
        metadata={
            "tipo": "manipulation_campaign",
            "target": args.target,
            "tipo_campana": args.tipo,
            "condicion": condicion,
            "seed": seed,
        },
    )

    exp = Experimento(
        nombre=f"manip_{args.target}_{args.tipo}_{condicion}_r{replica_id}",
        escenario=escenario,
        directorio_base=args.export,
    )

    config = configurar_campana(args, condicion, replica_id)

    exp.nota(
        f"Replica {replica_id}: condicion='{condicion}', "
        f"super_spreaders={config['super_spreaders']}, "
        f"rumores_por_dia={config['rumores_por_dia']}."
    )

    # Sembrar rumores segun condicion
    n_dias = args.duracion // 24
    for dia in range(n_dias):
        for n_rumor in range(config["rumores_por_dia"]):
            # Espaciar los rumores a lo largo del dia
            hora = 8 + (n_rumor * 4) + (dia % 3)
            t_rumor = t_inicio + timedelta(days=dia, hours=hora)
            ss = config["super_spreaders"][n_rumor % len(config["super_spreaders"])]
            rumor = RUMORES_DISPONIBLES[(dia + n_rumor) % len(RUMORES_DISPONIBLES)]

            exp.sembrar_gossip(
                t=t_rumor,
                origen=ss,
                topic=f"({args.target}) {rumor}",
                audiencia="vecinos",
                veracidad=0.3,
                intensidad=2.5,
            )

    # Snapshot pre-campana
    exp.snapshot("pre_campana")

    # Correr simulacion
    exp.correr(paso_segundos=600)  # 10 min por paso

    # Snapshot post-campana
    exp.snapshot("post_campana")

    exp.nota(f"Replica {replica_id} finalizada. Condicion: {condicion}.")
    return exp


def analizar(experimentos, args):
    """Analisis cruzado."""
    print()
    print("=" * 70)
    print(f" ANALISIS: CAMPANA DE {args.tipo.upper()} CONTRA {args.target}")
    print("=" * 70)
    print(f"{'Replica':<55} {'Rumores':<10} {'Conflictos':<12}")
    print("-" * 90)
    for exp in experimentos:
        res = exp.resumen()
        print(f"{exp.nombre:<55} {res['n_gossip_edges']:<10} {res['n_conflictos']:<12}")


def main():
    args = parsear_args()

    print("=" * 70)
    print(" EXPERIMENTO FORENSE: CAMPANA DE MANIPULACION")
    print("=" * 70)
    print(f"Target:      {args.target}")
    print(f"Tipo:        {args.tipo}")
    print(f"Duracion:    {args.duracion}h ({args.duracion // 24}d)")
    print(f"Replicas:    {args.replicas}")
    print()

    condiciones = ["control", "bajo", "medio", "alto"]
    n_efectivo = min(args.replicas, len(condiciones))
    if args.replicas > len(condiciones):
        print(f"[INFO] {args.replicas} replicas solicitadas pero solo "
              f"{len(condiciones)} condiciones disponibles.")

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
        d = Dashboard(exp)
        ruta_png = d.render_png()
        if ruta_png:
            print(f"  Dashboard: {ruta_png}")

    print()
    print("EXPERIMENTO COMPLETADO.")
    print(f"Resultados en: {args.export}/")


if __name__ == "__main__":
    main()
