# -*- coding: utf-8 -*-
# Sociedad Opita — Reloj virtual con velocidad, pausa y salto
# https://sociedad.opitacode.com (proximo)
"""
reloj.py
========
Reloj virtual con velocidad controlable.

OBJETIVO FORENSE
================
En un estudio forense real, el tiempo del experimento debe ser CONTROLABLE:

1. **Velocidad variable**: x1 (tiempo real), x60 (1 hora por minuto), x600
   (1 dia por minuto), x3600 (1 semana por minuto). Acelera la observacion
   de fenmenos lentos (gossip de un mes) sin esperar meses reales.

2. **Pausa**: detener el reloj virtual para inspeccionar estado, inyectar
   un evento, comparar snapshots.

3. **Salto temporal**: ir a un timestamp arbitrario (inicio de jornada,
   momento del Festival, crisis del acueducto). Reproducible.

4. **Independiente del wall-clock**: el reloj virtual NO depende de
   datetime.now() del sistema. Asi, un experimento de 10 dias simulados
   puede correr en 30 segundos reales con velocidad x28800.

METODOLOGIA
===========
- El reloj es un delta-time accumulator: avanza solo cuando el motor
  llama a `avanzar(dt_segundos_simulados)`. Esto desacopla el tiempo
  virtual del wall-clock.

- Velocidad es un multiplicador: si el motor llama a `avanzar(dt_wall)`
  y la velocidad es x10, entonces el tiempo virtual avanza `10 * dt_wall`.

- Pausa congela el reloj virtual pero deja el wall-clock correr.

- Todos los eventos quedan timestampados con el reloj VIRTUAL, no el
  real. Esto hace que los logs sean reproducibles.

LIMITACIONES CONOCIDAS
======================
- L1: La velocidad maxima depende del throughput del LLM (no del reloj).
  Si un dialogo tarda 2s reales, la velocidad efectiva del experimento
  es dt_virtual / 2s_real. Documentado en cada experimento.
- L2: Timestamps en JSON se guardan como ISO 8601 string (UTC offset 0
  por defecto).
- L3: El reloj virtual no maneja cambios de hora (DST) ni calendarios
  multiples (lunar, liturgico). Solo calendario civil.

USO
===
>>> from reloj import Reloj
>>> from datetime import datetime
>>> r = Reloj(datetime(2026, 6, 19, 6, 0), velocidad=60)
>>> r.ahora()
datetime.datetime(2026, 6, 19, 6, 0)
>>> r.avanzar(60)  # avanzar 1 minuto simulado
>>> r.ahora()
datetime.datetime(2026, 6, 19, 6, 1)
>>> r.velocidad = 3600  # 1 hora simulada por segundo real
>>> r.pausar()
>>> r.reanudar()
>>> r.saltar_a(datetime(2026, 6, 19, 18, 0))
"""

from datetime import datetime, timedelta


class Reloj:
    """Reloj virtual con velocidad, pausa y salto."""

    def __init__(self, t0=None, velocidad=1.0):
        """
        Args:
            t0: datetime inicial del tiempo virtual. Default: ahora (wall-clock).
            velocidad: multiplicador (1.0 = real, 60 = 1 hora virtual por
                       minuto real, 3600 = 1 dia virtual por minuto real).
        """
        self.t0 = t0 or datetime(2026, 6, 19, 6, 0)
        self.t = self.t0
        self.velocidad_inicial = float(velocidad)
        self.velocidad = float(velocidad)
        self.pausado = False
        self.historial_cambios = []  # (timestamp_wall, "set_velocidad", valor)
        self._log_cambio("init", {"t0": str(t0), "velocidad": velocidad})

    def _log_cambio(self, accion, payload):
        """Registra un cambio en el reloj (para audit trail forense)."""
        from datetime import datetime as _dt
        self.historial_cambios.append({
            "wall_time": _dt.now().isoformat(),
            "accion": accion,
            "payload": payload,
        })

    def ahora(self):
        """Devuelve el tiempo virtual actual."""
        return self.t

    def timestamp_iso(self):
        """Devuelve el tiempo virtual como ISO 8601."""
        return self.t.isoformat()

    def segundos_transcurridos(self):
        """Segundos virtuales desde t0."""
        return (self.t - self.t0).total_seconds()

    def avanzar(self, dt_segundos):
        """
        Avanza el reloj virtual por `dt_segundos` (tiempo VIRTUAL, no wall).
        Si esta pausado, no hace nada.
        """
        if self.pausado:
            return 0
        self.t += timedelta(seconds=dt_segundos)
        return dt_segundos

    def avanzar_wall(self, dt_wall_segundos):
        """
        Avanza el reloj virtual segun el wall-clock y la velocidad actual.
        Util cuando el motor corre en loop y avanza tiempo real.
        """
        if self.pausado:
            return 0
        dt_virtual = dt_wall_segundos * self.velocidad
        self.t += timedelta(seconds=dt_virtual)
        return dt_virtual

    def set_velocidad(self, velocidad):
        """Cambia la velocidad del reloj. x1, x10, x60, x3600, x28800."""
        v_anterior = self.velocidad
        self.velocidad = float(velocidad)
        self._log_cambio("set_velocidad", {
            "anterior": v_anterior,
            "nueva": self.velocidad,
        })

    def pausar(self):
        """Pausa el reloj virtual."""
        self.pausado = True
        self._log_cambio("pausar", {"t_virtual": self.timestamp_iso()})

    def reanudar(self):
        """Reanuda el reloj virtual."""
        self.pausado = False
        self._log_cambio("reanudar", {"t_virtual": self.timestamp_iso()})

    def saltar_a(self, t):
        """Salta el reloj virtual al timestamp t. No afecta velocidad ni pausa."""
        t_anterior = self.t
        self.t = t
        self._log_cambio("saltar_a", {
            "t_anterior": t_anterior.isoformat(),
            "t_nuevo": t.isoformat(),
        })

    def reset(self):
        """Resetea el reloj al t0 inicial."""
        self.t = self.t0
        self.velocidad = self.velocidad_inicial
        self.pausado = False
        self._log_cambio("reset", {"t": self.t.isoformat()})

    def estado(self):
        """Snapshot del estado del reloj (para UI)."""
        return {
            "t_virtual": self.timestamp_iso(),
            "t0": self.t0.isoformat(),
            "velocidad": self.velocidad,
            "pausado": self.pausado,
            "segundos_transcurridos": self.segundos_transcurridos(),
            "cambios_realizados": len(self.historial_cambios),
        }


# ===========================================================================
# UTILIDADES DE CALENDARIO
# ===========================================================================

DIAS_SEMANA = ["lunes", "martes", "miercoles", "jueves",
               "viernes", "sabado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

# Eventos anclados del Tello 2026 (para que el reloj pueda saltar)
EVENTOS_ANCLA_2026 = [
    {"fecha": "2026-04-05", "evento": "crisis_acueducto_inicio",
     "descripcion": "Creciente rio Villavieja rompe tuberia. 5 dias sin agua."},
    {"fecha": "2026-04-10", "evento": "crisis_acueducto_fin",
     "descripcion": "Carrotanques Neiva. Bomberos apoyan."},
    {"fecha": "2026-06-19", "evento": "hoy", "descripcion": "Sesion actual."},
    {"fecha": "2026-06-24", "evento": "festival_san_juan",
     "descripcion": "San Juan del Festival del Bambuco."},
    {"fecha": "2026-06-29", "evento": "festival_san_pedro",
     "descripcion": "San Pedro del Festival del Bambuco."},
    {"fecha": "2026-07-05", "evento": "reinado_nacional",
     "descripcion": "Reinado Nacional del Bambuco."},
]


def formatear_hora(dt):
    """Devuelve 'HH:MM' para UI."""
    return dt.strftime("%H:%M")


def formatear_dia(dt):
    """Devuelve 'YYYY-MM-DD (dia_semana)' para UI."""
    dia = DIAS_SEMANA[dt.weekday()]
    return f"{dt.strftime('%Y-%m-%d')} ({dia})"


def parsear_evento_ancla(nombre):
    """Devuelve el datetime del evento ancla por nombre."""
    for ev in EVENTOS_ANCLA_2026:
        if ev["evento"] == nombre:
            return datetime.fromisoformat(ev["fecha"] + "T06:00:00")
    raise ValueError(f"Evento ancla '{nombre}' no encontrado.")


if __name__ == "__main__":
    # Demo: reloj acelerado, pausa, salto
    from datetime import datetime

    print("=" * 60)
    print("DEMO: Reloj virtual")
    print("=" * 60)

    r = Reloj(datetime(2026, 6, 19, 6, 0), velocidad=1.0)
    print(f"t0:           {r.ahora()}")
    print(f"velocidad:    {r.velocidad}x")

    r.avanzar(3600)  # 1 hora simulada
    print(f"+1h:          {r.ahora()}")

    r.set_velocidad(60)
    r.avanzar_wall(60)  # 1 min wall * 60x = 60 min virtuales = 1h
    print(f"x60, +1m wall: {r.ahora()}  (salto de 1h virtual)")

    r.pausar()
    r.avanzar(1000)
    print(f"pausado:       {r.ahora()} (no avanza)")

    r.reanudar()
    r.saltar_a(datetime(2026, 6, 24, 18, 0))
    print(f"salto:         {r.ahora()}  (Festival San Juan, 6pm)")

    print()
    print("Eventos ancla 2026:")
    for ev in EVENTOS_ANCLA_2026:
        print(f"  {ev['fecha']}: {ev['evento']} - {ev['descripcion']}")

    print()
    print("Estado del reloj:")
    for k, v in r.estado().items():
        print(f"  {k}: {v}")
