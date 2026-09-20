#!/usr/bin/env python3
"""Deliverable 2: crawl the repo's public HTML and write seo/02-url-inventory.csv.

Records URL, title, H1, meta description, canonical, robots, schema types, word count,
internal-link count, cluster, and the audit action. Run from the repo root.
"""
import csv
import glob
import html
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SITE = "https://elevateaura.co.in"

ACTIONS = {
    "index-v2.html": ("NOINDEX", "Old homepage draft; noindex + robots disallow"),
    "index_backup_20260630.html": ("NOINDEX", "Backup; noindex + robots disallow"),
    "index_redirect.html": ("NOINDEX", "Redirect stub to web_app; noindex"),
    "welcome.html": ("NOINDEX", "Onboarding page for customers; noindex"),
    "admin.html": ("NOINDEX", "Internal admin; noindex + robots disallow"),
    "partner-admin.html": ("NOINDEX", "Internal admin; noindex + robots disallow"),
    "partner-portal.html": ("NOINDEX", "Logged-in portal; noindex + robots disallow"),
    "refer.html": ("REDIRECT", "Meta-refresh forward to partner.html with canonical; keep"),
    "about.html": ("IMPROVE", "Aura Business about page; retitled so it does not compete with /pages/about.html"),
    "contact.html": ("IMPROVE", "Aura Business demo page; retitled; primary conversion page for Aura Business"),
    "pages/about.html": ("IMPROVE", "Company entity page; add Organization schema and link to case studies (Phase 2)"),
    "pages/contact.html": ("KEEP", "Company contact page; primary CTA target for non-Aura-Business clusters"),
    "pricing.html": ("IMPROVE", "Module picker; publish tier prices in visible text (owner decision)"),
    "modules.html": ("KEEP", "Strong feature inventory; now linked from new feature pages"),
    "how-it-works.html": ("KEEP", ""),
    "partner.html": ("KEEP", "Partner programme; low SEO value, keep indexable"),
    "privacy.html": ("KEEP", ""), "terms.html": ("KEEP", ""),
    "pages/careers.html": ("KEEP", ""), "pages/privacy.html": ("MERGE", "Duplicate of /privacy.html; canonical to one copy (Phase 2)"),
    "pages/terms.html": ("MERGE", "Duplicate of /terms.html; canonical to one copy (Phase 2)"),
    "index.html": ("IMPROVE", "Entity schema upgraded; mobile HIMS link fixed; new hubs in footer"),
}
STUBS = ["amc-management-software.html", "biomedical-asset-management-software.html", "cmc-management-software.html",
         "field-service-management-software.html", "healthcare-crm-software.html", "healthcare-inventory-management-software.html",
         "hospital-operations-software.html", "medical-equipment-crm.html", "preventive-maintenance-software.html", "service-management-software.html"]


def field(rx, s, flags=re.S | re.I):
    m = re.search(rx, s, flags)
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else ""


def main():
    os.chdir(ROOT)
    files = ["index.html"] + sorted(glob.glob("*.html")) + sorted(glob.glob("pages/*.html")) + sorted(glob.glob("*/index.html")) + sorted(glob.glob("*/*/index.html"))
    seen, rows = set(), []
    for p in files:
        p = p.replace("\\", "/")
        if p in seen or p.startswith(("demo/", "web_app/", "404.html")):
            continue
        seen.add(p)
        s = open(p, encoding="utf-8", errors="ignore").read()
        body = re.sub(r"<script.*?</script>|<style.*?</style>", "", s, flags=re.S)
        text = re.sub(r"<[^>]+>", " ", body)
        words = len(text.split())
        links = len(re.findall(r'href="(?!https?://|mailto:|tel:|#)', s))
        schema = ";".join(sorted(set(re.findall(r'"@type":\s*"([A-Za-z]+)"', s))))
        cluster = p.split("/")[0] if "/" in p else "root"
        url = SITE + "/" if p == "index.html" else SITE + "/" + (p[:-len("index.html")] if p.endswith("/index.html") else p)
        if p in ACTIONS:
            action, note = ACTIONS[p]
        elif p in STUBS:
            action, note = "REDIRECT", "Meta-refresh forward with canonical to the cluster page; keep"
        elif p.count("/") == 2:
            action, note = ("KEEP", "Generated from seo/build/content") if os.path.exists(os.path.join("seo/build/content", "%s__%s.json" % (cluster, p.split("/")[1]))) else ("IMPROVE", "Hand-built cluster page; tracking, schema fix and further-reading links added")
        elif p in ("aura-business.html", "hims.html", "aurapacs.html", "aura-learn.html", "product-development.html", "auracare/index.html"):
            action, note = "IMPROVE", "Hub page; footer links to guides, comparisons and case studies added"
        else:
            action, note = "KEEP", ""
        rows.append({
            "url": url, "file": p, "cluster": cluster,
            "title": field(r"<title>(.*?)</title>", s), "h1": field(r"<h1[^>]*>(.*?)</h1>", s),
            "meta_description": field(r'<meta name="description" content="(.*?)"', s),
            "canonical": field(r'<link rel="canonical" href="(.*?)"', s),
            "robots": field(r'<meta name="robots" content="(.*?)"', s) or "index",
            "schema_types": schema, "word_count": words, "internal_links": links,
            "has_faq": "yes" if "FAQPage" in s else "no", "has_tracking": "yes" if "ea-track.js" in s or "gtag(" in s else "no",
            "action": action, "note": note,
        })
    out = os.path.join(ROOT, "seo", "02-url-inventory.csv")
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("inventory: %d urls -> %s" % (len(rows), out))
    from collections import Counter
    print(Counter(r["action"] for r in rows))


if __name__ == "__main__":
    main()
