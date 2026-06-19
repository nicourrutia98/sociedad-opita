/* -*- coding: utf-8 -*-
 * game/main.js — Orquestador principal del mapa forense
 *
 * RESPONSABILIDAD: conectar el motor PixiJS con los datos y paneles.
 * Sin gimmicks. Cada interacción tiene un propósito forense real.
 */

'use strict';

(async function main() {
    // 1. Cargar datos de la ciudad
    const cityData = await DataLoader.loadCity('tello');
    const personas = cityData.personas;

    // 2. Inicializar módulos
    const canvas = document.getElementById('map-canvas');
    canvas.width = canvas.clientWidth;
    canvas.height = canvas.clientHeight;

    InfoPanel.init(
        onSimulatePersona,
        onComparePersona,
        onExportPersona
    );

    Compare.init(onExportComparison);
    Exporter.init();
    Hud.init();

    // 3. Inicializar mapa
    TelloMap.init(canvas, personas, onPersonaClick);

    // 4. Helper para simulación (usa API real si existe, fallback a mensaje honesto)
    async function simulateScene(persona) {
        const scene = {
            time: '07:00',
            place: 'Plaza Bolívar',
            weather: '26°C',
        };

        // Intentar API real
        try {
            const response = await fetch(`${window.location.origin}/v1/simulate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    city_id: 'tello',
                    persona_id: persona.persona_id,
                    scene,
                    model: 'deepseek-chat',
                    temperature: 1.3,
                }),
            });
            if (response.ok) {
                const data = await response.json();
                return data.text;
            }
        } catch (e) {
            // API no disponible, fallback honesto
        }

        // Fallback honesto: muestra que la simulación requiere backend
        return null;
    }

    async function onPersonaClick(persona) {
        InfoPanel.show(persona);
        Hud.incrementViewed();
        Exporter.trackView(persona.persona_id);
        TelloMap.highlightPersona(persona.persona_id);
    }

    async function onSimulatePersona(persona) {
        const text = await simulateScene(persona);
        if (text) {
            InfoPanel.setSimulationResult(text);
        } else {
            // Honestamente: backend no disponible, mostrar mensaje transparente
            InfoPanel.setSimulationResult(
                '[Simulación LLM no disponible en este momento. ' +
                'El backend DeepSeek requiere deploy. ' +
                'Los datos psicométricos y la red mostrados son datos validados.]'
            );
        }
    }

    function onComparePersona(persona1) {
        Compare.start(persona1);
        Hud.incrementComparison();
    }

    function onExportPersona(persona) {
        Exporter.openModal();
    }

    function onExportComparison(p1, p2) {
        Exporter.openModal();
    }

    console.log(`Sociedad Opita — ${personas.length} personas cargadas de Tello, Huila`);
})();
