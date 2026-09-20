# Deliverable 10: Content templates

All templates are implemented as block sequences in `seo/build/CONTENT_SCHEMA.md` and rendered
by `seo/build/build_pages.py`. This document says which blocks each page type uses and what
each block must contain. Word counts are for section content, excluding hero, footer and FAQ
schema.

## A. Commercial feature page (product cluster) — 650 to 950 words

| Order | Block | Must contain |
|---|---|---|
| Hero | title, meta, H1 with one highlighted phrase, pill, sub, 3 trust ticks, primary CTA, demo button, WhatsApp | The primary keyword in title, H1 and sub; the buyer named in the pill |
| 1 | `answer` | Two or three paragraphs that answer the query directly in the first 80 words, name the module and where it sits in the platform |
| 2 | `pains` | 4-6 concrete failure modes written in the buyer's vocabulary |
| 3 | `flow` | 4-7 steps of the actual workflow from trigger to outcome |
| 4 | `caps` | Module list grouped 3-4 ways, with a "see all modules" link |
| 5 | `usecases` | 3-4 workflow-and-result pairs, no numbers |
| 6 | `who` | 5-6 buyer types |
| 7 | `compare` | Category comparison, last column is the product; no brand names |
| 8 | `cases` | Only the real projects relevant to the page |
| 9 | `faq` | 6 questions phrased as buyers ask them; 30-70 word answers; internal links in answers |
| 10 | `related` | 5-6 links per the linking rules |
| Close | CTA block | Restates the outcome, two buttons |

## B. Application or modality page (e.g. PACS for CT centres) — 650 to 900 words

`answer, pains, flow or table (what is different about this modality/application), caps,
usecases, who, compare, faq, related`. The `table` block carries the genuinely different facts
(study size, series count, reading behaviour), which is what keeps modality pages from being
the same page with a different noun.

## C. Industry or persona page — 650 to 900 words

`answer, pains, flow, caps, usecases, who (sub-segments), compare, faq, related`. The pains and
use cases must be that industry's, not the product's generic ones.

## D. City page — 600 to 850 words

`answer, prose (local context: industry cluster, buyer profile, delivery reality), caps (the
modules that matter for that profile), usecases (written for that profile), faq (travel,
training, support, billing), related`. Delivery honesty is mandatory: remote setup and WhatsApp
support everywhere; in-person only where true.

## E. Country page — 650 to 900 words

`answer, prose (market context, deployment, support, regulation-confirm-locally, currency),
caps, usecases, faq (internet outages, data location, who installs, support hours), related`.
`area_served` set in schema. No local office, partner, customer or regulation compliance claim.

## F. Guide (`/resources/`) — 800 to 1,100 words

`answer (definition in the first 80 words), prose x3-4 (how it works, terms confused with it,
deployment or types, what to check when buying), optional table, faq (6), related`. Byline and
Article schema with dates. Links to the commercial page once in the text and once in related.

## G. Comparison (`/compare/`) — 700 to 1,000 words

`answer (who each option is for), prose (how each works), compare or table (criteria: what it
covers, deployment, cost model without numbers, who runs it, when it wins, when it loses),
prose (how to decide), faq (6), related`. Must state when the other option is right. Use `table`
rather than `compare` when neither option is the product, so no column reads as an endorsement.

## H. Case study (`/case-studies/`) — 700 to 1,000 words

`answer (what, for whom), prose (situation), prose (what was built: modules, stack), prose (how
the work ran), prose (what it changed, qualitative), table (module vs what it replaced), faq (5),
related (the feature pages that were built)`. No numbers, quotes or client staff names that are
not on the record.

## I. Hub page — 400+ words

`answer, hubgrid (every child with a one-line description), why or cases, faq (optional),
related (other hubs)`.

## Metadata inside every template

- Title 50-70 characters, primary keyword first, product or brand last.
- Meta description 120-160 characters, keyword plus a reason to click, plain text.
- One H1. H2s carry secondary keywords naturally. H3s only inside prose blocks.
- Image `alt` describes what the screenshot shows, includes the product noun once.
- Canonical self-referencing. `og:` and `twitter:` derived from title and meta.
- Schema: BreadcrumbList always; SoftwareApplication (products), Service (services and
  clusters delivered as a service), Article (guides, comparisons, case studies); FAQPage when a
  FAQ block exists. Never Offer, AggregateRating or Review.

## Writing rules (from CONTENT_SCHEMA.md, repeated because they matter)

- Answer first, no preamble. Specific workflow nouns over adjectives.
- Every claim traceable to `FACTS.md`. No prices, counts, percentages, certifications,
  testimonials, or customers other than the three on record.
- No em dashes, no exclamation marks, British/Indian English, real ₹ symbol.
- No sentence reused between pages. The build fails on duplicate titles, H1s or URLs, thin
  content (fewer than ~450 words), missing FAQ or answer block, and banned claim patterns.
