/* -*- coding: utf-8 -*-
 * game/engine.js — Motor PixiJS del mapa 2D de Tello
 *
 * RESPONSABILIDAD: renderizar el mapa cenital y los nodos clickeables.
 * HONESTIDAD: cada nodo es información real (Big Five, Lomnitz, Dunbar),
 *              no decoración. El tooltip muestra el information scent real.
 */

'use strict';

const TelloMap = (() => {
    let app = null;
    let container = null;
    let personasLayer = null;
    let buildingsLayer = null;
    let selectedPersonaId = null;
    let onPersonaClick = null;

    // Configuración del mapa (proporciones en pixeles, no geográficas)
    const MAP_CONFIG = {
        width: 1400,
        height: 900,
        backgroundColor: 0xfaf6ed,
        buildingsColor: 0xc8b89a,
        buildingsStroke: 0x6b4f2e,
        roadColor: 0xd4c5a3,
        plazaColor: 0xb8d4a0,
        personaRadius: 12,
        personaStroke: 0x2c1810,
        selectedScale: 1.4,
    };

    // Edificios representativos de Tello (basados en geo_tello.py)
    const BUILDINGS = [
        { id: 'plaza_bolivar', label: 'Plaza Bolívar', x: 700, y: 450, w: 180, h: 140, kind: 'plaza' },
        { id: 'iglesia_san_antonio', label: 'Iglesia San Antonio', x: 700, y: 240, w: 100, h: 80, kind: 'iglesia' },
        { id: 'tienda_dona_rosa', label: 'Tienda Doña Rosa', x: 540, y: 460, w: 60, h: 50, kind: 'tienda' },
        { id: 'panaderia_mercedes', label: 'Panadería Mercedes', x: 580, y: 540, w: 50, h: 40, kind: 'tienda' },
        { id: 'botica_eliseo', label: 'Botica Eliseo', x: 850, y: 470, w: 50, h: 40, kind: 'tienda' },
        { id: 'casa_cural', label: 'Casa Cural', x: 640, y: 280, w: 70, h: 50, kind: 'casa' },
        { id: 'estacion_policia', label: 'Estación Policía', x: 880, y: 240, w: 70, h: 50, kind: 'oficial' },
        { id: 'banco_agrario', label: 'Banco Agrario', x: 540, y: 320, w: 70, h: 50, kind: 'oficial' },
        { id: 'hospital_san_antonio', label: 'Hospital San Antonio', x: 360, y: 280, w: 100, h: 70, kind: 'salud' },
        { id: 'ie_tello', label: 'IE Tello', x: 280, y: 580, w: 120, h: 80, kind: 'educacion' },
        { id: 'coliseo_cubierto', label: 'Coliseo Cubierto', x: 1100, y: 600, w: 90, h: 70, kind: 'deporte' },
        { id: 'estadio_municipal', label: 'Estadio Municipal', x: 1240, y: 580, w: 110, h: 90, kind: 'deporte' },
        { id: 'taberna_la_mocha', label: 'Taberna La Mocha', x: 780, y: 580, w: 60, h: 50, kind: 'social' },
        { id: 'billar_el_descanso', label: 'Billar El Descanso', x: 820, y: 620, w: 60, h: 50, kind: 'social' },
        { id: 'farmacia_san_jose', label: 'Farmacia San José', x: 870, y: 530, w: 50, h: 40, kind: 'salud' },
        { id: 'finca_quintero', label: 'Finca Quintero (Don Rosalío)', x: 200, y: 200, w: 100, h: 90, kind: 'finca' },
        { id: 'finca_matarredonda', label: 'Finca Matarredonda (Don Eliécer)', x: 1280, y: 200, w: 100, h: 90, kind: 'finca' },
        { id: 'casa_partera', label: 'Casa Doña Prudencia', x: 460, y: 600, w: 60, h: 50, kind: 'casa' },
        { id: 'rio_magdalena', label: 'Río Magdalena', x: 200, y: 800, w: 1100, h: 30, kind: 'rio' },
    ];

    // Posiciones aproximadas de las personas (basadas en rutas diarias geo_tello.py)
    // Simplificación para el mapa 2D — el original tiene sistema (-12..12, -8..8)
    const PERSONA_POSITIONS = {
        don_rosalio_ganadero:      { x: 250, y: 240, building: 'finca_quintero' },
        don_rosalio_rival:         { x: 380, y: 290, building: 'finca_quintero' },
        don_eliecer_patron:        { x: 1330, y: 240, building: 'finca_matarredonda' },
        jhon_eliecer_hijo_patron:  { x: 1340, y: 290, building: 'finca_matarredonda' },
        jhon_eliecer_jornalero:    { x: 1290, y: 280, building: 'finca_matarredonda' },
        padro_cecilio_sacerdote:   { x: 670, y: 295, building: 'casa_cural' },
        jhon_jairo_sacristan:      { x: 710, y: 280, building: 'iglesia_san_antonio' },
        dona_prudencia_viuda:      { x: 480, y: 620, building: 'casa_partera' },
        dona_prudencia_partera:    { x: 490, y: 625, building: 'casa_partera' },
        dona_rosa_tendera:         { x: 570, y: 480, building: 'tienda_dona_rosa' },
        don_eliecer_patron:        { x: 1330, y: 240, building: 'finca_matarredonda' },
        don_octavio_medico:        { x: 410, y: 320, building: 'hospital_san_antonio' },
        don_sigifredo_politico:    { x: 720, y: 410, building: 'plaza_bolivar' },
        don_sigifredo_inspector:   { x: 905, y: 270, building: 'estacion_policia' },
        don_fernando_alcalde:      { x: 575, y: 340, building: 'banco_agrario' },
        capitan_hernan_policia:    { x: 895, y: 260, building: 'estacion_policia' },
        subintendente_saavedra:    { x: 915, y: 275, building: 'estacion_policia' },
        beatriz_personera:         { x: 735, y: 440, building: 'plaza_bolivar' },
        patricia_comisaria:        { x: 745, y: 445, building: 'plaza_bolivar' },
        dona_mercedes_panadera:    { x: 600, y: 560, building: 'panaderia_mercedes' },
        don_eliseo_boticario:      { x: 870, y: 490, building: 'botica_eliseo' },
        don_abelardo_conductor:    { x: 730, y: 580, building: 'plaza_bolivar' },
        aurora_maestra:            { x: 320, y: 620, building: 'ie_tello' },
        edilma_secretaria:         { x: 350, y: 630, building: 'ie_tello' },
        dona_lucia_maestra_jubilada: { x: 340, y: 640, building: 'ie_tello' },
        laura_reina:               { x: 720, y: 470, building: 'plaza_bolivar' },
        mariana_universitaria:     { x: 700, y: 480, building: 'plaza_bolivar' },
        valentina_secretaria_joven: { x: 580, y: 350, building: 'banco_agrario' },
        jhon_fredy_joven:          { x: 800, y: 600, building: 'taberna_la_mocha' },
        don_emigdio_agricultor:    { x: 100, y: 380, building: 'vereda' },
    };

    // Colores por arquetipo (sin significado moral, solo organización visual)
    const ARCHETYPE_COLORS = {
        ganadero_tradicional: 0x8b4513,
        comerciante_urbano: 0x4682b4,
        sacerdote_rural: 0x6a0dad,
        maestro_escuela: 0x228b22,
        medico_tradicional: 0xdc143c,
        tendero_pueblo: 0xff8c00,
        autoridad_policia: 0x2f4f4f,
        artesano_independiente: 0x8b008b,
        politico_local: 0xb22222,
        trabajador_rural: 0xa0522d,
        viuda_anfitriona: 0xdb7093,
        joven_migrante: 0x00ced1,
    };

    function init(canvasElement, personasData, onClickCallback) {
        onPersonaClick = onClickCallback;

        app = new PIXI.Application({
            view: canvasElement,
            width: canvasElement.clientWidth,
            height: canvasElement.clientHeight,
            backgroundColor: MAP_CONFIG.backgroundColor,
            antialias: true,
            resolution: window.devicePixelRatio || 1,
            autoDensity: true,
        });

        container = new PIXI.Container();
        app.stage.addChild(container);

        // Centrar el mapa
        const scale = Math.min(
            canvasElement.clientWidth / MAP_CONFIG.width,
            canvasElement.clientHeight / MAP_CONFIG.height
        );
        container.scale.set(scale * 0.95);
        container.x = (canvasElement.clientWidth - MAP_CONFIG.width * scale * 0.95) / 2;
        container.y = (canvasElement.clientHeight - MAP_CONFIG.height * scale * 0.95) / 2;

        drawBackground();
        drawBuildings();
        drawRoads();
        drawPersonas(personasData);

        // Drag para mover el mapa (con scroll wheel o click-drag)
        setupInteraction();

        // Resize
        window.addEventListener('resize', () => {
            app.renderer.resize(canvasElement.clientWidth, canvasElement.clientHeight);
        });
    }

    function drawBackground() {
        // Fondo verde claro para veredas
        const bg = new PIXI.Graphics();
        bg.beginFill(0xe8e0c8);
        bg.drawRect(0, 0, MAP_CONFIG.width, MAP_CONFIG.height);
        bg.endFill();

        // Río Magdalena abajo
        bg.beginFill(0x6892b0, 0.6);
        bg.drawRoundedRect(0, 800, MAP_CONFIG.width, 40, 8);
        bg.endFill();

        container.addChild(bg);
    }

    function drawRoads() {
        const roads = new PIXI.Graphics();
        roads.beginFill(MAP_CONFIG.roadColor);
        // Camino principal este-oeste
        roads.drawRect(0, 440, MAP_CONFIG.width, 16);
        roads.endFill();
        roads.beginFill(MAP_CONFIG.roadColor);
        // Camino norte-sur
        roads.drawRect(690, 0, 16, MAP_CONFIG.height);
        roads.endFill();

        // Caminos secundarios
        roads.beginFill(MAP_CONFIG.roadColor, 0.7);
        roads.drawRect(0, 280, 400, 8);
        roads.drawRect(1180, 200, 8, 400);
        roads.endFill();

        container.addChild(roads);
    }

    function drawBuildings() {
        buildingsLayer = new PIXI.Container();
        container.addChild(buildingsLayer);

        for (const b of BUILDINGS) {
            const g = new PIXI.Graphics();

            // Color según tipo
            const colors = {
                plaza: MAP_CONFIG.plazaColor,
                iglesia: 0xa89878,
                tienda: 0xc89860,
                casa: 0xc8a878,
                oficial: 0x989898,
                salud: 0xf0f0f0,
                educacion: 0xe0c890,
                deporte: 0xa0c890,
                social: 0xb89080,
                finca: 0xa08060,
                rio: 0x6892b0,
                vereda: 0xc0b890,
            };

            g.beginFill(colors[b.kind] || MAP_CONFIG.buildingsColor);
            g.lineStyle(1.5, MAP_CONFIG.buildingsStroke, 0.7);
            g.drawRect(b.x - b.w / 2, b.y - b.h / 2, b.w, b.h);
            g.endFill();

            // Label
            const label = new PIXI.Text(b.label, {
                fontFamily: 'Georgia, serif',
                fontSize: 10,
                fill: 0x2c1810,
                align: 'center',
            });
            label.anchor.set(0.5);
            label.x = b.x;
            label.y = b.y + b.h / 2 + 10;

            buildingsLayer.addChild(g);
            buildingsLayer.addChild(label);
        }
    }

    function drawPersonas(personasData) {
        personasLayer = new PIXI.Container();
        container.addChild(personasLayer);

        for (const p of personasData) {
            const pos = PERSONA_POSITIONS[p.persona_id];
            if (!pos) continue;

            const color = ARCHETYPE_COLORS[p.archetype] || 0x808080;
            const g = new PIXI.Graphics();

            // Halo exterior
            g.beginFill(color, 0.2);
            g.drawCircle(pos.x, pos.y, MAP_CONFIG.personaRadius + 4);
            g.endFill();

            // Cuerpo principal
            g.beginFill(color, 0.85);
            g.lineStyle(1.5, MAP_CONFIG.personaStroke);
            g.drawCircle(pos.x, pos.y, MAP_CONFIG.personaRadius);
            g.endFill();

            // Iniciales
            const initials = getInitials(p.display_name);
            const text = new PIXI.Text(initials, {
                fontFamily: 'Georgia, serif',
                fontSize: 10,
                fontWeight: 'bold',
                fill: 0xffffff,
                align: 'center',
            });
            text.anchor.set(0.5);
            text.x = pos.x;
            text.y = pos.y;

            g.interactive = true;
            g.cursor = 'pointer';
            g.buttonMode = true;
            g.personaId = p.persona_id;
            g.personaData = p;

            g.on('pointerover', (event) => {
                showTooltip(event, p);
                g.scale.set(1.2);
            });
            g.on('pointerout', () => {
                hideTooltip();
                if (g.personaId !== selectedPersonaId) {
                    g.scale.set(1.0);
                }
            });
            g.on('click', (event) => {
                event.stopPropagation();
                selectPersona(g, p);
            });

            personasLayer.addChild(g);
            personasLayer.addChild(text);
        }
    }

    function getInitials(name) {
        // "Don Rosalío" -> "DR", "Doña Rosa" -> "DR"
        const parts = name.split(/\s+/);
        if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
        return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }

    let tooltipEl = null;
    function showTooltip(event, p) {
        if (!tooltipEl) {
            tooltipEl = document.getElementById('map-tooltip');
        }
        if (!tooltipEl) return;

        const preview = `
            <strong>${p.display_name}</strong><br>
            <span style="color:#8b5a3c;">${p.role}, ${p.age} años</span><br>
            <span style="font-style:italic;font-size:0.85em;">
                ${p.muletillas.slice(0, 1).join(' · ') || p.archetype}
            </span>
        `;
        tooltipEl.innerHTML = preview;
        tooltipEl.classList.remove('hidden');

        // Posicionar cerca del cursor
        const rect = event.target.view.canvas?.getBoundingClientRect() || { left: 0, top: 0 };
        tooltipEl.style.left = (rect.left + 20) + 'px';
        tooltipEl.style.top = (rect.top + 20) + 'px';
    }

    function hideTooltip() {
        if (tooltipEl) tooltipEl.classList.add('hidden');
    }

    function selectPersona(g, p) {
        // Deseleccionar anterior
        if (selectedPersonaId) {
            personasLayer.children.forEach(child => {
                if (child.personaId === selectedPersonaId) {
                    child.scale.set(1.0);
                }
            });
        }

        selectedPersonaId = p.persona_id;
        g.scale.set(MAP_CONFIG.selectedScale);

        if (onPersonaClick) {
            onPersonaClick(p);
        }
    }

    function setupInteraction() {
        let isDragging = false;
        let dragStart = { x: 0, y: 0 };
        let containerStart = { x: 0, y: 0 };

        app.stage.eventMode = 'static';
        app.stage.hitArea = app.screen;

        app.stage.on('pointerdown', (event) => {
            // Solo drag si el click NO fue en una persona
            if (event.target === app.stage) {
                isDragging = true;
                dragStart = { x: event.global.x, y: event.global.y };
                containerStart = { x: container.x, y: container.y };
            }
        });

        app.stage.on('pointermove', (event) => {
            if (isDragging) {
                container.x = containerStart.x + (event.global.x - dragStart.x);
                container.y = containerStart.y + (event.global.y - dragStart.y);
            }
        });

        app.stage.on('pointerup', () => { isDragging = false; });
        app.stage.on('pointerupoutside', () => { isDragging = false; });

        // Zoom con scroll
        app.stage.on('wheel', (event) => {
            event.preventDefault();
            const delta = event.deltaY > 0 ? 0.9 : 1.1;
            const newScale = Math.max(0.3, Math.min(2.5, container.scale.x * delta));
            container.scale.set(newScale);
        });
    }

    function highlightPersona(personaId) {
        // Para cuando se compara
        personasLayer.children.forEach(child => {
            if (child.personaId === personaId) {
                child.scale.set(1.3);
            } else if (child.personaId !== selectedPersonaId) {
                child.scale.set(1.0);
            }
        });
    }

    return {
        init,
        highlightPersona,
        get selectedPersonaId() { return selectedPersonaId; },
    };
})();
