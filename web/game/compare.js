/* -*- coding: utf-8 -*-
 * game/compare.js — Comparación 2 personas lado a lado
 *
 * RESPONSABILIDAD: comparación honesta de datos del dataset.
 * No inventa diferencias ni similitudes; las muestra.
 */

'use strict';

const Compare = (() => {
    let panel = null;
    let personasToCompare = [];

    function init(onExportCallback) {
        panel = document.getElementById('compare-panel');
        document.getElementById('compare-close').addEventListener('click', close);
        document.getElementById('btn-export-compare').addEventListener('click', () => {
            if (personasToCompare.length === 2 && onExportCallback) {
                onExportCallback(personasToCompare[0], personasToCompare[1]);
            }
        });
    }

    function start(persona1) {
        // Iniciar comparación pidiendo la segunda persona
        personasToCompare = [persona1];
        showSelectSecondPersona(persona1);
    }

    function showSelectSecondPersona(p1) {
        const all = DataLoader.getAllPersonas();
        const others = all.filter(p => p.persona_id !== p1.persona_id);

        panel.classList.remove('hidden');

        let html = `
            <p class="modal-intro">
                Comparación con <strong>${p1.display_name}</strong>. Selecciona la segunda persona:
            </p>
            <div class="compare-picker">
        `;

        for (const p of others) {
            html += `
                <button class="compare-pick-btn" data-id="${p.persona_id}">
                    <strong>${p.display_name}</strong><br>
                    <span class="role">${p.role}, ${p.age}</span>
                </button>
            `;
        }
        html += '</div>';

        document.getElementById('compare-content').innerHTML = html;

        // Bind clicks
        document.querySelectorAll('.compare-pick-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const p2 = DataLoader.getPersona(btn.dataset.id);
                if (p2) render(p1, p2);
            });
        });
    }

    function render(p1, p2) {
        personasToCompare = [p1, p2];

        // Cálculo de diferencias reales
        const diff = computeDifferences(p1, p2);

        const html = `
            <div class="compare-grid">
                <div class="compare-col">
                    <h3>${p1.display_name}</h3>
                    <p class="role">${p1.role}, ${p1.age} años</p>
                    <p class="archetype">${p1.archetype}</p>
                    ${renderComparisonBody(p1)}
                </div>
                <div class="compare-col">
                    <h3>${p2.display_name}</h3>
                    <p class="role">${p2.role}, ${p2.age} años</p>
                    <p class="archetype">${p2.archetype}</p>
                    ${renderComparisonBody(p2)}
                </div>
            </div>

            <div class="compare-summary">
                <h3>Diferencias</h3>
                ${diff}
            </div>
        `;
        document.getElementById('compare-content').innerHTML = html;
    }

    function renderComparisonBody(p) {
        return `
            <div class="compare-section">
                <h4>Big Five</h4>
                ${Object.entries(p.big_five).map(([k, v]) =>
                    `<div class="compare-bf"><span>${k}</span><span class="compare-val">${v}</span></div>`
                ).join('')}
            </div>
            <div class="compare-section">
                <h4>Lomnitz</h4>
                <p>Primario: <strong>${p.lomnitz.primary}</strong></p>
                ${p.lomnitz.secondary ? `<p>Secundario: ${p.lomnitz.secondary}</p>` : ''}
            </div>
            <div class="compare-section">
                <h4>Dunbar</h4>
                <p>Íntimos: ${p.dunbar.intimates} · Confidentes: ${p.dunbar.best_friends}</p>
                <p>Betweenness: ${p.network?.betweenness?.toFixed(2) || '—'}</p>
            </div>
            <div class="compare-section">
                <h4>Muletillas</h4>
                <p class="muletillas-compare">${(p.muletillas || []).map(m => `"${m}"`).join(' · ')}</p>
            </div>
        `;
    }

    function computeDifferences(p1, p2) {
        const differences = [];

        // Big Five diffs
        for (const trait of 'OCEAN') {
            const v1 = p1.big_five[trait];
            const v2 = p2.big_five[trait];
            const diff = Math.abs(v1 - v2);
            if (diff >= 15) {
                differences.push(`
                    <div class="diff-row">
                        <span class="diff-trait">${trait}</span>
                        <span class="diff-vals">${v1} vs ${v2}</span>
                        <span class="diff-delta">Δ ${diff}</span>
                    </div>
                `);
            }
        }

        // Lomnitz
        if (p1.lomnitz.primary !== p2.lomnitz.primary) {
            differences.push(`
                <div class="diff-row">
                    <span class="diff-trait">Lomnitz primario</span>
                    <span class="diff-vals">${p1.lomnitz.primary} vs ${p2.lomnitz.primary}</span>
                    <span class="diff-delta">distinto</span>
                </div>
            `);
        }

        // Betweenness
        const b1 = p1.network?.betweenness || 0;
        const b2 = p2.network?.betweenness || 0;
        const bDiff = Math.abs(b1 - b2);
        if (bDiff >= 0.1) {
            differences.push(`
                <div class="diff-row">
                    <span class="diff-trait">Betweenness</span>
                    <span class="diff-vals">${b1.toFixed(2)} vs ${b2.toFixed(2)}</span>
                    <span class="diff-delta">Δ ${bDiff.toFixed(2)}</span>
                </div>
            `);
        }

        // Archetype
        if (p1.archetype !== p2.archetype) {
            differences.push(`
                <div class="diff-row">
                    <span class="diff-trait">Arquetipo</span>
                    <span class="diff-vals">${p1.archetype} vs ${p2.archetype}</span>
                    <span class="diff-delta">distinto</span>
                </div>
            `);
        }

        if (differences.length === 0) {
            return '<p class="footnote">Las dos personas son similares en las métricas comparadas.</p>';
        }

        return differences.join('');
    }

    function close() {
        panel.classList.add('hidden');
        personasToCompare = [];
    }

    return { init, start, close, get personas() { return personasToCompare; } };
})();
