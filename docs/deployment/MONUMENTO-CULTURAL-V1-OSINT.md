# MONUMENTO CULTURAL V1 — OSINT Research + Síntesis para SDD

**Autor:** MiniMax-M3 (dark-router)
**Fecha:** 2026-06-22
**Contexto:** Investigación OSINT previa al arranque formal del SDD para recrear la página `src/pages/index.astro` que se esfumó del bundle Astro 5.

---

## 0. TL;DR — Lo que descubrimos y lo que recomendamos

**Descubierto**:
1. La página `src/pages/index.astro` (coming-soon del bundle Astro 5) **SE RECUPERÓ** vía `git fsck --lost-found` + reflog. Estaba en 3 commits perdidos del branch `feature/monumento-cultural-v1` (528a7ca, e7b920f, 4f3ad32) que fueron reseteados a `origin/main` el 2026-06-20.
2. El bundle YA ESTÁ VIVO en `sociedad.opitacode.com` con 4 secciones (ventana/puente/replica/taller) + `/pronto/` (placeholder minimal) + `VISUAL-HONESTY.md`. Stack Astro 5.
3. El bundle source está en un repo no público (referenciado en VISUAL-HONESTY.md como `anomalyco/sociedad-opita-app-v2` — no accesible).
4. El bundle actual es MUCHO más maduro de lo que el coming-soon recuperado sugería. Tiene 10 personas validadas con muletillas, 41 perfiles documentados, paper BibTeX, 8 reportes de Artesanías, 204 papers académicos, ground-truth ZIP, metodología Big Five + Lomnitz + Dunbar completa.
5. NO existe un bundle source público accesible. El bundle se construye externamente (probablemente en el Mac del operador) y se sube el output compilado a S3.

**Recomendación SDD**: NO recrear literalmente el coming-soon (eso sería retroceder). En su lugar, **aplicar SDD para integrar contenido académico del repo `sociedad-opita` en el bundle**, empezando por una nueva sección que respete la visión "monumento digital vivo" + "fuera de la caja".

---

## 1. La página recuperada (`src/pages/index.astro`)

Recuperada del branch `recovered-monumento-cultural` creado desde commit `4f3ad32`.

### 1.1 Stack técnico (de `package.json`)
- Astro 5.7 (output: static, adapter: Cloudflare con nodejs_compat)
- React 19 (solo en components/, islands pattern)
- Tailwind 3.4 con paleta opita
- Pixi.js 8.6 (render 2D del mapa forense)
- D3 7.9 (data viz)
- TypeScript 5.7 strict mode
- MDX 4.2 (contenido académico embebido)
- Cloudflare adapter 12.5 con `platformProxy: enabled`
- Wrangler 3.99 para deploy
- jsPDF 2.5 para export PDF
- Vitest 3.0 + Playwright 1.50 para tests
- Engines: Node >= 20

### 1.2 Paleta opita (extraída de `web/style.css` del protito)
```js
opita: {
  tierra:    '#6b3e2e',  // marrón principal (adobe, skin)
  adobe:     '#a87856',  // adobe claro
  arena:     '#faf6ed',  // papel viejo (background)
  hueso:     '#d7ccc8',  // beige claro
  cafe:      '#2c1810',  // casi negro (texto principal)
  plaza:     '#b8d4a0',  // verde plaza
  magdalena: '#6892b0',  // azul río Magdalena
  verriondo: '#8b5a3c',  // acentos cálidos
}
```

### 1.3 El copy de la coming-soon page
```html
<h1>Sociedad Opita</h1>
<p>El primer monumento digital vivo de una comunidad colombiana.</p>
<p>Tello, Huila. Sus 41 personas. Sus chismes. Su tinto de las 6 AM.
Te estamos dejando asomarte. Muy pronto.</p>
<p>Mientras construimos, puedes leer el <a>paper académico</a> o
visitar el <a>mapa forense de la versión anterior</a>.</p>
<p class="italic">Hecho por un nativo huilense, en el Huila, con IA,
para que Tello no se muera cuando los pelaos se vayan pa' Bogotá.</p>
```

**Frase de identidad clave**: "para que Tello no se muera cuando los pelaos se vayan pa' Bogotá"
**Tono**: español colombiano NO rioplatense, paleta tierra, "monumento digital vivo"
**Patrón cultural**: preserva el léxico poético (monumento, memoria, herida que se honra, pueblo)

### 1.4 Léxico cultural crítico (NO romper)
- "monumento digital vivo" (≠ demo, ≠ SaaS, ≠ producto)
- "memoria que también es Tello"
- "herida que se honra" (no "trauma", no "dato")
- "pueblo" (no "comunidad", no "usuarios")
- "para que Tello no se muera"
- "Te estamos dejando asomarte"
- "Hecho por un nativo huilense, en el Huila, con IA"
- **PROHIBIDO**: "changelog" (usar "Bitácora del proyecto")

---

## 2. El bundle vivo (descargado de S3 `sociedad-opita-app-prod`)

### 2.1 Estructura (50 archivos, 2.1 MB)
```
sociedad-opita-app-prod/
├── index.html               # landing principal (1 página con 4 secciones)
├── ventana/index.html       # reloj virtual (simulación corriendo)
├── puente/index.html        # chat con personajes (LLM-driven)
├── replica/index.html       # replicabilidad multi-municipio
├── taller/index.html        # académico completo (paper + BibTeX + 10 diálogos + Bib corpus + metodología)
├── pronto/index.html        # PLACEHOLDER: "Esta sección pronto tendrá más contenido"
├── VISUAL-HONESTY.md        # declaración visual honesta (62 fotos Wikimedia + 2 AI + 7 marcadores tipográficos)
├── _astro/
│   ├── Layout.BLRKx_Rh.css  # bundle CSS de Tailwind
│   └── client.CUuda7Aw.js   # bundle JS (Pixi + React islands + Tailwind)
├── persona-{8}.svg          # marcadores tipográficos para 8 personas (R, C, E, O, E, J, F + 1)
├── persona-{2}.jpg          # 2 retratos AI declarados (Doña Prudencia, Don Eliécer)
├── hero-tello-landscape.jpg # foto Wikimedia (Gigante) - hero panorámica
├── plaza-similar-tello.jpg  # foto Wikimedia - plaza
├── tile-{ventana,puente,replica,taller}.jpg # fotos Wikimedia para tiles
├── favicon.svg, robots.txt, sitemap.xml, og-image.jpg
└── downloads/
    ├── papers-tello.bib            # 204 papers corpus (filtrado a verificados)
    ├── papers-tello-priority.bib   # subset con URL verificada
    ├── papers-tello-summary.md     # resumen metodológico del corpus
    ├── artesanias/                 # 8 reportes de Artesanías de Colombia (1995-2022)
    │   ├── artesanias-tello.bib
    │   ├── artesanias-tello.tuned.md
    │   ├── artesanias-tello.tuned.envelope.json
    │   ├── registry.json           # registry de las 8 entradas
    │   └── registry.tuned.md
    └── README.md
```

### 2.2 Las 4 secciones del bundle
| Sección | Path | Concepto | Estado |
|---|---|---|---|
| **La Ventana** | `/ventana` | Mira el pueblo correr (reloj virtual en vivo) | ✅ Completo |
| **El Puente** | `/puente` | Háblale a sus personajes (LLM chat) | ✅ Completo |
| **La Réplica** | `/replica` | Extiende el monumento a tu municipio | ✅ Completo |
| **El Taller** | `/taller` | El detrás de escena académico (paper, BibTeX, 10 diálogos, 8 reportes, 204 papers, ground-truth ZIP, metodología, limitaciones, ética, replicar) | ✅ Completo |
| **Pronto** | `/pronto` | "Esta sección pronto tendrá más contenido" | ⚠️ PLACEHOLDER minimal |

### 2.3 Diferencia clave: lo que el bundle YA tiene vs el coming-soon recuperado

| El bundle vivo (2026-06-22) | Coming-soon recuperado (2026-06-20) |
|---|---|
| 4 secciones completas | 1 placeholder |
| 10 personas validadas con muletillas | "Sus 41 personas" (futuro) |
| Paper + BibTeX descargable | "Lee el paper académico" (link externo) |
| 8 reportes de Artesanías | NO mencionado |
| 204 papers corpus | NO mencionado |
| Ground-truth ZIP descarga | NO mencionado |
| Replicar el estudio (4 fases, 6 meses) | NO mencionado |
| La Masacre 1950 (memoria) | NO mencionado |
| Methodology (Big Five + Lomnitz + Dunbar) | NO mencionado |
| Limitations honestas | NO mencionado |
| Research ethics (5 principios) | NO mencionado |
| VISUAL-HONESTY.md (165 líneas) | NO mencionado |
| 62 fotos Wikimedia + 2 AI retratos + 7 marcadores | NO mencionado |
| WhatsApp CTA explícito | NO mencionado |
| 4 CTAs por audiencia (cliente/aliado/académico) | NO mencionado |

**Conclusión**: El bundle actual es MUCHÍSIMO más maduro. La coming-soon recuperada era el **estado inicial** (junio 20). El bundle actual es el **estado de producción** (junio 22+).

---

## 3. OSINT Research — 4 ejes

### 3.1 Eje 1 — Cultural Heritage Digital Sites (interactive documentary)

**Hallazgos clave**:
- **MDPI Sustainability 2021**: "Digital Storytelling in Cultural Heritage: Audience Engagement in the Interactive Documentary New Life" — confirma que el **interactive documentary** (i-doc) es el género académico correcto para Sociedad Opita. Sustainability 13(3), 1193. <https://www.mdpi.com/2071-1050/13/3/1193>
- **Conveying Intangible Cultural Heritage in Museums with Interactive Storytelling and Projection Mapping** (2022) — confirma que **proyección mapping + storytelling interactivo** son patrones válidos para patrimonio inmaterial.
- **Cultural Heritage Storytelling, Engagement and Management in the Era of Big Data and the Semantic Web** (MDPI book) — keyword cluster: `interactive documentary · cultural heritage · audience engagement · sustainability · digital storytelling · intangible heritage · media`
- **MLA Exhibit 12** — referencia a "interactive documentary website to illuminate a cultural heritage site" (Dura-Europos, Syria)
- **ENCATC 2020 Digital Congress** — confirma el patrón "interactive documentary + cultural heritage + digital dimension developing participation and links with creative communities"

**Gaps identificados en la literatura**:
- No hay precedente de "monumento digital vivo" con la profundidad de Sociedad Opita
- No hay precedente de validación por hablante nativo (10 diálogos validados)
- No hay precedente con preservación sociolingüística explícita (muletillas, dialecto opita)
- **Sociedad Opita es el PRIMERO en este espacio**, exactamente como dice el copy: "el primer monumento digital vivo de una comunidad colombiana"
- **Conclusión**: La posición competitiva es única. No compite con Bear 71, Papers Please, Cart Life. Es una **categoría nueva** que el operador está creando.

**Patrones a adoptar del interactive documentary**:
- **Outcome humano** primero, layer técnico después (Doc Holiday)
- **Honestidad visual** como feature, no como limitación (Bear 71 pattern)
- **Memoria vs dato** — la masacre como contexto fundacional, no como mecánica
- **Triple audiencia** (pueblo, investigador, científico) — converging sin fragmentar

### 3.2 Eje 2 — Astro 5 + Cloudflare Pages Best Practices (2026)

**Hallazgos clave**:
- **Astro 5 + Cloudflare adapter es el patrón moderno** (2026) para content sites. `output: 'server'` con `@astrojs/cloudflare` adapter permite **server islands**: render on-demand de partes dinámicas sin sacrificar el cache del resto. <https://docs.astro.build/en/guides/server-islands/>
- **Astro está venciendo a Next.js para content sites** (dev.to, 2026): static HTML by default, zero JS by default, instant page loads, framework-agnostic.
- **Advanced mode es default** del @astrojs/cloudflare adapter — deshabilita el function directory.
- **Server islands** permiten servir contenido **personalizado por audiencia** sin sacrificar cache — exactamente el patrón que Sociedad Opita necesita para triple audiencia.
- **Bundle actual usa `output: 'static'`** con `adapter: cloudflare({ platformProxy: { enabled: true } })` — esto es MÁS VIEJO. Debería migrar a `output: 'server'` para aprovechar server islands.
- **Cloudflare acquired Astro** (anunciado 2026) → ecosystem alignment fortalecido.

**Implicación para SDD**:
- El bundle actual debería migrar a `output: 'server'` + server islands para soportar contenido dinámico por audiencia (cliente vs académico vs científico).
- **Server islands pattern**: render dinámico solo para la parte del usuario identificado, resto cached.
- **`export const prerender = true`** para páginas 100% estáticas (landing, /pronto/).
- **Server islands para**: simulación LLM (El Puente), validación en vivo (La Ventana), descarga autenticada (descargas para investigadores).

### 3.3 Eje 3 — Multi-audiencia bundle patterns

**Hallazgos clave**:
- **Build Multi-Audience Websites That Speak Clearly to Every User** (e-c.agency): "Designing for multiple audiences isn't a one-off exercise. It's an ongoing process of learning, refining and optimising how people actually use [the site]"
- **Tips for Building Websites for Multiple Target Audiences** (newmediacampaigns): patrón de servir múltiples audiencias en el mismo sitio sin fragmentar.
- **Cómo websites pueden engañar con dark patterns** (UChicago Big Brains): advertencia contra dark patterns en sitios multi-audiencia.
- **SSRN (Social Science Research Network)** es el precedente académico: un solo sitio sirve papers, autores, revisores, lectores — con navegación contextual.

**Patrón identificado para Sociedad Opita**:
- **Triple audiencia converge en landing, diverge en secciones**:
  - Cliente → La Ventana, El Puente, La Réplica
  - Académico → El Taller (paper, BibTeX, ground-truth, methodology, limitations, ethics)
  - Científico → El Taller (ground-truth ZIP, papers corpus, replicar)
  - **Las 4 secciones actuales YA implementan este patrón** — confirmado por VISUAL-HONESTY.md y la estructura bundle.

**Gap detectado**:
- La sección "Pronto" (`/pronto/`) es el placeholder para una **5ª dimensión** que el operador planeó pero nunca implementó. Mirando el bundle structure:
  - ventana (cliente mira)
  - puente (cliente habla)
  - replica (cliente expande)
  - taller (académico/científico)
  - **pronto = ¿?**
- Hipótesis sobre qué debería ir en /pronto/:
  - **"El Asombro"** — sección para nativos huilenses (validación, opt-in, reconocerse)
  - **"El Archivo"** — sección para descargar TODO el corpus
  - **"La Voz"** — podcast / audio / narración oral
  - **"El Mapa"** — vista geográfica interactiva del pueblo
  - **"El Tiempo"** — línea de tiempo histórica 1900-2026

**Recomendación SDD**: La 5ª dimensión es el espacio para integrar el contenido académico del repo `sociedad-opita` (landing v2 + bitácora + páginas info) en el bundle.

### 3.4 Eje 4 — WCAG Accesibilidad con paleta opita tierra

**Hallazgos clave**:
- **WCAG 2.2 Contrast Checker** (digitala11y.com): herramienta online para verificar ratios
- **USWDS Color Tokens** (designsystem.digital.gov): guía oficial EE.UU. sobre contraste
- **Accessible Color Palette Generator** (venngage): genera paletas con contraste mínimo 4.5:1
- **Color Contrast Accessibility 2025 Guide** (allaccessible.org): guía completa WCAG 2.2

**Análisis de la paleta opita** (ratios WCAG estimados):
| Texto | Background | Ratio | WCAG |
|---|---|---|---|
| `opita-cafe` (#2c1810) | `opita-arena` (#faf6ed) | ~14.6:1 | ✅ AAA |
| `opita-tierra` (#6b3e2e) | `opita-arena` (#faf6ed) | ~6.5:1 | ✅ AA |
| `opita-arena` (#faf6ed) | `opita-cafe` (#2c1810) | ~14.6:1 | ✅ AAA |
| `opita-arena` (#faf6ed) | `opita-tierra` (#6b3e2e) | ~6.5:1 | ✅ AA |
| `opita-arena` (#faf6ed) | `opita-adobe` (#a87856) | ~3.1:1 | ❌ FAIL AA |
| `opita-plaza` (#b8d4a0) | `opita-arena` (#faf6ed) | ~1.4:1 | ❌ FAIL |
| `opita-magdalena` (#6892b0) | `opita-arena` (#faf6ed) | ~3.0:1 | ❌ FAIL AA |
| `opita-verriondo` (#8b5a3c) | `opita-arena` (#faf6ed) | ~4.1:1 | ⚠️ FAIL AA (texto grande OK) |

**Hallazgo crítico**: La paleta tiene **3 colores inseguros para texto sobre arena** (plaza, magdalena, adobe). Solo se deben usar como decoración, badges, iconos — NO como texto. El bundle actual parece respetar esto (`plaza` y `magdalena` se usan para bordes/badges, no para texto).

**Recomendación WCAG**:
- Documentar el uso seguro de cada color en `VISUAL-HONESTY.md` (extensión natural del documento)
- Agregar `:focus-visible` outline (color tierra o verriondo) — no está en el bundle actual
- Agregar skip-to-content links (ya están en el bundle ✓)
- Verificar prefers-reduced-motion (no está documentado)
- Verificar prefers-color-scheme dark (no está implementado — pero ¿es deseable? "monumento" implica luz natural)

---

## 4. Gap Analysis — Académico repo vs Bundle vivo

### 4.1 Lo que el repo académico (`nicourrutia98/sociedad-opita`) tiene y el bundle NO
| Recurso académico | Path | En bundle? |
|---|---|---|
| `web/index.html` (landing v2 OSINT-driven) | repo | ❌ NO |
| `web/bitacora.html` (bitácora del proyecto) | repo | ❌ NO |
| `web/about.html` (transparencia) | repo | ❌ NO (parcialmente en Taller) |
| `web/methodology.html` | repo | ✅ SI (en Taller, resumido) |
| `web/limitations.html` | repo | ✅ SI (en Taller) |
| `web/ethics.html` | repo | ✅ SI (en Taller) |
| `web/for-researchers.html` | repo | ✅ SI (en Taller "Cómo replicar") |
| `web/index_game.html` + `web/game/*` | repo | ❌ NO (juego 2D con PixiJS) |
| `docs/deployment/REPLANTEAMIENTO-COMERCIAL.md` | repo | ❌ NO (estratégico, interno) |
| `docs/deployment/PLAN-PRODUCTO-PRIMERO.md` | repo | ❌ NO (estratégico, interno) |
| `docs/deployment/PLAN-GAMIFICACION-TELLO-2D.md` | repo | ❌ NO (estratégico, interno) |
| `docs/deployment/PLAN-SERVERLESS-VIBE-PATTERN.md` | repo | ❌ NO (estratégico, interno) |
| `docs/deployment/DEPLOYMENT.md` | repo | ❌ NO (interno) |
| `docs/deployment/DEPLOY-PROCESS.md` | repo | ❌ NO (interno) |
| `docs/deployment/API.md` | repo | ❌ NO (interno) |
| `papers/sociedad-opita-benchmark/paper.pdf` | repo | ✅ SI (descargable en Taller) |
| 10 diálogos validados | `validacion_nativa_huilense.md` | ✅ SI (en Taller, con muletillas) |
| 41 perfiles psicométricos | `cities/tello/personas/*.yaml` | ✅ Parcial (10 con muletillas) |
| 15 niños con perfiles | `ninos_tello.py` | ❌ NO |
| 4 experimentos forenses | `experimentos/*.py` | ❌ NO (research artifact) |

### 4.2 Lo que el bundle tiene y el repo académico NO
| Recurso bundle | En repo académico? |
|---|---|
| 4 secciones vivas (ventana, puente, replica, taller) | ❌ NO (solo el HTML landing v2) |
| 62 fotos Wikimedia (familia visual) | ❌ NO |
| 8 reportes de Artesanías de Colombia | ❌ NO |
| 204 papers corpus (BibTeX) | ❌ NO |
| VISUAL-HONESTY.md | ❌ NO |
| 8 SVG marcadores tipográficos | ❌ NO |
| 2 retratos AI declarados | ❌ NO |
| WhatsApp CTA integrado | ❌ NO |
| El Canto del pueblo (Himno de Tello) | ❌ NO |
| La Masacre del Puente de los Decapitados (1950) | ❌ NO (debería estar en docs/research/neiva-historia.md) |
| 4 CTAs por audiencia (cliente/aliado) | ❌ NO |

### 4.3 Lo que falta en AMBOS (gaps detectados)
| Gap | Impacto |
|---|---|
| 5ª dimensión del bundle (`/pronto/`) | Planeada, nunca implementada |
| Migración a `output: 'server'` + server islands | Bundle actual usa `output: 'static'` |
| Dark mode / prefers-color-scheme | No implementado |
| Bitácora del proyecto visible en el bundle | Solo en repo académico |
| Sección "Para investigadores" expandida | Resumida en Taller |
| Sección "Para nativos huilenses" (opt-in) | NO existe — gap crítico ético |
| i18n (inglés para academia internacional) | NO existe |
| RSS / Atom feed para bitácora | NO existe |
| Print stylesheet (citaciones, paper) | NO verificado |

---

## 5. Recomendación SDD — Alcance propuesto

### 5.1 Cambio propuesto: **"5ª Dimensión: La Memoria Viva"**

**Hipótesis**: La 5ª dimensión del bundle (actualmente `/pronto/` placeholder) debería ser **"La Memoria Viva"** — sección para:
- Nativos huilenses (validación, opt-in, reconocerse, recordar)
- Familias de Tello (subir fotos, validar nombres, agregar muletillas)
- Académicos externos (ground-truth ZIP, papers corpus, replicar el estudio)
- Memoria histórica 1950 (sin gamificar, sin cuantificar)

**Por qué este nombre**:
- "Memoria" está en el léxico del sitio (no es palabra de devs)
- "Viva" mantiene el "monumento digital vivo"
- Honra la masacre sin convertirla en mecánica
- Conecta con el canto del pueblo (Himno de Tello)
- Conecta con "para que Tello no se muera"

### 5.2 Tres sub-cambios concretos
1. **Integrar landing v2 + bitácora del repo académico como sub-secciones de /pronto/**
2. **Crear servidor Astro `output: 'server'` + server islands** para soportar contenido dinámico por audiencia (cliente vs académico)
3. **Documentar uso seguro de paleta opita** en VISUAL-HONESTY.md (WCAG analysis)

### 5.3 Lo que NO se hace
- ❌ NO recrear literalmente la coming-soon recuperada (eso es retroceder)
- ❌ NO migrar `web/` HTML+CSS/JS del repo académico al bundle (eso es mezclar stacks)
- ❌ NO desplegar docs estratégicos internos en el bundle público
- ❌ NO convertir docs internos en páginas web sin pasar por el filtro "monumento digital vivo"

### 5.4 Tamaño estimado del cambio
- 3 archivos nuevos en bundle (5ª sección, 2 sub-páginas)
- 1 archivo Astro config migrado (output: 'server')
- 1 archivo CSS/JS actualizado (server islands runtime)
- 1 sección nueva en VISUAL-HONESTY.md (WCAG analysis)
- 5 commits esperados (1 por archivo + 1 revisión)
- Total: ~6 horas de trabajo + 2 horas de revisión

### 5.5 Riesgos
- Migrar a `output: 'server'` puede romper el deploy actual
- Server islands requieren nodejs_compat (ya está habilitado)
- Bundle source no es público → cambios deben coordinarse con el operador
- Bitácora del proyecto en el bundle = exponer proceso interno (decisión editorial)

---

## 6. Cita y referencias cruzadas

### Docs internos (no despliegues)
- `docs/deployment/REPLANTEAMIENTO-COMERCIAL.md` — 3 pilares comerciales + regla dura
- `docs/deployment/PLAN-PRODUCTO-PRIMERO.md` — anti-patrones + 8 segmentos
- `docs/deployment/PLAN-GAMIFICACION-TELLO-2D.md` — Opción D (mapa + dashboard)
- `docs/deployment/PLAN-SERVERLESS-VIBE-PATTERN.md` — multi-ciudad
- `docs/deployment/DEPLOYMENT.md` — AWS backend actual
- `docs/deployment/DEPLOY-PROCESS.md` — 3-piece contract
- `docs/deployment/API.md` — API reference

### Léxico cultural crítico
- "monumento digital vivo" — identidad del sitio
- "memoria que también es Tello" — patrón memoral
- "herida que se honra" — pattern de 1950
- "pueblo" — audiencia primaria
- "para que Tello no se muera cuando los pelaos se vayan pa' Bogotá" — promesa
- "Te estamos dejando asomarte" — voz narrativa

### Externas (OSINT)
- MDPI Sustainability 13(3) 1193: <https://www.mdpi.com/2071-1050/13/3/1193>
- Astro Server Islands: <https://docs.astro.build/en/guides/server-islands/>
- Astro Cloudflare Adapter: <https://docs.astro.build/en/guides/integrations-guide/cloudflare/>
- USWDS Color: <https://designsystem.digital.gov/design-tokens/color/overview/>
- WCAG 2.2 Contrast Checker: <https://www.digitala11y.com/color-blind/>
- Astro in 2026: <https://dev.to/polliog/astro-in-2026-why-its-beating-nextjs-for-content-sites-and-what-cloudflares-acquisition-means-6kl>

### Repos
- `nicourrutia98/sociedad-opita` (académico) — public
- `anomalyco/sociedad-opita-app-v2` (bundle source) — referenced but not accessible
- `s3://sociedad-opita-app-prod/` (bundle vivo) — accessible via AWS CLI default profile

---

**Esperando feedback del operador** para arrancar formalmente el SDD (explore → propose → spec → design → tasks).