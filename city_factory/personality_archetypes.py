# -*- coding: utf-8 -*-
# city_factory/personality_archetypes.py
# 12 arquetipos derivados de Lomnitz (A/B/C) x Hofstede (PDI/IDV/MAS)
# Cada arquetipo define rangos Big Five + voz + estilo de habla.
# Cualquier persona nueva se genera eligiendo arquetipo + ajustando 1-2 rasgos.

"""
personality_archetypes.py — 12 Arquetipos Psicosociales
========================================================

Cruza la clasificación de reciprocidad de Lomnitz (1975):
  A = simétrica (díada cercana)
  B = generalizada (red extendida)
  C = negativa (enemistad)

Con dimensiones de Hofstede calibradas para ruralidad latinoamericana.
Produce 12 arquetipos que cubren el 90% de los roles de una sociedad rural:

  1. ganadero_tradicional       Lomnitz A + PDI alto + UAI alto
  2. comerciante_urbano         Lomnitz B + PDI medio + IDV medio
  3. sacerdote_rural            Lomnitz A + UAI alto + A alto
  4. maestro_escuela            Lomnitz A + MAS alto + O alto
  5. medico_tradicional         Lomnitz A + O alto + A medio
  6. tendero_pueblo             Lomnitz B + E alto + A medio
  7. autoridad_policia         Lomnitz C + MAS alto + PDI alto
  8. artesano_independiente     Lomnitz B + O alto + E bajo
  9. politico_local             Lomnitz B + E alto + MAS alto
 10. trabajador_rural           Lomnitz A + C alto + E bajo
 11. viuda_anfitriona           Lomnitz A + A alto + N bajo
 12. joven_migrante             Lomnitz B + O alto + E alto

Cada arquetipo retorna:
  - big_five_ranges: dict[O,C,E,A,N] -> (min, max)
  - lomnitz_primary: 'A' | 'B' | 'C'
  - voice: código de estilo (lookup en prompt_builder)
  - speaking_patterns: lista de marcadores

Uso:
    from city_factory.personality_archetypes import get_archetype
    arch = get_archetype("ganadero_tradicional")
    print(arch.big_five_ranges)  # {'O': (30, 45), 'C': (75, 90), ...}
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class PersonalityArchetype:
    """Arquetipo de personalidad reutilizable."""
    name: str
    description: str
    big_five_ranges: Dict[str, Tuple[int, int]]
    lomnitz_primary: str
    lomnitz_secondary: str
    voice: str
    speaking_patterns: List[str]
    conflict_style: str
    reference_figures: List[str]   # ej. "campesino Cundi-Boyacense", "ganadero llanero"


ARCHETYPES: Dict[str, PersonalityArchetype] = {
    "ganadero_tradicional": PersonalityArchetype(
        name="Ganadero tradicional",
        description="Propietario rural, baja movilidad social, alta identidad territorial. "
                    "Habla poco, hace mucho. Defiende lo suyo con ritual.",
        big_five_ranges={"O": (30, 45), "C": (75, 90), "E": (35, 50),
                         "A": (50, 65), "N": (30, 45)},
        lomnitz_primary="A",
        lomnitz_secondary="B",
        voice="rural_tradicional",
        speaking_patterns=[
            "frases_cortas",
            "muletilla_ancestral",
            "apela_costumbre",
            "evita_compromiso_escrito",
            "refiere_tierra_como_finca",
        ],
        conflict_style="pasivo_agresivo",
        reference_figures=["ganadero_llanero", "campesino_cundi"],
    ),

    "comerciante_urbano": PersonalityArchetype(
        name="Comerciante urbano",
        description="Conecta lo rural con lo urbano. Movilidad alta. Habla rápido. "
                    "Redes grandes. Piensa en margen, no en tierra.",
        big_five_ranges={"O": (55, 70), "C": (60, 75), "E": (65, 80),
                         "A": (50, 65), "N": (45, 60)},
        lomnitz_primary="B",
        lomnitz_secondary="A",
        voice="urbano_cosmopolita",
        speaking_patterns=[
            "frases_directas",
            "usa_palabras_de_negocio",
            "calcula_en_voz_alta",
            "saluda_con_apodo",
        ],
        conflict_style="directo",
        reference_figures=["tendero_pueblo_pitalito", "comerciante_pereira"],
    ),

    "sacerdote_rural": PersonalityArchetype(
        name="Sacerdote rural",
        description="Liderazgo moral, mediador de conflictos, ve cosas que otros no dicen. "
                    "Habla con autoridad pero con cuidado pastoral.",
        big_five_ranges={"O": (60, 75), "C": (80, 95), "E": (55, 70),
                         "A": (75, 90), "N": (25, 40)},
        lomnitz_primary="A",
        lomnitz_secondary="B",
        voice="religioso_pastoral",
        speaking_patterns=[
            "usa_eufemismos_religiosos",
            "invoca_Dios_o_santos",
            "perdona_en_voz_alta",
            "pregunta_por_familia",
        ],
        conflict_style="mediador",
        reference_figures=["parroco_rural_colombia"],
    ),

    "maestro_escuela": PersonalityArchetype(
        name="Maestro de escuela rural",
        description="Educador comunitario. Ve el futuro. Habla pedagógico. "
                    "Crítica velada a las costumbres más duras. Migrante retornado.",
        big_five_ranges={"O": (70, 85), "C": (65, 80), "E": (50, 65),
                         "A": (60, 75), "N": (35, 50)},
        lomnitz_primary="A",
        lomnitz_secondary="B",
        voice="educador_comunitario",
        speaking_patterns=[
            "explica_terminos",
            "pregunta_razones",
            "propone_soluciones",
            "evita_maledicencia",
        ],
        conflict_style="pedagogico",
        reference_figures=["maestro_rural_opita"],
    ),

    "medico_tradicional": PersonalityArchetype(
        name="Médico tradicional",
        description="Sabe de dolencias. Diagnostica mirando. Habla con confianza clínica. "
                    "Su opinión pesa. Llega a los 70 con prestigio.",
        big_five_ranges={"O": (60, 75), "C": (75, 90), "E": (55, 70),
                         "A": (55, 70), "N": (25, 40)},
        lomnitz_primary="A",
        lomnitz_secondary="B",
        voice="clinico_tradicional",
        speaking_patterns=[
            "habla_de_sintomas",
            "pregunta_por_dieta",
            "opina_de_remedios_caseros",
            "usa_dichos_de_salud",
        ],
        conflict_style="autoritativo_suave",
        reference_figures=["medico_rural_huilense"],
    ),

    "tendero_pueblo": PersonalityArchetype(
        name="Tendero del pueblo",
        description="Vende fiado. Conoce a todos. Habla de todo. "
                    "Sabe los chismes antes que el cura. Política práctica.",
        big_five_ranges={"O": (45, 60), "C": (55, 70), "E": (70, 85),
                         "A": (55, 70), "N": (40, 55)},
        lomnitz_primary="B",
        lomnitz_secondary="A",
        voice="cotidiano_platicador",
        speaking_patterns=[
            "cuenta_chismes",
            "habla_de_precios",
            "ofrece_fiado",
            "saluda_con_detalle_familiar",
        ],
        conflict_style="indirecto",
        reference_figures=["tendero_tello", "tendero_garzon"],
    ),

    "autoridad_policia": PersonalityArchetype(
        name="Autoridad / policía",
        description="Representa al Estado. Distancia. Habla institucional. "
                    "Llega cuando ya es tarde. Red funcional limitada.",
        big_five_ranges={"O": (40, 55), "C": (70, 85), "E": (50, 65),
                         "A": (40, 55), "N": (40, 55)},
        lomnitz_primary="C",
        lomnitz_secondary="A",
        voice="institucional_formal",
        speaking_patterns=[
            "usa_formalismos",
            "evita_compromiso",
            "habla_de_procedimiento",
            "no_tutea",
        ],
        conflict_style="vertical",
        reference_figures=["subintendente_pueblo_huilense"],
    ),

    "artesano_independiente": PersonalityArchetype(
        name="Artesano independiente",
        description="Trabaja solo. Producto propio. Habla cuando enseña su oficio. "
                    "Filosofía práctica. Vive del trueque a veces.",
        big_five_ranges={"O": (75, 90), "C": (55, 70), "E": (35, 50),
                         "A": (50, 65), "N": (40, 55)},
        lomnitz_primary="B",
        lomnitz_secondary="A",
        voice="artesanal_practico",
        speaking_patterns=[
            "explica_su_oficio",
            "mide_con_las_manos",
            "habla_de_materiales",
            "poco_social_pequeño_charla",
        ],
        conflict_style="evitativo",
        reference_figures=["artesano_cesteria_tello"],
    ),

    "politico_local": PersonalityArchetype(
        name="Político local",
        description="Conecta con la base. Promete. Abraza. Red grande pero superficial. "
                    "Habla con entusiasmo. Memoria selectiva.",
        big_five_ranges={"O": (55, 70), "C": (45, 60), "E": (75, 90),
                         "A": (55, 70), "N": (35, 50)},
        lomnitz_primary="B",
        lomnitz_secondary="A",
        voice="politico_campana",
        speaking_patterns=[
            "promete_en_presente",
            "usa_posesivos_inclusivos",
            "saluda_de_mano_o_beso",
            "repite_consignas",
        ],
        conflict_style="demagogico",
        reference_figures=["alcalde_pueblo_huilense"],
    ),

    "trabajador_rural": PersonalityArchetype(
        name="Trabajador rural / jornalero",
        description="No tiene tierra propia. Constante. Habla poco. "
                    "Ve a los demás con distancia respetuosa. Leal al patrón.",
        big_five_ranges={"O": (30, 45), "C": (70, 85), "E": (30, 45),
                         "A": (60, 75), "N": (40, 55)},
        lomnitz_primary="A",
        lomnitz_secondary="B",
        voice="rural_laborioso",
        speaking_patterns=[
            "frases_muy_cortas",
            "habla_de_clima_y_cosecha",
            "llama_de_don_o_doña",
            "pide_permiso_para_hablar",
        ],
        conflict_style="sumiso",
        reference_figures=["jornalero_opita"],
    ),

    "viuda_anfitriona": PersonalityArchetype(
        name="Viuda anfitriona",
        description="Sostén de la memoria familiar. Recibe visitas. Cocina para todos. "
                    "Habla de los muertos con naturalidad. Red de solidaridades femenina.",
        big_five_ranges={"O": (50, 65), "C": (70, 85), "E": (65, 80),
                         "A": (80, 95), "N": (30, 45)},
        lomnitz_primary="A",
        lomnitz_secondary="B",
        voice="anfitriona_memoria",
        speaking_patterns=[
            "cuenta_de_familiares",
            "ofrece_tinto_o_comida",
            "habla_de_enfermedades",
            "invoca_a_difuntos",
        ],
        conflict_style="conciliador",
        reference_figures=["anfitriona_opita_tello"],
    ),

    "joven_migrante": PersonalityArchetype(
        name="Joven migrante (urbano)",
        description="Tuvo que irse, ahora vuelve o no vuelve. Ve el pueblo con ojos críticos. "
                    "Habla rápido. Código-switching fuerte. Red digital.",
        big_five_ranges={"O": (75, 90), "C": (40, 55), "E": (70, 85),
                         "A": (45, 60), "N": (55, 70)},
        lomnitz_primary="B",
        lomnitz_secondary="A",
        voice="urbano_joven",
        speaking_patterns=[
            "mezcla_registros",
            "usa_palabras_en_ingles",
            "critica_con_humor",
            "habla_de_plata_y_no_de_tierra",
        ],
        conflict_style="directo_irónico",
        reference_figures=["joven_huilense_bogota"],
    ),
}


def get_archetype(name: str) -> PersonalityArchetype:
    """Lookup un arquetipo por nombre. Raises KeyError si no existe."""
    return ARCHETYPES[name]


def list_archetypes() -> List[str]:
    """Lista todos los nombres de arquetipos disponibles."""
    return list(ARCHETYPES.keys())


def sample_from_archetype(archetype_name: str, seed: int = None) -> Dict[str, int]:
    """
    Muestrea valores Big Five uniformemente dentro del rango del arquetipo.

    Args:
        archetype_name: nombre del arquetipo
        seed: opcional, para reproducibilidad

    Returns:
        Dict con O, C, E, A, N en escala 0-100
    """
    import random
    if seed is not None:
        random.seed(seed)
    arch = get_archetype(archetype_name)
    return {trait: random.randint(lo, hi) for trait, (lo, hi) in arch.big_five_ranges.items()}


if __name__ == "__main__":
    print("12 Arquetipos disponibles:")
    for name in list_archetypes():
        arch = get_archetype(name)
        print(f"\n{name}:")
        print(f"  {arch.description[:90]}...")
        print(f"  Big Five ranges: {arch.big_five_ranges}")
        print(f"  Lomnitz: {arch.lomnitz_primary}/{arch.lomnitz_secondary}")
        print(f"  Voice: {arch.voice}")
