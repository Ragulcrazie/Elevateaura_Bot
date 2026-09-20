#!/usr/bin/env python3
"""Static page generator for the Elevate Aura SEO system.

Reads every JSON file in seo/build/content/, renders it with the shared cluster
template (same classes as the hand-built cluster pages, so the existing cluster CSS
applies) and writes <folder>/<slug>/index.html at the repo root. Also writes
seo/build/pages.csv, the manifest that feeds the master page database.

Run from the repo root:  python seo/build/build_pages.py [--check]
"""
import csv
import glob
import html
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONTENT = os.path.join(os.path.dirname(__file__), "content")
SITE = "https://elevateaura.co.in"
WA = "919578971156"
EMAIL = "elevateauraofficial@gmail.com"
OG = SITE + "/images/og_image.png"

CASES = [
    {"icon": "&#127973;", "name": "Carna Medicare", "tag": "Medical Equipment &middot; Chennai",
     "h": "12-module operations platform",
     "problem": "A distribution business run entirely on WhatsApp and Excel.",
     "built": "Field app, manager dashboard, GST billing and payment tracking.",
     "stack": "React Native, Supabase, WordPress.", "out": "Shipped end to end in 30 days",
     "href": "/case-studies/carna-medicare-medical-equipment-distributor-platform/"},
    {"icon": "&#129302;", "name": "Medline Robotics", "tag": "Medical Robotics &middot; Chennai",
     "h": "E-commerce &amp; distributor platform",
     "problem": "No online store or way to manage distributors.",
     "built": "Storefront, distributor portal, quote-to-order and 253 SEO pages.",
     "stack": "Supabase, JavaScript, Playwright.", "out": "Live store and partner portal",
     "href": "/case-studies/medline-robotics-ecommerce-distributor-platform/"},
    {"icon": "&#127891;", "name": "Elevate Aura", "tag": "Own product &middot; Play Store",
     "h": "Self-funded EdTech build",
     "problem": "Build and run a learning product end to end.",
     "built": "Android app, Telegram bots and content automation.",
     "stack": "Flutter, Python, Supabase.", "out": "Live on Google Play",
     "href": "/case-studies/exam-prep-learning-app/"},
]

CLUSTERS = {
    "aura-business": dict(folder="aura-business", css="/aura-business/biz.css", hub="/aura-business.html",
                          hub_name="Aura Business", product="Aura Business", theme="#6d28d9",
                          strip="Aura Business, the operations platform", schema="SoftwareApplication",
                          app_cat="BusinessApplication", contact="/contact.html", demo="/demo/aura-business.html",
                          cta="Book a Free Strategy Call", site_name="Aura Business by Elevate Aura",
                          foot_desc="The operations platform for distributors, dealers and field-service businesses. CRM, service, AMC, inventory and GST billing in one system.",
                          foot_links=[("/aura-business/medical-equipment-crm-software/", "Medical Equipment CRM"), ("/aura-business/medical-equipment-field-service-software/", "Field Service"), ("/aura-business/medical-equipment-amc-cmc-software/", "AMC / CMC"), ("/aura-business/medical-equipment-inventory-software/", "Inventory"), ("/aura-business/medical-equipment-billing-software/", "Billing"), ("/modules.html", "All 87 modules")]),
    "hims": dict(folder="hims", css="/hims/hims.css", hub="/hims.html", hub_name="HIMS", product="HIMS", theme="#6d28d9",
                 strip="HIMS &amp; AuraPACS clinical software", schema="SoftwareApplication", app_cat="HealthApplication",
                 contact="/pages/contact.html", demo="/demo/hospital.html", cta="Book a Free Strategy Call", site_name="HIMS by Elevate Aura",
                 foot_desc="A hospital and clinic management system for Indian hospitals, clinics and diagnostic centres: OP and IP, EMR, pharmacy, lab, inventory and billing, with AuraPACS imaging.",
                 foot_links=[("/hims/hospital-management-system/", "Hospital Management System"), ("/hims/clinic-management-software/", "Clinic Management"), ("/hims/hospital-billing-software/", "Hospital Billing"), ("/hims/hospital-pharmacy-management/", "Pharmacy"), ("/hims/hospital-laboratory-management/", "Laboratory"), ("/aurapacs.html", "AuraPACS imaging")]),
    "aurapacs": dict(folder="aurapacs", css="/aurapacs/pacs.css", hub="/aurapacs.html", hub_name="AuraPACS", product="AuraPACS", theme="#6d28d9",
                     strip="AuraPACS, browser-based imaging", schema="SoftwareApplication", app_cat="HealthApplication",
                     contact="/pages/contact.html", demo="https://pacs.elevateaura.co.in/", cta="Try the live demo", site_name="AuraPACS by Elevate Aura",
                     foot_desc="Hybrid on-premise and cloud PACS with a browser DICOM viewer, modality worklist, reporting and WhatsApp report sharing, for clinics, diagnostic centres and hospitals.",
                     foot_links=[("/aurapacs/pacs-software/", "PACS Software"), ("/aurapacs/dicom-viewer/", "DICOM Viewer"), ("/aurapacs/cloud-pacs-software/", "Cloud PACS"), ("/aurapacs/ris-pacs-software/", "RIS PACS"), ("/aurapacs/dicom-worklist-software/", "DICOM Worklist"), ("/hims.html", "HIMS")]),
    "aura-learn": dict(folder="aura-learn", css="/aura-learn/learn.css", hub="/aura-learn.html", hub_name="Aura Learn", product="Aura Learn", theme="#6d28d9",
                       strip="Aura Learn, the learning platform", schema="SoftwareApplication", app_cat="EducationalApplication",
                       contact="/pages/contact.html", demo="/demo/lms.html", cta="Book a Free Strategy Call", site_name="Aura Learn by Elevate Aura",
                       foot_desc="A learning platform with a learner app and instructor dashboard for coaching institutes, exam-prep businesses and teams certifying their own staff.",
                       foot_links=[("/aura-learn/learning-management-system/", "Learning Management System"), ("/aura-learn/online-exam-platform/", "Online Exam Platform"), ("/aura-learn/exam-preparation-platform/", "Exam Preparation"), ("/aura-learn/training-management-software/", "Training Management"), ("/aura-learn/custom-lms-development/", "Custom LMS")]),
    "product-development": dict(folder="product-development", css="/product-development/dev.css", hub="/product-development.html", hub_name="Product Development", product="Product Development", theme="#6d28d9",
                                strip="Product Development, embedded &amp; device software", schema="Service", app_cat="",
                                contact="/pages/contact.html", demo="", cta="Talk to us", site_name="Elevate Aura Product Development",
                                foot_desc="Embedded and device software for medical-device and robotics companies: firmware, communication, companion apps and cloud telemetry, written to your hardware spec.",
                                foot_links=[("/product-development/medical-device-software-development/", "Medical Device Software"), ("/product-development/embedded-software-development/", "Embedded Software"), ("/product-development/firmware-development/", "Firmware"), ("/product-development/ble-device-software/", "BLE Device Software"), ("/product-development/iot-product-development/", "IoT Product Development")]),
    "mobile-app-development": dict(folder="mobile-app-development", css="/assets/css/cluster.css", hub="/mobile-app-development/", hub_name="Mobile App Development", product="Mobile App Development", theme="#6d28d9",
                                   strip="Mobile apps for healthcare and field teams", schema="Service", app_cat="",
                                   contact="/pages/contact.html", demo="", cta="Talk to us", site_name="Elevate Aura",
                                   foot_desc="Android and iOS apps for hospitals, clinics, medical-equipment companies and field teams, built on React Native and Flutter with GPS, offline mode and Play Store publishing.",
                                   foot_links=[("/mobile-app-development/", "Mobile App Development"), ("/aura-business.html", "Aura Business"), ("/hims.html", "HIMS"), ("/product-development.html", "Device software")]),
    "web-development": dict(folder="web-development", css="/assets/css/cluster.css", hub="/web-development/", hub_name="Websites &amp; E-commerce", product="Websites & E-commerce", theme="#6d28d9",
                            strip="Websites, e-commerce and distributor portals", schema="Service", app_cat="",
                            contact="/pages/contact.html", demo="", cta="Talk to us", site_name="Elevate Aura",
                            foot_desc="WordPress and Next.js websites, online stores, product catalogues and distributor portals for medical-equipment and healthcare businesses.",
                            foot_links=[("/web-development/", "Websites &amp; E-commerce"), ("/seo-services/", "SEO Services"), ("/case-studies/", "Case Studies")]),
    "seo-services": dict(folder="seo-services", css="/assets/css/cluster.css", hub="/seo-services/", hub_name="SEO Services", product="SEO Services", theme="#6d28d9",
                         strip="Programmatic SEO and lead generation", schema="Service", app_cat="",
                         contact="/pages/contact.html", demo="", cta="Book a Strategy Call", site_name="Elevate Aura",
                         foot_desc="Programmatic and technical SEO for medical-equipment, healthcare and healthcare-SaaS businesses, built by the team that builds the sites.",
                         foot_links=[("/seo-services/", "SEO Services"), ("/web-development/", "Websites &amp; E-commerce"), ("/case-studies/", "Case Studies")]),
    "resources": dict(folder="resources", css="/assets/css/cluster.css", hub="/resources/", hub_name="Resources", product="Elevate Aura", theme="#6d28d9",
                      strip="Plain-language guides to healthcare software", schema="Article", app_cat="",
                      contact="/pages/contact.html", demo="", cta="Talk to us", site_name="Elevate Aura",
                      foot_desc="Plain-language guides to PACS, DICOM, HIMS, AMC software, CRM and device software, written by the team that builds them.",
                      foot_links=[("/resources/", "All guides"), ("/compare/", "Comparisons"), ("/case-studies/", "Case Studies")]),
    "compare": dict(folder="compare", css="/assets/css/cluster.css", hub="/compare/", hub_name="Comparisons", product="Elevate Aura", theme="#6d28d9",
                    strip="Honest comparisons for software buyers", schema="Article", app_cat="",
                    contact="/pages/contact.html", demo="", cta="Talk to us", site_name="Elevate Aura",
                    foot_desc="Side-by-side comparisons that help hospitals, diagnostic centres and distributors choose the right kind of software.",
                    foot_links=[("/compare/", "All comparisons"), ("/resources/", "Guides"), ("/case-studies/", "Case Studies")]),
    "case-studies": dict(folder="case-studies", css="/assets/css/cluster.css", hub="/case-studies/", hub_name="Case Studies", product="Elevate Aura", theme="#6d28d9",
                         strip="Real platforms shipped for real businesses", schema="Article", app_cat="",
                         contact="/pages/contact.html", demo="", cta="Talk to us", site_name="Elevate Aura",
                         foot_desc="Real platforms built and shipped by Elevate Aura for medical-equipment, robotics and learning businesses.",
                         foot_links=[("/case-studies/", "All case studies"), ("/aura-business.html", "Aura Business"), ("/web-development/", "Websites &amp; E-commerce")]),
}

CTA_DEFAULTS = {
    "resources": ("Still deciding what you need?", "Tell us how your centre or business works today and we will tell you plainly which parts of this apply to you, and which do not."),
    "compare": ("Not sure which side you are on?", "Describe your setup in a message. We will say which option fits, even when that option is not ours."),
    "case-studies": ("Have a similar problem to solve?", "Tell us how your business runs today and we will scope what a platform like this would look like for you, with a fixed timeline."),
    "seo-services": ("Want to know what is actually rankable?", "Send us your site and the products you sell. We will tell you where the real search demand is, and where it is not worth the effort."),
    "web-development": ("Planning a site or a store?", "Tell us what you sell and who buys it. We will scope the build, the catalogue structure and the pages worth ranking."),
    "mobile-app-development": ("Need an app your team will actually use?", "Tell us the workflow it has to support. We will scope the app, the backend it talks to and the timeline."),
    "product-development": ("Have a device that needs its software?", "Tell us about your hardware and what it needs to do. We will scope the software side, be clear on the boundary, and give you a fixed plan."),
}

TICK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M20 6L9 17l-5-5"/></svg>'
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'

EXTRA_CSS = """
.prose{max-width:760px;margin:0 auto}.prose p{margin:0 0 16px;color:#2b2a45;font-size:1.05rem}.prose h3{font-size:1.25rem;margin:28px 0 10px}
.prose ul{margin:0 0 18px 22px;color:#2b2a45}.prose li{margin:6px 0}.prose .lead{margin-bottom:20px}
.tbl{overflow-x:auto;background:#fff;border:1px solid var(--line2);border-radius:14px;box-shadow:var(--sh-sm)}
.tbl table{width:100%;border-collapse:collapse;font-size:.95rem;min-width:520px}.tbl th,.tbl td{padding:12px 14px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
.tbl th{background:var(--soft2);font-weight:800;font-size:.8rem;letter-spacing:.06em;text-transform:uppercase;color:var(--mut)}.tbl tr:last-child td{border-bottom:none}
.ans{background:var(--soft2);border:1px solid var(--line2);border-radius:var(--r-lg);padding:26px 28px;max-width:860px;margin:0 auto}
.ans p{margin:0 0 12px;font-size:1.08rem;color:var(--ink)}.ans p:last-child{margin:0}
.hubgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}@media(max-width:900px){.hubgrid{grid-template-columns:repeat(2,1fr)}}@media(max-width:560px){.hubgrid{grid-template-columns:1fr}}
.hubgrid a{display:block;background:#fff;border:1px solid var(--line2);border-radius:var(--r);padding:20px 22px;box-shadow:var(--sh-sm);color:var(--ink);transition:transform .2s,box-shadow .2s}
.hubgrid a:hover{transform:translateY(-3px);box-shadow:var(--sh)}.hubgrid b{display:block;font-size:1.05rem;margin-bottom:6px}.hubgrid p{color:var(--mut);font-size:.93rem;margin:0}
.byline{color:var(--mut);font-size:.9rem;margin-top:14px}
"""


def esc(s):
    return html.escape(str(s), quote=True)


def inline(s):
    """Content authors may use <b>, <a>, <em>, <span class=hl>. Everything else is literal."""
    return str(s)


def url_of(cluster, slug):
    c = CLUSTERS[cluster]
    if slug == "index":
        return "/%s/" % c["folder"]
    return "/%s/%s/" % (c["folder"], slug)


def wa_link(text):
    from urllib.parse import quote
    return "https://wa.me/%s?text=%s" % (WA, quote(text))


def render_ticks(items):
    return "".join("<li>%s%s</li>" % (TICK, inline(i)) for i in items)


def section(cls, inner):
    return '<section class="sec %s">\n  <div class="wrap">\n%s\n  </div>\n</section>\n' % (cls, inner)


def head_block(eyebrow, h2, lead=None):
    out = '    <div class="head center rv">\n'
    if eyebrow:
        out += '      <span class="eyebrow c">%s</span>\n' % inline(eyebrow)
    out += '      <h2 class="h2">%s</h2>\n' % inline(h2)
    if lead:
        out += '      <p class="lead">%s</p>\n' % inline(lead)
    out += '    </div>\n'
    return out


def render_block(b, page, c, tone):
    t = b["type"]
    if t == "answer":
        paras = "".join("<p>%s</p>" % inline(p) for p in b["paras"])
        return section(tone, head_block(b.get("eyebrow", "In one sentence"), b["h2"]) + '    <div class="ans rv">%s</div>' % paras)
    if t == "prose":
        inner = head_block(b.get("eyebrow"), b["h2"], b.get("lead"))
        body = ""
        for part in b["body"]:
            if isinstance(part, str):
                body += "<p>%s</p>" % inline(part)
            elif part.get("h3"):
                body += "<h3>%s</h3>" % inline(part["h3"])
            elif part.get("ul"):
                body += "<ul>%s</ul>" % "".join("<li>%s</li>" % inline(i) for i in part["ul"])
            elif part.get("table"):
                tb = part["table"]
                body += '<div class="tbl" style="margin:14px 0 22px"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (
                    "".join("<th>%s</th>" % inline(h) for h in tb["headers"]),
                    "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % inline(x) for x in r) for r in tb["rows"]))
        return section(tone, inner + '    <div class="prose rv">%s</div>' % body)
    if t == "pains":
        items = "".join('<div class="pain rv%s"><h3>%s</h3><p>%s</p></div>' % (" d1" if i % 3 == 1 else " d2" if i % 3 == 2 else "", inline(x["h"]), inline(x["p"])) for i, x in enumerate(b["items"]))
        return section(tone, head_block(b.get("eyebrow"), b["h2"], b.get("lead")) + '    <div class="pains">%s</div>' % items)
    if t == "flow":
        steps = []
        for i, s in enumerate(b["steps"]):
            steps.append('<div class="fs"><div class="n">%02d</div><h4>%s</h4><p>%s</p></div>' % (i + 1, inline(s["h"]), inline(s["p"])))
        return section(tone, head_block(b.get("eyebrow"), b["h2"], b.get("lead")) + '    <div class="flow rv">%s</div>' % '<div class="arr">&rarr;</div>'.join(steps))
    if t == "caps":
        groups = "".join('<div class="capg rv%s"><h3><span class="k">%s</span>%s</h3><ul>%s</ul></div>' % (" d1" if i % 2 else "", g.get("icon", "&#9679;"), inline(g["h"]), "".join("<li>%s</li>" % inline(x) for x in g["items"])) for i, g in enumerate(b["groups"]))
        foot = ('<p class="center" style="margin-top:26px"><a class="alink" href="%s">%s <span class="a">&rarr;</span></a></p>' % (b["more"]["href"], inline(b["more"]["label"]))) if b.get("more") else ""
        return section(tone, head_block(b.get("eyebrow"), b["h2"], b.get("lead")) + '    <div class="caps">%s</div>%s' % (groups, foot))
    if t == "split":
        img = b["image"]
        shot = '<div class="shot light"><div class="shot-bar"><i></i><i></i><i></i><span>%s</span></div><img src="%s" alt="%s" width="1680" height="945" loading="lazy"></div>' % (esc(img.get("bar", "elevateaura.co.in")), img["src"], esc(img["alt"]))
        text = '<div><span class="eyebrow">%s</span><h2 class="h2" style="font-size:1.5rem;margin-top:10px">%s</h2><ul class="ticks">%s</ul></div>' % (inline(b.get("eyebrow", "")), inline(b["h2"]), render_ticks(b["ticks"]))
        return section(tone, head_block(b.get("head_eyebrow"), b.get("head_h2", b["h2"]), b.get("lead")) + '    <div class="split rv">%s%s</div>' % (shot, text))
    if t == "who":
        items = "".join('<div class="w"><div class="g">%s</div><b>%s</b><p>%s</p></div>' % (x.get("icon", "&#9679;"), inline(x["b"]), inline(x["p"])) for x in b["items"])
        return section(tone, head_block(b.get("eyebrow"), b["h2"], b.get("lead")) + '    <div class="who rv">%s</div>' % items)
    if t == "usecases":
        items = "".join('<div class="u rv%s"><h3>%s</h3><p class="r"><b>Workflow:</b> %s</p><p><b>Result:</b> %s</p></div>' % (" d1" if i % 2 else "", inline(x["h"]), inline(x["workflow"]), inline(x["result"])) for i, x in enumerate(b["items"]))
        return section(tone, head_block(b.get("eyebrow"), b["h2"], b.get("lead")) + '    <div class="uc">%s</div>' % items)
    if t == "why":
        items = "".join('<div class="y"><div class="k">%s</div><b>%s</b><p>%s</p></div>' % (x.get("icon", "&#10003;"), inline(x["b"]), inline(x["p"])) for x in b["items"])
        return section(tone, head_block(b.get("eyebrow"), b["h2"], b.get("lead")) + '    <div class="why rv">%s</div>' % items)
    if t == "compare":
        cols = b["cols"]
        head = '<div class="r h"><div>&nbsp;</div>%s<div class="us">%s</div></div>' % ("".join("<div>%s</div>" % inline(x) for x in cols[:-1]), inline(cols[-1]))
        rows = "".join('<div class="r"><div class="cap">%s</div>%s<div class="us">%s</div></div>' % (inline(r[0]), "".join("<div>%s</div>" % inline(x) for x in r[1:-1]), inline(r[-1])) for r in b["rows"])
        return section(tone, head_block(b.get("eyebrow"), b["h2"], b.get("lead")) + '    <div class="cmp rv">%s%s</div>' % (head, rows))
    if t == "table":
        tb = '<div class="tbl rv"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (
            "".join("<th>%s</th>" % inline(h) for h in b["headers"]),
            "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % inline(x) for x in r) for r in b["rows"]))
        return section(tone, head_block(b.get("eyebrow"), b["h2"], b.get("lead")) + "    " + tb)
    if t == "faq":
        items = "".join("<details%s><summary>%s</summary><p>%s</p></details>" % (" open" if i == 0 else "", inline(x["q"]), inline(x["a"])) for i, x in enumerate(b["items"]))
        return section(tone, head_block(b.get("eyebrow", "Questions"), b["h2"]) + '    <div class="faq rv">%s</div>' % items)
    if t == "cases":
        keys = b.get("which", [0, 1, 2])
        items = ""
        for k in keys:
            x = CASES[k]
            items += '<a class="case" href="%s"><div class="ct"><span>%s</span>%s</div><div class="cb"><span class="tag">%s</span><h4>%s</h4><p><b>Problem:</b> %s</p><p><b>Built:</b> %s</p><p><b>Stack:</b> %s</p><div class="out">%s</div></div></a>' % (x["href"], x["icon"], x["name"], x["tag"], x["h"], x["problem"], x["built"], x["stack"], x["out"])
        return section(tone, head_block(b.get("eyebrow", "Proof"), b.get("h2", "Platforms we have actually shipped."), b.get("lead")) + '    <div class="cases rv">%s</div>' % items)
    if t == "related":
        items = "".join('<a class="w" href="%s"><div class="g">%s</div><b>%s</b><p>%s</p></a>' % (x["href"], x.get("icon", "&#10140;"), inline(x["b"]), inline(x["p"])) for x in b["items"])
        return '<section class="sec-t %s">\n  <div class="wrap">\n    <div class="head center rv" style="margin-bottom:26px"><span class="eyebrow c">%s</span><h2 class="h2" style="font-size:1.5rem">%s</h2></div>\n    <div class="who rv">%s</div>\n  </div>\n</section>\n' % (tone, inline(b.get("eyebrow", "Keep exploring")), inline(b.get("h2", "Related pages")), items)
    if t == "hubgrid":
        items = "".join('<a href="%s"><b>%s</b><p>%s</p></a>' % (x["href"], inline(x["b"]), inline(x["p"])) for x in b["items"])
        return section(tone, head_block(b.get("eyebrow"), b["h2"], b.get("lead")) + '    <div class="hubgrid rv">%s</div>' % items)
    raise ValueError("unknown block type %s" % t)


def schema_json(page, c, url):
    out = []
    crumbs = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
              {"@type": "ListItem", "position": 2, "name": html.unescape(c["hub_name"]), "item": SITE + c["hub"]}]
    if page["slug"] != "index":
        crumbs.append({"@type": "ListItem", "position": 3, "name": page["crumb"], "item": url})
    out.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": crumbs})
    org = {"@type": "Organization", "name": "Elevate Aura", "url": SITE + "/",
           "founder": {"@type": "Person", "name": "Ragul Sekar"},
           "address": {"@type": "PostalAddress", "addressLocality": "Chennai", "addressRegion": "Tamil Nadu", "addressCountry": "IN"}}
    kind = page.get("schema", c["schema"])
    desc = html.unescape(re.sub("<[^>]+>", "", page["meta"]))
    if kind == "SoftwareApplication":
        out.append({"@context": "https://schema.org", "@type": "SoftwareApplication", "name": page.get("schema_name", c["product"] + " " + page["crumb"]),
                    "applicationCategory": c["app_cat"], "operatingSystem": "Web, Android, iOS", "provider": org, "description": desc, "url": url})
    elif kind == "Service":
        svc = {"@context": "https://schema.org", "@type": "Service", "name": page.get("schema_name", page["crumb"]), "serviceType": page.get("service_type", page["crumb"]),
               "provider": org, "description": desc, "url": url}
        if page.get("area_served"):
            svc["areaServed"] = page["area_served"]
        out.append(svc)
    elif kind == "Article":
        out.append({"@context": "https://schema.org", "@type": "Article", "headline": html.unescape(re.sub("<[^>]+>", "", page["h1"])),
                    "description": desc, "url": url, "mainEntityOfPage": url, "image": OG,
                    "author": {"@type": "Person", "name": "Ragul Sekar", "url": "https://www.linkedin.com/in/ragul-sekar"},
                    "publisher": {"@type": "Organization", "name": "Elevate Aura", "url": SITE + "/", "logo": {"@type": "ImageObject", "url": SITE + "/assets/img/logo.png"}},
                    "datePublished": page.get("date", "2026-09-20"), "dateModified": page.get("modified", page.get("date", "2026-09-20"))})
    for b in page["sections"]:
        if b["type"] == "faq":
            out.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": html.unescape(re.sub("<[^>]+>", "", x["q"])),
                 "acceptedAnswer": {"@type": "Answer", "text": html.unescape(re.sub("<[^>]+>", "", x["a"]))}} for x in b["items"]]})
    return "\n".join('<script type="application/ld+json">\n%s\n</script>' % json.dumps(o, ensure_ascii=False) for o in out)


def render(page):
    c = CLUSTERS[page["cluster"]]
    url = SITE + url_of(page["cluster"], page["slug"])
    contact = page.get("cta_href", c["contact"])
    wa = wa_link(page.get("whatsapp_text", "Hi, I'd like to know more about %s." % html.unescape(c["product"])))
    body = []
    tone = "paper"
    for b in page["sections"]:
        body.append(render_block(b, page, c, tone))
        tone = "soft" if tone == "paper" else "paper"
    hero_img = ""
    if page.get("hero_image"):
        hi = page["hero_image"]
        hero_img = '<div><div class="shot"><div class="shot-bar"><i></i><i></i><i></i><span>%s</span></div><img src="%s" alt="%s" width="1680" height="945"></div></div>' % (esc(hi.get("bar", "elevateaura.co.in")), hi["src"], esc(hi["alt"]))
    grid_cls = "hero-grid" if hero_img else ""
    meta_ticks = "".join('<span>%s%s</span>' % (TICK.replace('stroke-width="2.4"', 'stroke-width="2.5"'), inline(t)) for t in page.get("meta_ticks", ["Founder-led delivery", "Live in 30 days where scope allows", "Support from the person who built it"]))
    demo_btn = ""
    if page.get("demo_href", c["demo"]):
        d = page.get("demo_href", c["demo"])
        ext = ' target="_blank" rel="noopener"' if d.startswith("http") else ""
        demo_btn = '<a class="btn btn-o" href="%s"%s>%s</a>' % (d, ext, inline(page.get("demo_label", "See the live demo")))
    byline = ""
    if page.get("schema", c["schema"]) == "Article":
        byline = '<p class="byline">By Ragul Sekar, founder of Elevate Aura &middot; Updated %s</p>' % page.get("modified", page.get("date", "2026-09-20"))
    crumb_last = '<li><span aria-current="page">%s</span></li>' % esc(page["crumb"]) if page["slug"] != "index" else ""
    hub_crumb = '<li><a href="%s">%s</a></li>' % (c["hub"], c["hub_name"]) if page["slug"] != "index" else '<li><span aria-current="page">%s</span></li>' % c["hub_name"]
    foot_links = "".join('<a href="%s">%s</a>' % (h, l) for h, l in c["foot_links"])
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="{c['theme']}">
<title>{esc(page['title'])}</title>
<meta name="description" content="{esc(page['meta'])}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{'article' if page.get('schema', c['schema']) == 'Article' else 'website'}">
<meta property="og:site_name" content="{c['site_name']}">
<meta property="og:title" content="{esc(page.get('og_title', page['title']))}">
<meta property="og:description" content="{esc(page.get('og_desc', page['meta']))}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{OG}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(page.get('og_title', page['title']))}">
<meta name="twitter:description" content="{esc(page.get('og_desc', page['meta']))}">
<meta name="twitter:image" content="{OG}">
<link rel="stylesheet" href="{c['css']}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/assets/img/logo.png" type="image/png">
<style>{EXTRA_CSS}</style>
{schema_json(page, c, url)}
<script defer src="/assets/js/ea-track.js"></script>
</head>
<body>

<div class="strip"><div class="wrap">
  <span><a href="/">&larr; Elevate Aura</a> &nbsp;&middot;&nbsp; {c['strip']}</span>
  <span>Chennai, India &middot; <a href="{wa}" target="_blank" rel="noopener">WhatsApp</a></span>
</div></div>

<nav class="crumb" aria-label="Breadcrumb"><ol>
  <li><a href="/">Home</a></li>
  {hub_crumb}
  {crumb_last}
</ol></nav>

<header class="hero">
  <div class="wrap {grid_cls}">
    <div>
      <span class="pill"><span class="d"></span>{inline(page.get('pill', c['hub_name']))}</span>
      <h1>{inline(page['h1'])}</h1>
      <p class="sub">{inline(page['sub'])}</p>
      <div class="hero-btns">
        <a class="btn btn-p" href="{contact}">{inline(page.get('cta_label', c['cta']))}{ARROW}</a>
        {demo_btn}
        <a class="btn btn-o" href="{wa}" target="_blank" rel="noopener">WhatsApp us</a>
      </div>
      <div class="hero-meta">{meta_ticks}</div>
      {byline}
    </div>
    {hero_img}
  </div>
</header>

{''.join(body)}
<section class="sec {tone}">
  <div class="wrap">
    <div class="cta rv">
      <h2>{inline(page.get('cta_h2', CTA_DEFAULTS.get(page['cluster'], ("Let's talk about your requirement.", ''))[0]))}</h2>
      <p>{inline(page.get('cta_p', CTA_DEFAULTS.get(page['cluster'], ('', 'Tell us how you work today. We will show you what the platform would look like for you, and give you a clear scope and timeline.'))[1]))}</p>
      <div class="cta-btns">
        <a class="btn btn-p" href="{contact}">{inline(page.get('cta_label', c['cta']))}</a>
        <a class="btn btn-w" href="{wa}" target="_blank" rel="noopener">WhatsApp us</a>
      </div>
      <p class="fine">Founder-led &middot; Chennai, India &middot; Built and supported by the person who wrote it</p>
    </div>
  </div>
</section>

<footer class="foot">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <h4>{c['site_name']}</h4>
        <p class="b">{c['foot_desc']}</p>
        <a href="https://wa.me/{WA}" target="_blank" rel="noopener">WhatsApp +91 95789 71156</a>
        <a href="mailto:{EMAIL}">{EMAIL}</a>
      </div>
      <div>
        <h4>{c['hub_name']}</h4>
        <a href="{c['hub']}">{c['hub_name']} home</a>
        {foot_links}
      </div>
      <div>
        <h4>Elevate Aura</h4>
        <a href="/">Home</a>
        <a href="/aura-business.html">Aura Business</a>
        <a href="/hims.html">HIMS</a>
        <a href="/aurapacs.html">AuraPACS</a>
        <a href="/aura-learn.html">Aura Learn</a>
        <a href="/product-development.html">Product Development</a>
        <a href="/case-studies/">Case Studies</a>
        <a href="/resources/">Guides</a>
        <a href="/compare/">Comparisons</a>
        <a href="/pages/about.html">About</a>
        <a href="/pages/contact.html">Contact</a>
      </div>
    </div>
    <div class="foot-bot">
      <span>&copy; 2026 Elevate Aura &middot; Chennai, India</span>
      <span>Founder-led delivery &middot; Ragul Sekar</span>
    </div>
  </div>
</footer>

<script>
(function(){{var all=document.querySelectorAll('.rv');function show(el){{el.classList.add('in');}}
if('IntersectionObserver'in window){{var o=new IntersectionObserver(function(es){{es.forEach(function(e){{if(e.isIntersecting){{show(e.target);o.unobserve(e.target);}}}});}},{{threshold:.12,rootMargin:'0px 0px -40px 0px'}});all.forEach(function(el){{o.observe(el);}});
/* Safety net: never leave content invisible if the observer misses an element during a fast scroll. */
setTimeout(function(){{all.forEach(function(el){{var r=el.getBoundingClientRect();if(r.top<window.innerHeight+200){{show(el);}}}});}},1500);
window.addEventListener('load',function(){{setTimeout(function(){{all.forEach(function(el){{var r=el.getBoundingClientRect();if(r.bottom<0||r.top<window.innerHeight){{show(el);}}}});}},300);}});}}
else{{all.forEach(show);}}}})();
</script>
</body>
</html>
"""
    return doc


def load_pages(only=None):
    pages = []
    for f in sorted(glob.glob(os.path.join(CONTENT, "*.json"))):
        if only and not os.path.basename(f).startswith(only + "__"):
            continue
        with open(f, encoding="utf-8") as fh:
            try:
                p = json.load(fh)
            except json.JSONDecodeError as e:
                raise SystemExit("Invalid JSON in %s: %s" % (f, e))
        p["_file"] = os.path.basename(f)
        pages.append(p)
    return pages


def validate(pages):
    errs = []
    seen_url, seen_title, seen_h1 = {}, {}, {}
    for p in pages:
        f = p["_file"]
        for k in ("cluster", "slug", "title", "meta", "h1", "sub", "crumb", "sections", "primary_keyword", "intent"):
            if k not in p:
                errs.append("%s: missing %s" % (f, k))
        if p.get("cluster") not in CLUSTERS:
            errs.append("%s: unknown cluster %s" % (f, p.get("cluster")))
            continue
        u = url_of(p["cluster"], p["slug"])
        if u in seen_url:
            errs.append("%s: duplicate url %s (%s)" % (f, u, seen_url[u]))
        seen_url[u] = f
        t = p.get("title", "")
        if t in seen_title:
            errs.append("%s: duplicate title with %s" % (f, seen_title[t]))
        seen_title[t] = f
        h = re.sub("<[^>]+>", "", p.get("h1", ""))
        if h in seen_h1:
            errs.append("%s: duplicate h1 with %s" % (f, seen_h1[h]))
        seen_h1[h] = f
        if len(t) > 70:
            errs.append("%s: title too long (%d)" % (f, len(t)))
        if not 80 <= len(p.get("meta", "")) <= 165:
            errs.append("%s: meta length %d (want 80-165)" % (f, len(p.get("meta", ""))))
        types = [b["type"] for b in p.get("sections", [])]
        if p["slug"] != "index" and "faq" not in types:
            errs.append("%s: no faq block" % f)
        if p["slug"] != "index" and "answer" not in types and "prose" not in types:
            errs.append("%s: no answer/prose block (needs a direct search-intent answer)" % f)
        words = len(re.sub("<[^>]+>", " ", json.dumps(p["sections"], ensure_ascii=False)).split())
        if p["slug"] != "index" and words < 450:
            errs.append("%s: thin content, ~%d words in sections" % (f, words))
        banned = re.compile(r"\b(HIPAA[- ]compliant|ISO ?\d{4,5}|FDA[- ](approved|cleared)|CE[- ]marked|NABH[- ]certified|trusted by \d|\d{2,}\+? (hospitals|clients|customers)|\d+% (faster|increase|reduction|growth))\b", re.I)
        m = banned.search(json.dumps(p, ensure_ascii=False))
        if m:
            errs.append("%s: banned claim '%s'" % (f, m.group(0)))
    return errs


def main():
    check = "--check" in sys.argv
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]
    pages = load_pages(only)
    if not pages:
        raise SystemExit("no content files found")
    errs = validate(pages)
    if errs:
        print("\n".join(errs))
        if check or len(errs) > 0:
            sys.exit(1)
    rows = []
    for p in pages:
        u = url_of(p["cluster"], p["slug"])
        out_dir = os.path.join(ROOT, u.strip("/"))
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(render(p))
        rows.append({"url": SITE + u, "cluster": p["cluster"], "slug": p["slug"], "title": p["title"], "h1": re.sub("<[^>]+>", "", p["h1"]),
                     "meta": p["meta"], "primary_keyword": p["primary_keyword"], "secondary_keywords": "; ".join(p.get("secondary_keywords", [])),
                     "intent": p["intent"], "persona": p.get("persona", ""), "country": p.get("country", "IN"), "city": p.get("city", ""),
                     "page_type": p.get("page_type", ""), "phase": p.get("phase", ""), "schema": p.get("schema", CLUSTERS[p["cluster"]]["schema"]) + ("+FAQPage" if any(b["type"] == "faq" for b in p["sections"]) else ""),
                     "parent": SITE + CLUSTERS[p["cluster"]]["hub"], "status": "PUBLISHED", "source": p["_file"]})
    if only:
        print("built %d pages (subset, manifest not written)" % len(rows)); return
    with open(os.path.join(os.path.dirname(__file__), "pages.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("built %d pages" % len(rows))


if __name__ == "__main__":
    main()
