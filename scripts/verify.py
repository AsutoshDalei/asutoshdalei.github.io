#!/usr/bin/env python3
"""Verify agentic-readiness requirements for the AsutoshDalei portfolio site.

Modes:
  python3 scripts/verify.py                       Offline checks against repo files
  python3 scripts/verify.py --live                Live checks against production URL
  python3 scripts/verify.py --live --include-root Also assert domain-root reachability
                                                  (passes only after user-site deploy)

Stdlib only. Exit code 0 = all checks passed, 1 = at least one failure.
"""

import argparse
import json
import random
import re
import string
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASE = "https://asutoshdalei.github.io/AsutoshDalei/"
ROOT = "https://asutoshdalei.github.io/"
AGENT_UAS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "GPTBot/1.0",
    "ChatGPT-User/1.0",
    "OAI-SearchBot/1.0",
    "ClaudeBot/1.0",
    "anthropic-ai/1.0",
    "Google-Extended",
    "DeepSeekBot/1.0",
    "PerplexityBot/1.0",
    "ora-agent/1.0",
]
TIMEOUT = 25


class TextExtract(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def visible_text(html):
    p = TextExtract()
    p.feed(html)
    return re.sub(r"\s+", " ", " ".join(p.parts)).strip()


def inner_tag_text(html, pattern):
    m = re.search(pattern, html, re.S | re.I)
    if not m:
        return None
    return re.sub(r"<[^>]+>", "", m.group(1)).strip()


results = []


def record(name, ok, detail="", warn=False, skip=False):
    status = "SKIP" if skip else ("PASS" if ok else ("WARN" if warn else "FAIL"))
    results.append((status, name, detail))


def read(rel):
    path = REPO / rel
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def http_fetch(url, ua=AGENT_UAS[0]):
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, dict(resp.headers), resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        return e.code, dict(e.headers or {}), body
    except (urllib.error.URLError, OSError, TimeoutError):
        return 0, {}, ""


def check_offline():
    base_re = re.compile(r"https://asutoshdalei\.github\.io/(?!AsutoshDalei)")

    sm = read("sitemap.xml")
    locs = []
    if sm:
        try:
            root = ET.fromstring(sm)
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            locs = [e.text.strip() for e in root.findall(".//sm:loc", ns) or root.findall(".//loc")]
            bad = [u for u in locs if "#" in u or not u.startswith(BASE)]
            record(
                "sitemap.xml valid, project-scoped URLs",
                len(locs) > 0 and not bad,
                f"{len(locs)} URLs" + (f"; bad: {bad}" if bad else ""),
            )
            required = {"about.html", "contact.html", "privacy.html"}
            missing = [r for r in required if not any(u.endswith(r) for u in locs)]
            record("sitemap lists trust pages", not missing, f"missing: {missing}" if missing else "")
        except ET.ParseError as e:
            record("sitemap.xml valid, project-scoped URLs", False, f"XML parse error: {e}")
    else:
        record("sitemap.xml valid, project-scoped URLs", False, "file missing")

    rb = read("robots.txt")
    record(
        "robots.txt Sitemap points at project sitemap",
        bool(rb) and f"Sitemap: {BASE}sitemap.xml" in rb,
    )

    idx = read("index.html") or ""
    record('index.html <html lang="en">', bool(re.search(r'<html[^>]*\blang="en"', idx, re.I)))
    canon = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', idx, re.I)
    record("index.html rel=canonical", bool(canon) and canon.group(1) == BASE,
           canon.group(1) if canon else "missing")
    og_img = re.search(r'<meta\s+property="og:image"\s+content="(https://[^"]+)"', idx, re.I)
    record("index.html og:image absolute URL", bool(og_img))
    record("index.html og:type", bool(re.search(r'<meta\s+property="og:type"', idx, re.I)))

    lds = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', idx, re.S)
    parsed, parse_err = [], None
    for block in lds:
        try:
            parsed.append(json.loads(block))
        except json.JSONDecodeError as e:
            parse_err = e
    person = next((d for d in parsed if d.get("@type") == "Person"), None)
    svc = next((d for d in parsed if d.get("@type") == "ProfessionalService"), None)
    record("JSON-LD parses", bool(lds) and parse_err is None, str(parse_err) if parse_err else f"{len(parsed)} blocks")
    record("Person schema has url+image",
           bool(person) and bool(person.get("url")) and bool(person.get("image")))
    record("ProfessionalService schema has contactPoint+address+url",
           bool(svc) and bool(svc.get("contactPoint")) and bool(svc.get("address")) and bool(svc.get("url")))

    for page in ("about.html", "contact.html", "privacy.html"):
        html = read(page)
        if not html:
            record(f"{page}: exists, canonical, H1, 500+ chars", False, "file missing")
            continue
        text = visible_text(html)
        pc = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', html, re.I)
        h1 = inner_tag_text(html, r"<h1[^>]*>(.*?)</h1>")
        ok = (
            bool(pc) and pc.group(1) == f"{BASE}{page}"
            and bool(h1) and len(text) >= 500
            and bool(re.search(r'<html[^>]*\blang="en"', html, re.I))
        )
        record(f"{page}: exists, canonical, H1, 500+ chars", ok,
               f"text={len(text)} chars")

    for page in ("index.md", "about.md", "contact.md", "privacy.md"):
        md = read(page)
        ok = bool(md) and md.lstrip().startswith("#") and len(md) >= 500
        record(f"{page}: markdown twin, 500+ chars", ok, f"{len(md or '')} chars")

    lt = read("llms.txt")
    lines = (lt or "").splitlines()
    links = re.findall(r"\((https://[^\s)]+)\)", lt or "")
    ok = (
        bool(lines) and lines[0].startswith("# ")
        and len(lines) > 1 and lines[1].strip().startswith(">")
        and "## When to use" in lt
        and all(u.startswith("https://") for u in links)
        and any(u == BASE for u in links)
    )
    record("llms.txt: title, summary, when-to-use, valid links", ok,
           f"{len(links)} links")

    nf = read("404.html")
    ok = bool(nf) and "llms.txt" in nf and "sitemap" in nf and BASE in nf
    record("404.html recovery links (home, llms.txt, sitemap)", ok)

    try:
        mcp = json.loads(read(".well-known/mcp") or "")
        record(".well-known/mcp manifest",
               bool(mcp.get("mcp_version"))
               and bool(mcp.get("documentation"))
               and bool(mcp.get("security", {}).get("security_contact")),
               "docs-only endpoints={}".format(bool(mcp.get("endpoints"))))
    except json.JSONDecodeError as e:
        record(".well-known/mcp manifest", False, f"invalid JSON: {e}")

    it = read("index.txt")
    record("index.txt is plain text", bool(it) and "<!DOCTYPE" not in it and "<html" not in it)

    stale = []
    for p in sorted(REPO.iterdir()):
        if p.is_file() and p.suffix.lower() in (".html", ".md", ".txt", ".xml"):
            hits = [m for m in base_re.finditer(p.read_text(encoding="utf-8", errors="replace"))]
            if hits:
                stale.append(p.name)
    record("no stale domain-root URLs outside user-site/", not stale,
           f"stale: {stale}" if stale else "")

    us = REPO / "user-site"
    needed = ["index.html", "robots.txt", "sitemap.xml", "llms.txt", "README.md"]
    missing = [f for f in needed if not (us / f).exists()]
    record("user-site package complete", not missing, f"missing: {missing}" if missing else "")


def check_live(base_url, include_root=False):
    home = base_url if base_url.endswith("/") else base_url + "/"
    rand = "".join(random.choices(string.ascii_lowercase, k=16))

    for ua in AGENT_UAS:
        code, _, _ = http_fetch(home, ua=ua)
        record(f"homepage reachable as {ua}", code == 200, f"HTTP {code}")

    _, _, html = http_fetch(home)
    text = visible_text(html)
    record("homepage H1 present", "Asutosh Dalei" in (inner_tag_text(html, r"<h1[^>]*>(.*?)</h1>") or ""))
    record("homepage 500+ chars without JS", len(text) >= 500, f"{len(text)} chars")
    record("homepage canonical + JSON-LD served",
           'rel="canonical"' in html and "application/ld+json" in html)

    machine = ["robots.txt", "sitemap.xml", "llms.txt", ".well-known/mcp", "index.md",
               "index.txt", "404.html"]
    for f in machine:
        code, _, _ = http_fetch(home + f)
        record(f"/{f} reachable", code == 200, f"HTTP {code}")

    for page in ("about.html", "contact.html", "privacy.html"):
        code, _, body = http_fetch(home + page)
        record(f"/{page} 200 with 500+ chars", code == 200 and len(visible_text(body)) >= 500,
               f"HTTP {code}, {len(visible_text(body))} chars")

    code, _, body = http_fetch(home + f"not-a-real-path-{rand}")
    recover = "llms.txt" in body or "sitemap" in body
    record("nonexistent path returns real 404", code == 404, f"HTTP {code}")
    record("404 body offers recovery links", recover)

    if home + "sitemap.xml":
        code, _, sm_body = http_fetch(home + "sitemap.xml")
        if code == 200:
            try:
                root = ET.fromstring(sm_body)
                ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
                urls = [e.text.strip() for e in root.findall(".//sm:loc", ns)]
                for u in urls:
                    c, _, _ = http_fetch(u)
                    record(f"sitemap URL -> 200: {u}", c == 200, f"HTTP {c}")
            except ET.ParseError as e:
                record("live sitemap parses", False, str(e))
        else:
            record("live sitemap parses", False, f"HTTP {code}")

    if include_root:
        for path in ("/", "/robots.txt", "/sitemap.xml", "/llms.txt"):
            code, _, _ = http_fetch(ROOT + path.lstrip("/"))
            record(f"domain root {path} reachable", code == 200, f"HTTP {code}")
        code, _, body = http_fetch(ROOT + f"not-a-real-path-{rand}")
        record("domain root nonexistent path returns 404", code == 404, f"HTTP {code}")
    else:
        record("domain-root checks skipped (use --include-root after user-site deploy)",
               True, warn=False, skip=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--live", nargs="?", const=BASE, metavar="URL",
                    help="run live checks against URL (default production)")
    ap.add_argument("--offline", action="store_true", help="run offline file checks")
    ap.add_argument("--include-root", action="store_true",
                    help="with --live: also assert domain-root reachability")
    args = ap.parse_args()

    if args.live is None and not args.offline:
        args.offline = True

    if args.offline:
        check_offline()
    if args.live is not None:
        check_live(args.live, include_root=args.include_root)

    width = max(len(n) for _, n, _ in results)
    fails = warns = passes = 0
    for status, name, detail in results:
        mark = {"PASS": "✓", "FAIL": "✗", "WARN": "!", "SKIP": "-"}[status]
        print(f"{mark} [{status:^4}] {name:<{width}}  {detail}")
        if status == "FAIL":
            fails += 1
        elif status == "WARN":
            warns += 1
        elif status == "PASS":
            passes += 1
    total = len(results)
    print(f"\n{total} checks: {passes} passed, {fails} failed, {warns} warnings, "
          f"{total - passes - fails - warns} skipped")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
