/* -*- coding: utf-8 -*-
 * game/export.js — Exportación honesta de artefactos
 *
 * RESPONSABILIDAD: dar al usuario SUS datos en formatos abiertos.
 * Cada artefacto refleja SOLO lo que el usuario vio/exploró.
 *
 * NO agregamos marca de agua en free tier.
 * NO limitamos exports de datos del usuario.
 * Los artefactos son del usuario, no nuestros.
 */

'use strict';

const Exporter = (() => {
    let sessionPersonasViewed = new Set();
    let sessionComparisons = 0;
    let sessionStartedAt = Date.now();

    function init() {
        // Botón global de export
        document.getElementById('export-btn').addEventListener('click', openModal);
        document.getElementById('export-close').addEventListener('click', closeModal);

        // Click en cada formato
        document.querySelectorAll('.export-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                exportFormat(btn.dataset.format);
            });
        });
    }

    function trackView(personaId) {
        sessionPersonasViewed.add(personaId);
        Hud.incrementInsights();
    }

    function trackComparison() {
        sessionComparisons++;
    }

    function openModal() {
        document.getElementById('export-modal').classList.remove('hidden');
    }

    function closeModal() {
        document.getElementById('export-modal').classList.add('hidden');
    }

    function exportFormat(format) {
        const data = collectSessionData();
        const filename = `sociedad-opita-${Date.now()}.${format}`;

        switch (format) {
            case 'json':       downloadFile(JSON.stringify(data, null, 2), filename, 'application/json'); break;
            case 'bibtex':     downloadFile(toBibTeX(data), filename, 'application/x-bibtex'); break;
            case 'csv':        downloadFile(toCSV(data), filename, 'text/csv'); break;
            case 'markdown':   downloadFile(toMarkdown(data), filename, 'text/markdown'); break;
            case 'pdf':        exportPDF(data, filename); break;
            case 'graph':      downloadFile(toObsidianGraph(data), filename, 'application/json'); break;
        }
        closeModal();
    }

    function collectSessionData() {
        return {
            metadata: {
                source: 'Sociedad Opita',
                city: 'Tello, Huila',
                exported_at: new Date().toISOString(),
                session_duration_seconds: Math.floor((Date.now() - sessionStartedAt) / 1000),
                personas_viewed: Array.from(sessionPersonasViewed),
                comparisons_made: sessionComparisons,
                total_personas_in_city: DataLoader.getAllPersonas().length,
                limitations: [
                    'Big Five derivado de marcadores biográficos, no inventariado',
                    'Validación nativa parcial',
                    'Sesgo pro-social del LLM parcialmente mitigado',
                ],
            },
            personas_viewed: Array.from(sessionPersonasViewed).map(id => DataLoader.getPersona(id)).filter(Boolean),
            comparison_pairs: Compare.personas.length === 2 ? [Compare.personas] : [],
            city_full_data: {
                city_id: 'tello',
                personas: DataLoader.getAllPersonas(),
            },
        };
    }

    function toBibTeX(data) {
        // Para citar el producto + los datos
        let bib = `% Generado por Sociedad Opita el ${data.metadata.exported_at}
% Fuente: https://sociedad.opitacode.com
% NOTA: cite el producto, no las personas simuladas (son datos derivados)

@misc{sociedad_opita_2026,
  author = {Sociedad Opita Project},
  title = {Sociedad Opita: Forensic Simulation of a Rural Colombian Society},
  year = {2026},
  url = {https://sociedad.opitacode.com},
  note = {Simulación forense de Tello, Huila con Big Five, Lomnitz y Dunbar}
}

`;

        // Cita cada persona vista
        for (const p of data.personas_viewed) {
            bib += `@misc{opita_${p.persona_id},
  author = {Sociedad Opita Project},
  title = {{${p.display_name}}: perfil psicosocial},
  year = {2026},
  howpublished = {Sociedad Opita Dataset, Tello, Huila},
  note = {Big Five O=${p.big_five.O} C=${p.big_five.C} E=${p.big_five.E} A=${p.big_five.A} N=${p.big_five.N}}
}

`;
        }
        return bib;
    }

    function toCSV(data) {
        const headers = ['persona_id', 'display_name', 'role', 'age', 'archetype',
                         'O', 'C', 'E', 'A', 'N',
                         'lomnitz_primary', 'dunbar_intimates', 'dunbar_best_friends',
                         'betweenness', 'muletilla_count'];
        const rows = [headers.join(',')];

        for (const p of data.personas_viewed) {
            rows.push([
                p.persona_id,
                `"${p.display_name}"`,
                `"${p.role}"`,
                p.age,
                p.archetype,
                p.big_five.O, p.big_five.C, p.big_five.E, p.big_five.A, p.big_five.N,
                p.lomnitz.primary,
                p.dunbar.intimates, p.dunbar.best_friends,
                p.network?.betweenness || 0,
                (p.muletillas || []).length,
            ].join(','));
        }
        return rows.join('\n');
    }

    function toMarkdown(data) {
        let md = `# Sesión de exploración — Sociedad Opita

**Ciudad**: ${data.metadata.city}
**Fecha**: ${new Date(data.metadata.exported_at).toLocaleString('es-CO')}
**Duración**: ${formatDuration(data.metadata.session_duration_seconds)}
**Personas vistas**: ${data.metadata.personas_viewed.length}/${data.metadata.total_personas_in_city}
**Comparaciones**: ${data.metadata.comparisons_made}

---

## Personas exploradas

`;

        for (const p of data.personas_viewed) {
            md += `### ${p.display_name}
**Rol**: ${p.role}, ${p.age} años · **Arquetipo**: ${p.archetype}

| Big Five | Valor |
|---|---|
| Openness | ${p.big_five.O} |
| Conscientiousness | ${p.big_five.C} |
| Extraversion | ${p.big_five.E} |
| Agreeableness | ${p.big_five.A} |
| Neuroticism | ${p.big_five.N} |

**Lomnitz**: ${p.lomnitz.primary} (primario)
**Dunbar**: ${p.dunbar.intimates} íntimos, ${p.dunbar.best_friends} confidentes
**Muletillas**: ${(p.muletillas || []).map(m => `"${m}"`).join(', ')}

`;
        }

        md += `
---

## Limitaciones declaradas

${data.metadata.limitations.map(l => `- ${l}`).join('\n')}

---

*Generado por Sociedad Opita. Datos abiertos para uso académico y de investigación.*
`;
        return md;
    }

    function toObsidianGraph(data) {
        // Formato JSON compatible con Obsidian/Roam Research
        const nodes = [];
        const edges = [];

        for (const p of data.personas_viewed) {
            nodes.push({
                id: p.persona_id,
                label: p.display_name,
                group: p.archetype,
                properties: {
                    role: p.role,
                    age: p.age,
                    big_five: p.big_five,
                    lomnitz: p.lomnitz.primary,
                    betweenness: p.network?.betweenness || 0,
                },
            });

            // Edges a aliados
            for (const ally of (p.network?.aliados || [])) {
                if (data.personas_viewed.some(v => v.persona_id === ally)) {
                    edges.push({ source: p.persona_id, target: ally, type: 'aliado' });
                }
            }
            // Edges a conflictos
            for (const conf of (p.network?.conflictos || [])) {
                if (data.personas_viewed.some(v => v.persona_id === conf)) {
                    edges.push({ source: p.persona_id, target: conf, type: 'conflicto' });
                }
            }
        }

        return JSON.stringify({
            format: 'obsidian-graph',
            version: '1.0',
            nodes,
            edges,
            metadata: data.metadata,
        }, null, 2);
    }

    function exportPDF(data, filename) {
        // jsPDF simple
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();

        doc.setFontSize(18);
        doc.text('Sociedad Opita — Informe de exploración', 20, 20);

        doc.setFontSize(11);
        doc.text(`Ciudad: ${data.metadata.city}`, 20, 35);
        doc.text(`Fecha: ${new Date(data.metadata.exported_at).toLocaleString('es-CO')}`, 20, 42);
        doc.text(`Duración: ${formatDuration(data.metadata.session_duration_seconds)}`, 20, 49);
        doc.text(`Personas vistas: ${data.metadata.personas_viewed.length}/${data.metadata.total_personas_in_city}`, 20, 56);

        let y = 75;
        doc.setFontSize(14);
        doc.text('Personas exploradas', 20, y);
        y += 10;

        for (const p of data.personas_viewed) {
            if (y > 260) { doc.addPage(); y = 20; }

            doc.setFontSize(12);
            doc.text(`${p.display_name} — ${p.role}, ${p.age} años`, 20, y);
            y += 6;

            doc.setFontSize(10);
            doc.text(`Arquetipo: ${p.archetype}`, 25, y);
            y += 5;
            doc.text(`Big Five: O=${p.big_five.O} C=${p.big_five.C} E=${p.big_five.E} A=${p.big_five.A} N=${p.big_five.N}`, 25, y);
            y += 5;
            doc.text(`Lomnitz: ${p.lomnitz.primary} | Dunbar: ${p.dunbar.intimates} íntimos`, 25, y);
            y += 5;
            doc.text(`Muletillas: ${(p.muletillas || []).slice(0, 3).join(', ')}`, 25, y);
            y += 10;
        }

        if (y > 250) { doc.addPage(); y = 20; }
        doc.setFontSize(11);
        doc.text('Limitaciones declaradas:', 20, y);
        y += 6;
        doc.setFontSize(9);
        for (const lim of data.metadata.limitations) {
            doc.text(`• ${lim}`, 25, y);
            y += 5;
        }

        doc.save(filename);
    }

    function downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function formatDuration(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${String(secs).padStart(2, '0')}`;
    }

    return { init, trackView, trackComparison, openModal, closeModal };
})();
