/* -*- coding: utf-8 -*-
 * game/info_panel.js — Panel lateral con datos de la persona
 *
 * RESPONSABILIDAD: mostrar la información REAL del dataset.
 * Si algo no está en los datos, no se inventa.
 */

'use strict';

const InfoPanel = (() => {
    let currentPersona = null;
    let panel = null;

    function init(onSimulateCallback, onCompareCallback, onExportCallback) {
        panel = document.getElementById('info-panel');
        document.getElementById('panel-close').addEventListener('click', close);
        document.getElementById('btn-simulate').addEventListener('click', () => {
            if (currentPersona && onSimulateCallback) onSimulateCallback(currentPersona);
        });
        document.getElementById('btn-compare').addEventListener('click', () => {
            if (currentPersona && onCompareCallback) onCompareCallback(currentPersona);
        });
        document.getElementById('btn-export-person').addEventListener('click', () => {
            if (currentPersona && onExportCallback) onExportCallback(currentPersona);
        });
    }

    function show(persona) {
        currentPersona = persona;
        panel.classList.remove('hidden');

        // Header
        document.getElementById('persona-name').textContent = persona.display_name;
        document.getElementById('persona-role').textContent =
            `${persona.role}, ${persona.age} años · ${persona.archetype}`;

        // Big Five — barras horizontales
        renderBigFive(persona.big_five);

        // Lomnitz
        renderLomnitz(persona.lomnitz);

        // Dunbar
        renderDunbar(persona.dunbar);

        // Muletillas
        renderMuletillas(persona.muletillas, persona.speaking_style);

        // Psicología
        renderPsychology(persona.motivations, persona.fears);

        // Red
        renderNetwork(persona.network);
    }

    function renderBigFive(bf) {
        const container = document.getElementById('big-five');
        const traits = [
            { key: 'O', name: 'Openness', desc: 'apertura a experiencia' },
            { key: 'C', name: 'Conscientiousness', desc: 'responsabilidad' },
            { key: 'E', name: 'Extraversion', desc: 'extraversión' },
            { key: 'A', name: 'Agreeableness', desc: 'amabilidad' },
            { key: 'N', name: 'Neuroticism', desc: 'neuroticismo' },
        ];

        container.innerHTML = traits.map(t => {
            const val = bf[t.key] || 0;
            const barColor = val >= 60 ? '#6b3e2e' : val >= 40 ? '#8b7355' : '#a89070';
            return `
                <div class="bf-row">
                    <div class="bf-label">
                        <strong>${t.key}</strong>
                        <span class="bf-desc">${t.desc}</span>
                    </div>
                    <div class="bf-bar">
                        <div class="bf-fill" style="width:${val}%;background:${barColor};"></div>
                    </div>
                    <div class="bf-value">${val}</div>
                </div>
            `;
        }).join('');
    }

    function renderLomnitz(l) {
        const container = document.getElementById('lomnitz-info');
        const meanings = {
            A: '<strong>A — Simétrica</strong>: reciprocidad entre iguales cercanos',
            B: '<strong>B — Generalizada</strong>: red extendida de favores',
            C: '<strong>C — Negativa</strong>: distancia, enemistad o conflicto',
        };
        container.innerHTML = `
            <div class="lomnitz-primary">${meanings[l.primary] || meanings.A}</div>
            ${l.secondary ? `<div class="lomnitz-secondary">Red secundaria: ${meanings[l.secondary] || meanings.B}</div>` : ''}
            <p class="footnote">Lomnitz (1975), <em>Cómo sobreviven los marginados</em>.</p>
        `;
    }

    function renderDunbar(d) {
        const container = document.getElementById('dunbar-info');
        container.innerHTML = `
            <div class="dunbar-stats">
                <div class="dunbar-stat">
                    <span class="dunbar-num">${d.layer}</span>
                    <span class="dunbar-desc">capa total</span>
                </div>
                <div class="dunbar-stat">
                    <span class="dunbar-num">${d.intimates}</span>
                    <span class="dunbar-desc">íntimos</span>
                </div>
                <div class="dunbar-stat">
                    <span class="dunbar-num">${d.best_friends}</span>
                    <span class="dunbar-desc">confidentes</span>
                </div>
                <div class="dunbar-stat">
                    <span class="dunbar-num">${d.aspirational}</span>
                    <span class="dunbar-desc">aspiracionales</span>
                </div>
            </div>
            <p class="footnote">Capas de Dunbar (1992).</p>
        `;
    }

    function renderMuletillas(muletillas, speakingStyle) {
        const container = document.getElementById('muletillas-info');
        const m = (muletillas || []).map(m => `<span class="muletilla">"${m}"</span>`).join(' ');
        const s = (speakingStyle || []).map(s => `<li>${s.replace(/_/g, ' ')}</li>`).join('');

        container.innerHTML = `
            <div class="muletillas-list">${m || '<em>(sin muletillas documentadas)</em>'}</div>
            ${s ? `<ul class="speaking-style">${s}</ul>` : ''}
            <p class="footnote">Extraídas del trabajo de campo. Muletillas mejoran la autenticidad.</p>
        `;
    }

    function renderPsychology(motivations, fears) {
        const container = document.getElementById('psychology-info');
        const m = (motivations || []).map(m => `<li>${m.replace(/_/g, ' ')}</li>`).join('');
        const f = (fears || []).map(f => `<li>${f.replace(/_/g, ' ')}</li>`).join('');

        container.innerHTML = `
            <div class="psych-section">
                <h4>Motivaciones</h4>
                <ul>${m || '<li><em>(no documentadas)</em></li>'}</ul>
            </div>
            <div class="psych-section">
                <h4>Miedos</h4>
                <ul>${f || '<li><em>(no documentados)</em></li>'}</ul>
            </div>
        `;
    }

    function renderNetwork(network) {
        const container = document.getElementById('network-info');
        if (!network) {
            container.innerHTML = '<p class="footnote">Red social no documentada.</p>';
            return;
        }
        const allies = (network.aliados || []).map(a => `<span class="net-ally">${formatSlug(a)}</span>`).join('');
        const conflicts = (network.conflictos || []).map(c => `<span class="net-conflict">${formatSlug(c)}</span>`).join('');

        container.innerHTML = `
            <div class="network-stats">
                <div class="net-stat">
                    <span class="net-num">${network.betweenness?.toFixed(2) || '—'}</span>
                    <span class="net-desc">betweenness</span>
                </div>
                <div class="net-stat">
                    <span class="net-num">${network.degree || 0}</span>
                    <span class="net-desc">grado</span>
                </div>
            </div>
            ${allies ? `<div class="net-section"><h4>Aliados</h4>${allies}</div>` : ''}
            ${conflicts ? `<div class="net-section"><h4>Conflictos</h4>${conflicts}</div>` : ''}
        `;
    }

    function formatSlug(slug) {
        return slug.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    }

    function setSimulationResult(text) {
        const el = document.getElementById('simulation-result');
        if (text) {
            el.innerHTML = `<div class="sim-result-text">"${text}"</div><p class="footnote">Generado por DeepSeek LLM. Validación nativa parcial.</p>`;
            el.classList.remove('hidden');
        } else {
            el.classList.add('hidden');
        }
    }

    function close() {
        panel.classList.add('hidden');
        currentPersona = null;
    }

    function getCurrentPersona() {
        return currentPersona;
    }

    return { init, show, close, setSimulationResult, getCurrentPersona };
})();
