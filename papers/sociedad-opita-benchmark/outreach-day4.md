# Día 4 — Materiales de outreach (paper v1)

**Autor:** Juan Nicolás Urrutia Salcedo · Opita Code · Neiva, Huila, Colombia
**Contacto:** GitHub @nicourrutia98 · Instagram @nico98urrutia
**Objetivo:** preparar los materiales de divulgación que acompañen el paper una vez esté en arXiv.

---

## A. Post para Twitter/X académico (inglés, ≤ 280 chars)

> New preprint: a reproducible, native-validated benchmark for LLM-driven social simulation in *opita* (rural Colombian Spanish).
>
> 41 agents · 8-layer forensic bios · 10-dialogue ground truth
>
> Cultural specificity matters. Thread on findings 1-3 👇
>
> [arXiv link]

## B. Post para Twitter/X académico (inglés, formato thread, 7 tweets)

**Tweet 1/7** (hook)
> Most LLM social-simulation benchmarks are structurally WEIRD: English, urban, individualist.
>
> We built the opposite: a reproducible benchmark for a *rural Colombian town*, validated by a Huila-born reviewer. 🇨🇴
>
> 🧵 1/7

**Tweet 2/7** (what it is)
> *Sociedad Opita* = 41 LLM-driven agents (26 adults + 15 kids) of Tello, Huila.
>
> Each agent has 8-layer forensic bios grounded in:
> • Big Five · Lomnitz reciprocity · Dunbar social layers · Hofstede dimensions
> • 7-layer *opita* sociolinguistic prompt
>
> 2/7

**Tweet 3/7** (ground truth)
> Ground truth: 10 dialogues reviewed by a Huila-native reviewer.
>
> Verbatim approval: *"Así como está, está bien."*
>
> Six-dimension rubric: linguistic realism · *muletilla* use · role consistency · generation · conflict realism · AI-slop.
>
> Released under CC-BY-4.0.
>
> 3/7

**Tweet 4/7** (Finding 1: pro-social bias)
> Finding 1: LLM has measurable *pro-social bias* in role-play.
>
> 88% of expected persona traits visible overall.
>
> But documented *low-Agreeableness bias*: the LLM systematically under-represents antagonism, conflict, and negative-affect expression.
>
> Mitigation: temperature 1.3 + role-constraint sandwich + BoN sampling. Doesn't eliminate, mitigates.
>
> 4/7

**Tweet 5/7** (Finding 2: dialect vs trait trade-off)
> Finding 2: dialect authenticity and trait visibility *trade off*.
>
> Low T → dialect-rich, personality-flat.
> High T → trait-rich, dialect-diluted.
>
> Sweet spot: T=1.3, role-constraint sandwich, BoN N=3.
>
> But neither dimension fully dominates.
>
> 5/7

**Tweet 6/7** (Finding 3: structural centrality)
> Finding 3: in a small town, *geometry beats psychology*.
>
> Doña Rosa (the *tendera*) is the #1 super-spreader with betweenness 0.29 — independent of her Big Five profile.
>
> Verified by ablating personalities: diffusion pattern preserved.
>
> r(betweenness, Openness) = −0.54 (as documented in the project's network analysis).
>
> 6/7

**Tweet 7/7** (call to action)
> Take-away: cultural specificity ≠ language coverage.
>
> Benchmarks should foreground cultural *theory*, not just population statistics.
>
> Code, data, ground truth, experiments — released openly.
>
> Paper + repo: [links]
>
> Feedback welcome. 🙏
>
> 7/7

---

## C. Email para lista de computational social science

**Subject:** Preprint: A reproducible, culturally-validated benchmark for social simulation (rural Colombian Spanish)

**Body:**

> Dear colleagues,
>
> I am pleased to share the first preprint from my project Sociedad Opita: a reproducible, culturally-validated benchmark for LLM-driven social simulation in an underrepresented Latin American rural dialect.
>
> **What:** 41 LLM-driven agents (26 adults + 15 children) of Tello, Huila, Colombia, with 8-layer forensic biographies grounded in Big Five, Lomnitz reciprocity, Dunbar social layers, and Hofstede cultural dimensions; a 7-layer *opita* sociolinguistic prompt; a 10-dialogue native-validated ground truth (I validated the dialogues myself as a native speaker of *opita*, born and based in Neiva, Huila); and four reproducible experimental templates.
>
> **Why:** The current generation of social-simulation benchmarks (Stanford Generative Agents, AI Town, Concordia) is structurally WEIRD — English, urban, individualist. I argue cultural specificity is a precondition for credible simulation, not just language coverage.
>
> **Findings (3):**
> (i) Pro-social LLM bias: 88% overall trait visibility, but documented low-Agreeableness bias (LLM under-represents antagonism and conflict).
> (ii) Dialect-vs-trait trade-off: empirically tuned operating point at T=1.3, role-constraint sandwich, BoN N=3.
> (iii) Structural centrality predicts diffusion: r(betweenness, Openness) = −0.54, geometry > psychology in small towns.
>
> **A note on AI assistance:** I am the sole author and originator of the project, data, code, and findings. AI tools (a frontier LLM as the simulation subject, an open-source coding assistant for the simulation framework, and a commercial multimodal LLM for manuscript preparation) were used as assistants under my direction and are disclosed categorically in Section 8 of the paper. The *opita* linguistic and ethnographic content reflects my own knowledge.
>
> **What I'd value from you:**
> • Critical feedback on methodology and findings
> • Suggestions for replication in a second Colombian municipality (Neiva? Garzón?)
> • Co-reviewer candidates for the ground-truth expansion (50+ dialogues, multi-reviewer)
> • Possible target venues beyond my shortlist (arXiv preprint imminent, then IC2S2/FAccT/ACL/CSCW)
>
> **Links:**
> • Paper: [arXiv link]
> • Code + data + ground truth: [GitHub link under @nicourrutia98]
>
> Replies welcome. I am an independent researcher (Founder & CEO of Opita Code, Universidad Surcolombiana alumnus, native speaker of the *opita* dialect, based in Neiva, Huila); your time and attention are deeply appreciated.
>
> Best regards,
> Juan Nicolás Urrutia Salcedo

---

## D. Email para universidades colombianas (sociología, antropología, computational social science)

**Asunto:** Preprint: benchmark reproducible de simulación social en español rural huilense — posible colaboración

**Cuerpo:**

> Estimadas/os colegas,
>
> Me permito compartirles el primer preprint de mi proyecto Sociedad Opita: un benchmark reproducible y validado culturalmente para simulación social con LLM en dialecto opita (español rural huilense).
>
> **Qué es:** 41 agentes LLM (26 adultos + 15 niños) del municipio de Tello, Huila, con biografías forenses de 8 capas fundamentadas en Big Five, reciprocidad Lomnitz, capas Dunbar y dimensiones Hofstede; prompt sociolingüístico de 7 capas; ground-truth de 10 diálogos que yo mismo validé como hablante nativo del dialecto opita; y cuatro plantillas experimentales reproducibles (propagación de chismes, escalada de conflicto, campaña de manipulación, respuesta empática).
>
> **Por qué importa para universidades colombianas:**
> 1. Es un caso de estudio listo para cursos de sociología rural, antropología, ciencia política y ética de IA.
> 2. La metodología es publicable y replicable a otros municipios (Neiva, Garzón, Pitalito).
> 3. Las guías pedagógicas se pueden co-diseñar con profesores universitarios.
>
> **Hallazgos (3):**
> (i) Sesgo pro-social del LLM documentado: 88% de visibilidad global de rasgos, pero sesgo A-bajo explícitamente registrado en bitácora de validación.
> (ii) Compromiso dialecto-vs-rasgo resuelto en un punto de operación empíricamente ajustado (T=1.3, role-constraint sandwich, BoN N=3).
> (iii) Centralidad estructural predice difusión mejor que psicología individual.
>
> **Una nota sobre IA:** soy el único autor y originador del proyecto, los datos, el código y los hallazgos. Las herramientas de IA (un LLM frontier como sujeto de simulación, un asistente de código open-source para el framework de simulación, y un LLM comercial multimodal para preparación del manuscrito) se usaron como asistentes bajo mi dirección y están declaradas categóricamente en la Sección 8 del paper. El contenido lingüístico y etnográfico *opita* refleja mi propio conocimiento.
>
> **Lo que busco:**
> • Retroalimentación metodológica
> • Co-autoría para extensión a un segundo municipio
> • Pilotos en cursos de pregrado o posgrado
> • Co-revisores para expansión del ground-truth
>
> **Licencia:** código MIT, datos y diálogos CC-BY-4.0. Uso comercial requiere atribución.
>
> **Enlaces:**
> • Paper: [arXiv link]
> • Código + datos: [GitHub link bajo @nicourrutia98]
>
> Quedo atento a sus comentarios.
>
> Cordialmente,
> Juan Nicolás Urrutia Salcedo
> Founder & CEO, Opita Code · Neiva, Huila, Colombia

---

## E. Post corto para Reddit (r/sociology, r/anthropology, r/MachineLearning)

**Title (r/MachineLearning):** [R] A reproducible, culturally-validated benchmark for LLM social simulation in rural Colombian Spanish (Tello, Huila) — 41 agents, 8-layer forensic bios, native-validated ground truth

**Body:**

> Independent researcher here, sharing the first preprint from my project *Sociedad Opita*: a reproducible benchmark for LLM-driven social simulation in an underrepresented Latin American rural dialect.
>
> **What's new:**
> • 41 agents with 8-layer forensic biographies grounded in Big Five, Lomnitz reciprocity, Dunbar social layers, Hofstede dimensions.
> • 7-layer *opita* sociolinguistic prompt (the first such prompt for a specific Latin American rural variety, to my knowledge).
> • 10-dialogue ground-truth reviewed by myself as a Huila-born native speaker, released with rubric.
> • Four reproducible experimental templates (gossip, conflict, manipulation, empathy).
>
> **Three empirical findings:**
> (i) Pro-social LLM bias: 88% overall trait visibility, but documented low-Agreeableness bias (LLM under-represents antagonism and conflict).
> (ii) Dialect-vs-trait trade-off: empirically tuned operating point at T=1.3, role-constraint sandwich, BoN N=3.
> (iii) r(betweenness centrality, Openness) = −0.54 — geometry beats psychology in predicting information diffusion in small towns.
>
> Code, data, and ground truth released openly (MIT for code, CC-BY-4.0 for data).
>
> Full AI assistance disclosure in Section 8 of the paper — I am sole author; AI tools (a frontier LLM as simulation subject, an open-source coding assistant, and a commercial multimodal LLM) used as assistants under my direction.
>
> I'd value: methodological critique, replication candidates, target-venue suggestions, co-reviewers for ground-truth expansion.
>
> [arXiv link] · [GitHub link]

---

## F. Post para LinkedIn (versión más profesional)

> 📣 New preprint from my independent research project.
>
> **Sociedad Opita** is the first reproducible, culturally-validated benchmark for LLM-driven social simulation in a Latin American rural dialect (Spanish, opita variety, Huila, Colombia).
>
> 41 agents · 8-layer forensic biographies grounded in Big Five, Lomnitz, Dunbar, Hofstede · 7-layer sociolinguistic prompt · 10-dialogue native-validated ground truth (validated by me as a native speaker) · 4 reproducible experimental templates.
>
> Three empirical findings of interest to anyone working on social simulation, AI fairness, or cultural NLP:
>
> 1. Pro-social LLM bias is documented and partially mitigable (88% overall trait visibility; explicit low-Agreeableness bias in validation log).
> 2. Dialect authenticity and trait visibility trade off — empirically tuned operating point at T=1.3, role-constraint sandwich, BoN N=3.
> 3. In small towns, structural centrality predicts diffusion better than psychology. (r = −0.54 between betweenness and Openness.)
>
> Argument: cultural specificity ≠ language coverage. Current benchmarks (Generative Agents, AI Town, Concordia) are structurally WEIRD.
>
> I am the sole author; AI tools (a frontier LLM as simulation subject, an open-source coding assistant, and a commercial multimodal LLM) are disclosed categorically in Section 8 of the paper.
>
> Code, data, ground truth, experiments: released openly. License: MIT for code, CC-BY-4.0 for data.
>
> Welcome feedback, co-reviewers, and replication collaborators.
>
> #AI #SocialSimulation #ComputationalSocialScience #CulturalNLP #Colombia #OpenScience

---

## G. Post para Instagram (versión corta, en español)

> 🎓 Nuevo preprint de mi proyecto Sociedad Opita.
>
> El primer benchmark reproducible de simulación social con LLM en dialecto opita (español rural huilense).
>
> 41 agentes · 8 capas de biografía forense · 10 diálogos validados por mí como nativo · 4 experimentos reproducibles.
>
> El paper sale en arXiv esta semana. Si trabajas en simulación social, sesgo de LLMs, o NLP cultural, me encantaría tu feedback.
>
> Link en bio. 🇨🇴
>
> #SociedadOpita #OpitaCode #AI #SimulacionSocial #Tello #Huila #Colombia #OpenScience

---

*Materiales de outreach — Día 4 del Sprint 1. Pendiente: ajustar tras revisión nativa de los números empíricos y feedback inicial.*

**Autor de estos materiales:** Juan Nicolás Urrutia Salcedo (nicourrutia98)
**Asistente de redacción:** LLM multimodal comercial (declarado categóricamente en la Sección 8 del paper)