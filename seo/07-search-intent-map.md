# Deliverable 7: Search-intent map

Derived from `03-master-page-database.csv` (615 opportunities). PUBLISHED = a live page targets the query; PLANNED = legitimate intent queued by phase; REJECTED = real query, but a page would be thin, unsupported by the product, or a doorway.

| Product | Total | Published | Planned | Rejected | Commercial | Transactional | Informational | Comparison | Local |
|---|---|---|---|---|---|---|---|---|---|
| aura-business | 146 | 72 | 69 | 5 | 104 | 5 | 20 | 7 | 10 |
| hims | 116 | 57 | 44 | 15 | 84 | 3 | 15 | 4 | 10 |
| aurapacs | 109 | 67 | 33 | 9 | 74 | 5 | 17 | 6 | 7 |
| aura-learn | 74 | 32 | 33 | 9 | 54 | 3 | 11 | 4 | 2 |
| product-development | 82 | 35 | 37 | 10 | 61 | 2 | 12 | 5 | 2 |
| mobile-app-development | 34 | 17 | 15 | 2 | 26 | 2 | 2 | 2 | 2 |
| web-development | 27 | 13 | 13 | 1 | 21 | 1 | 2 | 2 | 1 |
| seo-services | 27 | 12 | 14 | 1 | 19 | 2 | 3 | 2 | 1 |

## How intent maps to page type and CTA

| Intent | Page types | Where the query is answered | CTA |
|---|---|---|---|
| informational | guide, problem | `/resources/` guides; problem queries resolve to the guide or the feature page whose answer block addresses them | soft link to product, WhatsApp in the strip |
| comparison | comparison | `/compare/` pages with fair tables | link to both product pages, then contact |
| commercial | product, feature, application, industry, persona, country | product cluster pages with answer block, workflow, modules, use cases, comparison, FAQ | Book a strategy call, live demo, WhatsApp with topic prefill |
| transactional | commercial | contact, pricing (module picker), demo pages, AuraPACS download | WhatsApp, phone, email, download |
| local | city | city pages with local context and honest delivery statement | Book a call, WhatsApp |

## Rules applied

1. One URL per intent. Close variants (`AMC management software`, `AMC renewal software`) are served by one page and listed as SAME in the database, to be added to that page's H2s and FAQs rather than split into near-duplicates.
2. Rejections are recorded with the reason so the decision is not re-litigated: unsupported product claims, safety-critical positioning, doorway risk, or a listicle that would name competitors.
3. Pricing-intent queries are parked until the owner publishes a price list; the hub already states one Aura Business tier.
4. Specialty HIMS queries are rejected until specialty modules exist; a renamed generic page would be a doorway.
5. Planned pages open in phase order and only after Search Console shows impressions for the cluster; see `16-content-publishing-roadmap.md`.
