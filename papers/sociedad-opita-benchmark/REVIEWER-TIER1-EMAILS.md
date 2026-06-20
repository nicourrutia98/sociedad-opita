# Personalized Reviewer Invitations — Tier 1 (Top 3 Candidates)

> Each email below is **ready to send** with one personalization already wired in.
> Just fill in the recipient's email and hit send.
>
> Replace `[REPO_URL]` → `https://github.com/nicourrutia98/sociedad-opita`
> Replace `[ORCID]` → `0009-0009-5808-479X`

---

## Email 1 — Joon Sung Park (Stanford)

**To:** joonspk@stanford.edu (verify first)
**Subject:** Preprint review request + arXiv endorsement — Sociedad Opita (LLM-driven social simulation in the opita dialect)
**Attachment:** paper.pdf

```
Dear Joon,

I'm writing because your work — especially the 2024 paper on
simulating 1,052 individuals with personality-grounded LLM
agents — is the closest published benchmark to what I've built
for Tello, a rural Colombian town of 41 agents. I'm hoping
you'd be willing to read my preprint and, separately, consider
endorsing my submission to arXiv cs.CY.

The paper, "Sociedad Opita," is the first reproducible,
culturally-validated benchmark for LLM-driven agent-based social
simulation in a Latin American rural Spanish dialect (opita,
Huila, Colombia). I take the personality-injection idea from
your 2024 paper further into 8-layer forensic biographies + a
7-layer native opita sociolinguistic prompt + quantitative
best-of-N scoring, and I find that *structural centrality*
(geometric, not psychological) dominates psychological traits
in predicting diffusion. Across 26 adults, betweenness centrality
correlates r = -0.54 with Openness, and ablating personality while
keeping geographic positions preserves the pattern. Doña Rosa,
the tendera near the inspección, is the #1 super-spreader with
betweenness 0.29 — independent of her Big Five.

Three findings of immediate relevance to your research:
1. **Pro-social bias in role-play** — 88% trait visibility overall,
   but documented low-Agreeableness bias (the LLM refuses to be
   a faithful simulation instrument for conflict-heavy scenes).
2. **Dialect-vs-trait trade-off** — empirically tuned at T=1.3
   with role-constraint sandwich + best-of-N=3.
3. **Geometry > psychology** for predicting diffusion in
   small-town networks — your Christakis-Fowler tradition
   empirically confirmed in a fully LLM-driven simulation.

Two specific asks:

(a) If you can read the preprint (10 pp + appendices) and send
back feedback by **2026-07-10**, that would be invaluable. I'm
particularly interested in your read on whether the structural-vs-
psychological finding generalises to your 1,052-agent setup.

(b) Separately, if you'd be willing to endorse the submission to
arXiv cs.CY (my first-time submission to that category), that
would unblock the preprint process. The endorsement is a 5-minute
arXiv form once you've confirmed you've read the abstract; the
full review request above is independent of it.

Materials:
- Paper (PDF): attached
- Code + data + 17 experiment runs: https://github.com/nicourrutia98/sociedad-opita
- ORCID: 0009-0009-5808-479X

If the timing doesn't work, a brief recommendation of another
scholar who might be well-positioned to review would also be
deeply appreciated.

Thank you for your time.

Sincerely,
Juan Nicolás Urrutia Salcedo
Independent Researcher · Founder & CEO, Opita Code
Neiva, Huila, Colombia
GitHub: @nicourrutia98 · ORCID: 0009-0009-5808-479X · arXiv: Opitadev
```

---

## Email 2 — Christopher Bail (Duke)

**To:** christopher.bail@duke.edu (verify first)
**Subject:** Preprint review request — "Sociedad Opita" (LLM as social-science tool, tested on opita dialect)
**Attachment:** paper.pdf

```
Dear Chris,

I'm writing because your PNAS piece, "Can generative AI improve
social science?," is the closest published statement of the
methodological tension I've been wrestling with in practice:
are LLMs *subjects of* social-science analysis, or *tools for*
social-science analysis?

My preprint, "Sociedad Opita," sits exactly at that boundary.
It's a reproducible, culturally-validated benchmark of 41 LLM-
driven agents of Tello, Huila — a rural Colombian town — built
on 8-layer forensic biographies and a 7-layer opita socio-
linguistic prompt. The system is both: the LLM is the *subject*
of an empirical study on pro-social bias in role-play, AND the
*instrument* used to test cultural theory (Lomnitz reciprocity,
Dunbar layers, Hofstede dimensions).

I find what I think is a concrete version of the issue your PNAS
piece gestures at. Across 24 generated dialogues, 88% of expected
persona traits are visible overall, but the validation log
documents a low-Agreeableness bias — the LLM systematically under-
represents antagonism, conflict, and negative-affect expression.
The pro-social bias persists across mitigation strategies
(temperature, role-constraint sandwich, best-of-N sampling).

For the structural finding: in the gossip-propagation template,
geometric betweenness centrality of agent locations predicts
super-spreaders more strongly than Big Five. The #1 super-spreader
is Doña Rosa, the tendera near the inspección, with betweenness
0.29 — independent of her Big Five profile. This echoes your
Christakis-Fowler / structural tradition but is, to my knowledge,
the first empirical confirmation in a fully LLM-driven simulation.

I'd value your critical reading by **2026-07-10**. Particular
questions where your sociology + CS background would be useful:

- Is "forensic simulation instrument" a defensible framing for
  this kind of LLM population?
- Does the r = -0.54 betweenness-vs-Openness finding generalise
  beyond rural Latin America?
- Is single-reviewer native validation adequate, or do I need
  to expand the ground truth substantially before publishing?

Materials:
- Paper (PDF): attached
- Code + data + 17 experiment runs: https://github.com/nicourrutia98/sociedad-opita
- ORCID: 0009-0009-5808-479X

If timing is tight, I'd still value a brief recommendation of a
sociologist or computational social scientist in your network
who might be well-positioned.

Thank you.

Sincerely,
Juan Nicolás Urrutia Salcedo
Independent Researcher · Founder & CEO, Opita Code
Neiva, Huila, Colombia
GitHub: @nicourrutia98 · ORCID: 0009-0009-5808-479X
```

---

## Email 3 — Hannah Rose Kirk

**To:** verify current email (she has been at Oxford, DeepMind, independent — search Twitter @hannahrkirk)
**Subject:** Preprint review request — "Sociedad Opita" (cultural alignment in opita dialect, the multilingual ≠ multicultural problem)
**Attachment:** paper.pdf

```
Dear Hannah,

Your 2025 paper, "Multilingual ≠ multicultural," is the closest
published statement of the gap I've been trying to fix in
Tello. Your *Break the Checkbox* follow-up goes further into the
question of how closed-style evaluations of "cultural alignment"
miss the texture of how cultural communities actually behave.
My preprint sits squarely in that conversation.

"Sociedad Opita" is a reproducible, culturally-validated benchmark
of 41 LLM-driven agents of Tello, Huila, Colombia, built on
8-layer forensic biographies and a 7-layer opita socio-linguistic
prompt. The system is native-validated by a Huila-born reviewer
(me). The headline finding is *pro-social bias*: across 24
generated dialogues, 88% of expected persona traits are visible
overall, but the validation log documents a low-Agreeableness
bias — the LLM systematically under-represents antagonism,
conflict, and negative-affect expression.

The reason this matters for your line of work: opita is just
standard Spanish at ~80% lexical overlap. Yet the LLM drops
dramatically on conflict-laden scenes — the same model that
generates "competent standard-Spanish dialogue" generates
"sanitised, anti-conflict opita dialogue" because the alignment
training is upstream of any opita-specific tuning.

I think this is the same phenomenon your paper gestures at — the
alignment training that makes LLMs "culturally safe" in the broad
sense makes them culturally unfaithful in the minority-variant
sense. But I've only tested it on one community. I'd value your
read on whether this generalises to the other cases you studied.

Materials:
- Paper (PDF): attached
- Code + data + 17 experiment runs: https://github.com/nicourrutia98/sociedad-opita
- ORCID: 0009-0009-5808-479X

Two specific questions:
- Is 10 native-validated dialogues enough to call it "culturally
  validated," or do I need a different validation scheme
  entirely (e.g., cross-community)?
- Does the pro-social bias pattern predict what you'd expect
  from your closed-style evaluation critique?

I'd appreciate feedback by **2026-07-10** if possible.

Thank you.

Sincerely,
Juan Nicolás Urrutia Salcedo
Independent Researcher · Founder & CEO, Opita Code
Neiva, Huila, Colombia
GitHub: @nicourrutia98 · ORCID: 0009-0009-5808-479X · arXiv: Opitadev
```

---

## Send-tracking table

| # | Candidate | Email | Sent? | Response | Endorsement? | Deadline |
|---|-----------|-------|-------|----------|--------------|----------|
| 1 | Joon Sung Park | joonspk@stanford.edu | ☐ | ☐ | ☐ request  | 2026-07-10 |
| 2 | Christopher Bail | christopher.bail@duke.edu | ☐ | ☐ | ☐ optional | 2026-07-10 |
| 3 | Hannah Rose Kirk | (verify) | ☐ | ☐ | ☐ optional | 2026-07-10 |
| 4 | Su Lin Blodgett | (verify) | ☐ | ☐ | — | 2026-07-12 |
| 5 | Andrea Baronchelli | (verify) | ☐ | ☐ | ☐ optional | 2026-07-12 |
| 6 | USCO faculty | (personal) | ☐ | ☐ | — | 2026-07-15 |
| 7 | Colombian NLP | (verify) | ☐ | ☐ | — | 2026-07-15 |

After 7 days without response, send a polite nudge. After 14 days without response, move on.