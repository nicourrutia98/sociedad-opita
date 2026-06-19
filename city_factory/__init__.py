# -*- coding: utf-8 -*-
"""
city_factory/__init__.py — Public API para replicabilidad multi-ciudad
=====================================================================

Uso:
    from city_factory import load_city, list_available_cities, get_archetype

    # Cargar una ciudad completa (YAML-driven)
    tello = load_city("tello")
    for p in tello.personas:
        print(p.persona_id, p.display_name, p.archetype)

    # Listar ciudades disponibles
    print(list_available_cities())  # ["tello"]

    # Acceder a un arquetipo de personalidad
    from city_factory import get_archetype
    arch = get_archetype("ganadero_tradicional")
    print(arch.big_five_ranges)
"""

from .city_template import (
    CityTemplate,
    CityPersona,
    HofstedeProfile,
    load_city,
    list_available_cities,
    CITIES_DIR,
)

from .personality_archetypes import (
    PersonalityArchetype,
    ARCHETYPES,
    get_archetype,
    list_archetypes,
    sample_from_archetype,
)

__all__ = [
    # City
    "CityTemplate",
    "CityPersona",
    "HofstedeProfile",
    "load_city",
    "list_available_cities",
    "CITIES_DIR",
    # Archetypes
    "PersonalityArchetype",
    "ARCHETYPES",
    "get_archetype",
    "list_archetypes",
    "sample_from_archetype",
]
