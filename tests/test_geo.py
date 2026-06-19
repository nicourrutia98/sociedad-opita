# -*- coding: utf-8 -*-
# Sociedad Opita - Tests
# https://sociedad.opitacode.com (proximo)
#
"""
tests/test_geo.py
=================
Tests para el modulo de geografia (geo_tello.py).

USO:
    python tests/test_geo.py
"""

import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from geo_tello import (
    EDIFICIOS, AGENTES_GEO, distancia, distancia_metros,
    agentes_en_rango, matriz_distancias, SLUG_BIO,
)


def test_edificios_tienen_campos_requeridos():
    """Cada edificio tiene los 6 campos forenses requeridos."""
    campos = {"tipo", "coords", "direccion", "fuente", "confianza", "notas"}
    for eid, ed in EDIFICIOS.items():
        for campo in campos:
            assert campo in ed, f"Edificio {eid} falta campo '{campo}'"
    print("  [OK] test_edificios_tienen_campos_requeridos")


def test_agentes_tienen_casa_y_trabajo():
    """Cada agente tiene casa_coords y (opcionalmente) trabajo_coords."""
    for slug, ag in AGENTES_GEO.items():
        assert "casa_coords" in ag, f"Agente {slug} falta casa_coords"
        assert isinstance(ag["casa_coords"], tuple), \
            f"Agente {slug} casa_coords no es tupla"
        assert len(ag["casa_coords"]) == 2, \
            f"Agente {slug} casa_coords debe tener 2 elementos"
    print("  [OK] test_agentes_tienen_casa_y_trabajo")


def test_agentes_tienen_ruta_diaria():
    """Cada agente tiene ruta_diaria con items (hora, lugar, accion)."""
    for slug, ag in AGENTES_GEO.items():
        assert "ruta_diaria" in ag, f"Agente {slug} falta ruta_diaria"
        assert len(ag["ruta_diaria"]) >= 3, \
            f"Agente {slug} ruta_diaria muy corta"
        for item in ag["ruta_diaria"]:
            assert len(item) >= 3, \
                f"Agente {slug} item de ruta debe ser (hora, lugar, accion)"
    print("  [OK] test_agentes_tienen_ruta_diaria")


def test_distancia_euclidiana():
    """Distancia euclidiana entre dos puntos."""
    d = distancia((0, 0), (3, 4))
    assert abs(d - 5.0) < 0.001, f"Esperado 5.0, obtenido {d}"
    d = distancia((1, 1), (4, 5))
    assert abs(d - 5.0) < 0.001
    d = distancia((0, 0), (0, 0))
    assert d == 0
    print("  [OK] test_distancia_euclidiana")


def test_distancia_metros():
    """1 unidad = 30 metros."""
    d = distancia_metros((0, 0), (1, 0))
    assert d == 30, f"Esperado 30m, obtenido {d}m"
    d = distancia_metros((0, 0), (10, 0))
    assert d == 300
    print("  [OK] test_distancia_metros")


def test_agentes_en_rango():
    """Lista de agentes dentro de un radio (ordenado por distancia)."""
    agentes = agentes_en_rango((0, 0), 100)  # ~3.33 unidades
    # Todos deben estar dentro de 100m del origen
    for nombre, dist in agentes:
        assert dist * 30 <= 100, f"Agente {nombre} fuera de rango"
    # Deben estar ordenados por distancia
    distancias = [d for _, d in agentes]
    assert distancias == sorted(distancias)
    # Debe haber al menos el alcalde (cerca de la plaza)
    nombres = [n for n, _ in agentes]
    assert any("alcalde" in n for n in nombres), \
        "Deberia incluir al menos el alcalde cerca de la plaza"
    print("  [OK] test_agentes_en_rango")


def test_matriz_distancias_simetrica():
    """La matriz de distancias es simetrica."""
    matriz = matriz_distancias()
    agentes = list(matriz.keys())
    for a in agentes[:5]:  # sample
        for b in agentes[:5]:
            d_ab = matriz[a][b]
            d_ba = matriz[b][a]
            assert abs(d_ab - d_ba) < 0.001, \
                f"Distancias asimetricas: {a}-{b}={d_ab}, {b}-{a}={d_ba}"
    print("  [OK] test_matriz_distancias_simetrica")


def test_matriz_distancias_diagonal_cero():
    """Distancia de un agente a si mismo es 0."""
    matriz = matriz_distancias()
    for agente, dists in matriz.items():
        assert dists[agente] == 0, \
            f"Distancia {agente}-{agente} = {dists[agente]}, deberia ser 0"
    print("  [OK] test_matriz_distancias_diagonal_cero")


def test_slug_bio_cubre_agentes_principales():
    """SLUG_BIO mapea los agentes principales."""
    principales = [
        "don_eliecer_patron", "dona_rosa_tendera",
        "don_fernando_alcalde", "padre_cecilio_cura",
        "caliche_minero", "laura_reina",
    ]
    for slug in principales:
        assert slug in SLUG_BIO, \
            f"Falta mapeo SLUG_BIO para {slug}"
        assert SLUG_BIO[slug] != slug, \
            f"SLUG_BIO[{slug}] no transformado"
    print("  [OK] test_slug_bio_cubre_agentes_principales")


def test_confianza_edificios_en_rango():
    """Todos los edificios tienen confianza entre 0 y 1."""
    for eid, ed in EDIFICIOS.items():
        c = ed.get("confianza", 1.0)
        assert 0.0 <= c <= 1.0, \
            f"Edificio {eid} confianza {c} fuera de [0, 1]"
    print("  [OK] test_confianza_edificios_en_rango")


def test_plaza_bolivar_es_origen():
    """Plaza Bolivar debe estar en (0, 0)."""
    plaza = EDIFICIOS.get("plaza_bolivar")
    assert plaza is not None, "Plaza Bolivar no encontrada"
    assert plaza["coords"] == (0, 0), \
        f"Plaza en {plaza['coords']}, deberia ser (0, 0)"
    print("  [OK] test_plaza_bolivar_es_origen")


def main():
    print("=" * 60)
    print(" TESTS - Geografia (geo_tello.py)")
    print("=" * 60)
    tests = [
        test_edificios_tienen_campos_requeridos,
        test_agentes_tienen_casa_y_trabajo,
        test_agentes_tienen_ruta_diaria,
        test_distancia_euclidiana,
        test_distancia_metros,
        test_agentes_en_rango,
        test_matriz_distancias_simetrica,
        test_matriz_distancias_diagonal_cero,
        test_slug_bio_cubre_agentes_principales,
        test_confianza_edificios_en_rango,
        test_plaza_bolivar_es_origen,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  [FAIL] {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  [ERROR] {test.__name__}: {type(e).__name__}: {e}")
            failed += 1
    print()
    print(f"Resultado: {passed} OK, {failed} FAIL")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
