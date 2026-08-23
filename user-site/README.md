# user-site/ — Directory for custom domain or future user-site repo

This directory contains a standalone site package that was used when the
portfolio was served as a GitHub Pages **project site** under
`/AsutoshDalei/` and the domain root returned 404.

**This is no longer needed** — the site now serves directly at
`https://asutoshdalei.github.io/` (root), so all paths resolve correctly.
The files here are kept for reference in case you:
- Set up a custom domain that needs a root-level landing page
- Create a separate `AsutoshDalei.github.io` user-site repo

## Files

| File | Purpose |
|---|---|
| `index.html` | Root landing page with H1, bio, Person JSON-LD |
| `robots.txt` | Crawler policy + sitemap pointer |
| `sitemap.xml` | Root-level sitemap |
| `llms.txt` | Agent guide pointing into the main site |
| `.nojekyll` | Disables Jekyll processing |

If you deploy these to a separate user-site repo, keep the URLs in sync
with the main portfolio repo.