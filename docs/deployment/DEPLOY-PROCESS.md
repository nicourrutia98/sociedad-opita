# Proceso de Deploy — Sociedad Opita

**Regla de oro**: 1 deploy = 1 tag + 1 entrada de bitácora + 1 post-mortem en skill. Si no puedo hacer las 3 cosas, no deployo.

---

## 1. Versionado (semver estricto)

Cada deploy a `sociedad.opitacode.com` lleva un tag semver. Los tags se crean con `git tag -a` (annotated) para tener metadata.

| Tag | Significado | Cuándo se usa |
|---|---|---|
| `v0.0.1` | Experimental — puede fallar | Primer deploy, pruebas de integración |
| `v0.1.0` | Primer deploy público | Cuando sociedad.opitacode.com está live por primera vez |
| `v0.2.0` | Mejoras visuales / contenido | Cambios no-breaking al sitio |
| `v1.0.0` | Estable | Cuando el sitio está maduro, sin cambios breaking esperados |
| `v1.0.1` | Hotfix | Fix urgente sin breaking changes |
| `vX.Y.Z` | Semver estándar después | Major.minor.patch |

**Reglas**:
- NO se redeploya el mismo tag (un tag es inmutable)
- Cada commit a `main` que toque `web/` debería terminar en un nuevo tag
- Los tags siguen al release, no al commit

---

## 2. Pre-deploy checklist (anti-deuda-técnica)

Antes de CADA deploy, verificar:

- [ ] **Tests pasan localmente**: `pytest tests/ -v --tb=short` (debe dar 381/381)
- [ ] **Sitio actual responde**: `curl -I https://sociedad.opitacode.com` (debe dar 200)
- [ ] **Tag es semver correcto**: `git tag --list 'v*' | sort -V | tail -1` para ver el último
- [ ] **Bitácora lista**: hay un draft de la entrada para el nuevo tag en `web/bitacora.html`
- [ ] **Skill actualizada**: la skill `cloudflare-pages-deploy` está al día con los últimos post-mortems
- [ ] **Sin cambios sin commitear**: `git status --short` debe estar limpio

Si CUALQUIER check falla → no deployo, arreglo primero.

---

## 3. Procedimiento de deploy

### Paso 1: Asignar tag

```bash
# Ver el último tag
git tag --list 'v*' | sort -V | tail -1

# Asignar el nuevo tag al commit actual de main
git tag -a v0.1.0 -m "v0.1.0: primer deploy público a sociedad.opitacode.com"

# Push del tag
git push origin v0.1.0
```

### Paso 2: Trigger del deploy

El deploy se hace via Cloudflare Pages API o dashboard (ver `~/.config/opencode/skills/cloudflare-pages-deploy/SKILL.md` para el flujo detallado). El tag se usa como referencia del commit desplegado.

### Paso 3: Verificación

Después del deploy:

```bash
# Verificar que el sitio responde
curl -I https://sociedad.opitacode.com

# Verificar que el custom domain resuelve
nslookup sociedad.opitacode.com

# Verificar headers de cache
curl -I https://sociedad.opitacode.com/bitacora.html
# Debe tener: Cache-Control: public, max-age=300, must-revalidate
```

### Paso 4: Entrada en bitácora

Agregar nueva entrada en `web/bitacora.html` con:
- Tag del deploy
- Fecha
- Outcome humano
- Triple audiencia
- Detalle técnico (commit hash, archivos cambiados)
- Métricas del deploy (build time, status, URL)

Commit + push de la entrada de bitácora (siguiente tag).

### Paso 5: Post-mortem en skill

Agregar sección `## Post-Mortems` en `~/.config/opencode/skills/cloudflare-pages-deploy/SKILL.md` con:
- Qué funcionó
- Qué NO funcionó (con stack trace / HTTP codes)
- Mejoras para próximo deploy
- Comandos exactos que funcionaron (copy-paste-ready para el siguiente)

---

## 4. La regla del "no acumular deuda"

Cada deploy DEBE mejorar el sistema. Concretamente:

| Si pasa esto en un deploy... | Entonces en el próximo... |
|---|---|
| POST a Pages API dio 400 con body mínimo | Agregar pre-check `GET /pages/projects/<name>` antes del POST |
| Custom domain no resolvió inmediatamente | Documentar tiempo de propagación (~2 min típico) |
| Headers de cache no se aplicaron | Verificar que `_headers` esté en el build output (no excluido) |
| Git integration no triggereó auto-deploy | Documentar workaround: deploy manual via API hasta que se configure |
| Tests fallaron post-deploy | Agregar pre-deploy test run al checklist |

La skill `cloudflare-pages-deploy` crece orgánicamente con cada deploy. La bitácora refleja el estado real del sitio, no el "ideal".

---

## 5. Bitácora como log de deploys (no solo de código)

`web/bitacora.html` NO es solo "qué cambió en el código". Es el **registro público de cada deploy**, con:

1. **Para el visitante** (outcome humano): "qué cambia para ti"
2. **Para el investigador** (impacto académico): "qué papers / citas se ven afectados"
3. **Para el dev** (impacto técnico): "qué se deployó, con qué hash, qué status"

Esto convierte la bitácora en el **historial vivo del sitio**, no en un changelog genérico.

---

## 6. Por qué este sistema

Sin este sistema, lo que pasó hoy (deploy de sprint s1-cimientos) sería:
- ✅ Tag pusheado
- ✅ Landing v2 + bitácora commiteadas
- ❌ Bitácora con entrada del deploy: NO (el operador me corrigió)
- ❌ Skill con post-mortem: NO (la skill se creó sin él)
- ❌ Anti-deuda: NO (acumulé 4 intentos de POST 400 sin documentar)

Con el sistema, cada deploy se vuelve **reflexivo y trazable**. El costo de hacerlo bien es bajo (1 entrada de bitácora + 1 post-mortem = ~5 min), el beneficio es alto (futuro deploy es más fácil porque el post-mortem documenta los errores pasados).

---

## 7. Anti-patrones a evitar

❌ **Deploy sin reflexión**: pushear y ya, sin documentar nada. Esto es la forma #1 de acumular deuda técnica.

❌ **Mismo tag para múltiples deploys**: el tag es inmutable. Si necesitas re-deploy, usa un patch increment.

❌ **POST a API sin GET previo**: si no verificas que el proyecto existe antes de crearlo, recibes 409 conflict. Siempre GET primero.

❌ **Hardcodear tokens en scripts**: el token está en `CLOUDFLARE_API_TOKEN` (User scope env var). Nunca en archivos del repo.

❌ **Asumir que el deploy "funcionó" porque no dio error**: siempre verifica con `curl -I` y `curl -I <archivo específico>`. Los 200 OK del Pages API solo confirman que el deploy JOB terminó, no que el sitio responde.

---

## Referencias

- `~/.config/opencode/skills/cloudflare-pages-deploy/SKILL.md` — skill con el flujo operacional
- `~/.config/opencode/skills/bootstrap-deploy/SKILL.md` — skill para deploy del backend Lambda (separado)
- `web/bitacora.html` — log público de deploys
- `web/_headers` — source of truth para security + cache
- `web/README.md` — estructura del sitio
- `docs/deployment/REPLANTEAMIENTO-COMERCIAL.md` — visión del producto
