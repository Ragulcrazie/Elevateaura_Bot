#!/usr/bin/env python3
"""Deliverable 19: a readable index of every page implemented in this pass.

Reads seo/build/pages.csv (written by build_pages.py) and emits
seo/19-page-implementation-index.md, grouped by cluster, with the target query, intent,
persona and roadmap phase for each page. Run from the repo root after build_pages.py.
"""
import csv
import os
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CLUSTER_TITLES = {
    "aura-business": "Aura Business (distribution, field service, AMC)",
    "hims": "HIMS (hospital and clinic management)",
    "aurapacs": "AuraPACS (imaging, PACS, DICOM)",
    "aura-learn": "Aura Learn (LMS, training, exam prep)",
    "product-development": "Product Development (embedded and device software)",
    "mobile-app-development": "Mobile app development",
    "web-development": "Websites and e-commerce",
    "seo-services": "SEO services",
    "resources": "Guides (/resources/)",
    "compare": "Comparisons (/compare/)",
    "case-studies": "Case studies (/case-studies/)",
}
ORDER = list(CLUSTER_TITLES)


def main():
    os.chdir(ROOT)
    rows = list(csv.DictReader(open("seo/build/pages.csv", encoding="utf-8")))
    by = defaultdict(list)
    for r in rows:
        by[r["cluster"]].append(r)
    out = ["# Deliverable 19: page-by-page implementation index", "",
           "Every page generated in this pass, with the query it targets and why it exists. "
           "Source content lives in `seo/build/content/<cluster>__<slug>.json`; the HTML is built by "
           "`seo/build/build_pages.py`. Pages that already existed before this engagement are listed in "
           "`02-url-inventory.csv`, not here.", "",
           "| Total generated pages | %d |" % len(rows), "|---|---|",
           "| Clusters | %d |" % len(by),
           "| New content hubs | resources, compare, case-studies, mobile-app-development, web-development, seo-services |", ""]
    for c in ORDER:
        if c not in by:
            continue
        out += ["## %s" % CLUSTER_TITLES[c], "",
                "| URL | Primary keyword | Intent | Type | Phase |", "|---|---|---|---|---|"]
        for r in sorted(by[c], key=lambda x: (int(x["phase"] or 9), x["slug"])):
            url = r["url"].replace("https://elevateaura.co.in", "")
            out.append("| `%s` | %s | %s | %s | %s |" % (url, r["primary_keyword"], r["intent"], r["page_type"], r["phase"]))
        out.append("")
    out += ["## How to add the next page", "",
            "1. Write `seo/build/content/<cluster>__<slug>.json` against `build/CONTENT_SCHEMA.md` and `build/FACTS.md`.",
            "2. `python seo/build/build_pages.py` (it refuses thin, duplicate or unsupported content).",
            "3. Add the page to two sibling `related` blocks, and to `RELATED` in `build/patch_existing.py` if the hand-built pages should link to it.",
            "4. `python seo/build/build_sitemaps.py && python seo/build/inventory.py && python seo/build/build_master_db.py && python seo/build/build_index_doc.py && python seo/build/qa.py`.", ""]
    with open("seo/19-page-implementation-index.md", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out))
    print("index doc: %d pages across %d clusters" % (len(rows), len(by)))


if __name__ == "__main__":
    main()
