# -*- coding: utf-8 -*-
# Sociedad Opita — 15 ninos con perfiles evolutivos
# https://sociedad.opitacode.com (proximo)
"""
ninos_tello.py
==============
Perfiles forenses de 15 ninos de Tello, Huila 2026 (4-17 anos).

OBJETIVO FORENSE
================
Los ninos en la simulacion de Tello son agentes especiales:

1. NO son LLM-driven en la misma escala que adultos (demasiado costoso
   para su marginalidad narrativa). En cambio:
   - Son VISIBLES en rutinas (donde estan a cada hora).
   - Son DISCUTIDOS por adultos (los adultos mencionan "mijo", "mi
     nietico", "el pelao ese").
   - Son ACTIVOS en escenas especificas (escuela, parque, finca).
   - Tienen SUB-RED propia (companeros, conflictos, amores).

2. Para analisis de chisme, son nodos TERMINALES (reciben chisme de
   padres/hermanos, no lo retransmiten mucho fuera de su sub-red).

3. Para conflictos, son TESTIGOS o VICTIMAS colaterales, no actores
   principales (excepto en conflictos escolares o bullying).

MARCO TEORICO FORENSE
=====================
Para ninos no se usa Big Five (personalidad adulta). Se usa:

- **Temperamento (Thomas & Chess 1977)**:
    * Facil (40%): ritmicos, adaptables, humor positivo
    * Dificil (10%): irritables, irregulares, evitación
    * Lento para calentar (15%): baja reactividad, retraidos
    * Mixto (35%): combinaciones

- **Etapas de Piaget**:
    * Preoperacional (4-7): egocentrismo, animismo, magia
    * Operacional concreto (7-12): logica concreta, conservacion
    * Operacional formal (12+): hipotetico-deductivo, abstraccion

- **Apego (Bowlby/Ainsworth)**:
    * Seguro: explora, busca consuelo en cuidador
    * Ansioso: miedo al abandono, no explora
    * Evitativo: no busca consuelo, pseudo-independencia

- **Contextos de desarrollo (Bronfenbrenner)**:
    * Microsistema: familia, escuela, barrio
    * Mesosistema: relaciones entre microsistemas
    * Exosistema: padres en trabajo, vecinos

ESTRUCTURA DE PERFIL POR NINO
=============================
Cada nino documenta 7 capas forenses:

1. Datos civiles: nombre, edad, grado escolar
2. Familia: con quien vive, relacion con padres/abuelos
3. Escuela: grado, rendimento, companeros clave
4. Rutina diaria: por hora (incluye escuela, juego, tareas)
5. Vinculos: mejores amigos, hermanos, primos
6. Conflictos: bullying, rivalidades, miedos
7. Voz tipica: muletillas, registro, temas de conversacion

USO
===
>>> from ninos_tello import NINOS, NINOS_POR_EDAD
>>> n = NINOS["maria_camila_perdomo"]
>>> n["edad"]
4
>>> n["rutina_diaria"][2]
('10:00', 'parque_infantil', 'jugar')
"""

# ===========================================================================
# 15 NINOS - TELLO, HUILA 2026
# ===========================================================================

NINOS = {
    # -----------------------------------------------------------------------
    # PREESCOLARES (4-5 ANOS)
    # -----------------------------------------------------------------------
    "maria_camila_perdomo": {
        "edad": 4,
        "genero": "femenino",
        "etapa_piaget": "preoperacional",
        "temperamento": "facil",
        "apego": "seguro",
        "grado": "preescolar",
        "familia": {
            "vive_con": ["abuelo_don_eliecer", "tio_jhon_eliecer"],
            "padres": "mama en Bogota (Rosalba), papa fallecio (accidente 2024)",
            "abuelos_paternos": ["don_eliecer_patron"],
            "hermanos": 0,
            "primos": ["jhonatan_perdomo"],
        },
        "escuela": {
            "jornada": "manana (7-12)",
            "docente": "auxiliar sin nombre",
            "amigos_clave": ["juan_esteban_quintero"],
        },
        "casa": "finca_matarredonda",
        "casa_coords": (-8, -2),
        "rutina_diaria": [
            ("06:00", "finca_matarredonda", "despertar con abuelo"),
            ("07:00", "ie_tello", "preescolar"),
            ("12:00", "finca_matarredonda", "almorzar"),
            ("13:00", "parque_infantil", "jugar"),
            ("16:00", "finca_matarredonda", "merienda con abuelo"),
            ("20:00", "finca_matarredonda", "dormir"),
        ],
        "conflictos": [
            "animo el abuelo Don Eliecer cuando Leonor (abuela) murio",
            "asustada cuando se murio un ternero",
        ],
        "voz_tipica": {
            "muletillas": ["abuelo", "y entonces?", "mira mira"],
            "registro": "infantil, 2-3 palabras por frase",
            "temas": "animales de la finca, abuelo, comida",
        },
        "metadata": {
            "fuente": "inferido_por_contexto",
            "confianza": 0.7,
            "notas": "Nieta del Patron. Huérfana de padre. Caso emocional.",
        },
    },

    "juan_esteban_quintero": {
        "edad": 5,
        "genero": "masculino",
        "etapa_piaget": "preoperacional",
        "temperamento": "lento_para_calentar",
        "apego": "ansioso",
        "grado": "preescolar",
        "familia": {
            "vive_con": ["abuela_dona_prudencia", "mama_adolescente"],
            "padres": "mama adolescente (17 anos), papa desconocido",
            "abuelos_paternos": ["dona_prudencia_partera"],
            "hermanos": 0,
            "primos": [],
        },
        "escuela": {
            "jornada": "manana (7-12)",
            "docente": "auxiliar sin nombre",
            "amigos_clave": ["maria_camila_perdomo"],
        },
        "casa": "casa_partera",
        "casa_coords": (-2, -3),
        "rutina_diaria": [
            ("06:30", "casa_partera", "despertar"),
            ("07:00", "ie_tello", "preescolar"),
            ("12:00", "casa_partera", "almorzar con abuela"),
            ("14:00", "casa_partera", "dormir siesta"),
            ("16:00", "parque_infantil", "jugar timido"),
            ("19:00", "casa_partera", "comer y dormir"),
        ],
        "conflictos": [
            "asustado cuando mama llora",
            "no sabe quien es su papa",
        ],
        "voz_tipica": {
            "muletillas": ["abuela", "...", "(mudo)"],
            "registro": "muy callado, mira mucho",
            "temas": "abuela, animales pequenos",
        },
        "metadata": {
            "fuente": "inferido_por_contexto",
            "confianza": 0.65,
            "notas": "Hijo de madre adolescente que Doña Prudencia saco adelante.",
        },
    },

    # -----------------------------------------------------------------------
    # PRIMARIA BAJA (6-9 ANOS)
    # -----------------------------------------------------------------------
    "sofia_vargas_trujillo": {
        "edad": 7,
        "genero": "femenino",
        "etapa_piaget": "operacional_concreto_inicial",
        "temperamento": "facil",
        "apego": "seguro",
        "grado": "2do primaria",
        "familia": {
            "vive_con": ["papa_caliche", "abuela_paterna"],
            "padres": "caliche (minero) soltero, mama murio en parto",
            "abuelos_paternos": ["sin_abuelo_paterno"],
            "hermanos": ["andres_felipe_vargas"],
            "primos": ["brayan_stiven_vargas"],
        },
        "escuela": {
            "jornada": "manana (7-12)",
            "docente": "profesora sin nombre",
            "amigos_clave": ["mateo_losada", "valentina_pinilla"],
        },
        "casa": "casa_caliche",
        "casa_coords": (-1, -2),
        "rutina_diaria": [
            ("05:30", "casa_caliche", "despertar"),
            ("06:00", "ie_tello", "escuela"),
            ("12:00", "casa_caliche", "almorzar"),
            ("13:00", "ie_tello", "tareas"),
            ("15:00", "parque_infantil", "jugar"),
            ("17:00", "tienda_dona_rosa", "mandado (comprar pan)"),
            ("19:00", "casa_caliche", "comer"),
        ],
        "conflictos": [
            "compania del padre ausente por trabajo en la mina",
            "amigos la molestan por papá minero",
        ],
        "voz_tipica": {
            "muletillas": ["mi papa", "(risitas)", "que mas!"],
            "registro": "habladora, curiosa",
            "temas": "motos, animales, manda de la tienda",
        },
        "metadata": {
            "fuente": "inferido_por_contexto",
            "confianza": 0.7,
            "notas": "Hija de Caliche. Callejera por necesidad (manda tienda).",
        },
    },

    "mateo_losada_pinilla": {
        "edad": 8,
        "genero": "masculino",
        "etapa_piaget": "operacional_concreto",
        "temperamento": "facil",
        "apego": "seguro",
        "grado": "3ro primaria",
        "familia": {
            "vive_con": ["mama_aurora_maestra", "papa_sin_datos"],
            "padres": "aurora (maestra) y esposo ausentista",
            "abuelos_paternos": [],
            "hermanos": ["sin_hermanos_menores"],
            "primos": ["daniela_ramirez"],
        },
        "escuela": {
            "jornada": "manana (7-12)",
            "docente": "mama_aurora",
            "amigos_clave": ["sofia_vargas", "samuel_suarez"],
            "problema": "amigos le dicen 'nerd' por estudiar mucho",
        },
        "casa": "casa_aurora",
        "casa_coords": (-3, 0),
        "rutina_diaria": [
            ("06:00", "casa_aurora", "despertar"),
            ("07:00", "ie_tello", "escuela"),
            ("12:00", "casa_aurora", "almorzar con mama"),
            ("13:00", "casa_aurora", "tareas"),
            ("15:00", "parque_infantil", "jugar"),
            ("17:00", "ie_tello", "tareas extra con mama"),
            ("19:00", "casa_aurora", "comer"),
        ],
        "conflictos": [
            "bullied por ser estudioso",
            "papá no vive con ellos",
        ],
        "voz_tipica": {
            "muletillas": ["mama dice", "pero si...", "profe..."],
            "registro": "educado, inseguro",
            "temas": "escuela, libros, tareas",
        },
        "metadata": {
            "fuente": "inferido_por_contexto",
            "confianza": 0.7,
            "notas": "Hijo de la maestra. Víctima de bullying.",
        },
    },

    "valentina_pinilla": {
        "edad": 6,
        "genero": "femenino",
        "etapa_piaget": "operacional_concreto_inicial",
        "temperamento": "facil",
        "apego": "seguro",
        "grado": "1ro primaria",
        "familia": {
            "vive_con": ["mama_dona_mercedes", "papa_don_abelardo"],
            "padres": "mercedes (panadera) y abelardo (conductor)",
            "abuelos_paternos": [],
            "hermanos": 0,
            "primos": [],
        },
        "escuela": {
            "jornada": "manana (7-12)",
            "docente": "profesora sin nombre",
            "amigos_clave": ["sofia_vargas"],
        },
        "casa": "panaderia_mercedes",
        "casa_coords": (-1, 2),
        "rutina_diaria": [
            ("04:30", "panaderia_mercedes", "despertar con mama"),
            ("05:00", "panaderia_mercedes", "ayudar a amasar"),
            ("07:00", "ie_tello", "escuela"),
            ("12:00", "panaderia_mercedes", "almorzar"),
            ("13:00", "ie_tello", "tareas"),
            ("15:00", "panaderia_mercedes", "ayudar a vender"),
            ("20:00", "panaderia_mercedes", "comer y dormir"),
        ],
        "conflictos": [
            "cansada de madrugar",
            "quiere jugar mas",
        ],
        "voz_tipica": {
            "muletillas": ["mama", "pan!", "tengo sueno"],
            "registro": "infantil, directa",
            "temas": "pan, escuelita, jugar",
        },
        "metadata": {
            "fuente": "inferido_por_contexto",
            "confianza": 0.7,
            "notas": "Ayudante infantil en la panaderia. Caso de trabajo infantil leve.",
        },
    },

    "samuel_suarez_trujillo": {
        "edad": 9,
        "genero": "masculino",
        "etapa_piaget": "operacional_concreto",
        "temperamento": "facil",
        "apego": "seguro",
        "grado": "4to primaria",
        "familia": {
            "vive_con": ["papa_don_emigdio", "mama_sin_datos"],
            "padres": "emigdio (jubilado) y esposa",
            "abuelos_paternos": [],
            "hermanos": ["yulieth_andrea_suarez"],
            "primos": [],
        },
        "escuela": {
            "jornada": "manana (7-12)",
            "docente": "profesora sin nombre",
            "amigos_clave": ["mateo_losada"],
            "interes": "motos",
        },
        "casa": "casa_emigdio",
        "casa_coords": (2, -1),
        "rutina_diaria": [
            ("06:00", "casa_emigdio", "despertar"),
            ("07:00", "ie_tello", "escuela"),
            ("12:00", "casa_emigdio", "almorzar"),
            ("13:00", "taberna_la_mocha", "ayudar al padre"),
            ("16:00", "estadio_municipal", "jugar futbol"),
            ("20:00", "taberna_la_mocha", "comer con papa"),
        ],
        "conflictos": [
            "expuesto a alcoholismo del padre",
            "peleas en la escuela por tomar partido de grupos",
        ],
        "voz_tipica": {
            "muletillas": ["mi papa", "(chistoso)", "mire!"],
            "registro": "hablador, callejero",
            "temas": "motos, fútbol, papá",
        },
        "metadata": {
            "fuente": "inferido_por_contexto",
            "confianza": 0.7,
            "notas": "Hijo del jubilado que pasa el dia en la taberna. Caso de riesgo.",
        },
    },

    # -----------------------------------------------------------------------
    # PRIMARIA ALTA (10-12 ANOS)
    # -----------------------------------------------------------------------
    "daniela_ramirez_perdomo": {
        "edad": 11,
        "genero": "femenino",
        "etapa_piaget": "operacional_concreto",
        "temperamento": "facil",
        "apego": "seguro",
        "grado": "6to primaria",
        "familia": {
            "vive_con": ["mama_auxiliar_enfermeria", "papa_sin_datos"],
            "padres": "madre soltera, padre ausente",
            "abuelos_paternos": [],
            "hermanos": 0,
            "primos": ["mateo_losada"],
        },
        "escuela": {
            "jornada": "manana (7-12)",
            "docente": "profesora sin nombre",
            "rol": "lider del grupo",
            "amigos_clave": ["camila_andrea_meneses", "sofia_vargas"],
        },
        "casa": "casa_daniela",
        "casa_coords": (-3, 2),
        "rutina_diaria": [
            ("06:00", "casa_daniela", "despertar"),
            ("07:00", "ie_tello", "escuela"),
            ("12:00", "casa_daniela", "almorzar"),
            ("13:00", "ie_tello", "tareas"),
            ("15:00", "parque_infantil", "liderar grupo"),
            ("19:00", "casa_daniela", "comer"),
        ],
        "conflictos": [
            "presion de grupo sobre amiguitos",
            "discute con Camila por chicos",
        ],
        "voz_tipica": {
            "muletillas": ["las nenas", "yo digo que", "obvio"],
            "registro": "mandona, social",
            "temas": "chismes de colegio, chicos, moda",
        },
        "metadata": {
            "fuente": "inferido_por_contexto",
            "confianza": 0.65,
            "notas": "Lider natural del grupo de chicas. Super-spreader infantil.",
        },
    },

    "andres_felipe_vargas": {
        "edad": 10,
        "genero": "masculino",
        "etapa_piaget": "operacional_concreto",
        "temperamento": "dificil",
        "apego": "evitativo",
        "grado": "5to primaria",
        "familia": {
            "vive_con": ["abuela_paterna", "primo_brayan"],
            "padres": "caliche ausente, mama en Neiva",
            "abuelos_paternos": [],
            "hermanos": ["sofia_vargas_trujillo"],
            "primos": ["brayan_stiven_vargas"],
        },
        "escuela": {
            "jornada": "manana (7-12)",
            "docente": "profesora sin nombre",
            "problema": "mal rendimiento, peleas",
            "amigos_clave": ["brayan_stiven_vargas"],
        },
        "casa": "casa_caliche",
        "casa_coords": (-1, -2),
        "rutina_diaria": [
            ("07:00", "ie_tello", "escuela (a veces falta)"),
            ("12:00", "casa_caliche", "almorzar"),
            ("14:00", "calle", "callejear"),
            ("18:00", "casa_caliche", "comer"),
        ],
        "conflictos": [
            "problemas de conducta",
            "sigue a primo Brayan (pandilla)",
        ],
        "voz_tipica": {
            "muletillas": ["(groserias)", "que importa"],
            "registro": "agresivo, huraño",
            "temas": "calle, primo, plata",
        },
        "metadata": {
            "fuente": "inferido_por_contexto",
            "confianza": 0.7,
            "notas": "Hermano de Sofia, primo de Brayan. Caso de riesgo medio.",
        },
    },

    "camila_andrea_meneses": {
        "edad": 12,
        "genero": "femenino",
        "etapa_piaget": "operacional_concreto_final",
        "temperamento": "facil",
        "apego": "seguro",
        "grado": "7mo (1ro bachillerato)",
        "familia": {
            "vive_con": ["tia_laura_reina", "tio_sin_datos"],
            "padres": "mama en Bogota, papa fallecido",
            "abuelos_paternos": [],
            "hermanos": 0,
            "primos": ["laura_reina_sobrina"],
        },
        "escuela": {
            "jornada": "manana (7-12)",
            "docente": "profesor sin nombre",
            "rol": "rebelde, contestataria",
            "amigos_clave": ["daniela_ramirez"],
        },
        "casa": "casa_laura",
        "casa_coords": (0, -1),
        "rutina_diaria": [
            ("06:00", "casa_laura", "despertar"),
            ("07:00", "ie_tello", "bachillerato"),
            ("12:00", "casa_laura", "almorzar"),
            ("13:00", "ie_tello", "tareas"),
            ("15:00", "plaza_bolivar", "socializar"),
            ("17:00", "casa_laura", "ayudar a tia"),
            ("20:00", "casa_laura", "comer"),
        ],
        "conflictos": [
            "discute mucho con tía Laura",
            "quiere irse a Neiva a estudiar",
        ],
        "voz_tipica": {
            "muletillas": ["tia", "que pereza", "yo me voy"],
            "registro": "adolescente, rebelde",
            "temas": "irse a Neiva, chicos, reggaeton",
        },
        "metadata": {
            "fuente": "inferido_por_contexto",
            "confianza": 0.65,
            "notas": "Sobrina de la Reina. Caso de emigración juvenil.",
        },
    },

    # -----------------------------------------------------------------------
    # SECUNDARIA (13-17 ANOS)
    # -----------------------------------------------------------------------
    "brayan_stiven_vargas": {
        "edad": 14,
        "genero": "masculino",
        "etapa_piaget": "operacional_formal_inicial",
        "temperamento": "dificil",
        "apego": "evitativo",
        "grado": "8vo (2do bachillerato)",
        "familia": {
            "vive_con": ["abuela_paterna", "tio_caliche_a_veces"],
            "padres": "padre en otra vereda, mama ausente",
            "abuelos_paternos": [],
            "hermanos": 0,
            "primos": ["andres_felipe_vargas", "sofia_vargas"],
        },
        "escuela": {
            "jornada": "manana (7-12)",
            "docente": "profesor sin nombre",
            "problema": "repetidor, problemas con drogas",
            "amigos_clave": ["andres_felipe_vargas"],
        },
        "casa": "casa_caliche",
        "casa_coords": (-1, -2),
        "rutina_diaria": [
            ("09:00", "ie_tello", "escuela (cuando va)"),
            ("12:00", "calle", "callejear"),
            ("15:00", "taberna_la_mocha", "tomar"),
            ("17:00", "cancha_multiple", "futbol"),
            ("22:00", "calle", "rumba"),
        ],
        "conflictos": [
            "pandilla juvenil",
            "consumo de sustancias",
            "rivalidad con Michael Steven",
        ],
        "voz_tipica": {
            "muletillas": ["(vulgaridades)", "parce", "no joda"],
            "registro": "callejero, hostil",
            "temas": "drogas, futbol, peleas",
        },
        "metadata": {
            "fuente": "inferido_por_contexto",
            "confianza": 0.75,
            "notas": "Caso problematico. Pandilla, posible consumo. Vecino de Yulieth (novia).",
        },
    },

    "laura_valentina_trujillo": {
        "edad": 13,
        "genero": "femenino",
        "etapa_piaget": "operacional_formal_inicial",
        "temperamento": "facil",
        "apego": "seguro",
        "grado": "8vo",
        "familia": {
            "vive_con": ["papa_don_sigifredo", "mama_sin_datos"],
            "padres": "sigifredo (inspector) y esposa",
            "abuelos_paternos": [],
            "hermanos": 0,
            "primos": [],
        },
        "escuela": {
            "jornada": "manana (7-12)",
            "docente": "profesor sin nombre",
            "rol": "estudiosa, intenta ayudar a papá",
            "amigos_clave": ["daniela_ramirez"],
        },
        "casa": "casa_sigifredo",
        "casa_coords": (-3, -2),
        "rutina_diaria": [
            ("05:30", "casa_sigifredo", "despertar"),
            ("07:00", "ie_tello", "bachillerato"),
            ("12:00", "casa_sigifredo", "almorzar"),
            ("13:00", "casa_sigifredo", "estudiar"),
            ("16:00", "inspeccion", "ayudar a papá"),
            ("20:00", "casa_sigifredo", "comer"),
        ],
        "conflictos": [
            "sabe que papá favorece al Patrón",
            "discute con él por ética",
        ],
        "voz_tipica": {
            "muletillas": ["papa", "eso no esta bien", "necio"],
            "registro": "juiciosa, adolescente",
            "temas": "escuela, etica, chicos",
        },
        "metadata": {
            "fuente": "inferido_por_contexto",
            "confianza": 0.7,
            "notas": "Hija del Inspector. Caso etico: hija descubre favoritismo del padre.",
        },
    },

    "jhonatan_perdomo": {
        "edad": 16,
        "genero": "masculino",
        "etapa_piaget": "operacional_formal",
        "temperamento": "facil",
        "apego": "seguro",
        "grado": "10mo (4to bachillerato)",
        "familia": {
            "vive_con": ["abuelo_don_eliecer", "tio_jhon_eliecer"],
            "padres": "padre en Bogota, mama fallecida",
            "abuelos_paternos": ["don_eliecer_patron"],
            "hermanos": 0,
            "primos": ["maria_camila_perdomo"],
        },
        "escuela": {
            "jornada": "manana (7-12)",
            "docente": "profesor sin nombre",
            "problema": "abandona para trabajar en finca",
            "amigos_clave": ["michael_steven_quintero"],
        },
        "casa": "finca_matarredonda",
        "casa_coords": (-8, -2),
        "rutina_diaria": [
            ("05:00", "finca_matarredonda", "trabajar"),
            ("07:00", "ie_tello", "escuela (faltas frecuentes)"),
            ("12:00", "finca_matarredonda", "almorzar"),
            ("13:00", "finca_matarredonda", "trabajar"),
            ("18:00", "finca_matarredonda", "comer"),
        ],
        "conflictos": [
            "rivalidad con Michael Steven por Yulieth",
            "no quiere estudiar, prefiere trabajo",
        ],
        "voz_tipica": {
            "muletillas": ["abuelo", "el trabajo", "la tierra"],
            "registro": "adulto, austero",
            "temas": "ganaderia, finca, chica",
        },
        "metadata": {
            "fuente": "inferido_por_contexto",
            "confianza": 0.75,
            "notas": "Nieto del Patron. Continuador del negocio familiar. Caso de desercion.",
        },
    },

    "yulieth_andrea_suarez": {
        "edad": 15,
        "genero": "femenino",
        "etapa_piaget": "operacional_formal",
        "temperamento": "facil",
        "apego": "ansioso",
        "grado": "9no (3ro bachillerato)",
        "familia": {
            "vive_con": ["papa_don_emigdio", "mama_sin_datos"],
            "padres": "emigdio (jubilado, alcoholico) y esposa",
            "abuelos_paternos": [],
            "hermanos": ["samuel_suarez"],
            "primos": [],
        },
        "escuela": {
            "jornada": "manana (7-12)",
            "docente": "profesor sin nombre",
            "problema": "rendimiento bajo por novio problematico",
            "amigos_clave": ["daniela_ramirez"],
        },
        "casa": "casa_emigdio",
        "casa_coords": (2, -1),
        "rutina_diaria": [
            ("06:00", "casa_emigdio", "despertar"),
            ("07:00", "ie_tello", "bachillerato"),
            ("12:00", "casa_emigdio", "almorzar"),
            ("13:00", "taberna_la_mocha", "juntarse con Brayan"),
            ("18:00", "casa_emigdio", "comer"),
        ],
        "conflictos": [
            "novia de Brayan (pandilla)",
            "papá alcoholico",
            "pelea con Michael por Brayan",
        ],
        "voz_tipica": {
            "muletillas": ["Brayan", "mi papa", "(llora)"],
            "registro": "adolescente insegura",
            "temas": "novio, papá, conflictos",
        },
        "metadata": {
            "fuente": "inferido_por_contexto",
            "confianza": 0.75,
            "notas": "Novia de Brayan. Caso de pareja adolescente problematico.",
        },
    },

    "michael_steven_quintero": {
        "edad": 17,
        "genero": "masculino",
        "etapa_piaget": "operacional_formal",
        "temperamento": "dificil",
        "apego": "evitativo",
        "grado": "11mo (5to bachillerato, ultimo)",
        "familia": {
            "vive_con": ["papa_don_rosalio", "mama_sin_datos"],
            "padres": "rosalio (ganadero) y esposa",
            "abuelos_paternos": [],
            "hermanos": 0,
            "primos": [],
        },
        "escuela": {
            "jornada": "manana (7-12)",
            "docente": "profesor sin nombre",
            "rol": "problematico, golpea",
            "amigos_clave": ["jhonatan_perdomo"],
        },
        "casa": "finca_quintero",
        "casa_coords": (-9, -1),
        "rutina_diaria": [
            ("05:00", "finca_quintero", "trabajar"),
            ("07:00", "ie_tello", "bachillerato"),
            ("12:00", "finca_quintero", "almorzar"),
            ("13:00", "finca_quintero", "trabajar"),
            ("18:00", "taberna_la_mocha", "tomar"),
        ],
        "conflictos": [
            "rivalidad con Jhonatan Perdomo (amor + linderos)",
            "violento, problema con personera",
        ],
        "voz_tipica": {
            "muletillas": ["mi papa", "(amenazas)", "le doy"],
            "registro": "agresivo, territorial",
            "temas": "ganaderia, Yulieth, Jhonatan",
        },
        "metadata": {
            "fuente": "inferido_por_contexto",
            "confianza": 0.75,
            "notas": "Hijo de Rosalío (rival). Caso de violencia + triangulo amoroso.",
        },
    },

    "karol_tatiana_losada": {
        "edad": 17,
        "genero": "femenino",
        "etapa_piaget": "operacional_formal",
        "temperamento": "facil",
        "apego": "seguro",
        "grado": "11mo (ultimo)",
        "familia": {
            "vive_con": ["mama_sin_datos", "papa_sin_datos"],
            "padres": "padres profesionales (familia Losada)",
            "abuelos_paternos": [],
            "hermanos": 0,
            "primos": ["patricia_comisaria"],
        },
        "escuela": {
            "jornada": "manana (7-12)",
            "docente": "profesor sin nombre",
            "rol": "excelencia academica",
            "amigos_clave": ["laura_valentina_trujillo"],
        },
        "casa": "casa_losada",
        "casa_coords": (-1, 3),
        "rutina_diaria": [
            ("05:00", "casa_losada", "despertar"),
            ("06:00", "bus_neiva", "viajar a U. Surcolombiana"),
            ("18:00", "casa_losada", "regresar"),
            ("20:00", "casa_losada", "estudiar"),
        ],
        "conflictos": [
            "quiere irse a Bogota a estudiar medicina",
            "diferencia de clase con compaeros",
        ],
        "voz_tipica": {
            "muletillas": ["mami", "necesito estudiar", "(seria)"],
            "registro": "seria, academica",
            "temas": "universidad, medicina, salir del pueblo",
        },
        "metadata": {
            "fuente": "inferido_por_contexto",
            "confianza": 0.7,
            "notas": "Hija de Losada. Caso de movilidad social por educacion.",
        },
    },
}


# ===========================================================================
# UTILIDADES
# ===========================================================================

def ninos_por_edad():
    """Agrupa ninos por edad."""
    por_edad = {}
    for slug, n in NINOS.items():
        edad = n["edad"]
        por_edad.setdefault(edad, []).append(slug)
    return por_edad


def ninos_por_etapa():
    """Agrupa ninos por etapa Piaget."""
    por_etapa = {}
    for slug, n in NINOS.items():
        etapa = n["etapa_piaget"]
        por_etapa.setdefault(etapa, []).append(slug)
    return por_etapa


def ninos_por_escuela():
    """Agrupa ninos por lugar donde pasan la manana."""
    por_escuela = {}
    for slug, n in NINOS.items():
        # Buscar el item de la rutina donde dice 'ie_tello'
        lugar_escuela = "fuera_de_escuela"
        for hora, lugar, accion in n["rutina_diaria"]:
            if "ie_tello" in lugar:
                lugar_escuela = lugar
                break
        por_escuela.setdefault(lugar_escuela, []).append(slug)
    return por_escuela


def ninos_por_temperamento():
    """Agrupa ninos por temperamento Thomas & Chess."""
    por_temp = {}
    for slug, n in NINOS.items():
        temp = n["temperamento"]
        por_temp.setdefault(temp, []).append(slug)
    return por_temp


def ninos_geo():
    """Devuelve dict slug -> coords para todos los ninos."""
    return {slug: n["casa_coords"] for slug, n in NINOS.items()}


if __name__ == "__main__":
    print(f"Ninos catalogados: {len(NINOS)}")
    print()
    print("Por edad:")
    for edad in sorted(ninos_por_edad().keys()):
        ns = ninos_por_edad()[edad]
        print(f"  {edad} anos: {len(ns)} ninos - {ns}")
    print()
    print("Por etapa Piaget:")
    for etapa, ns in ninos_por_etapa().items():
        print(f"  {etapa}: {len(ns)} - {ns}")
    print()
    print("Por temperamento:")
    for t, ns in ninos_por_temperamento().items():
        print(f"  {t}: {len(ns)} - {ns}")
    print()
    print("Total ninos: {}".format(sum(len(v) for v in ninos_por_edad().values())))
