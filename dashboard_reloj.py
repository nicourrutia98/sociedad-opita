# -*- coding: utf-8 -*-
# Sociedad Opita — Visualizacion forense: terminal + PNG
# https://sociedad.opitacode.com (proximo)
"""
dashboard_reloj.py
==================
Visualizacion forense del estado del reloj virtual y los eventos.

OBJETIVO FORENSE
================
Dar al operador una vista consolidada en tiempo real de:
1. Tiempo virtual actual vs tiempo real (wall-clock).
2. Velocidad de simulacion.
3. Eventos pendientes.
4. Arbol de propagacion de gossip (mas reciente).
5. Conflictos activos y su estado.
6. Timeline 24h con eventos sembrados.

METODOLOGIA
===========
- Dos formatos: terminal (ANSI) y PNG (matplotlib).
- El terminal dashboard es actualizable en sitio (mismo proceso).
- El PNG es estatico, para reports.

LIMITACIONES
============
- L1: Terminal dashboard no funciona en Windows cmd.exe (solo Terminal
  o PowerShell con VT100). Se degrada a ASCII puro.
- L2: Sin auto-refresh. El operador debe llamar `render_terminal()`
  cada vez que quiera actualizar.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional


class Dashboard:
    """Visualizador forense del reloj y eventos."""

    def __init__(self, experimento):
        self.exp = experimento
        self.reloj = experimento.reloj

    def render_terminal(self):
        """Renderiza dashboard en terminal con colores ANSI."""
        # ANSI codes
        BOLD = "\033[1m"
        DIM = "\033[2m"
        RESET = "\033[0m"
        CYAN = "\033[96m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        RED = "\033[91m"
        BLUE = "\033[94m"
        MAGENTA = "\033[95m"

        # Desactivar si no es TTY
        if not sys.stdout.isatty():
            return self._render_ascii()

        lines = []
        lines.append(f"{BOLD}{CYAN}{'=' * 70}{RESET}")
        lines.append(f"{BOLD}{CYAN} DASHBOARD FORENSE - SIMULACION TELLO{RESET}")
        lines.append(f"{BOLD}{CYAN}{'=' * 70}{RESET}")
        lines.append("")

        # Reloj
        t = self.reloj.ahora()
        from reloj import formatear_dia, formatear_hora, DIAS_SEMANA
        dia_semana = DIAS_SEMANA[t.weekday()]
        lines.append(f"{BOLD}RELOJ VIRTUAL{RESET}")
        lines.append(f"  {CYAN}t_virtual:{RESET}  {formatear_dia(t)} {formatear_hora(t)}")
        lines.append(f"  {CYAN}velocidad:{RESET} {self.reloj.velocidad}x  "
                     f"{'(PAUSADO)' if self.reloj.pausado else '(corriendo)'}")
        lines.append(f"  {CYAN}transcurrido:{RESET} "
                     f"{self.reloj.segundos_transcurridos() / 3600:.2f}h "
                     f"virtuales desde t0")
        lines.append("")

        # Experimento
        lines.append(f"{BOLD}EXPERIMENTO{RESET}")
        lines.append(f"  {GREEN}nombre:{RESET} {self.exp.nombre}")
        lines.append(f"  {GREEN}seed:{RESET} {self.exp.random_seed}")
        lines.append(f"  {GREEN}version_prompt:{RESET} {self.exp.version_prompt}")
        lines.append(f"  {GREEN}hipotesis:{RESET} {self.exp.escenario.hipotesis[:80]}...")
        lines.append("")

        # Métricas
        lines.append(f"{BOLD}METRICAS{RESET}")
        lines.append(f"  {YELLOW}log entries:{RESET} {len(self.exp.log)}")
        lines.append(f"  {YELLOW}gossip edges:{RESET} {len(self.exp.gossip_edges)}")
        lines.append(f"  {YELLOW}conflictos activos:{RESET} {len(self.exp.conflictos)}")
        lines.append(f"  {YELLOW}eventos pendientes:{RESET} {len(self.exp.cola_eventos)}")
        lines.append(f"  {YELLOW}snapshots:{RESET} {len(self.exp.snapshots)}")
        lines.append("")

        # Conflictos
        if self.exp.conflictos:
            lines.append(f"{BOLD}CONFLICTOS{RESET}")
            for cid, c in self.exp.conflictos.items():
                estado_color = {
                    "latente": DIM,
                    "activo": YELLOW,
                    "institucional": RED,
                }.get(c["estado"], "")
                lines.append(f"  [{estado_color}{c['estado']}{RESET}] "
                             f"{BOLD}{cid}{RESET} ({len(c['historia'])} eventos)")
            lines.append("")

        # Gossip reciente
        if self.exp.gossip_edges:
            lines.append(f"{BOLD}GOSSIP RECIENTE (ultimos 5){RESET}")
            for edge in self.exp.gossip_edges[-5:]:
                t_edge = edge.get("t", "?")[11:19]  # HH:MM:SS
                if "topic" in edge and "origen" in edge:
                    lines.append(f"  {BLUE}[{t_edge}]{RESET} "
                                 f"{edge['origen']} -> ({edge.get('audiencia', '?')}): "
                                 f"{edge['topic'][:50]}")
                elif "de" in edge and "a" in edge:
                    lines.append(f"  {BLUE}[{t_edge}]{RESET} "
                                 f"{edge['de']} -> {edge['a']}: "
                                 f"{edge.get('topic', '?')[:50]}")
            lines.append("")

        # Eventos pendientes
        if self.exp.cola_eventos:
            lines.append(f"{BOLD}EVENTOS PENDIENTES{RESET}")
            for ev in self.exp.cola_eventos[:5]:
                t_ev = ev.t.isoformat()[11:19]
                lines.append(f"  [{MAGENTA}{t_ev}{RESET}] {ev.tipo}: "
                             f"{str(ev.payload)[:60]}")
            if len(self.exp.cola_eventos) > 5:
                lines.append(f"  ... y {len(self.exp.cola_eventos) - 5} mas")
            lines.append("")

        # Timeline 24h
        lines.append(f"{BOLD}TIMELINE 24h{RESET}")
        lines.append("  " + self._render_timeline_24h())

        print("\n".join(lines))

    def _render_ascii(self):
        """Renderiza dashboard en ASCII puro (no-TTY)."""
        t = self.reloj.ahora()
        from reloj import formatear_dia, formatear_hora
        print("=" * 70)
        print(" DASHBOARD FORENSE - SIMULACION TELLO")
        print("=" * 70)
        print(f"t_virtual: {formatear_dia(t)} {formatear_hora(t)}")
        print(f"velocidad: {self.reloj.velocidad}x")
        print(f"log entries: {len(self.exp.log)}")
        print(f"gossip edges: {len(self.exp.gossip_edges)}")
        print(f"conflictos activos: {len(self.exp.conflictos)}")
        print(f"eventos pendientes: {len(self.exp.cola_eventos)}")
        if self.exp.conflictos:
            print("conflictos:")
            for cid, c in self.exp.conflictos.items():
                print(f"  [{c['estado']}] {cid}")
        print("TIMELINE 24h:")
        print("  " + self._render_timeline_24h())

    def _render_timeline_24h(self):
        """Renderiza timeline de las ultimas 24h."""
        # Bucket de eventos en intervalos de 1h
        if not self.exp.log:
            return "(sin eventos)"

        t_actual = self.reloj.ahora()
        t_inicio = t_actual - timedelta(hours=12)
        t_fin = t_actual + timedelta(hours=12)

        # Contar eventos por hora
        eventos_por_hora = {}
        for entry in self.exp.log:
            try:
                t_ev = datetime.fromisoformat(entry["t"])
                if t_inicio <= t_ev <= t_fin:
                    hora = t_ev.replace(minute=0, second=0, microsecond=0)
                    eventos_por_hora[hora] = eventos_por_hora.get(hora, 0) + 1
            except (ValueError, KeyError):
                continue

        # Contar eventos pendientes por hora
        for ev in self.exp.cola_eventos:
            if t_inicio <= ev.t <= t_fin:
                hora = ev.t.replace(minute=0, second=0, microsecond=0)
                eventos_por_hora[hora] = eventos_por_hora.get(hora, 0) + 1

        # Renderizar 24 buckets
        timeline = []
        h = t_inicio.replace(minute=0, second=0, microsecond=0)
        for i in range(24):
            n = eventos_por_hora.get(h, 0)
            if h == t_actual.replace(minute=0, second=0, microsecond=0):
                marker = "|*"
            elif h < t_actual:
                marker = " ."
            else:
                marker = "  "
            bar = "#" * min(n, 8) if n > 0 else ""
            timeline.append(f"{h.strftime('%H:%M')}{marker}{bar}({n})")
            h += timedelta(hours=1)

        return "  ".join(timeline[:12]) + "\n  " + "  ".join(timeline[12:])

    def render_png(self, ruta=None):
        """Renderiza dashboard como PNG estatico."""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
        except ImportError:
            print("[ERROR] matplotlib no disponible.")
            return None

        if ruta is None:
            ruta = f"experimentos/{self.exp.nombre}_dashboard.png"
        Path(ruta).parent.mkdir(parents=True, exist_ok=True)

        fig, axes = plt.subplots(3, 1, figsize=(14, 10))
        fig.suptitle(f"Dashboard Forense - {self.exp.nombre}",
                     fontsize=14, fontweight="bold")

        # Panel 1: Timeline de eventos
        ax1 = axes[0]
        eventos_t = []
        eventos_tipo = []
        for entry in self.exp.log:
            try:
                eventos_t.append(datetime.fromisoformat(entry["t"]))
                eventos_tipo.append(entry["evento"])
            except (ValueError, KeyError):
                continue
        for ev in self.exp.cola_eventos:
            eventos_t.append(ev.t)
            eventos_tipo.append(f"(pendiente) {ev.tipo}")

        if eventos_t:
            tipos_unicos = sorted(set(eventos_tipo))
            colors = plt.cm.tab10(range(len(tipos_unicos)))
            color_map = dict(zip(tipos_unicos, colors))
            for t, tp in zip(eventos_t, eventos_tipo):
                ax1.scatter(t, tipos_unicos.index(tp),
                            color=color_map[tp], s=50, alpha=0.7)
            ax1.set_yticks(range(len(tipos_unicos)))
            ax1.set_yticklabels(tipos_unicos, fontsize=8)
            ax1.set_xlabel("Tiempo virtual")
            ax1.set_title("Eventos en el tiempo")
            ax1.grid(True, alpha=0.3)
        else:
            ax1.text(0.5, 0.5, "Sin eventos",
                     ha="center", va="center", transform=ax1.transAxes)
            ax1.set_title("Eventos en el tiempo")

        # Panel 2: Gossip propagation
        ax2 = axes[1]
        gossip_counts_por_t = {}
        for edge in self.exp.gossip_edges:
            try:
                t = datetime.fromisoformat(edge["t"])
                hora = t.replace(minute=0, second=0, microsecond=0)
                gossip_counts_por_t[hora] = gossip_counts_por_t.get(hora, 0) + 1
            except (ValueError, KeyError):
                continue
        if gossip_counts_por_t:
            ts = sorted(gossip_counts_por_t.keys())
            counts = [gossip_counts_por_t[t] for t in ts]
            ax2.plot(ts, counts, "o-", color="red", linewidth=2)
            ax2.fill_between(ts, counts, alpha=0.3, color="red")
            ax2.set_xlabel("Tiempo virtual")
            ax2.set_ylabel("Edges de gossip (acumulado)")
            ax2.set_title("Propagacion de chismes")
            ax2.grid(True, alpha=0.3)
        else:
            ax2.text(0.5, 0.5, "Sin gossip registrado",
                     ha="center", va="center", transform=ax2.transAxes)
            ax2.set_title("Propagacion de chismes")

        # Panel 3: Estado de conflictos
        ax3 = axes[2]
        if self.exp.conflictos:
            cids = list(self.exp.conflictos.keys())
            estados = [self.exp.conflictos[c]["estado"] for c in cids]
            estado_counts = {}
            for e in estados:
                estado_counts[e] = estado_counts.get(e, 0) + 1
            colores_estado = {"latente": "gray", "activo": "orange",
                              "institucional": "red"}
            bars = ax3.bar(range(len(cids)),
                           [estado_counts.get(e, 0) for e in set(estados)],
                           color=[colores_estado.get(e, "blue") for e in set(estados)])
            ax3.set_xticks(range(len(cids)))
            ax3.set_xticklabels(cids, rotation=45, ha="right", fontsize=8)
            ax3.set_ylabel("Eventos en el conflicto")
            ax3.set_title("Estado de conflictos")
            ax3.grid(True, alpha=0.3, axis="y")
            # Leyenda
            patches_legend = [mpatches.Patch(color=c, label=s)
                              for s, c in colores_estado.items()]
            ax3.legend(handles=patches_legend, loc="upper right", fontsize=8)
        else:
            ax3.text(0.5, 0.5, "Sin conflictos activos",
                     ha="center", va="center", transform=ax3.transAxes)
            ax3.set_title("Estado de conflictos")

        plt.tight_layout()
        plt.savefig(ruta, dpi=100, bbox_inches="tight")
        plt.close()
        return ruta


if __name__ == "__main__":
    # Demo: renderiza dashboard del experimento demo_gossip_v1
    from experimento import Escenario, Experimento

    print("Demo: dashboard requiere un experimento previo.")
    print("Uso: from dashboard_reloj import Dashboard; d = Dashboard(exp); d.render_terminal()")
