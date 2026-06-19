# Sociedad Opita

**A reproducible, culturally-validated benchmark for LLM-driven agent-based social simulation in the *opita* dialect of rural Colombian Spanish.**

> 📄 **Companion paper:** `papers/sociedad-opita-benchmark/paper.pdf` (preprint, forthcoming on arXiv cs.CY).
> 🎯 **What this repo is:** the simulation framework, 41 personas of Tello (Huila), the 7-layer *opita* sociolinguistic prompt, the 10-dialogue native-validated ground truth, and 17 reproducible experiment runs.
> 🪪 **Author:** Juan Nicolás Urrutia Salcedo · [ORCID](https://orcid.org/) (forthcoming) · Founder & CEO, Opita Code · Neiva, Huila, Colombia.

---

## At a glance

| | |
|---|---|
| **Agents** | 41 (26 adults + 15 children) |
| **Town** | Tello, Huila, Colombia |
| **Dialect** | *opita* (variety of rural Colombian Spanish) |
| **Biographies** | 8-layer forensic (civil data → verbal register) |
| **Psychometrics** | Big Five · Lomnitz reciprocity · Dunbar layers · Hofstede dimensions |
| **Sociolinguistic prompt** | 7 layers + 13 anti-AI-slop rules |
| **Ground truth** | 10 dialogues, validated by a native speaker (the author) |
| **Experimental templates** | 4 (gossip · conflict escalation · manipulation · empathy) |
| **Reproducibility** | 32-bit seed → byte-identical re-runs |
| **Findings** | 3 (pro-social bias · dialect-vs-trait trade-off · structural centrality) |

---

## Quick start

### 1. Clone + install

```bash
git clone https://github.com/nicourrutia98/sociedad-opita
cd sociedad-opita
pip install -r requirements.txt
```

### 2. Provide your LLM API key

The benchmark was developed with DeepSeek Chat (the simulation subject). To reproduce:

```bash
export DEEPSEEK_API_KEY="sk-your-key-here"
```

The system falls back to OpenRouter, Google Gemini, or any OpenAI-compatible endpoint via the multi-provider client (`multi_client.py`).

### 3. Run a single experiment

```bash
python experimento.py \
  --city tello \
  --scene "Parque Bolívar, domingo 7:30 AM" \
  --personas don_eliecer_patron don_rosalio_ganadero \
  --seed 42 \
  --output ./runs/my_first_run.jsonl
```

### 4. Reproduce the four experimental templates

```bash
# Gossip propagation
python experimentos/gossip_propagation.py --seed 42 --replicas 3

# Conflict escalation
python experimentos/conflict_escalation.py --condition mediation_by_cura

# Manipulation campaign
python experimentos/manipulation_campaign.py --target don_fernando_alcalde --intensity medio

# Empathy roleplay
python experimentos/empathy_roleplay.py --scenario inundacion
```

Each template writes JSONL events with cryptographic content hashes (`analysis/estadistica.py` validates chain-of-custody).

### 5. Inspect the validated ground truth

```bash
ls ground-truth/   # 10 dialogues + 6-dimension rubric + validator metadata
```

All dialogues were validated by the author (native speaker of *opita*, born and based in Neiva, Huila). Each was approved with the verbatim statement *"Así como está, está bien."*

---

## Repository structure

```
sociedad-opita/
├── papers/sociedad-opita-benchmark/    # The academic paper (PDF + Markdown + LaTeX)
├── cities/tello/                        # 26 adult + 15 child personas (YAML)
├── cities/_template/                    # Template for replicating to another municipality
├── prompts/                             # 7-layer sociolinguistic system prompt
├── ground-truth/                        # 10 validated dialogues + rubric (CC-BY-4.0)
├── experimentos/                        # 4 experimental templates + dashboards
├── analysis/                            # Statistics, network centrality, best-of-N
├── city_factory/                        # Reusable city template generator
├── docs/                                # Methodology, biographies, psychometric protocol
├── web/                                 # Static frontend (HTML/JS)
├── tests/                               # Pytest suite
├── reloj.py                             # Virtual-time clock (deterministic)
├── motor_simulacion.py                  # Main simulation engine
├── prompt_builder.py                    # Prompt assembly
├── multi_client.py                      # Multi-provider LLM client (public-safe)
├── geo_tello.py                         # Geographic positions for the 41 personas
├── simulacion_v3_geografica.py          # End-to-end runner with geo + network
└── requirements.txt
```

---

## What this benchmark is — and what it isn't

**Is:** a reproducible instrument for measuring how well frontier LLMs represent the *opita* dialect and the cultural dynamics of a single small Colombian town.

**Is not:** a measurement instrument in the psychometric sense. Validation is **internal** (consistency) and **ecological** (forensic credibility to a native), not classical psychometrics. Findings are qualitative and quantitative where the data supports them.

See the paper's **Section 5 (Limitations)** and **Section 7 (Ethics Statement)** for the full discussion.

---

## Three empirical findings (from the paper)

1. **Pro-social bias in LLM role-play.** Across 24 dialogues, 88% of expected persona traits are visible overall, but low-Agreeableness personas are systematically muted. Documented mitigation: temperature elevation (T=1.3), role-constraint sandwich, anti-congeniality system instructions, best-of-N sampling.

2. **Dialect-vs-trait trade-off.** Dialect authenticity (muletilla density) and trait visibility (Big Five consistency) trade off against each other. The empirically tuned operating point is T=1.3 with role-constraint sandwich and best-of-N=3.

3. **Structural centrality predicts diffusion more than psychology.** In the gossip-propagation template, geometric betweenness centrality of agent locations predicts super-spreaders more strongly than Big Five. Doña Rosa (the *tendera* near the inspección) is the #1 super-spreader with betweenness 0.29 — independent of her Big Five. Ablating personality while keeping geography preserves the pattern. Across the 26 adults, *r*(betweenness, Openness) = −0.54.

---

## Extending to a second municipality

The `cities/_template/` directory contains a starter template for adding a new town:

```bash
cp -r cities/_template cities/my_new_town
# Edit city.yaml, hofstede.yaml, cultural_markers.md
# Add personas to personas/ following the 8-layer protocol
# Re-run experiments — the framework auto-detects the new city
```

A natural follow-up is replicating to **Neiva** (the departmental capital) to test cultural variation within Huila, or **Garzón** (different microregion of Huila) to test within-department variation.

---

## Ethics

All biographical data are **composite, fictionalised personas**. Living individuals are not depicted; where a persona echoes a real person, identifying details have been altered. The project ships an **opt-out protocol**: any member of the Tello community who identifies a persona as depicting them can request modification or removal (see `web/ethics.html`).

The benchmark is released openly for **non-commercial use**; commercial use requires attribution. See `LICENSE`.

---

## Citation

```bibtex
@misc{urrutia2026sociedadopita,
  title        = {Sociedad Opita: A Reproducible, Culturally-Validated Benchmark for Agent-Based Social Simulation in an Underrepresented Latin American Rural Dialect},
  author       = {Urrutia Salcedo, Juan Nicolás},
  year         = {2026},
  month        = jun,
  day          = 19,
  howpublished = {\url{https://github.com/nicourrutia98/sociedad-opita}},
  note         = {Forthcoming public release; preprint on arXiv (cs.CY)}
}
```

---

## License

- **Code:** MIT
- **Personas, ground-truth dialogues, and biographical data:** CC-BY-4.0
- **Paper text:** CC-BY-4.0
- **Commercial use** of the benchmark requires attribution to the author.

See `LICENSE` for full text.

---

## Contact

Juan Nicolás Urrutia Salcedo · GitHub [@nicourrutia98](https://github.com/nicourrutia98) · Instagram [@nico98urrutia](https://instagram.com/nico98urrutia) · Neiva, Huila, Colombia
