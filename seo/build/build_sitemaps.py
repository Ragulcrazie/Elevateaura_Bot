#!/usr/bin/env python3
"""Segmented XML sitemaps for elevateaura.co.in.

Writes sitemap.xml (index) plus sitemap-core.xml, sitemap-products.xml,
sitemap-services.xml, sitemap-locations.xml and sitemap-resources.xml.
lastmod comes from the last git commit that touched the file (today's date for
files not yet committed). Pages carrying a robots noindex tag are skipped.

Run from the repo root: python seo/build/build_sitemaps.py
"""
import datetime
import glob
import os
import re
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SITE = "https://elevateaura.co.in"
TODAY = datetime.date.today().isoformat()

CORE = ["index.html", "pages/about.html", "pages/contact.html", "pages/careers.html", "about.html", "contact.html",
        "pricing.html", "how-it-works.html", "modules.html", "partner.html", "privacy.html", "terms.html"]
PRODUCT_DIRS = ["aura-business", "hims", "aurapacs", "aura-learn", "product-development", "auracare"]
SERVICE_DIRS = ["mobile-app-development", "web-development", "seo-services"]
RESOURCE_DIRS = ["resources", "compare", "case-studies"]
HUBS = ["aura-business.html", "hims.html", "aurapacs.html", "aura-learn.html", "product-development.html"]
LOCATION_RE = re.compile(r"-(chennai|bangalore|hyderabad|mumbai|coimbatore|madurai|delhi|india|uae|saudi-arabia|nigeria|kenya|usa|uk|australia)/?$")


def lastmod(path):
    try:
        out = subprocess.check_output(["git", "log", "-1", "--format=%cs", "--", path], cwd=ROOT, stderr=subprocess.DEVNULL).decode().strip()
        if out:
            # Uncommitted edits count as modified today.
            st = subprocess.check_output(["git", "status", "--porcelain", "--", path], cwd=ROOT).decode().strip()
            return TODAY if st else out
    except Exception:
        pass
    return TODAY


def url_for(path):
    path = path.replace("\\", "/")
    if path == "index.html":
        return SITE + "/"
    if path.endswith("/index.html"):
        return SITE + "/" + path[:-len("index.html")]
    return SITE + "/" + path


def noindex(path):
    with open(os.path.join(ROOT, path), encoding="utf-8", errors="ignore") as fh:
        head = fh.read(4000)
    return 'name="robots"' in head and "noindex" in head


def entry(path, priority, changefreq=None):
    u = url_for(path)
    cf = "<changefreq>%s</changefreq>" % changefreq if changefreq else ""
    return "  <url><loc>%s</loc><lastmod>%s</lastmod>%s<priority>%s</priority></url>" % (u, lastmod(path), cf, priority)


def write_map(name, entries):
    body = "\n".join(entries)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s\n</urlset>\n' % body
    with open(os.path.join(ROOT, name), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(xml)
    return len(entries)


def main():
    os.chdir(ROOT)
    maps = {}
    core = [entry(p, "1.0" if p == "index.html" else "0.6", "weekly" if p == "index.html" else None) for p in CORE if os.path.exists(p) and not noindex(p)]
    core += [entry(h, "0.9", "monthly") for h in HUBS if os.path.exists(h)]
    core.append(entry("auracare/index.html", "0.9", "monthly"))
    maps["sitemap-core.xml"] = core
    products, locations, services, resources = [], [], [], []
    for d in PRODUCT_DIRS:
        for p in sorted(glob.glob("%s/*/index.html" % d)):
            p = p.replace("\\", "/")
            if noindex(p):
                continue
            (locations if LOCATION_RE.search(p[:-len("index.html")]) else products).append(entry(p, "0.8"))
    for d in SERVICE_DIRS:
        for p in sorted(glob.glob("%s/index.html" % d) + glob.glob("%s/*/index.html" % d)):
            p = p.replace("\\", "/")
            if noindex(p):
                continue
            (locations if LOCATION_RE.search(p[:-len("index.html")]) else services).append(entry(p, "0.8" if p.count("/") == 1 else "0.7"))
    for d in RESOURCE_DIRS:
        for p in sorted(glob.glob("%s/index.html" % d) + glob.glob("%s/*/index.html" % d)):
            p = p.replace("\\", "/")
            if not noindex(p):
                resources.append(entry(p, "0.7" if p.count("/") == 1 else "0.6"))
    maps["sitemap-products.xml"] = products
    maps["sitemap-services.xml"] = services
    maps["sitemap-locations.xml"] = locations
    maps["sitemap-resources.xml"] = resources
    total = 0
    idx = []
    for name, entries in maps.items():
        if not entries:
            continue
        n = write_map(name, entries)
        total += n
        idx.append("  <sitemap><loc>%s/%s</loc><lastmod>%s</lastmod></sitemap>" % (SITE, name, TODAY))
        print("%-24s %d urls" % (name, n))
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s\n</sitemapindex>\n' % "\n".join(idx))
    print("sitemap.xml index written, %d urls total" % total)


if __name__ == "__main__":
    main()
