# Deliverable 1: Website SEO audit (elevateaura.co.in, 20 September 2026)

Scope: every HTML file in the repository that deploys to elevateaura.co.in, plus live HTTP checks
against the production site. The Telegram bot, Python services and database folders in the
same repository were left untouched. Full per-URL data is in `02-url-inventory.csv`.

## How the site is built and served

- Static HTML on GitHub Pages with the custom domain in `CNAME`. No server, so no 301
  redirects, no header control, no server-side rendering. Every SEO control has to live in
  the HTML, `robots.txt` and the sitemaps.
- 100 public URLs before this work: 1 homepage, 5 product hubs, 1 Auracare hub, 60 product
  cluster pages (10 per hub), 11 Auracare pages, 10 root-level forward stubs, company pages
  in two places (`/about.html` for Aura Business and `/pages/about.html` for the company),
  and 7 internal or leftover pages.
- Each cluster has its own stylesheet (`biz.css`, `hims.css`, `pacs.css`, `learn.css`,
  `dev.css`, `care.css`) with the same class vocabulary, which is what made a shared page
  generator possible without touching the existing design.

## What was already good

- Every cluster page has a unique title, one H1, a meta description, a self-referencing
  canonical, BreadcrumbList, SoftwareApplication or Service schema and FAQPage schema.
- Titles and H1s are keyword-led and not duplicated across the 60 cluster pages.
- Content is specific to the product (job cards, e-way bills, worklists), not filler, and
  runs 1,700 to 2,600 words per page.
- Hubs link to all ten children; children link sideways to siblings in FAQs, related grids
  and footers. The site is already a set of clusters, not a flat list.
- Auracare has correct MedicalBusiness local schema with service areas.
- `robots.txt` existed and blocked the demo folder; a sitemap existed and was complete for the
  pages of 11 August 2026.

## Defects found and fixed in this pass

| # | Finding | Impact | Fix |
|---|---|---|---|
| 1 | `og:image` on every page pointed to `/images/og_image.png`, which returned 404 | Broken share previews on WhatsApp and LinkedIn, the site's two main referral channels | Generated a 1200x630 branded image at that path |
| 2 | No `404.html` | GitHub's default 404 with no navigation or tracking | Added a branded 404 with links to every hub, noindexed |
| 3 | Mobile menu on the homepage sent "HIMS" to `aurapacs.html` | Wrong destination for mobile users | Fixed |
| 4 | Two Offer blocks in schema had no visible counterpart: `price 0 INR` on the CRM page, and `6000 INR per month for 15 modules` on the Aura Business hub | Prices in structured data that the visitor cannot see anywhere, against Google's markup policy | Both removed |
| 5 | Homepage schema was `ProfessionalService` only, no `WebSite`, no `sameAs`, no telephone | Weak entity signal for "Elevate Aura" | Upgraded to Organization plus ProfessionalService with `@id`, `sameAs`, telephone and address; added WebSite |
| 6 | GA4 (`G-3XX97R8F1Y`) was loaded only on privacy, terms and a redirect stub | No traffic or conversion data on any page that matters | Added `assets/js/ea-track.js` to all 100 public pages: GA4 plus WhatsApp, phone, email, CTA, download and form events |
| 7 | `robots.txt` allowed admin, partner portal, backup homepage, old homepage draft and the web app | Crawl waste and thin pages eligible for indexing | Disallowed them; noindex confirmed on each |
| 8 | `/about.html` and `/contact.html` (Aura Business) competed with `/pages/about.html` and `/pages/contact.html` (company) on near-identical titles | Two "About" pages diluting each other | Retitled the Aura Business pair; the company pair stays the entity pages |
| 9 | One flat sitemap with a single lastmod for everything | No freshness signal, no segmentation for diagnosis | Sitemap index with core, products, services, locations and resources maps; lastmod from git |
| 10 | No case-study pages, no educational content, no comparisons | Nothing to earn links or answer research-stage queries; case studies existed only as three cards | New `/case-studies/`, `/resources/`, `/compare/` hubs |
| 11 | Three services described on the homepage (mobile apps, websites and e-commerce, SEO) had no pages | Zero search presence for services the studio sells | New `/mobile-app-development/`, `/web-development/`, `/seo-services/` hubs |
| 12 | Existing cluster pages did not link to anything outside their own cluster | New pages would have been orphans | "Further reading" block added before the closing CTA on every hand-built cluster page; hub footers extended |

## Defects noted, not fixed here (need an owner decision or product work)

- `/pages/privacy.html` and `/pages/terms.html` duplicate `/privacy.html` and `/terms.html`.
  Pick one copy and canonical the other (marked MERGE in the inventory).
- Forward stubs at the root (`/medical-equipment-crm.html` and nine others) use meta refresh
  because GitHub Pages cannot 301. They carry canonicals, which is the best available. If the
  site ever sits behind Cloudflare, convert them to real redirects.
- `pricing.html` computes a tier in JavaScript and renders no price text at all. The only price
  that existed anywhere on the site was the 6,000 INR figure inside the Aura Business hub's
  structured data, now removed because nothing visible backed it. The owner has decided not to
  publish prices at all, so price-intent search is served by pricing pages that explain the
  model and ask for a call instead of quoting a figure.
- The GitHub Actions workflow references a `blog/` folder that does not exist. It is bot-
  related and was not touched.
- Image weight: `hero_abstract_tech_*.png` (658 KB) and `process_visual_*.png` (519 KB) sit
  in the repo; the homepage uses the WebP versions, so no action beyond deleting the PNGs.
- Cluster pages load Google Fonts only on the homepage; cluster pages use system fonts, which
  is good for Core Web Vitals. No render-blocking third-party scripts were found. The tracking
  script is deferred.
- No hreflang: the site is English-only and hreflang is not needed until a second language
  or region-specific duplicate exists.

## Live checks (production, 20 September 2026)

| URL | Status |
|---|---|
| `/`, `/aura-business.html`, cluster pages | 200 |
| `/images/og_image.png` | 404 (fixed in this branch) |
| `/this-does-not-exist` | 404, GitHub default page (fixed in this branch) |
| `/admin.html`, `/index-v2.html` | 200 and crawlable (now disallowed) |
| `/sitemap.xml`, `/robots.txt` | 200 |

## Content and entity observations

- The site tells one consistent story: founder-led, Chennai, 30 days, unlimited users,
  three real projects, one builder. That consistency is an asset for entity SEO and has been
  carried into every new page and the Organization schema.
- The weakest area was intent coverage: ten pages per product covers the head terms but
  none of the feature-level, problem-level, comparison or research queries that precede a
  demo request. That is what the new pages address.
- Claims discipline is good: no fake testimonials, ratings or certifications were found.
  The one fabricated data point was the schema price, now removed. `FACTS.md` records what
  may be claimed so the discipline survives future pages.
