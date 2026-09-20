#!/usr/bin/env python3
"""Idempotent technical-SEO patches for the hand-built pages.

Run from the repo root: python seo/build/patch_existing.py
Each patch checks for its own marker, so the script can be re-run safely.
"""
import glob
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TRACK = '<script defer src="/assets/js/ea-track.js"></script>'
NOINDEX = '<meta name="robots" content="noindex">'

PUBLIC = (["index.html", "about.html", "contact.html", "pricing.html", "how-it-works.html", "partner.html", "modules.html",
           "aura-business.html", "hims.html", "aurapacs.html", "aura-learn.html", "product-development.html", "privacy.html", "terms.html"]
          + glob.glob("pages/*.html") + glob.glob("auracare/index.html") + glob.glob("*/*/index.html"))
JUNK_NOINDEX = ["index_backup_20260630.html", "index_redirect.html", "index-v2.html", "welcome.html", "admin.html", "partner-admin.html", "partner-portal.html"]

# Links added to the hand-built cluster pages so the new guides, comparisons and case studies
# are reachable from the pages that already rank. Keyed by cluster folder.
RELATED = {
    "aura-business": [
        ("/aura-business/medical-equipment-service-management-software/", "Service management", "Call to invoice, every job."),
        ("/aura-business/preventive-maintenance-software/", "Preventive maintenance", "PM visits from the contract."),
        ("/aura-business/installed-base-management-software/", "Installed base", "Every serial and its history."),
        ("/resources/what-is-medical-equipment-crm/", "Guide: medical equipment CRM", "The full cycle explained."),
        ("/compare/generic-crm-vs-medical-equipment-crm/", "Generic CRM vs equipment CRM", "An honest comparison."),
        ("/case-studies/carna-medicare-medical-equipment-distributor-platform/", "Case study: Carna Medicare", "A 12-module platform in 30 days."),
    ],
    "hims": [
        ("/hims/hospital-emr-software/", "Hospital EMR", "One record across departments."),
        ("/hims/hospital-insurance-tpa-billing-software/", "TPA and insurance billing", "Cash, insurance and TPA in one view."),
        ("/hims/abha-abdm-ready-hospital-software/", "ABHA and ABDM ready", "What ready actually means."),
        ("/resources/what-is-hims/", "Guide: what is HIMS", "Modules and the patient journey."),
        ("/resources/how-to-choose-hospital-management-software/", "How to choose HIMS", "A buyer's checklist."),
        ("/compare/hims-vs-hospital-erp/", "HIMS vs hospital ERP", "Which one a hospital needs."),
    ],
    "aurapacs": [
        ("/aurapacs/hybrid-pacs/", "Hybrid PACS", "On-premise speed, cloud reach."),
        ("/aurapacs/whatsapp-medical-report-sharing/", "WhatsApp report sharing", "Reports on the referrer's phone."),
        ("/aurapacs/radiology-reporting-software/", "Radiology reporting", "Templates to signed PDF."),
        ("/resources/what-is-pacs/", "Guide: what is PACS", "Plain-language explanation."),
        ("/resources/how-to-choose-pacs/", "How to choose a PACS", "A buyer's checklist."),
        ("/compare/cloud-pacs-vs-on-premise-pacs/", "Cloud vs on-premise PACS", "And the hybrid option."),
    ],
    "aura-learn": [
        ("/aura-learn/coaching-institute-management-software/", "Coaching institute software", "Batches, fees, tests, app."),
        ("/aura-learn/mock-test-platform/", "Mock test platform", "Auto-graded, instant review."),
        ("/aura-learn/healthcare-training-lms/", "Healthcare staff training", "Certify engineers and staff."),
        ("/resources/what-is-lms/", "Guide: what is an LMS", "For institutes and teams."),
        ("/compare/lms-vs-youtube-and-whatsapp-for-coaching/", "LMS vs YouTube and WhatsApp", "When free tools stop working."),
        ("/case-studies/exam-prep-learning-app/", "Case study: exam-prep app", "The product behind Aura Learn."),
    ],
    "product-development": [
        ("/product-development/medical-device-firmware-development/", "Medical device firmware", "Written to your hardware spec."),
        ("/product-development/healthcare-iot-software-development/", "Healthcare IoT software", "Device to cloud to dashboard."),
        ("/product-development/ota-firmware-update-development/", "OTA updates", "Ship fixes to devices in the field."),
        ("/mobile-app-development/", "Mobile app development", "Companion and field apps."),
        ("/product-development/embedded-software-development-usa/", "For US companies", "Remote engagement from Chennai."),
        ("/case-studies/", "Case studies", "Real platforms shipped."),
    ],
}


def read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def write(p, s):
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(s)


def patch_tracking(p, s):
    if "ea-track.js" in s or "</head>" not in s:
        return s
    return s.replace("</head>", "  " + TRACK + "\n</head>", 1)


def patch_noindex(p, s):
    if 'name="robots"' in s or "</head>" not in s:
        return s
    return s.replace("<head>", "<head>\n" + NOINDEX, 1) if "<head>" in s else s


def patch_related(p, s):
    cluster = p.split(os.sep)[0].split("/")[0]
    if cluster not in RELATED or "<!-- ea-related -->" in s:
        return s
    parts = p.split("/")
    if len(parts) == 3 and os.path.exists(os.path.join(ROOT, "seo", "build", "content", "%s__%s.json" % (cluster, parts[1]))):
        return s  # generated page: links live in its JSON
    anchor = '<section class="sec paper">\n  <div class="wrap">\n    <div class="cta rv">'
    if anchor not in s:
        return s
    items = "".join('<a class="w" href="%s"><div class="g">&#10140;</div><b>%s</b><p>%s</p></a>' % x for x in RELATED[cluster])
    block = ('<!-- ea-related -->\n<section class="sec-t soft">\n  <div class="wrap">\n    <div class="head center rv" style="margin-bottom:26px"><span class="eyebrow c">Further reading</span><h2 class="h2" style="font-size:1.5rem">Guides, comparisons and related software</h2></div>\n    <div class="who rv">%s</div>\n  </div>\n</section>\n\n' % items)
    return s.replace(anchor, block + anchor, 1)


def patch_homepage(s):
    # Mobile menu pointed HIMS at aurapacs.html.
    s = s.replace('<a href="aurapacs.html" class="mobile-link" style="color:#7c3aed;font-weight:700">HIMS</a>',
                  '<a href="hims.html" class="mobile-link" style="color:#7c3aed;font-weight:700">HIMS</a>')
    # Entity schema: Organization with sameAs, plus WebSite. Keep the ProfessionalService block's facts.
    if '"@type": "ProfessionalService"' in s and "ea-entity" not in s:
        s = s.replace('"@type": "ProfessionalService",', '"@type": ["Organization", "ProfessionalService"],\n      "@id": "https://elevateaura.co.in/#organization",\n      "sameAs": ["https://www.linkedin.com/in/ragul-sekar", "https://github.com/Ragulcrazie"],\n      "telephone": "+91-95789-71156",\n      "address": { "@type": "PostalAddress", "addressLocality": "Chennai", "addressRegion": "Tamil Nadu", "addressCountry": "IN" },', 1)
        website = ('    <!-- ea-entity -->\n    <script type="application/ld+json">\n    {"@context":"https://schema.org","@type":"WebSite","@id":"https://elevateaura.co.in/#website","url":"https://elevateaura.co.in/","name":"Elevate Aura","publisher":{"@id":"https://elevateaura.co.in/#organization"},"inLanguage":"en"}\n    </script>\n')
        s = s.replace("    <style>\n    /* Enhancement sections", website + "    <style>\n    /* Enhancement sections", 1)
    # Footer: reachable entry points for the new hubs.
    if "/case-studies/" not in s and "<h4>Company</h4>" in s:
        s = s.replace("<h4>Company</h4>", '<h4>Company</h4>\n                    <a href="/case-studies/">Case Studies</a>\n                    <a href="/resources/">Guides</a>\n                    <a href="/compare/">Comparisons</a>\n                    <a href="/mobile-app-development/">Mobile Apps</a>\n                    <a href="/web-development/">Websites &amp; E-commerce</a>\n                    <a href="/seo-services/">SEO Services</a>', 1)
    return s


def patch_hub_footers(p, s):
    """Add guide / case-study / comparison links to the product hub footers.

    Guarded by its own marker: not every hub's extra links mention /case-studies/, so keying
    off that string re-inserted the block on each run.
    """
    if "<!-- ea-hubfoot -->" in s or "<h4>Company</h4>" not in s:
        return s
    extra = {
        "aura-business.html": '<a href="/case-studies/carna-medicare-medical-equipment-distributor-platform/">Case study: Carna Medicare</a>\n<a href="/resources/what-is-medical-equipment-crm/">Guide: medical equipment CRM</a>\n<a href="/compare/crm-vs-erp-for-medical-equipment-distributors/">CRM vs ERP</a>',
        "hims.html": '<a href="/resources/what-is-hims/">Guide: what is HIMS</a>\n<a href="/compare/hims-vs-hospital-erp/">HIMS vs hospital ERP</a>\n<a href="/hims/abha-abdm-ready-hospital-software/">ABHA / ABDM ready</a>',
        "aurapacs.html": '<a href="/resources/what-is-pacs/">Guide: what is PACS</a>\n<a href="/compare/cloud-pacs-vs-on-premise-pacs/">Cloud vs on-premise PACS</a>\n<a href="/aurapacs/pacs-software-india/">PACS software India</a>',
        "aura-learn.html": '<a href="/resources/what-is-lms/">Guide: what is an LMS</a>\n<a href="/case-studies/exam-prep-learning-app/">Case study: exam-prep app</a>\n<a href="/aura-learn/coaching-institute-management-software/">Coaching institute software</a>',
        "product-development.html": '<a href="/product-development/medical-device-firmware-development/">Medical device firmware</a>\n<a href="/mobile-app-development/">Mobile app development</a>\n<a href="/case-studies/">Case studies</a>',
        "about.html": '<a href="/case-studies/">Case studies</a>', "contact.html": '<a href="/case-studies/">Case studies</a>',
        "pricing.html": '<a href="/case-studies/">Case studies</a>', "modules.html": '<a href="/resources/what-is-medical-equipment-crm/">Guide: medical equipment CRM</a>', "how-it-works.html": '<a href="/case-studies/">Case studies</a>',
    }
    base = os.path.basename(p)
    if base not in extra:
        return s
    return s.replace("<h4>Company</h4>", "<h4>Company</h4>\n<!-- ea-hubfoot -->\n" + extra[base], 1)


def patch_schema_price(s):
    """Structured data must describe what the page actually shows.

    Two Offer blocks did not: a price of 0 on the CRM page, and a 6000 INR tier on the
    Aura Business hub that appears in no visible text (pricing.html computes its tier in
    JavaScript and renders no figure). Both are removed. If the tier prices are published
    as visible copy later, the markup can come back with them.
    """
    s = s.replace(',\n"offers":{"@type":"Offer","priceCurrency":"INR","price":"0","description":"Custom-scoped per project"}', "")
    s = re.sub(r'[ \t]*"offers":\{"@type":"Offer","price":"6000"[^}]*\},?\r?\n', "", s)
    return s


def patch_titles(p, s):
    """The Aura Business company pages at the root collide with /pages/ company pages."""
    fixes = {
        "about.html": ("<title>About | Aura Business by Elevate Aura</title>", "<title>About Aura Business | The Operations Platform by Elevate Aura</title>"),
        "contact.html": ("<title>Book a Demo | Aura Business</title>", "<title>Book an Aura Business Demo | Elevate Aura, Chennai</title>"),
    }
    b = os.path.basename(p)
    if b in fixes and p.count("/") == 0 and os.sep not in p:
        s = s.replace(*fixes[b])
    return s


CANONICAL_FIXES = {
    # The company entity pages pointed their canonical at the Aura Business pages of the same
    # name, which asks Google to drop the company pages in favour of a product page. They are
    # different pages with different H1s, so each now points at itself.
    "pages/about.html": ("https://elevateaura.co.in/about.html", "https://elevateaura.co.in/pages/about.html"),
    "pages/contact.html": ("https://elevateaura.co.in/contact.html", "https://elevateaura.co.in/pages/contact.html"),
}

# Pages that had no meta description at all, so search engines wrote their own snippet.
DESCRIPTIONS = {
    "privacy.html": "How Elevate Aura collects, uses and protects the information you share through elevateaura.co.in and its products. Contact us in Chennai with any question.",
    "terms.html": "The terms that apply when you use the Elevate Aura website and its products, including scope of work, payments, ownership of code and support.",
    "pages/privacy.html": "How Elevate Aura collects, uses and protects the information you share through elevateaura.co.in and its products. Contact us in Chennai with any question.",
    "pages/terms.html": "The terms that apply when you use the Elevate Aura website and its products, including scope of work, payments, ownership of code and support.",
    "pages/careers.html": "Work with Elevate Aura in Chennai on healthcare and medical-equipment software: operations platforms, hospital systems, imaging and device software.",
}


def patch_canonical(p, s):
    if p not in CANONICAL_FIXES:
        return s
    old, new = CANONICAL_FIXES[p]
    return s.replace('<link rel="canonical" href="%s"' % old, '<link rel="canonical" href="%s"' % new, 1)


def patch_description(p, s):
    if p not in DESCRIPTIONS or 'name="description"' in s:
        return s
    tag = '<meta name="description" content="%s">' % DESCRIPTIONS[p]
    if "<title>" in s:
        t = re.search(r"<title>.*?</title>", s, re.S).group(0)
        return s.replace(t, t + "\n" + tag, 1)
    return s.replace("<head>", "<head>\n" + tag, 1)


def main():
    os.chdir(ROOT)
    changed = []
    for p in sorted(set(PUBLIC)):
        p = p.replace("\\", "/")
        s0 = read(p)
        s = patch_tracking(p, s0)
        s = patch_related(p, s)
        s = patch_schema_price(s)
        s = patch_titles(p, s)
        s = patch_canonical(p, s)
        s = patch_description(p, s)
        if p == "index.html":
            s = patch_homepage(s)
        elif "/" not in p:
            s = patch_hub_footers(p, s)
        if s != s0:
            write(p, s)
            changed.append(p)
    for p in JUNK_NOINDEX:
        if os.path.exists(p):
            s0 = read(p)
            s = patch_noindex(p, s0)
            if s != s0:
                write(p, s)
                changed.append(p)
    print("patched %d files" % len(changed))
    for c in changed:
        print("  " + c)


if __name__ == "__main__":
    main()
