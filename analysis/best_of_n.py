# -*- coding: utf-8 -*-
# Sociedad Opita - Best-of-N Sampling para roleplay forense
# https://sociedad.opitacode.com (proximo)
#
"""
analysis/best_of_n.py
=====================
Implementa Best-of-N sampling para seleccionar la mejor respuesta de LLM
en simulacion forense de Sociedad Opita.

MOTIVACION OSINT
================
- ICML 2024 (Stiennon et al.): Best-of-N con reward model es efectivo para
  alinear LLMs con preferencias humanas.
- Wang et al. (NAACL 2025): Self-Consistency mejora accuracy generando N
  trayectorias independientes y seleccionando por votacion mayoritaria.
- Para roleplay, no tenemos reward model, asi que usamos un SCORING
  OBJETIVO basado en:
  1. Coincidencia con marcadores culturales huilenses (keywords)
  2. Coincidencia con perfil Big Five del agente
  3. Presencia de nombres propios / lugares / contexto local
  4. Ausencia de muletillas del LLM base (anti-AI-slop)

METODOLOGIA
===========
1. Generar N=3 muestras por agente con deepseek-chat (temp=1.3, OSINT refinado)
2. Puntuar cada muestra con scoring objetivo multi-criterio
3. Seleccionar la de mayor score
4. Comparar tasa de exito vs single-sample (que era nuestro baseline)

USO
===
>>> from analysis.best_of_n import generar_best_of_n
>>> resultados = generar_best_of_n(['Don Eliecer', 'Don Rosalio'], n=3)
"""

import sys
import io
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import time
from motor_simulacion import SimulationEngine, Scene
import perfiles_psicometricos as pp


# ============================================================================
# SCORING OBJETIVO MULTI-CRITERIO
# ============================================================================

# Marcadores culturales huilenses (region Tello, Huila)
KW_HUILENSES = {
    'aperturas': ['pues', 'pos', 'verá', 'mire', 'eche', 'uy', 'mijito', 'mijita',
                  'comadre', 'pues mire', 'pos sí', 'mijo', 'verá mijo',
                  'a ver mijo', 'pos', 'pos hombre', 'mire pues'],
    'muletillas_conflict': ['qué berraca', 'qué disparate', 'qué verraco',
                             'qué joder', 'no joda', 'qué pereza',
                             'maldita sea', 'qué vaina'],
    'insultos_cariñosos': ['mijo bobo', 'mijita boba', 'bobo', 'pere nontil',
                            'pere nontil', 'pere tantico', 'mi negra',
                            'mi viejo', 'mi vida'],
    'comparaciones_rurales': ['más terco que una mula', 'más bobo que burro viejo',
                                'más arisco que venado', 'más enredado que pelo de negro',
                                'más arrugado que pasa de fique', 'más necio que piedra',
                                'más bragado que gallo', 'más resbaloso que culebra',
                                'más duro que cacho de toro', 'más arisco que gato montés'],
    'contextos_locales': ['finca', 'vereda', 'plaza', 'misa', 'tienda',
                           'taberna', 'lindero', 'fiado', 'compadrazgo',
                           'matanza', 'cosecha', 'ganado', 'tambo',
                           'matarredonda', 'acueducto', 'cerro neiva',
                           'el parque', 'la iglesia'],
    'aplausos_negativos': ['qué pesar', 'qué vaina', 'eso sí es verraco',
                            'eso no se hace', 'qué abuso'],
    'muletillas_devocion': ['con la bendicion de dios', 'gracias a dios',
                              'ay dios mio', 'dios mio', 'si dios quiere',
                              'si dios nos ayuda', 'la virgen'],
}

# Palabras del LLM base que NO son del personaje (anti-AI-slop)
KW_LLM_TICS = [
    'con todo respeto', 'con el debido respeto', 'le sugiero',
    'le recomiendo', 'podriamos buscar una solucion',
    'encontremos una solucion', 'dialoguemos', 'conversemos sobre',
    'es importante senalar', 'cabe destacar', 'sin lugar a dudas',
    'en conclusion', 'es fundamental', 'amigo mio',
    'estimado', 'senor usuario', 'le propongo',
]

# Marcadores de confrontación para A-bajo
KW_CONFRONT_A_BAJO = [
    'no me venga', 'no señor', 'le digo que no', 'carajo', 'le juro',
    'me vale', 'no me busque', 'no sea güevón', 'no me salga',
    'más terco que', 'más bobo que', 'no me hable más',
    'a mí no me', 'conmigo no', 'ni modo', 'ni se le ocurra',
    'no me interesa', 'yo no voy a', 'no pienso',
]

# Marcadores prosociales para A-alto
KW_PROSOCIAL_A_ALTO = [
    'ay mija', 'ay mijo', 'ayudar', 'con dios', 'bendición',
    'tranquila', 'tranquilo', 'no se preocupe', 'aquí estoy',
    'cuénteme', 'con calma', 'entre nos', 'mi amor',
    'siéntese', 'siéntense', 'pase pase', 'cuénteme todo',
    'aquí estamos', 'no está sola', 'no está solo',
]


def score_text(text, perfil_bf, perfil_rasgos):
    """Calcula score objetivo de un output de LLM contra el perfil esperado.

    Returns: dict con subscores y total
    """
    text_lower = text.lower()

    # 1. Huilensidad: presencia de marcadores culturales
    huilensidad = 0
    huilensidad_detalle = {}
    for categoria, kws in KW_HUILENSES.items():
        count = sum(1 for kw in kws if kw in text_lower)
        huilensidad += count
        huilensidad_detalle[categoria] = count

    # 2. Anti-LLM-slop: PENALIZACION por cada tico del LLM base
    llm_tics = sum(1 for tic in KW_LLM_TICS if tic in text_lower)

    # 3. Coherencia Big Five: según A del perfil
    A = perfil_bf['A']
    if A <= 40:
        # Esperamos confrontación
        confrontacion = sum(1 for kw in KW_CONFRONT_A_BAJO if kw in text_lower)
        prosocial = sum(1 for kw in KW_PROSOCIAL_A_ALTO if kw in text_lower)
        # Bonus por confrontacion, penalty por prosocial excesivo
        coherencia = confrontacion - (prosocial * 0.5)
        max_coherencia = 5
    elif A >= 75:
        # Esperamos prosocial
        confrontacion = sum(1 for kw in KW_CONFRONT_A_BAJO if kw in text_lower)
        prosocial = sum(1 for kw in KW_PROSOCIAL_A_ALTO if kw in text_lower)
        # Bonus por prosocial, penalty por confrontacion excesiva
        coherencia = prosocial - (confrontacion * 0.5)
        max_coherencia = 5
    else:
        # A medio: equilibrio
        confrontacion = sum(1 for kw in KW_CONFRONT_A_BAJO if kw in text_lower)
        prosocial = sum(1 for kw in KW_PROSOCIAL_A_ALTO if kw in text_lower)
        coherencia = (confrontacion + prosocial) * 0.5
        max_coherencia = 3

    # 4. Score final ponderado
    # Huilensidad (peso 2.0) — el patron cultural es lo MAS importante
    # Coherencia Big Five (peso 2.5) — fidelidad al perfil
    # Anti-LLM-slop (peso -1.0) — penaliza muletillas del modelo
    score_total = (
        huilensidad * 2.0
        + coherencia * 2.5
        - llm_tics * 1.0
    )

    return {
        'total': score_total,
        'huilensidad': huilensidad,
        'huilensidad_detalle': huilensidad_detalle,
        'coherencia': coherencia,
        'confrontacion': confrontacion,
        'prosocial': prosocial,
        'llm_tics': llm_tics,
        'max_coherencia': max_coherencia,
    }


# ============================================================================
# BEST-OF-N SAMPLING
# ============================================================================

def generar_best_of_n(nombres_agentes, n=3, escena_fn=None, output_dir=None):
    """Genera N muestras por agente y selecciona la mejor segun scoring objetivo.

    Args:
        nombres_agentes: lista de nombres como aparecen en biografias
        n: numero de muestras por agente (default 3)
        escena_fn: funcion(slug) -> contexto de la escena
        output_dir: directorio donde guardar resultados

    Returns:
        dict {nombre_agente: {'mejor': {...}, 'todas': [{...}, ...]}}
    """
    engine = SimulationEngine()
    agents = engine.initialize_agents(nombres_agentes)

    SLUG_TO_NOMBRE = {
        'elicer-perdomo-motta-el-patrn': 'Don Eliécer',
        'rosalo-quintero-hernndez-el-rival': 'Don Rosalío',
        'eliseo-mendoza-trujillo-el-boticario': 'Don Eliseo',
        'jhon-elicer-perdomo-el-hijo-del-patrn': 'Jhon Eliécer',
        'patricia-losada-motta-la-comisaria': 'Patricia',
        'prudencia-gutirrez-vda-de-perdomo-la-partera': 'Doña Prudencia',
        'rosa-elvira-trujillo-de-perdomo-la-tendera': 'Doña Rosa',
        'cecilio-ramrez-lozano-el-cura': 'Padre Cecilio',
    }

    # Mapeo inverso: slug prompt_builder -> slug perfil (underscore)
    SLUG_BIO_TO_PERFIL = {
        'elicer-perdomo-motta-el-patrn': 'don_eliecer_patron',
        'rosalo-quintero-hernndez-el-rival': 'don_rosalio_rival',
        'eliseo-mendoza-trujillo-el-boticario': 'don_eliseo_boticario',
        'jhon-elicer-perdomo-el-hijo-del-patrn': 'jhon_eliecer_hijo_patron',
        'patricia-losada-motta-la-comisaria': 'patricia_comisaria',
        'prudencia-gutirrez-vda-de-perdomo-la-partera': 'dona_prudencia_partera',
        'rosa-elvira-trujillo-de-perdomo-la-tendera': 'dona_rosa_tendera',
        'cecilio-ramrez-lozano-el-cura': 'padre_cecilio_cura',
    }

    # Escenas default (mismas que validacion v2)
    default_escenas = {
        'Don Eliécer': 'Don Rosalío llegó a la tranquera a reclamar por linderos',
        'Don Rosalío': 'Don Eliécer mandó un peón a mover una cerca del lindero',
        'Don Eliseo': 'Un borracho del pueblo llega a pedirle inyectables sin fórmula',
        'Jhon Eliécer': 'Su papá el Patrón le dice que no se puede ir a Bogotá',
        'Patricia': 'Llegan esposas del Patrón pidiendo ayuda, él acaba de amenazarlas',
        'Doña Prudencia': 'Una parturienta con complicaciones llegó de madrugada',
        'Doña Rosa': 'Una vecina le cuenta que vio al marido de X con otra mujer',
        'Padre Cecilio': 'Dos feligreses se están peleando afuera del templo',
    }

    resultados = {}
    total_cost = 0

    for slug, agent in agents.items():
        nombre_key = SLUG_TO_NOMBRE.get(slug, agent.name.split(' (')[0])
        contexto = (escena_fn(slug) if escena_fn else None) or default_escenas.get(nombre_key, '')
        if not contexto:
            continue
        # Buscar perfil para scoring
        perfil_slug = SLUG_BIO_TO_PERFIL.get(slug)
        perfil = pp.PERFILES_ADULTOS.get(perfil_slug) if perfil_slug else None
        if not perfil:
            print(f'  [skip] {nombre_key}: no encontre perfil para slug={slug}')
            continue
        bf = perfil['big_five']


        # Generar N muestras
        muestras = []
        for i in range(n):
            scene = Scene(time='10:00', place='Tello', weather='26°C',
                          people=[], context=contexto)
            t0 = time.time()
            try:
                r = engine.run_round(slug, scene, save_memory=False)
                dt = time.time() - t0
                total_cost += r.cost_usd
                score = score_text(r.content, bf, perfil['rasgos'])
                muestras.append({
                    'output': r.content,
                    'cost': r.cost_usd,
                    'latencia': dt,
                    'score': score,
                })
                print(f'  {nombre_key} [{i}] score={score["total"]:+.1f} done in {dt:.1f}s')
            except Exception as e:
                muestras.append({'error': str(e)})

        # Seleccionar la mejor (mayor score)
        muestras_validas = [m for m in muestras if 'score' in m]
        if muestras_validas:
            mejor = max(muestras_validas, key=lambda m: m['score']['total'])
        else:
            mejor = None

        resultados[nombre_key] = {
            'slug': slug,
            'perfil': bf,
            'contexto': contexto,
            'muestras': muestras,
            'mejor': mejor,
            'mejor_idx': muestras_validas.index(mejor) if mejor else None,
        }

    # Guardar
    if output_dir is None:
        # Path portable: directorio raiz del repo / demo_output
        # (best_of_n.py vive en analysis/, asi que subimos un nivel)
        output_dir = Path(__file__).resolve().parent.parent / "demo_output"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    out_path = output_dir / 'validacion_best_of_n.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        # Convert Path in results
        def make_serializable(obj):
            if isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [make_serializable(x) for x in obj]
            return obj
        json.dump(make_serializable(resultados), f, indent=2, ensure_ascii=False)

    return resultados


def imprimir_reporte(resultados):
    """Imprime resumen de resultados best-of-n."""
    print()
    print('#' * 70)
    print('#' + ' BEST-OF-N SAMPLING — SOCIEDAD OPITA '.center(68) + '#')
    print('#' * 70)
    print()

    for nombre, data in resultados.items():
        if not data.get('muestras'):
            continue
        bf = data['perfil']
        mejor = data.get('mejor')
        if not mejor:
            continue

        score = mejor['score']
        n_muestras = len(data['muestras'])

        print(f'>>> {nombre} (Big Five: O={bf["O"]} C={bf["C"]} E={bf["E"]} A={bf["A"]} N={bf["N"]})')
        print(f'    N muestras: {n_muestras}, mejor idx: {data["mejor_idx"]}')
        print(f'    Score total: {score["total"]:.1f}')
        print(f'      Huilensidad: {score["huilensidad"]} {score["huilensidad_detalle"]}')
        print(f'      Coherencia: {score["coherencia"]:.1f} (confront={score["confrontacion"]}, prosocial={score["prosocial"]})')
        print(f'      LLM tics (penalizados): {score["llm_tics"]}')
        print(f'    Output ganador:')
        print(f'      "{mejor["output"]}"')
        print()

        # Mostrar comparación de las 3 muestras
        print(f'    Comparativa de las {n_muestras} muestras:')
        for i, m in enumerate(data['muestras']):
            if 'score' not in m:
                continue
            label = ' [MEJOR]' if i == data['mejor_idx'] else ''
            print(f'      [{i}] score={m["score"]["total"]:+.1f} hui={m["score"]["huilensidad"]} '
                  f'coh={m["score"]["coherencia"]:+.1f}{label}')
            print(f'          "{m["output"][:120]}{"..." if len(m["output"]) > 120 else ""}"')
        print()


if __name__ == '__main__':
    # UTF-8 stdout para consola Windows
    import sys as _sys
    _sys.stdout = io.TextIOWrapper(_sys.stdout.buffer, encoding='utf-8')

    print('Generando best-of-n (N=3) para 8 agentes...')
    resultados = generar_best_of_n(
        nombres_agentes=[
            'Don Eliécer', 'Don Rosalío', 'Don Eliseo', 'Jhon Eliécer',
            'Patricia', 'Doña Prudencia', 'Doña Rosa', 'Padre Cecilio',
        ],
        n=3,
    )
    imprimir_reporte(resultados)
    print()
    print(f'[JSON] demo_output/validacion_best_of_n.json')