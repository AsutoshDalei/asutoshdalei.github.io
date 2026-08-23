# User site: AsutoshDalei.github.io

This folder contains the ready-to-push contents of a **second repository** that fixes the
domain-root problem on GitHub Pages.

## Why this exists

The portfolio repo (`AsutoshDalei/AsutoshDalei`) is a *project* site, so it is served only
under `https://asutoshdalei.github.io/AsutoshDalei/`. Domain-root probes fail:

| URL | Status without this repo |
|---|---|
| `https://asutoshdalei.github.io/` | 404 |
| `https://asutoshdalei.github.io/robots.txt` | 404 |
| `https://asutoshdalei.github.io/sitemap.xml` | 404 |

AI agents and audit crawlers routinely probe these root paths first, which caused the
"could not fetch homepage" / "crawlers blocked" findings in the agentic-readiness audit.
A **user site** repo is always served at the domain root, which fixes all three.

## Setup (one time, ~2 minutes)

1. Create a new public repository named exactly: `AsutoshDalei.github.io`
   (Settings → keep default branch `main`).
2. Copy the contents of this folder into that new repo (not the folder itself):

   ```bash
   cd /path/to/new/repo
   cp -R /Users/asutoshdalei/Work/AsutoshDalei/user-site/* .
   cp -R /Users/asutoshdalei/Work/AsutoshDalei/user-site/.nojekyll . 2>/dev/null || true
   git add -A && git commit -m "Domain-root landing, robots.txt, sitemap for agent reachability"
   git push origin main
   ```

3. Enable Pages: repo **Settings → Pages → Source: Deploy from a branch → Branch: main,
   Folder: / (root)** → Save.
4. Wait ~1 minute for the first deploy.

## Verify afterwards

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://asutoshdalei.github.io/            # expect 200
curl -s -o /dev/null -w "%{http_code}\n" https://asutoshdalei.github.io/robots.txt  # expect 200
curl -s -o /dev/null -w "%{http_code}\n" https://asutoshdalei.github.io/sitemap.xml # expect 200
curl -s -o /dev/null -w "%{http_code}\n" https://asutoshdalei.github.io/llms.txt    # expect 200
```

Or run the repo's verifier with the root scope included:

```bash
python3 scripts/verify.py --live https://asutoshdalei.github.io/AsutoshDalei/ --include-root
```

## Contents

| File | Purpose |
|---|---|
| `index.html` | Meaningful 200 landing page at domain root (H1 + bio + JSON-LD) that instantly redirects into `/AsutoshDalei/` |
| `robots.txt` | Root-level crawler policy + sitemap pointer |
| `sitemap.xml` | Root-level sitemap covering both the root page and all portfolio URLs |
| `llms.txt` | Agent guide pointing from the domain root into the portfolio |

Keep these files in sync if portfolio URLs ever change. The portfolio repo's
`scripts/verify.py --include-root` will flag mismatches.
