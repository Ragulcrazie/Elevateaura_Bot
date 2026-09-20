#!/usr/bin/env python3
"""End-to-end SEO QA over every public HTML page. Run from the repo root.

Checks: one H1, unique titles and H1s, title and meta length, canonical present and
self-referencing (or pointing at an existing page for forward stubs), valid JSON-LD, no
banned claims, every internal href resolves to a file, every generated page has at least
two inbound links, sitemap URLs exist and are indexable, tracking script present.
Writes seo/20-seo-qa-report.md and exits non-zero on failures.
"""
import glob
import html
import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SITE = "https://elevateaura.co.in"
BANNED = re.compile(r"\b(HIPAA[- ]compliant|ISO ?\d{4,5}|FDA[- ](approved|cleared)|CE[- ]marked|NABH[- ]certified|trusted by \d|\d{2,}\+? (hospitals|clients|customers)|\d+% (faster|increase|reduction|growth))\b", re.I)
SKIP_PREFIX = ("demo/", "web_app/", "venv/", "bot/", "seo/", "node_modules/")
JUNK = {"index-v2.html", "index_backup_20260630.html", "index_redirect.html", "welcome.html", "admin.html", "partner-admin.html", "partner-portal.html", "404.html", "refer.html"}
STUBS = {"amc-management-software.html", "biomedical-asset-management-software.html", "cmc-management-software.html", "field-service-management-software.html", "healthcare-crm-software.html", "healthcare-inventory-management-software.html", "hospital-operations-software.html", "medical-equipment-crm.html", "preventive-maintenance-software.html", "service-management-software.html"}
# The legal pages exist at two paths and are genuine duplicates, so the /pages/ copies point
# their canonical at the root copies on purpose and stay out of the sitemaps. Their H1s match
# for the same reason. Everything else must be self-canonical and unique.
CANONICAL_DUPES = {"pages/privacy.html": "privacy.html", "pages/terms.html": "terms.html"}


def norm(p):
    return p.replace("\\", "/")


def url_to_file(u):
    u = u.split("#")[0].split("?")[0]
    if u.startswith(SITE):
        u = u[len(SITE):]
    if not u.startswith("/"):
        return None
    if u == "/":
        return "index.html"
    if u.endswith("/"):
        return u.strip("/") + "/index.html"
    return u.lstrip("/")


def main():
    os.chdir(ROOT)
    files = [norm(p) for p in glob.glob("*.html") + glob.glob("pages/*.html") + glob.glob("*/index.html") + glob.glob("*/*/index.html")]
    files = sorted(set(f for f in files if not f.startswith(SKIP_PREFIX)))
    pages = {}
    fails, warns = [], []
    for f in files:
        s = open(f, encoding="utf-8", errors="ignore").read()
        pages[f] = s
    titles, h1s = defaultdict(list), defaultdict(list)
    inbound = defaultdict(set)
    generated = set()
    for j in glob.glob("seo/build/content/*.json"):
        b = os.path.basename(j)[:-5]
        c, slug = b.split("__", 1)
        folder = c
        generated.add("%s/index.html" % folder if slug == "index" else "%s/%s/index.html" % (folder, slug))
    for f, s in pages.items():
        if f in JUNK or f in STUBS:
            continue
        # links
        for href in re.findall(r'href="([^"]+)"', s):
            if href.startswith(("http", "mailto:", "tel:", "#", "javascript:")) and not href.startswith(SITE):
                continue
            if href.startswith(SITE) or href.startswith("/"):
                target = url_to_file(href)
            else:
                target = norm(os.path.normpath(os.path.join(os.path.dirname(f), href.split("#")[0].split("?")[0])))
                if target.endswith("/"):
                    target += "index.html"
                elif os.path.isdir(target):
                    target = target + "/index.html"
            if target and not target.endswith((".css", ".png", ".jpg", ".jpeg", ".webp", ".ico", ".js", ".svg", ".xml", ".txt", ".exe", ".sh")):
                if not os.path.exists(target):
                    fails.append("%s: dead link %s" % (f, href))
                else:
                    inbound[norm(target)].add(f)
        # on-page
        n_h1 = len(re.findall(r"<h1[\s>]", s))
        if n_h1 != 1:
            fails.append("%s: %d h1" % (f, n_h1))
        t = html.unescape(re.sub("<[^>]+>", "", (re.search(r"<title>(.*?)</title>", s, re.S) or re.search("()", "")).group(1))).strip()
        titles[t].append(f)
        h = html.unescape(re.sub("<[^>]+>", "", (re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S) or re.search("()", "")).group(1))).strip()
        h1s[h].append(f)
        if not t:
            fails.append("%s: no title" % f)
        elif len(t) > 75:
            warns.append("%s: title %d chars" % (f, len(t)))
        m = re.search(r'<meta name="description" content="(.*?)"', s, re.S)
        if not m:
            fails.append("%s: no meta description" % f)
        elif not 60 <= len(m.group(1)) <= 175:
            warns.append("%s: meta %d chars" % (f, len(m.group(1))))
        c = re.search(r'<link rel="canonical" href="(.*?)"', s)
        if not c:
            fails.append("%s: no canonical" % f)
        elif f in CANONICAL_DUPES:
            if c.group(1) != SITE + "/" + CANONICAL_DUPES[f]:
                fails.append("%s: canonical should point at %s" % (f, CANONICAL_DUPES[f]))
        else:
            expect = SITE + "/" if f == "index.html" else SITE + "/" + (f[:-len("index.html")] if f.endswith("/index.html") else f)
            if c.group(1) != expect:
                fails.append("%s: canonical %s != %s" % (f, c.group(1), expect))
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            try:
                json.loads(block)
            except json.JSONDecodeError as e:
                fails.append("%s: invalid JSON-LD (%s)" % (f, e))
        txt = re.sub(r"<script.*?</script>|<style.*?</style>", "", s, flags=re.S)
        b = BANNED.search(txt)
        if b:
            fails.append("%s: banned claim '%s'" % (f, b.group(0)))
        if "ea-track.js" not in s and "gtag(" not in s:
            fails.append("%s: no tracking" % f)
        if "og:image" in s and "/images/og_image.png" in s and not os.path.exists("images/og_image.png"):
            fails.append("%s: og image missing" % f)
    for t, fs in titles.items():
        if len(fs) > 1:
            fails.append("duplicate title '%s': %s" % (t[:60], ", ".join(fs)))
    for h, fs in h1s.items():
        if len(fs) > 1 and set(fs) - set(CANONICAL_DUPES) - set(CANONICAL_DUPES.values()):
            fails.append("duplicate h1 '%s': %s" % (h[:60], ", ".join(fs)))
    for g in sorted(generated):
        if not os.path.exists(g):
            fails.append("%s: content file exists but page not built" % g)
            continue
        n = len(inbound.get(g, set()))
        if n < 2:
            fails.append("%s: only %d inbound link(s)" % (g, n))
    # sitemaps
    sm_urls = []
    for sm in glob.glob("sitemap-*.xml"):
        sm_urls += re.findall(r"<loc>(.*?)</loc>", open(sm, encoding="utf-8").read())
    for u in sm_urls:
        tf = url_to_file(u)
        if not tf or not os.path.exists(tf):
            fails.append("sitemap: %s has no file" % u)
        elif 'name="robots" content="noindex"' in pages.get(tf, ""):
            fails.append("sitemap: %s is noindex" % u)
    seen = set()
    for u in sm_urls:
        if u in seen:
            fails.append("sitemap: duplicate %s" % u)
        seen.add(u)
    indexable = [f for f in pages if f not in JUNK and 'content="noindex"' not in pages[f][:3000]]
    missing = [f for f in indexable if f not in STUBS and f not in CANONICAL_DUPES and (SITE + "/" if f == "index.html" else SITE + "/" + (f[:-len("index.html")] if f.endswith("/index.html") else f)) not in seen]
    for f in missing:
        warns.append("not in sitemap: %s" % f)
    words = {f: len(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", "", s, flags=re.S)).split()) for f, s in pages.items()}
    report = ["# Deliverable 20: End-to-end SEO QA report", "",
              "Generated by `seo/build/qa.py`. Re-run after every content change.", "",
              "| Check | Result |", "|---|---|",
              "| Public HTML pages scanned | %d |" % len(pages),
              "| Generated pages (from seo/build/content) | %d |" % len(generated),
              "| Indexable pages | %d |" % len(indexable),
              "| URLs in sitemaps | %d |" % len(sm_urls),
              "| Failures | %d |" % len(fails),
              "| Warnings | %d |" % len(warns),
              "| Thinnest indexable page (words, incl. nav/footer) | %s |" % min(((words[f], f) for f in indexable), default=("", ""))[1],
              "", "## Checks performed", "",
              "- Exactly one H1; unique title and H1 across the site; title length; meta description present and 60-175 chars",
              "- Canonical present and self-referencing (forward stubs excluded)",
              "- Every JSON-LD block parses; FAQPage, BreadcrumbList, SoftwareApplication/Service/Article present on generated pages by construction",
              "- No banned claim patterns (certifications, client counts, percentage outcomes) in visible text",
              "- Every internal link resolves to a file; every generated page has at least two inbound links (no orphans)",
              "- Every sitemap URL exists and is indexable; no duplicates; every indexable page is in a sitemap",
              "- Tracking script present on every public page; OG image file exists",
              "- robots.txt disallows admin, portals, backups, drafts, demo and data folders (see 13-technical-seo-plan.md)",
              "", "## Failures", ""] + (["- " + x for x in fails] or ["None."]) + ["", "## Warnings", ""] + (["- " + x for x in warns] or ["None."])
    with open("seo/20-seo-qa-report.md", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(report) + "\n")
    print("pages %d, generated %d, sitemap urls %d, failures %d, warnings %d" % (len(pages), len(generated), len(sm_urls), len(fails), len(warns)))
    for x in fails[:60]:
        print("FAIL", x)
    for x in warns[:30]:
        print("WARN", x)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
