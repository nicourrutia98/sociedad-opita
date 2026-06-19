# -*- coding: utf-8 -*-
# Sociedad Opita - Tests
# https://sociedad.opitacode.com (proximo)
#
"""
tests/test_experimento.py
=========================
Tests para el framework de experimentos (experimento.py).

USO:
    python tests/test_experimento.py
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from experimento import Experimento, Escenario, Evento


def test_crear_experimento_basico():
    """Verifica creacion basica."""
    escenario = Escenario(
        t_inicial=datetime(2026, 6, 19, 6, 0),
        duracion_segundos=86400,
        agentes={"a": {}, "b": {}},
        random_seed=42,
    )
    exp = Experimento(nombre="test_v1", escenario=escenario)
    assert exp.nombre == "test_v1"
    assert exp.random_seed == 42
    assert exp.version_prompt == "2.0"
    print("  [OK] test_crear_experimento_basico")


def test_reproducibilidad_por_seed():
    """Misma semilla produce mismo log."""
    escenario1 = Escenario(
        t_inicial=datetime(2026, 6, 19, 6, 0),
        duracion_segundos=86400,
        agentes={},
        random_seed=42,
    )
    exp1 = Experimento(nombre="t1", escenario=escenario1)
    exp1.sembrar_gossip(
        t=datetime(2026, 6, 19, 8, 0),
        origen="a", topic="tema X",
        veracidad=0.5, intensidad=1.0,
    )
    n_log1 = len(exp1.log)

    escenario2 = Escenario(
        t_inicial=datetime(2026, 6, 19, 6, 0),
        duracion_segundos=86400,
        agentes={},
        random_seed=42,
    )
    exp2 = Experimento(nombre="t2", escenario=escenario2)
    exp2.sembrar_gossip(
        t=datetime(2026, 6, 19, 8, 0),
        origen="a", topic="tema X",
        veracidad=0.5, intensidad=1.0,
    )
    n_log2 = len(exp2.log)

    assert n_log1 == n_log2, f"Logs diferentes: {n_log1} vs {n_log2}"
    print("  [OK] test_reproducibilidad_por_seed")


def test_sembrar_gossip():
    """Seed de gossip se registra correctamente (en cola_eventos)."""
    escenario = Escenario(
        t_inicial=datetime(2026, 6, 19, 6, 0),
        duracion_segundos=86400,
        agentes={},
    )
    exp = Experimento(nombre="t1", escenario=escenario)
    exp.sembrar_gossip(
        t=datetime(2026, 6, 19, 8, 0),
        origen="dona_rosa",
        topic="Don F se robo la plata",
        veracidad=0.2,
        intensidad=2.0,
    )
    # El evento esta en cola_eventos, no procesado aun
    assert len(exp.cola_eventos) == 1
    ev = exp.cola_eventos[0]
    assert ev.tipo == "gossip_seed"
    assert ev.payload["origen"] == "dona_rosa"
    assert ev.payload["veracidad"] == 0.2
    # Avanzar para procesarlo
    exp.avanzar(7200)  # 2h -> llega al t=8:00
    assert len(exp.gossip_edges) == 1
    edge = exp.gossip_edges[0]
    assert edge["origen"] == "dona_rosa"
    assert edge["topic"] == "Don F se robo la plata"
    assert edge["veracidad"] == 0.2
    assert edge["intensidad"] == 2.0
    print("  [OK] test_sembrar_gossip")


def test_trigger_conflicto():
    """Disparar conflicto lo registra (al procesarse)."""
    escenario = Escenario(
        t_inicial=datetime(2026, 6, 19, 6, 0),
        duracion_segundos=86400,
        agentes={},
    )
    exp = Experimento(nombre="t1", escenario=escenario)
    exp.trigger_conflicto(
        t=datetime(2026, 6, 19, 14, 0),
        conflicto_id="linderos",
        participantes=["don_e", "don_r"],
        tipo="escalar",
    )
    # El evento esta en cola_eventos, no procesado aun
    assert len(exp.cola_eventos) == 1
    assert len(exp.conflictos) == 0
    # Avanzar para procesarlo
    exp.avanzar(8 * 3600)  # 8h -> llega al t=14:00
    assert "linderos" in exp.conflictos
    assert exp.conflictos["linderos"]["estado"] == "activo"
    assert len(exp.conflictos["linderos"]["historia"]) == 1
    print("  [OK] test_trigger_conflicto")


def test_inyectar_evento_tipo_invalido():
    """Tipo de evento invalido lanza error."""
    escenario = Escenario(
        t_inicial=datetime(2026, 6, 19, 6, 0),
        duracion_segundos=86400,
        agentes={},
    )
    exp = Experimento(nombre="t1", escenario=escenario)
    try:
        exp.inyectar_evento(
            t=datetime(2026, 6, 19, 8, 0),
            tipo="tipo_invalido_xyz",
            payload={},
        )
        print("  [FAIL] test_inyectar_evento_tipo_invalido: debio lanzar excepcion")
        return False
    except ValueError:
        print("  [OK] test_inyectar_evento_tipo_invalido")
        return True


def test_snapshot():
    """Snapshot captura estado actual."""
    escenario = Escenario(
        t_inicial=datetime(2026, 6, 19, 6, 0),
        duracion_segundos=86400,
        agentes={},
    )
    exp = Experimento(nombre="t1", escenario=escenario)
    snap = exp.snapshot("pre_test")
    assert "pre_test" in exp.snapshots
    assert snap["etiqueta"] == "pre_test"
    assert snap["t"] == "2026-06-19T06:00:00"
    print("  [OK] test_snapshot")


def test_correr_avanza_log():
    """Correr el experimento avanza el log."""
    escenario = Escenario(
        t_inicial=datetime(2026, 6, 19, 6, 0),
        duracion_segundos=3600,  # 1h
        agentes={},
    )
    exp = Experimento(nombre="t1", escenario=escenario)
    n_inicial = len(exp.log)
    exp.correr(paso_segundos=600)
    n_final = len(exp.log)
    assert n_final > n_inicial, f"Log no crecio: {n_inicial} -> {n_final}"
    print("  [OK] test_correr_avanza_log")


def test_exportar_crea_archivos():
    """Exportar genera los 5 archivos esperados."""
    import tempfile
    import shutil

    escenario = Escenario(
        t_inicial=datetime(2026, 6, 19, 6, 0),
        duracion_segundos=3600,
        agentes={"a": {}},
        random_seed=42,
    )
    exp = Experimento(nombre="t1", escenario=escenario)
    exp.sembrar_gossip(
        t=datetime(2026, 6, 19, 8, 0),
        origen="a", topic="tema",
    )
    exp.correr(paso_segundos=600)

    tmpdir = tempfile.mkdtemp()
    try:
        ruta = exp.exportar(tmpdir, comprimir=True)
        archivos = set(f.name for f in Path(ruta).iterdir())
        esperado = {"manifest.json", "log.jsonl.gz",
                    "gossip_graph.json", "snapshots.json",
                    "conflictos.json"}
        assert esperado.issubset(archivos), \
            f"Faltan archivos: {esperado - archivos}"
        print("  [OK] test_exportar_crea_archivos")
    finally:
        shutil.rmtree(tmpdir)


def test_exportar_manifest_contiene_seed():
    """Manifest incluye seed, hipotesis, version prompt."""
    import tempfile
    import shutil

    escenario = Escenario(
        t_inicial=datetime(2026, 6, 19, 6, 0),
        duracion_segundos=3600,
        agentes={},
        random_seed=123,
        hipotesis="El rumor se propaga rapido",
    )
    exp = Experimento(nombre="t1", escenario=escenario,
                      version_prompt="2.0")
    exp.correr(paso_segundos=600)

    tmpdir = tempfile.mkdtemp()
    try:
        ruta = exp.exportar(tmpdir)
        manifest = json.loads(
            (Path(ruta) / "manifest.json").read_text(encoding="utf-8")
        )
        assert manifest["random_seed"] == 123
        assert manifest["version_prompt"] == "2.0"
        assert "propaga rapido" in manifest["hipotesis"]
        print("  [OK] test_exportar_manifest_contiene_seed")
    finally:
        shutil.rmtree(tmpdir)


def test_eventos_pendientes_se_procesan():
    """Eventos con t <= reloj.ahora() se procesan al avanzar."""
    escenario = Escenario(
        t_inicial=datetime(2026, 6, 19, 6, 0),
        duracion_segundos=3600,
        agentes={},
    )
    exp = Experimento(nombre="t1", escenario=escenario)
    # Evento a las 6:00 (mismo t0)
    exp.sembrar_gossip(
        t=datetime(2026, 6, 19, 6, 0),
        origen="a", topic="tema",
    )
    assert len(exp.cola_eventos) == 1
    # Avanzar 5 minutos -> el evento debe procesarse
    exp.avanzar(300)
    assert len(exp.cola_eventos) == 0
    assert len(exp.gossip_edges) == 1
    print("  [OK] test_eventos_pendientes_se_procesan")


def main():
    print("=" * 60)
    print(" TESTS - Framework de experimentos")
    print("=" * 60)
    tests = [
        test_crear_experimento_basico,
        test_reproducibilidad_por_seed,
        test_sembrar_gossip,
        test_trigger_conflicto,
        test_inyectar_evento_tipo_invalido,
        test_snapshot,
        test_correr_avanza_log,
        test_exportar_crea_archivos,
        test_exportar_manifest_contiene_seed,
        test_eventos_pendientes_se_procesan,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            result = test()
            if result is False:
                failed += 1
            else:
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
