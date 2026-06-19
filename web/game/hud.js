/* -*- coding: utf-8 -*-
 * game/hud.js — HUD honesto (sin manipulación psicológica)
 *
 * RESPONSABILIDAD: mostrar métricas de la exploración del usuario.
 * - Métricas REALES de lo que el usuario hizo
 * - Sin "engagement vacío" (no se cuenta tiempo inactivo)
 * - Sin comparación social (no hay leaderboard)
 * - Sin FOMO (no hay "X personas mirando esto ahora")
 *
 * Insight density es la métrica honesta: cuántos insights generados.
 */

'use strict';

const Hud = (() => {
    let viewedCount = 0;
    let comparisonCount = 0;
    let insightsCount = 0;
    let activeSeconds = 0;
    let lastActiveTick = Date.now();
    let tickInterval = null;

    function init() {
        // Tick cada segundo, solo cuenta si el usuario está activo (mouse en página)
        tickInterval = setInterval(() => {
            if (document.visibilityState === 'visible' && Date.now() - lastActiveTick < 30000) {
                activeSeconds++;
                updateTimeDisplay();
            }
        }, 1000);

        // Mouse/key activity
        ['mousemove', 'keydown', 'click', 'scroll'].forEach(ev => {
            document.addEventListener(ev, () => { lastActiveTick = Date.now(); }, { passive: true });
        });
    }

    function incrementViewed() {
        viewedCount++;
        document.getElementById('hud-viewed').textContent = `${viewedCount}/29`;
    }

    function incrementComparison() {
        comparisonCount++;
        document.getElementById('hud-comparisons').textContent = comparisonCount;
        Exporter.trackComparison();
    }

    function incrementInsights() {
        // Cada click en persona = 1 insight (vio info nueva)
        insightsCount++;
        document.getElementById('hud-insights').textContent = insightsCount;
    }

    function updateTimeDisplay() {
        const mins = Math.floor(activeSeconds / 60);
        const secs = activeSeconds % 60;
        document.getElementById('hud-time').textContent = `${mins}:${String(secs).padStart(2, '0')}`;
    }

    return { init, incrementViewed, incrementComparison, incrementInsights };
})();
