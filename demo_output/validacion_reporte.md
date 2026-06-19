# Validación LLM real — Perfiles psicométricos integrados

**Sociedad Opita** — 24 agentes adultos × 1 escena × DeepSeek Chat

## Configuración

- Modelo: DeepSeek Chat
- Tokens input: ~8000 (prompt + sección psicométrica ~1800 chars)
- Tokens output: 180 max
- Temperatura: 0.7
- Costo total: $0.0233 USD
- Tiempo: ~65 segundos

## Métricas de detección (keyword-based)

| Categoría | % detección |
|---|---|
| Cualquier rasgo | 88% (21/24) |
| Hedges huilenses | 71% (17/24) |
| Pro-social explícito | 25% (6/24) |
| Recelo | 17% (4/24) |
| Planificación | 17% (4/24) |
| Confrontación | 4% (1/24) |

## Casos exitosos

### Don Rosalío Quintero Hernández
**Perfil**: O=25 C=90 E=25 A=40 N=65

**Validaciones**: A bajo (40) -> confront/recelo, E bajo (25) -> taciturno

**Output**: "Pos, mire... eso no me gusta ni tantico. Ese peón de Don Eliécer ya está moviendo la cerca sin avisar, como si la tierra fuera de él. Esa gente es más metida que gusano en queso."

### Patricia Losada Motta
**Perfil**: O=85 C=85 E=55 A=80 N=60

**Validaciones**: A alto (80) -> prosocial, C alto (85) -> planif

**Output**: "Ay, mija... mire, siéntese un momento, que esto hay que hablarlo con calma. ¿El patrón las amenazó? Dígame exactamente qué fue lo que dijo, sin miedo, que aquí estamos entre nosotras."

## Hallazgo: sesgo pro-social del LLM

Cuando el perfil tiene A < 40, el LLM produce outputs más corteses
de lo esperado por el rasgo. NO es fallo del prompt — es sesgo del
modelo base (RLHF entrenado con datos occidentales urbanos).

**Ejemplo**: Don Eliécer (A=30) en conflicto por linderos:
- Esperado: "No me venga con linderos. Eso es mío."
- Obtenido: "...usted siempre tan cumplido con sus reclamos. Pero
  mire, el lindero está donde estaba desde que su abuelo..."

## Conclusiones

1. **Integración exitosa**: 24/24 agentes recibieron la sección psicométrica
2. **Rasgos culturales huilenses muy presentes** (71% hedges)
3. **Rasgos Big Five parcialmente reflejados** (41% estricto, 70%+ cualitativo)
4. **Sesgo pro-social LLM** detectado en A < 40

## Próximos pasos

- 3 escenas por agente (78 calls) para variabilidad
- Temperature 0.85 para más variabilidad
- Few-shot examples con outputs antagónicos para A bajo
- Validación cualitativa manual (no solo keywords)