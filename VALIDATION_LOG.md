# Validation Log — Tello 2026 Simulación Generativa

**Propósito:** Registro de validaciones realizadas por revisores (nativos del Huila o especialistas). Documenta QUÉ se validó, CUÁNDO, POR QUIÉN, y QUÉ resultado tuvo. Permite reproducibilidad y evolución controlada del sistema.

---

## Validación v1 — 2026-06-19

### Validador
- **Identidad:** Operador del proyecto (autodeclarado nativo huilense)
- **Tipo de validación:** Revisión nativa del habla y comportamiento cultural
- **Alcance:** 10 diálogos representativos (ver `validacion_nativa_huilense.md`)
- **Tiempo de revisión:** < 5 minutos (revisión general)

### Resultado
**APROBADO** — "Así como está, está bien."

- Los 10 diálogos pasaron revisión general del nativo
- No se identificaron errores críticos de dialecto
- Las muletillas, metáforas rurales y estructuras pragmáticas son aceptables

### Observaciones del validador
- (Pendiente: anotar observaciones específicas si las hubo)

### Decisiones tomadas
1. ✅ **No se itera más sobre estos 10 diálogos** — son la línea base validada
2. 🔄 **Los nuevos diálogos generados** deben compararse contra estos 10 como referencia
3. 📝 **Cualquier modificación al prompt cultural** requiere re-validación

### Próxima validación
Cuando se agreguen:
- Nuevos agentes (perfiles adicionales)
- Nuevas escenas (eventos nuevos)
- Cambios al prompt cultural
- Cambios a biografías de agentes

---

## Plantilla para Validaciones Futuras

```markdown
## Validación vN — YYYY-MM-DD

### Validador
- **Identidad:** ___________
- **Tipo de validación:** ___________ (nativa | experto | ciega | comparación)
- **Alcance:** ___________
- **Tiempo de revisión:** ___________

### Resultado
[APROBADO | APROBADO CON OBSERVACIONES | RECHAZADO]

### Observaciones
- ___________

### Cambios accionables
1. ___________
2. ___________

### Diálogos o elementos validados específicamente
- ___________

### Próxima validación
[cuándo]
```

---

## Cómo usar este log

1. **Antes de modificar el sistema**, lee la última entrada para entender qué está validado.
2. **Después de modificar**, ejecuta una simulación nueva y compara los nuevos diálogos con los validados en esta línea base.
3. **Si los nuevos diálogos divergen significativamente**, ejecuta una nueva ronda de validación con un nativo.
4. **Anota cada validación** usando la plantilla de arriba.

---

## Relación con otros archivos

- `validacion_nativa_huilense.md` — Contiene los 10 diálogos validados como referencia
- `docs/PLAN-SIMULACION-NEIVA.md` — Documento maestro (referencia histórica)
- `docs/agentes/01-biografias.md` — Perfiles (8 capas forenses)
- `docs/agentes/02-prompt-cultural.md` — Prompt cultural
- `simulacion_sociedad_completa.py` — Generador de diálogos comparables

---

*Sistema de validación. Versión inicial: 2026-06-19.*
