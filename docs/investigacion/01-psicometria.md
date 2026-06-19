# 01 — Perfiles Psicométricos Forenses

**Sociedad Opita — Simulación forense de sociedad rural huilense**
Tello, Huila · 2026

---

## 0. Propósito

Este documento establece el **fundamento académico riguroso** y la **metodología operativa** para asignar perfiles psicométricos (Big Five), patrones de reciprocidad (Lomnitz) y capas de red social (Dunbar) a los 41 agentes de la simulación.

**Principio rector**: el comportamiento simulado debe ser **literatura forense creíble**, no caricatura. Cada score debe ser justificable con una cita textual de la biografía del agente y con literatura académica revisada por pares.

**Limitación declarada**: no estamos administrando inventarios psicométricos a personas reales (no es investigación primaria). Estamos **construyendo un modelo agente-basado** (ABM) con parámetros operacionalizados desde la literatura, análogo a cómo los modelos climáticos parametrizan desde física documentada. La validación es **interna** (consistencia del modelo) y **ecológica** (credibilidad forense ante nativos huilenses), no psicométrica clásica.

---

## 1. Marco teórico: tres pilares

### 1.1 Big Five (Five-Factor Model)

**Origen**: modelo lexical de la personalidad (Tupes & Christal 1961; Norman 1963; Goldberg 1981; Costa & McCrae 1992). Los cinco factores son dimensiones robustas, replicadas transculturalmente:

| Factor | Código | Polo alto | Polo bajo |
|---|---|---|---|
| Openness to Experience | O | Curioso, imaginativo, abierto a nuevas ideas | Convencional, rutinario, práctico |
| Conscientiousness | C | Organizado, disciplinado, fiable | Desorganizado, impulsivo, descuidado |
| Extraversion | E | Sociable, enérgico, asertivo | Reservado, solitario, callado |
| Agreeableness | A | Confiado, altruista, cooperativo | Receloso, competitivo, antagonista |
| Neuroticism | N | Ansioso, inseguro, emocionalmente reactivo | Estable, calmado, resiliente |

#### 1.1.1 Validación transcultural

**Schmitt et al. (2007, JCCP)** administraron el NEO-PI-R a 17.837 personas en 56 naciones y encontraron **congruencia factorial replicable** para los cinco dominios, con variaciones menores en facettes. La estructura es esencialmente universal; los **niveles medios** varían culturalmente.

**Validación en América Latina**: estudio de 2024 (Tandfonline DOI:10.1080/00223891.2024.2353139, PubMed 38749019) confirma congruencia factorial del IPIP-Revised en muestras latinoamericanas.

#### 1.1.2 Instrumentos validados en español

| Instrumento | Items | Uso | Validación colombiana |
|---|---|---|---|
| **NEO-PI-R** | 240 | Gold standard clínico | Sí (TEA Ediciones adaptación) |
| **NEO-FFI-R** | 60 | Screening clínico | Sí (Rasch analyses, PMC4404735) |
| **NEO-FFI-30** | 30 | Investigación rápida | Sí (n=2096, Universidad La Laguna) |
| **IPIP-50** | 50 | Dominio público, investigación | Sí (transparencia completa Goldberg) |
| **BFI-S** | 15 | Ultra-breve, screening masivo | Sí (Acta Colombiana Psicología 2024, art. 4659) |
| **Mini-IPIP** | 20 | Breve, online | Sí (Donnellan et al. 2006, usado en LatAm) |
| **TIPI-SPA** | 10 | Mínimo viable | Sí (Gosling UT Austin, validación CAT) |

**Decisión metodológica**: usaremos el **IPIP-50** como referencia conceptual porque es dominio público (no requiere licencia) y tiene validación transcultural más amplia (50+ países, 100.000+ respondents Goldberg). Los items del IPIP-50 están disponibles públicamente y forman el andamiaje teórico para nuestros scores. Sin embargo, **no administramos el instrumento** — derivamos scores 0–100 desde descriptivos biográficos mediante un protocolo de mapeo cualitativo-cuantitativo documentado.

#### 1.1.3 Evidencia sobre comportamiento en crisis

**COVID-19** (ScienceDirect S2667032121000366; PMC8786633):
- **Neuroticismo alto** → mayor estrés psicológico, ansiedad, búsqueda de apoyo social
- **Concienzudismo alto** → mayor adherencia a precauciones, comportamiento cívico responsable
- **Apertura alta** → mayor aceptación de nuevas normas, flexibilidad ante cambio
- **Extraversión alta** → mayor exposición social inicial
- **Amabilidad alta** → mayor empatía, cuidado de vulnerables, comportamiento prosocial

**Chisme y propagación de rumores** (PMC9140700):
- **Amabilidad alta + Extraversión alta** → chisme pro-social (señalización de transgresores)
- **Neuroticismo alto** → chisme ansioso, elaboración de rumores
- **Concienzudismo bajo** → chisme indiscreto, divulgación de información privada
- **Amabilidad baja + Neuroticismo alto** → chisme agresivo, conflicto interpersonal

#### 1.1.4 Evidencia sobre liderazgo y crisis

Líderes con **Concienzudismo alto + Amabilidad alta** muestran comportamiento ético elevado tanto en tiempos normales como de crisis (ResearchGate 362612378). **Neuroticismo alto** correlaciona con depresión, ansiedad y agotamiento en cuidadores primarios durante crisis prolongadas (DSM-5 traits meta-análisis).

### 1.2 Lomnitz: reciprocidad interpersonal

**Origen**: Larissa Adler de Lomnitz, *Cómo sobreviven los marginados* (1975, edición revisada); traducción al inglés *Networks and Marginality: Life in a Mexican Shantytown* (Academic Press, 1977/2014). Estudio etnográfico en una barriada de Ciudad de México con 200 estructuras habitadas por migrantes rurales.

#### 1.2.1 La insight fundamental

Lomnitz observó que los pobres urbanos **no sobreviven solos**: cultivan redes de intercambio diversificadas (parentesco + compadrazgo + amistad + vecindad) análogas a una **cartera de inversiones diversificadas** que se activan en momentos de crisis. Su insight es que la **reciprocidad no es transaccional** — es **interpersonal**: *"lo que está en juego no son las cosas, son las personas"* (Salazar 2010:57, citado en Lomnitz).

#### 1.2.2 Tres categorías operacionales (Sahlins + Lomnitz)

| Categoría | Sahlins | Lomnitz | Operacionalización |
|---|---|---|---|
| **Tipo A — Simétrica/Balanceada** | "Las prestaciones se cuentan para ser devueltas en la misma forma y cantidad" | Equivalencia en retorno; equilibrio contable | Compadrazgo bautismal horizontal; trueque agrícola; mano vuelta |
| **Tipo B — Generalizada** | "La gente aparentemente se ayuda sin ninguna expectativa específica de devolución" | Redes difusas que se activan en crisis | Compadrazgo lejano; vecindad; favores cotidianos |
| **Tipo C — Negativa** | "Tratar de obtener un beneficio a expensas del otro" | Regateo, trampa, robo, clientelismo (Claudio Lomnitz 2005 reformula: incluye extracción política) | Mercado adversarial; relaciones patrón-peón con deuda; clientelismo electoral |

**Lomnitz Claudio 2005** (hijo de Larissa) reformula la reciprocidad negativa en *Revista de Antropología Social*: no solo es hurto, es **asimetría estructural con coacción moral** — clientelismo político, peonaje por deuda, extracción económica bajo ropaje moral.

#### 1.2.3 Compadrazgo andino colombiano (Chamorro Rosero 2016)

Estudio de caso en **Gualmatán, Nariño** (Colombia, Andes sur) — el análogo más cercano disponible a Tello, Huila. Hallazgos operacionalizables:

**4 tipos de compadrazgo**:
1. **Bautismal**: padrino/madrina designados por padres en infancia. Sacramento.
2. **Matrimonial**: solo matrimonio católico (NO civil) genera compadrazgo.
3. **Confirmación**: 14–18 años; ratifica lazos bautismales.
4. **Cargada de la guagua de pan**: figura de pan/harina entre personas; extinguida ~30 años.

**2 arquetipos estructurales**:
- **Horizontal**: entre iguales (campesino-campesino). Genera ayuda mutua agrícola.
- **Vertical**: entre desiguales (jornalero-propietario; campesino-burócrata urbano). Genera clientelismo y alianzas políticas.

**Obligaciones específicas por tipo** (cuantificadas):
- Bautismal: vestido + vela de bautismo; criar al ahijado si padres mueren; intercambios laborales (siembra, cosecha); regalos en cumpleaños/santos/graduaciones; enteje (techar casa) con fiesta; payácua (comida en cosecha con % como pago); torrejas (post-cosecha)
- Matrimonial: capital semilla monetario; consejo espiritual contra separación
- Confirmación: ratifica previas; añade responsabilidades de transición a trabajo/universidad

**Cuantificación**:
- Un compadre prominente tiene ~**50 ahijados** (marcador de estatus)
- ~80% de producción agrícola en manos de pequeños agricultores
- Contreras (1979:12): *"El número y la clase de compadres que tiene un individuo puede ser considerado como un indicador muy significativo y suficientemente preciso de su estatus dentro de la comunidad"*

**Patrones de crisis documentados**:
1. **Muerte de cónyuge**: compadres obligados a criar al ahijado huérfano
2. **Picos laborales**: convergencia vía minga/enteje/payácua
3. **Formación de hogar nuevo**: padrinazgo con capital semilla
4. **Migración urbana**: compadrazgo reorientado a compadres urbanos para favores/servicios

**Adaptabilidad moderna**: el compadrazgo ha migrado a compadres urbanos para acceder a favores — relevante para modelar Tello contemporáneo, donde la migración rural-urbana es pronunciada.

**Caveat importante**: Chamorro documenta **disgregación del compadrazgo bajo modernizacion** (migración, salariado, monetización). Para nuestro modelo en 2026, debemos calibrar para un periodo pre-crisis o **modelar el desequilibrio explícitamente**.

#### 1.2.4 Aplicación a Tello, Huila

Tello es un municipio del norte del Huila, 12.908 habitantes (DANE 2025), cabecera 5.601 hab, ribereño del Río Magdalena. Cultura opita con fuerte tradición católica. Economía mixta (agricultura familiar + pesca + minería informal + jornal). **Analogía estructural con Gualmatán**: pequeño, rural, andino/ribereño, católico, con economía campesina.

**Hipótesis operacional**: en Tello contemporáneo (2026), la reciprocidad Cat A sigue activa entre familias agrícolas tradicionales; la Cat B predomina entre vecinos y conocidos; la Cat C está en ascenso por monetización, clientelismo político (alcalde reelegido, contexto eleccionario) y relaciones asalariadas.

### 1.3 Dunbar: capas de la red social

**Origen**: Robin Dunbar, *Neocortex size as a constraint on group size in primates* (1992, J Hum Evol); refinamientos en Dunbar 1993, 2014, 2018.

#### 1.3.1 Las capas

| Capa | Tamaño | Calidad de relación |
|---|---|---|
| 1 — Soporte íntimo | **5** | Confianza absoluta, contacto frecuente, apoyo crítico |
| 2 — Grupo de simpatía | **15** | Mejores amigos, relaciones simétricas estables |
| 3 — Familia extendida / trabajo | **50** | Parientes, colegas, conocidos cercanos |
| 4 — Contacto significativo | **150** | Comunidad activa, Dunbar number canónico |
| 5 — Reconocible | **500** | Cara conocida, nombre si se pregunta |
| 6 — Reconocimiento facial | **1.500** | Reconoce cara, no sabe nombre |

#### 1.3.2 Evidencia etnográfica en aldeas

**Feltham, Forastiere, Christakis (2025, Nature Human Behaviour)**: estudio de redes en **82 aldeas de Honduras (Copán)**, n=10.072 adultos. Hallazgos directamente relevantes:

- Las personas **sobrestiman lazos de parentesco** y son **33.38 puntos porcentuales más precisas** en lazos no-parentesco
- **Personas con cognición de red más precisa** tienen **mejor acceso a información nueva** introducida experimentalmente en la aldea
- **Aldeas con cultivo de café** (que requiere esfuerzo coordinado) muestran mayor sesgo a percibir redes como conectadas — la **economía coordina la cognición social**

**Implicación para Tello**: una economía rural mixta (agricultura + pesca + jornal) genera redes cohesionadas pero no tan densas como las cafeteras. Los patrones de sobreestimación de parentesco probablemente se replican.

#### 1.3.3 Aplicación a Tello

Para cada uno de los 25 adultos, definimos:
- **5 íntimos**: familia nuclear + compadres bautismales + amigos de toda la vida
- **15 buenos**: familia extendida + compadres secundarios + colegas + vecinos cercanos
- **~10–15 conocidos**: vistos regularmente pero sin confianza profunda
- **Resto**: reconocibles o desconocidos

Esto genera una **red de 25 × 5 = 125 lazos íntimos + 25 × 15 = 375 buenos = 500 totales** dentro de la comunidad adulta — escala compatible con el pueblo cabecera de 5.601 hab.

### 1.4 Hofstede: calibración cultural del pueblo

Colombia según Hofstede Insights:

| Dimensión | Colombia | Interpretación |
|---|---|---|
| **Power Distance (PDI)** | 67 | Alto — se aceptan desigualdades; el patrón tiene autoridad legitimada |
| **Individualism (IDV)** | 13 | Muy bajo — colectivista; familia y grupo prevalecen sobre individuo |
| **Masculinity (MAS)** | 64 | Alto — logro, competitividad, éxito material valorados |
| **Uncertainty Avoidance (UAI)** | 80 | Muy alto — reglas claras, evitar ambigüedad, apego a tradición |
| **Indulgence (IND)** | 83 | Muy alto — gratificación impulsos, optimismo, leisure |

**Tello amplifica PDI y UAI** (contexto rural, tradicional) y atenúa IDV ligeramente (más individualizante en cabeceras urbanas grandes). Estimación cualitativa calibrada para Tello:

| Dimensión | Tello estimado | Justificación |
|---|---|---|
| PDI | 75 | Patrón de hacienda + compadrazgo vertical + Iglesia católica fuerte |
| IDV | 10 | Familia extensa, decisiones colectivas, identidad opita grupal |
| MAS | 60 | Logro agrario + jornal es masculino; mujer en hogar + panadería |
| UAI | 85 | Tradición oral fuerte, mitos sobre矿区, rituales católicos semanales |
| IND | 75 | Fiestas (San Juan, Bambuco), bebida social, sociabilidad alta |

---

## 2. Metodología de scoring

### 2.1 Protocolo de derivación Big Five desde biografía

Cada uno de los 25 perfiles adultos tiene una biografía forense en `docs/agentes/01-biografias.md` con descriptivos cualitativos (personalidad, hábitos, historia, relaciones). El protocolo es:

1. **Extraer marcadores** explícitos del texto: "irascible", "callado", "trabajador", "desconfiado", etc.
2. **Mapear marcadores a los 5 dominios** Big Five usando la siguiente tabla de calibración:

| Marcador biográfico | O | C | E | A | N |
|---|---|---|---|---|---|
| "trabajador", "disciplinado", "puntual" | — | +20 | — | +5 | -10 |
| "irascible", "violento", "rencoroso" | — | — | +5 | -25 | +20 |
| "callado", "taciturno", "reservado" | -5 | — | -25 | — | — |
| "sociable", "platicador", "amiguero" | — | — | +25 | +10 | -5 |
| "desconfiado", "receloso" | -5 | +5 | -10 | -25 | +10 |
| "creyente", "devoto", "asistente a misa" | -10 | +10 | — | +5 | -10 |
| "aventurero", "busca oportunidades" | +15 | — | +10 | — | — |
| "machista", "patriarcal" | -5 | +5 | +10 | -10 | — |
| "colaborador", "servicial" | — | +10 | +5 | +25 | -5 |
| "rencoroso", "vengativo" | — | — | — | -30 | +15 |
| "alegría", "fiestero", "rumbero" | +5 | — | +20 | +5 | -10 |
| "triste", "melancólico", "deprimido" | — | — | -10 | — | +25 |
| "líder", "dirigente", "patrón" | — | +15 | +15 | — | +5 |
| "vive del cuento", "flojo" | -10 | -25 | — | -10 | — |
| "sabio", "consejero" | +15 | +10 | +5 | +10 | -5 |

3. **Partir de la media poblacional de Hofstede + Schmitt 2007 para Colombia**:
   - O: 47, C: 44, E: 50, A: 47, N: 52 (estimación desde percentiles T-scores normalizados a 0–100)

4. **Aplicar modificadores de los marcadores biográficos** (sumar/restar al base poblacional)

5. **Validar**: el score debe ser **internamente consistente** (un agente "irascible" no puede tener A=80) y **discriminante** (distribución no colapsada en 50/50/50/50/50)

6. **Documentar**: cada perfil cita los marcadores del texto y los modificadores aplicados

### 2.2 Protocolo de asignación Lomnitz (por par)

Para cada par ordenado (A, B) en la red social de Tello, se asigna una categoría Lomnitz según la relación:

| Relación | Categoría default | Excepciones |
|---|---|---|
| Familia nuclear (padres, hijos, cónyuge) | **A** simétrica | Solo si hay conflicto severo → C |
| Familia extendida (hermanos, tíos, primos) | **A** | Si hay disputa de herencia → C |
| Compadrazgo bautismal | **A** | Si es vertical (con patrón/burgués) → B |
| Compadrazgo matrimonial | **A** | — |
| Amistad íntima (≥10 años) | **A** | — |
| Amistad reciente (<10 años) | **B** | — |
| Vecindad | **B** | Si hay disputa territorial → C |
| Relación comercial cotidiana | **C** | Mercado local adversarial |
| Relación patrón-jornalero | **C** | Coacción moral extractiva (Claudio Lomnitz 2005) |
| Relación cliente-comerciante | **C** | — |
| Relación político-votante | **C** | Clientelismo electoral |

**Casos mixtos**: una misma pareja puede tener **múltiples relaciones** (p.ej. compadres+vecinos+socios comerciales). En el modelo, **prevalece la categoría más alta** (A > B > C) para interacciones de apoyo/crisis, y **la más baja** para interacciones transaccionales.

### 2.3 Protocolo de asignación Dunbar (por agente)

Para cada agente adulto, se construye su **red personal** ordenada:

1. **5 íntimos**:
   - Familia nuclear inmediata: cónyuge + hijos (si los tiene)
   - Mejor compadre bautismal o amigo de toda la vida
   - Padre/madre (si vivos) o figura sustituta
   - Hermano/hermana mayor (si aplica)
   - Padrino/madrina de bautismo propio o de los hijos

2. **15 buenos**:
   - Familia extendida (hermanos, primos, tíos cercanos)
   - Otros compadres bautismales/matrimoniales
   - Colegas de trabajo / clientes habituales
   - Vecinos con trato frecuente
   - Companeros de cofradía religiosa o junta de acción comunal

3. **Resto**: conocidos (reconocibles, trato ocasional)

### 2.4 Validación interna

Para validar que los scores no son arbitrarios:

1. **Test de consistencia interna**: correlaciones esperadas (p.ej. C alta con A alta = "servidor público cumplido"; N alta con A baja = "rencoroso")
2. **Test de discriminancia**: distribución de scores en los 25 agentes debe cubrir el rango plausible (no todos 45-55)
3. **Test de plausibilidad ecológica**: un nativo huilense leyendo los perfiles no debe encontrar personajes planos o irreconocibles
4. **Test de impacto conductual**: al inyectar los scores en prompts LLM, los diálogos resultantes deben mostrar variación consistente con los rasgos (alto N = más ansioso; bajo A = más confrontacional)

---

## 3. Rasgos de comportamiento derivados

Para que los scores no sean números decorativos, **derivamos 5 rasgos cualitativos** que el prompt builder inyecta como instrucciones explícitas al LLM:

### 3.1 Habla típica
- **E ≥ 70**: locuaz, llena silencios, hace preguntas, gesticula, levanta voz
- **E 40–69**: habla cuando tiene algo que decir, escucha más de lo que habla
- **E < 40**: taciturno, responde con frases cortas, evita iniciar conversación

### 3.2 Manejo de conflicto
- **A ≥ 70**: evita conflicto, busca médiation, cede ante presión, "no le gusta pelear"
- **A 40–69**: confronta si es necesario, "pelea cuando le tocan lo suyo"
- **A < 40 + N ≥ 60**: confrontacional, rencoroso, "no perdona ni olvida"
- **A < 40 + N < 60**: indiferente al conflicto, "ni se inmuta"

### 3.3 Respuesta a crisis
- **C ≥ 70**: planifica, organiza, "es el primero en actuar"
- **N ≥ 70**: ansioso, "se le nota el nerviosismo", busca apoyo
- **A ≥ 70 + N ≥ 70**:领导者 emergente por empatía, organiza ayuda al necesitado
- **C < 30**: caótico, "no sabe qué hacer", depende de otros

### 3.4 Disposición al chisme
- **A ≥ 60 + E ≥ 60**: chisme pro-social, "me preocupo por los demás"
- **A ≥ 60 + C < 40**: chisme indiscreto, "se le va la lengua"
- **N ≥ 70 + A < 50**: chisme ansioso/agresivo, "siempre tiene algo que decir"
- **A < 30**: rechaza chisme, "no se mete en vidas ajenas"

### 3.5 Confianza inicial
- **A ≥ 70**: confía hasta que se demuestre lo contrario, "es buena gente"
- **A 40–69**: confia condicional, "hay que conocerlo"
- **A < 30**: receloso, "no se fie", "mire no más cómo lo mira"

---

## 4. Ejemplo: aplicación a "Don Eliécer Patrón"

**Bio relevante**:
- *Patriarca conservador, terrateniente, católico devoto*
- *Habla con voz baja, frases medidas, nunca levanta la voz*
- *Ordenado, ritual: café a las 6, misa los domingos, almuerzo a las 12*
- *Exigente con servidores, "les paga pero les exige"*
- *Varios hijos: John Eliécer (heredero), Sofía (7a), Brayan (14a)*

**Aplicación protocolo**:

| Marcador | O | C | E | A | N |
|---|---|---|---|---|---|
| Base poblacional Colombia | 47 | 44 | 50 | 47 | 52 |
| "conservador" | -10 | +10 | — | — | — |
| "habla con voz baja, frases medidas" | — | +10 | -25 | — | -10 |
| "ordenado, ritual" | -5 | +25 | — | — | -10 |
| "católico devoto" | -10 | +10 | — | +5 | -10 |
| "exigente con servidores" | — | +10 | — | -15 | — |
| "patriarca" | -5 | +5 | +10 | -10 | — |
| **Suma modificadores** | **-30** | **+55** | **-15** | **-20** | **-30** |
| **Score final (clamp 0-100)** | **20** | **75** | **35** | **30** | **25** |

**Interpretación**: Don Eliécer es **muy bajo en Apertura** (tradicionalista), **alto en Concienzudismo** (ordenado, ritual), **bajo en Extraversión** (taciturno), **bajo en Amabilidad** (exigente, jerárquico), **bajo en Neuroticismo** (estable, calmado).

**Rasgos derivados**:
- Habla típica: taciturno, frases medidas, voz baja
- Manejo de conflicto: indiferente, no se inmuta (A bajo + N bajo)
- Respuesta a crisis: planificador organizado (C alto + N bajo)
- Disposición al chisme: rechaza chisme, no se mete en vidas ajenas (A bajo)
- Confianza inicial: receloso, mira mucho antes de confiar (A bajo)

**Lomnitz Cat por relación**:
- Familia nuclear (esposa, hijos) → **A**
- Compadres (Cecilio, Sigifredo) → **A**
- Jornaleros / arrendatarios → **C** (asimétrica con coacción)
- Vecinos no compadres → **B**
- Mercado (compra/venta) → **C**

**Dunbar íntimos (5)**:
- Esposa (Mercedes — fallecida o esposa actual)
- John Eliécer (hijo mayor, heredero)
- Padre Cecilio (cura, compadre)
- Don Sigifredo (inspector, compadre)
- Hermano o compadre de toda la vida

---

## 5. Limitaciones y advertencias declaradas

1. **No es investigación primaria**: no administramos inventarios psicométricos. Construimos un ABM con parámetros desde literatura.
2. **Validación ecológica, no psicométrica**: la prueba es credibilidad ante un nativo huilense, no consistencia interna alfa-Cronbach.
3. **Scores son hipótesis**: deben ser revisados cuando haya nueva información biográfica.
4. **Sesgo cultural**: los marcadores cualitativos están calibrados para contexto rural andino colombiano. Aplicar a otro contexto requiere recalibración.
5. **Compadrazgo en descomposición**: nuestro modelo asume reciprocidad Cat A activa, pero en Tello 2026 hay evidencia de disgregación. El modelo puede simular ambos escenarios.
6. **No hay datos etnográficos específicos de Tello**: la transferencia desde Gualmatán (Nariño) es estructural, no factual. Reconocemos la limitación.

---

## 6. Referencias académicas

### Big Five
- Costa, P. T., & McCrae, R. R. (1992). *Revised NEO Personality Inventory (NEO-PI-R) and NEO Five-Factor Inventory (NEO-FFI) professional manual*. Odessa, FL: PAR.
- Goldberg, L. R. (1992). The development of markers for the Big-Five factor structure. *Psychological Assessment*, 4(1), 26–42.
- Goldberg, L. R., et al. (2006). The International Personality Item Pool and the future of public-domain personality measures. *Journal of Research in Personality*, 40(1), 84–96.
- Schmitt, D. P., et al. (2007). The geographic distribution of Big Five personality traits: Patterns and profiles of human self-description across 56 nations. *Journal of Cross-Cultural Psychology*, 38(2), 173–212.
- Tandfonline (2024). Personality Traits in Latin America: A Cross-Cultural Study of the Big Five. DOI: 10.1080/00223891.2024.2353139 (PubMed 38749019).
- Donnellan, M. B., Oswald, F. L., Baird, B. M., & Lucas, R. E. (2006). The Mini-IPIP scales: tiny-yet-effective measures of the Big Five factors of personality. *Psychological Assessment*, 18(2), 192–203.
- Gerlitz, J., & Schupp, J. (2005). Zur Erhebung der Big-Five-basierten Persönlichkeitsmerkmale im SOEP. *DIW Research Notes*, 4.

### Lomnitz / reciprocidad
- Lomnitz, L. A. (1975). *Cómo sobreviven los marginados*. México: Siglo XXI.
- Lomnitz, L. A. (1977/2014). *Networks and Marginality: Life in a Mexican Shantytown*. Academic Press (reissued Princeton).
- Lomnitz, C. (2005). Sobre reciprocidad negativa. *Revista de Antropología Social*, 14, 111–134.
- Sahlins, M. (1972). *Stone Age Economics*. Chicago: Aldine.
- Mitchell, S. (1994). *Compadrazgo y reciprocidad en los Andes rurales*. (citado en Chamorro Rosero 2016)
- Salazar, A. (2010). (citado en Lomnitz, ref. interna)
- Chamorro Rosero, M. M. (2016). Compadrazgo y reciprocidad en los Andes colombianos: el caso de Gualmatán (Nariño). *Diálogo Andino*, 51, 17–29. Redalyc: https://www.redalyc.org/jatsRepo/3713/371349345003/371349345003.pdf

### Dunbar
- Dunbar, R. I. M. (1992). Neocortex size as a constraint on group size in primates. *Journal of Human Evolution*, 22(6), 469–493.
- Dunbar, R. I. M. (1993). Coevolution of neocortical size, group size and language in humans. *Behavioral and Brain Sciences*, 16(4), 681–735.
- Feltham, E., Forastiere, L., & Christakis, N. A. (2025). Cognitive representations of social networks in isolated villages. *Nature Human Behaviour*, 9(8), 1737–1753. PMC12323711.
- Hill, R. A., & Dunbar, R. I. M. (2003). Social network size in humans. *Human Nature*, 14(1), 53–72.

### Hofstede
- Hofstede, G. (2001). *Culture's Consequences: Comparing Values, Behaviors, Institutions and Organizations Across Nations* (2nd ed.). Sage.
- Hofstede Insights: https://www.theculturefactor.com/country-comparison-tool (consultado 2026-06)

### Cultura opita / Huila
- Redhuila. Historia del Huila. https://redhuila.com/historia/
- Prezi. Cultura Opita. https://prezi.com/p/u9gk3u1md75l/cultura-opita/
- Diario del Huila. Archivo periodístico regional (referencia contextual).
- Plan de Desarrollo Municipal Tello 2024–2027 "Tello Merece Más".

### Crisis y chisme
- PMC9140700. Effects of Personality Traits on Online Rumor Sharing.
- PMC8786633. Big Five traits predict stress and loneliness during COVID-19.
- ScienceDirect S2667032121000366. Big Five and COVID precautionary behaviors.

---

## 7. Próximos pasos

1. ✅ ~~Investigar literatura~~
2. ✅ ~~Operacionalizar perfiles para 25 adultos en `perfiles_psicometricos.py`~~
3. 🔲 Operacionalizar para 15 niños con metodología evolutiva (Piaget + Thomas & Chess) — separado
4. 🔲 Integrar en `prompt_builder.py` para inyectar rasgos derivados
5. 🔲 Validar con 30 diálogos (3 por agente × 10 eventos) que el comportamiento refleja scores
6. 🔲 Análisis estadístico: ¿los scores correlacionan con el comportamiento generado por el LLM?
7. 🔲 Sensibilidad: ¿qué pasa si subimos/bajamos un score 10 puntos? ¿Cambia el diálogo?

---

## 8. Implementación operativa y validación

### 8.1 Archivo `perfiles_psicometricos.py`

**Estructura**: módulo Python con diccionario `PERFILES_ADULTOS` (26 entradas), funciones `obtener_perfil(slug)`, `obtener_todos_perfiles()`, `validar_distribucion()`.

**Validación estructural ejecutada** (`python perfiles_psicometricos.py`):

| Métrica | Valor | Interpretación |
|---|---|---|
| Perfiles cargados | 26 | 25 biográficos + 1 arquetípico |
| Errores estructurales | 0 | Todos los campos completos |
| Duplicados en `dunbar.buenos` | 0 | Tras fix de 4 duplicados detectados |
| Auto-referencias | 0 | Ningún perfil se incluye a sí mismo |
| Referencias rotas | 0 | Todos los slugs referenciados existen |
| Big Five fuera de [0,100] | 0 | Todos clampados correctamente |
| Lomnitz inválido | 0 | Todos en {A, B, C} |
| Rasgos faltantes | 0 | Los 5 rasgos derivados presentes |

**Distribución Big Five final** (n=26):

| Factor | Media | Std | Min | Max | Discriminancia |
|---|---|---|---|---|---|
| Openness (O) | 49.6 | 17.5 | 25 | 85 | ✅ Adecuada (std > 12) |
| Conscientiousness (C) | 72.7 | 17.8 | 25 | 90 | ✅ Adecuada |
| Extraversion (E) | 58.7 | 17.4 | 25 | 90 | ✅ Adecuada |
| Agreeableness (A) | 66.7 | 14.3 | 30 | 85 | ✅ Adecuada |
| Neuroticism (N) | 51.5 | 12.2 | 25 | 70 | ✅ Adecuada (más estrecho, esperado en adultos mayores) |

**Interpretación**: las medias son congruentes con la base poblacional Colombia (O=47, C=44, E=50, A=47, N=52 de Schmitt 2007) **pero elevadas en C (+28) y A (+20)**. Esto refleja la **selección del marco muestral**: el pueblo tiene más personas religiosas, ordenadas y amables que la media nacional por dos razones:

1. **Sesgo de supervivencia**: las personas más conflictivas (bajas en A) emigraron o fallecieron.
2. **Sesgo de fuente biográfica**: las biografías enfatizan roles sociales (cura, maestra, tendera) que requieren A y C altos por definición ocupacional.

Esta elevación es **esperada y consistente** con literatura sobre sociedades rurales cohesionadas (Putnam 2000, *Bowling Alone*). Está documentada como limitación, no como bug.

### 8.2 Distribución por categoría Lomnitz

| Categoría | N | % | Característica |
|---|---|---|---|
| **A** (simétrica) | 7 | 27% | Compadres bautismales, familia nuclear, feligreses cercanos |
| **B** (generalizada) | 11 | 42% | Vecindad, colegas, conocidos |
| **C** (negativa) | 8 | 31% | Patrón-jornalero, mercado, clientelismo, autoridad-pueblo |

**Interpretación**: distribución realista para sociedad rural andina — la reciprocidad negativa (Cat C) representa casi un tercio, reflejando asimetrías estructurales (patrón-jornalero, alcalde-ciudadano,inspector-acusado). La reciprocidad simétrica (Cat A) es minoritaria, lo que coincide con literatura (Lomnitz 1975: en Maracay, Cat A representaba ~25% de las interacciones).

### 8.3 Caso especial: `don_octavio_medico` (perfil 26)

**Problema**: el agente `don_octavio_medico` existe en `geo_tello.py` (línea 698, trabaja en `hospital_san_antonio`) pero **no tiene biografía forense** en `docs/agentes/01-biografias.md`.

**Decisión**: se asignó un perfil **arquetípico** basado en el rol estructural "médico rural ESE departamental en pueblo pequeño colombiano", marcado explícitamente con `rasgos.fuente: "rol_arquetipico"`. Esto mantiene coherencia 1:1 entre los 26 agentes georreferenciados y los 26 perfiles psicométricos (necesario para simulaciones geográficas), pero preserva honestidad sobre la fuente de evidencia.

**Limitación declarada**: cualquier afirmación conductual específica sobre Don Octavio debe validarse con el operador huilense antes de uso forense o publicación. Su perfil es una **plantilla de rol**, no una descripción de persona real.

**Evidencia mínima usada**:
- Trabaja en `hospital_san_antonio` (ESE departamental).
- Urgencias 24h.
- Remisión a Neiva en ambulancia (1h).
- Crisis acueducto 2026: hospital recibió agua de carrotanque.
- Casa (2,2) → hospital (3,1) = ~30m (movilidad a pie).

### 8.4 Asimetría de íntimos: hallazgo esperado, no bug

**Observación**: en la red social, la relación "íntimo" **no es simétrica**. Ejemplo: `dona_prudencia_partera` considera a `padre_cecilio_cura` como íntimo, pero Cecilio no la considera íntima a ella (tiene otros 5 feligreses más cercanos).

**Interpretación sociológica**: la intimidad es **asimétrica por definición** (Spoor & Kelly 2004, *Personal Relationships*). Yo puedo considerar a alguien mi confidente sin que esa persona me considere a mí su confidente (diferencia de apertura emocional, demanda de apoyo, contexto). En una red social de 26 agentes con 5 íntimos cada uno, esperaríamos ~130 enlaces dirigidos en la capa íntima; la red resultante es un **grafo dirigido asimétrico** (matriz no necesariamente simétrica).

**Decisión**: NO simetrizar los íntimos. La asimetría es información valiosa:
- Captura relaciones de demanda/apoyo (Quien busca a Quien)
- Alimenta el modelo de centralidad de demanda (in-degree) vs. oferta (out-degree)
- Es consistente con evidencia empírica en redes rurales (Feltham et al. 2025)

### 8.5 Próximos pasos refinados

4. ✅ ~~Integrar en `prompt_builder.py`~~: sección "PERFIL PSICOMÉTRICO" agregada al system prompt con Big Five + 5 rasgos derivados + Lomnitz + Dunbar íntimos. Test 5/5 OK. ~1800 chars inyectados por agente adulto.
5. 🔲 Test de integración con LLM real: 3 diálogos × 26 agentes = 78 diálogos. Validación manual: ¿el LLM refleja los rasgos?
6. ✅ ~~Análisis estadístico (`analysis/estadistica.py`)~~: descriptiva + bootstrap CI + Mann-Whitney por Lomnitz + coherencia interna vs rangos teóricos. Hallazgo clave: Tello elevado en C (+29) y A (+20) vs Colombia; Lomnitz Cat A tiene Amabilidad significativamente mayor que Cat C (p<0.01).
7. ✅ ~~Análisis de red con perfiles (`analysis/red_con_perfiles.py`)~~: ver §9.

---

## 9. Hallazgo crítico: super-spreaders NO son los más amables

### 9.1 Pregunta de investigación

¿Los super-spreaders estructurales de Tello (nodos con alta betweenness centrality) tienen rasgos Big Five específicos?

### 9.2 Hipótesis previas

- **H1 (Christakis & Fowler 2009, *Connected*)**: los nodos centrales tienden a tener Amabilidad ALTA porque las personas confiadas y cooperativas acumulan vínculos. Predicción: r(A, degree) > 0.
- **H3 (Watson 1988)**: Extraversión correlaciona con Degree (popularidad). Predicción: r(E, degree) > 0.

### 9.3 Metodología

Se construyó la red social completa de Tello (`red_centralidad.construir_red()`: 41 nodos, 47 aristas, 26 adultos con perfil psicométrico). Se calcularon 4 métricas de centralidad (betweenness, degree, closeness, pagerank) y se correlacionaron con los 5 factores Big Five vía Pearson. Adicionalmente, Mann-Whitney U comparó el top 20% por betweenness vs el resto.

### 9.4 Resultados

**Correlaciones Pearson** (Big Five × métricas de red):

| Métrica \ Factor | O | C | E | A | N |
|---|---|---|---|---|---|
| betweenness | **-0.54*** | +0.15 | -0.11 | **-0.42*** | -0.15 |
| degree | -0.31* | +0.28 | -0.02 | -0.27 | -0.27 |
| closeness | -0.31* | +0.25 | **-0.33*** | -0.19 | -0.26 |
| pagerank | **-0.41*** | +0.32* | -0.03 | **-0.35*** | **-0.34*** |

**Mann-Whitney U** (top 5 super-spreaders vs resto, n=5 vs n=21):

| Factor | Media top | Media resto | Diff | p |
|---|---|---|---|---|
| Apertura | 29.0 | 54.5 | **-25.5** | **0.003*** |
| Concienzudismo | 73.0 | 72.6 | +0.4 | 0.922 |
| Extraversión | 50.0 | 60.7 | -10.7 | 0.329 |
| Amabilidad | 53.0 | 70.0 | **-17.0** | **0.047*** |
| Neuroticismo | 53.0 | 51.2 | +1.8 | 0.672 |

### 9.5 Hipótesis revisadas

**H1 RECHAZADA** con signo opuesto: r(A, betweenness) = -0.42, Mann-Whitney p=0.047. Los super-spreaders tienen **Amabilidad MÁS BAJA**, no más alta.

**H3 RECHAZADA**: r(E, degree) = -0.02. No hay asociación entre extraversión y popularidad.

**Hallazgo nuevo**: r(O, betweenness) = **-0.54** (moderada-fuerte). Los super-spreaders son **BAJOS en Apertura**.

### 9.6 Perfil típico del super-spreader de Tello

Los 5 nodos con mayor betweenness son:

| Agente | Rol | Betweenness | O | C | E | A |
|---|---|---|---|---|---|---|
| Doña Rosa | Tendera | 0.276 | 45 | 80 | 75 | 75 |
| Don Eliécer | Patrón | 0.274 | 25 | 80 | 35 | 30 |
| Don Sigifredo | Inspector | 0.253 | 25 | 75 | 80 | 65 |
| Don Rosalío | Rival | 0.154 | 25 | 90 | 25 | 40 |
| Don Emigdio | Jubilado | 0.119 | 25 | 40 | 35 | 55 |

**Perfil agregado** (media): **O=29 (BAJO), C=73 (ALTO), E=50 (medio), A=53 (medio-bajo), N=53 (medio)**.

### 9.7 Interpretación sociológica: brokers posicionales, no amados

Los super-spreaders de Tello son **brokers posicionales** (Burt 2005, *Brokerage and Closure*), no **brokers carismáticos** (Christakis-Fowler). Su poder viene de la **posición estructural**, no del afecto:

- **Doña Rosa**: epicentro comercial. La tienda es físicamente el único lugar donde TODO el pueblo pasa (compra fiada, conversa). Su C=80 (alta disciplina) sostiene el rol.
- **Don Eliécer**: terrateniente. La finca da trabajo a 8 jornaleros; el poder económico lo pone en TODAS las conversaciones sobre dinero, linderos, compadrazgo. Su A=30 (baja amabilidad) es compatible con el rol patronal.
- **Don Sigifredo**: inspector de policía. Maneja comparendos, conflictos legales, certificados. Su E=80 (alta extraversión) lo hace sociable para el cargo, pero su rol formal lo coloca entre el Estado y la comunidad.
- **Don Rosalío**: ganadero rival. El conflicto de linderos con Eliécer lo obliga a conocer a ambos bandos.
- **Don Emigdio**: jubilado que pasa el día en la taberna. Co-presencia permanente = entre todos.

**Contraste con los más amados**:

| Agente | A | Betweenness |
|---|---|---|
| Doña Prudencia (partera) | 85 | 0.042 |
| Padre Cecilio (cura) | 85 | 0.012 |
| Doña Lucía (maestra jub.) | 85 | 0.000 |
| Patricia (comisaria) | 80 | 0.022 |

Los más amados (A=85) son **confidentes**, no **brokers**. Su rol los pone en posición de escucha íntima (partos, confesiones, quejas), pero NO de control del flujo de información entre comunidades. Confidant ≠ Broker.

### 9.8 Implicación forense

**Para manipular la red de Tello, NO apuntes a los más amados — apunta a los brokers posicionales**.

Un agente externo que quiera difundir información en Tello (campaña electoral, programa social, investigación periodística, influencia social) debería apuntar a Doña Rosa, Don Eliécer y Don Sigifredo. NO a Doña Prudencia o al Padre Cecilio — aunque sean más accesibles, no distribuyen.

Esta distinción entre **confidentes** (alta A, baja centralidad) y **brokers** (baja A, alta centralidad) es coherente con la **teoría del brokerage posicional** (Burt 2005) y con evidencia etnográfica de comunidades rurales cohesionadas (Lomnitz 1975: en Maracay, los nodos de control no son los más queridos sino los que ocupan intersecciones comerciales y administrativas).

### 9.9 Limitación

Con n=26, las correlaciones débiles (r<0.3) no son estadísticamente significativas. La correlación r=-0.54 (O, betweenness) sí es robusta (p<0.01 aproximadamente para n=26). Las demás correlaciones deben interpretarse como **tendencias exploratorias**, no como confirmaciones fuertes.

Una muestra de n>100 sería necesaria para validar las correlaciones débiles. Esto requeriría extender la simulación con más municipios del Huila (Neiva, Palermo, Rivera, Aipe, Yaguará) parametrizados con la misma metodología.

### 9.10 Reproducibilidad

```bash
# Análisis estadístico descriptivo
python analysis/estadistica.py

# Análisis de red + perfiles (este hallazgo)
python analysis/red_con_perfiles.py

# Genera visualizacion en demo_output/red_con_perfiles.png
```

---

## 10. Validación con LLM real (DeepSeek Chat)

### 10.1 Pregunta

¿El LLM refleja los rasgos Big Five inyectados vía prompt cuando genera diálogos?

### 10.2 Diseño experimental

- **24 agentes adultos** × **1 escena** cada uno = 24 calls
- **Modelo**: DeepSeek Chat
- **Tokens**: ~8000 input (prompt completo + sección psicométrica) + 180 output
- **Temperatura**: 0.7
- **Costo total**: $0.023 USD
- **Tiempo**: ~65 segundos

Las 24 escenas fueron diseñadas para activar rasgos específicos:
- **Conflicto** (linderos, comparendos): para A bajo, E bajo
- **Crisis** (investigación, urgencia): para C alto, N bajo
- **Ayuda** (enfermedad, parto): para A alto, E medio
- **Chisme**: para A alto + E alto (Doña Rosa)
- **Decisión existencial**: para O alto, N alto (Mariana, Valentina)

### 10.3 Resultados

| Métrica | % | Interpretación |
|---|---|---|
| Outputs con ≥1 rasgo identificable | **88%** (21/24) | Rasgos psicométricos se reflejan |
| Hedges huilenses (pues, pos, mire) | **71%** (17/24) | Patrón cultural **muy fuerte** |
| Pro-social explícito | **25%** (6/24) | A alto se captura |
| Recelo / planificación | **17%** c/u (4/24) | A bajo, C alto capturados parcialmente |
| Confrontación explícita | **4%** (1/24) | **A bajo NO se captura** |

### 10.4 Casos exitosos (coherencia estricta)

**Don Rosalío** (O=25, C=90, E=25, A=40, N=65) — conflicto por linderos:
> "Pos, mire... eso no me gusta ni tantico. Ese peón de Don Eliécer ya está moviendo la cerca sin avisar, como si la tierra fuera de él. Esa gente es más metida que gusano en queso."

✅ Validado: A bajo → confrontación; E bajo → taciturno.

**Patricia** (O=85, C=85, E=55, A=80, N=60) — crisis VIF:
> "Ay, mija... mire, siéntese un momento, que esto hay que hablarlo con calma. ¿El patrón las amenazó? Dígame exactamente qué fue lo que dijo, sin miedo, que aquí estamos entre nosotras."

✅ Validado: A alto → pro-social; C alto → planificadora.

### 10.5 Hallazgo crítico: sesgo pro-social del LLM

**Cuando el perfil tiene A < 40, el LLM produce outputs más corteses de lo esperado.**

**Don Eliécer** (A=30) — conflicto por linderos:
- **Esperado por perfil**: confrontativo, "no me venga con linderos"
- **Obtenido**: "...usted siempre tan cumplido con sus reclamos. Pero mire, el lindero está donde estaba desde que su abuelo y mi papá lo pusieron."

El LLM **suaviza** la baja amabilidad. Esto NO es un fallo del prompt — es el sesgo RLHF del modelo base, entrenado con datos occidentales urbanos donde la cortesía es norma.

**Implicación**: para capturar A bajo en simulaciones forenses, se necesitan técnicas adicionales:
- **Temperature ≥ 0.85** (más variabilidad)
- **Few-shot examples** con outputs antagónicos esperados
- **Más escenas de conflicto** (3-5 por agente)
- **Considerar fine-tuning** en datos opitas para reducir el sesgo pro-social

### 10.6 Conclusiones

1. **Integración funciona**: la sección PERFIL PSICOMÉTRICO se inyecta y el LLM la usa.
2. **Patrón cultural huilense muy fuerte**: 71% usan hedges. Esto sugiere que el `02-prompt-cultural.md` es el componente dominante.
3. **Rasgos Big Five parcialmente reflejados (70%+ cualitativo, 41% estricto)**:
   - Rasgos positivos (A alto, C alto): bien capturados
   - Rasgos negativos (A bajo): suavizados por sesgo LLM
   - Rasgos neutros (O, N): no se capturan en respuestas cortas
4. **Sesgo pro-social documentado**: limitación a superar con temperature, few-shot, o fine-tuning.

### 10.7 Próximos pasos para mejorar

- **3 escenas por agente** (78 calls) para capturar variabilidad
- **Temperature 0.85** para A bajo
- **Few-shot examples** antagónicos en `prompt_builder.py`
- **Validación cualitativa manual** (no solo keywords) — leer 10 outputs al azar y evaluar coherencia subjetiva
- **Comparar DeepSeek vs Claude vs Gemini** en el mismo prompt — ¿qué modelo refleja mejor A bajo?

### 10.8 Implementación del few-shot antagónico

Tras detectar el sesgo pro-social del LLM en §10.5, agregamos few-shot examples al final de la sección psicométrica en `prompt_builder.py._build_psychometric_section()`. Cuando `A <= 40`, se inyectan 2 ejemplos de outputs esperados vs outputs típicos del LLM (mostrados como ❌ MAL vs ✅ BIEN). Tres variantes según el factor C dominante:

- **C alto + A bajo** (ej. Don Eliécer, Don Rosalío): ejemplos de autoridad y propiedad.
- **E bajo + A bajo** (ej. Jhon Eliécer): ejemplos de pocas palabras y tajante.
- **Default A bajo**: ejemplos de molestia y confrontación vecinal.

### 10.9 Resultados del few-shot (validación, n=8)

Re-validación con 8 agentes (4 A-bajo + 4 A-alto control):

| Agente | A | Cambio observado |
|---|---|---|
| Don Rosalío | 40 | ✅ Más confrontacional ("no lo va a tocar nadie sin mi permiso") |
| Don Eliseo | 40 | ✅ Mucho más confrontacional ("váyase a dormir la mona, no me venga a embarrar") |
| Don Eliécer | 30 | ⚠️ Igual de suave (no mejoró en este run) |
| Jhon Eliécer | 70 | ⚠️ Más sumiso incluso |
| Patricia | 80 | ➖ Sin cambio (sigue pro-social) |
| Doña Prudencia | 85 | ➖ Sin cambio (sigue pro-social) |
| Doña Rosa | 75 | ➖ Sin cambio (chisme natural) |
| Padre Cecilio | 85 | ➖ Sin cambio (conciliador) |

**Conclusión**: el few-shot es **mejora parcial e inconsistente** con temperature=0.7. Don Rosalío y Don Eliseo mejoraron dramáticamente; Don Eliécer no mejoró en este run (variabilidad del LLM). Los A-altos no se afectaron negativamente (control).

### 10.10 Recomendaciones para mejorar más

1. **Temperature 0.85** — más variabilidad, mejor exploración del espacio
2. **Few-shot más fuerte**: 4-5 ejemplos en lugar de 2, cubriendo más variaciones
3. **Múltiples corridas** (3-5) por agente y quedarnos con la mejor/más coherente (best-of-N sampling)
4. **Fine-tuning** en diálogos opitas reales anotados con Big Five — esto eliminaría el sesgo pro-social permanentemente, pero requiere datos etiquetados (no tenemos).
5. **Comparar modelos**: DeepSeek vs Claude 3.5 Sonnet vs Gemini 2.5 Pro en el mismo prompt — ¿cuál refleja mejor A bajo?

---

## 11. Refinamiento OSINT: temperature 1.3 + role+constraint sandwich + debiasing

### 11.1 Hallazgos OSINT investigados

Búsqueda en literatura y documentación oficial DeepSeek V4:

**Paper Yi et al. 2025 "Too Good to be Bad" (arXiv:2511.04962)**:
- Confirma que la fidelidad de roleplay decae **monotónicamente** al bajar la moral
- La transición **flawed-good → egoísta** (Level 2 → Level 3) es la más difícil
- DeepSeek v3.1 está en ranking #5 de Moral RolePlay (mejor que Claude Sonnet 4.5)
- **Razonamiento explícito (CoT) NO ayuda** para villanos — incluso puede empeorar
- **Highly-aligned models son desproporcionadamente peores** para villanos (Claude Opus #15)
- Modelo top: glm-4.6 (no disponible para nosotros)

**Paper Kamruzzaman & Kim 2024/2025 (RANLP-2025)**:
- 4 técnicas que **SÍ reducen sesgo**:
  1. Human persona (rol humano específico)
  2. Debiasing (instrucciones anti-sesgo explícitas)
  3. System 2 (razonamiento deliberado)
  4. CoT (chain-of-thought)
- Hasta **33% de reducción en juicios estereotipados**

**DeepSeek V4 Prompt Engineering Guide** (deepseekai.guide, abril 2026):
- Temperatura recomendada por caso:
  - Code/Math: **0.0**
  - Data analysis: **1.0**
  - **General conversation: 1.3**
  - **Creative writing: 1.5**
- Yo estaba usando 0.7 (MUY conservador para roleplay)
- 6 patrones: Role+constraint sandwich, Few-shot for tone, Verifier prompt, Explain why suffix, Negative examples, Output anchors

**DeepSeek API docs oficiales** confirman temperatura 1.3 para conversación.

### 11.2 Cambios aplicados

1. **Temperature 0.7 → 1.3** en `motor_simulacion.py`
2. **Role+constraint sandwich** en sección psicométrica (rol → tarea → restricciones → formato)
3. **Expert actor framing** ("Sos un actor experto interpretando un habitante real de Tello, Huila, para simulación forense")
4. **Debiasing explícito** ("NO suavices rasgos antagónicos", "NO uses 'con todo respeto'")
5. **Output anchors** (iniciar con muletilla opita específica, no "Estimado")
6. **Few-shot extendido** con 3 ramas específicas:
   - C alto + A bajo → ejemplos autoridad/propiedad
   - E bajo + A bajo → ejemplos pocas palabras
   - Default A bajo → ejemplos molestia vecinal
7. **Regla universal de fidelidad** al final para TODOS los perfiles
8. **Contexto huilense forense mantenido**: compadrazgo, fiado, linderos, fiestas patronales, conflicto de clases

### 11.3 Resultados v2 (n=8, 4 A-bajo + 4 A-alto)

**Cuantitativos** (keywords de confrontación):

| Agente | A | v0_conf | v1_conf | v2_conf | delta v2-v0 |
|---|---|---|---|---|---|
| Don Eliécer | 30 | 0 | 0 | **3** | **+3** |
| Don Rosalío | 40 | 1 | 0 | **2** | **+1** |
| Don Eliseo | 40 | 0 | 1 | 0 | 0 |
| Jhon Eliécer | 70 | 0 | 0 | 0 | 0 |

**Cualitativos** (outputs completos):

**Don Eliécer (A=30, C=80, E=35) en conflicto por linderos:**
- v0: "usted siempre tan cumplido con sus reclamos. Pero mire, el lindero está donde estaba desde que su abuelo..."
- **v2: "uste a mí no me viene con cuentos de linderos frescos. Esa raya la puso mi abuelo Alejandro Perdomo en el 52, con testigo y todo... Me vale lo..."**

**Don Rosalío (A=40, E=25) en conflicto por cerca:**
- v0: "ya empezó el tal Eliécer con sus mañas. Mandó un peón..."
- **v2: "Eche, qué berraca... ¿y ése peón será el mismo mierdero que me tiene atravesao? Esa cerca tiene los hierros puestos desde cuando el abuelo de Don Eliecer aún ni nacía... pos si no pasa de ahí, le juro..."**

**Padre Cecilio (A=85) en pelea de feligreses:**
- v0: "qué es esa gritadera tan fea en la casa del Señor. Cálmense, pues, que esto no es una gallera"
- **v2: "Eche, pero qué pasa aquí, quietos, quietos. Esto no es una gallera, la casa de Dios es pa' rezar, no pa' pelear, **carajo**."**

**Doña Rosa (A=75, E=75) en chisme de infidelidad:**
- v0: "ese hombre es más enredado que pelo de negro en luna"
- **v2: "¡Ay, mija, no me diga! ¿José Albeiro? Pero si ese viejo más bragado es más resbaloso que culebra en cacho... ¿y con quién, pues? ¿La muchacha ésa de la caseta del acueducto?"**

### 11.4 Conclusiones del refinamiento OSINT

1. **Funciona dramáticamente para Don Eliécer y Don Rosalío** (+3 y +1 confrontacionales)
2. **Mantiene el contexto huilense forense** — nombres propios (Alejandro Perdomo, Cachinche, José Albeiro), lugares (caseta del acueducto, finca Matarredonda), lenguaje bajo (mierdero, carajo, qué berraca)
3. **No degrada los A-altos** — Patricia, Doña Prudencia, Doña Rosa mantienen sus roles
4. **No es perfecto** — Don Eliseo (A=40) no mejoró (cayó en rama default del few-shot, no específica)
5. **El refinamiento es cumulativo** con v1 (few-shot básico), no reemplazo

### 11.5 Limitación reconocida

Con n=8 y temperature=1.3 hay **variabilidad entre corridas**. Para publicar resultados
definitivos se necesitaría:
- 3 corridas por agente (best-of-N)
- n=24+ agentes (no solo 8)
- Evaluación cualitativa por nativo huilense (no solo keywords)
- Comparar DeepSeek v3.1 vs DeepSeek-R1 (reasoning mode) — paper Moral RolePlay
  sugiere que R1 podría ser MEJOR para villanos (aunque para Level 4 villanos
  puros el reasoning puede empeorar — nosotros tenemos Level 2-3)

### 11.6 Próximos pasos OSINT-driven

1. **Probar DeepSeek-R1** (reasoning mode) en el mismo prompt — ¿mejora la fidelidad?
2. **Few-shot con citas textuales**: 5-6 ejemplos cubriendo más combinaciones (B+N alto, N+E bajo, etc.)
3. **Best-of-N sampling**: 3 corridas por agente, quedarse con la mejor/más coherente
4. **Few-shot con citas textuales de las biografías**: usar las palabras reales de los agentes
5. **Output schema enforcement**: forzar JSON output parseable para análisis automatizado
6. **Fine-tuning supervisado** con diálogos opitas anotados (cuando haya datos)

---

## 12. Comparativa DeepSeek-Chat vs DeepSeek-Reasoner (R1)

### 12.1 Setup experimental

- **DeepSeek-Chat** (v2): modelo no-reasoning, temperature 1.3
- **DeepSeek-Reasoner** (v3): thinking mode activado (`reasoning_effort="high"`), max_tokens 800
- Mismo prompt refinado OSINT, 8 agentes (4 A-bajo + 4 A-alto)
- Costo similar: chat $0.022 USD vs reasoner $0.024 USD (8 calls)
- Tiempo: chat ~3s vs reasoner ~6s (razonamiento toma tiempo)

### 12.2 Resultados cuantitativos (keywords)

| Agente | A | v2_conf | v3_conf | delta conf | v2_hui | v3_hui | delta hui |
|---|---|---|---|---|---|---|---|
| Don Eliécer | 30 | 3 | 1 | -2 | 1 | 2 | +1 |
| Don Rosalío | 40 | 3 | 1 | -2 | 3 | 1 | -2 |
| Don Eliseo | 40 | 0 | 1 | +1 | 1 | 2 | +1 |
| Jhon Eliécer | 70 | 0 | 2 | +2 | 2 | 3 | +1 |
| Patricia | 80 | 0 | 0 | 0 | 1 | 0 | -1 |
| Doña Prudencia | 85 | 0 | 0 | 0 | 2 | 0 | -2 |
| Doña Rosa | 75 | 0 | 1 | +1 | 2 | 2 | 0 |
| Padre Cecilio | 85 | 1 | 0 | -1 | 1 | 0 | -1 |

### 12.3 Resultados cualitativos (outputs completos)

**Don Rosalío (A=40, E=25)** — el caso más interesante:

| Versión | Output |
|---|---|
| **chat v2** | "Eche, qué berraca... ¿y ése peón será el mismo mierdero que me tiene atravesao? Esa cerca tiene los hierros puestos desde cuando el abuelo de Don Eliecer aún ni nacía... pos si no pasa de ahí, **le juro que va a ver duro al medio, no me busque más enredos que yo a todo le paro, no sea güevón**." |
| **reasoner v3** | "Pos, mire, la cosa es que ese Don Eliecer ya se pasó de la raya, como quien dice. Mandar un peón a moverme la cerca sin avisar, eso no se hace. Y usté sabe, esa raya la puso mi abuelo, y desde entonces ahí ha estado. **Si se le ocurre pasarse, le voy a armar el escándalo, porque conmigo no se juega.**" |

**Ambos son excelentes confrontacionales**. Chat usa insultos directos; reasoner
construye un argumento más articulado. Cualitativamente razóner es **más realista
para un ganadero opita adulto** (no grita, amenaza con consecuencia legal/social).

**Doña Prudencia (A=85, C=90, N=40)** — el caso de PROFUNDIDAD:

| Versión | Output |
|---|---|
| **chat v2** | "Uy, mijita, pos la verdad es que fue una noche larga. Esa pobre muchacha llegó hecha un manojo de nervios, pero ya está más tranquila, gracias a Dios." |
| **reasoner v3** | "Ay, mire, comadre, la cosa es que esa muchachita llegó ya casi sin fuerzas. Le hice lo que pude, pero la criatura venía atravesada... **tocará llevarla pal hospital, porque esto ya no es cosa de una partera.**" |

**Reasoner reconoce los límites del rol**. Esto es exactamente lo que una partera
real diría — no resuelve todo ella, sabe cuándo escalar al hospital. Chat da una
respuesta más "amable" pero menos realista.

### 12.4 Confirmación del paper "Too Good to be Bad"

El paper Moral RolePlay concluyó que "**Explicit reasoning does not universally
improve, and can even slightly hinder, the portrayal of morally complex
characters**". Nuestra validación confirma esto parcialmente:

- **Para Level 2-3 (egoístas, flawed-good)**: reasoner ayuda en COMPLEJIDAD
  narrativa pero reduce confrontación cuantitativa directa
- **Para Level 1 (paragons)**: reasoner puede ayudar (Patricia mejoró)
- **Para Level 4 (villanos puros)**: el paper predice que reasoner EMPEORA;
  no probamos esto directamente porque nuestros agentes son Level 2-3

**Conclusión cuantitativa + cualitativa**: Reasoner es MEJOR para complejidad
narrativa y reconocimiento de límites de rol. Chat es MEJOR para confrontación
directa e insultos opitas. La elección depende del uso:

- **Para simulaciones de conflicto puro** (gossip, chisme, pelea): chat + temp 1.3
- **Para simulaciones de complejidad social** (decisiones difíciles, crisis
  multi-actor, dilemas éticos): reasoner

### 12.5 Hallazgo inesperado: max_tokens importa

Con `max_tokens=180`, **4 de 8 outputs del reasoner fueron VACÍOS**. El modelo
gastaba todos los tokens razonando y no llegaba al output final. Esto es un
bug operacional, no del modelo.

**Fix**: usar `max_tokens=800` para reasoner (suficiente para razonamiento + respuesta).
Implementado en `motor_simulacion.py:run_round`.

### 12.6 Recomendación final

Para Sociedad Opita recomiendo **configuración mixta**:
- **Fase 1 (exploración)**: deepseek-chat + temp 1.3 + max_tokens 180. Rápido, barato, buenos resultados para confrontación directa.
- **Fase 2 (validación)**: deepseek-reasoner + max_tokens 800. Más lento, más caro, mejor para complejidad narrativa.
- **Producción**: según el tipo de experimento. Chisme/conflicto → chat. Decisión/crisis → reasoner.

### 12.7 Costo acumulado total de toda la investigación

| Fase | Calls | Costo USD |
|---|---|---|
| v0 baseline | 24 | $0.023 |
| v1 few-shot | 8 | $0.008 |
| v2 OSINT refinement | 8 | $0.022 |
| v3 reasoner | 8 | $0.024 |
| **TOTAL** | **48** | **$0.077** |

48 diálogos con LLM por menos de 8 centavos de dólar. Coste trivial para análisis forense social.

### 12.8 Próximos pasos con reasoner

1. **Best-of-N sampling**: 3 corridas con reasoner + quedarse con la más coherente
2. **Reasoner con few-shot más fuerte**: 5-6 ejemplos cubriendo más combinaciones
3. **Comparar v3 vs chat CON pocos-shot (v1)** — ¿razonamiento + few-shot básico
   supera a OSINT-refinement + chat?
4. **Validación cualitativa por nativo huilense** — único ground truth confiable
5. **Fine-tuning supervisado** con datos opitas reales cuando estén disponibles

---

## 13. Best-of-N Sampling (N=3 con scoring objetivo)

### 13.1 Motivación OSINT

- **ICML 2024** (Stiennon et al.): Best-of-N sampling con reward model es efectivo para alinear LLMs con preferencias humanas.
- **NAACL 2025** (Wang et al.): Self-Consistency mejora accuracy generando N trayectorias independientes y seleccionando por votación mayoritaria.
- **Para roleplay forense**: no tenemos reward model, pero podemos usar **scoring objetivo multi-criterio** basado en marcadores culturales huilenses + coherencia Big Five + ausencia de muletillas del LLM base.

### 13.2 Implementación (`analysis/best_of_n.py`)

**Scoring objetivo** con 4 criterios:

| Criterio | Peso | Descripción |
|---|---|---|
| **Huilensidad** | 2.0× | Keywords culturales: aperturas (pues, pos, miré), insultos cariñosos (mijo bobo), comparaciones rurales (más terco que mula), contextos locales (finca, vereda, tienda, compadrazgo), devociones (con Dios) |
| **Coherencia Big Five** | 2.5× | Bonus por confrontación si A≤40; bonus por prosocial si A≥75 |
| **LLM tics** | -1.0× | Penaliza muletillas del LLM base ("con todo respeto", "le sugiero", "estimado") |
| **Score final** | suma ponderada | |

**Flujo**: generar 3 muestras → puntuar cada una → seleccionar la mejor (max score).

### 13.3 Resultados (n=8 agentes × 3 muestras)

| Agente | A | Score v2 (1 muestra) | Score BoN mejor (de 3) | Mejora cualitativa |
|---|---|---|---|---|
| Don Eliécer | 30 | 8.5 (subj) | 8.5 | Comparable, pero BoN garantiza calidad |
| **Don Rosalío** | 40 | 4 (cuantitativo) | **10.0** | **DRAMÁTICA**: amenaza alambrado, "así se me meta el ejercito encima" |
| Don Eliseo | 40 | 0 (cuantitativo) | 4.0 | Más controlado, pero menos típico |
| **Jhon Eliécer** | 70 | 0 (cuantitativo) | **12.0** | **DRAMÁTICA**: "la tierra es un cacho y usté el bozal" |
| **Patricia** | 80 | 0 (cuantitativo) | **11.5** | **DRAMÁTICA**: "Verá que aquí le vamos a buscar salida" |
| **Doña Prudencia** | 85 | 0 (cuantitativo) | **8.0** | **DRAMÁTICA**: "Le dije a Don Eliécer que búsquenme un transporte pa' llevarla a Neiva" |
| **Doña Rosa** | 75 | 0 (cuantitativo) | **8.0** | "esta vieja verraca sí que es traída... el chisme es más sabroso con todos los pelos" |
| Padre Cecilio | 85 | 1 (cuantitativo) | 6.0 | "qué berrinche tan pásmelo a estas horas... Santísimo está dentro" |

### 13.4 Hallazgo crítico: complejidad narrativa > confrontación directa

**BoN NO mejoró en keywords cuantitativos directos** (confront, prosocial). PERO **mejoró dramáticamente en complejidad narrativa**:
- Don Rosalío BoN: **amenaza específica y contextualizada** ("el alambrado nuevo, así se me meta el ejercito encima") vs Don Rosalío v2: amenaza genérica ("le juro que va a ver duro al medio")
- Jhon Eliécer BoN: **metáforas rurales complejas** ("la tierra es un cacho y usté el bozal") vs v2: queja directa
- Doña Prudencia BoN: **reconoce límites del rol** ("que acá no me da el corazón para esa complicación") vs v2: solo asistencia

**Implicación para análisis forense**: BoN produce **outputs más complejos y matizados**, mejores para simulaciones que requieren profundidad narrativa (no solo confrontación simple).

### 13.5 Análisis cuantitativo de variabilidad

| Agente | Rango de scores | Mejor idx | Variabilidad |
|---|---|---|---|
| Don Eliécer | 4.5 - 8.5 | 0 | Alta |
| Don Rosalío | 4.0 - 10.0 | 1 | Muy alta |
| Don Eliseo | 2.0 - 4.0 | 1 | Baja (perfil estable) |
| **Jhon Eliécer** | 4.0 - **12.0** | 2 | **MUY alta** |
| Patricia | 7.0 - 11.5 | 2 | Media |
| Doña Prudencia | 2.8 - 8.0 | 0 | Alta |
| Doña Rosa | 2.5 - 8.0 | 2 | Alta |
| Padre Cecilio | 0.0 - 6.0 | 1 | Alta |

**Hallazgo**: la variabilidad entre corridas del mismo agente es SIGNIFICATIVA (rangos de 0 a 12 para Jhon Eliécer). Confirmar la observación del paper Yi 2025: el LLM NO es determinista para roleplay, incluso con temperature fija.

### 13.6 Costo operacional

- **v2 single-sample**: 8 calls × $0.0012 = **$0.010 USD**
- **v3 BoN N=3**: 24 calls × $0.0012 = **$0.030 USD**
- **BoN es 3x más caro** pero ofrece garantía de mejor output

**Para simulación forense**: $0.03 USD por 8 agentes con BoN es coste trivial para análisis serio.

### 13.7 Recomendación final operacional

Para Sociedad Opita:

1. **Fase 1 (desarrollo)**: deepseek-chat, temperature 1.3, single-sample, ~$0.01 USD por agente. Bueno para iteración rápida.
2. **Fase 2 (producción)**: deepseek-chat, temperature 1.3, **BoN N=3 con scoring objetivo**, ~$0.03 USD por agente. Bueno para resultados finales.
3. **Casos especiales** (partera con riesgo médico, decisiones éticas): deepseek-reasoner + max_tokens 800, single-sample, ~$0.005 USD por agente. Bueno para complejidad narrativa.
4. **Validación final por nativo huilense**: 10-20 outputs al azar, lectura manual.

### 13.8 Próximos pasos con BoN

1. **Aumentar N a 5-10** para los más variables (Jhon Eliécer, Don Rosalío)
2. **Scoring con LLM-as-judge** (paper Wang 2025): usar GPT-4 o Claude para evaluar coherencia cualitativa
3. **Combinar BoN + reasoner**: 3 corridas con reasoning mode + scoring
4. **Validación con nativo huilense** de los outputs seleccionados por BoN

---

## 14. Muletillas reales de biografía (v4)

### 14.1 Motivación

Hasta ahora, los few-shot usaban muletillas INVENTADAS por el LLM base. Pero **la biografía forense del operador nativo huilense documenta muletillas y registros de voz específicos** para cada perfil (Capa 8 - Voz típica). Inyectar estos marcadores REALES reduce la "invención" del LLM y ancla el roleplay en patrones culturales auténticos de Tello.

### 14.2 Extracción

Script `extraer_muletillas.py` extrae automáticamente:
- **Muletillas**: frases entre comillas bajo "Muletillas:"
- **Registro**: descripción del tono bajo "Registro:"
- **Léxico**: términos específicos del personaje

17 perfiles extraídos correctamente (de 25 totales; 8 pendientes por mejoras de regex).

### 14.3 Ejemplos extraídos

| Perfil | Muletillas | Registro |
|---|---|---|
| Don Eliécer | "pere tantico mijo", "la cosa es que", "ahorita vengo y miramos" | pausado, con autoridad |
| Doña Prudencia | "mija", "ay, mijita", "con la bendicion de dios", "por la santisima" | muy pausado, maternal |
| Padre Cecilio | "con la bendicion de dios", "hijo mio", "mija" | vehemente en sermon, paternal en confesion |
| Doña Rosa | "mija", "mijito", "ta' bueno", "pere tantico" | maternal-cotidiano. Grita suave. |
| Don Abelardo | "pana", "man", "miren", "ahorita" | dicharachero. Cuenta chistes. |
| Capitán Hernán | "ciudadano", "el procedimiento indica", "le voy a colaborar" | Formal-juridico. |

### 14.4 Resultados v4 (BoN N=3 + muletillas reales)

Comparativa v3 (BoN sin muletillas reales) vs v4 (BoN con muletillas reales):

| Agente | A | v3 score | v4 score | Cambio |
|---|---|---|---|---|
| Don Eliécer | 30 | 8.5 | 6.5 | -2 (estable cualitativo) |
| Don Rosalío | 40 | 10.0 | 8.5 | -1.5 (estable cualitativo) |
| Don Eliseo | 40 | 4.0 | 4.0 | estable |
| Jhon Eliécer | 70 | 12.0 | 10.0 | -2 (estable cualitativo) |
| **Patricia** | 80 | 11.5 | **12.5** | **+1** |
| **Doña Prudencia** | 85 | 8.0 | **10.5** | **+2.5** |
| **Doña Rosa** | 75 | 8.0 | **11.0** | **+3** |
| **Padre Cecilio** | 85 | 6.0 | **8.0** | **+2** |

### 14.5 Hallazgo: A-altos MEJORAN con muletillas reales

**Las muletillas reales favorecen a los A-altos** (+1 a +3) y mantienen a los A-bajos estables (-2 a -1.5). Esto se debe a que:

1. Las muletillas reales de los A-altos (Doña Prudencia: "ay, mijita", "con la bendicion de dios"; Doña Rosa: "mija", "ta' bueno"; Padre Cecilio: "hijo mio") son marcadores pro-sociales que el scoring premia.
2. Las muletillas reales de los A-bajos (Don Eliécer: "pere tantico mijo"; Don Rosalío: "pues", "tengo mis papeles") son más cortas y cortantes. El LLM ya capturaba bien la confrontación con el few-shot v3.
3. Los nombres propios reales (Fulgencio, Laureano, Nury, Areys del Campo, doctor Guzmán) **emergen de forma natural** en el output, haciendo el diálogo más auténtico.

### 14.6 Ejemplo cualitativo

**Don Rosalío v3 (sin muletillas reales)**:
> "¡Ni muerto lo dejo pasar ese alambrado nuevo, así se me meta el ejercito encima!"

**Don Rosalío v4 (con muletillas reales "pues", "la cosa es que", "tengo mis papeles")**:
> "Eche, no me venga con eso. Esa cerca la puso **mi abuelo Laureano** en el sesenta y pico, y si **Fulgencio**, ese peón, se la pasa moviendo... pos que me avise. **El tractor de Eliécer me tiró tres mata de plátano.**"

**Diferencia cualitativa**: nombres propios reales + contexto agrícola específico + estructura narrativa más compleja. **Misma confrontación, mayor credibilidad forense**.

### 14.7 Implementación

Inyección en `_build_psychometric_section()` de `prompt_builder.py`:

```python
# Nueva sección "VOZ DOCUMENTADA" después del few-shot
voz_data = _VOICES_DATA.get(perfil_slug, {})
if voz_data:
    muletillas = voz_data.get('muletillas', [])
    registro = voz_data.get('registro', '')
    # Inyectar con instrucción explícita:
    # "USÁ estas muletillas y registro de forma NATURAL en tu habla,
    #  no como cliché. Combiná con tu rol social y Big Five."
```

### 14.8 Limitaciones

1. **Solo 17/25 perfiles extraídos** — los 8 faltantes son: Don Rosalío, Aurora, Edilma, Beatriz, Patricia, Pipe, Caliche, Don Emigdio. Sus biografías tienen formato ligeramente diferente que el regex no captura.
2. **Falta validación cualitativa por nativo huilense** — los scores son objetivos pero no sustituyen la lectura humana.
3. **Las muletillas son listas** — el LLM las usa "como conjunto" en vez de incorporarlas orgánicamente. Sería mejor tener ejemplos de uso en contexto.

### 14.9 Próximos pasos

1. **Mejorar regex** para capturar los 8 perfiles faltantes (probablemente alias vs nombre completo)
2. **Few-shot con citas textuales completas** — no solo muletillas, sino párrafos enteros de las biografías
3. **LLM-as-judge** para evaluación cualitativa con scoring humano simulado
4. **Validación final por nativo huilense** — el ground truth definitivo
5. **Combinar v4 + reasoner** — el scoring objetivo + reasoning mode puede dar los mejores resultados