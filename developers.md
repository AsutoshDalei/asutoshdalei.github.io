# Developer Resources & Docs Index — Asutosh Dalei

Every machine-readable file and developer resource published by this site, at predictable URLs. This is the docs index for [asutoshdalei.github.io](https://asutoshdalei.github.io/), the personal portfolio of Asutosh Dalei.

HTML version: <https://asutoshdalei.github.io/developers.html>

## Machine-readable files

- [llms.txt](https://asutoshdalei.github.io/llms.txt) — agent-oriented site guide with when-to-use guidance and a full site map
- [sitemap.xml](https://asutoshdalei.github.io/sitemap.xml) — all indexable URLs with lastmod dates
- [robots.txt](https://asutoshdalei.github.io/robots.txt) — crawl rules plus pointers to machine-readable entry points
- [.well-known/mcp](https://asutoshdalei.github.io/.well-known/mcp) — MCP discovery manifest (documentation only; no live server)

## Markdown versions of every page

Each HTML page has a Markdown twin at the same path with an `.md` extension, served as `text/markdown`. GitHub Pages does not negotiate on the `Accept` header and cannot emit `Vary: Accept`; to get Markdown, request the `.md` URL directly.

- [index.md](https://asutoshdalei.github.io/index.md) — full home-page content as Markdown
- [about.md](https://asutoshdalei.github.io/about.md)
- [contact.md](https://asutoshdalei.github.io/contact.md)
- [privacy.md](https://asutoshdalei.github.io/privacy.md)
- [404.md](https://asutoshdalei.github.io/404.md) — recovery links served for missing paths
- [index.txt](https://asutoshdalei.github.io/index.txt) — plain-text résumé profile

## API status

This is a static personal portfolio hosted on GitHub Pages. There is no public REST API, so there are no API docs and no OpenAPI spec. There are no webhooks. The [.well-known/mcp](https://asutoshdalei.github.io/.well-known/mcp) manifest declares zero capabilities and exists only for discovery documentation.

## Security notes

- [docs/chat-security.md](https://asutoshdalei.github.io/docs/chat-security.md) — how the (currently paused) browser chat feature handled API keys and abuse controls

Security contact: [asutoshdalei@gmail.com](mailto:asutoshdalei@gmail.com)

## Structured data

All HTML pages embed JSON-LD (`application/ld+json`) Person, Organization, and ProfessionalService schemas, plus Open Graph and Twitter Card metadata.
