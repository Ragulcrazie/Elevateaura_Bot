# Elevate Aura SEO system

Everything that turns elevateaura.co.in into an interconnected set of product, research and
proof pages lives here. The site stays static HTML on GitHub Pages; new pages are generated
from JSON content files so quality rules are enforced at build time.

## Deliverables

| # | File | What it is |
|---|---|---|
| 1 | `01-site-audit.md` | Audit of the live site and repository: what was good, what was broken, what was fixed |
| 2 | `02-url-inventory.csv` | Every public URL with title, H1, meta, canonical, robots, schema, links and the KEEP / IMPROVE / MERGE / REDIRECT / NOINDEX action |
| 3 | `03-master-page-database.csv` | The opportunity matrix: every legitimate query per product with intent, persona, URL, phase and PUBLISHED / PLANNED / REJECTED status |
| 4 | `04-keyword-database.csv` | Keyword view of the same data |
| 5 | `05-international-country-strategy.md` | Which products travel, which markets, what every country page must say |
| 6 | `06-city-region-strategy.md` | Which cities get pages and why, and which do not |
| 7 | `07-search-intent-map.md` | Counts by product and intent, and how intent maps to page type and CTA |
| 8 | `08-url-architecture.md` | Folder and slug rules, every page built, what was deliberately not built |
| 9 | `09-internal-linking-architecture.md` | The link graph and the rules the generator enforces |
| 10 | `10-content-templates.md` | Block sequences and requirements per page type |
| 11 | `11-metadata-framework.md` | Title, meta, heading, OG, canonical and image rules |
| 12 | `12-schema-implementation-plan.md` | Structured data by page type and what is deliberately not used |
| 13 | `13-technical-seo-plan.md` | Crawl, index, performance, monitoring and deployment safety |
| 14 | `14-conversion-tracking-plan.md` | GA4 events, key events, reports |
| 15 | `15-lead-generation-funnel.md` | Search to customer, stage by stage |
| 16 | `16-content-publishing-roadmap.md` | Phases, what shipped, what is next, how to prioritise |
| 17 | `17-competitor-gap-analysis.md` | Who ranks for the twelve head queries and the gaps taken |
| 18 | `18-seo-dashboard-spec.md` | Looker Studio dashboard on Search Console, GA4 and the CRM |
| 19 | `19-page-implementation-index.md` plus `build/content/*.json` and the generated `/<hub>/<slug>/index.html` pages | Page-by-page implementation |
| 20 | `20-seo-qa-report.md` | Output of the QA script over the whole site |

## Build

Run in this order from the repo root. Every step is idempotent, so a re-run is safe.

```bash
python seo/build/build_pages.py        # JSON content -> HTML pages + build/pages.csv
python seo/build/patch_existing.py     # tracking, schema fixes and links on hand-built pages
python seo/build/trim_meta.py          # shorten titles and descriptions that SERPs would cut
python seo/build/hand_metas.py         # seven descriptions that needed a human rewrite
python seo/build/build_sitemaps.py     # sitemap.xml index + five segments
python seo/build/inventory.py          # 02-url-inventory.csv
python seo/build/build_master_db.py    # 03, 04, 07
python seo/build/build_index_doc.py    # 19
python seo/build/qa.py                 # 20, exits non-zero on any failure
```

`build/FACTS.md` is the claims boundary: nothing may be published that it does not support.
`build/CONTENT_SCHEMA.md` is the content format. The build refuses thin pages, duplicate
titles or H1s, missing FAQs, over-length metadata and a list of banned claim patterns, so
quality rules are enforced by the tooling rather than by review.

The Telegram bot, Python services and database folders that share this repository were not
touched by any of it.
