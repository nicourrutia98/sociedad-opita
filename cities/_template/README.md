# Cómo agregar una nueva ciudad al modelo Vibe Pattern

Esta guía te permite **crear una nueva ciudad en <2 horas** sin tocar código Python.

## Requisitos

- Conocimiento cultural del municipio (literatura, trabajo de campo, nativos)
- 15-50 personas documentadas con biografía
- 1 hora de OSINT para Hofstede + festividades

## Paso 1: Crear la estructura de directorios

```bash
# Desde el root del proyecto
mkdir -p cities/mi_ciudad/personas
cp cities/_template/city.yaml cities/mi_ciudad/city.yaml
cp cities/_template/hofstede.yaml cities/mi_ciudad/hofstede.yaml
cp cities/_template/cultural_markers.md cities/mi_ciudad/cultural_markers.md
cp cities/_template/personas/_template.yaml cities/mi_ciudad/personas/_persona_01.yaml
```

## Paso 2: Llenar `city.yaml`

Completa los campos:
- `city_id`: slug único (ej. "pitalito")
- `display_name`: "Pitalito, Huila"
- `coordinates`: lat/lon del parque principal
- `festivities`: 4-8 fiestas principales

## Paso 3: Calibrar `hofstede.yaml`

Usa los valores de Hofstede Insights como base, ajusta +5/+10 en:
- `PDI`: +5 si la ciudad es más jerárquica que el promedio
- `UAI`: +5 si hay fuerte apego a la tradición
- `MAS`: -5 si hay cooperación más que competencia

## Paso 4: Llenar `cultural_markers.md`

- **Muletillas**: mínimo 10 frases hechas del dialecto local
- **Léxico**: 15-30 palabras regionales
- **Conflictos típicos**: 3-5 tipos comunes
- **Resoluciones**: cómo se dirimen localmente

## Paso 5: Crear personas (mínimo 15)

Por cada persona, copia `_template.yaml` a `personas/[slug].yaml`:

1. **Elige arquetipo** de los 12 disponibles en `city_factory/personality_archetypes.py`:
   - ganadero_tradicional, comerciante_urbano, sacerdote_rural, maestro_escuela,
     medico_tradicional, tendero_pueblo, autoridad_policia, artesano_independiente,
     politico_local, trabajador_rural, viuda_anfitriona, joven_migrante

2. **Ajusta Big Five** dentro del rango del arquetipo (1-2 rasgos únicos)

3. **Completa muletillas** (3-5 frases hechas)

4. **Define red social** (aliados, conflictos, centralidad)

## Paso 6: Validar

```bash
python -c "from city_factory import load_city; c = load_city('mi_ciudad'); print(f'{c.display_name}: {len(c.personas)} personas')"
```

Si hay errores, el sistema te dirá exactamente qué campo está mal.

## Paso 7: Probar una simulación

```bash
python -c "
from city_factory import load_city
from core.engine import SimulationEngine, Scene
c = load_city('mi_ciudad')
engine = SimulationEngine(city=c)
result = engine.simulate_one('persona_01', Scene(time='07:00', place='Parque'))
print(result.text)
"
```

## Paso 8 (opcional): Publicar en el demo web

Edita `web/index.html` para agregar la nueva ciudad al selector. El API REST la expone automáticamente en `/v1/cities`.

## Tiempo estimado

| Actividad | Tiempo |
|---|---|
| Estructura + city.yaml | 10 min |
| Hofstede | 5 min |
| cultural_markers.md | 20 min |
| 15 personas × 15 min | 4 horas |
| Validación + 1 simulación de prueba | 15 min |
| **TOTAL** | **~5 horas** |

## Próximos pasos después de la primera ciudad

- Replicar para 3-5 ciudades del mismo departamento
- Análisis cross-city (comparar redes, ver qué arquetipos dominan dónde)
- Publicar paper académico con datos comparativos
