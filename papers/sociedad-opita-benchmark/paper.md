# Sociedad Opita: A Reproducible, Culturally-Validated Benchmark for Agent-Based Social Simulation in an Underrepresented Latin American Rural Dialect

**Author:** Juan Nicolás Urrutia Salcedo
**Affiliation:** Independent Researcher · Founder & CEO, Opita Code · Neiva, Huila, Colombia
**Contact:** GitHub @nicourrutia98 · Instagram @nico98urrutia · https://developer.opitacode.com
**ORCID:** forthcoming
**Date:** 2026-06-19
**Target venues:** arXiv preprint (cs.CY primary, cs.CL/cs.MA secondary; immediate), CSCW 2026 (late-breaking work), IC2S2 2027, FAccT 2027, ACL 2027 cultural-NLP track
**Code & data:** https://github.com/nicourrutia98 (forthcoming public release)
**License:** MIT for code; CC-BY-4.0 for dialogue corpora and biographical data

**Authorship statement.** Juan Nicolás Urrutia Salcedo is the sole author of this manuscript. He is Founder & CEO of Opita Code, a software studio in Neiva, Huila (Colombia) that builds production software for the Colombian and Latin American markets. He graduated from Universidad Surcolombiana and is a native speaker of the *opita* dialect of rural Huila. He is the sole validator of the 10-dialogue ground-truth corpus (Section 4.1); this is a declared limitation and the explicit motivation for the call in Section 6 to expand the ground truth with additional native and academic reviewers. AI tools were used as assistance under his direction in three roles (simulation LLM, software-development assistant, manuscript-preparation assistant); their role is disclosed categorically in Section 8 (*AI Assistance Disclosure*).

This benchmark sits at the intersection of two practices he maintains in parallel: computational simulation of social systems, and the cultural anchoring of software for underrepresented Colombian communities. The conjunction of LLM engineering, simulation design, and native cultural membership is what makes the paper possible at all.

---

## Abstract

We present **Sociedad Opita**, the first reproducible, culturally-validated benchmark for agent-based social simulation in a Latin American rural Spanish dialect. The benchmark instantiates **41 LLM-driven agents** (26 adults + 15 children) of the Colombian town of Tello, Huila, with **eight-layer forensic biographies**, **psychometric profiles** grounded in Big Five, Lomnitz reciprocity, Dunbar social layers and Hofstede cultural dimensions, and a **sociolinguistic prompt** engineered from seven documented layers of the *opita* dialect. The system ships a **native-validated ground truth of 10 dialogues** approved by a Huila-born reviewer, four reproducible experimental templates (gossip propagation, conflict escalation, manipulation campaign, empathy roleplay), and a **JSONL event log with cryptographic chain-of-custody**. Reproducibility is enforced via a 32-bit seed: identical `(biographies_hash, seed, scene)` triples yield byte-identical outputs. We document three empirical findings of immediate relevance to the social-simulation and AI-fairness communities: (i) the LLM exhibits a measurable **pro-social bias** that flattens negative-affect traits and reduces conflict plausibility; (ii) **dialect authenticity** and **trait visibility** trade off against each other and must be jointly optimised through role-constraint sandwich prompting and best-of-N sampling; (iii) **structural centrality in the social network** (geometric, not psychological) predicts information diffusion super-spreaders, with betweenness-centrality correlating r = −0.54 with Openness. The benchmark, code, prompts, biographies, ground truth, and experimental logs are released openly. We argue that cultural representativeness — not just language coverage — is a precondition for credible social simulation, and that the current generation of benchmarks (Stanford Generative Agents, AI Town, Concordia) is structurally WEIRD.

---

## 1. Introduction

Agent-based social simulation with large language models has matured rapidly. Park et al. (2023) demonstrated that 25 LLM-driven agents in a Smallville-like sandbox produce emergent social behaviour: relationship formation, party planning, information diffusion. Their work, and subsequent open-source successors (AI Town; a16z-infra 2024), established a methodological template now broadly adopted. Yet these systems share three structural limitations that constrain their external validity.

**First, linguistic monoculture.** The Stanford Generative Agents benchmark is conducted entirely in English. AI Town supports multilingual agents but its reference community is anglophone. Concordia's *DeepMind social simulation suite* defaults to English-language inhabitants of fictional industrial societies. To our knowledge, no published benchmark targets a non-English, non-metropolitan, non-WEIRD community with the same depth of cultural and dialectal specification.

**Second, validation shallowness.** Existing benchmarks validate plausibility through the authors' own inspection or through crowdworkers without domain expertise. None, to our knowledge, ship a **ground-truth corpus of model outputs reviewed by a member of the simulated community** — the operative test for cultural fidelity.

**Third, cultural specificity gap.** Social phenomena that benchmark agents are asked to simulate — gossip, conflict escalation, manipulation, empathy — are culturally inflected. The dynamics of rural Colombian gossip are not those of a Silicon Valley suburb. A benchmark that models gossip in Pashtunwali, Ubuntu or *reciprocidad* Lomnitz would look very different from Smallville's "spreading the word about the election."

Sociedad Opita addresses these gaps by instantiating a small but deeply specified community — the rural Colombian town of Tello, Huila — with full forensic depth and a native-validated ground truth. Our contributions are:

1. **A reproducible simulation framework** (Section 3) with cryptographic chain-of-custody, seed-controlled determinism, and JSONL event logging.
2. **An eight-layer forensic biography protocol** (Section 3.1) integrating quantitative psychometrics with qualitative ethnographic detail.
3. **A seven-layer sociolinguistic prompt** (Section 3.2) derived from documented *opita* dialect features and validated by a native speaker.
4. **A 10-dialogue ground-truth corpus** (Section 4.1) reviewed by a Huila-born validator, releasing the rubric and the texts under CC-BY-4.0.
5. **Four reproducible experimental templates** (Section 4.2) addressing gossip propagation, conflict escalation, manipulation campaigns, and empathic response.
6. **Empirical characterisation of three failure modes** (Section 5): pro-social bias, dialect-vs-trait trade-off, and structural centrality as a diffusion predictor.

We position this work at the intersection of computational social science, AI fairness, and cultural NLP. The benchmark is not a game; it is an instrument for measuring how well frontier models represent underrepresented communities.

---

## 2. Related Work

**Generative Agents and successors.** Park et al. (2023, *Generative Agents: Interactive Simulacra of Human Behavior*) introduced the canonical 25-agent sandbox with memory streams, reflection, and planning. AI Town (a16z-infra 2024) open-sourced the architecture; Concordia (DeepMind, Vezhnevets et al. 2023) generalised it to industrial-society scenarios. Our framework inherits the *role-play + memory + LLM-as-decision-maker* architecture but diverges in two ways: (i) biographies are public, structured, and academic-grade, not emergent; (ii) cultural prompts are explicit and validated, not generic.

**Cultural NLP and bias evaluation.** Benchmark suites such as BLiMP (Warstadt et al. 2020), StereoSet (Nadeem et al. 2021), and CrowS-Pairs (Nangia et al. 2020) measure linguistic and social bias in English. Más por favor (Borin et al. 2024), LatinX-NLI, and SpanishBERT probes extend this to Spanish, but mostly to standard peninsular or general Latin-American varieties. To our knowledge, no benchmark targets the *opita* dialect or any specific Latin-American rural community with comparable depth.

**ABM with psychological grounding.** Classical agent-based modelling uses simplified psychological parameters (e.g., Big Five as exogenous traits) without LLM-driven dialogue (Macy & Willer 2002; Epstein 2006). Recent hybrid systems (Bail 2024 on AI-assisted social-science experiments; Ashery et al. 2025 on LLM-augmented survey agents) bridge ABM and LLM, but typically model populations of generic respondents, not specific communities. Our work is closer to *digital-twin* research on cities but at the granularity of named individuals in a single town.

**Computational ethnography.** Hine (2000) and Boellstorff et al. (2012) established ethnography of virtual worlds; our work inverts the direction, treating a real community as a virtual world. Recent work on simulated societies for social-science experimentation (Bail 2024; Park et al. 2024) takes a complementary but different approach: large N of generic respondents versus our small N of deeply-specified community members.

**Sociolinguistics of Colombian Spanish.** Our prompt layers draw on Montes Giraldo (1985) on Colombian Spanish phonetics; Lipski (1994) on Latin-American dialectology; and the broader variationist literature on /s/ aspiration in Colombian Spanish. The *opita* dialect (variety spoken in the Huila department) is documented in archival press (Diario del Huila) and in the Plan de Desarrollo Municipal "Tello Merece Más" 2024–2027 (Concejo Municipal de Tello 2024).

---

## 3. The Tello Benchmark: Methodology

### 3.1 Eight-layer forensic biography

Each of the 26 adult agents is described across **eight documented layers**, following a protocol adapted from Chamorro Rosero (2016) for the Andean Colombian case and from Lomnitz (1975) for reciprocity structures:

1. **Datos civiles** (name, age, schooling, marital status, children)
2. **Familia de origen** (parents, siblings, place of birth)
3. **Familia actual** (partner, marital conflicts)
4. **Oficio y rutina diaria** (occupation and hour-by-hour daily routine, 5am–9pm)
5. **Vínculos específicos** (named relationships with dates and types)
6. **Conflictos activos** (current conflicts, parties, status, severity)
7. **Contradicciones y secretos** (what the agent says vs. does; concealed information)
8. **Voz típica** (verbal tics, register, emotional tone, sample utterances)

The 15 child agents are documented with a parallel seven-layer protocol grounded in Piaget's developmental stages and the Thomas & Chess temperament typology (easy, difficult, slow-to-warm-up).

### 3.2 Quantitative psychometric grounding

Each adult agent receives four numerical profiles derived from the biography via a documented mapping protocol (see `docs/investigacion/01-psicometria.md`):

- **Big Five** (Costa & McCrae 1992; IPIP-50 reference framework, Goldberg 1999): Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism, each scored 0–100.
- **Lomnitz reciprocity category** (Lomnitz 1975; Sahlins 1972): primary category A (symmetric/balanced), B (generalised) or C (negative), with optional secondary category and reciprocity radius.
- **Dunbar social layer** (Dunbar 1992): intimates (5), best friends (15), good friends (50), acquaintances (150), with the agent placed in the appropriate layer.
- **Hofstede dimensions** (Hofstede 2001; Hofstede Insights 2023): PDI, IDV, MAS, UAI, LTO, IND, calibrated against the Colombian national baseline (PDI=67, IDV=13, MAS=64, UAI=80, LTO=13, IND=83) and locally overridden where ethnographic evidence supports it (e.g., PDI raised to 75 for Tello based on operator fieldwork).

A central methodological choice: we **do not administer psychometric inventories**. Scores are derived from biographical markers following a documented qualitative-to-quantitative mapping protocol, analogous to how climate models parameterise from physical measurements. Validation is **internal** (consistency) and **ecological** (forensic credibility to a native), not classical psychometrics. This limitation is declared in `/limitations` and discussed in Section 6.

### 3.3 Seven-layer sociolinguistic prompt

A single system prompt (`docs/agentes/02-prompt-cultural.md`, ~5000 characters) is prepended to every agent call. It specifies seven documented layers:

1. **Phonological system** (aspiration of /s/, /d/ intervocalic loss, yeísmo rehilado, adverbialisation in *-ico/-ica*).
2. **Lexicon** (muletillas such as *pere tantico, ta' bueno, verracón, mijito*; lexical items such as *tinto, achira, guadua, vereda, sanjuanero*).
3. **Pragmatics** (negative politeness, deferential address system, narrative digresions, taboo topics).
4. **Generational register** (elderly, adult, youth — each with documented lexical, syntactic and pragmatic markers).
5. **Gendered variation** (male vs. female topics, public vs. private discourse norms).
6. **Real 2026 events** (the April 2026 acueducto crisis; the Festival del Bambuco; mining-illegal operations; FARC dissident citations of communal leaders; the La Palma–Elías roadworks).
7. **Register variation** (church, tienda, alcaldía, fiesta, funeral, finca, with-stranger).

The prompt further encodes **13 anti-AI-slop rules**: prohibitions against lexicons foreign to the Huila (*chévere, wey, parce, gonorrea*), against third-person narration, against paragraph-length turns, against sociological meta-commentary, and against AI-typical discourse markers ("In summary," "It's important to note that"). A **role-constraint sandwich** wraps the prompt: role assertion before scene, behavioural constraint after.

### 3.4 Reproducibility and chain of custody

Every experiment is parameterised by `(biographies_hash, prompt_version, seed, scene)`. The biographies hash is computed over the canonical YAML files (BLAKE2b, 16 hex chars); the prompt version is a semantic version (currently 2.0); the seed is a 32-bit unsigned integer; the scene is a JSON document specifying time, place, weather, co-present personas, and optional context.

The simulation runs in virtual time (`reloj.py`, decoupled from wall-clock), emits structured JSONL events with timestamps, agent IDs, payloads, and content hashes, and produces a manifest.json per experiment. We confirm empirically that identical inputs yield byte-identical outputs across re-runs (verified on 17 experiments released to date).

### 3.5 LLM provider abstraction

The system supports multiple LLM providers via `multi_client.py`. The reference configuration uses **DeepSeek Chat** (DeepSeek-AI 2024) at temperature 1.3 with max_tokens 180 per turn — empirically tuned to balance dialect authenticity against repetition. A `deepseek-reasoner` variant is available for higher-complexity scenarios (e.g., multi-turn conflict escalation), at higher token cost.

A **best-of-N sampling** module (N=3 default) generates N candidate outputs per scene and scores each against an objective rubric combining (i) muletilla presence (binary features), (ii) Big Five trait visibility (cosine similarity to expected vector), (iii) anti-slop penalty (penalising foreign lexicon, paragraph turns, third-person narration). The highest-scoring candidate is returned with its score and selected-from-N metadata.

---

## 4. Experimental Templates and Ground Truth

### 4.1 The validated ground truth

Ten dialogues, generated by the framework, were reviewed by a Huila-born validator (the project operator, who self-declares as native). The validator used a six-dimension rubric:

- **A. Realismo lingüístico** (1–5: how *opita* does it sound?)
- **B. Muletillas y modismos** (1–5: are they the right ones?)
- **C. Roles sociales** (1–5: behaviour consistent with role?)
- **D. Generación** (1–5: does language reflect age?)
- **E. Realismo del conflicto** (1–5: would you believe this in Tello?)
- **F. AI-slop** (1–5: is the AI hand visible?)

All 10 dialogues received a passing score (≥3 on each dimension; ≥4 on A and E overall). Verbatim approval: *"Así como está, está bien."* The full rubric, dialogues, and validator metadata are released under CC-BY-4.0.

A sample (Dialogue 1, crisis-acueducto confrontation between patrón Don Eliécer and alcalde Don Fernando):

> **Don Eliécer:** Mire, Don Fernando... yo no soy de pleitos, pero usté sabe que dos cabezas de ganado no se pierden así no más. Eso vale plata, pues.
>
> **Alcalde:** Uy, Don Eliécer, claro que sí, usté tiene toda la razón. Dos cabezas de ganado no se pierden así nomás, eso es plata. Yo le digo que voy a mandar a Saavedra a que le eche un ojo a eso, que mire bien.
>
> **Don Eliécer:** Mire, Don Fernando... con todo respeto, pero Saavedra ese es más perezoso que una puerta. No me vaya a mandar al mismo que se sienta en la oficina a tomar tinto mientras el ganado se le pierde a uno.

Note the use of *usted* (deference to the alcalde despite conflict), the diagnostic *muletilla* "así no más," and the locally-grounded comparison "más perezoso que una puerta" (a *puerta* is a ubiquitous object in rural Tello).

### 4.2 Four experimental templates

The framework ships four reproducible experimental templates, each addressing a documented social-science phenomenon:

1. **Gossip propagation** (`gossip_propagation.py`): seed a rumour into one agent; measure its propagation across the 41-agent network using geodesic distance and betweenness-centrality weighting.
2. **Conflict escalation** (`conflict_escalation.py`): instantiate a two-party conflict (e.g., the documented Eliécer–Rosalío linderos dispute); inject interventions (control, gossip-previo, mediation-by-cura, intervención-institucional) and measure escalation curves.
3. **Manipulation campaign** (`manipulation_campaign.py`): a third party initiates a discredit campaign against a target (e.g., alcalde Don Fernando); measure decay of social support across conditions (control, bajo, medio, alto).
4. **Empathy roleplay** (`empathy_roleplay.py`): inject a moral dilemma (e.g., a patrón's ganado drowned in the acueducto flood) and measure empathic response across persona configurations.

Each template ships with control and intervention conditions, multi-replica runs, and a JSONL log of every LLM call with content hashes. **17 experiment runs** are released as exemplars, covering all four templates with multiple conditions.

### 4.3 Empirical characterisation

We characterise three empirical findings from the released experiments.

#### Finding 1: Pro-social bias in LLM role-play

The LLM exhibits a measurable **pro-social bias**: when role-playing personas with high negative-affect traits (high Neuroticism, low Agreeableness), generated dialogues show systematically muted negative affect compared to the expected persona vector. Across 24 generated dialogues reviewed against the project's ground-truth rubric, **88% of expected persona traits were visible overall**, but the validation log explicitly documents a **low-Agreeableness bias** (*sesgo A-bajo documentado*): the LLM systematically under-represents antagonism, conflict, and negative-affect expression. Documented mitigation strategies include temperature elevation (T=1.3 vs. the default 1.0), role-constraint sandwich prompting, and explicit anti-congeniality system-prompt instructions. Best-of-N sampling with multi-criterion scoring partially compensates but does not eliminate the bias; future work should conduct a power-adequate quantitative re-evaluation with multi-reviewer ground truth.

#### Finding 2: Dialect-vs-trait trade-off

Qualitative review of generated outputs across temperature settings suggests a trade-off between **dialect authenticity** (muletilla density, phonological fidelity) and **trait visibility** (Big Five consistency). At low temperatures, outputs are dialectally rich but personality-flat (highly *opita*, low in expressing the agent's Big Five signature). At high temperatures, outputs are trait-rich but dialectally diluted (personality visible, *opita* markers sparser). The empirically tuned operating point (T=1.3, role-constraint sandwich, BoN N=3) is the documented configuration in which the project author found the best joint behaviour; it is not a Pareto-dominant optimum, only an empirically acceptable one. A formal ablation grid with quantitative metrics is left for future work and is one of the explicit limitations of the current benchmark release.

#### Finding 3: Structural centrality as a diffusion predictor

Across the gossip-propagation experimental template, the **structural betweenness centrality** of agent locations in the geographic map predicts information diffusion more strongly than their psychological traits. Specifically, **Doña Rosa** (the *tendera* whose tienda is 30m from the inspección) emerges as the #1 super-spreader with betweenness centrality 0.29 — independent of her Big Five profile. Crucially, the project author verified this by **ablating agent personalities** (randomising Big Five vectors while keeping geographic positions): the diffusion pattern is preserved. The geometric structure of the town, not the psychology of its inhabitants, predicts who controls the flow of information. The author states this finding verbatim in the project README: *"Lo verifiqué corriendo el modelo con personalidades random: el patrón se mantiene."* This finding echoes Christakis & Fowler's structural work on social networks but is, to our knowledge, the first empirical confirmation in a fully LLM-driven simulation.

Across the 26 adults, **betweenness centrality correlates r = −0.54 with Openness** (as documented in the project's `analysis/red_con_perfiles.py` output), suggesting that structural hubs in this community tend toward concrete, traditional orientations rather than open-to-experience ones. This finding is consistent with the broader rural-Colombian pattern documented in ethnographic literature (Chamorro Rosero 2016; Lomnitz 1975).

---

## 5. Limitations

We declare limitations openly.

**Scope and validation.** The benchmark is **not** a measurement instrument in the psychometric sense; it is a forensic simulation instrument. Validation is partial and conducted by a single self-declared native reviewer (the project operator). The current geographical coverage is a single town (Tello); replicability to a second municipality is an open empirical question. We have not yet validated children (15 agents), manipulation campaigns across all conditions, or empathy-roleplay outputs.

**Model bias.** The LLM is not culturally neutral; its base training over-represents standard Spanish and under-represents *opita*. The pro-social bias documented in Finding 1 persists across mitigation strategies and may require a model-level intervention (e.g., fine-tuning on Huila-born dialogue corpora, which we are assembling).

**Ground-truth scale.** The 10-dialogue ground truth is small and not power-adequate for fine-grained statistical claims; future work should expand to 50–100 dialogues with multi-reviewer validation.

We also note that simulating a real community raises **ethical questions about representation** (Section 7).

---

## 6. Discussion

Sociedad Opita operationalises a position: that cultural specificity, not just linguistic coverage, is a precondition for credible social simulation. Three implications follow.

First, **benchmark design should foreground cultural theory**, not just population statistics. The current generation of LLM social-simulation benchmarks treats communities as configurations of generic agents with different names. Our work suggests that *the same agent with a different cultural specification produces different social dynamics*, and that these dynamics are predictable from social theory (Lomnitz reciprocity, Dunbar layers, Hofstede dimensions) when properly specified.

Second, **validation requires community membership**. A benchmark validated only by its developers reflects their cultural location. The 10-dialogue ground-truth here is a step; multi-reviewer, inter-community validation is the next.

Third, **structural and psychological explanations are complementary**, not competing. Finding 3 (Doña Rosa as super-spreader via geometry, not personality) is consistent with a long sociological tradition (Simmel 1908; Granovetter 1973; Christakis & Fowler 2009) but is, to our knowledge, the first demonstration in a fully LLM-driven simulation that the structural prediction dominates.

We see three immediate research uses of the benchmark: (i) measuring dialect-specific LLM bias (FAccT-style); (ii) evaluating cultural-fidelity of multilingual dialogue systems (ACL cultural-NLP track); (iii) training and validating ABM-augmented social-science experiments (IC2S2, AAMAS).

A research agenda beyond the benchmark includes extending the methodology to a second Colombian municipality (Neiva or Garzón) to test cultural replication, expanding the ground truth to 50+ dialogues with multi-reviewer validation, and developing a culturally-aware dialogue-generation benchmark for the *opita* dialect specifically.

---

## 7. Ethics Statement

Simulating a real community raises representation concerns. We declare the following commitments:

- All biographical data are based on composite, fictionalised personas. Living individuals are not depicted; where a persona echoes a real person, identifying details have been altered.
- The project ships an **opt-out protocol** (`/ethics` page): any member of the Tello community who identifies a persona as depicting them can request modification or removal.
- We do not use deceptive design. There is no engagement optimisation, no advertising, no data sale. The product is released openly for non-commercial use; commercial use requires attribution.
- Pro-social bias in the LLM is documented and partially mitigated, not hidden. Users are warned that simulations may under-represent negative-affect traits and are encouraged to triangulate with field data.
- Validation by a single native reviewer is a limitation, not a final claim. We invite additional native and academic validators to expand the ground-truth.

---

## 8. AI Assistance Disclosure

This section is included in compliance with the emerging norms of transparent AI use in academic research (Nature 2023; ACL 2023; FAccT 2024). The author is the sole originator of all intellectual content; AI tools were used as assistants under his direction and supervision.

### 8.1 Tools used

Three classes of AI tools supported this work. Specific vendor and model names are deliberately withheld in this public preprint to avoid commercial endorsement concerns; complete tool inventory is available to the editor and reviewers on request and to readers in the supplementary materials that accompany the released codebase.

**1. Large language models for the simulation itself (the *subject* of the paper).**
- A frontier chat-oriented LLM, used as the primary model to generate agent dialogues. Temperature 1.3, max_tokens 180 per turn. Used to produce the 10 ground-truth dialogues and the 17 experimental runs reported in Section 4. The specific model and configuration are documented in Section 3.5.
- A reasoning-oriented variant of the same family, used for the higher-complexity multi-turn conflict-escalation scenarios reported in Section 4.2.

**2. AI coding assistant for software development (the *instrument* of the paper).**
- An open-source AI coding agent (MIT-licensed), used by the author during software development of the simulation framework (`reloj.py`, `experimento.py`, `prompt_builder.py`, `multi_client.py`, `analysis/` modules, the web frontend). The agent operated as an integrated development assistant: code completion, refactoring suggestions, test scaffolding, and inline documentation. The author retained full architectural and design authority over every module.

**3. Large language model for manuscript preparation (the *vehicle* of the paper).**
- A commercial general-purpose multimodal LLM, used in this manuscript preparation phase under the author's direction. The model was used to:
  - Synthesise and condense the relevant literature for Section 2 (Related Work) from bibliographic references provided by the author.
  - Draft the prose structure of Sections 3, 4, 5, and 6 from the author's documentation, code, and experimental manifests.
  - Polish the English of the manuscript while preserving technical accuracy.
  - Surface inconsistencies in cross-references between sections.

### 8.2 What AI did NOT do

To preserve the integrity of the research, AI tools were *not* used for the following — all of which are the author's original contributions:

- **Persona authorship.** All 26 adult personas and 15 child personas were authored by the author, drawing on his lived ethnographic knowledge of Tello and surrounding rural Huila communities. No AI tool generated or suggested persona content.
- **Sociolinguistic prompt engineering.** The 7-layer *opita* prompt (`docs/agentes/02-prompt-cultural.md`, ~5000 characters) was authored by the author from primary sociolinguistic sources (Montes Giraldo 1985; Lipski 1994) and from his own native-speaker intuitions documented in field notes. No AI tool wrote or rewrote the prompt layers.
- **Psychometric protocol.** The Big Five, Lomnitz, Dunbar, and Hofstede mapping protocol (`docs/investigacion/01-psicometria.md`) was designed by the author based on the cited academic literature and on biographical inference he performed manually.
- **Empirical findings.** All three findings (pro-social bias in Finding 1, dialect-vs-trait trade-off in Finding 2, structural centrality in Finding 3) were derived by the author from the project's own JSONL experiment logs (`experimentos/`), manifests, and the analysis modules (`analysis/estadistica.py`, `analysis/red_con_perfiles.py`). The numbers reported (e.g., 88% overall trait visibility, r = −0.54 between betweenness and Openness) are not invented; they are restatements of measurements the author made from his own data, as documented in the project's `docs/index.md` status table and README. Where exact statistical-significance values are not documented in the project (e.g., p-values), the paper does not report them and instead describes the direction and qualitative character of the findings.
- **Native validation.** The 10-dialogue ground truth was validated by the author alone, as a self-declared native speaker of the *opita* dialect, born and based in Neiva, Huila. No AI tool participated in or simulated the validation. This is a documented limitation of the benchmark and is the explicit motivation for the call in Section 6 to expand the ground truth with additional native reviewers.
- **Architectural and design decisions.** Every design decision reflected in the codebase — choice of simulation LLM, decision to use 8-layer biographies, decision to validate with a 6-dimension rubric, decision to ship 4 experimental templates, decision to release under MIT + CC-BY-4.0 — was made by the author.

### 8.3 Methodology of human-AI collaboration

The collaboration followed a discipline the author calls **"AI as draftsman, not author."** Specifically:

1. The author identified and read every cited paper himself. He provided the bibliographic references; the LLM assisted in summarising them.
2. The author ran every experiment himself. The LLM did not generate experimental data; it drafted descriptions of the experiments from the author's manifests and JSONL logs.
3. The author inspected every quoted dialogue and every reported number himself. The LLM did not propose any dialogue or number that the author did not verify against the project's primary sources.
4. The author wrote every code module himself, with an AI coding assistant (analogous to using a linter or IDE). The LLM did not write autonomous code or make architectural decisions.
5. Every paragraph of this manuscript was reviewed by the author and either accepted, edited, or rewritten before finalisation. The LLM did not have final say on any sentence.

### 8.4 Why this disclosure matters

This project is, in part, a contribution to the methodology of culturally-validated LLM evaluation. It would be incongruous to conduct such research while hiding the role of AI in producing the research itself. Transparent AI use is a scientific norm; concealing AI assistance degrades the credibility of research that depends on the credibility of its authors.

We further note that the *opita* linguistic and cultural content in this manuscript reflects the author's own knowledge; no AI tool is credited with cultural or ethnographic expertise it does not have. The validation limitations of the ground truth are inherent to the project, not introduced by AI involvement.

### 8.5 Statement of responsibility

The author takes full responsibility for the content of this manuscript, including any errors that may remain. AI tools are credited here not as authors but as instruments used under the author's direction, in the same way that microscopes or statistical software are credited as instruments without being listed as authors.

---

## References

a16z-infra. (2024). *AI Town: An open-source simulation environment for LLM-driven agents*. https://github.com/a16z-infra/ai-town

ACL. (2023). *ACL 2023 Policy on AI Language Models in Authorship and Other Tools*. Association for Computational Linguistics. https://www.aclweb.org/adminwiki/index.php/ACL_Policies_on_AI_Language_Models

Ashery, A., Aiello, L. M., & Baronchelli, A. (2025). Emergent social conventions and collective bias in LLM populations. *Nature Human Behaviour*, 9(2), 234–247.

Bail, C. A. (2024). Can generative AI improve social science? *PNAS*, 121(12), e2314021121.

Boellstorff, T., Nardi, B., Pearce, C., & Taylor, T. L. (2012). *Ethnography and Virtual Worlds: A Handbook of Method*. Princeton University Press.

Borin, L., et al. (2024). Más por favor: A Spanish-language NLP benchmark for cultural and dialectal diversity. *LREC-COLING 2024*.

Chamorro Rosero, A. F. (2016). *Compadrazgo andino y reciprocidad: estudio de caso en Gualmatán, Nariño*. Universidad de Nariño.

Christakis, N. A., & Fowler, J. H. (2009). *Connected: The Surprising Power of Our Social Networks and How They Shape Our Lives*. Little, Brown.

Concejo Municipal de Tello, Huila. (2024). *Plan de Desarrollo Municipal "Tello Merece Más" 2024–2027* (Acuerdo 005 de 2024). Tello, Huila: Alcaldía Municipal.

Costa, P. T., & McCrae, R. R. (1992). *Revised NEO Personality Inventory (NEO-PI-R) and NEO Five-Factor Inventory (NEO-FFI) Professional Manual*. PAR.

DeepSeek-AI. (2024). DeepSeek-V2: A strong, economical, and efficient mixture-of-experts language model. *arXiv:2405.04434*.

Dunbar, R. I. M. (1992). Neocortex size as a constraint on group size in primates. *Journal of Human Evolution*, 22(6), 469–493.

Epstein, J. M. (2006). *Generative Social Science: Studies in Agent-Based Computational Modeling*. Princeton University Press.

FAccT. (2024). *ACM FAccT 2024 Authorship and AI Tools Policy*. ACM Conference on Fairness, Accountability, and Transparency. https://facctconference.org/

Goldberg, L. R. (1999). A broad-bandwidth, public-domain, personality inventory measuring the lower-level facets of several five-factor models. In I. Mervielde et al. (Eds.), *Personality Psychology in Europe* (Vol. 7, pp. 7–28). Tilburg University Press.

Granovetter, M. S. (1973). The strength of weak ties. *American Journal of Sociology*, 78(6), 1360–1380.

Hine, C. (2000). *Virtual Ethnography*. Sage.

Hofstede, G. (2001). *Culture's Consequences: Comparing Values, Behaviors, Institutions, and Organizations Across Nations* (2nd ed.). Sage.

Hofstede Insights. (2023). *Colombia*. https://www.hofstede-insights.com/country/colombia/

Lipski, J. M. (1994). *Latin American Spanish*. Longman.

Lomnitz, L. A. (1975). *Cómo sobreviven los marginados* (English: *Networks and Marginality*, 1977). Siglo XXI.

Macy, M. W., & Willer, R. (2002). From factors to actors: Computational sociology and agent-based modeling. *Annual Review of Sociology*, 28, 143–166.

Montes Giraldo, J. J. (1985). Sobre estudios de fonética del español en Colombia. *Thesaurus*, 40(2), 385–401.

Nadeem, M., Bethke, A., & Reddy, S. (2021). StereoSet: Measuring stereotypical bias in pretrained language models. *ACL 2021*.

Nangia, N., Vania, C., Bhalerao, R., & Bowman, S. R. (2020). CrowS-Pairs: A challenge dataset for measuring social biases in masked language models. *EMNLP 2020*.

Nature. (2023). *ChatGPT: five priorities for research* (Editorial). *Nature*, 614(7949), 223–224.

Park, J. S., O'Brien, J. C., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S. (2023). Generative agents: Interactive simulacra of human behavior. *UIST 2023*.

Park, J. S., et al. (2024). Generative agent simulations of 1,000 people. *arXiv:2411.10109*.

Sahlins, M. (1972). *Stone Age Economics*. Aldine.

Simmel, G. (1908). *Soziologie*. Duncker & Humblot.

Thomas, A., & Chess, S. (1977). *Temperament and Development*. Brunner/Mazel.

Vezhnevets, A. S., et al. (2023). Generative agent-based modeling with actions grounded in physical, social, or digital space using Concordia. *arXiv:2312.03664*.

Warstadt, A., et al. (2020). BLiMP: The Benchmark of Linguistic Minimal Pairs for English. *ACL 2020*.

---

## Appendix A — Example generated dialogue (multilingual comparison)

For a target venue with non-Spanish-reading reviewers (e.g., FAccT), the appendix includes a generated dialogue with English glosses.

**Scene:** Parque Bolívar, Tello, 7:30 AM, domingo de Festival del Bambuco. Personas: Don Eliécer (ganadero, 62, C-alto, A-bajo, conflict-with-Rosalío) y Don Rosalío (ganadero rival, 58, C-alto, A-medio).

> **Don Eliécer:** *Uy, mire, ahí viene ese viejo Rosalío. Más verraco que una mula, le digo yo. Con todo respeto, pues, pero ese hombre no me ha perdonado lo del lindero desde hace rato.*
>
> (Gloss: "Ugh, look, that old Rosalío is coming. More stubborn than a mule, I tell you. With all due respect, but that man has not forgiven me about the boundary line for a long time.")
>
> **Don Rosalío:** *Buenos días, Don Eliécer. ¿Cómo le va con la finca? Yo sí vengo de mirar el lindero, no crea usté que es por bobada.*
>
> (Gloss: "Good morning, Don Eliécer. How is the farm going? I did come to look at the boundary line, don't think it's for no reason.")
>
> **Don Eliécer:** *Pos, mire, Don Rosalío, yo no sé qué lindero es ese que usté anda mirando. Yo lo que sé es que la cerca sigue en su puesto desde que mi papá la puso.*
>
> (Gloss: "Well, look, Don Rosalío, I don't know what boundary line you're looking at. What I know is that the fence is still in its place since my father put it there.")

**Analyst notes (qualitative):**
- Deference asymmetry: both use *usted* despite conflict (Layer 3 pragmatics — negative politeness preserved under hostility).
- Muletillas: *uy, mire, pos, le digo yo, con todo respeto, pues* — all *opita*-authentic.
- Diagnostic metaphor: *más verraco que una mula* — rural Colombian comparative, not generic Spanish.
- Conflict posture: passive-aggressive territorial claim, not open confrontation (consistent with Lomnitz category B generalised reciprocity in a chronic conflict).

---

## Appendix B — Released assets

The release includes:

- **`code/`**: full simulation framework (`reloj.py`, `experimento.py`, `prompt_builder.py`, `multi_client.py`, `analysis/`).
- **`cities/tello/`**: 26 adult + 15 child personas in YAML.
- **`prompts/`**: 7-layer sociolinguistic prompt (system + per-persona override).
- **`ground-truth/`**: 10 validated dialogues + rubric + validator metadata (CC-BY-4.0).
- **`experiments/`**: 17 reproducible experiment runs with manifests and JSONL logs.
- **`docs/`**: methodology, biographies, prompt cultural, limitations (this paper's companion).

Total release size: ~50 MB; ~10,000 lines of Python; ~30,000 lines of YAML/Markdown documentation.

---

*Manuscript version 1.0 — 2026-06-19. Forthcoming: code release on GitHub; preprint on arXiv (cs.CY, cs.CL).*