# -*- coding: utf-8 -*-
# city_factory/city_template.py
# CityTemplate dataclass + loaders. Toda la info cultural de una ciudad.

"""
city_template.py — Plantilla de Ciudad Replicable
===================================================

Una ciudad en el modelo Vibe Pattern NO es código, es data.
CityTemplate es el contenedor que carga city.yaml + personas/ + cultural_markers.md

Diseño replicable:
  - cities/_template/  → esqueleto vacío con README
  - cities/tello/      → primera instancia (ya existe en datos)
  - cities/neiva/      → futura
  - cities/garzon/     → futura

Uso:
    from city_factory.city_template import CityTemplate, load_city
    tello = load_city("tello")
    print(f"{tello.display_name}: {len(tello.personas)} personas")
    for p in tello.personas:
        print(f"  {p.persona_id} ({p.archetype})")
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import yaml


# Ruta al directorio de ciudades
CITIES_DIR = Path(__file__).resolve().parent.parent / "cities"


@dataclass
class CityPersona:
    """Una persona dentro de una ciudad. Inmutable post-load."""
    persona_id: str
    display_name: str
    archetype: str                          # ej. "ganadero_tradicional"
    role: str                               # rol específico: ganadero, tendero, etc.
    gender: str                             # M | F | X
    age: int

    # Big Five (0-100)
    big_five: Dict[str, int]                # {O,C,E,A,N}

    # Lomnitz
    lomnitz_primary: str                    # A | B | C
    lomnitz_secondary: str = ""

    # Dunbar
    dunbar_layer: int = 25
    dunbar_intimates: int = 8
    dunbar_best_friends: int = 3
    dunbar_aspirational: int = 12

    # Rasgos derivados
    rasgos_derivados: Dict[str, str] = field(default_factory=dict)

    # Psicología profunda
    motivations: List[str] = field(default_factory=list)
    fears: List[str] = field(default_factory=list)
    speaking_style: List[str] = field(default_factory=list)
    muletillas: List[str] = field(default_factory=list)

    # Memoria
    formative_events: List[Dict] = field(default_factory=list)

    # Red social
    network_betweenness: float = 0.0
    network_degree: int = 0
    aliados_con: List[str] = field(default_factory=list)
    conflictos_con: List[str] = field(default_factory=list)

    # Meta
    source_bio_file: Optional[str] = None
    notes: str = ""

    def validate(self) -> List[str]:
        """Retorna lista de errores de validación. Vacía si OK."""
        errors = []
        if not (0 <= self.big_five.get("O", -1) <= 100):
            errors.append(f"{self.persona_id}: O fuera de rango")
        for trait in "OCEAN":
            if trait not in self.big_five:
                errors.append(f"{self.persona_id}: falta big_five[{trait}]")
        if self.lomnitz_primary not in ("A", "B", "C"):
            errors.append(f"{self.persona_id}: lomnitz_primary inválido {self.lomnitz_primary}")
        return errors


@dataclass
class HofstedeProfile:
    """Dimensiones culturales Hofstede calibradas para una ciudad."""
    PDI: int = 67    # Power Distance Index (Colombia base)
    IDV: int = 13   # Individualism
    MAS: int = 64   # Masculinity
    UAI: int = 80   # Uncertainty Avoidance
    IND: int = 13   # Indulgence
    LTO: int = 13   # Long-Term Orientation

    def as_dict(self) -> Dict[str, int]:
        return {"PDI": self.PDI, "IDV": self.IDV, "MAS": self.MAS,
                "UAI": self.UAI, "IND": self.IND, "LTO": self.LTO}


@dataclass
class CityTemplate:
    """Plantilla completa de una ciudad: data + personas + cultura."""
    city_id: str
    display_name: str
    department: str = ""
    country: str = "CO"
    altitude_msnm: int = 0
    climate: str = ""
    population: int = 0
    language: str = "es-CO"
    dialect: str = ""
    coordinates: Dict[str, float] = field(default_factory=dict)

    hofstede: HofstedeProfile = field(default_factory=HofstedeProfile)
    festivities: List[Dict] = field(default_factory=list)

    personas: List[CityPersona] = field(default_factory=list)
    cultural_markers: str = ""          # markdown con muletillas, léxico, etc.
    academic_refs: List[str] = field(default_factory=list)

    notes: str = ""

    def get_persona(self, persona_id: str) -> CityPersona:
        """Lookup una persona por ID. Raises KeyError si no existe."""
        for p in self.personas:
            if p.persona_id == persona_id:
                return p
        raise KeyError(f"Persona '{persona_id}' no encontrada en ciudad '{self.city_id}'. "
                       f"Disponibles: {[p.persona_id for p in self.personas]}")

    def validate(self) -> List[str]:
        """Valida toda la ciudad. Retorna lista de errores."""
        errors = []
        # Hofstede
        for dim, val in self.hofstede.as_dict().items():
            if not (0 <= val <= 120):
                errors.append(f"{self.city_id}: Hofstede {dim}={val} fuera de rango [0,120]")
        # Personas
        ids_seen = set()
        for p in self.personas:
            if p.persona_id in ids_seen:
                errors.append(f"{self.city_id}: persona_id duplicado '{p.persona_id}'")
            ids_seen.add(p.persona_id)
            errors.extend(p.validate())
        # Alianzas y conflictos referencian personas existentes
        for p in self.personas:
            for ref in p.aliados_con + p.conflictos_con:
                if ref not in ids_seen:
                    errors.append(f"{self.city_id}: {p.persona_id} referencia desconocida '{ref}'")
        return errors


def _yaml_to_persona(data: dict) -> CityPersona:
    """Convierte dict YAML a CityPersona."""
    bf = data.get("big_five", {})
    memory = data.get("memory", {})
    net = data.get("network", {})
    psy = data.get("psychology", {})

    return CityPersona(
        persona_id=data["persona_id"],
        display_name=data["display_name"],
        archetype=data.get("archetype", "ganadero_tradicional"),
        role=data["role"],
        gender=data["gender"],
        age=data["age"],
        big_five={
            "O": bf.get("O", 50),
            "C": bf.get("C", 50),
            "E": bf.get("E", 50),
            "A": bf.get("A", 50),
            "N": bf.get("N", 50),
        },
        lomnitz_primary=data.get("lomnitz", {}).get("primary", "A"),
        lomnitz_secondary=data.get("lomnitz", {}).get("secondary", "B"),
        dunbar_layer=data.get("dunbar", {}).get("layer", 25),
        dunbar_intimates=data.get("dunbar", {}).get("intimates", 8),
        dunbar_best_friends=data.get("dunbar", {}).get("best_friends", 3),
        dunbar_aspirational=data.get("dunbar", {}).get("aspirational", 12),
        rasgos_derivados=data.get("rasgos_derivados", {}),
        motivations=psy.get("motivations", []),
        fears=psy.get("fears", []),
        speaking_style=psy.get("speaking_style", []),
        muletillas=data.get("muletillas", []),
        formative_events=memory.get("formative", []),
        network_betweenness=net.get("centralidad_betweenness", 0.0),
        network_degree=net.get("centralidad_grado", 0),
        aliados_con=net.get("aliados_con", []),
        conflictos_con=net.get("conflictos_con", []),
        source_bio_file=data.get("source_bio_file"),
        notes=data.get("notes", ""),
    )


def _load_hofstede(path: Path) -> HofstedeProfile:
    if not path.exists():
        return HofstedeProfile()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return HofstedeProfile(**data)


def load_city(city_id: str) -> CityTemplate:
    """
    Carga una ciudad completa desde cities/{city_id}/.

    Args:
        city_id: identificador (ej. "tello", "neiva")

    Returns:
        CityTemplate validado

    Raises:
        FileNotFoundError: si el directorio no existe
        ValueError: si la validación falla
    """
    city_dir = CITIES_DIR / city_id
    if not city_dir.exists():
        raise FileNotFoundError(
            f"Ciudad '{city_id}' no encontrada. "
            f"Buscada en: {city_dir}. "
            f"Disponibles: {list_available_cities()}"
        )

    # Cargar city.yaml
    city_yaml = city_dir / "city.yaml"
    if not city_yaml.exists():
        raise FileNotFoundError(f"Falta {city_yaml}")
    city_data = yaml.safe_load(city_yaml.read_text(encoding="utf-8"))

    # Hofstede opcional
    hofstede = _load_hofstede(city_dir / "hofstede.yaml")

    # Cultural markers opcional
    markers_path = city_dir / "cultural_markers.md"
    cultural_markers = markers_path.read_text(encoding="utf-8") if markers_path.exists() else ""

    # Personas
    personas_dir = city_dir / "personas"
    personas: List[CityPersona] = []
    if personas_dir.exists():
        for yml_file in sorted(personas_dir.glob("*.yaml")):
            data = yaml.safe_load(yml_file.read_text(encoding="utf-8"))
            if data:
                personas.append(_yaml_to_persona(data))

    # Construir
    coords = city_data.get("coordinates", {})
    template = CityTemplate(
        city_id=city_data.get("city_id", city_id),
        display_name=city_data.get("display_name", city_id),
        department=city_data.get("department", ""),
        country=city_data.get("country", "CO"),
        altitude_msnm=city_data.get("altitude_msnm", 0),
        climate=city_data.get("climate", ""),
        population=city_data.get("population", 0),
        language=city_data.get("language", "es-CO"),
        dialect=city_data.get("dialect", ""),
        coordinates={"lat": coords.get("lat", 0.0), "lon": coords.get("lon", 0.0)},
        hofstede=hofstede,
        festivities=city_data.get("festivities", []),
        personas=personas,
        cultural_markers=cultural_markers,
        academic_refs=city_data.get("academic_refs", []),
        notes=city_data.get("notes", ""),
    )

    # Validar
    errors = template.validate()
    if errors:
        raise ValueError(
            f"Ciudad '{city_id}' tiene {len(errors)} errores de validación:\n"
            + "\n".join(f"  - {e}" for e in errors)
        )

    return template


def list_available_cities() -> List[str]:
    """Lista los city_id disponibles en cities/."""
    if not CITIES_DIR.exists():
        return []
    return sorted([
        d.name for d in CITIES_DIR.iterdir()
        if d.is_dir() and not d.name.startswith("_") and (d / "city.yaml").exists()
    ])


if __name__ == "__main__":
    print("Ciudades disponibles:")
    for cid in list_available_cities():
        try:
            c = load_city(cid)
            print(f"  {cid}: {c.display_name} ({len(c.personas)} personas)")
        except Exception as e:
            print(f"  {cid}: ERROR {e}")
