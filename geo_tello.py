# -*- coding: utf-8 -*-
# Sociedad Opita — Geografia forense: 34 edificios + 26 adultos
# https://sociedad.opitacode.com (proximo)
"""
geo_tello.py
============
Base de datos geogrfica forense de Tello, Huila.

OBJETIVO FORENSE
================
Documentar con precisin cada lugar fsico de Tello para que las simulaciones
puedan:
1. Calcular distancias reales entre agentes (Lomnitz: la cercana fsica
   predice probabilidad de interaccin).
2. Visualizar el territorio y la red de relaciones sobre el mapa.
3. Investigar propagacin de chismes segn topologa fsica (Dunbar +
   proximidad geogrfica).
4. Documentar manipulacin social sembrando rumores en nodos geogrficos
   estratgicos (taberna, tienda, escuela, plaza).

METODOLOGA
===========
- Sistema de coordenadas cartesianas locales:
    * Origen: Parque Bolvar (plaza principal de la cabecera, 0,0).
    * Eje X: +x hacia el ESTE (ro Magdalena), -x hacia el OESTE (montaas).
    * Eje Y: +y hacia el NORTE (va a Neiva, 60 km), -y hacia el SUR.
    * 1 unidad = 30 metros (resolucin: media cuadra).
    * Rango: x [-12, +12], y [-12, +12] -> dimetro cabecera ~720 m.

- Cada lugar tiene metadata forense:
    * id: identificadornico.
    * tipo: (residencial|comercial|institucional|religioso|recreativo|
             educativo|salud|seguridad|hidraulico|vereda|otro)
    * coords: tupla (x, y).
    * direccion: direccin aproximada estilo colombiano (Calle 5 # 4-32).
    * fuente: ("documentado"|"inferido"|"a_validar").
    * confianza: float 0.0-1.0 (1.0 = confirmado por operador huilense).
    * notas: texto libre para evidencia cualitativa.

FUENTES
=======
- F1: docs/agentes/01-biografias.md lneas 40-72 (mapa de 4 cuadras,
     documentado por operador).
- F2: Conocimiento pblico del Magdalena (este), Cordillera Central (oeste),
     Neiva al norte (60 km).
- F3: DANE/Tello divipola -> 12.908 hab cabecera 5.601, 575 msnm.
- F4: Eventos 2026 documentados en Diario del Huila (crisis acueducto,
     festival, minera, FARC).
- F5: Inferencia plausible (marcada confianza < 0.7) -> requiere validacin
     del operador huilense para promover a "documentado".

LIMITACIONES CONOCIDAS
======================
- L1: El mapa existente (F1) tiene una posible inconsistencia:
     "CARRERA 5 (OCCIDENTE - va a Neiva, 60 km)" -> geogrficamente la va
     a Neiva debera ir al NORTE. Marcado como "a_validar".
- L2: Veredas reales (nmero y nombres exactos) requieren validacin
     del operador; nombres propuestos son plausibles per divipola.
- L3: Coordenadas son estimaciones a resolucin de media cuadra; algunas
     podran tener error de 1-2 unidades (30-60 m).
"""

# ===========================================================================
# CATLOGO DE EDIFICIOS DE LA CABECERA
# ===========================================================================

EDIFICIOS = {
    # --- PLAZA Y ENTORNO INMEDIATO ---
    "plaza_bolivar": {
        "tipo": "recreativo",
        "coords": (0, 0),
        "direccion": "Parque Principal, carrera 5 con calle 5",
        "nombre_comun": "El Parque",
        "fuente": "F1",
        "confianza": 0.95,
        "notas": "Nodo central de la cabecera. Lugar de encuentro maana "
                 "(ancianos tomando tinto) y tarde (jvenes despus del "
                 "Festival). Frente a la Iglesia.",
    },
    "iglesia_san_antonio": {
        "tipo": "religioso",
        "coords": (0, 1),
        "direccion": "Parque Bolvar, costado norte",
        "nombre_comun": "La Iglesia",
        "fuente": "F1",
        "confianza": 0.95,
        "notas": "Iglesia principal. Misa 6:00 am (ancianos), 7:00 pm "
                 "(adultos). Padre Cecilio desde 1995. Bautizos, matrimonios, "
                 "funerales: aqu se formalizan los vnculos.",
    },
    "tanque_agua_elevado": {
        "tipo": "hidraulico",
        "coords": (-1, 3),
        "direccion": "Detrs de la iglesia, calle 6",
        "nombre_comun": "El Tanque",
        "fuente": "F1",
        "confianza": 0.9,
        "notas": "VACO desde 5 abril 2026. Creciente del ro Villavieja "
                 "rompi tubera. Smbolo de la crisis. Simboliza la "
                 "impotencia de la alcalda.",
    },
    "alcaldia": {
        "tipo": "institucional",
        "coords": (-1, 1),
        "direccion": "Carrera 5 # 5-32 (esquina NW)",
        "nombre_comun": "La Alcalda",
        "fuente": "F1",
        "confianza": 0.95,
        "notas": "Don Fernando Solano Gmez. 2 pisos. Secretaria en puerta. "
                 "Investigacin Contralora por sobrecostos acueducto.",
    },
    "personeria": {
        "tipo": "institucional",
        "coords": (-2, 1),
        "direccion": "Carrera 5 # 5-28 (al lado de alcalda)",
        "nombre_comun": "La Personera",
        "fuente": "F1",
        "confianza": 0.8,
        "notas": "Doa Beatriz Vallejo Losada. Defensa derechos humanos. "
                 "Punto donde VIF escala a institucional.",
    },
    "casa_cural": {
        "tipo": "residencial",
        "coords": (-1, 2),
        "direccion": "Carrera 5 # 5-40 (NW del parque)",
        "nombre_comun": "La Casa Cural",
        "fuente": "F1",
        "confianza": 0.85,
        "notas": "Residencia del Padre Cecilio. Recibe visitas de consejo "
                 "espiritual y arreglos polticos (es de los pocos donde "
                 "ancianos rivales van juntos).",
    },
    "tienda_dona_rosa": {
        "tipo": "comercial",
        "coords": (-1, -1),
        "direccion": "Carrera 5 # 4-21 (esquina SW)",
        "nombre_comun": "La Tienda de Rosa",
        "fuente": "F1",
        "confianza": 0.95,
        "notas": "Doa Rosa Elvira Trujillo. 50+ aos all. ES EL EPICENTRO "
                 "DEL CHISME CABECERA. Vende a crdito (control social). "
                 "Horario 6:00-21:00. Domingos cerrado.",
    },
    "inspeccion": {
        "tipo": "institucional",
        "coords": (-2, -1),
        "direccion": "Carrera 5 # 4-17 (al lado de la tienda)",
        "nombre_comun": "La Inspeccin",
        "fuente": "F1",
        "confianza": 0.9,
        "notas": "Don Sigifredo Quintero Perdomo. Conflictos de linderos, "
                 "multas, permisos. Aparentemente neutral; en realidad "
                 "favorece al Patrn (compadres).",
    },
    "panaderia_mercedes": {
        "tipo": "comercial",
        "coords": (-1, 2),
        "direccion": "Carrera 5 # 5-44 (esquina NW)",
        "nombre_comun": "La Panadera",
        "fuente": "F1",
        "confianza": 0.95,
        "notas": "Doa Mercedes Pinilla. 4:30 am comienza. Pan, roscones, "
                 "buuelos. Vende fiado. Tambin punto de chisme (menos "
                 "que la tienda).",
    },
    "botica_eliseo": {
        "tipo": "salud",
        "coords": (-1, -2),
        "direccion": "Calle 4 # 5-23 (esquina SW)",
        "nombre_comun": "La Botica",
        "fuente": "F1",
        "confianza": 0.95,
        "notas": "Don Eliseo Mendoza. Farmacia + consulta menor. Tambin "
                 "atiende VIF (enfermermedad psicosomtica). Vecino de "
                 "comisara -> reportes cruzados.",
    },
    "comisaria": {
        "tipo": "institucional",
        "coords": (-2, -2),
        "direccion": "Calle 4 # 5-19 (al lado de botica)",
        "nombre_comun": "La Comisara",
        "fuente": "F1",
        "confianza": 0.9,
        "notas": "Patricia Losada Motta. Familia, VIF, menores. "
                 "Conflictos conyugales. Vecina de botica -> protocolo "
                 "cruzado VIF.",
    },
    "estacion_policia": {
        "tipo": "seguridad",
        "coords": (1, -1),
        "direccion": "Carrera 6 # 4-22 (esquina SE)",
        "nombre_comun": "La Estacin",
        "fuente": "F1",
        "confianza": 0.95,
        "notas": "Capitn Hernn Arturo Prez Lozano. 2 motos, 8 policas. "
                 "Atiende rias, hurtos menores, VIF. Coordinador con "
                 "subintendente veredas.",
    },
    "banco_agrario": {
        "tipo": "comercial",
        "coords": (0, -1),
        "direccion": "Calle 5 # 5-50 (al lado del parque)",
        "nombre_comun": "El Banco",
        "fuente": "F5",
        "confianza": 0.7,
        "notas": "Don Hermes.nico banco. Viernes: pagos familias, "
                 "chisme financiero. Marcado a_validar direccin exacta.",
    },

    # --- SERVICIOS PBLICOS Y EQUIPAMIENTOS ---
    "hospital_san_antonio": {
        "tipo": "salud",
        "coords": (3, 1),
        "direccion": "Va al Malecn, km 1",
        "nombre_comun": "El Hospital",
        "fuente": "F5",
        "confianza": 0.8,
        "notas": "Don Octavio. ESE departamental. Urgencias 24h. "
                 "Remisin a Neiva en ambulancia (1 hora). Crisis "
                 "acueducto: hospital recibi agua de carrotanque.",
    },
    "ie_tello": {
        "tipo": "educativo",
        "coords": (-4, 1),
        "direccion": "Va al occidente, km 0.3",
        "nombre_comun": "La Escuela",
        "fuente": "F5",
        "confianza": 0.75,
        "notas": "Institucin Educativa Tello. Preescolar + primaria + "
                 "secundaria. Sede principal. Profesora Aurora directora. "
                 "15 nios simulados (4-17 aos).",
    },
    "ie_los_pinos": {
        "tipo": "educativo",
        "coords": (5, -3),
        "direccion": "Va al sur, km 1.5",
        "nombre_comun": "Los Pinos",
        "fuente": "F5",
        "confianza": 0.6,
        "notas": "Sede rural (secundaria). Puede no existir con ese "
                 "nombre -> a_validar.",
    },
    "coliseo_cubierto": {
        "tipo": "recreativo",
        "coords": (5, 2),
        "direccion": "Va al oriente, km 0.4",
        "nombre_comun": "El Coliseo",
        "fuente": "F5",
        "confianza": 0.7,
        "notas": "Eventos deportivos, Festival del Bambuco. Punto "
                 "concentracin Festival.",
    },
    "cementerio": {
        "tipo": "otro",
        "coords": (-7, 0),
        "direccion": "Va al occidente, km 0.6",
        "nombre_comun": "El Cementerio",
        "fuente": "F5",
        "confianza": 0.7,
        "notas": "Misa de difuntos, Halloween (vspera). Vnculo fuerte "
                 "ancianos.",
    },
    "matadero": {
        "tipo": "otro",
        "coords": (5, -4),
        "direccion": "Va al sur, km 1",
        "nombre_comun": "El Matadero",
        "fuente": "F5",
        "confianza": 0.6,
        "notas": "Matanza lunes y jueves. A_validar ubicacin.",
    },
    "estadio_municipal": {
        "tipo": "recreativo",
        "coords": (-5, 2),
        "direccion": "Va al occidente, km 0.4",
        "nombre_comun": "La Cancha",
        "fuente": "F1",
        "confianza": 0.9,
        "notas": "Ftbol domingos, bsquet, microftbol. Frente al "
                 "parque (F1) o al occidente (mapa actual). A_validar.",
    },
    "parque_infantil": {
        "tipo": "recreativo",
        "coords": (1, 2),
        "direccion": "Calle 6 # 5-30",
        "nombre_comun": "El Parque",
        "fuente": "F5",
        "confianza": 0.6,
        "notas": "Juegos para nios. Punto de socializacin infantil. "
                 "Madres y abuelas llevan a nietos. A_validar.",
    },
    "taberna_la_mocha": {
        "tipo": "comercial",
        "coords": (2, 0),
        "direccion": "Carrera 6 # 5-15",
        "nombre_comun": "La Taberna",
        "fuente": "F5",
        "confianza": 0.7,
        "notas": "Alcohol, rumba viernes-sbado. Super-spreader de "
                 "chismes nocturnos. Tambin punto de conflicto "
                 "(rias).",
    },
    "billar_el_descanso": {
        "tipo": "comercial",
        "coords": (-3, 1),
        "direccion": "Carrera 5 # 5-65",
        "nombre_comun": "El Billar",
        "fuente": "F5",
        "confianza": 0.65,
        "notas": "Billar masculino adulto. Otro super-spreader. Ms "
                 "moderado que la taberna. A_validar.",
    },
    "farmacia_san_jose": {
        "tipo": "salud",
        "coords": (-1, 2),
        "direccion": "Calle 6 # 5-21",
        "nombre_comun": "La Farmacia",
        "fuente": "F5",
        "confianza": 0.6,
        "notas": "Distinta a la botica (Eliseo). Cadena. A_validar.",
    },
    "cancha_multiple": {
        "tipo": "recreativo",
        "coords": (2, -2),
        "direccion": "Calle 4 # 6-12",
        "nombre_comun": "La Cancha Mltiple",
        "fuente": "F5",
        "confianza": 0.6,
        "notas": "Microftbol, voleibol, bsquet. Punto de encuentro "
                 "jvenes despus de clases.",
    },

    # --- VEREDAS (FUERA DE CABECERA) ---
    # Tello tiene 6 veredas per DANE. Nombres plausibles; a_validar.
    "vereda_anacleto_garcia": {
        "tipo": "vereda",
        "coords": (-9, 2),
        "direccion": "Va al occidente-norte, km 8",
        "nombre_comun": "Anacleto",
        "fuente": "F5",
        "confianza": 0.6,
        "notas": "Vereda montaosa. Jornaleros, fincas cafeteras. "
                 "Lder comunal: posiblemente citado por FARC. "
                 "A_validar.",
    },
    "vereda_la_encarnacion": {
        "tipo": "vereda",
        "coords": (-7, -3),
        "direccion": "Va al sur-occidente, km 6",
        "nombre_comun": "La Encarnacin",
        "fuente": "F5",
        "confianza": 0.6,
        "notas": "Vereda montaosa. A_validar nombre.",
    },
    "vereda_la_union": {
        "tipo": "vereda",
        "coords": (-5, -8),
        "direccion": "Va al sur-occidente, km 10",
        "nombre_comun": "La Unin",
        "fuente": "F5",
        "confianza": 0.6,
        "notas": "Vereda ms alejada. Don Pompilio ganadero vive "
                 "aqu (a_validar: en biografa dice 'finca').",
    },
    "vereda_san_andres": {
        "tipo": "vereda",
        "coords": (-9, -2),
        "direccion": "Va al occidente, km 8",
        "nombre_comun": "San Andrs",
        "fuente": "F5",
        "confianza": 0.6,
        "notas": "A_validar nombre. Cercana a La Encarnacin.",
    },
    "vereda_santa_marta": {
        "tipo": "vereda",
        "coords": (-6, 6),
        "direccion": "Va al norte-occidente, km 6",
        "nombre_comun": "Santa Marta",
        "fuente": "F5",
        "confianza": 0.6,
        "notas": "A_validar nombre. Hacia Neiva.",
    },
    "vereda_cerro_neiva": {
        "tipo": "vereda",
        "coords": (-10, 5),
        "direccion": "Va al nor-occidente, km 10",
        "nombre_comun": "Cerro Neiva",
        "fuente": "F5",
        "confianza": 0.6,
        "notas": "Cerro homnimo a Neiva. Posible minera ilegal. "
                 "Don Pompilio ganadero o Caliche minero. A_validar.",
    },

    # --- ROS Y REFERENTES GEOGRFICOS NATURALES ---
    "rio_magdalena": {
        "tipo": "otro",
        "coords": (12, 0),
        "direccion": "Oriente, lmite municipal",
        "nombre_comun": "El Ro",
        "fuente": "F2",
        "confianza": 0.95,
        "notas": "Lmite oriental del municipio. Pescadores: Brayan "
                 "(joven). Crecientes en abril = crisis acueducto.",
    },
    "malecón": {
        "tipo": "recreativo",
        "coords": (8, 0),
        "direccion": "Va al ro km 1.2",
        "nombre_comun": "El Malecn",
        "fuente": "F5",
        "confianza": 0.7,
        "notas": "Mirador al ro. Punto de paseo familiar y de "
                 "jvenes (atardecer). A_validar.",
    },
    "rio_villavieja": {
        "tipo": "otro",
        "coords": (8, -8),
        "direccion": "Sur-oriente",
        "nombre_comun": "Ro Villavieja",
        "fuente": "F1",
        "confianza": 0.9,
        "notas": "Afluente del Magdalena. Creciente 5 abril 2026 "
                 "rompi tubera acueducto. Conflicto: hay tesis de "
                 "sobrecostos de reparacin.",
    },
}


# ===========================================================================
# ASIGNACIN GEOGRFICA DE AGENTES
# ===========================================================================
# Cada agente de docs/agentes/01-biografias.md tiene casa_id y trabajo_id
# con coordenadas (x, y). El campo "casa" y "trabajo" referencian un id
# de EDIFICIOS. La "ruta_diaria" lista lugares por hora.

AGENTES_GEO = {
    # --- ANCIANOS (65+) ---
    "don_eliecer_patron": {
        "generacion": "anciano",
        "casa": "finca_matarredonda",  # NO en EDIFICIOS -> coords propias
        "casa_coords": (-8, -2),
        "trabajo": "finca_matarredonda",
        "trabajo_coords": (-8, -2),
        "ruta_diaria": [
            ("05:00", "casa", "despertar"),
            ("06:00", "iglesia_san_antonio", "misa"),
            ("07:00", "finca_matarredonda", "revisar animales"),
            ("12:00", "finca_matarredonda", "almorzar"),
            ("18:00", "plaza_bolivar", "tinto con Rosalío"),
            ("20:00", "casa", "comida + TV"),
        ],
        "movilidad": "a_pie_y_caballo",
    },
    "dona_prudencia_partera": {
        "casa": "casa_partera",
        "casa_coords": (-2, -3),
        "trabajo": "casa_partera",  # atiende en casa
        "trabajo_coords": (-2, -3),
        "ruta_diaria": [
            ("05:00", "casa", "despertar"),
            ("06:30", "iglesia_san_antonio", "rosario"),
            ("08:00", "casa", "atender partos/pacientes"),
            ("12:00", "casa", "almorzar"),
            ("16:00", "tienda_dona_rosa", "visitar"),
            ("20:00", "casa", "comida"),
        ],
        "movilidad": "a_pie",
    },
    "don_rosalio_rival": {
        "casa": "finca_quintero",
        "casa_coords": (-9, -1),
        "trabajo": "finca_quintero",
        "trabajo_coords": (-9, -1),
        "ruta_diaria": [
            ("05:00", "casa", "despertar"),
            ("06:00", "iglesia_san_antonio", "misa"),
            ("07:30", "finca_quintero", "revisar finca"),
            ("12:00", "finca_quintero", "almorzar"),
            ("18:00", "plaza_bolivar", "tinto con Eliécer (rival)"),
            ("20:00", "casa", "comida"),
        ],
        "movilidad": "a_pie_y_caballo",
    },
    "padre_cecilio_cura": {
        "casa": "casa_cural",
        "casa_coords": (-1, 2),
        "trabajo": "iglesia_san_antonio",
        "trabajo_coords": (0, 1),
        "ruta_diaria": [
            ("05:00", "casa_cural", "oracin"),
            ("06:00", "iglesia_san_antonio", "misa"),
            ("07:30", "casa_cural", "desayuno"),
            ("09:00", "iglesia_san_antonio", "oficina parroquial"),
            ("12:00", "casa_cural", "almorzar"),
            ("15:00", "visitas_pastorales", "visitar enfermos"),
            ("18:00", "iglesia_san_antonio", "misa vespertina"),
            ("20:00", "casa_cural", "comida + lectura"),
        ],
        "movilidad": "a_pie",
    },
    "dona_rosa_tendera": {
        "casa": "tienda_dona_rosa",
        "casa_coords": (-1, -1),  # encima de la tienda
        "trabajo": "tienda_dona_rosa",
        "trabajo_coords": (-1, -1),
        "ruta_diaria": [
            ("05:30", "tienda_dona_rosa", "abrir"),
            ("12:00", "tienda_dona_rosa", "almorzar"),
            ("13:00", "tienda_dona_rosa", "abrir"),
            ("21:00", "tienda_dona_rosa", "cerrar"),
        ],
        "movilidad": "a_pie",
    },
    "dona_lucia_maestra_jubilada": {
        "casa": "casa_lucia",
        "casa_coords": (0, 2),
        "trabajo": None,  # jubilada
        "ruta_diaria": [
            ("05:00", "casa", "despertar"),
            ("06:30", "iglesia_san_antonio", "misa"),
            ("08:00", "ie_tello", "voluntaria (reforzamiento)"),
            ("12:00", "casa", "almorzar"),
            ("16:00", "plaza_bolivar", "pasear"),
            ("19:00", "casa", "comida"),
        ],
        "movilidad": "a_pie",
    },

    # --- ADULTOS (35-60) ---
    "don_fernando_alcalde": {
        "casa": "casa_alcalde",
        "casa_coords": (0, 1),
        "trabajo": "alcaldia",
        "trabajo_coords": (-1, 1),
        "ruta_diaria": [
            ("06:00", "casa", "despertar"),
            ("07:00", "alcaldia", "reunin gabinete"),
            ("12:00", "casa", "almorzar"),
            ("13:00", "alcaldia", "gestin"),
            ("18:00", "alcaldia", "evento/reunin"),
            ("20:00", "casa", "comida"),
        ],
        "movilidad": "moto_oficial",
    },
    "capitan_hernan_policia": {
        "casa": "casa_capitan",
        "casa_coords": (1, -2),
        "trabajo": "estacion_policia",
        "trabajo_coords": (1, -1),
        "ruta_diaria": [
            ("05:30", "casa", "despertar"),
            ("06:30", "estacion_policia", "turno"),
            ("12:00", "estacion_policia", "almorzar"),
            ("18:00", "casa", "descansar"),
            ("19:00", "estacion_policia", "turno noche"),
        ],
        "movilidad": "moto_oficial",
    },
    "subintendente_saavedra": {
        "casa": "vereda_anacleto_garcia",
        "casa_coords": (-9, 2),
        "trabajo": "vereda_anacleto_garcia",  # patrulla veredas
        "trabajo_coords": (-9, 2),
        "ruta_diaria": [
            ("05:00", "casa", "despertar"),
            ("06:00", "vereda_anacleto_garcia", "patrullar"),
            ("12:00", "casa", "almorzar"),
            ("13:00", "vereda_anacleto_garcia", "patrullar"),
            ("19:00", "casa", "comida"),
        ],
        "movilidad": "moto",
    },
    "beatriz_personera": {
        "casa": "casa_beatriz",
        "casa_coords": (1, 3),
        "trabajo": "personeria",
        "trabajo_coords": (-2, 1),
        "ruta_diaria": [
            ("06:30", "casa", "despertar"),
            ("07:30", "personeria", "oficina"),
            ("12:00", "casa", "almorzar"),
            ("13:00", "personeria", "oficina"),
            ("18:00", "casa", "comida"),
        ],
        "movilidad": "a_pie_y_moto",
    },
    "don_sigifredo_inspector": {
        "casa": "casa_sigifredo",
        "casa_coords": (-3, -2),
        "trabajo": "inspeccion",
        "trabajo_coords": (-2, -1),
        "ruta_diaria": [
            ("06:00", "casa", "despertar"),
            ("07:00", "inspeccion", "oficina"),
            ("12:00", "casa", "almorzar"),
            ("13:00", "inspeccion", "oficina"),
            ("18:00", "tienda_dona_rosa", "chisme"),
            ("20:00", "casa", "comida"),
        ],
        "movilidad": "a_pie",
    },
    "patricia_comisaria": {
        "casa": "casa_patricia",
        "casa_coords": (-1, -3),
        "trabajo": "comisaria",
        "trabajo_coords": (-2, -2),
        "ruta_diaria": [
            ("06:30", "casa", "despertar"),
            ("07:30", "comisaria", "oficina"),
            ("12:00", "casa", "almorzar"),
            ("13:00", "comisaria", "oficina"),
            ("18:00", "casa", "comida"),
        ],
        "movilidad": "a_pie",
    },
    "dona_mercedes_panadera": {
        "casa": "panaderia_mercedes",
        "casa_coords": (-1, 2),
        "trabajo": "panaderia_mercedes",
        "trabajo_coords": (-1, 2),
        "ruta_diaria": [
            ("03:00", "panaderia_mercedes", "amasar"),
            ("06:00", "panaderia_mercedes", "vender"),
            ("12:00", "panaderia_mercedes", "almorzar"),
            ("13:00", "panaderia_mercedes", "vender"),
            ("20:00", "panaderia_mercedes", "cerrar"),
        ],
        "movilidad": "a_pie",
    },
    "don_eliseo_boticario": {
        "casa": "botica_eliseo",
        "casa_coords": (-1, -2),
        "trabajo": "botica_eliseo",
        "trabajo_coords": (-1, -2),
        "ruta_diaria": [
            ("06:30", "botica_eliseo", "abrir"),
            ("12:00", "botica_eliseo", "almorzar"),
            ("13:00", "botica_eliseo", "abrir"),
            ("20:00", "botica_eliseo", "cerrar"),
        ],
        "movilidad": "a_pie",
    },
    "aurora_maestra": {
        "casa": "casa_aurora",
        "casa_coords": (-3, 0),
        "trabajo": "ie_tello",
        "trabajo_coords": (-4, 1),
        "ruta_diaria": [
            ("05:30", "casa", "despertar"),
            ("07:00", "ie_tello", "clase"),
            ("12:00", "casa", "almorzar"),
            ("13:00", "ie_tello", "clase"),
            ("17:00", "casa", "regresar"),
        ],
        "movilidad": "a_pie",
    },
    "edilma_secretaria": {
        "casa": "casa_edilma",
        "casa_coords": (-2, 2),
        "trabajo": "alcaldia",
        "trabajo_coords": (-1, 1),
        "ruta_diaria": [
            ("06:00", "casa", "despertar"),
            ("07:00", "alcaldia", "oficina"),
            ("12:00", "casa", "almorzar"),
            ("13:00", "alcaldia", "oficina"),
            ("17:00", "casa", "regresar"),
        ],
        "movilidad": "a_pie",
    },
    "don_abelardo_conductor": {
        "casa": "casa_abelardo",
        "casa_coords": (1, 2),
        "trabajo": "estacion_policia",  # conduce patrulla
        "trabajo_coords": (1, -1),
        "ruta_diaria": [
            ("05:00", "casa", "despertar"),
            ("06:00", "estacion_policia", "turno"),
            ("18:00", "casa", "regresar"),
        ],
        "movilidad": "patrulla",
    },
    "jhon_jairo_sacristan": {
        "casa": "casa_jhon_jairo",
        "casa_coords": (-1, 0),
        "trabajo": "iglesia_san_antonio",
        "trabajo_coords": (0, 1),
        "ruta_diaria": [
            ("05:00", "casa", "despertar"),
            ("05:30", "iglesia_san_antonio", "preparar misa"),
            ("07:00", "iglesia_san_antonio", "campanero"),
            ("12:00", "casa", "almorzar"),
            ("17:00", "iglesia_san_antonio", "misa vespertina"),
            ("19:00", "casa", "comida"),
        ],
        "movilidad": "a_pie",
    },
    "don_octavio_medico": {
        "casa": "casa_octavio",
        "casa_coords": (2, 2),
        "trabajo": "hospital_san_antonio",
        "trabajo_coords": (3, 1),
        "ruta_diaria": [
            ("06:00", "casa", "despertar"),
            ("07:00", "hospital_san_antonio", "consulta"),
            ("16:00", "hospital_san_antonio", "urgencias"),
            ("20:00", "casa", "comida"),
        ],
        "movilidad": "a_pie",
    },
    "don_emigdio_jubilado": {
        "casa": "casa_emigdio",
        "casa_coords": (2, -1),
        "trabajo": "taberna_la_mocha",  # pasa el da
        "trabajo_coords": (2, 0),
        "ruta_diaria": [
            ("08:00", "casa", "despertar tarde"),
            ("10:00", "taberna_la_mocha", "tinto"),
            ("12:00", "taberna_la_mocha", "almorzar"),
            ("14:00", "taberna_la_mocha", "billar"),
            ("20:00", "taberna_la_mocha", "comida + trago"),
        ],
        "movilidad": "a_pie",
    },

    # --- JVENES (17-34) ---
    "laura_reina": {
        "casa": "casa_laura",
        "casa_coords": (0, -1),
        "trabajo": None,  # estudiante + reina
        "ruta_diaria": [
            ("07:00", "casa", "despertar"),
            ("09:00", "alcaldia", "gestin reinados"),
            ("13:00", "casa", "almorzar"),
            ("15:00", "plaza_bolivar", "ensayo"),
            ("20:00", "casa", "comida"),
        ],
        "movilidad": "a_pie",
    },
    "pipe_hincha": {
        "casa": "casa_pipe",
        "casa_coords": (2, 1),
        "trabajo": "taberna_la_mocha",  # informal
        "trabajo_coords": (2, 0),
        "ruta_diaria": [
            ("09:00", "casa", "despertar tarde"),
            ("11:00", "taberna_la_mocha", "almorzar"),
            ("14:00", "estadio_municipal", "ftbol"),
            ("19:00", "taberna_la_mocha", "rumba"),
        ],
        "movilidad": "moto",
    },
    "mariana_universitaria": {
        "casa": "casa_mariana",
        "casa_coords": (1, 0),
        "trabajo": None,  # estudia fuera
        "ruta_diaria": [
            ("06:00", "casa", "despertar"),
            ("07:00", "bus_neiva", "viajar a Neiva (U. Surcolombiana)"),
            ("18:00", "casa", "regresar"),
        ],
        "movilidad": "bus",
    },
    "caliche_minero": {
        "casa": "casa_caliche",
        "casa_coords": (-1, -2),
        "trabajo": "vereda_cerro_neiva",  # minera ilegal
        "trabajo_coords": (-10, 5),
        "ruta_diaria": [
            ("04:00", "casa", "despertar"),
            ("05:00", "vereda_cerro_neiva", "mina"),
            ("16:00", "casa", "regresar"),
            ("19:00", "taberna_la_mocha", "vender oro"),
        ],
        "movilidad": "moto",
    },
    "valentina_secretaria_joven": {
        "casa": "casa_valentina",
        "casa_coords": (0, 2),
        "trabajo": "alcaldia",
        "trabajo_coords": (-1, 1),
        "ruta_diaria": [
            ("06:00", "casa", "despertar"),
            ("07:00", "alcaldia", "oficina"),
            ("12:00", "casa", "almorzar"),
            ("13:00", "alcaldia", "oficina"),
            ("17:00", "casa", "regresar"),
        ],
        "movilidad": "a_pie",
    },
    "jhon_eliecer_hijo_patron": {
        "casa": "finca_matarredonda",
        "casa_coords": (-8, -2),
        "trabajo": "finca_matarredonda",
        "trabajo_coords": (-8, -2),
        "ruta_diaria": [
            ("05:00", "casa", "despertar"),
            ("07:00", "finca_matarredonda", "revisar animales"),
            ("12:00", "finca_matarredonda", "almorzar"),
            ("18:00", "plaza_bolivar", "tinto con padre"),
            ("20:00", "casa", "comida"),
        ],
        "movilidad": "a_pie_y_caballo",
    },
}


# ===========================================================================
# UTILIDADES
# ===========================================================================

# Mapeo entre mis slugs (geo_tello) y los slugs de biografia (prompt_builder).
# Esto permite integrar la geo con el sistema de prompts ya validado.
SLUG_BIO = {
    "don_eliecer_patron": "elicer-perdomo-motta-el-patrn",
    "dona_prudencia_partera": "prudencia-gutirrez-vda-de-perdomo-la-partera",
    "don_rosalio_rival": "rosalo-quintero-hernndez-el-rival",
    "don_fernando_alcalde": "fernando-solano-gmez-el-alcalde",
    "padre_cecilio_cura": "cecilio-ramrez-lozano-el-cura",
    "dona_rosa_tendera": "rosa-elvira-trujillo-de-perdomo-la-tendera",
    "dona_mercedes_panadera": "mercedes-pinilla-la-panadera",
    "don_eliseo_boticario": "eliseo-mendoza-trujillo-el-boticario",
    "aurora_maestra": "aurora-losada-motta-la-maestra",
    "edilma_secretaria": "sra-edilma-campos-trujillo-la-secretaria",
    "don_abelardo_conductor": "abelardo-caycedo-perdomo-el-conductor",
    "jhon_jairo_sacristan": "jhon-jairo-motta-perdomo-el-sacristn",
    "capitan_hernan_policia": "capitn-hernn-arturo-prez-lozano-el-comandante",
    "subintendente_saavedra": "subintendente-manuel-saavedra-trujillo-el-patrullero-del-pueblo",
    "beatriz_personera": "beatriz-vallejo-losada-la-personera",
    "don_sigifredo_inspector": "sigifredo-quintero-perdomo-el-inspector",
    "patricia_comisaria": "patricia-losada-motta-la-comisaria",
    "laura_reina": "laura-sofa-meneses-la-reina-del-pueblo",
    "pipe_hincha": "andrs-felipe-pipe-ospina-el-hincha",
    "mariana_universitaria": "mariana-daz-polanco-la-universitaria",
    "caliche_minero": "carlos-andrs-caliche-vargas-el-minero-ilegal",
    "valentina_secretaria_joven": "valentina-losada-la-secretaria-joven",
    "jhon_eliecer_hijo_patron": "jhon-elicer-perdomo-el-hijo-del-patrn",
    "dona_lucia_maestra_jubilada": "luca-ramrez-la-maestra-jubilada",
    "don_emigdio_jubilado": "emigdio-surez-el-jubilado-que-no-sirve",
    "dona_prudencia_partera": "prudencia-gutirrez-vda-de-perdomo-la-partera",
    "jhon_jairo_sacristan": "jhon-jairo-motta-perdomo-el-sacristn",
}


def distancia(a, b):
    """Distancia euclidiana entre dos puntos (x, y)."""
    import math
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def distancia_metros(a, b):
    """Distancia en metros (1 unidad = 30 m)."""
    return distancia(a, b) * 30


def agentes_en_rango(coords, radio_metros):
    """Lista de agentes cuyo lugar principal (casa) cae dentro del radio."""
    radio_unidades = radio_metros / 30
    en_rango = []
    for nombre, ag in AGENTES_GEO.items():
        d = distancia(coords, ag["casa_coords"])
        if d <= radio_unidades:
            en_rango.append((nombre, d))
    return sorted(en_rango, key=lambda x: x[1])


def matriz_distancias():
    """Matriz NxN de distancias entre casas (en metros)."""
    nombres = list(AGENTES_GEO.keys())
    matriz = {}
    for n1 in nombres:
        matriz[n1] = {}
        for n2 in nombres:
            matriz[n1][n2] = distancia_metros(
                AGENTES_GEO[n1]["casa_coords"],
                AGENTES_GEO[n2]["casa_coords"]
            )
    return matriz


if __name__ == "__main__":
    print(f"Edificios catalogados: {len(EDIFICIOS)}")
    print(f"Agentes georreferenciados: {len(AGENTES_GEO)}")
    print()
    print("--- Ejemplo: agentes a 200 m de la Plaza ---")
    for nombre, d in agentes_en_rango((0, 0), 200):
        print(f"  {nombre}: {d * 30:.0f} m")
    print()
    print("--- Ejemplo: distancias entre actores clave ---")
    pares = [
        ("dona_rosa_tendera", "don_sigifredo_inspector"),
        ("dona_rosa_tendera", "don_eliecer_patron"),
        ("padre_cecilio_cura", "don_eliecer_patron"),
        ("don_fernando_alcalde", "capitan_hernan_policia"),
    ]
    for n1, n2 in pares:
        d = distancia_metros(
            AGENTES_GEO[n1]["casa_coords"],
            AGENTES_GEO[n2]["casa_coords"],
        )
        print(f"  {n1} <-> {n2}: {d:.0f} m")
