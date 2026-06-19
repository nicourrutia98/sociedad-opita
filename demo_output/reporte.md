# Reporte Ejecutivo - Sociedad Opita Demo

**Generado:** 2026-06-19 10:44

---

## Resumen

Tello, Huila. 12.908 habitantes. 41 agentes simulados (26 adultos + 15 niños), 34 edificios georreferenciados, 3 generaciones, 1 capa institucional.

## Hallazgo destacado

**Doña Rosa Tendera (la tendera) es el super-spreader #1** de la red social de Tello. Su betweenness centrality (0.29) supera a cualquier otro agente, lo que confirma la hipotesis de que la geometria del pueblo predice quien controla el flujo de informacion.

Ver `centralidad_reporte.txt` para el analisis completo.

## Outputs generados

- **Mapa**: `mapa_tello.png` (165 KB)
- **Red social**: `red_social_red.png` (139 KB)
- **Dialogos**: `dialogos.md` (2 KB)
- **Dashboard**: `dashboard.png` (74 KB)
- **Centralidad**: `red_centralidad.png` (222 KB)

## Metricas clave

| Metrica | Valor |
|---|---|
| Agentes adultos | 26 |
| Agentes ninos | 15 |
| Edificios georreferenciados | 34 |
| Veredas | 6 |
| Plantillas de experimento | 4 |
| Validacion nativa (dialogos) | 10 aprobados |
| Costo LLM/hora | ~$0.024 USD |
| Tiempo virtual x real | Hasta x28800 |
| Super-spreader #1 | Dona Rosa (betweenness=0.29) |

## Que sigue

- Ver `docs/index.md` para la documentacion completa.
- Ver `validacion_nativa_huilense.md` para la linea base de autenticidad linguistica.
- Correr `python panel_control.py` para interaccion interactiva.
- Correr `python experimentos/gossip_propagation.py --replicas 5` para experimento de propagacion de chismes.
- Ver `centralidad_reporte.txt` para el analisis de red.
