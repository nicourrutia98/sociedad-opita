# Web — `sociedad.opitacode.com`

Static public site for **Sociedad Opita** (Tello, Huila, Colombia).

## What lives here

| File / dir | Purpose |
|---|---|
| `index.html` | Landing v2 (OSINT-driven re-architecture, 2026-06-22) |
| `bitacora.html` | Bitácora del proyecto (sprint changelog) |
| `about.html` | Acerca: qué es, qué no es, por qué existe |
| `methodology.html` | Metodología forense (Big Five + Lomnitz + Dunbar + Hofstede) |
| `limitations.html` | Limitaciones declaradas |
| `ethics.html` | Compromisos éticos públicos |
| `for-researchers.html` | Para investigadores (BibTeX, citas, flujos) |
| `index_game.html` | Entry point del mundo 2D (PixiJS) |
| `game/` | PixiJS engine + map data + HUD + export |
| `style.css` | Estilo base (paleta marrón + Georgia serif) |
| `app.js` | JS compartido |
| `_headers` | Cloudflare Pages security + cache headers |

## Deploy

This site is deployed to **Cloudflare Pages** at `sociedad.opitacode.com`.

### Production deploy (manual, via dashboard)

Cloudflare Pages is configured for automatic deploys on push to the `main` branch:

1. `git push origin main` (from `feature/s1-cimientos` after merge)
2. Cloudflare Pages detects the push, builds (no build step — static files), and deploys
3. `sociedad.opitacode.com` updated within ~30 seconds

### First-time setup (one-time, via Cloudflare dashboard)

1. Go to <https://dash.cloudflare.com/?to=/:account/pages>
2. **Create a project** → **Connect to Git** → select `nicourrutia98/sociedad-opita`
3. **Project name**: `sociedad-opita`
4. **Production branch**: `main`
5. **Build command**: *(leave empty — no build step)*
6. **Build output directory**: `web`
7. **Root directory (advanced)**: `web` (alternative: leave at repo root and put `_headers`/`_redirects` at `web/`)
8. **Environment variables**: none needed for static deploy
9. Click **Save and Deploy**
10. After first deploy: **Custom domains** → add `sociedad.opitacode.com` (Cloudflare will verify DNS automatically if `opitacode.com` is already on Cloudflare)

### Preview deploys

Every PR automatically gets a preview URL like `https://<hash>.sociedad-opita.pages.dev`. Use this to validate changes before merging to `main`.

## File conventions

- HTML pages: `<section>` blocks with H2/H3 hierarchy, `class="info-nav"` for nav, `class="info-hero"` for hero blocks
- CSS: inline `<style>` blocks for page-specific styles, `style.css` for shared
- New pages: add link to `info-nav` in every existing page (5 places: `index.html`, `bitacora.html`, `about.html`, `methodology.html`, `limitations.html`, `ethics.html`, `for-researchers.html`, `index_game.html`)
- Naming: nunca uses "changelog" o "release notes" en el sitio. Usa "Bitácora del proyecto" (léxico del sitio: monumento, memoria, pueblo)

## Local preview

```powershell
# Opción 1: file:// directo (rápido, sin servidor)
start web/index.html

# Opción 2: servidor local (mejor para probar _headers y cache)
cd web
python -m http.server 8000
# → http://localhost:8000
```

## What is NOT here

- **Backend** (FastAPI + DeepSeek): deployed separately to AWS Lambda via `deploy/lambda_deploy.py` (see `~/.config/opencode/skills/bootstrap-deploy/SKILL.md`)
- **Repositorio académico** (paper, datos crudos, validador): in repo root + `papers/sociedad-opita-benchmark/`
- **Capa comercial** (futuro videojuego 2D con monetización): proyecto separado, no en este repo (per `REPLANTEAMIENTO-COMERCIAL.md` §2 — open source core + commercial layer on top)
