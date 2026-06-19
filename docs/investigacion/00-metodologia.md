# Framework Forense de Simulación Social — Tello, Huila 2026

**Versión:** 2.0
**Fecha:** 2026-06-19
**Estado:** Operativo, validado por nativo huilense

---

## Resumen ejecutivo

Sistema computacional para simular la sociedad de Tello, Huila (Colombia) con el rigor metodológico de un estudio forense. Permite:

1. **Control granular del tiempo virtual** (pausa, velocidad x1-x28800, salto a timestamps arbitrarios)
2. **Inyección reproducible de eventos** (chismes, conflictos, intervenciones, observaciones)
3. **Logging estructurado** (JSONL append-only con chain of custody)
4. **Análisis cuantitativo** (cobertura, velocidad de propagación, super-spreaders, escépticos)
5. **Visualización** (mapa geográfico + red social + dashboard temporal)

---

## Arquitectura del sistema

```
┌─────────────────────────────────────────────────────────────┐
│  Panel de Control CLI  (panel_control.py)                  │
│  init / play / pause / speed / step / jump / inject / ...  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Framework de Experimentos  (experimento.py)               │
│  Escenario + Eventos + Log + Gossip + Conflictos + Export  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Motor de Simulación Geográfica  (simulacion_v3_geografica) │
│  Co-presencia + Probability + LLM sampling                  │
└────┬──────────────┬──────────────┬─────────────────────────┘
     │              │              │
     ▼              ▼              ▼
┌─────────┐  ┌──────────┐  ┌──────────────┐
│ Reloj   │  │ Geo +    │  │ PromptBuilder│
│ virtual │  │ Niños    │  │ + MultiClient│
│         │  │          │  │ (DeepSeek)   │
└─────────┘  └──────────┘  └──────────────┘
```

---

## Componentes

### 1. `reloj.py` — Reloj virtual

**Función:** Provee tiempo virtual desacoplado del wall-clock.

**API principal:**
```python
from reloj import Reloj
from datetime import datetime

r = Reloj(datetime(2026, 6, 19, 6, 0), velocidad=60.0)
r.avanzar(3600)              # avanza 1h virtual
r.avanzar_wall(60)           # avanza 60*60=3600s con velocidad 60x
r.set_velocidad(3600)       # 1h virtual por segundo wall
r.pausar() / r.reanudar()
r.saltar_a(datetime(2026, 6, 24, 18, 0))
```

**Eventos ancla 2026 predefinidos:**
- `crisis_acueducto_inicio` (5 abril)
- `festival_san_juan` (24 junio)
- `festival_san_pedro` (29 junio)
- `reinado_nacional` (5 julio)

### 2. `experimento.py` — Framework de experimentos

**Función:** Encapsula un experimento reproducible.

**Estructura:**
```python
exp = Experimento(
    nombre="gossip_acueducto_v1",
    escenario=Escenario(
        t_inicial=datetime(2026, 6, 19, 6, 0),
        duracion_segundos=86400,
        agentes={...},
        random_seed=42,
        hipotesis="..."
    ),
    version_prompt="2.0",
)
exp.sembrar_gossip(t, origen, topic, veracidad, intensidad)
exp.trigger_conflicto(t, conflicto_id, participantes)
exp.correr(paso_segundos=300)
exp.exportar("experimentos/v1/", comprimir=True)
```

**Output por experimento:**
```
experimentos/{nombre}/
├── manifest.json       (metadata, seed, hipotesis, hash biografias)
├── log.jsonl[.gz]      (eventos append-only)
├── gossip_graph.json   (edges de propagación)
├── snapshots.json      (estados en tiempos arbitrarios)
└── conflictos.json     (historia de cada conflicto)
```

### 3. `geo_tello.py` — Geografía forense

**Catálogo:** 34 edificios + 26 adultos georreferenciados + 6 veredas.

**Coordenadas cartesianas locales:**
- Origen: Plaza Bolívar (0,0)
- +x = ESTE (Río Magdalena)
- -x = OESTE (montañas, veredas)
- +y = NORTE (Neiva, 60 km)
- -y = SUR
- 1 unidad = 30 metros

**Cada edificio tiene metadata forense:**
```python
{
    "id": "tienda_dona_rosa",
    "tipo": "comercial",
    "coords": (-1, -1),
    "direccion": "Carrera 5 # 4-21",
    "fuente": "F1" | "F2" | ...,
    "confianza": 0.95,  # 1.0 = confirmado por operador
    "notas": "..."
}
```

**Cada agente tiene:**
```python
{
    "casa": "finca_matarredonda",
    "casa_coords": (-8, -2),
    "trabajo": "finca_matarredonda",
    "trabajo_coords": (-8, -2),
    "ruta_diaria": [
        ("05:00", "casa", "despertar"),
        ("06:00", "iglesia_san_antonio", "misa"),
        ...
    ],
    "generacion": "anciano" | "adulto" | "joven",
}
```

### 4. `ninos_tello.py` — 15 niños con perfiles forenses

**Distribución:**
| Edad | # niños | Etapa Piaget |
|---|---|---|
| 4-5 | 2 | Preoperacional |
| 6-9 | 4 | Operacional concreto inicial |
| 10-12 | 3 | Operacional concreto |
| 13-17 | 6 | Operacional formal |

**Capas por niño:**
1. Datos civiles (nombre, edad, grado)
2. Familia (con quién vive, padres, abuelos)
3. Escuela (jornada, docente, amigos)
4. Rutina diaria (5-7 items)
5. Conflictos específicos
6. Voz típica (muletillas, registro)
7. Metadata forense (fuente, confianza, notas)

**Temperamento Thomas & Chess:**
- Fácil: 11 niños (40% típico)
- Lento para calentar: 1 niño
- Difícil: 3 niños (riesgo: pandilla, sustancias)

### 5. `panel_control.py` — Panel CLI

**Comandos:**
```
init <escenario>     Inicializa experimento
play                 Corre en loop
pause                Pausa el reloj
speed <n>            Velocidad (1, 10, 60, 3600, ...)
step <segundos>      Avanza N segundos
jump <YYYY-MM-DD HH:MM>   Salta a timestamp
inject gossip|conflicto|nota [flags]
status               Estado actual
snapshot <etiqueta>  Capturar estado
export <ruta>        Exportar
reset                Resetear
eventos              Listar pendientes
log <n>              Ver últimas N entradas
quit                 Salir
```

**Escenarios predefinidos:**
- `gossip_acueducto` — Chisme de sobrecostos, 24h
- `manipulacion_alcalde` — Campaña de descrédito, 1 semana
- `conflicto_linderos` — Eliécer vs Rosalío, 72h
- `festival_reinado` — Durante Bambuco, 10 días
- `crisis_acueducto_recuerdos` — Volver al 5 abril

### 6. `dashboard_reloj.py` — Visualización

**Terminal (ANSI):**
```
======================================================================
 DASHBOARD FORENSE - SIMULACION TELLO
======================================================================
RELOJ VIRTUAL
  t_virtual:  2026-06-19 (viernes) 08:00
  velocidad: 60x  (corriendo)
  transcurrido: 2.00h virtuales desde t0
EXPERIMENTO
  nombre: gossip_acueducto
  seed: 42
  hipotesis: Chisme llega al 80% de adultos en 24h...
METRICAS
  log entries: 247
  gossip edges: 12
  conflictos activos: 1
  eventos pendientes: 3
TIMELINE 24h
  ...
```

**PNG (matplotlib):**
- Panel 1: Timeline de eventos por tipo
- Panel 2: Acumulación de gossip edges
- Panel 3: Estado de conflictos

### 7. `experimentos/` — Templates forenses

| Template | Réplicas | Condiciones |
|---|---|---|
| `gossip_propagation.py` | N | veracidad × intensidad |
| `conflict_escalation.py` | 4 | control, mediación cura, gossip previo, intervención institucional |
| `manipulation_campaign.py` | 4 | control, bajo, medio, alto |
| `empathy_roleplay.py` | 4 | control, inundación leve/severa, presión social |

Cada template corre N réplicas con seeds variables y exporta resultados individuales + dashboard + tabla comparativa.

### 8. `simulacion_v3_geografica.py` — Simulación integrada

**Integra todo:** corre la simulación completa con co-presencia geográfica, probabilidad realista, y muestreo LLM.

**Uso:**
```bash
# Sin LLM (estructura pura)
python simulacion_v3_geografica.py --duracion 4 --speed 60

# Con LLM (DeepSeek, ~$0.024/hora)
python simulacion_v3_geografica.py --duracion 4 --speed 60 --con_llm --llm_sample 0.1
```

**Niveles de simulación:**
- 1: Básico (cualquier par co-presente dialoga)
- 2: Con relaciones (filtrar por vinculos existentes)
- 3: Con probabilidad realista (default, inverso a distancia)
- 4: LLM autónomo (placeholder)

---

## Metodología estándar forense

Para cada experimento se documenta:

### 1. Hipótesis explícita
```python
hipotesis = "Rumor 'X' (v=0.2, i=2.0) plantado por origen=O a las 8:00 "
            "llega al 80% de adultos en 24h, con super-spreaders "
            "dona_rosa_tendera y padre_cecilio_cura."
```

### 2. Diseño experimental
- **Condiciones:** control vs tratamiento(s)
- **Réplicas:** N=5-10 por condición
- **Semillas:** random.Random(seed) reproducible
- **Variables:** independientes (manipuladas), dependientes (medidas), confundidoras (controladas)

### 3. Recolección de datos
- Log append-only JSONL con timestamps virtuales
- Snapshot pre/post experimento
- Export completo (manifest + log + gossip + conflictos + snapshots)

### 4. Análisis
- Cobertura (% agentes que recibieron chisme)
- Velocidad (tiempo a 50% cobertura)
- Distorsión (cambio en topic en cada transmisión)
- Super-spreaders (top N difusores)
- Escépticos (recibieron pero no retransmitieron)

### 5. Reproducibilidad
- `random_seed` registrado en manifest
- `version_prompt` registrado en manifest
- `biografias_hash` registrado en manifest
- Cualquiera puede re-correr el experimento con mismos parámetros

---

## Limitaciones conocidas

### L1: Encoding UTF-8
El sistema operativo (Windows PowerShell) tiene problemas con UTF-8 multibyte en archivos Python. Workaround: identificadores ASCII, contenido español en strings con `sys.stdout.reconfigure(encoding='utf-8')`.

### L2: Veracidad y Distorsión
El marco actual mide veracidad como atributo del seed (0.0-1.0) pero no calcula automáticamente la distorsión del topic después de N transmisiones. Esto requiere LLM-as-judge o análisis manual posterior.

### L3: Sin rollback
Un experimento divergente requiere re-correr desde t0 con el mismo seed. No hay checkpoints internos para rollback.

### L4: LLM sampling
Con `llm_sample < 1.0`, no todos los diálogos se generan con LLM. Esto introduce varianza en análisis cualitativo. Para análisis de contenido completo, usar `llm_sample = 1.0`.

### L5: Coordenadas aproximadas
Las coordenadas de edificios están estimadas a resolución de 30m (1 unidad). Errores de 1-2 unidades (30-60m) son posibles. Marcadas con `confianza < 0.7` cuando son inferidas.

### L6: Sin validación externa
Los agentes son validados por el operador (nativo huilense). No hay validación independiente de los perfiles forenses.

### L7: Recursos computacionales
LLM calls cuestan ~$0.0008 USD cada una. Una simulación completa de 1 semana con llm_sample=0.5 = ~$5-10 USD.

---

## Validación nativa huilense

10 diálogos generados por el sistema fueron evaluados por el operador (nativo huilense) y aprobados como línea base de autenticidad lingüística.

**Archivo:** `validacion_nativa_huilense.md`
**Log:** `VALIDATION_LOG.md`

Cualquier cambio al prompt cultural o a los perfiles requiere re-validación contra esta línea base.

---

## Archivos generados (referencia rápida)

```
generative/
├── reloj.py                          # Reloj virtual
├── experimento.py                    # Framework de experimentos
├── panel_control.py                  # CLI panel
├── dashboard_reloj.py                # Dashboard terminal + PNG
├── geo_tello.py                      # Geografía forense
├── ninos_tello.py                    # 15 niños
├── prompt_builder.py                 # Construcción de prompts
├── multi_client.py                   # Multi-provider LLM
├── motor_simulacion.py               # Motor LLM ya validado
├── simulacion_v3_geografica.py       # Integración final
├── visualizar_mapa_tello.py          # Mapa PNG + red
├── visualizar_red_social.py          # Red social PNG
├── experimentos/                     # Templates forenses
│   ├── gossip_propagation.py
│   ├── conflict_escalation.py
│   ├── manipulation_campaign.py
│   └── empathy_roleplay.py
├── docs/
│   ├── agentes/
│   │   ├── 01-biografias.md          # 25 perfiles adultos
│   │   └── 02-prompt-cultural.md     # 7 capas sociolingüísticas
│   └── investigacion/
│       ├── 00-metodologia.md         # Este archivo
│       └── 01-chismes.md             # TBD: hallazgos gossip
├── validacion_nativa_huilense.md     # Línea base validación
└── VALIDATION_LOG.md                 # Log de validaciones
```

---

## Próximos pasos

### Corto plazo
- [ ] Análisis cruzado de réplicas (estadística inferencial)
- [ ] Identificación automática de super-spreaders por betweenness centrality
- [ ] Métricas de distorsión (LLM-as-judge)

### Mediano plazo
- [ ] Visualización animada de propagación de gossip en el mapa
- [ ] Dashboard web (Flask/FastAPI + HTMX)
- [ ] Integración con engram para memoria persistente de agentes

### Largo plazo
- [ ] Validación cruzada con datos reales (Diario del Huila, Personería)
- [ ] Comparación con otros municipios del Huila
- [ ] Exportación a STIX 2.1 para sharing con MISP/Splunk
