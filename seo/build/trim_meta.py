#!/usr/bin/env python3
"""Shorten over-length titles and meta descriptions on the hand-built pages.

Search results truncate titles past roughly 60-65 characters and descriptions past
roughly 160, so the tail of every long one was invisible. Titles here follow the
"Keyword | Claim | Product" pattern, so the middle segment is dropped first, keeping the
keyword and the brand. Descriptions are cut at the last sentence or clause boundary that
fits, so the sentence still reads as written.

Idempotent: run from the repo root as often as you like.
"""
import glob
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TITLE_MAX = 65
META_MAX = 160


# Hub titles that cannot be shortened safely by rule: the keyword phrase itself is long, so
# they are rewritten by hand, keyword first, brand last, inside 65 characters.
HAND_TITLES = {
    "aura-business.html": "Aura Business | Distributor, Field Service &amp; AMC Software",
    "aurapacs.html": "AuraPACS | PACS, DICOM Viewer &amp; WhatsApp Report Sharing",
    "aura-learn.html": "Aura Learn | LMS, Training &amp; Exam Prep Platform",
    "product-development.html": "Product Development | Embedded &amp; Device Software",
    "modules.html": "87 Modules for Medical-Equipment Distribution | Aura Business",
    "how-it-works.html": "How Aura Business Works | Setup to Go-Live in 30 Days",
}


def generated_pages():
    out = set()
    for j in glob.glob(os.path.join(os.path.dirname(__file__), "content", "*.json")):
        c, s = os.path.basename(j)[:-5].split("__", 1)
        out.add("%s/index.html" % c if s == "index" else "%s/%s/index.html" % (c, s))
    return out


def shorten_title(t):
    if len(t) <= TITLE_MAX:
        return t
    parts = [p.strip() for p in t.split("|")]
    while len(parts) > 2 and len(" | ".join(parts)) > TITLE_MAX:
        parts.pop(len(parts) - 2)          # drop the middle claim, keep keyword and brand
    cand = " | ".join(parts)
    if 30 <= len(cand) <= TITLE_MAX:
        return cand
    if len(parts) == 2 and 30 <= len(parts[0]) <= TITLE_MAX:
        return parts[0]                     # keyword alone beats a cut brand name
    return t   # nothing safe to drop: a long title beats a damaged one


DANGLING = {"with", "and", "or", "for", "plus", "including", "from", "in", "on", "to", "the", "a", "an", "by", "of"}


def shorten_meta(m, limit=META_MAX):
    if len(m) <= limit:
        return m
    acc = ""
    for s in re.split(r"(?<=\.)\s+", m.strip()):
        cand = (acc + " " + s).strip()
        if len(cand) <= limit:
            acc = cand
        else:
            break
    if len(acc) >= 100:
        return _guard(acc, m)
    body = m.rstrip()
    best = None
    for mt in re.finditer(r"[,;]\s", body):
        if mt.start() <= limit - 1:
            best = mt.start()
    if best and best >= 100:
        return _guard(_tidy(body[:best]), m)
    return _guard(_tidy(body[:limit - 1].rsplit(" ", 1)[0]), m)


def _guard(cut, original):
    """A cut that ends on a one or two word fragment reads worse than a long description."""
    tail = re.split(r"[,:;]", cut.rstrip(".").strip())[-1].strip()
    return original if len(tail.split()) < 3 else cut


def _tidy(t):
    t = t.rstrip(" ,;:")
    words = t.split()
    while words and words[-1].lower().strip(",;:") in DANGLING:
        words.pop()
    return " ".join(words).rstrip(" ,;:") + "."


def main():
    os.chdir(ROOT)
    skip = generated_pages() | {"index_backup_20260630.html", "index-v2.html", "index_redirect.html", "welcome.html"}
    files = sorted(set(f.replace("\\", "/") for f in
                       glob.glob("*.html") + glob.glob("pages/*.html") + glob.glob("*/index.html") + glob.glob("*/*/index.html")))
    changed = 0
    for f in files:
        if f in skip:
            continue
        s0 = open(f, encoding="utf-8", errors="ignore").read()
        s = s0
        mt = re.search(r"<title>(.*?)</title>", s, re.S)
        if mt and f in HAND_TITLES:
            s = s.replace("<title>%s</title>" % mt.group(1), "<title>%s</title>" % HAND_TITLES[f], 1)
        elif mt and len(mt.group(1)) > TITLE_MAX:
            s = s.replace("<title>%s</title>" % mt.group(1), "<title>%s</title>" % shorten_title(mt.group(1)), 1)
        md = re.search(r'<meta name="description" content="(.*?)"', s, re.S)
        if md and len(md.group(1)) > META_MAX + 5:
            s = s.replace('<meta name="description" content="%s"' % md.group(1),
                          '<meta name="description" content="%s"' % shorten_meta(md.group(1)), 1)
        if s != s0:
            with open(f, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(s)
            changed += 1
            if "--verbose" in sys.argv:
                nt = re.search(r"<title>(.*?)</title>", s, re.S)
                nd = re.search(r'<meta name="description" content="(.*?)"', s, re.S)
                print("%s\n  T %d %s\n  M %d %s" % (f, len(nt.group(1)), nt.group(1), len(nd.group(1)), nd.group(1)))
    print("shortened %d files" % changed)


if __name__ == "__main__":
    main()
