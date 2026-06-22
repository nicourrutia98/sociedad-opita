# -*- coding: utf-8 -*-
"""
tests/test_prompt_builder.py — Tests para prompt_builder.py
=============================================================

Cubre:
  - Agent dataclass: slug(), topic_*()
  - EngramStore: search_memories, save_memory, get_world_events
    (con sqlite in-memory + schema FTS5 sintético)
  - PromptBuilder._infer_profile, _extract_zona, _extract_bio_paragraph,
    _profile_variant, _anti_ai_slop_rules
  - PromptBuilder._find_psychometric_slug (con mock de perfiles_psicometricos)
  - PromptBuilder._build_psychometric_section (con mock)
  - PromptBuilder.build_agent_prompt (integración con todo mockeado)

Estrategia de mocking:
  - EngramStore real con sqlite in-memory + schema mínimo
  - perfiles_psicometricos como SimpleNamespace (como en test_estadistica)
  - BIOGRAFIAS_PATH y CULTURAL_PROMPT_PATH parcheados con tmp_path

Los archivos reales del repo (docs/agentes/01-biografias.md y
docs/agentes/02-prompt-cultural.md) están commiteados y se usan como
referencia para los fixtures sintéticos.
"""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest


# ======================================================================
# Schema FTS5 sintético para EngramStore
# ======================================================================

FTS5_SCHEMA = """
CREATE TABLE IF NOT EXISTS observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sync_id TEXT NOT NULL,
    session_id TEXT,
    type TEXT,
    title TEXT,
    content TEXT,
    project TEXT,
    scope TEXT,
    topic_key TEXT,
    created_at TEXT,
    updated_at TEXT,
    last_seen_at TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS observations_fts USING fts5(
    title, content, type,
    content='observations',
    content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS observations_ai AFTER INSERT ON observations
BEGIN
    INSERT INTO observations_fts(rowid, title, content, type)
    VALUES (new.id, new.title, new.content, new.type);
END;
"""


@pytest.fixture
def engram_db(tmp_path: Path):
    """Crea una DB sqlite con schema FTS5 mínimo y devuelve el path."""
    db_path = tmp_path / "engram_test.db"
    con = sqlite3.connect(db_path)
    con.executescript(FTS5_SCHEMA)
    con.commit()
    con.close()
    return str(db_path)


# ======================================================================
# Tests de Agent dataclass
# ======================================================================

class TestAgentDataclass:
    """Agent es un @dataclass con name/age/profile/zona/bio_paragraph/raw_bio."""

    def _make(self, name="Don Eliécer", age=60, profile="adulto",
              zona="Vereda Matarredonda", alias="el patrón"):
        from prompt_builder import Agent
        return Agent(
            name=f"{name} ({alias})",
            age=age,
            profile=profile,
            zona=zona,
            bio_paragraph="Bio de prueba",
            raw_bio="raw",
        )

    def test_slug_removes_don_title(self):
        agent = self._make(name="Don Eliécer", alias="el patrón")
        slug = agent.slug()
        # "Don Eliécer (el patrón)" → "don eliecer (el patron)" → remove "don "
        # → "eliecer (el patron)" → regex [^a-z0-9\s-] removes "é" → "el cer" + " (el patron)"
        # wait: "eliecer" tiene e-l-i-é-c-e-r → quitando é → e-l-i-c-e-r = "elicer"
        # → espacios a "-" → "elicer-el-patron"
        assert slug == "elicer-el-patrn"
        assert "don" not in slug.split("-")

    def test_slug_removes_dona_title(self):
        from prompt_builder import Agent
        a = Agent(name="Doña Rosa (la tendera)", age=55, profile="adulto",
                  zona="Calle 5", bio_paragraph="", raw_bio="")
        slug = a.slug()
        assert "dona" not in slug.split("-")
        assert "rosa" in slug

    def test_slug_removes_padre_title(self):
        from prompt_builder import Agent
        a = Agent(name="Padre Cecilio (el cura)", age=50, profile="mayor",
                  zona="Iglesia", bio_paragraph="", raw_bio="")
        slug = a.slug()
        assert "padre" not in slug.split("-")

    def test_slug_removes_profesora_title(self):
        from prompt_builder import Agent
        a = Agent(name="Profesora Aurora (la maestra)", age=45, profile="adulto",
                  zona="Escuela", bio_paragraph="", raw_bio="")
        slug = a.slug()
        assert "profesora" not in slug.split("-")

    def test_slug_handles_jhon_fredy(self):
        from prompt_builder import Agent
        a = Agent(name="Jhon Fredy (el joven)", age=22, profile="joven",
                  zona="Calle 6", bio_paragraph="", raw_bio="")
        slug = a.slug()
        assert slug == "jhon-fredy-el-joven"

    def test_topic_keys_have_correct_format(self):
        agent = self._make()
        slug = agent.slug()
        assert agent.topic_memories() == f"agent/{slug}/memories"
        assert agent.topic_relationships() == f"agent/{slug}/relationships"
        assert agent.topic_identity() == f"agent/{slug}/identity"

    def test_topic_keys_are_distinct(self):
        agent = self._make()
        topics = {
            agent.topic_memories(),
            agent.topic_relationships(),
            agent.topic_identity(),
        }
        assert len(topics) == 3  # todas distintas


# ======================================================================
# Tests de EngramStore
# ======================================================================

class TestEngramStore:
    """EngramStore es un wrapper sobre sqlite3 con FTS5."""

    def _insert_memory(self, db_path: str, project: str, topic_key: str,
                       title: str, content: str, type_: str = "memory"):
        con = sqlite3.connect(db_path)
        con.execute("""
            INSERT INTO observations
              (sync_id, session_id, type, title, content, project, scope,
               topic_key, created_at, updated_at, last_seen_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (f"obs-{title}", "test-session", type_, title, content,
              project, "project", topic_key,
              "2026-06-22T00:00:00Z", "2026-06-22T00:00:00Z", "2026-06-22T00:00:00Z"))
        con.commit()
        con.close()

    def _make_agent(self, slug: str = "don-eliecer", name: str = "Don Eliécer"):
        from prompt_builder import Agent
        return Agent(name=name, age=60, profile="adulto", zona="X",
                     bio_paragraph="", raw_bio="")

    def test_init_with_db_path(self, engram_db):
        from prompt_builder import EngramStore
        es = EngramStore(db_path=engram_db)
        assert es.db_path == engram_db

    def test_save_memory_returns_id(self, engram_db):
        from prompt_builder import EngramStore
        es = EngramStore(db_path=engram_db)
        agent = self._make_agent()
        mem_id = es.save_memory(agent, "Conversación con Rosalío",
                                "Hablamos sobre los linderos", type_="memory")
        assert isinstance(mem_id, int)
        assert mem_id > 0

    def test_save_memory_uses_topic_memories(self, engram_db):
        from prompt_builder import EngramStore
        es = EngramStore(db_path=engram_db)
        # El slug real de "Don Eliécer" (sin alias) es "elicer" (sin tilde).
        # Para que el slug contenga "-el-patrn" se necesita el alias en el name.
        from prompt_builder import Agent
        agent = Agent(name="Don Eliécer (el patrón)", age=60,
                      profile="adulto", zona="X",
                      bio_paragraph="", raw_bio="")
        es.save_memory(agent, "Test", "Contenido")
        con = sqlite3.connect(engram_db)
        row = con.execute(
            "SELECT topic_key FROM observations WHERE title = ?", ("Test",)
        ).fetchone()
        assert row[0] == "agent/elicer-el-patrn/memories"

    def test_save_relationship_uses_relationship_type(self, engram_db):
        from prompt_builder import EngramStore
        es = EngramStore(db_path=engram_db)
        agent = self._make_agent()
        es.save_relationship(agent, "Don Rosalío", "Es mi compadre")
        con = sqlite3.connect(engram_db)
        row = con.execute(
            "SELECT type FROM observations WHERE title = ?",
            ("Relación con Don Rosalío",),
        ).fetchone()
        assert row[0] == "relationship"

    def test_search_memories_by_query(self, engram_db):
        from prompt_builder import EngramStore
        project = "generative"
        self._insert_memory(engram_db, project,
                           "agent/elicer/memories",
                           "Conversación sobre linderos",
                           "Discutimos el alambrado")
        self._insert_memory(engram_db, project,
                           "agent/elicer/memories",
                           "Misa del domingo",
                           "El padre Cecilio predicó")

        es = EngramStore(db_path=engram_db)
        agent = self._make_agent()
        results = es.search_memories(agent, query="linderos", limit=5)
        assert len(results) >= 1
        assert any("linderos" in r["title"].lower() for r in results)

    def test_search_memories_no_query_returns_recent(self, engram_db):
        from prompt_builder import EngramStore
        project = "generative"
        self._insert_memory(engram_db, project,
                           "agent/elicer/memories", "Memoria 1", "...")
        self._insert_memory(engram_db, project,
                           "agent/elicer/memories", "Memoria 2", "...")

        es = EngramStore(db_path=engram_db)
        agent = self._make_agent()
        results = es.search_memories(agent, query="", limit=10)
        assert len(results) == 2

    def test_search_memories_filters_by_topic(self, engram_db):
        """Búsqueda solo dentro del topic del agente (no contamina otros)."""
        from prompt_builder import EngramStore
        project = "generative"
        self._insert_memory(engram_db, project,
                           "agent/elicer/memories", "Memoria Eliecer", "...")
        self._insert_memory(engram_db, project,
                           "agent/rosa/memories", "Memoria Rosa", "...")

        es = EngramStore(db_path=engram_db)
        agent = self._make_agent(slug="elicer")
        results = es.search_memories(agent, query="", limit=10)
        assert all("elicer" in r["topic_key"] for r in results)
        assert not any("rosa" in r["topic_key"] for r in results)

    def test_get_world_events_filters_by_world_prefix(self, engram_db):
        from prompt_builder import EngramStore
        project = "generative"
        self._insert_memory(engram_db, project,
                           "world/neiva/events/festival",
                           "Festival del Bambuco",
                           "San Juan 2026")
        self._insert_memory(engram_db, project,
                           "agent/don-eliecer/memories",
                           "No es un evento del mundo", "...")

        es = EngramStore(db_path=engram_db)
        events = es.get_world_events(limit=5)
        assert all(ev["title"] != "No es un evento del mundo" for ev in events)
        assert any(ev["title"] == "Festival del Bambuco" for ev in events)


# ======================================================================
# Tests de PromptBuilder._infer_profile, _extract_zona, _extract_bio_paragraph
# ======================================================================

class TestParseHelpers:
    """Helpers de parsing del markdown de biografías."""

    def _pb(self):
        from prompt_builder import PromptBuilder
        # Mockear __init__ para no leer filesystem
        with patch.object(PromptBuilder, "__init__", lambda self, engram=None: None):
            return PromptBuilder()

    def test_infer_profile_rural_by_vereda_keyword(self):
        pb = self._pb()
        body = "Vive en **Vereda:** Matarredonda. Trabaja la tierra con fique."
        assert pb._infer_profile(body) == "rural"

    def test_infer_profile_mayor_by_jubilado(self):
        pb = self._pb()
        body = "Es jubilado de Electrohuila, trabajó 35 años. Viudo."
        assert pb._infer_profile(body) == "mayor"

    def test_infer_profile_joven_by_universidad(self):
        pb = self._pb()
        body = "Estudia en la Surcolombiana. Baila en los ensayos de San Juan."
        assert pb._infer_profile(body) == "joven"

    def test_infer_profile_adulto_default(self):
        pb = self._pb()
        body = "Tiene una tienda en el centro. Vende queso y panela."
        assert pb._infer_profile(body) == "adulto"

    def test_extract_zona_barrio(self):
        pb = self._pb()
        body = "**Rol:** Tendera\n**Barrio:** Centro, Calle 5 con Carrera 6"
        assert pb._extract_zona(body) == "Centro, Calle 5 con Carrera 6"

    def test_extract_zona_ubicacion(self):
        pb = self._pb()
        body = "**Ubicación:** Vereda El Carmen"
        assert pb._extract_zona(body) == "Vereda El Carmen"

    def test_extract_zona_vereda(self):
        pb = self._pb()
        body = "**Vereda:** Matarredonda"
        assert pb._extract_zona(body) == "Matarredonda"

    def test_extract_zona_default(self):
        pb = self._pb()
        body = "Texto sin campo de zona."
        assert pb._extract_zona(body) == "Neiva"

    def test_extract_bio_paragraph_with_structured_fields(self):
        pb = self._pb()
        body = (
            "**Rol estructural:** Tendera de la tienda de la esquina\n"
            "**Vínculos:**\n"
            "- Hija de Don Eliecer\n"
            "- Comadre de Doña Mercedes\n"
            "**Estereotipo visible:** La que todo lo sabe\n"
            "**Recurso crítico:** La tienda como centro del pueblo"
        )
        result = pb._extract_bio_paragraph(body, alias="la tendera")
        assert "Rol: Tendera de la tienda de la esquina" in result
        assert "Vínculo clave: Hija de Don Eliecer" in result
        assert "Estereotipo: La que todo lo sabe" in result
        assert "Recurso: La tienda como centro del pueblo" in result

    def test_extract_bio_paragraph_fallback_to_alias(self):
        """Sin campos estructurados, devuelve frase con el alias."""
        pb = self._pb()
        body = "Texto sin estructura."
        result = pb._extract_bio_paragraph(body, alias="la tendera")
        assert result == "Eres conocido como 'la tendera'."

    def test_extract_bio_paragraph_uses_first_bullet_only(self):
        pb = self._pb()
        body = (
            "**Vínculos:**\n"
            "- Primera conexión\n"
            "- Segunda conexión\n"
            "**Estereotipo visible:** X"
        )
        result = pb._extract_bio_paragraph(body, alias="")
        assert "Vínculo clave: Primera conexión" in result
        assert "Segunda conexión" not in result


# ======================================================================
# Tests de _profile_variant y _anti_ai_slop_rules
# ======================================================================

class TestPromptFragments:
    """Fragmentos de prompt que se incluyen en cada llamada al LLM."""

    def _pb(self):
        from prompt_builder import PromptBuilder
        with patch.object(PromptBuilder, "__init__", lambda self, engram=None: None):
            return PromptBuilder()

    def test_profile_variant_joven(self):
        pb = self._pb()
        v = pb._profile_variant("joven")
        assert "joven" in v.lower()
        assert "papi" in v or "timbico" in v

    def test_profile_variant_adulto(self):
        pb = self._pb()
        v = pb._profile_variant("adulto")
        assert "adulto" in v.lower()

    def test_profile_variant_mayor(self):
        pb = self._pb()
        v = pb._profile_variant("mayor")
        assert "mayor" in v.lower() or "viejo" in v.lower()
        assert "mijo" in v or "mija" in v

    def test_profile_variant_rural(self):
        pb = self._pb()
        v = pb._profile_variant("rural")
        assert "rural" in v.lower() or "campo" in v.lower()

    def test_profile_variant_unknown_defaults_to_adulto(self):
        pb = self._pb()
        v = pb._profile_variant("perfil_inexistente")
        v_adulto = pb._profile_variant("adulto")
        assert v == v_adulto

    def test_anti_ai_slop_has_13_rules(self):
        pb = self._pb()
        rules = pb._anti_ai_slop_rules()
        # Debe tener 13 reglas numeradas (1-13)
        for n in range(1, 14):
            pattern = rf'\*\*{n}\.'
            assert re.search(pattern, rules), f"Falta regla {n}"

    def test_anti_ai_slop_includes_recordatorio(self):
        pb = self._pb()
        rules = pb._anti_ai_slop_rules()
        assert "RECORDATORIO" in rules

    def test_anti_ai_slop_mentions_muletillas_variety(self):
        """La regla 11 obliga a variar muletillas."""
        pb = self._pb()
        rules = pb._anti_ai_slop_rules()
        # Busca palabras clave de la regla 11
        assert "VARÍA" in rules or "VARIAS" in rules or "ROTAR" in rules.upper()


# ======================================================================
# Tests de _find_psychometric_slug
# ======================================================================

class TestFindPsychometricSlug:
    """Mapeo del slug de biografía al slug de perfil psicométrico."""

    def _pb_with_pp(self, pp_data, monkeypatch):
        """Crea PromptBuilder con perfiles_psicometricos mockeado.
        Usa monkeypatch para que los patches estén activos durante el test.
        """
        from prompt_builder import PromptBuilder
        mock_pp = SimpleNamespace(PERFILES_ADULTOS=pp_data)

        # Patchear el __init__ para no leer filesystem
        monkeypatch.setattr(PromptBuilder, "__init__",
                            lambda self, engram=None: None)
        pb = PromptBuilder()

        # Activar los patches de módulo (estarán activos hasta el fin del test)
        monkeypatch.setattr("prompt_builder._pp", mock_pp)
        monkeypatch.setattr("prompt_builder._PP_DISPONIBLE", True)
        return pb

    def test_explicit_mapping_takes_priority(self, monkeypatch):
        """El mapeo explícito _BIO_TO_PERFIL tiene prioridad sobre fuzzy."""
        pp_data = {"don_eliecer_patron": {"name": "Don Eliécer"}}
        pb = self._pb_with_pp(pp_data, monkeypatch)
        # Slug que está en _BIO_TO_PERFIL
        slug = pb._find_psychometric_slug("elicer-perdomo-motta-el-patrn")
        assert slug == "don_eliecer_patron"

    def test_fallback_returns_none_when_no_match(self, monkeypatch):
        pp_data = {"some_other_slug": {"name": "X"}}
        pb = self._pb_with_pp(pp_data, monkeypatch)
        # Slug que NO está ni en mapeo ni en perfil_slugs
        slug = pb._find_psychometric_slug("slug-que-no-existe")
        assert slug is None

    def test_fallback_exact_match(self, monkeypatch):
        """Si agent_slug está en perfil_slugs pero NO en _BIO_TO_PERFIL,
        matchea por la regla 2 (fuzzy exacto)."""
        pp_data = {"unknown-slug-not-in-bio-mapping": {"name": "X"}}
        pb = self._pb_with_pp(pp_data, monkeypatch)
        slug = pb._find_psychometric_slug("unknown-slug-not-in-bio-mapping")
        assert slug == "unknown-slug-not-in-bio-mapping"

    def test_fallback_normalized_match(self, monkeypatch):
        """Misma slug con guiones vs underscores."""
        pp_data = {"don_eliecer_patron": {"name": "X"}}
        pb = self._pb_with_pp(pp_data, monkeypatch)
        # Slug bio con guion debe matchear perfil_slug con underscore
        slug = pb._find_psychometric_slug("don-eliecer-patron")
        assert slug == "don_eliecer_patron"

    def test_returns_none_when_pp_not_available(self, monkeypatch):
        from prompt_builder import PromptBuilder
        monkeypatch.setattr(PromptBuilder, "__init__",
                            lambda self, engram=None: None)
        pb = PromptBuilder()
        monkeypatch.setattr("prompt_builder._PP_DISPONIBLE", False)
        slug = pb._find_psychometric_slug("don-eliecer")
        assert slug is None

    def test_alias_match(self, monkeypatch):
        """Si agent_name tiene '(alias)', intenta matchear por alias extraído."""
        # El alias "la tendera" normalizado es "la_tendera"
        pp_data = {"la_tendera": {"name": "Doña Rosa"}}
        pb = self._pb_with_pp(pp_data, monkeypatch)
        slug = pb._find_psychometric_slug("rosa-la-tendera",
                                          agent_name="Doña Rosa (la tendera)")
        # El slug "rosa-la-tendera" empieza por "rosa-la-tendera" pero la normalización
        # lo convierte a "rosa_la_tendera". Verifica matchea por la regla startswith.
        assert slug == "la_tendera"


# ======================================================================
# Tests de _build_psychometric_section
# ======================================================================

class TestBuildPsychometricSection:
    """Construye la sección Big Five + Lomnitz + Dunbar del system prompt."""

    def _pb(self):
        from prompt_builder import PromptBuilder
        with patch.object(PromptBuilder, "__init__", lambda self, engram=None: None):
            return PromptBuilder()

    def _perfil(self, **overrides):
        defaults = {
            "name": "Don Eliécer",
            "big_five": {"O": 35, "C": 65, "E": 45, "A": 30, "N": 70},
            "rasgos": {
                "habla_tipica": "Tajante, con muletillas rurales",
                "manejo_conflicto": "Confronta directamente",
                "respuesta_crisis": "Se cierra, no negocia",
                "disposicion_chisme": "Bajo, le molesta",
                "confianza_inicial": "Muy baja",
                "fuente": "biografica",
            },
            "dunbar": {
                "intimos": ["esposa", "hijo"],
                "buenos": ["compadre1", "vecino1"],
            },
            "lomnitz_default": "C",
        }
        defaults.update(overrides)
        return defaults

    def test_includes_big_five_numbers(self):
        pb = self._pb()
        perfil = self._perfil()
        with patch("prompt_builder._pp", SimpleNamespace(obtener_perfil=lambda slug: perfil)), \
             patch("prompt_builder._VOICES_DATA", {}):
            section = pb._build_psychometric_section("don_eliecer_patron")
        assert "O=35" in section
        assert "A=30" in section

    def test_includes_lomnitz_translation(self):
        pb = self._pb()
        perfil = self._perfil(lomnitz_default="A")
        with patch("prompt_builder._pp", SimpleNamespace(obtener_perfil=lambda slug: perfil)), \
             patch("prompt_builder._VOICES_DATA", {}):
            section = pb._build_psychometric_section("x")
        assert "SIMÉTRICA" in section

    def test_includes_dunbar_intimos(self):
        pb = self._pb()
        perfil = self._perfil()
        with patch("prompt_builder._pp", SimpleNamespace(obtener_perfil=lambda slug: perfil)), \
             patch("prompt_builder._VOICES_DATA", {}):
            section = pb._build_psychometric_section("x")
        assert "esposa" in section
        assert "hijo" in section

    def test_low_amabilidad_triggers_few_shot(self):
        """A <= 40 debe activar few-shot antagónico."""
        pb = self._pb()
        perfil = self._perfil()
        with patch("prompt_builder._pp", SimpleNamespace(obtener_perfil=lambda slug: perfil)), \
             patch("prompt_builder._VOICES_DATA", {}):
            section = pb._build_psychometric_section("x")
        assert "FEW-SHOT" in section or "EJEMPLOS" in section
        assert "ANTI-SESGO" in section or "debiasing" in section.lower()

    def test_high_amabilidad_no_few_shot(self):
        """A >= 75 sin N alto → no few-shot antagónico."""
        pb = self._pb()
        perfil = self._perfil(
            big_five={"O": 60, "C": 70, "E": 60, "A": 80, "N": 30},
        )
        with patch("prompt_builder._pp", SimpleNamespace(obtener_perfil=lambda slug: perfil)), \
             patch("prompt_builder._VOICES_DATA", {}):
            section = pb._build_psychometric_section("x")
        # No debe haber few-shot antagónico
        assert "ANTI-SESGO (debiasing)" not in section or "few-shot" not in section.lower()

    def test_arquetipico_source_adds_aviso(self):
        pb = self._pb()
        perfil = self._perfil()
        perfil["rasgos"]["fuente"] = "rol_arquetipico"
        with patch("prompt_builder._pp", SimpleNamespace(obtener_perfil=lambda slug: perfil)), \
             patch("prompt_builder._VOICES_DATA", {}):
            section = pb._build_psychometric_section("x")
        assert "AVISO" in section
        assert "ARQUETÍPICO" in section or "ARQUETIPICO" in section

    def test_voices_data_injects_biographical_section(self):
        """Si _VOICES_DATA tiene muletillas del perfil, se inyectan."""
        pb = self._pb()
        perfil = self._perfil()
        voces = {
            "don_eliecer_patron": {
                "muletillas": ["pues mire", "eso es"],
                "registro": "Grave y pausado",
            }
        }
        with patch("prompt_builder._pp", SimpleNamespace(obtener_perfil=lambda slug: perfil)), \
             patch("prompt_builder._VOICES_DATA", voces):
            section = pb._build_psychometric_section("don_eliecer_patron")
        assert "pues mire" in section
        assert "Grave y pausado" in section

    def test_universal_debiasing_always_present(self):
        """La regla universal anti-sesgo aparece en TODOS los perfiles."""
        pb = self._pb()
        perfil = self._perfil(
            big_five={"O": 60, "C": 70, "E": 60, "A": 80, "N": 30},
        )
        with patch("prompt_builder._pp", SimpleNamespace(obtener_perfil=lambda slug: perfil)), \
             patch("prompt_builder._VOICES_DATA", {}):
            section = pb._build_psychometric_section("x")
        assert "REGLA UNIVERSAL DE FIDELIDAD" in section


# ======================================================================
# Tests de build_agent_prompt (integración)
# ======================================================================

class TestBuildAgentPrompt:
    """Prueba end-to-end del constructor principal de prompts."""

    @pytest.fixture
    def biografia_md(self, tmp_path):
        """Markdown de biografía sintético para parsear."""
        content = """\
# Biografías de Tello

### 1. Don Eliécer Perdomo — "el patrón" (60 años)

**Rol estructural:** Patrón ganadero de la vereda Matarredonda.

**Vínculos:**
- Compadre del Alcalde Fernando Solano
- Padrino de Jhon Eliécer (su hijo)

**Estereotipo visible:** El que manda en la vereda.

**Recurso crítico:** 80 cabezas de ganado.

Texto adicional sobre la vida de Don Eliécer...

### 2. Doña Rosa Trujillo — "la tendera" (55 años)

**Rol estructural:** Tendera de la tienda de la esquina.

**Vínculos:**
- Hija de Don Eliécer
- Comadre de Doña Mercedes

Texto adicional sobre Doña Rosa...

"""
        p = tmp_path / "01-biografias.md"
        p.write_text(content, encoding="utf-8")
        return p

    @pytest.fixture
    def cultural_md(self, tmp_path):
        """Prompt cultural sintético (mínimo)."""
        content = """\
# Prompt cultural huilense

```
Sos un huilense de Tello. Hablás en dialecto opita.
Usás muletillas como "pues", "pos", "mijo".
```

"""
        p = tmp_path / "02-prompt-cultural.md"
        p.write_text(content, encoding="utf-8")
        return p

    def _make_pb(self, biografia_path, cultural_path, engram_mock=None):
        from prompt_builder import PromptBuilder
        # Patchear paths y _VOICES_DATA
        with patch("prompt_builder.BIOGRAFIAS_PATH", biografia_path), \
             patch("prompt_builder.CULTURAL_PROMPT_PATH", cultural_path), \
             patch("prompt_builder._VOICES_DATA", {}), \
             patch.object(PromptBuilder, "__init__",
                          lambda self, engram=None: setattr(self, 'engram', engram or engram_mock) or None):
            # El lambda de arriba no llama al __init__ real, así que inicializo manualmente
            pb = PromptBuilder.__new__(PromptBuilder)
            pb.engram = engram_mock or MagicMock(
                search_memories=MagicMock(return_value=[]),
                get_world_events=MagicMock(return_value=[]),
            )
            from prompt_builder import BIOGRAFIAS_PATH, CULTURAL_PROMPT_PATH
            pb.biographies_text = BIOGRAFIAS_PATH.read_text(encoding="utf-8")
            pb.cultural_prompt = pb._extract_cultural_prompt()
            pb.agents_cache = {}
            return pb

    def test_returns_system_and_user_keys(self, biografia_md, cultural_md):
        pb = self._make_pb(biografia_md, cultural_md)
        with patch("prompt_builder._PP_DISPONIBLE", False):
            result = pb.build_agent_prompt(
                agent_name="Don Eliécer",
                scene={"hora": "07:00", "lugar": "Finca"},
            )
        assert "system" in result
        assert "user" in result

    def test_system_includes_agent_name(self, biografia_md, cultural_md):
        pb = self._make_pb(biografia_md, cultural_md)
        with patch("prompt_builder._PP_DISPONIBLE", False):
            result = pb.build_agent_prompt(
                agent_name="Don Eliécer",
                scene={"hora": "07:00"},
            )
        assert "Don Eliécer" in result["system"]
        assert "60 años" in result["system"]

    def test_user_includes_scene(self, biografia_md, cultural_md):
        pb = self._make_pb(biografia_md, cultural_md)
        with patch("prompt_builder._PP_DISPONIBLE", False):
            result = pb.build_agent_prompt(
                agent_name="Don Eliécer",
                scene={"hora": "07:30", "lugar": "Finca Matarredonda",
                       "clima": "26°C",
                       "personas_presentes": ["Mayordomo"]},
            )
        assert "07:30" in result["user"]
        assert "Finca Matarredonda" in result["user"]
        assert "Mayordomo" in result["user"]

    def test_user_includes_scene_context(self, biografia_md, cultural_md):
        pb = self._make_pb(biografia_md, cultural_md)
        with patch("prompt_builder._PP_DISPONIBLE", False):
            result = pb.build_agent_prompt(
                agent_name="Don Eliécer",
                scene={"hora": "07:00"},
                scene_context="Don Eliécer volvió de misa.",
            )
        assert "Don Eliécer volvió de misa" in result["user"]

    def test_user_includes_memories_when_present(self, biografia_md, cultural_md):
        engram = MagicMock()
        engram.search_memories.return_value = [
            {"type": "memory", "title": "Conversación con Rosalío",
             "content": "Hablamos sobre linderos", "created_at": "x", "topic_key": "x"}
        ]
        engram.get_world_events.return_value = []
        pb = self._make_pb(biografia_md, cultural_md, engram)
        with patch("prompt_builder._PP_DISPONIBLE", False):
            result = pb.build_agent_prompt(
                agent_name="Don Eliécer",
                scene={"hora": "07:00"},
                memory_query="linderos",
            )
        assert "RECUERDOS" in result["user"]
        assert "Conversación con Rosalío" in result["user"]

    def test_user_includes_world_events_when_present(self, biografia_md, cultural_md):
        engram = MagicMock()
        engram.search_memories.return_value = []
        engram.get_world_events.return_value = [
            {"title": "Festival del Bambuco", "content": "San Juan 2026"}
        ]
        pb = self._make_pb(biografia_md, cultural_md, engram)
        with patch("prompt_builder._PP_DISPONIBLE", False):
            result = pb.build_agent_prompt(
                agent_name="Don Eliécer",
                scene={"hora": "07:00"},
            )
        assert "EVENTOS EN NEIVA" in result["user"]
        assert "Festival del Bambuco" in result["user"]

    def test_user_excludes_world_events_when_disabled(self, biografia_md, cultural_md):
        engram = MagicMock()
        engram.search_memories.return_value = []
        engram.get_world_events.return_value = [
            {"title": "Festival", "content": "x"}
        ]
        pb = self._make_pb(biografia_md, cultural_md, engram)
        with patch("prompt_builder._PP_DISPONIBLE", False):
            result = pb.build_agent_prompt(
                agent_name="Don Eliécer",
                scene={"hora": "07:00"},
                include_world_events=False,
            )
        assert "EVENTOS EN NEIVA" not in result["user"]

    def test_unknown_agent_raises_value_error(self, biografia_md, cultural_md):
        pb = self._make_pb(biografia_md, cultural_md)
        with patch("prompt_builder._PP_DISPONIBLE", False):
            with pytest.raises(ValueError, match="not found"):
                pb.build_agent_prompt(
                    agent_name="Fulano Que No Existe",
                    scene={"hora": "07:00"},
                )

    def test_parse_agents_finds_don_eliecer(self, biografia_md, cultural_md):
        pb = self._make_pb(biografia_md, cultural_md)
        agents = pb.parse_agents()
        # El slug real es "elicer-perdomo-el-patrn" (sin "don" y sin tildes)
        assert "elicer-perdomo-el-patrn" in agents

    def test_parse_agents_finds_dona_rosa(self, biografia_md, cultural_md):
        pb = self._make_pb(biografia_md, cultural_md)
        agents = pb.parse_agents()
        assert any("rosa" in slug for slug in agents.keys())

    def test_parse_agents_caches(self, biografia_md, cultural_md):
        pb = self._make_pb(biografia_md, cultural_md)
        agents1 = pb.parse_agents()
        agents2 = pb.parse_agents()
        assert agents1 is agents2  # misma referencia = cache hit