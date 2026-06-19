# -*- coding: utf-8 -*-
"""
tests/test_city_factory.py — Tests para city_factory (multi-ciudad)
==================================================================

Cubre:
- 12 arquetipos disponibles
- Big Five en rangos válidos
- Lomnitz válido (A/B/C)
- CityTemplate carga YAML correctamente
- Validación detecta errores
- list_available_cities funciona
- Slug lookup

Ejecutar: pytest tests/test_city_factory.py -v
"""

import pytest
from city_factory import (
    load_city,
    list_available_cities,
    list_archetypes,
    get_archetype,
    sample_from_archetype,
    CityTemplate,
    CityPersona,
    HofstedeProfile,
)
from city_factory.personality_archetypes import ARCHETYPES


# ------------------------------------------------------------------
# Tests: arquetipos
# ------------------------------------------------------------------

def test_list_archetypes_returns_12():
    """Hay exactamente 12 arquetipos definidos."""
    archs = list_archetypes()
    assert len(archs) == 12, f"Esperaba 12 arquetipos, encontré {len(archs)}"


def test_archetypes_have_valid_big_five_ranges():
    """Cada arquetipo tiene rangos Big Five válidos [0, 100]."""
    for name, arch in ARCHETYPES.items():
        for trait in "OCEAN":
            assert trait in arch.big_five_ranges, f"{name}: falta {trait}"
            lo, hi = arch.big_five_ranges[trait]
            assert 0 <= lo <= hi <= 100, f"{name}.{trait}: rango {lo}-{hi} fuera de [0,100]"


def test_archetypes_have_valid_lomnitz():
    """Lomnitz primario debe ser A, B o C."""
    for name, arch in ARCHETYPES.items():
        assert arch.lomnitz_primary in ("A", "B", "C"), \
            f"{name}: lomnitz_primary={arch.lomnitz_primary}"


def test_archetypes_have_voice_and_patterns():
    """Cada arquetipo tiene voz y patrones de habla."""
    for name, arch in ARCHETYPES.items():
        assert arch.voice, f"{name}: sin voz"
        assert len(arch.speaking_patterns) >= 3, \
            f"{name}: solo {len(arch.speaking_patterns)} patrones"


def test_sample_from_archetype_is_in_range():
    """Muestreo produce valores dentro del rango del arquetipo."""
    arch = get_archetype("ganadero_tradicional")
    for seed in range(10):
        sample = sample_from_archetype("ganadero_tradicional", seed=seed)
        for trait, (lo, hi) in arch.big_five_ranges.items():
            assert lo <= sample[trait] <= hi, \
                f"seed={seed}: {trait}={sample[trait]} fuera de [{lo},{hi}]"


def test_sample_deterministic_with_seed():
    """Muestreo es determinista con seed."""
    s1 = sample_from_archetype("tendero_pueblo", seed=42)
    s2 = sample_from_archetype("tendero_pueblo", seed=42)
    assert s1 == s2


def test_sample_different_seeds_different_values():
    """Distintos seeds producen distintos valores (con alta probabilidad)."""
    s1 = sample_from_archetype("ganadero_tradicional", seed=1)
    s2 = sample_from_archetype("ganadero_tradicional", seed=2)
    assert s1 != s2, "Esperaba valores distintos con seeds distintos"


# ------------------------------------------------------------------
# Tests: carga de ciudad
# ------------------------------------------------------------------

def test_list_available_cities_includes_tello():
    """Tello está disponible."""
    cities = list_available_cities()
    assert "tello" in cities, f"Tello no está en {cities}"


def test_load_tello_returns_city_template():
    """load_city('tello') retorna CityTemplate con display_name correcto."""
    city = load_city("tello")
    assert isinstance(city, CityTemplate)
    assert city.display_name == "Tello, Huila"
    assert city.department == "Huila"
    assert city.country == "CO"
    assert city.coordinates["lat"] == pytest.approx(2.9547)
    assert city.coordinates["lon"] == pytest.approx(-75.2564)


def test_tello_has_29_personas():
    """Tello tiene 29 personas (26 base + 3 gemelos para conflictos)."""
    city = load_city("tello")
    assert len(city.personas) == 29, f"Esperaba 29, encontré {len(city.personas)}"


def test_tello_hofstede_calibration():
    """Hofstede de Tello está calibrado al alza vs Colombia base."""
    city = load_city("tello")
    assert city.hofstede.PDI == 75       # vs CO base 67
    assert city.hofstede.IDV == 10       # vs CO base 13 (más colectivista)
    assert city.hofstede.UAI == 85       # vs CO base 80
    assert city.hofstede.IND == 75       # vs CO base 13


def test_tello_has_cultural_markers():
    """cultural_markers.md existe y tiene muletillas."""
    city = load_city("tello")
    assert "asina es la cosa" in city.cultural_markers
    assert "Ave María Purísima" in city.cultural_markers
    assert "tinto" in city.cultural_markers


def test_tello_has_festivities():
    """Tello tiene festividades (San Juan, San Pedro, etc.)."""
    city = load_city("tello")
    fest_names = [f["name"] for f in city.festivities]
    assert any("San Juan" in n for n in fest_names)
    assert any("San Pedro" in n for n in fest_names)


# ------------------------------------------------------------------
# Tests: validación de personas
# ------------------------------------------------------------------

def test_all_personas_have_valid_big_five():
    """Todas las personas tienen Big Five en [0, 100]."""
    city = load_city("tello")
    for p in city.personas:
        for trait in "OCEAN":
            val = p.big_five[trait]
            assert 0 <= val <= 100, \
                f"{p.persona_id}.{trait}={val} fuera de rango"


def test_all_personas_have_valid_lomnitz():
    """Todas las personas tienen Lomnitz primario válido."""
    city = load_city("tello")
    for p in city.personas:
        assert p.lomnitz_primary in ("A", "B", "C"), \
            f"{p.persona_id}: lomnitz={p.lomnitz_primary}"


def test_all_personas_have_muletillas():
    """Todas las personas tienen al menos 1 muletilla."""
    city = load_city("tello")
    for p in city.personas:
        assert len(p.muletillas) >= 1, \
            f"{p.persona_id}: sin muletillas"


def test_all_personas_have_archetype():
    """Todas las personas tienen un arquetipo de los 12 disponibles."""
    city = load_city("tello")
    valid_archs = set(list_archetypes())
    for p in city.personas:
        assert p.archetype in valid_archs, \
            f"{p.persona_id}: arquetipo '{p.archetype}' no válido"


def test_all_personas_have_speaking_style():
    """Todas las personas tienen al menos 3 speaking_style."""
    city = load_city("tello")
    for p in city.personas:
        assert len(p.speaking_style) >= 3, \
            f"{p.persona_id}: solo {len(p.speaking_style)} patrones"


def test_network_references_valid():
    """Las alianzas y conflictos referencian personas existentes."""
    city = load_city("tello")
    errors = city.validate()
    network_errors = [e for e in errors if "referencia desconocida" in e]
    assert len(network_errors) == 0, f"Red rota: {network_errors}"


def test_get_persona_by_id():
    """get_persona() encuentra personas conocidas."""
    city = load_city("tello")
    p = city.get_persona("don_rosalio_ganadero")
    assert p.display_name == "Don Rosalío"
    assert p.archetype == "ganadero_tradicional"
    assert p.big_five["O"] == 30


def test_get_persona_raises_for_unknown():
    """get_persona() lanza KeyError si no existe."""
    city = load_city("tello")
    with pytest.raises(KeyError):
        city.get_persona("no_existe")


def test_load_nonexistent_city_raises():
    """load_city() lanza FileNotFoundError para ciudad inexistente."""
    with pytest.raises(FileNotFoundError):
        load_city("ciudad_que_no_existe")


def test_validate_passes_for_tello():
    """Validación de Tello pasa sin errores."""
    city = load_city("tello")
    errors = city.validate()
    assert errors == [], f"Errores: {errors}"


# ------------------------------------------------------------------
# Tests: dataclasses
# ------------------------------------------------------------------

def test_hofstede_as_dict():
    """HofstedeProfile.as_dict() retorna las 6 dimensiones."""
    h = HofstedeProfile(PDI=70, IDV=15, MAS=60, UAI=80, IND=20, LTO=15)
    d = h.as_dict()
    assert d == {"PDI": 70, "IDV": 15, "MAS": 60, "UAI": 80, "IND": 20, "LTO": 15}


def test_city_persona_validate_catches_invalid_big_five():
    """CityPersona.validate() detecta Big Five fuera de rango."""
    p = CityPersona(
        persona_id="test",
        display_name="Test",
        archetype="ganadero_tradicional",
        role="test",
        gender="M",
        age=50,
        big_five={"O": 150, "C": 50, "E": 50, "A": 50, "N": 50},  # O fuera de rango
        lomnitz_primary="A",
    )
    errors = p.validate()
    assert any("O fuera de rango" in e for e in errors)


def test_city_persona_validate_catches_invalid_lomnitz():
    """CityPersona.validate() detecta Lomnitz inválido."""
    p = CityPersona(
        persona_id="test",
        display_name="Test",
        archetype="ganadero_tradicional",
        role="test",
        gender="M",
        age=50,
        big_five={"O": 50, "C": 50, "E": 50, "A": 50, "N": 50},
        lomnitz_primary="Z",  # inválido
    )
    errors = p.validate()
    assert any("lomnitz_primary inválido" in e for e in errors)


# ------------------------------------------------------------------
# Tests: réplica multi-ciudad (la prueba de fuego)
# ------------------------------------------------------------------

def test_template_city_loads_with_no_errors():
    """La plantilla _template/ está bien formada (es la prueba de replicabilidad)."""
    import yaml
    from pathlib import Path

    template_dir = Path(__file__).parent.parent / "cities" / "_template"
    assert template_dir.exists(), "Falta directorio _template/"

    city_yaml = template_dir / "city.yaml"
    assert city_yaml.exists(), "Falta _template/city.yaml"

    data = yaml.safe_load(city_yaml.read_text(encoding="utf-8"))
    assert "city_id" in data
    assert "display_name" in data
    assert "coordinates" in data
