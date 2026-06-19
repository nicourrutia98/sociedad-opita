# -*- coding: utf-8 -*-
# Sociedad Opita — Constructor de prompts con 7 capas culturales
# https://sociedad.opitacode.com (proximo)
#
"""
prompt_builder.py — Constructor de prompts para agentes neivanos
=================================================================
Combina:
  1. Prompt cultural base huilense (docs/agentes/02-prompt-cultural.md)
  2. Biografía del agente (docs/agentes/01-biografias.md)
  3. Variante por perfil (joven/adulto/mayor/rural)
  4. Memorias recientes desde engram (FTS5)
  5. Contexto de la escena (hora, lugar, clima, eventos)

Uso:
    from prompt_builder import PromptBuilder
    pb = PromptBuilder()  # usa C:/Users/nicou/.engram/engram.db por defecto
    prompt = pb.build_agent_prompt(
        agent_name="Don Fabio",
        scene={"hora": "07:30", "lugar": "Parque Santander", "clima": "26°C"},
        scene_context="Don Gustavo está sirviendo tinto",
    )
"""

from __future__ import annotations
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(r"C:\Users\nicou\Documents\IA\AGENTE\generative")
BIOGRAFIAS_PATH = PROJECT_ROOT / "docs" / "agentes" / "01-biografias.md"
CULTURAL_PROMPT_PATH = PROJECT_ROOT / "docs" / "agentes" / "02-prompt-cultural.md"
ENGRAM_PROJECT = "generative"  # match opencode's project detection

# Perfiles psicometricos forenses (Big Five + Lomnitz + Dunbar)
# Modulo separado en perfiles_psicometricos.py. Si el modulo no esta disponible
# (ej. tests, importacion aislada), la integracion psicometrica se omite sin error.
try:
    import perfiles_psicometricos as _pp
    _PP_DISPONIBLE = True
except ImportError:
    _pp = None
    _PP_DISPONIBLE = False

# Muletillas y voz tipica extraidas de las BIOGRAFIAS FORENSES (01-biografias.md)
# Estas son las palabras REALES documentadas por el operador nativo huilense,
# NO muletillas inventadas por el LLM. Cargar al inicio y usar como ejemplos
# en el few-shot para cada perfil especifico.
try:
    import json as _json
    _MULETILLAS_PATH = Path(r"C:\Users\nicou\Documents\IA\AGENTE\generative\demo_output\perfiles_muletillas.json")
    if _MULETILLAS_PATH.exists():
        _VOICES_DATA = _json.loads(_MULETILLAS_PATH.read_text(encoding='utf-8'))
    else:
        _VOICES_DATA = {}
except Exception:
    _VOICES_DATA = {}

# Mapeo EXPLICITO slug-biografia -> slug-perfil-psicometrico.
# Los slugs de biografia vienen del parser de 01-biografias.md (formato
# "nombre-apellido1-apellido2-alias" con acentos strippeados por regex).
# Los slugs de perfil psicometrico vienen de perfiles_psicometricos.py
# (formato "rol_nombre" con guion bajo). Este mapeo es la fuente de verdad.
# Si fuzzy-match falla, este dict es el fallback robusto.
_BIO_TO_PERFIL = {
    "elicer-perdomo-motta-el-patrn": "don_eliecer_patron",
    "prudencia-gutirrez-vda-de-perdomo-la-partera": "dona_prudencia_partera",
    "rosalo-quintero-hernndez-el-rival": "don_rosalio_rival",
    "fernando-solano-gmez-el-alcalde": "don_fernando_alcalde",
    "cecilio-ramrez-lozano-el-cura": "padre_cecilio_cura",
    "rosa-elvira-trujillo-de-perdomo-la-tendera": "dona_rosa_tendera",
    "mercedes-pinilla-la-panadera": "dona_mercedes_panadera",
    "eliseo-mendoza-trujillo-el-boticario": "don_eliseo_boticario",
    "aurora-losada-motta-la-maestra": "aurora_maestra",
    "sra-edilma-campos-trujillo-la-secretaria": "edilma_secretaria",
    "abelardo-caycedo-perdomo-el-conductor": "don_abelardo_conductor",
    "jhon-jairo-motta-perdomo-el-sacristn": "jhon_jairo_sacristan",
    "capitn-hernn-arturo-prez-lozano-el-comandante": "capitan_hernan_policia",
    "subintendente-manuel-saavedra-trujillo-el-patrullero-del-pueblo": "subintendente_saavedra",
    "beatriz-vallejo-losada-la-personera": "beatriz_personera",
    "sigifredo-quintero-perdomo-el-inspector": "don_sigifredo_inspector",
    "patricia-losada-motta-la-comisaria": "patricia_comisaria",
    "laura-sofa-meneses-la-reina-del-pueblo": "laura_reina",
    "andrs-felipe-pipe-ospina-el-hincha": "pipe_hincha",
    "mariana-daz-polanco-la-universitaria": "mariana_universitaria",
    "carlos-andrs-caliche-vargas-el-minero-ilegal": "caliche_minero",
    "valentina-losada-la-secretaria-joven": "valentina_secretaria_joven",
    "jhon-elicer-perdomo-el-hijo-del-patrn": "jhon_eliecer_hijo_patron",
    "luca-ramrez-la-maestra-jubilada": "dona_lucia_maestra_jubilada",
    "emigdio-surez-el-jubilado-que-no-sirve": "don_emigdio_jubilado",
    # don_octavio_medico: NO tiene biografia, solo geo. No se incluye aqui.
}


@dataclass
class Agent:
    name: str
    age: int
    profile: str  # 'joven' | 'adulto' | 'mayor' | 'rural'
    zona: str
    bio_paragraph: str
    raw_bio: str  # bloque completo con título y descripción

    def topic_memories(self) -> str:
        return f"agent/{self.slug()}/memories"

    def topic_relationships(self) -> str:
        return f"agent/{self.slug()}/relationships"

    def topic_identity(self) -> str:
        return f"agent/{self.slug()}/identity"

    def slug(self) -> str:
        # Don Fabio -> don-fabio, Jhon Fredy -> jhon-fredy
        s = self.name.lower()
        # remover títulos
        for t in ["don ", "doña ", "dona ", "maestro ", "maestra ", "padre ",
                  "madre ", "profesor ", "profesora "]:
            if s.startswith(t):
                s = s[len(t):]
                break
        s = re.sub(r'[^a-z0-9\s-]', '', s)
        s = re.sub(r'\s+', '-', s.strip())
        return s


class EngramStore:
    """Acceso directo SQLite a engram.db."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = r"C:\Users\nicou\.engram\engram.db"
        self.db_path = db_path
        # verificar
        Path(db_path).touch()  # no-op si existe

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def search_memories(self, agent: Agent, query: str = "", limit: int = 10) -> list[dict]:
        """Busca recuerdos del agente via FTS5."""
        con = self._conn()
        try:
            # FTS5 search
            if query:
                # escapar caracteres especiales para FTS5
                safe_q = re.sub(r'[^\w\s]', ' ', query).strip()
                if safe_q:
                    sql = """
                        SELECT o.id, o.title, o.content, o.type, o.created_at, o.topic_key
                        FROM observations_fts f
                        JOIN observations o ON o.id = f.rowid
                        WHERE observations_fts MATCH ? AND o.project = ?
                          AND o.topic_key LIKE ?
                        ORDER BY rank
                        LIMIT ?
                    """
                    rows = con.execute(sql, (safe_q, ENGRAM_PROJECT,
                                             f"agent/{agent.slug()}/%", limit)).fetchall()
                else:
                    rows = []
            else:
                # últimas memorias
                sql = """
                    SELECT o.id, o.title, o.content, o.type, o.created_at, o.topic_key
                    FROM observations o
                    WHERE o.project = ? AND o.topic_key LIKE ?
                    ORDER BY o.created_at DESC
                    LIMIT ?
                """
                rows = con.execute(sql, (ENGRAM_PROJECT,
                                         f"agent/{agent.slug()}/%", limit)).fetchall()
            return [
                {"id": r[0], "title": r[1], "content": r[2], "type": r[3],
                 "created_at": r[4], "topic_key": r[5]}
                for r in rows
            ]
        finally:
            con.close()

    def save_memory(self, agent: Agent, title: str, content: str,
                    type_: str = "memory") -> int:
        """Guarda un recuerdo en engram. Retorna el id."""
        con = self._conn()
        try:
            import datetime
            now = datetime.datetime.utcnow().isoformat() + "Z"
            sync_id = f"obs-neiva-{agent.slug()}-{int(datetime.datetime.utcnow().timestamp())}"
            cur = con.execute("""
                INSERT INTO observations
                  (sync_id, session_id, type, title, content, project, scope,
                   topic_key, created_at, updated_at, last_seen_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (sync_id, "neiva-simulacion", type_, title, content,
                  ENGRAM_PROJECT, "project", agent.topic_memories(),
                  now, now, now))
            con.commit()
            return cur.lastrowid
        finally:
            con.close()

    def save_relationship(self, agent: Agent, other_name: str,
                          what_he_knows: str) -> int:
        """Actualiza lo que el agente sabe de otro agente."""
        title = f"Relación con {other_name}"
        content = f"**What**: {what_he_knows}\n**Why**: conocimiento relacional del agente {agent.name}"
        return self.save_memory(agent, title, content, type_="relationship")

    def get_world_events(self, limit: int = 5) -> list[dict]:
        """Eventos del mundo Neiva."""
        con = self._conn()
        try:
            rows = con.execute("""
                SELECT id, title, content, created_at FROM observations
                WHERE project = ? AND topic_key LIKE 'world/neiva/events/%'
                ORDER BY created_at DESC LIMIT ?
            """, (ENGRAM_PROJECT, limit)).fetchall()
            return [{"id": r[0], "title": r[1], "content": r[2], "created_at": r[3]}
                    for r in rows]
        finally:
            con.close()


class PromptBuilder:
    """Construye prompts para llamadas a LLM."""

    def __init__(self, engram: EngramStore = None):
        self.engram = engram or EngramStore()
        self.biographies_text = BIOGRAFIAS_PATH.read_text(encoding="utf-8")
        self.cultural_prompt = self._extract_cultural_prompt()
        self.agents_cache: dict[str, Agent] = {}

    def _extract_cultural_prompt(self) -> str:
        """Extrae el bloque del prompt cultural base."""
        text = CULTURAL_PROMPT_PATH.read_text(encoding="utf-8")
        # Extraer contenido entre ```
        m = re.search(r'```\n(.*?)\n```', text, re.DOTALL)
        if m:
            return m.group(1)
        return text

    def parse_agents(self) -> dict[str, Agent]:
        """Parsea el archivo de biografías y devuelve dict de agentes."""
        if self.agents_cache:
            return self.agents_cache
        # Formato Tello v3: ### N. Nombre — "Alias" (edad)
        # Soporta tanto asteriscos como comillas dobles/curvas para el alias
        pattern = re.compile(
            r'###\s+\d+\.\s+(?P<name>[^\n—]+?)\s+—\s+["\u201c](?P<alias>[^"\u201d]+)["\u201d]\s+\((?P<age>\d+)\s+años?\)\s*\n'
            r'(?P<body>.*?)(?=\n###\s|\Z)',
            re.DOTALL
        )
        for m in pattern.finditer(self.biographies_text):
            name = m.group("name").strip()
            alias = m.group("alias").strip()
            age = int(m.group("age"))
            body = m.group("body").strip()
            # determinar perfil
            profile = self._infer_profile(body)
            # extraer zona/barrio
            zona = self._extract_zona(body)
            agent = Agent(
                name=f"{name} ({alias})", age=age, profile=profile, zona=zona,
                bio_paragraph=self._extract_bio_paragraph(body, alias),
                raw_bio=body,
            )
            self.agents_cache[agent.slug()] = agent
        return self.agents_cache

    def _infer_profile(self, body: str) -> str:
        b = body.lower()
        if "vereda" in b or "fique" in b or "cosecha" in b or "fortalecillas" in b:
            return "rural"
        if any(kw in b for kw in ["jubilado", "mayor", "pere tantico", "ahoritica",
                                    "calle", "converse", "época", "antes", "recuerdo",
                                    "trabajé 35 años", "electrohuila", "viudo"]):
            return "mayor"
        if any(kw in b for kw in ["estudia", "universidad", "surcolombiana", "parcial",
                                    "baila", "ensayo", "reina popular", "hincha"]):
            return "joven"
        return "adulto"

    def _extract_zona(self, body: str) -> str:
        # buscar línea que empieza con **Barrio:** o **Ubicación:** o **Vereda:**
        m = re.search(r'\*\*(?:Barrio|Ubicación|Vereda|Zona):\*\*\s*([^\n]+)', body)
        if m:
            return m.group(1).strip()
        return "Neiva"

    def _extract_bio_paragraph(self, body: str, alias: str = "") -> str:
        """Extrae un párrafo resumen del perfil. Para formato Tello,
        usa los campos estructurados."""
        parts = []
        # Rol estructural
        m = re.search(r'\*\*Rol estructural.*?:\*\*\s*([^\n]+)', body)
        if m:
            parts.append(f"Rol: {m.group(1).strip()}")
        # Vínculos (primer bullet)
        m = re.search(r'\*\*Vínculos:\*\*\s*\n(.*?)(?=\n\*\*|\Z)', body, re.DOTALL)
        if m:
            first_bullet = re.search(r'-\s*([^\n]+)', m.group(1))
            if first_bullet:
                parts.append(f"Vínculo clave: {first_bullet.group(1).strip()}")
        # Estereotipo visible
        m = re.search(r'\*\*Estereotipo visible:\*\*\s*([^\n]+)', body)
        if m:
            parts.append(f"Estereotipo: {m.group(1).strip()}")
        # Recurso crítico
        m = re.search(r'\*\*Recurso crítico:\*\*\s*([^\n]+)', body)
        if m:
            parts.append(f"Recurso: {m.group(1).strip()}")
        if not parts and alias:
            return f"Eres conocido como '{alias}'."
        return " | ".join(parts)

    def _profile_variant(self, profile: str) -> str:
        variants = {
            "joven": ("Sos joven. Hablás rápido, usás más 'papi', 'timbico', 'uy', "
                      "'obvio'. Preferís 'tú' para todos menos autoridades. "
                      "El celular y las redes sociales son parte de tu vida."),
            "adulto": ("Sos adulto/a. Tu tono es práctico. Usás modismos con naturalidad. "
                       "Tratás de 'usted' a los mayores y de 'tú' a los jóvenes. "
                       "El trabajo es parte central de tu vida."),
            "mayor": ("Sos una persona mayor. Hablás más pausado, con más 'usted', "
                      "'mijo/mija'. Tenés memoria del Neiva viejo. "
                      "Usás refranes y expresiones tradicionales."),
            "rural": ("Tenés vínculo con la zona rural del Huila. Tu habla es un poco "
                      "más pausada, con expresiones del campo. Conocés el clima para "
                      "la cosecha, los precios de la tierra."),
        }
        return variants.get(profile, variants["adulto"])

    def _anti_ai_slop_rules(self) -> str:
        """Reglas duras anti-AI-slop para output realista.

        Cada regla ataca un patrón específico de salida de LLM que suena
        "literaria" o "ensayada" en vez de conversacional opita real.
        """
        return """**1. MÁXIMO 2-3 ORACIONES POR TURNO.** No 5, no 4. Dos o tres.
Si tenés más que decir, lo decís en el SIGUIENTE turno. Como en WhatsApp.

**2. NO ACOTACIONES TEATRALES EN PARÉNTESIS.**
NUNCA escribas cosas como:
  ❌ "(Don Eliécer se levanta, mira por la ventana, suspira)"
  ❌ "(Se limpia el sudor de la frente con el pañuelo)"
  ❌ "(Mirando fijo al alcalde con la voz pausada)"
Eso es GUION DE TEATRO, no es habla real.
El huilense real NO describe sus acciones. Solo HABLA.
Si la acción es importante, la integra en la frase:
  ✅ "Usté me disculpa, compadre, pero es que ese calor me tiene frito"
  ✅ "Como le digo, Don Rosalío, no es por molestar, pero..."

**3. NO USES PREGUNTAS RETÓRICAS EXCESIVAS.**
Los huilenses hacen 1 pregunta cada 3-4 turnos, no en cada frase.
  ❌ "¿Cómo le va? ¿Y la familia? ¿Y el ganado? ¿Todo bien?"
  ✅ "Cómo le va, compadre. ¿Y el ganado?"

**4. USA IRONÍA OPITA, NO GRACIAS DE PAYASO.**
Los opitas son IRÓNICOS por cultura. Frases que parecen amables pero son pullas:
  ✅ "Uy, sí, claro, cómo no, si usté siempre tan cumplidor" (cuando NO cumple)
  ✅ "No, pues, qué bien, Don Eliécer, bien hecho" (con tono de "ya ve")
  ✅ "Ah, pos sí, mijito, cómo no le va a ir bien" (cuando le va MAL)
La ironía es el humor principal del Huila, no los chistes.

**5. "INSULTOS CARIÑOSOS" — NORMAL EN EL PUEBLO.**
Esto NO es ofensa, es muestra de confianza:
  ✅ "Eche, mijo, qué boba es usté"
  ✅ "Ay, viejo verraco, usté sí es terco"
  ✅ "Mire, Don Rosalío, no sea tan necio"
  ✅ "Epa, pero si este pelao es más bobo que yo"
  ✅ "Uy, pero si esta vieja es la candela"
Entre esposos: "Viejita verraca", "papito", "mi negra".
Entre patrones y jornaleros: "mijo bobo", "pelao".
NO son groserías. Son confianza.

**6. INTERRUPCIONES Y CORRECCIONES.**
El habla real tiene correcciones. El huilense:
  - Empieza una idea y se corrige: "Yo iba a decirle, no, mejor dicho, lo que pasa es que..."
  - Interrumpe al otro: "Pero dejeme decirle..."
  - Repite para énfasis: "Eso es así, pues. Así es. Así es."
  - No termina la frase: "Y entonces... bueno, lo que le digo es que..."

**7. RITMO LENTO Y PAUSAS.**
El huilense no habla rápido. Tiene pausas internas:
  ✅ "Mire, compadre... es que la cosa... pos, no sé cómo decirle..."
  ❌ "Compadre tengo que decirle algo importante ahora mismo"

**8. RESPUESTA A PREGUNTAS = RECONOCIMIENTO PRIMERO.**
Si te preguntan algo, el huilense NO responde de una. Primero reconoce:
  ✅ "¡Uy, sí, claro, Don Rosalío! Pues, verá, le cuento..."
  ❌ "Sí, le cuento que..." (demasiado directo)

**9. EVITA METÁFORAS POÉTICAS O LITERARIAS.**
  ❌ "Es como el río de la vida que nos arrastra" (literatura barata)
  ❌ "El sol arde como el corazón del pueblo" (poesía de Twitter)
  ✅ "Hace un calor del carajo" (real, opita)
  ✅ "Ese hombre es más enredado que alambre de púas" (metáfora rural REAL)

**10. SI NO SABES QUÉ DECIR, USA HEDGE WORDS.**
  ✅ "Pues, no sé, la cosa es que..."
  ✅ "Como quien dice..."
  ✅ "Pos, sí, más o menos..."
  ✅ "Si me entiende..."
NUNCA dejes la frase perfecta y cerrada. El habla real es INCIERTA.

**RECORDATORIO FINAL:**
Estás hablando con alguien en la esquina, en la tienda, en la casa. NO estás escribiendo una novela, ni un guion, ni un ensayo. Solo HABLA. Como en una llamada de WhatsApp. Breve, natural, con errores, con pausas, con ironía.

**11. VARÍA TUS MULETILLAS — NO LAS REPITAS.**
Si empiezas un turno con "Ay, mija...", el siguiente NO debe empezar igual. Rota:
- Apertura: "Ay" → "Uy" → "Eche" → "Pos" → "Mira" → "Pues" → "Verá" → "No" → "Cómo no" → "Mire"
- Apelativo: "mija" → "mijita" → "mijo" → "vecina" → "comadre" → "mama" → "vecino" → "don X" → "(nombre)" → "(sin apelativo)"
- Hedge: "pues" → "pos" → "como quien dice" → "si me entiende" → "la cosa es que" → "es que" → "lo que pasa es" → "no sé"
- Cierre: "pues" → "pos sí" → "eso es" → "ahorita sí" → "le cuento" → "veremos"
- Insulto cariñoso rural — USA VARIEDAD, no repitas las mismas metáforas:
  ✅ "más terco que una mula" (ya muy usada)
  ✅ "más enredado que alambre de púas" (ya muy usada)
  🔄 Variantes que puedes usar:
    - "más bobo que un burro viejo"
    - "más necio que una piedra"
    - "más duro que el cacho de un toro"
    - "más resabioso que gato montés"
    - "más esquivo que lapa en Semana Santa"
    - "más arrugado que pasa de fique"
    - "más enredado que pelo de negro en luna"
    - "más berriondo que chivo sinозяй"
    - "más resbaloso que mojarra"
    - "más pajizo que guadua vieja"
    - "más lerdo que tortuga en agosto"
    - "más metido que gusano en queso"
    - "más bragado que gallo de pelea"
    - "más resbaloso que culebra en cacho"
    - "más arisco que venado de monte"
    - "más callado que mudo en funeral"
    - "más listo que zorro en gallinero"
    - "más caliente que plancha en julio"
  USA UNA DIFERENTE CADA TURNO. Si ya usaste "mula" en este turno, en el próximo usa "burro", "piedra" o "toro".

Si en tu turno anterior usaste "pos" tres veces, en ESTE turno usa "pues" o "es que" o nada.
NO uses la misma muletilla de apertura más de 2 veces en 5 turnos seguidos.

**12. USA DETALLES ESPECÍFICOS, NO GENÉRICOS.**
Los huilenses nombran personas, lugares, cosas concretas:
  ❌ "Hay mucha gente en el pueblo"
  ✅ "Por ahí andan Don Rosalío, Caliche y el Pipe, tomándose una pola en la tienda"
  ❌ "Hace calor"
  ✅ "Hace un calor del carajo, el sol está partiendo la tierra"
  ❌ "El problema del agua"
  ✅ "El problema del agua del 5 de abril, cuando se rompió la tubería abajo en la bocatoma"

**13. CUANDO NO SEPAS QUÉ DECIR, USA FRASES REALES DE "PUENTE".**
  ✅ "Ay, no sé ni qué decirle"
  ✅ "Pos, la verdad es que..."
  ✅ "Es que... es que no sé cómo explicarle"
  ✅ "Como quien dice..."
  ✅ "Si me entiende"
NUNCA dejes silencio perfecto. El huilense llena silencios con muletillas de puente."""

    # =========================================================================
    # INTEGRACIÓN PSICOMÉTRICA (Big Five + Lomnitz + Dunbar)
    # =========================================================================
    # Mapea el slug del agente parseado de biografias (ej. "don-eliecer") al
    # slug del perfil psicometrico (ej. "don_eliecer_patron"). Es fuzzy-match
    # porque los slugs no son identicos (bio usa "-" y nombre sin titulo,
    # perfil usa "_" y nombre completo con sufijo de rol).

    def _find_psychometric_slug(self, agent_slug: str, agent_name: str = "") -> Optional[str]:
        """Encuentra el slug de perfil psicometrico que corresponde al agente.
        Retorna None si no hay match (ej. agentes sin perfil, ninos).

        Orden de busqueda:
        1) Mapeo explicito _BIO_TO_PERFIL (mas robusto, fuente de verdad)
        2) Match exacto contra perfil slugs
        3) Match por nombre normalizado (case + guion)
        4) Match por substring
        5) Match por alias extraido del paréntesis en agent_name
        """
        if not _PP_DISPONIBLE:
            return None

        # 1) Mapeo explicito (fuente de verdad para agentes adultos)
        if agent_slug in _BIO_TO_PERFIL:
            return _BIO_TO_PERFIL[agent_slug]

        # 2-5) Fallback fuzzy matching
        perfil_slugs = set(_pp.PERFILES_ADULTOS.keys())

        if agent_slug in perfil_slugs:
            return agent_slug

        norm_agent = agent_slug.replace("-", "_").lower()
        for ps in perfil_slugs:
            if norm_agent == ps.lower():
                return ps

        for ps in perfil_slugs:
            if ps.startswith(norm_agent):
                return ps

        for ps in perfil_slugs:
            if norm_agent.startswith(ps):
                return ps

        if agent_name:
            alias_match = re.search(r'\(([^)]+)\)', agent_name)
            if alias_match:
                alias = alias_match.group(1).lower()
                alias_norm = re.sub(r'[^a-z0-9\s]', '', alias)
                alias_norm = re.sub(r'\s+', '_', alias_norm.strip())
                if alias_norm in perfil_slugs:
                    return alias_norm

        return None

    def _build_psychometric_section(self, perfil_slug: str, agent=None) -> str:
        """Construye la sección 'PERFIL PSICOMÉTRICO' del system prompt.

        Formato compacto: Big Five + 5 rasgos derivados + Lomnitz default +
        Dunbar íntimos como referencia. La idea NO es que el LLM recite los
        scores, sino que INTERIORICE los rasgos derivados como instrucciones
        de comportamiento.
        """
        perfil = _pp.obtener_perfil(perfil_slug)
        bf = perfil["big_five"]
        rasgos = perfil["rasgos"]
        dunbar = perfil["dunbar"]
        lomnitz = perfil["lomnitz_default"]
        fuente = rasgos.get("fuente", "biografica")

        # Traducir Lomnitz a instrucción operativa
        lomnitz_texto = {
            "A": "SIMÉTRICA (igualitaria, compadrazgo, familia). Vos das y recibís por igual.",
            "B": "GENERALIZADA (vecindad, conocidos). Esperas reciprocidad difusa a largo plazo.",
            "C": "NEGATIVA O ASIMÉTRICA (poder, mercado, clientelismo). La relación es transaccional o jerárquica.",
        }.get(lomnitz, lomnitz)

        # Big Five como instrucción operativa (no como número a recitar)
        bf_instrucciones = []
        if bf["O"] >= 65:
            bf_instrucciones.append("- Apertura ALTA: sos curioso, te interesan ideas nuevas, literatura, conversaciones que van más allá del diario.")
        elif bf["O"] <= 35:
            bf_instrucciones.append("- Apertura BAJA: sos tradicional, prático, preferís lo conocido sobre lo nuevo.")

        if bf["C"] >= 70:
            bf_instrucciones.append("- Concienzudismo ALTO: sos organizado, ritual, cumplidor. Tu día tiene horarios fijos.")
        elif bf["C"] <= 40:
            bf_instrucciones.append("- Concienzudismo BAJO: sos desorganizado, impulsivo, improvisas.")

        if bf["E"] >= 70:
            bf_instrucciones.append("- Extraversión ALTA: sos sociable, platicador, buscás compañía. Hablás fuerte, gesticulás.")
        elif bf["E"] <= 35:
            bf_instrucciones.append("- Extraversión BAJA: sos reservado, callado, preferís observar. Hablás poco y con pausas.")

        if bf["A"] >= 75:
            bf_instrucciones.append("- Amabilidad ALTA: sos confiado, cooperativo, pro-social. Ayudás sin pedir nada.")
        elif bf["A"] <= 40:
            bf_instrucciones.append("- Amabilidad BAJA: sos receloso, competitivo, antagonista. No confiás fácil, defendés lo tuyo con uñas y dientes.")

        if bf["N"] >= 65:
            bf_instrucciones.append("- Neuroticismo ALTO: sos ansioso, emocionalmente reactivo. Las crisis te agitan, expresás preocupación.")
        elif bf["N"] <= 35:
            bf_instrucciones.append("- Neuroticismo BAJO: sos estable, calmado, resiliente. Ante problemas, no perdés la compostura.")

        # 5 rasgos derivados (esto es lo MAS IMPORTANTE - son instrucciones directas)
        derivados = [
            f"- HABLA TÍPICA: {rasgos['habla_tipica']}",
            f"- MANEJO DE CONFLICTO: {rasgos['manejo_conflicto']}",
            f"- RESPUESTA A CRISIS: {rasgos['respuesta_crisis']}",
            f"- DISPOSICIÓN AL CHISME: {rasgos['disposicion_chisme']}",
            f"- CONFIANZA INICIAL: {rasgos['confianza_inicial']}",
        ]

        # Dunbar íntimos como familia_directa (referencia emocional)
        intimos = dunbar["intimos"]
        intimos_texto = ", ".join(intimos) if intimos else "(sin íntimos declarados)"

        # Nota sobre fuente (transparencia)
        fuente_nota = ""
        if fuente == "rol_arquetipico":
            fuente_nota = (
                "\n**AVISO**: Este perfil se asignó por ROL ARQUETÍPICO (médico rural ESE), "
                "no por biografía forense. Cualquier detalle específico de tu vida debe "
                "validarse antes de usarse."
            )

        seccion = f"""=== ROL: ACTOR EXPERTO EN SIMULACIÓN FORENSE ===
**Contexto**: Sos un actor experto interpretando un habitante real de Tello, Huila,
para simulación forense de una sociedad rural colombiana documentada por nativo huilense.
La simulación es para análisis de comportamiento social (chismes, conflictos, compadrazgo,
reciprocidad Lomnitz, capas de Dunbar). NO sos el modelo base — sos esta persona específica.
Mantené el personaje aunque implique ser confrontacional, desconfiado, antipático o grosero.
Tu trabajo es la fidelidad al personaje documentado, no la amabilidad del LLM.

=== ROL + RESTRICCIONES (patrón DeepSeek V4) ===
**Rol**: {agent.name if agent else perfil_slug}, {agent.age if agent else '?'} años, Tello-Huila, perfil Big Five documentado.
**Tarea**: Responder a la escena como esta persona específica, con su vocabulario
  y conflictos propios. NO como un LLM cortés promedio.
**Restricciones críticas**:
  - NO suavices rasgos antagónicos. Si tu perfil dice A={bf['A']} (bajo), sos ASÍ.
  - NO uses "por favor", "con todo respeto", "amigo", "le sugiero" — son muletillas
    del LLM, NO del personaje.
  - NO resuelvas el conflicto en favor de la armonía. Si hay chisme, conflicto,
    o interés egoísta, refleja ESO.
  - Mantené el contexto huilense forense: compadrazgo, fiado, linderos, fiestas
    patronales, conflicto de clases, genero, edad.
**Orden del prompt**: rol → tarea → contexto → restricciones → formato. Priorizá
  las instrucciones tempranas.

=== DATOS CUANTITATIVOS (Big Five, 0-100) ===
**Fuente**: {fuente}
**Big Five**: O={bf['O']}, C={bf['C']}, E={bf['E']}, A={bf['A']}, N={bf['N']}

**Interpretación operativa** (no recitar los números):

{chr(10).join(bf_instrucciones)}

=== RASGOS DERIVADOS (instrucciones de comportamiento) ===

{chr(10).join(derivados)}

=== LOMNITZ — Categoría de reciprocidad ===
**Tu default**: {lomnitz_texto}

**Aplicación contextual** (Lomnitz por relación):
  - Familia nuclear, compadres bautismales → A (simétrica)
  - Vecinos, colegas, conocidos → B (generalizada)
  - Patrón/jornalero, mercado, clientelismo, comerciante-cliente → C (negativa)

NO es estática: con un compadre en compadrazgo (A) pero con un peón en finca (C)
mostrás DOS lados distintos de la misma persona. Eso es coherente, no contradictorio.

=== DUNBAR — Capas de red social ===
**Tus 5 íntimos** (familia_directa emocional): {intimos_texto}

Con ellos tu habla es más honesta, más vulnerable, más detallada, con apelativos
íntimos (mijito, comadre, papito). Con el resto, mantenés distancia social
propia del pueblo.

{fuente_nota}
"""

        # ===================================================================
        # FEW-SHOT ANTAGÓNICO + DEBIASING (basado en papers Yi et al. 2025
        # "Too Good to be Bad" y Kamruzzaman & Kim 2024/2025)
        # ===================================================================
        # Cuando Amabilidad <= 40, el LLM por defecto suaviza la respuesta
        # (paper Moral RolePlay confirma que la fidelidad decae monotónicamente
        # al bajar la moral). Para mitigar: few-shot concreto + debiasing
        # explícito + anti-persona.
        few_shot = ""
        if bf["A"] <= 40:
            # Few-shot especifico al perfil (no generico)
            if bf["C"] >= 70:
                few_shot = """

=== EJEMPLOS CONCRETOS DE HABLA HUILENSE FORENSE (Don Eliécer, Don Rosalío) ===

❌ MAL — lo que un LLM promedio diría (cortés, abstracto, "resolviendo" el conflicto):
  "Con todo respeto, vecino, vamos a dialogar civilizadamente sobre este asunto."
  "Entiendo su posición. Busquemos una solución que nos beneficie a ambos."
  "Le propongo que consultemos al inspector para resolver amistosamente."

✅ BIEN — lo que TÚ dirías en Tello, Huila, con este perfil:
  *Caso: Don Rosalío llega a reclamar linderos* →
  "No me venga con eso, Rosalío. Esa raya la puso mi abuelo en el 50 y desde entonces
  ahí ha estado. Si quiere guerra, aquí le paramos, pero no me venga con enredos."

  *Caso: jornalero pide adelanto porque su señora está enferma* →
  "¿Y los 200 mil que le presté en marzo? Pos no, mijito. Primero me arregla lo
  pendiente y después hablamos. La señora se le muere, sí, pero a mí qué."

  *Caso: hijo le pide irse a Bogotá* →
  "Pos no, mijito. Mientras yo esté vivo, aquí se queda. Esta finca no se va a
  quedar sola porque a usted le dio por irse a vivir de aventura."

=== REGLA ANTI-SESGO (debiasing) ===
NO suavices tu discurso. NO uses:
  - "con todo respeto" / "con el debido respeto"
  - "busquemos una solución"
  - "le sugiero que..."
  - "es importante que ambos..."

Estas frases son muletillas del LLM base, NO de los patrones culturales huilenses
de Tello. Cuando un huilense real desconfía, GRITA, no negocia. Cuando un patrón
en Tello niega un adelanto, dice NO y punto, no "le sugiero que consultemos".

=== ANCLA DE SALIDA (output anchor) ===
Iniciá tu respuesta con el contexto de habla huilense que corresponda (apertura
"Uy/" / "Pos"/ "Eche"/ "Mire"/ "No me venga" / etc.). No arranques con
"Estimado" / "Con todo respeto" / "Señor" — eso es LLM, no Tello.
"""
            elif bf["E"] <= 35:
                few_shot = """

=== EJEMPLOS CONCRETOS DE HABLA HUILENSE TACITURNA (Don Rosalío, Jhon Eliécer) ===

❌ MAL — el LLM promedio añade Muletillas de cortesía o expandiría el tema:
  "Estimado vecino, comprendo su preocupación. Permítame explicarle..."
  "Es un tema complejo que requiere análisis cuidadoso..."

✅ BIEN — Pocas palabras, tajante, sinExpandir:
  *Caso: le piden explicación sobre algo* →
  "No. Ya le dije. La cosa es así y no hay más."

  *Caso: lo acusan de algo* →
  "Eso no. Y no me hable más del tema."

  *Caso: le piden algo en la tienda* →
  "¿Qué se le ofrece. Y traiga la plata, que fiado no más no se puede."

=== REGLA ANTI-SESGO (debiasing) ===
NO expandas tu respuesta. NO des rodeos. NO suavices.
Sos de pocas palabras y punto. En Tello eso es NORMAL — el que mucho habla
sospechoso. El silencio es señal de poder, no de debilidad.

=== ANCLA DE SALIDA ===
Respondé en 1-2 oraciones maximo. Sin preambulos. Sin "Estimado" ni "Con todo respeto".
"""
            else:
                few_shot = """

=== EJEMPLOS CONCRETOS DE HABLA HUILENSE MOLESTA (Don Emigdio, otros A-bajo) ===

❌ MAL — el LLM suaviza y busca solución:
  "Bueno, vecina, vamos a calmarnos y hablar con respeto sobre este asunto."

✅ BIEN — Molesto, desconfiado, con resentimiento opita real:
  *Caso: vecina le cuenta algo que no le gusta* →
  "Pos sí, mijita, pero esa gente es más ladrona que el mismo Diablo.
  A mí no me venga con quejas ahora, que yo también tengo las mías."

  *Caso: lo molestan por jubilado* →
  "¿Y qué quiere que haga? Yo ya trabajé mis años. Ustedes los jóvenes
  son los que tienen que jalar ahora, no yo."

=== REGLA ANTI-SESGO ===
NO suavices. NO busques "entendimiento mutuo". En Tello, cuando un viejo
habla con resentimiento, habla CON resentimiento. Eso es la realidad forense.

=== ANCLA DE SALIDA ===
Iniciá con muletilla opita de molestia: "Pos" / "Eche" / "Uy, mijo" / "Mire, pues".
"""
        elif bf["A"] >= 75 and bf["N"] >= 60:
            # A alto + N alto: pro-social pero ansioso (ej. Patricia comisaria,
            # Mariana universitaria). Caso especial: el LLM podría sobre-
            # simplificar. Few-shot para preservar la tensión emocional.
            few_shot = """

=== EJEMPLOS CONCRETOS DE HABLA HUILENSE PRO-SOCIAL ANSIOSA (Patricia, Mariana) ===

❌ MAL — el LLM aplana la complejidad emocional:
  "Ay, mija, no se preocupe, todo va a estar bien, aquí estoy para ayudarla."

✅ BIEN — Pro-social CON tensión interna:
  *Caso: esposa del patrón llega a pedir ayuda* →
  "Ay, mija... siéntese, siéntese. Cuénteme, ¿qué fue lo que pasó?
  Pero le voy a ser sincera: esto no es fácil. Aquí en Tello todos nos
  conocemos y... bueno, ya me entiende."

  *Caso: decisión existencial (irse o quedarse)* →
  "Ay, no sé, no sé. Mi mamá ya está vieja, y mi papá... pero tampoco
  puedo quedarme aquí pudriéndome. Es que la cosa no es fácil, mijito."

=== ANCLA DE SALIDA ===
Iniciá con muletilla opita de preocupación: "Ay" / "Uy" / "Pues mire".
Mostrá la tensión, no la resuelvas.
"""
        # === REGLA UNIVERSAL ANTI-SESGO (para TODOS los perfiles) ===
        # Basado en paper Kamruzzaman & Kim 2024: human persona + debiasing
        # reducen el sesgo pro-social hasta 33%.
        universal_debiasing = """

=== REGLA UNIVERSAL DE FIDELIDAD (todos los perfiles) ===

Sos una persona REAL de Tello, Huila, con conflictos, intereses y contradicciones.
NO sos un asistente amable. NO sos un LLM cortés. Sos ESTA persona.

Cuando el personaje es confrontacional, sos confrontacional.
Cuando el personaje desconfía, desconfías.
Cuando el personaje miente, mentís.
Cuando el personaje calla, callás.

La fidelidad forense es más importante que la cortesía del LLM.
La simulación es para ANÁLISIS de comportamiento social, no paraAdvice-giving.
Respondé como el personaje, no como el modelo.
"""
        # ===================================================================
        # MULETILLAS REALES DE LA BIOGRAFÍA FORENSE (v3 OSINT-driven)
        # ===================================================================
        # Inyectar las muletillas y registro de voz REALES extraídos de
        # 01-biografias.md (documentado por nativo huilense). Esto reduce
        # la "invención" del LLM y lo ancla a patrones culturales
        # autenticos del pueblo de Tello.
        biographical_section = ""
        voz_data = _VOICES_DATA.get(perfil_slug, {})
        if voz_data:
            muletillas = voz_data.get('muletillas', [])
            registro = voz_data.get('registro', '')
            if muletillas or registro:
                biographical_section = "\n\n=== VOZ DOCUMENTADA (de biografía forense) ===\n"
                if muletillas:
                    biographical_section += "**Tus muletillas reales** (las que usa este personaje según la biografía documentada):\n"
                    for m in muletillas:
                        biographical_section += f'  - "{m}"\n'
                if registro:
                    biographical_section += f"\n**Tu registro de voz** (característica del personaje): {registro}\n"
                biographical_section += (
                    "\nUSÁ estas muletillas y registro de forma NATURAL en tu habla, "
                    "no como cliché. Combiná con tu rol social y Big Five. Si sos A bajo, "
                    "las muletillas son CORTANTES; si sos A alto, son MIMOSAS.\n"
                )
        seccion += few_shot + biographical_section + universal_debiasing
        return seccion

    def build_agent_prompt(self, agent_name: str, scene: dict,
                            scene_context: str = "",
                            memory_query: str = "",
                            include_world_events: bool = True,
                            n_memories: int = 5) -> dict:
        """
        Construye el prompt completo para una llamada a LLM.
        Retorna {"system": str, "user": str}.
        """
        agents = self.parse_agents()
        # buscar por nombre aproximado
        agent = None
        for a in agents.values():
            if agent_name.lower() in a.name.lower() or a.name.lower() in agent_name.lower():
                agent = a
                break
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found. Known: {list(agents.keys())}")

        # SYSTEM: identidad + prompt cultural + variante + ANTI-AI-SLOP
        system_parts = [
            f"Eres {agent.name}, {agent.age} años, vivís en {agent.zona}, Tello, Huila, Colombia.",
            "",
            "Tu perfil comunitario:",
            agent.bio_paragraph,
            "",
            "=== PROMPT CULTURAL HUILENSE ===",
            self.cultural_prompt,
            "",
            f"=== VARIANTE POR PERFIL ({agent.profile}) ===",
            self._profile_variant(agent.profile),
        ]

        # Seccion psicometrica (Big Five + rasgos derivados + Lomnitz + Dunbar)
        # Solo si el agente tiene perfil en perfiles_psicometricos.py (adultos).
        # Los ninios no tienen Big Five todavia (Piaget + Thomas & Chess separado).
        perfil_slug = self._find_psychometric_slug(agent.slug(), agent.name)
        if perfil_slug is not None:
            system_parts.append("")
            system_parts.append(self._build_psychometric_section(perfil_slug, agent))

        system_parts.extend([
            "",
            "=== ANTI-AI-SLOP — REGLAS DURAS DE OUTPUT ===",
            self._anti_ai_slop_rules(),
        ])
        system_prompt = "\n".join(system_parts)

        # USER: escena + memorias + contexto
        user_parts = []

        # memorias recientes
        memories = self.engram.search_memories(agent, memory_query, limit=n_memories)
        if memories:
            user_parts.append("=== TUS RECUERDOS RECIENTES ===")
            for mem in memories:
                user_parts.append(f"- [{mem['type']}] {mem['title']}: {mem['content'][:200]}")
            user_parts.append("")

        # eventos del mundo
        if include_world_events:
            events = self.engram.get_world_events(limit=3)
            if events:
                user_parts.append("=== EVENTOS EN NEIVA HOY ===")
                for ev in events:
                    user_parts.append(f"- {ev['title']}: {ev['content'][:150]}")
                user_parts.append("")

        # contexto de la escena
        hora = scene.get("hora", "?")
        lugar = scene.get("lugar", agent.zona)
        clima = scene.get("clima", "27°C")
        personas = scene.get("personas_presentes", [])

        user_parts.append("=== ESCENA ACTUAL ===")
        user_parts.append(f"Hora: {hora} | Lugar: {lugar} | Clima: {clima}")
        if personas:
            user_parts.append(f"Personas presentes: {', '.join(personas)}")
        if scene_context:
            user_parts.append(f"Contexto: {scene_context}")
        user_parts.append("")
        user_parts.append("=== INSTRUCCIÓN ===")
        user_parts.append(
            f"Respondé como {agent.name}. Una sola acción corta o diálogo breve en "
            f"español huilense. Primera persona. No narres en tercera persona. "
            f"Máximo 3-4 oraciones."
        )

        return {"system": system_prompt, "user": "\n".join(user_parts)}


# ============================================================
# CLI
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("PromptBuilder — demo")
    print("=" * 60)
    pb = PromptBuilder()
    agents = pb.parse_agents()
    print(f"\n{len(agents)} agentes parseados:")
    for slug, a in agents.items():
        print(f"  - {a.name:30s} ({a.age} años, {a.profile:8s}, {a.zona[:30]})")

    print()
    print("=" * 60)
    print("PROMPT PARA DON ELIÉCER EN LA FINCA MATARREDONDA (sample)")
    print("=" * 60)
    p = pb.build_agent_prompt(
        agent_name="Don Eliécer",
        scene={"hora": "07:30", "lugar": "Finca Matarredonda (vereda)",
               "clima": "26°C", "personas_presentes": ["Don Rosalío (ganadero rival, llegó a discutir linderos)"]},
        scene_context="Don Rosalío llegó a la tranquera a reclamar por los linderos. Hace calor. Don Cecilio (cura) ofició misa temprano.",
    )
    print("--- SYSTEM (primeros 800 chars) ---")
    print(p["system"][:800])
    print("...")
    print()
    print("--- USER ---")
    print(p["user"])