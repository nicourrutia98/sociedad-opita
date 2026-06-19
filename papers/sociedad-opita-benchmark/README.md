# Sociedad Opita Benchmark — Paper

This directory contains the academic paper, supplementary materials, and submission metadata for the **Sociedad Opita** benchmark.

## Author

**Juan Nicolás Urrutia Salcedo**
Independent Researcher · Opita Code · Neiva, Huila, Colombia
GitHub: [@nicourrutia98](https://github.com/nicourrutia98)
Instagram: [@nico98urrutia](https://www.instagram.com/nico98urrutia/)

## Paper

**Title:** *Sociedad Opita: A Reproducible, Culturally-Validated Benchmark for Agent-Based Social Simulation in an Underrepresented Latin American Rural Dialect*

**File:** [`paper.md`](./paper.md) (Markdown source, ~5,000 words / ~5–6 pages in two-column IC2S2/FAccT layout)

**Status:** Draft v1.0, 2026-06-19.

**Authorship note:** Juan Nicolás Urrutia Salcedo is the sole author and originator of the project, the data, the code, the personas, the sociolinguistic prompt, the experimental design, the validation protocol, and the empirical findings reported in the manuscript. He is also the sole validator of the ground-truth corpus (Section 4.1) in his capacity as a native speaker of the *opita* dialect. AI tools were used as assistance under his direction; their role is disclosed in full in **Section 8** of the paper (*AI Assistance Disclosure*).

## Target Venues (in submission priority order)

| Venue | Deadline (estimated) | Track | Format | Fit |
|---|---|---|---|---|
| **arXiv preprint** | 2026-06-25 | cs.CY | Preprint | **Highest priority** — establish priority + gather feedback |
| **IC2S2 2026** | ~2026-03 (already past — 2027 next cycle) | Computational Social Science | 4–6 pages + appendix | Primary methodological fit |
| **FAccT 2026** | ~2026-01 (already past — 2026 late cycle) | Fairness, Accountability, Transparency | 10 pages + appendix | Strong fit: cultural representation, bias documentation |
| **ACL 2026** | ~2026-02 (already past — 2027 next cycle) | Cultural NLP / Multilingual | 8 pages long, 4 pages short | Fit: dialect-specific LLM benchmark |
| **CSCW 2026** | ~2026-07 | Late-breaking work | 4 pages | Fit: computational ethnography |
| **Nature Human Behaviour** | n/a | Letter / Perspective | n/a | Aspirational; needs deeper empirical claims |

**Realistic primary target:** **arXiv preprint first** (immediate), then **IC2S2 2027 / FAccT 2027 / ACL 2027 / CSCW late-breaking 2026** depending on cycle.

## Companion Release

The paper is accompanied by the project repository containing:

- Full simulation framework (`code/`)
- 41 personas in YAML (`cities/tello/`)
- 7-layer sociolinguistic prompt (`prompts/`)
- 10 validated dialogues + rubric (`ground-truth/`)
- 17 reproducible experiment runs (`experiments/`)
- Methodology documentation (`docs/`)

The public GitHub release is available at: **https://github.com/nicourrutia98/sociedad-opita**

## AI Assistance Summary

Three classes of AI tools supported this work:

1. **Frontier chat-oriented LLM (the simulation subject)** — the model used to generate agent dialogues. The specific vendor and version are disclosed in Section 3.5 of the paper (and referenced in `metadata.json`), since they constitute the empirical subject of the study.
2. **Open-source AI coding assistant (MIT-licensed)** — the *instrument* (coding assistant for the simulation framework). Vendor intentionally generalised in this public README to keep focus on the benchmark rather than the development tooling.
3. **Commercial multimodal LLM** — the *vehicle* (manuscript preparation assistant: literature synthesis, prose drafting, English polishing). Vendor withheld for the same reason.

Full disclosure in **Section 8** of the paper.

---

*Last updated: 2026-06-19*