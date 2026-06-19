# Reviewer Invitation Texts — Sociedad Opita

> Templates listos para copiar y enviar. Cada uno incluye PDF adjunto + invitación al repo GitHub.
> URL del repo: **https://github.com/nicourrutia98/sociedad-opita** ✅ (público)
> Reemplazá `https://github.com/nicourrutia98/sociedad-opita` con la URL real en cada template antes de enviar.

---

## 1. EMAIL CORTO (para colegas cercanos / Slack DM) — ESPAÑOL

```
Asunto: ¿Me ayudás a revisar un preprint? (Sociedad Opita, simulación social con LLM en opita)

Hola [nombre],

Te adjunto el primer preprint de mi proyecto Sociedad Opita: un
benchmark reproducible y validado culturalmente para simulación social
con LLM en dialecto opita (español rural huilense).

Resumen rápido:
• 41 agentes LLM del municipio de Tello, Huila
• Biografías forenses de 8 capas + psicometría Big Five/Lomnitz/Dunbar/Hofstede
• Prompt sociolingüístico de 7 capas (opita)
• Ground-truth de 10 diálogos validados por mí como hablante nativo
• 4 plantillas experimentales reproducibles (gossip, conflicto, manipulación, empatía)
• 3 hallazgos empíricos: sesgo pro-social, trade-off dialecto-vs-rasgo, centralidad estructural

Adjunto: paper.pdf (10 pp)
Repo con código + data + ground-truth: https://github.com/nicourrutia98/sociedad-opita
Licencia: MIT (código) + CC-BY-4.0 (data)

Si tenés 30-45 minutos para leerlo y mandarme feedback antes de
submit a arXiv (objetivo: esta semana), te lo agradezco mucho.
Especialmente me interesa tu lectura sobre:
• Validez ecológica del ground-truth
• Robustez metodológica del best-of-N sampling
• Framing de las implicaciones para AI fairness

Si no podés en este momento, también me sirve un "no puedo ahora"
para saber a quién no molestar la próxima vez.

Gracias!
Juan
```

---

## 2. EMAIL MEDIANO (cold outreach a investigador afín) — ESPAÑOL

```
Asunto: Preprint solicitud de feedback — Sociedad Opita (LLM simulation, opita dialect, Colombia)

Estimado/a Dr./Dra. [Apellido],

Le escribo porque su trabajo en [tema específico suyo — simulación
social / cultural NLP / AI fairness / sociolingüística computacional]
es directamente afín a mi preprint adjunto, y me gustaría mucho
contar con su lectura crítica antes del submission a arXiv.

Soy Juan Nicolás Urrutia Salcedo, investigador independiente basado
en Neiva, Huila (Colombia), nativo del dialecto opita y autor único
del trabajo adjunto. El paper presenta Sociedad Opita, el primer
benchmark reproducible y culturalmente validado para simulación
social con LLM en una variedad rural del español latinoamericano
(Tello, Huila — 41 agentes, 8-layer forensic biographies, 7-layer
sociolinguistic prompt, 10-dialogue native-validated ground truth).

Tres hallazgos que pueden ser de su interés:
1. Sesgo pro-social medible en role-play con LLM (88% rasgos
   visibles globales, pero A-bajo sistemáticamente subrepresentado)
2. Trade-off empírico entre autenticidad dialectal y visibilidad de
   rasgos — resoluble con role-constraint sandwich + best-of-N
3. r = -0.54 entre betweenness centrality y Openness — la geometría
   predice super-spreaders más que la psicología

Adjunto el manuscrito (paper.pdf, ~10 páginas).
Código, datos, ground-truth y bitácoras experimentales están en
https://github.com/nicourrutia98/sociedad-opita bajo licencia MIT (código) y CC-BY-4.0 (datos).

Si pudiera leerlo y enviarme comentarios antes del [fecha tentativa,
ej. 2026-07-05], sería invaluable. Estoy particularmente
interesado en su perspectiva sobre [tema afín suyo].

Quedo atento a su respuesta, sea positiva o negativa — y si puede
recomendarme otro colega afín al tema, también lo agradezco.

Cordialmente,
Juan Nicolás Urrutia Salcedo
Founder & CEO, Opita Code · Neiva, Huila, Colombia
nicourrutia98 · @nico98urrutia
```

---

## 3. EMAIL FORMAL (reviewer académico senior / editorial board) — INGLÉS

```
Subject: Preprint review request — "Sociedad Opita" (LLM-driven social simulation, opita dialect)

Dear Prof. [Lastname],

I am writing to invite you to review the attached preprint,
"Sociedad Opita: A Reproducible, Culturally-Validated Benchmark
for Agent-Based Social Simulation in an Underrepresented Latin
American Rural Dialect," which I plan to submit to arXiv (cs.CY)
within the next two weeks and subsequently to IC2S2 2027, FAccT
2027, and ACL 2027 (cultural-NLP track).

I selected you because your work on [their specific topic — e.g.,
"computational social science with LLM agents" / "cultural NLP
benchmark design" / "fairness evaluation in generative systems"]
is directly relevant to the methodological and substantive
contributions of this paper.

**Summary of contributions**

The benchmark instantiates 41 LLM-driven agents of a single
Colombian rural town (Tello, Huila) — including 26 adults with
eight-layer forensic biographies (Big Five, Lomnitz reciprocity,
Dunbar social layers, Hofstede dimensions) and 15 children with
parallel developmental protocols. A seven-layer sociolinguistic
prompt, engineered from documented features of the opita dialect,
governs every agent turn. A 10-dialogue ground-truth corpus,
validated by the author (a native speaker of opita) using a
six-dimension rubric, is released under CC-BY-4.0. Four
reproducible experimental templates address gossip propagation,
conflict escalation, manipulation campaigns, and empathic
response. Empirical findings: (i) a measurable pro-social bias
in LLM role-play that flattens negative-affect traits; (ii) a
trade-off between dialect authenticity and trait visibility,
resolvable at an empirically tuned operating point; (iii)
structural centrality (geometric, not psychological) as the
dominant predictor of information-diffusion super-spreaders
(r = -0.54 between betweenness centrality and Openness).

**Materials**

The manuscript is attached (paper.pdf, ~10 pages).
Code, data, ground-truth, and experimental logs are public at:
https://github.com/nicourrutia98/sociedad-opita
License: MIT (code), CC-BY-4.0 (data).

**Requested feedback**

I would value your critical reading before arXiv submission
(target: [date, ~10-14 days out]). Particular topics where your
expertise would be especially helpful:

• The validity of using biographical inference (rather than
  psychometric inventories) for agent profile construction
• The 6-dimension validation rubric for opita dialogue quality
• The generalisability of the r = -0.54 structural-centrality
  finding to other small-rural-town settings
• Framing of the WEIRD critique in the AI-fairness literature

If the timing is not convenient, I would still value a brief
recommendation of another scholar who might be well-positioned
to review this work.

Thank you for your time and consideration.

Sincerely,
Juan Nicolás Urrutia Salcedo
Independent Researcher · Founder & CEO, Opita Code
Neiva, Huila, Colombia
GitHub: @nicourrutia98 · ORCID: [forthcoming]
```

---

## 4. POST LINKEDIN (broadcast corto) — INGLÉS

```
First preprint from my project Sociedad Opita — the first
reproducible, native-validated benchmark for LLM-driven social
simulation in a Latin American rural Spanish dialect (opita, Huila,
Colombia).

41 agents · 8-layer forensic biographies · 7-layer sociolinguistic
prompt · 10-dialogue ground truth (validated by me, native speaker) ·
4 reproducible experimental templates.

Three empirical findings:
• Pro-social bias measurable in LLM role-play (A-bajo under-represented)
• Dialect-vs-trait trade-off resolvable at tuned operating point
• Structural centrality > psychology for predicting super-spreaders
  (r = -0.54, betweenness vs Openness)

Paper + code + data: https://github.com/nicourrutia98/sociedad-opita

Would value feedback from anyone working on cultural NLP,
agent-based simulation, or AI fairness. Replies welcome.
```

---

## 5. TWEET THREAD (8 tweets) — INGLÉS

```
1/ New preprint from my project Sociedad Opita — first reproducible,
native-validated benchmark for LLM-driven social simulation in a
Latin American rural Spanish dialect (opita, Huila, Colombia).

Paper + code + data: https://github.com/nicourrutia98/sociedad-opita

2/ Why this matters: existing LLM social-simulation benchmarks
(Stanford Generative Agents, AI Town, Concordia) are structurally
WEIRD — anglophone, metropolitan, individually focused.

Society Opita is a Colombian rural town (Tello, Huila) — 41
agents with deep ethnographic specification.

3/ Each of the 26 adult agents has an 8-layer forensic biography:
civil data, family of origin, current family, daily routine,
specific ties, active conflicts, contradictions and secrets,
verbal register. Grounded in Big Five, Lomnitz reciprocity,
Dunbar social layers, Hofstede dimensions.

4/ Every agent call is wrapped in a 7-layer sociolinguistic
prompt: phonology, lexicon, pragmatics, generational register,
gendered variation, real 2026 events, register variation.
Plus 13 anti-AI-slop rules.

5/ 10 dialogues were validated by me (native speaker) using a
6-dimension rubric. All passed with ≥4/5 on linguistic realism
and conflict realism. Verbatim approval: "Así como está, está bien."

6/ Finding 1: LLM has a measurable pro-social bias — 88% trait
visibility overall, but low-Agreeableness systematically
under-represented (sesgo A-bajo documentado).

7/ Finding 2: dialect authenticity and trait visibility trade
off against each other. Tuned operating point: T=1.3,
role-constraint sandwich, BoN N=3.

8/ Finding 3: in a small town, geometry beats psychology.
Doña Rosa (the tendera near the inspección) is the #1
super-spreader with betweenness 0.29 — independent of her
Big Five. r(betweenness, Openness) = -0.54 across the 26 adults.

Feedback welcome: nicourrutia98.
```

---

## CHECKLIST antes de enviar

- [ ] PDF final revisado (paper.pdf, 222 KB)
- [ ] Repo público creado en github.com/nicourrutia98/sociedad-opita
- [ ] URL del repo pegada en cada template donde dice https://github.com/nicourrutia98/sociedad-opita
- [ ] ORCID registrado y link en footer
- [ ] Lista de 5-10 candidatos a reviewer (ver outreach-day4.md)
- [ ] Personalizar campos [nombre], [tema específico suyo], [fecha tentativa]
