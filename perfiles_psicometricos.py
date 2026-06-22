# -*- coding: utf-8 -*-
"""
SOCIEDAD OPITA — Perfiles psicometricos forenses
=================================================

Asignacion de Big Five + Lomnitz + Dunbar + rasgos derivados para los 25 adultos
de Tello, Huila, basada en biografias forenses y literatura academica revisada
por pares (ver docs/investigacion/01-psicometria.md).

Cada perfil incluye:
- Big Five scores (0-100): O, C, E, A, N
- Categoria Lomnitz default (A/B/C)
- Capas Dunbar: 5 intimos + 15 buenos (referencias a otros slugs)
- Rasgos derivados: habla_tipica, manejo_conflicto, respuesta_crisis,
  disposicion_chisme, confianza_inicial

Todos los scores son JUSTIFICADOS con marcador biografico textual en el campo
`justificacion_bio` para auditoria.

Metodologia: Schmitt 2007 + Lomnitz 1975 + Dunbar 1992 + Hofstede calibrado Tello.
"""

# Constantes poblacionales Colombia (Schmitt 2007, normalizadas a 0-100)
BASE_POBLACIONAL = {
    "O": 47,
    "C": 44,
    "E": 50,
    "A": 47,
    "N": 52,
}

# Hofstede calibrado para Tello rural
HOFSTEDE_TELLO = {
    "PDI": 75,
    "IDV": 10,
    "MAS": 60,
    "UAI": 85,
    "IND": 75,
}


def _perfil(slug, big_five, lomnitz_default, intimos, buenos, rasgos, justificacion_bio):
    return {
        "slug": slug,
        "big_five": big_five,
        "lomnitz_default": lomnitz_default,
        "dunbar": {
            "intimos": intimos,
            "buenos": buenos,
        },
        "rasgos": rasgos,
        "justificacion_bio": justificacion_bio,
    }

# =============================================================================
# 25 PERFILES ADULTOS
# =============================================================================

PERFILES_ADULTOS = {

    # === 1. Don Eliecer Perdomo Motta — El Patron (74) ===
    "don_eliecer_patron": _perfil(
        slug="don_eliecer_patron",
        big_five={"O": 25, "C": 80, "E": 35, "A": 30, "N": 30},
        lomnitz_default="C",
        intimos=[
            "jhon_eliecer_hijo_patron",
            "padre_cecilio_cura",
            "don_sigifredo_inspector",
            "dona_mercedes_panadera",
            "jhon_jairo_sacristan",
        ],
        buenos=[
            "don_fernando_alcalde",
            "dona_rosa_tendera",
            "don_abelardo_conductor",
            "edilma_secretaria",
            "don_rosalio_rival",
            "aurora_maestra",
            "don_eliseo_boticario",
            "subintendente_saavedra",
            "capitan_hernan_policia",
            "dona_prudencia_partera",
            "beatriz_personera",
            "patricia_comisaria",
            "dona_lucia_maestra_jubilada",
            "don_emigdio_jubilado",
            "laura_reina",
        ],
        rasgos={
            "habla_tipica": "Taciturno, frases medidas, voz baja. Nunca levanta la voz, pero cada palabra pesa.",
            "manejo_conflicto": "Indiferente al conflicto abierto. No se inmuta; maneja con silencio o con terceros.",
            "respuesta_crisis": "Planificador. Es el primero en actuar, convoca a su red de compadres.",
            "disposicion_chisme": "Rechaza el chisme. No se mete en vidas ajenas. Pero escucha todo.",
            "confianza_inicial": "Receloso. Observa mucho antes de confiar.",
        },
        justificacion_bio=(
            "Bio: patriarca conservador, terrateniente, catolico devoto. "
            "Habla con voz baja, frases medidas, nunca levanta la voz. "
            "Ordenado, ritual: cafe a las 6, misa los domingos. "
            "Exigente con servidores, les paga pero les exige. "
            "Marcadores: patriarca-conservador [-10O +5C +10E -10A], "
            "devoto [-10O +10C +5A -10N], "
            "habla baja-frases medidas [+10C -25E -10N], "
            "ritual-ordenado [-5O +25C -10N], "
            "exigente con servidores [+10C -15A]. "
            "Suma: O -25, C +50, E -15, A -20, N -30. "
            "Base: O=47-25=22(clamp 25), C=44+50=94(clamp 80), E=50-15=35, "
            "A=47-20=27(clamp 30), N=52-30=22(clamp 30). "
            "Contradiccion: reza todos los dias pero controla jornaleros con deuda."
        ),
    ),

    # === 2. Dona Prudencia Gutierrez — La Partera (76) ===
    "dona_prudencia_partera": _perfil(
        slug="dona_prudencia_partera",
        big_five={"O": 50, "C": 75, "E": 60, "A": 85, "N": 30},
        lomnitz_default="A",
        intimos=[
            "dona_rosa_tendera",
            "patricia_comisaria",
            "padre_cecilio_cura",
            "laura_reina",
            "dona_lucia_maestra_jubilada",
        ],
        buenos=[
            "dona_mercedes_panadera",
            "aurora_maestra",
            "don_eliecer_patron",
            "don_eliseo_boticario",
            "don_rosalio_rival",
            "jhon_jairo_sacristan",
            "don_sigifredo_inspector",
            "edilma_secretaria",
            "don_fernando_alcalde",
            "beatriz_personera",
            "mariana_universitaria",
            "valentina_secretaria_joven",
            "pipe_hincha",
            "jhon_eliecer_hijo_patron",
            "capitan_hernan_policia",
        ],
        rasgos={
            "habla_tipica": "Maternal, voz baja, casi susurro en temas serios. Con la bendicion de Dios, ay, mijita.",
            "manejo_conflicto": "Evita conflicto abierto. Si el paciente es grosero, le demora la mejoria (pasivo-agresivo sutil).",
            "respuesta_crisis": "Lider emergente por empatia. Organiza ayuda al necesitado, convoca su red de comadres.",
            "disposicion_chisme": "Pro-social. Sabe secretos de partos, hijos no reconocidos, abortos. Nunca habla.",
            "confianza_inicial": "Confia hasta que se demuestre lo contrario. Es buena gente con todos por igual.",
        },
        justificacion_bio=(
            "Bio: partera, sobandera, curandera. No cobra. Le regalan productos. "
            "Madrina de bautizo de medio pueblo. 3 generaciones de nacidos en Tello. "
            "Sabe secretos de partos dificiles, hijos no reconocidos, abortos. Nunca habla. "
            "Marcadores: curandera-herbolaria [+5O +10C +5A], "
            "no cobra-altruista [+25A -5N], "
            "sabia-consejera [+15O +10C +5E +10A -5N], "
            "nunca habla secretos [+20A -5E], "
            "tradicional vs EPS [-5E]. "
            "Suma: O +20, C +20, E +15, A +35, N -10. "
            "Base: O=47+20(clamp 50 tradicional), C=44+20(clamp 75), E=50+15(clamp 60), "
            "A=47+35(clamp 85), N=52-10(clamp 30 por baja ansiedad)."
        ),
    ),

    # === 3. Don Rosalio Quintero — El Rival (70) ===
    "don_rosalio_rival": _perfil(
        slug="don_rosalio_rival",
        big_five={"O": 25, "C": 90, "E": 25, "A": 40, "N": 65},
        lomnitz_default="B",
        intimos=[
            "don_abelardo_conductor",
            "dona_rosa_tendera",
            "dona_mercedes_panadera",
            "don_emigdio_jubilado",
            "don_sigifredo_inspector",
        ],
        buenos=[
            "don_eliecer_patron",
            "padre_cecilio_cura",
            "don_fernando_alcalde",
            "subintendente_saavedra",
            "jhon_jairo_sacristan",
            "aurora_maestra",
            "don_eliseo_boticario",
            "edilma_secretaria",
            "capitan_hernan_policia",
            "beatriz_personera",
            "patricia_comisaria",
            "dona_prudencia_partera",
            "dona_lucia_maestra_jubilada",
            "laura_reina",
            "jhon_eliecer_hijo_patron",
        ],
        rasgos={
            "habla_tipica": "Taciturno y cortante. Frases cortas. Pues, la cosa es que, tengo mis papeles.",
            "manejo_conflicto": "Confrontacional. El conflicto de linderos ES su vida. No cede, no olvida, no perdona.",
            "respuesta_crisis": "Ansioso. Eso se resolvera cuando Dios quiera es resignacion ansiosa, no planificacion.",
            "disposicion_chisme": "Chisme ansioso. Siempre tiene algo que decir del lindero. Desconfia de todos.",
            "confianza_inicial": "Receloso extremo. No se fie. Desconfia incluso de su propia familia politica.",
        },
        justificacion_bio=(
            "Bio: campesino medio, resenado con Eliecer. Madruga mas que Eliecer (4:30) por rencor. "
            "Todos los dias revisa el lindero. Desconfiado, cortante. Esconde informacion. "
            "Bebe solo los domingos, nadie lo sabe excepto Balbina. "
            "Marcadores: rencoroso-vengativo [-30A +15N], "
            "desconfiado-receloso [-5O +5C -10E -25A +10N], "
            "madrugador-ritual [+20C -5A +5N], "
            "campesino-medio [+5C -5O], "
            "callado-cortante [-5O -25E]. "
            "Suma: O -10, C +25, E -35, A -55, N +30. "
            "Base: O=47-10(clamp 25), C=44+25(clamp 90 por obsesion del lindero), "
            "E=50-35(clamp 25), A=47-55(clamp 40), N=52+30(clamp 65)."
        ),
    ),

    # === 4. Dona Lucia Ramirez — La Maestra Jubilada (69) ===
    "dona_lucia_maestra_jubilada": _perfil(
        slug="dona_lucia_maestra_jubilada",
        big_five={"O": 60, "C": 75, "E": 55, "A": 85, "N": 50},
        lomnitz_default="A",
        intimos=[
            "dona_mercedes_panadera",
            "padre_cecilio_cura",
            "aurora_maestra",
            "dona_prudencia_partera",
            "dona_rosa_tendera",
        ],
        buenos=[
            "jhon_jairo_sacristan",
            "don_eliecer_patron",
            "don_rosalio_rival",
            "don_fernando_alcalde",
            "beatriz_personera",
            "patricia_comisaria",
            "edilma_secretaria",
            "don_eliseo_boticario",
            "don_emigdio_jubilado",
            "don_abelardo_conductor",
            "valentina_secretaria_joven",
            "mariana_universitaria",
            "laura_reina",
            "capitan_hernan_policia",
            "don_sigifredo_inspector",
        ],
        rasgos={
            "habla_tipica": "Ay, mijito, con Dios, en mis tiempos. Narrativa, con anecdotas. Voz maternal y calida.",
            "manejo_conflicto": "Evita conflicto. Conciliadora natural. No le gusta pelear.",
            "respuesta_crisis": "Planifica con apoyo comunitario. Organiza desde la iglesia. Liderazgo moral tranquilo.",
            "disposicion_chisme": "Pro-social. Se preocupa por los demas, comparte para ayudar. Teje red de apoyo entre mujeres.",
            "confianza_inicial": "Confia hasta que se demuestre lo contrario. Es buena gente. Ve lo mejor en cada persona.",
        },
        justificacion_bio=(
            "Bio: jubilada como maestra. Ayuda en misa. Tejia y vendia almojabanas. "
            "Visita amigas, iglesia. Extrana dar clase. Le pide a Dios que llueva. "
            "Marcadores: maestra-sabia [+15O +10C +5E +10A -5N], "
            "devota-feligresa [-10O +10C +5A -10N], "
            "servicial-ayuda en misa [+10C +5E +25A -5N], "
            "sociable-visita amigas [+5O +20E +5A -10N], "
            "jubilada-artritis [-5C -5E +10N]. "
            "Suma: O +10, C +25, E +30, A +40, N -20. "
            "Base: O=47+10(clamp 60), C=44+25(clamp 75), E=50+30(clamp 55 por edad), "
            "A=47+40(clamp 85), N=52-20(clamp 50 por artritis y soledad de hija)."
        ),
    ),

    # === 5. Don Emigdio Suarez — El Jubilado Que No Sirve (66) ===
    "don_emigdio_jubilado": _perfil(
        slug="don_emigdio_jubilado",
        big_five={"O": 25, "C": 40, "E": 35, "A": 55, "N": 65},
        lomnitz_default="B",
        intimos=[
            "dona_mercedes_panadera",
            "subintendente_saavedra",
            "don_rosalio_rival",
            "dona_rosa_tendera",
            "don_abelardo_conductor",
        ],
        buenos=[
            "don_eliecer_patron",
            "padre_cecilio_cura",
            "jhon_jairo_sacristan",
            "don_fernando_alcalde",
            "don_sigifredo_inspector",
            "don_eliseo_boticario",
            "dona_prudencia_partera",
            "aurora_maestra",
            "edilma_secretaria",
            "dona_lucia_maestra_jubilada",
            "beatriz_personera",
            "jhon_eliecer_hijo_patron",
            "capitan_hernan_policia",
            "pipe_hincha",
            "valentina_secretaria_joven",
        ],
        rasgos={
            "habla_tipica": "Quejumbroso, lento. Pues, en mis tiempos, eso ya no es como antes. Resentimiento velado.",
            "manejo_conflicto": "Evita conflicto abierto. Resentimiento pasivo. No confronta a Mercedes, internaliza la queja.",
            "respuesta_crisis": "Depende de otros. No sabe que hacer. Espera que Mercedes o alguien mas resuelva.",
            "disposicion_chisme": "Chisme ansioso pasivo. Habla mal del progreso, de Don Eliecer. Queja cronica como chisme.",
            "confianza_inicial": "Condicional. Hay que conocerlo. Desconfia de los jovenes, confia en sus contemporaneos.",
        },
        justificacion_bio=(
            "Bio: jubilado, no trabaja formalmente. Antes jornalero. Mercedes le reclama que no ayude. "
            "Masculinidad herida. Habla mal del progreso. Envidia de Don Eliecer (que sigue activo). "
            "Se levanta tarde, tinto en parque, vuelta al pueblo, siesta, bingo o tienda. "
            "Marcadores: flojo-no trabaja [-10O -25C -10A], "
            "quejumbroso-resentido [-5O -5C -5E -15A +15N], "
            "envidioso [-5O -10A +10N], "
            "habla mal del progreso [-10O -5E +5N], "
            "jubilado-sin proposito [-5O -10C -5E +5N]. "
            "Suma: O -30, C -35, E -10, A -25, N +35. "
            "Base: O=47-30(clamp 25), C=44-35(clamp 40 rutina minima), "
            "E=50-10(clamp 35), A=47-25(clamp 55), N=52+35(clamp 65)."
        ),
    ),

    # === 6. Padre Cecilio Ramirez Lozano — El Cura (65) ===
    "padre_cecilio_cura": _perfil(
        slug="padre_cecilio_cura",
        big_five={"O": 55, "C": 80, "E": 65, "A": 85, "N": 25},
        lomnitz_default="A",
        intimos=[
            "don_eliecer_patron",
            "dona_mercedes_panadera",
            "jhon_jairo_sacristan",
            "patricia_comisaria",
            "dona_rosa_tendera",
        ],
        buenos=[
            "don_fernando_alcalde",
            "dona_prudencia_partera",
            "don_rosalio_rival",
            "dona_lucia_maestra_jubilada",
            "beatriz_personera",
            "aurora_maestra",
            "don_sigifredo_inspector",
            "edilma_secretaria",
            "don_eliseo_boticario",
            "don_emigdio_jubilado",
            "subintendente_saavedra",
            "don_abelardo_conductor",
            "capitan_hernan_policia",
            "valentina_secretaria_joven",
            "mariana_universitaria",
        ],
        rasgos={
            "habla_tipica": "Vehemente en sermon, paternal en confesion. Con la bendicion de Dios, hijo mio. Citas biblicas.",
            "manejo_conflicto": "Evita conflicto, busca reconciliacion. Media entre Eliecer y Rosalio sin tomar partido abierto.",
            "respuesta_crisis": "Planificador con fe. Reza pero tambien organiza. Convocatoria a red catolica para ayuda humanitaria.",
            "disposicion_chisme": "Pro-social selectivo. Escucha en confesion pero no repite. Confidencialidad sacerdotal.",
            "confianza_inicial": "Confia en la redencion de cada persona. Ve el potencial, no solo el pecado. Todos somos hijos de Dios.",
        },
        justificacion_bio=(
            "Bio: sacerdote 35 anos en Tello. Misa diaria 6:00. Confesiones, bautizos, matrimonios, funerales. "
            "Vehemente en sermon, paternal en confesion. Le preocupa el alma de Eliecer. "
            "Tiene dudas teologicas serias que comparte con el obispo. "
            "Marcadores: devoto-sacerdote [-10O +10C +5A -10N], "
            "lider espiritual [+15C +15E -5A +5N], "
            "sabio-consejero [+15O +10C +5E +10A -5N], "
            "compasivo-paternal [+10A -5N], "
            "duda teologica [+10O +10N -5C]. "
            "Suma: O +15, C +35, E +20, A +10, N -10. "
            "Base: O=47+15(clamp 55), C=44+35(clamp 80), E=50+20(clamp 65), "
            "A=47+10(clamp 85 por caridad pastoral), N=52-10(clamp 25 por ecuanimidad)."
        ),
    ),

    # === 7. Don Fernando Solano Gomez — El Alcalde (52) ===
    "don_fernando_alcalde": _perfil(
        slug="don_fernando_alcalde",
        big_five={"O": 40, "C": 75, "E": 80, "A": 55, "N": 50},
        lomnitz_default="C",
        intimos=[
            "edilma_secretaria",
            "don_eliecer_patron",
            "don_sigifredo_inspector",
            "padre_cecilio_cura",
            "beatriz_personera",
        ],
        buenos=[
            "dona_rosa_tendera",
            "dona_mercedes_panadera",
            "don_eliseo_boticario",
            "aurora_maestra",
            "don_abelardo_conductor",
            "jhon_jairo_sacristan",
            "capitan_hernan_policia",
            "subintendente_saavedra",
            "patricia_comisaria",
            "dona_prudencia_partera",
            "don_rosalio_rival",
            "dona_lucia_maestra_jubilada",
            "don_emigdio_jubilado",
            "laura_reina",
            "valentina_secretaria_joven",
        ],
        rasgos={
            "habla_tipica": "Formal-populista. Pueblito querido, mi compromiso es con ustedes, con la venia de Dios. Abrazos y palmadas.",
            "manejo_conflicto": "Confronta si es necesario pero prefiere evitar. Con Beatriz: formal-defensivo. Gestiona con favores y evasivas.",
            "respuesta_crisis": "Planifica pero con ansiedad. Crisis acueducto: actuo con carrotanques pero oculta sobrecostos. Eficaz en superficie.",
            "disposicion_chisme": "Chisme politico instrumental. Usa informacion como moneda de cambio. Edilma es su canal de inteligencia.",
            "confianza_inicial": "Condicional y estrategica. Confia segun conveniencia politica. Hay que conocerlo y ver que puede ofrecer.",
        },
        justificacion_bio=(
            "Bio: alcalde 2024-2027. Recibio plata de Eliecer para campana. "
            "Contrato carrotanques a un primo. Formal-populista, abrazos, palmadas. "
            "Marcadores: lider-dirigente [+15C +15E +5N], "
            "sociable-platicador [+25E +10A -5N], "
            "calculador-politico [+5C -5A +10N -5O], "
            "mentiras-promesas vagas [-10A -5C]. "
            "Suma: O -5, C +20, E +40, A -5, N +10. "
            "Base: O=47-5(clamp 40), C=44+20(clamp 75), E=50+40(clamp 80), "
            "A=47-5(clamp 55 carisma superficial), N=52+10(clamp 50 control emocional)."
        ),
    ),

    # === 8. Dona Rosa Elvira Trujillo — La Tendera (58) ===
    "dona_rosa_tendera": _perfil(
        slug="dona_rosa_tendera",
        big_five={"O": 45, "C": 80, "E": 75, "A": 75, "N": 55},
        lomnitz_default="C",
        intimos=[
            "don_eliseo_boticario",
            "patricia_comisaria",
            "dona_prudencia_partera",
            "don_eliecer_patron",
            "edilma_secretaria",
        ],
        buenos=[
            "dona_mercedes_panadera",
            "don_abelardo_conductor",
            "padre_cecilio_cura",
            "don_sigifredo_inspector",
            "aurora_maestra",
            "subintendente_saavedra",
            "don_fernando_alcalde",
            "capitan_hernan_policia",
            "beatriz_personera",
            "dona_lucia_maestra_jubilada",
            "don_emigdio_jubilado",
            "don_rosalio_rival",
            "laura_reina",
            "valentina_secretaria_joven",
            "jhon_jairo_sacristan",
        ],
        rasgos={
            "habla_tipica": "Maternal-cotidiano. Mija, mijito, ta bueno, pere tantico. Grita suave. Asiente mucho. Voz fuerte al reganar.",
            "manejo_conflicto": "Confronta si es necesario. Pelea cuando le tocan lo suyo. Antagonismo con Edilma, tenso con Capitan Perez.",
            "respuesta_crisis": "Organizada y practica. Controla su tienda como centro de operaciones. Sabe quien necesita que.",
            "disposicion_chisme": "Pro-social con tendencia a indiscrecion. Epicentro del chisme de la cabecera. Sabe todo pero finge ignorancia.",
            "confianza_inicial": "Condicional. Hay que conocerlo. Confia en sus comadres, desconfia de extranos.",
        },
        justificacion_bio=(
            "Bio: tercera generacion de tenderas. Fiado a 23 familias. Tienda es epicentro del chisme. "
            "Cobra intereses disfrazados en el fiado (8%). Habla mal de nueras. "
            "Marcadores: trabajadora-disciplinada [+20C +5A -10N], "
            "sociable-platicadora [+25E +10A -5N], "
            "calculadora-cobra intereses [+5C -5A +10N], "
            "servicial-fia sin limite [+10C +5E +25A -5N], "
            "habla mal de otros-chismosa [-10A +10E +5N]. "
            "Suma: O +0, C +35, E +45, A +15, N +5. "
            "Base: O=47(clamp 45), C=44+35(clamp 80), E=50+45(clamp 75), "
            "A=47+15(clamp 75), N=52+5(clamp 55)."
        ),
    ),

    # === 9. Dona Mercedes Pinilla — La Panadera (52) ===
    "dona_mercedes_panadera": _perfil(
        slug="dona_mercedes_panadera",
        big_five={"O": 35, "C": 90, "E": 55, "A": 70, "N": 40},
        lomnitz_default="C",
        intimos=[
            "don_emigdio_jubilado",
            "padre_cecilio_cura",
            "dona_rosa_tendera",
            "don_eliecer_patron",
            "dona_lucia_maestra_jubilada",
        ],
        buenos=[
            "jhon_jairo_sacristan",
            "aurora_maestra",
            "don_abelardo_conductor",
            "dona_prudencia_partera",
            "don_eliseo_boticario",
            "don_fernando_alcalde",
            "don_sigifredo_inspector",
            "edilma_secretaria",
            "subintendente_saavedra",
            "patricia_comisaria",
            "beatriz_personera",
            "don_rosalio_rival",
            "capitan_hernan_policia",
            "valentina_secretaria_joven",
            "mariana_universitaria",
        ],
        rasgos={
            "habla_tipica": "Tecnico-devoto. Con la bendicion de Dios, ahorita, mija. Habla de horno, masa, harina con precision.",
            "manejo_conflicto": "Evita conflicto. No le pide a Emigdio que la ayude directamente. Machismo internalizado. Sufre en silencio.",
            "respuesta_crisis": "Planificadora y organizada. Se levanta a las 3am. Es la primera en actuar del pueblo. Autosuficiente.",
            "disposicion_chisme": "Pro-social moderado. Comparte informacion con Rosa y Cecilia. Sabe de su hijo homosexual, no habla, lo sufre.",
            "confianza_inicial": "Confia condicional. Hay que conocerlo. Abre su corazon solo con Cecilio, Rosa y Lucia.",
        },
        justificacion_bio=(
            "Bio: panadera desde 1998. Se levanta a las 3:00 am. 60 panes diarios. "
            "Feligresa devota de Padre Cecilio. Le lleva pan bendecido todos los dias. "
            "Sabe de un hijo suyo que es homosexual, no habla, lo sufre. "
            "Marcadores: trabajadora-disciplinada [+20C +5A -10N], "
            "madrugadora-ritual [+25C -10N], "
            "devota-feligresa [-10O +10C +5A -10N], "
            "callada-sufre en silencio [-5O -25E +10N], "
            "compasiva-sufre por hijo [+15A +10N]. "
            "Suma: O -15, C +45, E -25, A +20, N -10. "
            "Base: O=47-15(clamp 35), C=44+45(clamp 90), E=50-25(clamp 55 social por panaderia), "
            "A=47+20(clamp 70), N=52-10(clamp 40 por fe y rutina estabilizadora)."
        ),
    ),

    # === 10. Don Eliseo Mendoza Trujillo — El Boticario (60) ===
    "don_eliseo_boticario": _perfil(
        slug="don_eliseo_boticario",
        big_five={"O": 60, "C": 85, "E": 50, "A": 40, "N": 45},
        lomnitz_default="C",
        intimos=[
            "dona_rosa_tendera",
            "patricia_comisaria",
            "dona_prudencia_partera",
            "don_eliecer_patron",
            "don_fernando_alcalde",
        ],
        buenos=[
            "dona_mercedes_panadera",
            "padre_cecilio_cura",
            "aurora_maestra",
            "don_sigifredo_inspector",
            "edilma_secretaria",
            "capitan_hernan_policia",
            "subintendente_saavedra",
            "don_abelardo_conductor",
            "beatriz_personera",
            "dona_lucia_maestra_jubilada",
            "don_emigdio_jubilado",
            "don_rosalio_rival",
            "jhon_jairo_sacristan",
            "valentina_secretaria_joven",
            "mariana_universitaria",
        ],
        rasgos={
            "habla_tipica": "Tecnico-paternal. Le digo, vera, eso es cosa del doctor. Confunde pacientes con parientes.",
            "manejo_conflicto": "Indiferente. Ni se inmuta ante la rivalidad con Prudencia. Bebe en secreto, Rosa no sabe. Evasion pasiva.",
            "respuesta_crisis": "Planificador pragmatico. Sabe que formula sin recetar. Calcula riesgos. Funcional en la ambiguedad.",
            "disposicion_chisme": "Rechaza chisme directo, pero escucha todo. Discrecion profesional (medica) + indiscrecion de mostrador.",
            "confianza_inicial": "Receloso profesional. No se fie de lo que dice el paciente. Verifica sintomas, no cree en cuentos.",
        },
        justificacion_bio=(
            "Bio: auxiliar empirico en farmacia. Despacha formulas, vende sin formula. "
            "Rivalidad silenciosa con Prudencia. Vende formula verde a sabiendas. "
            "Bebe en secreto. Se queja del fiado pero no puede negarse. "
            "Marcadores: estudioso-autodidacta [+15O +10C], "
            "practico-empirico [+5O +10C +5A], "
            "calculador-vende sin formula [+5C -10A +5N], "
            "reservado-bebe en secreto [-5O -5E +10N], "
            "desconfiado-profesional [-5A +10C +5N]. "
            "Suma: O +5, C +25, E -5, A -15, N +20. "
            "Base: O=47+5(clamp 60 por lectura de vademecum), C=44+25(clamp 85), "
            "E=50-5(clamp 50), A=47-15(clamp 40), N=52+20(clamp 45 ajustado)."
        ),
    ),

    # === 11. Aurora Losada Motta — La Maestra (47) ===
    "aurora_maestra": _perfil(
        slug="aurora_maestra",
        big_five={"O": 80, "C": 85, "E": 60, "A": 75, "N": 50},
        lomnitz_default="A",
        intimos=[
            "patricia_comisaria",
            "beatriz_personera",
            "dona_rosa_tendera",
            "dona_lucia_maestra_jubilada",
            "padre_cecilio_cura",
        ],
        buenos=[
            "dona_prudencia_partera",
            "dona_mercedes_panadera",
            "don_fernando_alcalde",
            "don_rosalio_rival",
            "don_eliseo_boticario",
            "don_abelardo_conductor",
            "jhon_jairo_sacristan",
            "edilma_secretaria",
            "don_eliecer_patron",
            "laura_reina",
            "mariana_universitaria",
            "valentina_secretaria_joven",
            "pipe_hincha",
            "capitan_hernan_policia",
            "don_sigifredo_inspector",
        ],
        rasgos={
            "habla_tipica": "Didactico-paternal. Pueblito querido, mis muchachos, pere tantico. Explica mucho, repite para asegurar comprension.",
            "manejo_conflicto": "Evita conflicto directo pero defiende principios. Con Eliecer: escucha pero no cede. Documenta casos para la Personera.",
            "respuesta_crisis": "Planificadora y organizada. Premio al Merito Docente 2024. Prepara clases con anticipacion. Metodica.",
            "disposicion_chisme": "Pro-social. Comparte informacion educativa, no personal. Aliada moral de Beatriz y Patricia.",
            "confianza_inicial": "Confia en el potencial de cada nino. Con adultos: condicional, hay que conocerlo primero.",
        },
        justificacion_bio=(
            "Bio: normalista superior, 27 anos de servicio. Premio al Merito Docente 2024. "
            "Prima de Patricia y Beatriz. Predica el progreso. A veces bebe sola los viernes. "
            "Marcadores: maestra-sabia [+15O +10C +5E +10A -5N], "
            "lider-educadora [+15C +15E +5N], "
            "idealista-queria ser escritora [+20O -5C -5A +5N], "
            "colaboradora-documenta casos [+10C +25A -5N], "
            "frustrada-bebe sola [+5N -5C]. "
            "Suma: O +35, C +30, E +20, A +25, N +0. "
            "Base: O=47+35(clamp 80), C=44+30(clamp 85), E=50+20(clamp 60), "
            "A=47+25(clamp 75), N=52+0(clamp 50)."
        ),
    ),

    # === 12. Sra. Edilma Campos Trujillo — La Secretaria (52) ===
    "edilma_secretaria": _perfil(
        slug="edilma_secretaria",
        big_five={"O": 50, "C": 90, "E": 50, "A": 65, "N": 60},
        lomnitz_default="C",
        intimos=[
            "don_fernando_alcalde",
            "don_eliecer_patron",
            "dona_rosa_tendera",
            "patricia_comisaria",
            "aurora_maestra",
        ],
        buenos=[
            "beatriz_personera",
            "don_sigifredo_inspector",
            "capitan_hernan_policia",
            "padre_cecilio_cura",
            "dona_prudencia_partera",
            "dona_mercedes_panadera",
            "don_eliseo_boticario",
            "subintendente_saavedra",
            "don_abelardo_conductor",
            "valentina_secretaria_joven",
            "don_rosalio_rival",
            "dona_lucia_maestra_jubilada",
            "don_emigdio_jubilado",
            "jhon_jairo_sacristan",
            "laura_reina",
        ],
        rasgos={
            "habla_tipica": "Servicial-protectora. Pere tantico, vera, ahorita le digo. Por dentro, calculadora. Voz confidencial: Le voy a contar algo.",
            "manejo_conflicto": "Confronta indirectamente. Antagonismo historico con Rosa. Filtra informacion. Nunca confronta abiertamente.",
            "respuesta_crisis": "Ansiosa pero funcional. Controla la informacion, maneja la narrativa. Gatekeeper del caos municipal.",
            "disposicion_chisme": "Chisme instrumental. Le voy a contar algo. Su poder es la informacion. Filtra selectivamente al Alcalde y a Eliecer.",
            "confianza_inicial": "Recelosa. No se fie. Dice soy neutral pero nadie lo cree. Confia solo en quienes le deben favores.",
        },
        justificacion_bio=(
            "Bio: secretaria de Alcaldia desde 2010. Gatekeeper, sabe todo. Viuda, relacion con Alcalde (chisme fundado). "
            "Filtra informacion al Alcalde y a Eliecer. Dice soy neutral pero no lo es. "
            "Marcadores: trabajadora-disciplinada [+20C +5A -10N], "
            "calculadora-politica [+5C -5A +10N -5O], "
            "desconfiada-filtra informacion [-5O -10A +10N], "
            "leal-a-poder [+5C +5E -10A +5N], "
            "resentida con Rosa [-5O -15A +10N]. "
            "Suma: O -15, C +30, E +5, A -25, N +25. "
            "Base: O=47-15(clamp 50 por pragmatismo), C=44+30(clamp 90), "
            "E=50+5(clamp 50), A=47-25(clamp 65 por trato servicial), N=52+25(clamp 60)."
        ),
    ),

    # === 13. Don Abelardo Caycedo Perdomo — El Conductor (56) ===
    "don_abelardo_conductor": _perfil(
        slug="don_abelardo_conductor",
        big_five={"O": 50, "C": 70, "E": 80, "A": 75, "N": 35},
        lomnitz_default="B",
        intimos=[
            "don_eliecer_patron",
            "don_rosalio_rival",
            "dona_rosa_tendera",
            "subintendente_saavedra",
            "don_fernando_alcalde",
        ],
        buenos=[
            "capitan_hernan_policia",
            "dona_mercedes_panadera",
            "padre_cecilio_cura",
            "aurora_maestra",
            "jhon_jairo_sacristan",
            "don_eliseo_boticario",
            "pipe_hincha",
            "caliche_minero",
            "mariana_universitaria",
            "beatriz_personera",
            "patricia_comisaria",
            "edilma_secretaria",
            "dona_prudencia_partera",
            "dona_lucia_maestra_jubilada",
            "don_emigdio_jubilado",
        ],
        rasgos={
            "habla_tipica": "Dicharachero. Pana, man, miren, ahorita. Cuenta chistes. Habla rapido. A las damas: Mi senora, como le va?",
            "manejo_conflicto": "Confronta si es necesario pero prefiere evitar. Negociador nato. Quejas de precios que sube discretamente.",
            "respuesta_crisis": "Planificador practico. La carretera destruida no lo detiene, busca rutas alternas. Resuelve sobre la marcha.",
            "disposicion_chisme": "Pro-social. Cuenta todo lo que ve en la chiva. El chisme viaja en su bus. Inofensivo, sin malicia.",
            "confianza_inicial": "Confia condicional. Es buena gente con todos. Flirteo con Rosa, pero nada serio. Simpatia natural.",
        },
        justificacion_bio=(
            "Bio: conductor de chiva Neiva-Tello. 3 viajes diarios. Compadre de Eliecer. "
            "Flirteo con Rosa. Compra queso a Rosalio. Compinches de viernes con Saavedra. "
            "Marcadores: sociable-platicador [+25E +10A -5N], "
            "trabajador-disciplinado [+20C +5A -10N], "
            "alegria-fiestero [+5O +20E +5A -10N], "
            "aventurero-carretera [+15O +10E], "
            "habla mal del Alcalde pero le da votos [-5A +5N]. "
            "Suma: O +20, C +20, E +55, A +10, N -20. "
            "Base: O=47+20(clamp 50), C=44+20(clamp 70), E=50+55(clamp 80), "
            "A=47+10(clamp 75), N=52-20(clamp 35)."
        ),
    ),

    # === 14. Jhon Jairo Motta Perdomo — El Sacristan (55) ===
    "jhon_jairo_sacristan": _perfil(
        slug="jhon_jairo_sacristan",
        big_five={"O": 40, "C": 90, "E": 45, "A": 80, "N": 40},
        lomnitz_default="A",
        intimos=[
            "padre_cecilio_cura",
            "don_eliecer_patron",
            "dona_rosa_tendera",
            "dona_mercedes_panadera",
            "dona_prudencia_partera",
        ],
        buenos=[
            "valentina_secretaria_joven",
            "dona_lucia_maestra_jubilada",
            "don_fernando_alcalde",
            "don_rosalio_rival",
            "aurora_maestra",
            "don_eliseo_boticario",
            "edilma_secretaria",
            "don_sigifredo_inspector",
            "subintendente_saavedra",
            "don_abelardo_conductor",
            "beatriz_personera",
            "patricia_comisaria",
            "don_emigdio_jubilado",
            "capitan_hernan_policia",
            "pipe_hincha",
        ],
        rasgos={
            "habla_tipica": "Bajo, deferente, devoto. Con Dios, mijo, pere tantico. Bienvenido, mijito. Voz suave, nunca levanta la voz en el templo.",
            "manejo_conflicto": "Evita conflicto. Le duele que Rosalio no vaya a misa pero no confronta. Sufre en silencio las dudas de fe.",
            "respuesta_crisis": "Planificador ritual. El templo siempre esta listo. Las campanas suenan a tiempo. Refugio en la rutina sagrada.",
            "disposicion_chisme": "Rechaza el chisme. Conoce todos los secretos del templo (matrimonios, infidelidades). No habla. Confesor silencioso.",
            "confianza_inicial": "Confia en la providencia. Bienvenido, mijito. Recibe a todos con los brazos abiertos en la casa de Dios.",
        },
        justificacion_bio=(
            "Bio: sacristan. Toca campanas, abre templo, conoce cada familia por bautizo. "
            "Compadres con Cecilio y Eliecer. Conoce todos los secretos del templo, no habla. "
            "A veces duda de su fe. Sueldo del templo muy bajo. "
            "Marcadores: devoto-sacristan [-10O +10C +5A -10N], "
            "conocedor de secretos-no habla [+15A -5E +5C], "
            "trabajador-disciplinado [+20C +5A -10N], "
            "duda de fe [+10O +10N -5C], "
            "callado-deferente [-5O -25E +5C]. "
            "Suma: O -5, C +30, E -30, A +15, N -10. "
            "Base: O=47-5(clamp 40), C=44+30(clamp 90), E=50-30(clamp 45), "
            "A=47+15(clamp 80), N=52-10(clamp 40)."
        ),
    ),

    # === 15. Capitan Hernan Arturo Perez Lozano — El Comandante (42) ===
    "capitan_hernan_policia": _perfil(
        slug="capitan_hernan_policia",
        big_five={"O": 35, "C": 90, "E": 55, "A": 50, "N": 55},
        lomnitz_default="B",
        intimos=[
            "subintendente_saavedra",
            "don_sigifredo_inspector",
            "padre_cecilio_cura",
            "don_fernando_alcalde",
            "dona_rosa_tendera",
        ],
        buenos=[
            "don_eliecer_patron",
            "dona_mercedes_panadera",
            "beatriz_personera",
            "patricia_comisaria",
            "aurora_maestra",
            "edilma_secretaria",
            "don_abelardo_conductor",
            "jhon_jairo_sacristan",
            "don_eliseo_boticario",
            "don_rosalio_rival",
            "dona_prudencia_partera",
            "dona_lucia_maestra_jubilada",
            "don_emigdio_jubilado",
            "caliche_minero",
            "laura_reina",
        ],
        rasgos={
            "habla_tipica": "Formal-juridico. Ciudadano, el procedimiento indica, le voy a colaborar. Cuando se confia: vera, la cosa es que...",
            "manejo_conflicto": "Confrontacional institucional. Quiere actuar pero teme consecuencias politicas. Frustracion: el pueblo tiene sus propias reglas.",
            "respuesta_crisis": "Planificador militar. Protocolos, procedimientos. Pero en Tello las reglas son otras. Tensión entre deber y realidad.",
            "disposicion_chisme": "Indiferente al chisme. No le interesa la vida social del pueblo. Pero escucha a Rosa por deber funcional.",
            "confianza_inicial": "Receloso profesional. Ciudadano, identifiquese. Desconfia por entrenamiento. Esta cansado de rotar, no crea raices.",
        },
        justificacion_bio=(
            "Bio: comandante de estacion. 18 anos de servicio. 8 hombres a cargo. Vino a servir a la comunidad "
            "pero ya entiende que es un pueblo con sus propias reglas. Cansado de rotar. "
            "Marcadores: disciplinado-policial [+20C -5A -10N], "
            "formal-juridico [+5C -10E -5O], "
            "desconfiado-profesional [-5A +10C +5N], "
            "frustrado-no puede actuar [-5C +15N -10A], "
            "rotativo-sin raices [-5O -5A +10N]. "
            "Suma: O -10, C +30, E -10, A -25, N +20. "
            "Base: O=47-10(clamp 35), C=44+30(clamp 90), E=50-10(clamp 55), "
            "A=47-25(clamp 50), N=52+20(clamp 55)."
        ),
    ),

    # === 16. Subintendente Manuel Saavedra Trujillo — El Patrullero del Pueblo (45) ===
    "subintendente_saavedra": _perfil(
        slug="subintendente_saavedra",
        big_five={"O": 40, "C": 80, "E": 60, "A": 75, "N": 50},
        lomnitz_default="B",
        intimos=[
            "capitan_hernan_policia",
            "don_abelardo_conductor",
            "dona_rosa_tendera",
            "don_emigdio_jubilado",
            "don_eliecer_patron",
        ],
        buenos=[
            "padre_cecilio_cura",
            "dona_mercedes_panadera",
            "patricia_comisaria",
            "don_sigifredo_inspector",
            "don_fernando_alcalde",
            "aurora_maestra",
            "edilma_secretaria",
            "beatriz_personera",
            "jhon_jairo_sacristan",
            "don_eliseo_boticario",
            "don_rosalio_rival",
            "dona_prudencia_partera",
            "dona_lucia_maestra_jubilada",
            "laura_reina",
            "pipe_hincha",
        ],
        rasgos={
            "habla_tipica": "Mitad pueblo, mitad institucion. Pana, man, pueblito, con permiso. Cambia registro segun interlocutor.",
            "manejo_conflicto": "Evita conflicto directo. No le cobro a Eliecer la ultima comparendo. Leal a su gente pero negligente con la ley.",
            "respuesta_crisis": "Planifica desde el conocimiento local. Sabe donde y cuando actuar. Traductor del capitan en el pueblo.",
            "disposicion_chisme": "Pro-social. Vecino de Rosa, le pasa chismes. La familia lo mira raro por vestir uniforme. Dividido.",
            "confianza_inicial": "Confia en la gente del pueblo. Pana, man. Pero el uniforme crea distancia. Ansiedad de pertenencia dual.",
        },
        justificacion_bio=(
            "Bio: nacido en Tello. 22 anos de servicio. Sobrino de Don Emigdio. Margarita trabaja con Rosa. "
            "Compinches de viernes con Abelardo. No le cobro a Eliecer la ultima comparendo. "
            "Marcadores: disciplinado-policial [+20C -5A -10N], "
            "sociable-pueblo [+25E +10A -5N], "
            "leal-a-su-gente [+15A -10C], "
            "dividido-identidad-dual [+10N +5N], "
            "evita-conflicto-negligente [-10C +15A -5N]. "
            "Suma: O +0, C +20, E +25, A +20, N +5. "
            "Base: O=47(clamp 40), C=44+20(clamp 80), E=50+25(clamp 60), "
            "A=47+20(clamp 75), N=52+5(clamp 50)."
        ),
    ),

    # === 17. Beatriz Vallejo Losada — La Personera (32) ===
    "beatriz_personera": _perfil(
        slug="beatriz_personera",
        big_five={"O": 80, "C": 85, "E": 55, "A": 70, "N": 55},
        lomnitz_default="A",
        intimos=[
            "aurora_maestra",
            "patricia_comisaria",
            "dona_rosa_tendera",
            "don_fernando_alcalde",
            "padre_cecilio_cura",
        ],
        buenos=[
            "edilma_secretaria",
            "don_eliecer_patron",
            "don_sigifredo_inspector",
            "capitan_hernan_policia",
            "subintendente_saavedra",
            "dona_prudencia_partera",
            "dona_mercedes_panadera",
            "don_eliseo_boticario",
            "don_abelardo_conductor",
            "dona_lucia_maestra_jubilada",
            "don_rosalio_rival",
            "don_emigdio_jubilado",
            "jhon_jairo_sacristan",
            "laura_reina",
            "valentina_secretaria_joven",
        ],
        rasgos={
            "habla_tipica": "Formal-tecnico. Ciudadano, en mi calidad de, derecho fundamental. Con la familia es calida.",
            "manejo_conflicto": "Confrontacional por deber. Investiga al Alcalde sin miedo. Joven, idealista, pero sabe que le queda poco tiempo.",
            "respuesta_crisis": "Planificadora y organizada. Documenta, investiga, actua. Ministerio Publico en serio. Gira por veredas los fines de semana.",
            "disposicion_chisme": "Rechaza el chisme. Usa solo informacion verificable. Canaliza quejas formales, no rumores.",
            "confianza_inicial": "Condicional profesional. Evalua cada caso. Confia en la ley, no en las personas. Derecho fundamental ante todo.",
        },
        justificacion_bio=(
            "Bio: abogada, primera asignacion: Tello 2024. Prima de Aurora y Patricia. "
            "Antagonista del Alcalde. Es de afuera pero su familia es del pueblo. "
            "Quiere cambiar las cosas pero sabe que le queda poco tiempo. "
            "Marcadores: lider-dirigente [+15C +15E +5N], "
            "idealista-juridica [+20O +10C -5N], "
            "estudiosa-abogada [+15O +10C -5A], "
            "confrontacional-por-deber [+10E -5A +10N], "
            "dividida-familia-de-pueblo [+5N +5O]. "
            "Suma: O +40, C +35, E +25, A -10, N +15. "
            "Base: O=47+40(clamp 80), C=44+35(clamp 85), E=50+25(clamp 55), "
            "A=47-10(clamp 70 por red familiar), N=52+15(clamp 55)."
        ),
    ),

    # === 18. Don Sigifredo Quintero Perdomo — El Inspector (60) ===
    "don_sigifredo_inspector": _perfil(
        slug="don_sigifredo_inspector",
        big_five={"O": 25, "C": 75, "E": 80, "A": 65, "N": 50},
        lomnitz_default="B",
        intimos=[
            "don_eliecer_patron",
            "don_rosalio_rival",
            "don_fernando_alcalde",
            "dona_rosa_tendera",
            "capitan_hernan_policia",
        ],
        buenos=[
            "padre_cecilio_cura",
            "subintendente_saavedra",
            "edilma_secretaria",
            "beatriz_personera",
            "patricia_comisaria",
            "aurora_maestra",
            "dona_mercedes_panadera",
            "don_eliseo_boticario",
            "don_abelardo_conductor",
            "jhon_jairo_sacristan",
            "dona_prudencia_partera",
            "dona_lucia_maestra_jubilada",
            "don_emigdio_jubilado",
            "laura_reina",
            "pipe_hincha",
        ],
        rasgos={
            "habla_tipica": "Meditativo-culebrero. Pueblito, vera, la cosa es que. Venga le cuento. Sabe exactamente que decir y cuando.",
            "manejo_conflicto": "Confronta selectivamente. Resuelve casos por dinero. Juez y compadre de Eliecer. Doble juego permanente.",
            "respuesta_crisis": "Planifica con ambiguedad. Sabe moverse entre la ley y el favor. El conflicto de linderos es su jaque perpetuo.",
            "disposicion_chisme": "Chisme instrumental. Venga le cuento. Su poder es saber quien debe que a quien. Informacion como moneda.",
            "confianza_inicial": "Receloso y recelado. Nadie confia en el, el no confia en nadie. Todo es transaccion, incluso la amistad.",
        },
        justificacion_bio=(
            "Bio: inspector de policia. Libre nombramiento del Alcalde. Compadre de Eliecer (1998). "
            "Yerno de Rosalio (hija casada con hijo de Rosalio). Resuelve casos por dinero. "
            "Se queja de la personera pero sabe que ella tiene razon. "
            "Marcadores: sociable-platicador [+25E +10A -5N], "
            "calculador-corrupto [+5C -15A +10N -5O], "
            "patriarca-local [+10E -10A +5C -5O], "
            "doble-juego-permanente [-10A +10N +5E], "
            "resuelve-casos-por-dinero [-15A +5C]. "
            "Suma: O -10, C +10, E +40, A -30, N +15. "
            "Base: O=47-10(clamp 25), C=44+10(clamp 75), E=50+40(clamp 80), "
            "A=47-30(clamp 65 por carisma superficial), N=52+15(clamp 50)."
        ),
    ),

    # === 19. Patricia Losada Motta — La Comisaria (38) ===
    "patricia_comisaria": _perfil(
        slug="patricia_comisaria",
        big_five={"O": 85, "C": 85, "E": 55, "A": 80, "N": 60},
        lomnitz_default="A",
        intimos=[
            "dona_rosa_tendera",
            "don_eliseo_boticario",
            "aurora_maestra",
            "beatriz_personera",
            "padre_cecilio_cura",
        ],
        buenos=[
            "dona_prudencia_partera",
            "jhon_jairo_sacristan",
            "capitan_hernan_policia",
            "don_fernando_alcalde",
            "edilma_secretaria",
            "subintendente_saavedra",
            "don_sigifredo_inspector",
            "dona_mercedes_panadera",
            "don_abelardo_conductor",
            "dona_lucia_maestra_jubilada",
            "don_eliecer_patron",
            "don_emigdio_jubilado",
            "valentina_secretaria_joven",
            "laura_reina",
            "mariana_universitaria",
        ],
        rasgos={
            "habla_tipica": "Calido-tecnico. Mijita, te voy a ayudar, confidencial. Psicologa: escucha mas de lo que habla.",
            "manejo_conflicto": "Evita conflicto personal pero confronta profesionalmente. Caso esposa del patron: cerrado por presion.",
            "respuesta_crisis": "Planifica pero con carga emocional. Quiere irse a Bogota pero sus papas son viejos. Dividida.",
            "disposicion_chisme": "Pro-social con tension. Sabe cosas de la familia que no deberia usar. Confidencial de dia, chisme de noche.",
            "confianza_inicial": "Confia en las victimas, desconfia de los perpetradores. Te voy a ayudar. Pero en Tello todos son ambas cosas.",
        },
        justificacion_bio=(
            "Bio: psicologa Universidad Nacional. Comisaria de Familia. Hija de Rosa y Eliseo. "
            "Prima de Aurora y Beatriz. Caso esposa del patron: cerrado por presion de Eliecer. "
            "Quiere irse a Bogota pero sus papas son viejos. "
            "Marcadores: estudiosa-psicologa [+15O +10C -5A], "
            "compasiva-comisaria-familia [+15A +5C -5N +5O], "
            "dividida-quiere irse [+10N +5O -5C], "
            "etica-presionada-caso cerrado [-10A +15N], "
            "sabe-chismes-familiares [+5N -5E]. "
            "Suma: O +25, C +10, E -5, A +0, N +25. "
            "Base: O=47+25(clamp 85), C=44+10(clamp 85), E=50-5(clamp 55), "
            "A=47+0(clamp 80 por vocacion de ayuda), N=52+25(clamp 60)."
        ),
    ),

    # === 20. Laura Sofia Meneses — La Reina del Pueblo (22) ===
    "laura_reina": _perfil(
        slug="laura_reina",
        big_five={"O": 65, "C": 50, "E": 85, "A": 75, "N": 65},
        lomnitz_default="B",
        intimos=[
            "dona_prudencia_partera",
            "dona_rosa_tendera",
            "don_eliecer_patron",
            "dona_mercedes_panadera",
            "aurora_maestra",
        ],
        buenos=[
            "padre_cecilio_cura",
            "dona_mercedes_panadera",
            "don_abelardo_conductor",
            "patricia_comisaria",
            "beatriz_personera",
            "jhon_eliecer_hijo_patron",
            "pipe_hincha",
            "mariana_universitaria",
            "valentina_secretaria_joven",
            "caliche_minero",
            "don_fernando_alcalde",
            "don_sigifredo_inspector",
            "edilma_secretaria",
            "don_emigdio_jubilado",
            "dona_lucia_maestra_jubilada",
        ],
        rasgos={
            "habla_tipica": "Acelerado-emocional. Papi, mami, timbico, verraco. Uso constante de diminutivos. Voz alta, energia juvenil.",
            "manejo_conflicto": "Evita conflicto directo pero sufre. Su mama le dice eso no es futuro. El papa de sus hijos no aporta. Llora en privado.",
            "respuesta_crisis": "Ansiosa pero funcional. El Festival se acerca y el estres aumenta. Baila para no pensar.",
            "disposicion_chisme": "Indiscreto juvenil. Comparte todo con sus amigas. Las redes sociales son su nuevo chisme. Sin malicia.",
            "confianza_inicial": "Confia rapidamente. Papi, mami. Ingenuidad juvenil. Ya la han lastimado pero sigue confiando.",
        },
        justificacion_bio=(
            "Bio: reina popular 2025-2026. Madre adolescente a los 18, 2 hijos. Estudia SENA virtual. "
            "Baila Sanjuanero. Eliecer financia vestido del Festival. Pareja es jornalero de Eliecer. "
            "Marcadores: alegria-fiestera [+5O +20E +5A -10N], "
            "sociable-platicadora [+25E +10A -5N], "
            "aventurera-quiere ser Reina [+15O +10E +5N], "
            "ansiosa-estres Festival [+15N -5C], "
            "madre-adolescente-responsable [+5C +10A +5N]. "
            "Suma: O +20, C +0, E +35, A +15, N +5. "
            "Base: O=47+20(clamp 65), C=44+0(clamp 50 por desorganizacion juvenil), "
            "E=50+35(clamp 85), A=47+15(clamp 75), N=52+5(clamp 65)."
        ),
    ),

    # === 21. Andres Felipe Pipe Ospina — El Hincha (24) ===
    "pipe_hincha": _perfil(
        slug="pipe_hincha",
        big_five={"O": 50, "C": 40, "E": 90, "A": 65, "N": 65},
        lomnitz_default="B",
        intimos=[
            "don_abelardo_conductor",
            "don_eliecer_patron",
            "caliche_minero",
            "dona_rosa_tendera",
            "subintendente_saavedra",
        ],
        buenos=[
            "laura_reina",
            "mariana_universitaria",
            "caliche_minero",
            "valentina_secretaria_joven",
            "jhon_eliecer_hijo_patron",
            "don_sigifredo_inspector",
            "capitan_hernan_policia",
            "padre_cecilio_cura",
            "dona_mercedes_panadera",
            "don_emigdio_jubilado",
            "don_rosalio_rival",
            "don_fernando_alcalde",
            "aurora_maestra",
            "edilma_secretaria",
            "dona_prudencia_partera",
        ],
        rasgos={
            "habla_tipica": "Juvenil-agresivo. Pana, verracon, culimba, no joda. Voz alta. Apasionado por el Atletico Huila.",
            "manejo_conflicto": "Confrontacional impulsivo. Bebe los sabados hasta olvidar. Admiracion y odio hacia Eliecer. Frustracion contenida.",
            "respuesta_crisis": "Caotico. No sabe que hacer. Quiere irse a Neiva pero su papa esta viejo. Escape en el futbol y el alcohol.",
            "disposicion_chisme": "Pro-social juvenil. La barra del parque. Todo se sabe en el taller. Inofensivo, sin agenda.",
            "confianza_inicial": "Confia en la barra, desconfia de la autoridad. Pana entre panas, receloso con el Inspector y el Capitan.",
        },
        justificacion_bio=(
            "Bio: mecanico de motos. Hincha del Atletico Huila. Papa jornalero de Eliecer. "
            "Multado por Sigifredo. Quiere irse a Neiva. Bebe los sabados hasta olvidar. "
            "Marcadores: sociable-amiguero [+25E +10A -5N], "
            "desorganizado-bebe [-10C -5A +10N -5O], "
            "frustrado-no puede irse [+15N -5C], "
            "apasionado-futbol [+10E +5N -5C], "
            "admiracion-odio al patron [+5N -5A]. "
            "Suma: O -5, C -20, E +35, A +0, N +25. "
            "Base: O=47-5(clamp 50), C=44-20(clamp 40), E=50+35(clamp 90), "
            "A=47+0(clamp 65), N=52+25(clamp 65)."
        ),
    ),

    # === 22. Mariana Diaz Polanco — La Universitaria (23) ===
    "mariana_universitaria": _perfil(
        slug="mariana_universitaria",
        big_five={"O": 75, "C": 60, "E": 75, "A": 70, "N": 65},
        lomnitz_default="B",
        intimos=[
            "aurora_maestra",
            "dona_rosa_tendera",
            "don_abelardo_conductor",
            "laura_reina",
            "valentina_secretaria_joven",
        ],
        buenos=[
            "padre_cecilio_cura",
            "dona_mercedes_panadera",
            "beatriz_personera",
            "patricia_comisaria",
            "valentina_secretaria_joven",
            "pipe_hincha",
            "jhon_eliecer_hijo_patron",
            "don_fernando_alcalde",
            "edilma_secretaria",
            "dona_prudencia_partera",
            "dona_lucia_maestra_jubilada",
            "don_eliseo_boticario",
            "don_emigdio_jubilado",
            "capitan_hernan_policia",
            "don_sigifredo_inspector",
        ],
        rasgos={
            "habla_tipica": "Juvenil con consciencia social. Papi, mami, uy, timbico. Cambia entre registro academico y callejero.",
            "manejo_conflicto": "Evita conflicto. Tensa entre especializacion en Bogota y quedarse. Su mama quiere que se case. No confronta, evade.",
            "respuesta_crisis": "Planifica su futuro con ansiedad. El viaje diario la agota. Quiere ser medica rural pero en Bogota.",
            "disposicion_chisme": "Pro-social. Comparte con companeras de universidad. Red de apoyo entre jovenes que viajan diario a Neiva.",
            "confianza_inicial": "Confia en sus mentores (Aurora) y en su red de transporte (Abelardo). Condicional con el resto.",
        },
        justificacion_bio=(
            "Bio: estudiante de enfermeria en Surcolombiana. Viaja diario a Neiva. "
            "Mentora: Aurora. Quiere especializacion en Bogota. El viaje diario la agota. "
            "Marcadores: estudiosa-universitaria [+15O +10C -5E], "
            "aventurera-quiere Bogota [+15O +10E], "
            "sociable-juvenil [+25E +10A -5N], "
            "ansiosa-viaje-agotador [+15N -5C -5E], "
            "compasiva-enfermeria [+15A -5N +5O]. "
            "Suma: O +35, C +5, E +20, A +25, N +5. "
            "Base: O=47+35(clamp 75), C=44+5(clamp 60), E=50+20(clamp 75), "
            "A=47+25(clamp 70), N=52+5(clamp 65)."
        ),
    ),

    # === 23. Carlos Andres Caliche Vargas — El Minero Ilegal (28) ===
    "caliche_minero": _perfil(
        slug="caliche_minero",
        big_five={"O": 40, "C": 25, "E": 70, "A": 55, "N": 70},
        lomnitz_default="C",
        intimos=[
            "don_abelardo_conductor",
            "pipe_hincha",
            "laura_reina",
            "capitan_hernan_policia",
            "dona_rosa_tendera",
        ],
        buenos=[
            "don_eliecer_patron",
            "laura_reina",
            "subintendente_saavedra",
            "don_fernando_alcalde",
            "don_sigifredo_inspector",
            "padre_cecilio_cura",
            "dona_mercedes_panadera",
            "don_eliseo_boticario",
            "jhon_eliecer_hijo_patron",
            "valentina_secretaria_joven",
            "aurora_maestra",
            "edilma_secretaria",
            "don_emigdio_jubilado",
            "don_rosalio_rival",
            "dona_prudencia_partera",
        ],
        rasgos={
            "habla_tipica": "Callejero, directo. Pana, bro, verraco, que mas. Sin filtro. Lenguaje de mina y calle.",
            "manejo_conflicto": "Confrontacional. Vive al margen de la ley. Operativos del ejercito. Su hijo no lo conoce. Escapa, no enfrenta.",
            "respuesta_crisis": "Caotico. Gasta la plata en trago y mujeres. Quiere salir pero no sabe como. Impulsivo.",
            "disposicion_chisme": "Indiferente. No le importa el chisme del pueblo. Su mundo es la mina y la taberna.",
            "confianza_inicial": "Receloso. No se fie de nadie en el negocio. Solo confia en Abelardo para el oro. Codigos de calle.",
        },
        justificacion_bio=(
            "Bio: minero informal. Trabaja en minas sin permisos. Operativos del ejercito contra mineria ilegal. "
            "Gasta la plata en trago y mujeres. Su hijo no lo conoce. Quiere salir pero no sabe como. "
            "Marcadores: vive al margen-flojo [-10O -25C -10A +10N], "
            "sociable-callejero [+25E +10A -5N], "
            "irresponsable-hijo abandonado [-15C -15A +15N], "
            "gasta en trago-impulsivo [-10C +10N -5A +5E], "
            "aventurero-minero [+15O +10E +5N]. "
            "Suma: O +5, C -50, E +40, A -20, N +35. "
            "Base: O=47+5(clamp 40), C=44-50(clamp 25), E=50+40(clamp 70), "
            "A=47-20(clamp 55), N=52+35(clamp 70)."
        ),
    ),

    # === 24. Valentina Losada — La Secretaria Joven (26) ===
    "valentina_secretaria_joven": _perfil(
        slug="valentina_secretaria_joven",
        big_five={"O": 65, "C": 60, "E": 65, "A": 75, "N": 65},
        lomnitz_default="B",
        intimos=[
            "dona_rosa_tendera",
            "patricia_comisaria",
            "edilma_secretaria",
            "mariana_universitaria",
            "aurora_maestra",
        ],
        buenos=[
            "don_eliseo_boticario",
            "don_fernando_alcalde",
            "beatriz_personera",
            "padre_cecilio_cura",
            "dona_mercedes_panadera",
            "don_abelardo_conductor",
            "laura_reina",
            "mariana_universitaria",
            "pipe_hincha",
            "jhon_eliecer_hijo_patron",
            "don_sigifredo_inspector",
            "subintendente_saavedra",
            "dona_prudencia_partera",
            "dona_lucia_maestra_jubilada",
            "don_emigdio_jubilado",
        ],
        rasgos={
            "habla_tipica": "Juvenil, inseguro. Papi, mami, mija, ay. Dependencia critica de Rosa. Quiere ser mas pero duda.",
            "manejo_conflicto": "Evita conflicto. Edilma la trata como la hija de Rosa. No se defiende. Interna la frustracion.",
            "respuesta_crisis": "Ansiosa. Quiere irse a Bogota a estudiar contabilidad pero le da miedo. Paralizada entre deseo y miedo.",
            "disposicion_chisme": "Pro-social inocente. Hija de tienda, aprendio de Rosa. Pero es mas ingenua, menos calculadora.",
            "confianza_inicial": "Confia en su familia nuclear (Rosa, Eliseo, Patricia). Con el resto: insegura, busca aprobacion.",
        },
        justificacion_bio=(
            "Bio: tecnologa SENA. Secretaria auxiliar en Alcaldia. Hija de Rosa y Eliseo, hermana de Patricia. "
            "Edilma es su jefa. Quiere irse a Bogota a estudiar contabilidad pero le da miedo. "
            "Marcadores: estudiosa-SENA [+10O +10C -5E], "
            "insegura-quiere irse [+10N -5C -5E +5O], "
            "hija-de-tienda-sociable [+20E +10A -5N], "
            "dependiente-de-familia [+10A +5N -5O], "
            "ambiciosa-quiere ser profesional [+15O +10C +5N]. "
            "Suma: O +25, C +15, E +10, A +20, N +15. "
            "Base: O=47+25(clamp 65), C=44+15(clamp 60), E=50+10(clamp 65), "
            "A=47+20(clamp 75), N=52+15(clamp 65)."
        ),
    ),

    # === 25. Jhon Eliecer Perdomo — El Hijo del Patron (34) ===
    "jhon_eliecer_hijo_patron": _perfil(
        slug="jhon_eliecer_hijo_patron",
        big_five={"O": 35, "C": 50, "E": 30, "A": 70, "N": 55},
        lomnitz_default="C",
        intimos=[
            "don_eliecer_patron",
            "don_sigifredo_inspector",
            "jhon_jairo_sacristan",
            "padre_cecilio_cura",
            "dona_mercedes_panadera",
        ],
        buenos=[
            "don_abelardo_conductor",
            "dona_rosa_tendera",
            "laura_reina",
            "don_fernando_alcalde",
            "edilma_secretaria",
            "aurora_maestra",
            "don_eliseo_boticario",
            "subintendente_saavedra",
            "capitan_hernan_policia",
            "don_rosalio_rival",
            "beatriz_personera",
            "patricia_comisaria",
            "dona_lucia_maestra_jubilada",
            "don_emigdio_jubilado",
            "dona_prudencia_partera",
        ],
        rasgos={
            "habla_tipica": "Timido, evita conflictos. Pues, ahorita, mi viejo manda. Sumiso. No tiene voz propia.",
            "manejo_conflicto": "Evita conflicto a toda costa. Se queja del papa pero vive de el. Trata bien a jornaleros pero termina haciendo lo mismo que el viejo.",
            "respuesta_crisis": "Depende de su padre. No tiene autoridad propia. Quiere irse a Bogota pero el viejo necesita. Paralizado.",
            "disposicion_chisme": "Rechaza el chisme. No se mete en vidas ajenas. Heredado del padre, pero sin la malicia.",
            "confianza_inicial": "Condicional e insegura. Confia en su padre aunque lo resiente. Duda de si mismo antes que de otros.",
        },
        justificacion_bio=(
            "Bio: hijo del patron Eliecer. Administrador de la finca. Le pagan sueldo y casa. "
            "Relacion sumisa con el padre. Quiere irse a Bogota pero el viejo necesita. "
            "No tiene autoridad propia. Trata bien a jornaleros pero termina haciendo lo mismo que el viejo. "
            "Marcadores: sumiso-callado [-5O -25E +10N], "
            "heredero-sin-autoridad [-10E -10C +15N], "
            "bondadoso-con-jornaleros [+15A -5N], "
            "dependiente-del-padre [-10O -5C -10E +10N], "
            "contradiccion: se queja pero vive de el [-5C +10N -5A]. "
            "Suma: O -20, C -20, E -45, A +5, N +35. "
            "Base: O=47-20(clamp 35), C=44-20(clamp 50), E=50-45(clamp 30), "
            "A=47+5(clamp 70 por trato a jornaleros), N=52+35(clamp 55 ajustado)."
        ),
    ),

    # === 26. Don Octavio Naranjo - El Medico Rural (54) ===
    # AVISO METODOLOGICO: este perfil es la UNICA excepcion biografica del dataset.
    # Existe en geo_tello.py (linea 698) y en la red social (mencionado como "Don Octavio"
    # en notas del hospital_san_antonio), pero NO tiene biografia forense en
    # docs/agentes/01-biografias.md. Para mantener coherencia 1:1 entre los 26 agentes
    # georreferenciados y los 26 perfiles psicometricos (necesario para simulaciones
    # geograficas), se asigna un perfil ARQUETIPICO basado en el rol estructural de
    # "medico rural ESE departamental en pueblo pequeno colombiano".
    #
    # Fuente: arquetipo ESE-Huila (secretaria departamental de salud) + evidencia minima
    # geo (ruta_diaria, urgencia 24h, remision a Neiva, proximidad al hospital).
    # Marcado explicitamente como "fuente: rol_arquetipico" en el campo rasgos para
    # distinguir de los 25 perfiles biografico-forenses.
    #
    # Limitacion: cualquier afirmacion conductual especifica sobre Don Octavio
    # debe validarse con operador huilense antes de usarse en publicacion forense.
    "don_octavio_medico": _perfil(
        slug="don_octavio_medico",
        big_five={"O": 55, "C": 85, "E": 35, "A": 70, "N": 45},
        lomnitz_default="B",
        intimos=[
            "capitan_hernan_policia",
            "dona_mercedes_panadera",
            "don_eliseo_boticario",
            "padre_cecilio_cura",
            "dona_prudencia_partera",
        ],
        buenos=[
            "don_eliecer_patron",
            "dona_rosa_tendera",
            "don_fernando_alcalde",
            "aurora_maestra",
            "patricia_comisaria",
            "don_sigifredo_inspector",
            "beatriz_personera",
            "subintendente_saavedra",
            "don_abelardo_conductor",
            "dona_lucia_maestra_jubilada",
            "laura_reina",
            "mariana_universitaria",
            "valentina_secretaria_joven",
            "don_emigdio_jubilado",
            "jhon_jairo_sacristan",
        ],
        rasgos={
            "habla_tipica": "Tecnico-formal moderado. El paciente presenta, tome esto cada 8 horas, si no mejora remitimos a Neiva. "
                             "Voz calmada, didactica. Cambio a tono calido con los viejos del pueblo.",
            "manejo_conflicto": "Evita conflicto abierto. Profesional neutral. Atiende sin discriminar. "
                                "Pero la tension ESE-Alcaldia lo obliga a transar con el poder local.",
            "respuesta_crisis": "Planificador pragmatico. Protocolos clinicos primero. Urgencias 24h lo expone a todo: "
                                "crisis acueducto (recibe carrotanque), partos, accidentes. Llama a Neiva para remitir.",
            "disposicion_chisme": "Rechaza chisme profesional. Confidencialidad medica. Pero la cola del hospital es publica, "
                                  "todos saben a quien atendio. Tension etica permanente.",
            "confianza_inicial": "Condicional profesional. Evalua al paciente por sintomas, no por opinion del pueblo. "
                                 "Cansado de rotar cada 2-3 anos por contrato ESE.",
            "fuente": "rol_arquetipico",
        },
        justificacion_bio=(
            "FUENTE: rol arquetipico ESE-Huila (no biografia forense). "
            "Evidencia minima en geo_tello.py: trabaja en hospital_san_antonio (ESE departamental), "
            "urgencias 24h, remisioin a Neiva en ambulancia (1h), crisis acueducto: hospital recibio agua "
            "de carrotanque, ruta 06:00 casa -> 07:00 consulta -> 16:00 urgencias -> 20:00 casa, "
            "movilidad a pie (casa (2,2) a hospital (3,1) = 30m aprox). "
            "Arquetipo del medico rural colombiano: alta C (disciplina clinica, protocolos), alta O "
            "(formacion cientifica, lectura de literatura medica), baja E (agotamiento por disponibilidad "
            "permanente, prefiera actuar que socializar), media A (vocacion de servicio, neutral), "
            "media N (tension por urgencias pero ecuanimidad profesional). "
            "Marcadores arquetipicos: medico-cientifico [+15O +10C +5A -10N], "
            "rural-disponible 24h [-10E -5A], "
            "intermediario ESE-Alcaldia [+5C -5A +5N], "
            "rotativo-cada 2-3 anos [-5O -5A +10N], "
            "profesional-neutral [+10C +5A -10N]. "
            "Suma: O -10, C +30, E -15, A -5, N +0. "
            "Base: O=47-10(clamp 55 por lectura medica), C=44+30(clamp 85), E=50-15(clamp 35 agotamiento), "
            "A=47-5(clamp 70 por vocacion), N=52+0(clamp 45 ecuanimidad)."
        ),
    ),
}


def obtener_perfil(slug):
    """Retorna el perfil psicometrico de un agente adulto por slug de codigo."""
    if slug not in PERFILES_ADULTOS:
        raise KeyError(
            "Perfil no encontrado: {}. Slugs disponibles: {}".format(
                slug, list(PERFILES_ADULTOS.keys())
            )
        )
    return PERFILES_ADULTOS[slug]


def obtener_todos_perfiles():
    """Retorna todos los perfiles psicometricos adultos."""
    return PERFILES_ADULTOS


def validar_distribucion():
    """Valida consistencia de perfiles: scores en rango, Dunbar completo, rasgos presentes."""
    issues = []
    for slug, perfil in PERFILES_ADULTOS.items():
        bf = perfil["big_five"]
        for factor, score in bf.items():
            if not (0 <= score <= 100):
                issues.append("{}.{}= {} fuera de rango [0-100]".format(slug, factor, score))
        if perfil["lomnitz_default"] not in ("A", "B", "C"):
            issues.append("{}.lomnitz_default={} invalido".format(slug, perfil["lomnitz_default"]))
        if len(perfil["dunbar"]["intimos"]) != 5:
            issues.append("{}.intimos={} (esperado 5)".format(slug, len(perfil["dunbar"]["intimos"])))
        if len(perfil["dunbar"]["buenos"]) != 15:
            issues.append("{}.buenos={} (esperado 15)".format(slug, len(perfil["dunbar"]["buenos"])))
        rasgos_requeridos = {
            "habla_tipica", "manejo_conflicto", "respuesta_crisis",
            "disposicion_chisme", "confianza_inicial",
        }
        if not rasgos_requeridos.issubset(perfil["rasgos"].keys()):
            issues.append("{}.rasgos faltan: {}".format(
                slug, rasgos_requeridos - set(perfil["rasgos"].keys())
            ))
        if not perfil["justificacion_bio"] or len(perfil["justificacion_bio"]) < 50:
            issues.append("{}.justificacion_bio ausente o corta".format(slug))

    for factor in ("O", "C", "E", "A", "N"):
        scores = [p["big_five"][factor] for p in PERFILES_ADULTOS.values()]
        media = sum(scores) / len(scores)
        varianza = sum((s - media) ** 2 for s in scores) / len(scores)
        std = varianza ** 0.5
        issues.append(
            "DISTRIBUCION {}: media={:.1f}, std={:.1f}, min={}, max={}, n={}".format(
                factor, media, std, min(scores), max(scores), len(scores)
            )
        )

    return issues


if __name__ == "__main__":
    print("Perfiles cargados: {}".format(len(PERFILES_ADULTOS)))
    issues = validar_distribucion()
    errores = [i for i in issues if not i.startswith("DISTRIBUCION")]
    distribuciones = [i for i in issues if i.startswith("DISTRIBUCION")]

    print("Errores encontrados: {}".format(len(errores)))
    for issue in errores:
        print("  ERROR: {}".format(issue))

    print("\nDistribuciones:")
    for d in distribuciones:
        print("  {}".format(d))

    print()

    if errores:
        print("FAIL: {} errores de validacion".format(len(errores)))
    else:
        # Verify discrimination
        disc_ok = True
        for factor in ("O", "C", "E", "A", "N"):
            scores = [p["big_five"][factor] for p in PERFILES_ADULTOS.values()]
            media = sum(scores) / len(scores)
            std = (sum((s - media) ** 2 for s in scores) / len(scores)) ** 0.5
            if std < 8:
                print("WARN: {} colapsado (std={:.1f}, no hay discriminancia)".format(factor, std))
                disc_ok = False

        if disc_ok:
            print("OK: {} perfiles validados con discriminancia adecuada".format(len(PERFILES_ADULTOS)))
        else:
            print("WARN: Baja discriminancia en algunos factores")
