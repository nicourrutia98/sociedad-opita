# -*- coding: utf-8 -*-
# Sociedad Opita — Simulacion geografica integrada
# https://sociedad.opitacode.com (proximo)
"""
simulacion_v3_geografica.py
============================
Simulacion forense completa: integra reloj virtual + geografia + ninos +
LLM + framework de experimentos sobre Tello, Huila.

OBJETIVO FORENSE
================
Esta es la pieza de integracion que une todos los modulos:

  reloj.py          -> tiempo virtual controlable
  geo_tello.py      -> coordenadas, edificios, ruta_diaria por agente
  ninos_tello.py    -> 15 ninos con rutinas y redes
  experimento.py    -> log append-only, gossip, conflictos, snapshots
  prompt_builder.py -> prompts con perfiles forenses + cultural huilense
  motor_simulacion.py -> motor LLM ya validado
  multi_client.py   -> DeepSeek primario + fallbacks

METODOLOGIA
===========
Por cada paso de simulacion (5 min virtuales):
1. Determinar ubicacion de cada agente segun su ruta_diaria + t_virtual.
2. Detectar grupos co-presentes en cada edificio.
3. Para cada par co-presente con relacion existente:
   a. Probabilidad de hablar segun cercania, rol, horario.
   b. Si hablan, generar dialogo via LLM (motor_simulacion).
   c. Loggear interaccion (via experimento framework).
4. Procesar eventos inyectados (gossip seed, conflicto, etc).
5. Avanzar reloj virtual.

NIVELES DE SIMULACION
=====================
Nivel 1 (default): solo co-presencia geografica (todos con todos si estan)
Nivel 2: filtra por relacion existente (solo dialogan si se conocen)
Nivel 3: filtra por probabilidad realista (horario, cercania, rol)
Nivel 4 (maximo): LLM decide si hablar (autonomia del agente)

USO
===
>>> python simulacion_v3_geografica.py
>>> python simulacion_v3_geografica.py --nivel 3 --duracion 12 --speed 60
>>> python simulacion_v3_geografica.py --escenario crisis_acueducto
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from reloj import Reloj, formatear_dia, formatear_hora
from experimento import Experimento, Escenario
from dashboard_reloj import Dashboard
from geo_tello import AGENTES_GEO, EDIFICIOS, distancia_metros, agentes_en_rango


# Intentar importar ninos y motor
try:
    from ninos_tello import NINOS, ninos_por_edad
    HAVE_NINOS = True
except ImportError:
    HAVE_NINOS = False

try:
    from motor_simulacion import SimulationEngine, Scene
    HAVE_ENGINE = True
except ImportError:
    HAVE_ENGINE = False

# Mapeo entre mis slugs (geo_tello) y nombres reconocibles (substring match
# contra a.name en prompt_builder).
SLUG_A_NOMBRE = {
    "don_eliecer_patron": "Don Eliécer",
    "don_eliecer_patrón": "Don Eliécer",
    "dona_prudencia_partera": "Doña Prudencia",
    "dona_prudencia_partera": "Doña Prudencia",
    "don_rosalio_rival": "Don Rosalío",
    "don_rosalío_rival": "Don Rosalío",
    "don_fernando_alcalde": "Don Fernando",
    "padre_cecilio_cura": "Padre Cecilio",
    "dona_rosa_tendera": "Doña Rosa Elvira",
    "doña_rosa_tendera": "Doña Rosa Elvira",
    "dona_mercedes_panadera": "Doña Mercedes",
    "doña_mercedes_panadera": "Doña Mercedes",
    "don_eliseo_boticario": "Don Eliseo",
    "aurora_maestra": "Aurora",
    "edilma_secretaria": "Edilma",
    "don_abelardo_conductor": "Don Abelardo",
    "jhon_jairo_sacristan": "Jhon Jairo",
    "jhon_jairo_sacristán": "Jhon Jairo",
    "capitan_hernan_policia": "Capitán Hernán",
    "capitán_hernan_policia": "Capitán Hernán",
    "capitán_hernán_policia": "Capitán Hernán",
    "subintendente_saavedra": "Subintendente Manuel",
    "beatriz_personera": "Beatriz",
    "don_sigifredo_inspector": "Don Sigifredo",
    "patricia_comisaria": "Patricia",
    "laura_reina": "Laura Sofía",
    "laura_reina_pueblo": "Laura Sofía",
    "pipe_hincha": "Pipe",
    "mariana_universitaria": "Mariana",
    "caliche_minero": "Caliche",
    "valentina_secretaria_joven": "Valentina",
    "jhon_eliecer_hijo_patron": "Jhon Eliécer",
    "jhon_eliécer_hijo_patron": "Jhon Eliécer",
    "dona_lucia_maestra_jubilada": "Doña Lucía",
    "doña_lucia_maestra_jubilada": "Doña Lucía",
    "doña_lucia_maestra_jubilada": "Doña Lucía",
    "doña_lucía_maestra_jubilada": "Doña Lucía",
    "don_emigdio_jubilado": "Don Emigdio",
    "don_octavio_medico": "Don Octavio",
}


def a_slug_bio(slug_mio):
    """Convierte mi slug a un nombre reconocible para biografia."""
    if slug_mio in SLUG_A_NOMBRE:
        return SLUG_A_NOMBRE[slug_mio]
    # Fallback: quitar acentos, espacios, etc.
    import unicodedata
    s = unicodedata.normalize("NFD", slug_mio)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("_", " ").title()


def parsear_args():
    p = argparse.ArgumentParser(
        description="Simulacion forense geografica de Tello."
    )
    p.add_argument("--nivel", type=int, default=3,
                   choices=[1, 2, 3, 4],
                   help="Nivel de simulacion (1=basic, 4=maximo).")
    p.add_argument("--duracion", type=int, default=12,
                   help="Duracion en horas.")
    p.add_argument("--t_inicio", default="2026-06-19 06:00",
                   help="Tiempo inicial virtual.")
    p.add_argument("--speed", type=float, default=1.0,
                   help="Velocidad del reloj virtual.")
    p.add_argument("--paso", type=int, default=600,
                   help="Paso de simulacion en segundos virtuales (default 10min).")
    p.add_argument("--seed", type=int, default=42,
                   help="Semilla para reproducibilidad.")
    p.add_argument("--escenario", default="manana_tipica",
                   help="Escenario predefinido (manana_tipica, crisis, festival).")
    p.add_argument("--con_llm", action="store_true",
                   help="Llamar LLM real (DeepSeek). Cuesta dinero.")
    p.add_argument("--llm_sample", type=float, default=0.1,
                   help="Fraccion de interacciones que llaman LLM (0.0-1.0).")
    p.add_argument("--export", default="experimentos/simulacion_v3",
                   help="Directorio de exportacion.")
    return p.parse_args()


def cargar_todos_los_agentes():
    """Carga todos los agentes (adultos + ninos) con geo."""
    agentes = dict(AGENTES_GEO)
    if HAVE_NINOS:
        for slug, n in NINOS.items():
            agentes[f"nino_{slug}"] = {
                "casa": n["casa"],
                "casa_coords": n["casa_coords"],
                "trabajo": "ie_tello",
                "trabajo_coords": (-4, 1),
                "ruta_diaria": n["rutina_diaria"],
                "generacion": f"nino_{n['edad']}",
                "tipo": "nino",
                "perfil": n,
            }
    return agentes


def ubicacion_en_tiempo(agente, t_virtual):
    """
    Determina la ubicacion del agente en el tiempo virtual t_virtual.
    Usa la ruta_diaria.

    Returns: (coords, lugar_id, accion)
    """
    if "ruta_diaria" not in agente:
        casa_coords = agente.get("casa_coords", (0, 0))
        return casa_coords, agente.get("casa", "?"), "sin_ruta"

    hora_decimal = t_virtual.hour + t_virtual.minute / 60
    ruta = agente["ruta_diaria"]

    # Buscar el item de ruta mas cercano al tiempo actual
    mejor = None
    mejor_dif = float("inf")
    for hora_str, lugar, accion in ruta:
        h, m = map(int, hora_str.split(":"))
        hora_item = h + m / 60
        dif = abs(hora_item - hora_decimal)
        if dif < mejor_dif:
            mejor_dif = dif
            mejor = (lugar, accion, hora_item)

    if not mejor:
        casa_coords = agente.get("casa_coords", (0, 0))
        return casa_coords, agente.get("casa", "?"), "sin_ruta"

    lugar, accion, _ = mejor

    # Resolver coords del lugar
    if lugar in EDIFICIOS:
        return EDIFICIOS[lugar]["coords"], lugar, accion
    elif lugar == "casa":
        return agente["casa_coords"], agente.get("casa", "?"), accion
    elif lugar == "trabajo":
        trabajo = agente.get("trabajo")
        if trabajo and trabajo in EDIFICIOS:
            return EDIFICIOS[trabajo]["coords"], trabajo, accion
        return agente.get("trabajo_coords", agente["casa_coords"]), trabajo or "?", accion
    else:
        # Buscar en EDIFICIOS por coincidencia parcial
        for eid, ed in EDIFICIOS.items():
            if lugar in eid or eid in lugar:
                return ed["coords"], eid, accion
        return agente["casa_coords"], lugar, accion


def detectar_copresencia(agentes, t_virtual):
    """
    Detecta grupos co-presentes en el tiempo t_virtual.

    Returns: dict {lugar_id: [lista_agentes]}
    """
    grupos = {}
    for slug, ag in agentes.items():
        coords, lugar, accion = ubicacion_en_tiempo(ag, t_virtual)
        grupos.setdefault(lugar, []).append((slug, coords, accion))
    # Filtrar solo grupos con >= 2 personas
    return {lugar: miembros for lugar, miembros in grupos.items()
            if len(miembros) >= 2}


def main():
    args = parsear_args()
    if not HAVE_ENGINE:
        print("[ERROR] motor_simulacion.py no disponible.")
        return

    print("=" * 70)
    print(" SIMULACION FORENSE GEOGRAFICA - TELLO, HUILA 2026")
    print("=" * 70)
    print(f"Nivel:       {args.nivel} ({['basico', 'con relaciones',
                                           'con probabilidad', 'con LLM'][args.nivel-1]})")
    print(f"Duracion:    {args.duracion}h")
    print(f"t_inicio:    {args.t_inicio}")
    print(f"Velocidad:   {args.speed}x")
    print(f"Paso:        {args.paso}s")
    print(f"Seed:        {args.seed}")
    print(f"Con LLM:     {args.con_llm}")
    print()

    # Inicializar experimento
    t_inicio = datetime.strptime(args.t_inicio, "%Y-%m-%d %H:%M")
    t_fin = t_inicio + timedelta(hours=args.duracion)

    agentes = cargar_todos_los_agentes()
    escenario = Escenario(
        t_inicial=t_inicio,
        duracion_segundos=(t_fin - t_inicio).total_seconds(),
        agentes=agentes,
        random_seed=args.seed,
        hipotesis=(
            f"Simulacion geografica nivel {args.nivel}, {args.duracion}h. "
            f"Co-presencia segun ruta_diaria. "
            f"{len(agentes)} agentes ({len(AGENTES_GEO)} adultos + "
            f"{len(NINOS) if HAVE_NINOS else 0} ninos)."
        ),
        metadata={
            "tipo": "simulacion_geografica",
            "nivel": args.nivel,
            "con_llm": args.con_llm,
            "duracion_horas": args.duracion,
        },
    )

    exp = Experimento(
        nombre=f"sim_v3_n{args.nivel}_{t_inicio.strftime('%Y%m%d_%H%M')}",
        escenario=escenario,
        version_prompt="2.0",
        directorio_base=args.export,
    )
    exp.reloj.set_velocidad(args.speed)

    # Inicializar motor LLM
    engine = SimulationEngine()
    # Mapear mis slugs a slugs de biografia
    agentes_llm = [a_slug_bio(s) for s in agentes.keys() if not s.startswith("nino_")]
    engine.initialize_agents(agentes_llm)
    exp.nota(f"Simulacion geografica iniciada. Nivel {args.nivel}. "
             f"{len(agentes_llm)} agentes LLM + {len(NINOS) if HAVE_NINOS else 0} ninos.")

    # Snapshot pre-simulacion
    exp.snapshot("inicio")

    # Loop principal
    n_pasos = int((t_fin - t_inicio).total_seconds() // args.paso)
    n_interacciones = 0
    n_dialogos_llm = 0
    costo_total = 0.0
    MAX_LLM_POR_PASO = 5  # Limitar para no saturar

    print(f"\nCorriendo {n_pasos} pasos ({args.paso}s virtuales cada uno)...")
    print("=" * 70)

    for paso in range(n_pasos):
        t_actual = t_inicio + timedelta(seconds=paso * args.paso)
        exp.reloj.saltar_a(t_actual)

        # Detectar co-presencia
        grupos = detectar_copresencia(agentes, t_actual)

        # Limite LLM en este paso
        llm_este_paso = 0

        # Procesar cada grupo
        for lugar, miembros in grupos.items():
            if len(miembros) < 2:
                continue

            # Filtrar ninos (solo intervienen si hay adultos)
            adultos_presentes = [m for m in miembros if not m[0].startswith("nino_")]
            ninos_presentes = [m for m in miembros if m[0].startswith("nino_")]

            # Si solo hay ninos, no simular
            if not adultos_presentes:
                continue

            # Generar interacciones entre pares de adultos
            for i in range(len(adultos_presentes)):
                for j in range(i + 1, len(adultos_presentes)):
                    slug_a, coords_a, accion_a = adultos_presentes[i]
                    slug_b, coords_b, accion_b = adultos_presentes[j]

                    # Distancia (en metros)
                    d = distancia_metros(coords_a, coords_b)

                    # Filtrar por nivel
                    if args.nivel == 1:
                        probabilidad = 1.0
                    elif args.nivel == 2:
                        probabilidad = 0.8
                    elif args.nivel == 3:
                        probabilidad = max(0.1, 1.0 - d / 1000)
                    else:
                        probabilidad = 0.7

                    # Decidir si interactuan
                    if exp._random.random() < probabilidad:
                        # Log
                        exp.inyectar_evento(
                            t=t_actual, tipo="gossip_transmit",
                            payload={
                                "topic": f"(charla casual en {lugar})",
                                "de": slug_a, "a": slug_b,
                                "canal": "presencial",
                                "lugar": lugar,
                                "distancia_m": round(d, 1),
                                "probabilidad": round(probabilidad, 2),
                            }
                        )
                        n_interacciones += 1

                        # Si hay ninos presentes, registrar
                        if ninos_presentes:
                            ninos_str = ", ".join([n[0] for n in ninos_presentes])
                            exp.inyectar_evento(
                                t=t_actual, tipo="observacion_manual",
                                payload={
                                    "observacion": f"Ninos presentes: {ninos_str}",
                                    "lugar": lugar,
                                }
                            )

                        # Si con_llm, llamar al LLM (con sampling + limite por paso)
                        if (args.con_llm and
                            llm_este_paso < MAX_LLM_POR_PASO and
                            exp._random.random() < args.llm_sample):
                            llm_este_paso += 1
                            try:
                                slug_a_bio = a_slug_bio(slug_a)
                                slug_b_bio = a_slug_bio(slug_b)
                                # Buscar el slug real iterando por nombre completo
                                real_slug_a = None
                                real_slug_b = None
                                for s, ag in engine.active_agents.items():
                                    nombre_lower = ag.name.lower()
                                    partes_a = [p for p in slug_a_bio.lower().split()
                                                if p not in ("don", "dona", "doña", "el", "la")]
                                    partes_b = [p for p in slug_b_bio.lower().split()
                                                if p not in ("don", "dona", "doña", "el", "la")]
                                    if all(p in nombre_lower for p in partes_a):
                                        real_slug_a = s
                                    if all(p in nombre_lower for p in partes_b):
                                        real_slug_b = s

                                if not real_slug_a or not real_slug_b:
                                    raise ValueError(
                                        f"No encontre slugs reales para {slug_a_bio}/{slug_b_bio}"
                                    )

                                scene = Scene(
                                    time=t_actual.strftime("%H:%M"),
                                    place=lugar,
                                    weather="27°C, despejado",
                                    people=[slug_a.replace("_", " ").title(),
                                            slug_b.replace("_", " ").title()],
                                    context=f"Encuentro casual. Distancia {d:.0f}m."
                                )
                                results = engine.dialogue_round(
                                    real_slug_a, real_slug_b, scene, n_exchanges=1
                                )
                                for r in results:
                                    exp._log("dialogo_llm", {
                                        "agente": r.agent_name,
                                        "contenido": r.content[:300],
                                        "lugar": lugar,
                                        "tokens_in": r.prompt_tokens,
                                        "tokens_out": r.response_tokens,
                                        "costo": r.cost_usd,
                                    })
                                    costo_total += r.cost_usd
                                n_dialogos_llm += 1
                            except Exception as e:
                                exp._log("error_llm", {"error": str(e)[:200],
                                                       "slug_a": slug_a, "slug_b": slug_b})

        # Progreso cada 10 pasos
        if (paso + 1) % 10 == 0:
            t_progreso = t_actual.strftime("%H:%M")
            print(f"  Paso {paso+1}/{n_pasos} | t={t_progreso} | "
                  f"interacciones={n_interacciones} | "
                  f"dialogos_llm={n_dialogos_llm} | "
                  f"costo=${costo_total:.4f}")

    # Snapshot final
    exp.snapshot("final")
    exp.nota(f"Simulacion completada. {n_interacciones} interacciones, "
             f"{n_dialogos_llm} dialogos LLM, costo ${costo_total:.4f} USD.")

    print()
    print("=" * 70)
    print(" SIMULACION COMPLETADA")
    print("=" * 70)
    print(f"Interacciones:   {n_interacciones}")
    print(f"Dialogos LLM:    {n_dialogos_llm}")
    print(f"Costo total:     ${costo_total:.4f} USD")
    print(f"t_virtual final: {exp.reloj.timestamp_iso()}")

    # Export
    ruta = exp.exportar(comprimir=True)
    print(f"\n[EXPORT] {ruta}")
    d = Dashboard(exp)
    ruta_png = d.render_png()
    if ruta_png:
        print(f"  Dashboard PNG: {ruta_png}")
    ruta_mapa = "experimentos/mapa_tello_2026.png"
    if Path(ruta_mapa).exists():
        print(f"  Mapa:          {ruta_mapa}")


if __name__ == "__main__":
    main()
