# -*- coding: utf-8 -*-
# Sociedad Opita - Tests runner
# https://sociedad.opitacode.com (proximo)
#
"""
run_all_tests.py
================
Ejecuta todos los tests del proyecto.

USO:
    python run_all_tests.py
"""

import sys
import subprocess
from pathlib import Path

TESTS = [
    "tests/test_reloj.py",
    "tests/test_experimento.py",
    "tests/test_geo.py",
]


def main():
    base = Path(__file__).parent
    print("=" * 70)
    print(" SOCIEDAD OPITA - EJECUTANDO TODOS LOS TESTS")
    print("=" * 70)
    print()

    resultados = []
    for test_path in TESTS:
        ruta = base / test_path
        if not ruta.exists():
            print(f"[SKIP] {test_path} no existe")
            continue
        print(f"--- {test_path} ---")
        resultado = subprocess.run(
            [sys.executable, str(ruta)],
            cwd=str(base),
            capture_output=True,
            text=True,
        )
        # Output
        if resultado.stdout:
            for linea in resultado.stdout.splitlines():
                if linea.strip():
                    print(f"  {linea}")
        if resultado.stderr:
            for linea in resultado.stderr.splitlines():
                if linea.strip():
                    print(f"  [STDERR] {linea}")
        resultados.append((test_path, resultado.returncode))
        print()

    # Resumen
    print("=" * 70)
    print(" RESUMEN")
    print("=" * 70)
    total = len(resultados)
    passed = sum(1 for _, rc in resultados if rc == 0)
    failed = total - passed
    for test_path, rc in resultados:
        status = "OK" if rc == 0 else "FAIL"
        print(f"  [{status}] {test_path}")
    print()
    print(f"Total: {total} modulos, {passed} OK, {failed} FAIL")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
