# -*- coding: utf-8 -*-
# Sociedad Opita - Tests
# https://sociedad.opitacode.com (proximo)
#
"""
tests/test_reloj.py
===================
Tests para el reloj virtual (reloj.py).

USO:
    python tests/test_reloj.py
    python -m pytest tests/test_reloj.py -v
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from reloj import Reloj


def test_crear_reloj_basico():
    """Verifica creacion con tiempo inicial."""
    t0 = datetime(2026, 6, 19, 6, 0)
    r = Reloj(t0=t0, velocidad=1.0)
    assert r.ahora() == t0
    assert r.velocidad == 1.0
    assert not r.pausado
    print("  [OK] test_crear_reloj_basico")


def test_avanzar_segundos():
    """Avanzar N segundos virtuales."""
    r = Reloj(t0=datetime(2026, 6, 19, 6, 0))
    r.avanzar(3600)  # 1 hora
    assert r.ahora() == datetime(2026, 6, 19, 7, 0)
    print("  [OK] test_avanzar_segundos")


def test_pausar_reanudar():
    """Pausar detiene avance, reanudar lo reactiva."""
    r = Reloj(t0=datetime(2026, 6, 19, 6, 0))
    r.avanzar(1800)
    r.pausar()
    assert r.pausado
    r.avanzar(3600)  # No debe avanzar
    assert r.ahora() == datetime(2026, 6, 19, 6, 30)
    r.reanudar()
    assert not r.pausado
    r.avanzar(3600)
    assert r.ahora() == datetime(2026, 6, 19, 7, 30)
    print("  [OK] test_pausar_reanudar")


def test_velocidad():
    """Cambiar velocidad funciona."""
    r = Reloj(t0=datetime(2026, 6, 19, 6, 0))
    r.set_velocidad(60)
    assert r.velocidad == 60
    # Avanzar 60 segundos wall con velocidad 60 = 3600 seg virtuales
    r.avanzar_wall(60)
    delta = (r.ahora() - datetime(2026, 6, 19, 6, 0)).total_seconds()
    assert delta == 3600, f"Esperado 3600, obtenido {delta}"
    print("  [OK] test_velocidad")


def test_saltar_a():
    """Salto a timestamp arbitrario."""
    r = Reloj(t0=datetime(2026, 6, 19, 6, 0))
    r.saltar_a(datetime(2026, 6, 24, 18, 0))  # Festival San Juan
    assert r.ahora() == datetime(2026, 6, 24, 18, 0)
    print("  [OK] test_saltar_a")


def test_reset():
    """Reset vuelve a t0 y velocidad inicial."""
    r = Reloj(t0=datetime(2026, 6, 19, 6, 0), velocidad=60)
    r.avanzar(3600)
    r.set_velocidad(3600)
    r.reset()
    assert r.ahora() == datetime(2026, 6, 19, 6, 0)
    assert r.velocidad == 60
    print("  [OK] test_reset")


def test_segundos_transcurridos():
    """Cuenta segundos virtuales desde t0."""
    r = Reloj(t0=datetime(2026, 6, 19, 6, 0))
    r.avanzar(7200)  # 2h
    assert r.segundos_transcurridos() == 7200
    print("  [OK] test_segundos_transcurridos")


def test_historial_cambios():
    """Todos los cambios quedan en historial (audit trail)."""
    r = Reloj(t0=datetime(2026, 6, 19, 6, 0))
    r.set_velocidad(60)
    r.pausar()
    r.reanudar()
    r.saltar_a(datetime(2026, 6, 24, 12, 0))
    # Al menos 4 cambios (init, set_velocidad, pausar, reanudar, saltar_a)
    assert len(r.historial_cambios) >= 4
    acciones = [c["accion"] for c in r.historial_cambios]
    assert "set_velocidad" in acciones
    assert "pausar" in acciones
    assert "reanudar" in acciones
    assert "saltar_a" in acciones
    print("  [OK] test_historial_cambios")


def test_eventos_ancla():
    """Eventos ancla del 2026 son accesibles."""
    from reloj import EVENTOS_ANCLA_2026, parsear_evento_ancla
    t = parsear_evento_ancla("crisis_acueducto_inicio")
    assert t == datetime(2026, 4, 5, 6, 0)
    t = parsear_evento_ancla("festival_san_juan")
    assert t == datetime(2026, 6, 24, 6, 0)
    t = parsear_evento_ancla("reinado_nacional")
    assert t == datetime(2026, 7, 5, 6, 0)
    print("  [OK] test_eventos_ancla")


def test_estado_serializable():
    """Estado del reloj es JSON-serializable."""
    import json
    r = Reloj(t0=datetime(2026, 6, 19, 6, 0))
    r.set_velocidad(60)
    estado = r.estado()
    # Debe poder serializarse a JSON
    json.dumps(estado, default=str)
    print("  [OK] test_estado_serializable")


def main():
    print("=" * 60)
    print(" TESTS - Reloj virtual")
    print("=" * 60)
    tests = [
        test_crear_reloj_basico,
        test_avanzar_segundos,
        test_pausar_reanudar,
        test_velocidad,
        test_saltar_a,
        test_reset,
        test_segundos_transcurridos,
        test_historial_cambios,
        test_eventos_ancla,
        test_estado_serializable,
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
            print(f"  [ERROR] {test.__name__}: {e}")
            failed += 1
    print()
    print(f"Resultado: {passed} OK, {failed} FAIL")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
