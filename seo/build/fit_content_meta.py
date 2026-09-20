#!/usr/bin/env python3
"""Bring over-length titles and descriptions in the content JSON inside the build's limits.

Writers routinely land a few characters over. Rather than bounce the file back, this trims at
the last sentence or clause boundary that fits and refuses any cut that would end on a
one or two word fragment, reusing the same guarded logic as trim_meta.py. Titles are shortened
by dropping the middle "| claim |" segment, never by cutting mid-phrase.

Run from the repo root: python seo/build/fit_content_meta.py [--dry-run]
"""
import glob
import importlib.util
import io
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
META_MAX = 163          # build allows 165; leave a little headroom
TITLE_MAX = 65


def load_trimmer():
    spec = importlib.util.spec_from_file_location("tm", os.path.join(os.path.dirname(__file__), "trim_meta.py"))
    tm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tm)
    return tm


def main():
    os.chdir(ROOT)
    tm = load_trimmer()
    dry = "--dry-run" in sys.argv
    changed = 0
    for f in sorted(glob.glob("seo/build/content/*.json")):
        d = json.load(io.open(f, encoding="utf-8"))
        before = (d.get("title", ""), d.get("meta", ""))
        if len(d.get("title", "")) > TITLE_MAX:
            t = tm.shorten_title(d["title"])
            if len(t) <= TITLE_MAX:
                d["title"] = t
        if len(d.get("meta", "")) > META_MAX:
            m = tm.shorten_meta(d["meta"], META_MAX)
            if len(m) <= META_MAX:
                d["meta"] = m
        if (d.get("title"), d.get("meta")) != before:
            changed += 1
            print("%-56s T%-3d M%-3d" % (os.path.basename(f)[:-5][:56], len(d["title"]), len(d["meta"])))
            if not dry:
                json.dump(d, io.open(f, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
    print("%s %d file(s)" % ("would change" if dry else "fitted", changed))


if __name__ == "__main__":
    main()
