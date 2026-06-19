# -*- coding: utf-8 -*-
# Sociedad Opita - Analisis Estadistico de Perfiles Psicometricos
# https://sociedad.opitacode.com (proximo)
#
"""
analysis/estadistica.py
========================
Estadistica descriptiva e inferencial sobre los 26 perfiles psicometricos
(Big Five + Lomnitz + Dunbar) de Sociedad Opita.

OBJETIVO
=========
Caracterizar la distribucion de Big Five en la poblacion simulada de Tello,
validar la coherencia interna de los perfiles (correlaciones teoricamente
esperadas), y producir intervalos de confianza via bootstrap sobre metricas
de red agregadas.

METODOLOGIA
===========
1. **Estadistica descriptiva**:
   - Media, mediana, std, min, max, IQR por factor Big Five
   - Distribucion categorica Lomnitz (A/B/C)
   - Distribucion por capa Dunbar (intimos vs buenos)
   - Histogramas normalizados

2. **Validacion de coherencia interna**:
   - Correlacion Pearson entre los 5 factores Big Five
   - Hipotesis: ciertos pares deberian correlacionar teoricamente:
     * A-C (amabilidad-concienzudismo): +0.2 a +0.4 (Block 1995)
     * A-E (amabilidad-extraversion): +0.2 a +0.3 (Costa & McCrae 1992)
     * O-E (apertura-extraversion): +0.2 a +0.3
     * N-E (neuroticismo-extraversion): -0.2 a -0.4 (Watson 1988)
   - Si nuestras correlaciones caen FUERA de estos rangos, sugiere que los
     perfiles fueron generados con ruido aleatorio o sin coherencia interna.

3. **Bootstrap CI**:
   - 10,000 remuestreos con reemplazo (n=26)
   - 95% CI por percentiles (2.5%, 97.5%) sobre la media de cada factor
   - Util para comparar con la base poblacional Colombia (Schmitt 2007)

4. **Mann-Whitney U** (analisis categorico):
   - Compara scores Big Five entre grupos Lomnitz (A vs B vs C)
   - H1: patron-jornalero (C) tiene A mas bajo que compadres (A)
   - H0: las distribuciones son iguales

USO
===
>>> from analysis.estadistica import analizar_perfiles, validar_coherencia
>>> resultados = analizar_perfiles()
>>> validar_coherencia()

>>> python analysis/estadistica.py  # genera reporte completo en terminal
"""

import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))

import perfiles_psicometricos as pp
import numpy as np

# ============================================================================
# 1. ESTADISTICA DESCRIPTIVA
# ============================================================================

FACTORES = ("O", "C", "E", "A", "N")
NOMBRES = {
    "O": "Apertura",
    "C": "Concienzudismo",
    "E": "Extraversion",
    "A": "Amabilidad",
    "N": "Neuroticismo",
}

# Base poblacional Colombia normalizada a 0-100
# Schmitt et al. 2007 (JCCP), Tabla 3, Colombia n~400
BASE_COLOMBIA = {"O": 47, "C": 44, "E": 50, "A": 47, "N": 52}


def estadistica_descriptiva():
    """Calcula estadistica descriptiva por factor Big Five."""
    perfiles = pp.PERFILES_ADULTOS
    n = len(perfiles)

    resultados = {}
    for factor in FACTORES:
        scores = [p["big_five"][factor] for p in perfiles.values()]
        arr = np.array(scores, dtype=float)
        resultados[factor] = {
            "n": n,
            "media": float(np.mean(arr)),
            "mediana": float(np.median(arr)),
            "std": float(np.std(arr, ddof=1)),  # ddof=1 = sample std
            "min": int(np.min(arr)),
            "max": int(np.max(arr)),
            "q25": float(np.percentile(arr, 25)),
            "q75": float(np.percentile(arr, 75)),
            "iqr": float(np.percentile(arr, 75) - np.percentile(arr, 25)),
            "scores": scores,
        }
    return resultados


def distribucion_lomnitz():
    """Cuenta agentes por categoria Lomnitz default."""
    perfiles = pp.PERFILES_ADULTOS
    cats = Counter(p["lomnitz_default"] for p in perfiles.values())
    n = len(perfiles)
    return {
        "A": {"n": cats.get("A", 0), "pct": cats.get("A", 0) / n * 100},
        "B": {"n": cats.get("B", 0), "pct": cats.get("B", 0) / n * 100},
        "C": {"n": cats.get("C", 0), "pct": cats.get("C", 0) / n * 100},
    }


def distribucion_dunbar():
    """Estadisticas de las capas Dunbar (intimos=5, buenos=15)."""
    perfiles = pp.PERFILES_ADULTOS
    # Asimetria: cuenta enlaces unicos (grafo dirigido)
    enlaces_intimos = set()
    enlaces_buenos = set()
    for slug_origen, perfil in perfiles.items():
        for d in perfil["dunbar"]["intimos"]:
            enlaces_intimos.add((slug_origen, d))
        for d in perfil["dunbar"]["buenos"]:
            enlaces_buenos.add((slug_origen, d))

    # Auto-referencias
    auto_intimos = sum(1 for o, d in enlaces_intimos if o == d)
    auto_buenos = sum(1 for o, d in enlaces_buenos if o == d)

    # Asimetria: (a -> b) sin (b -> a)
    reciprocos_intimos = sum(
        1 for o, d in enlaces_intimos
        if (d, o) in enlaces_intimos and o < d  # evitar doble conteo
    )
    asimetria_intimos = len(enlaces_intimos) - 2 * reciprocos_intimos

    reciprocos_buenos = sum(
        1 for o, d in enlaces_buenos
        if (d, o) in enlaces_buenos and o < d
    )
    asimetria_buenos = len(enlaces_buenos) - 2 * reciprocos_buenos

    # In/out-degree
    in_degree_intimos = Counter()
    out_degree_intimos = Counter()
    for o, d in enlaces_intimos:
        out_degree_intimos[o] += 1
        in_degree_intimos[d] += 1
    in_degree_buenos = Counter()
    out_degree_buenos = Counter()
    for o, d in enlaces_buenos:
        out_degree_buenos[o] += 1
        in_degree_buenos[d] += 1

    return {
        "n_perfiles": len(perfiles),
        "intimos": {
            "n_enlaces_dirigidos": len(enlaces_intimos),
            "n_esperado": len(perfiles) * 5,
            "auto_referencias": auto_intimos,
            "reciprocos": reciprocos_intimos,
            "asimetricos": asimetria_intimos,
            "pct_asimetria": asimetria_intimos / len(enlaces_intimos) * 100,
            "in_degree_top": in_degree_intimos.most_common(5),
            "out_degree_top": out_degree_intimos.most_common(5),
        },
        "buenos": {
            "n_enlaces_dirigidos": len(enlaces_buenos),
            "n_esperado": len(perfiles) * 15,
            "auto_referencias": auto_buenos,
            "reciprocos": reciprocos_buenos,
            "asimetricos": asimetria_buenos,
            "pct_asimetria": asimetria_buenos / len(enlaces_buenos) * 100,
            "in_degree_top": in_degree_buenos.most_common(5),
            "out_degree_top": out_degree_buenos.most_common(5),
        },
    }


# ============================================================================
# 2. BOOTSTRAP CI SOBRE MEDIAS BIG FIVE
# ============================================================================

def bootstrap_ci(scores, n_boot=10000, ci=0.95, seed=42):
    """Bootstrap confidence interval sobre la media de un vector de scores.

    Returns: (media, ci_low, ci_high, std_error)
    """
    rng = np.random.default_rng(seed)
    arr = np.array(scores, dtype=float)
    n = len(arr)
    medias = np.empty(n_boot)
    for i in range(n_boot):
        muestra = rng.choice(arr, size=n, replace=True)
        medias[i] = muestra.mean()
    alpha = (1 - ci) / 2
    ci_low = float(np.percentile(medias, alpha * 100))
    ci_high = float(np.percentile(medias, (1 - alpha) * 100))
    return {
        "media": float(arr.mean()),
        "ci_low": ci_low,
        "ci_high": ci_high,
        "std_error": float(medias.std()),
        "n_boot": n_boot,
    }


# ============================================================================
# 3. VALIDACION DE COHERENCIA INTERNA (correlaciones teoricas)
# ============================================================================

# Pares teoricamente correlacionados (rango esperado basado en literatura)
CORRELACIONES_ESPERADAS = {
    ("A", "C"): {"rango": (0.2, 0.4), "fuente": "Costa & McCrae 1992"},
    ("A", "E"): {"rango": (0.2, 0.3), "fuente": "Costa & McCrae 1992"},
    ("O", "E"): {"rango": (0.2, 0.3), "fuente": "Watson 1988"},
    ("N", "E"): {"rango": (-0.4, -0.2), "fuente": "Watson 1988"},
    ("O", "C"): {"rango": (0.0, 0.2), "fuente": "Block 1995"},
}


def correlacion_pearson(x, y):
    """Coeficiente de correlacion Pearson entre dos vectores."""
    x_arr = np.array(x, dtype=float)
    y_arr = np.array(y, dtype=float)
    if len(x_arr) < 3:
        return float("nan")
    return float(np.corrcoef(x_arr, y_arr)[0, 1])


def validar_coherencia(descriptiva=None):
    """Compara las correlaciones observadas con los rangos teoricos.

    Retorna True si TODAS las correlaciones caen en su rango esperado.
    False si alguna cae fuera (señal de perfiles sin coherencia interna).
    """
    if descriptiva is None:
        descriptiva = estadistica_descriptiva()

    print()
    print("=" * 70)
    print("VALIDACION DE COHERENCIA INTERNA (correlaciones Big Five)")
    print("=" * 70)
    print(f"{'Par':<8}{'r_observado':>14}{'r_esperado':>16}{'fuente':<30}{'OK?'}")
    print("-" * 70)
    todo_ok = True
    for (f1, f2), esperado in CORRELACIONES_ESPERADAS.items():
        r_obs = correlacion_pearson(
            descriptiva[f1]["scores"],
            descriptiva[f2]["scores"],
        )
        r_min, r_max = esperado["rango"]
        en_rango = r_min <= r_obs <= r_max
        ok = "OK" if en_rango else "FUERA"
        if not en_rango:
            todo_ok = False
        print(f"{f1}-{f2:<6}{r_obs:>14.3f}    [{r_min:+.1f}, {r_max:+.1f}]    "
              f"{esperado['fuente']:<30}{ok}")
    print("-" * 70)
    print(f"Resultado: {'COHERENTE con literatura' if todo_ok else 'INCOHERENTE - revisar perfiles'}")
    return todo_ok


# ============================================================================
# 4. COMPARACION CON BASE POBLACIONAL COLOMBIA
# ============================================================================

def comparar_con_base(descriptiva=None):
    """Compara la media de Tello con la base Colombia (Schmitt 2007).

    Si la media de Tello cae FUERA del 95% CI bootstrap, sugiere diferencia
    poblacional real (no ruido muestral).
    """
    if descriptiva is None:
        descriptiva = estadistica_descriptiva()

    print()
    print("=" * 70)
    print("COMPARACION CON BASE POBLACIONAL COLOMBIA (Schmitt 2007)")
    print("=" * 70)
    print(f"{'Factor':<14}{'Media Tello':>14}{'IC 95%':>22}{'Colombia':>12}{'Diferencia':>14}{'OK?'}")
    print("-" * 70)
    for factor in FACTORES:
        ci = bootstrap_ci(descriptiva[factor]["scores"])
        base = BASE_COLOMBIA[factor]
        diff = ci["media"] - base
        # Test: ¿el valor de Colombia cae dentro del CI de Tello?
        en_ci = ci["ci_low"] <= base <= ci["ci_high"]
        ok = "dentro" if en_ci else "FUERA"
        print(f"{NOMBRES[factor]:<14}{ci['media']:>14.1f}"
              f"  [{ci['ci_low']:5.1f}, {ci['ci_high']:5.1f}]"
              f"{base:>12}{diff:>+14.1f}   {ok}")
    print()


# ============================================================================
# 5. MANN-WHITNEY U POR CATEGORIA LOMNITZ
# ============================================================================

def comparar_lomnitz(descriptiva=None):
    """Mann-Whitney U entre grupos Lomnitz (A vs B, A vs C, B vs C).

    H1: patron-jornalero (Lomnitz C) tiene Amabilidad mas baja que compadres (A).
    H0: distribuciones son iguales.
    """
    if descriptiva is None:
        descriptiva = estadistica_descriptiva()

    perfiles = pp.PERFILES_ADULTOS

    # Agrupa scores por Lomnitz
    grupos = {"A": [], "B": [], "C": []}
    for slug, perfil in perfiles.items():
        grupos[perfil["lomnitz_default"]].append(slug)

    print()
    print("=" * 70)
    print("COMPARACION BIG FIVE POR CATEGORIA LOMNITZ")
    print("=" * 70)
    print(f"Grupos: A={len(grupos['A'])} agentes, B={len(grupos['B'])}, C={len(grupos['C'])}")
    print()

    # Mann-Whitney U manual (sin scipy dependency)
    def mann_whitney_u(x, y):
        """Calcula U y p-value aproximado via aproximacion normal."""
        nx, ny = len(x), len(y)
        if nx == 0 or ny == 0:
            return float("nan"), float("nan")
        # Rank combined
        combined = [(v, "x") for v in x] + [(v, "y") for v in y]
        combined.sort(key=lambda t: t[0])
        ranks = {}
        for i, (v, src) in enumerate(combined, start=1):
            ranks.setdefault(v, []).append(i)
        # Average rank for ties
        avg_ranks = {}
        for v, rs in ranks.items():
            avg_ranks[v] = sum(rs) / len(rs)
        # Sum of ranks for x
        rx = sum(avg_ranks[v] for v in x)
        u_x = rx - nx * (nx + 1) / 2
        u_y = nx * ny - u_x
        u = min(u_x, u_y)
        # Normal approximation (sin ties correction)
        mu_u = nx * ny / 2
        sigma_u = (nx * ny * (nx + ny + 1) / 12) ** 0.5
        if sigma_u == 0:
            return u, 1.0
        z = (u - mu_u) / sigma_u
        # Two-tailed p-value (approx, sin libreria)
        # Para z>=0: p = 2 * (1 - Phi(z))
        # Phi approx: 0.5 * (1 + erf(z / sqrt(2)))
        from math import erf, sqrt
        phi = 0.5 * (1 + erf(abs(z) / sqrt(2)))
        p = 2 * (1 - phi)
        return u, p

    print(f"{'Factor':<14}{'A vs B (p)':>14}{'A vs C (p)':>14}{'B vs C (p)':>14}")
    print("-" * 60)
    for factor in FACTORES:
        scores_a = [pp.PERFILES_ADULTOS[s]["big_five"][factor] for s in grupos["A"]]
        scores_b = [pp.PERFILES_ADULTOS[s]["big_five"][factor] for s in grupos["B"]]
        scores_c = [pp.PERFILES_ADULTOS[s]["big_five"][factor] for s in grupos["C"]]
        u_ab, p_ab = mann_whitney_u(scores_a, scores_b)
        u_ac, p_ac = mann_whitney_u(scores_a, scores_c)
        u_bc, p_bc = mann_whitney_u(scores_b, scores_c)
        sig_ab = "*" if p_ab < 0.05 else ""
        sig_ac = "*" if p_ac < 0.05 else ""
        sig_bc = "*" if p_bc < 0.05 else ""
        print(f"{NOMBRES[factor]:<14}{p_ab:>13.3f}{sig_ab:1}"
              f"{p_ac:>13.3f}{sig_ac:1}{p_bc:>13.3f}{sig_bc:1}")
    print()
    print("* = p < 0.05 (Mann-Whitney U test, aproximacion normal)")
    print()


# ============================================================================
# 6. REPORTES
# ============================================================================

def imprimir_reporte():
    """Imprime reporte completo en terminal."""
    print()
    print("#" * 70)
    print("#" + " ESTADISTICA: PERFILES PSICOMETRICOS SOCIEDAD OPITA ".center(68) + "#")
    print("#" * 70)

    descriptiva = estadistica_descriptiva()
    lomnitz = distribucion_lomnitz()
    dunbar = distribucion_dunbar()

    # 1. Descriptiva
    print()
    print("=" * 70)
    print("1. ESTADISTICA DESCRIPTIVA - BIG FIVE (n=26)")
    print("=" * 70)
    print(f"{'Factor':<14}{'N':>4}{'Media':>8}{'Mediana':>9}{'Std':>8}"
          f"{'Min':>6}{'Max':>6}{'IQR':>8}")
    print("-" * 60)
    for factor in FACTORES:
        d = descriptiva[factor]
        print(f"{NOMBRES[factor]:<14}{d['n']:>4}{d['media']:>8.1f}{d['mediana']:>9.1f}"
              f"{d['std']:>8.1f}{d['min']:>6}{d['max']:>6}{d['iqr']:>8.1f}")
    print()

    # 2. Lomnitz
    print("=" * 70)
    print("2. DISTRIBUCION LOMNITZ")
    print("=" * 70)
    print(f"  A (simetrica):    {lomnitz['A']['n']:>3} ({lomnitz['A']['pct']:>5.1f}%)")
    print(f"  B (generalizada): {lomnitz['B']['n']:>3} ({lomnitz['B']['pct']:>5.1f}%)")
    print(f"  C (negativa):     {lomnitz['C']['n']:>3} ({lomnitz['C']['pct']:>5.1f}%)")
    print()

    # 3. Dunbar
    print("=" * 70)
    print("3. DISTRIBUCION DUNBAR (red social)")
    print("=" * 70)
    print(f"  Perfiles:        {dunbar['n_perfiles']}")
    print(f"  Intimos (5 esperados c/u):")
    print(f"    Enlaces dirigidos: {dunbar['intimos']['n_enlaces_dirigidos']} "
          f"(esperado {dunbar['intimos']['n_esperado']})")
    print(f"    Auto-referencias: {dunbar['intimos']['auto_referencias']}")
    print(f"    Reciprocos:       {dunbar['intimos']['reciprocos']}")
    print(f"    Asimetricos:       {dunbar['intimos']['asimetricos']} "
          f"({dunbar['intimos']['pct_asimetria']:.1f}% del total)")
    print(f"    Top in-degree:    {dunbar['intimos']['in_degree_top']}")
    print(f"    Top out-degree:   {dunbar['intimos']['out_degree_top']}")
    print(f"  Buenos (15 esperados c/u):")
    print(f"    Enlaces dirigidos: {dunbar['buenos']['n_enlaces_dirigidos']} "
          f"(esperado {dunbar['buenos']['n_esperado']})")
    print(f"    Auto-referencias: {dunbar['buenos']['auto_referencias']}")
    print(f"    Reciprocos:       {dunbar['buenos']['reciprocos']}")
    print(f"    Asimetricos:       {dunbar['buenos']['asimetricos']} "
          f"({dunbar['buenos']['pct_asimetria']:.1f}% del total)")
    print(f"    Top in-degree:    {dunbar['buenos']['in_degree_top']}")
    print(f"    Top out-degree:   {dunbar['buenos']['out_degree_top']}")
    print()

    # 4. Coherencia interna
    validar_coherencia(descriptiva)

    # 5. Comparacion con base Colombia
    comparar_con_base(descriptiva)

    # 6. Mann-Whitney por Lomnitz
    comparar_lomnitz(descriptiva)

    print("#" * 70)
    print("#" + " FIN DEL REPORTE ".center(68) + "#")
    print("#" * 70)
    print()


def analizar_perfiles():
    """Funcion principal: retorna diccionario con todos los analisis."""
    return {
        "descriptiva": estadistica_descriptiva(),
        "lomnitz": distribucion_lomnitz(),
        "dunbar": distribucion_dunbar(),
        "bootstrap": {
            factor: bootstrap_ci(estadistica_descriptiva()[factor]["scores"])
            for factor in FACTORES
        },
    }


if __name__ == "__main__":
    imprimir_reporte()