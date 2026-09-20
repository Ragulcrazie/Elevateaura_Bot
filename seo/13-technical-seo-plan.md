# Deliverable 13: Technical SEO implementation plan

Constraint: GitHub Pages. No server config, no redirects, no headers, no edge rules. Everything
below is achievable in the repository, and the items marked DONE are in this branch.

## Crawl and index control

| Item | Status | Detail |
|---|---|---|
| robots.txt | DONE | Allows all, disallows `/demo/`, `/web_app/`, admin and portal pages, backups, drafts, bot and data folders; points to the sitemap index |
| noindex on non-public pages | DONE | 404, admin, partner portal and admin, welcome, old homepage draft, backup, redirect stub |
| Sitemap index and segments | DONE | `sitemap.xml` → core, products, services, locations, resources; lastmod from git; noindex pages excluded; rebuild with `python seo/build/build_sitemaps.py` |
| Canonicals | DONE | Self-referencing on every generated page; forward stubs canonical to destination |
| 404 page | DONE | Branded, noindex, links to hubs, tracking loaded so 404 hits are visible in GA4 |
| Duplicate company pages | OPEN | `/pages/privacy.html` and `/pages/terms.html` duplicate the root copies: pick one, canonical the other |
| Forward stubs | ACCEPTED | Meta refresh + canonical is the ceiling on GitHub Pages; convert to 301s if a CDN is ever added |
| Trailing slash consistency | DONE | Internal links to folder pages always end with `/`; GitHub serves `/x/` and `/x/index.html` identically, the canonical picks `/x/` |

## Rendering and performance

- Pages are static HTML with CSS in one file per cluster and one small inline style for new
  blocks. No client-side rendering, no framework. Googlebot sees the full content on first
  fetch.
- Only JavaScript: the reveal-on-scroll observer (already on the site) and the deferred
  tracking script. The reveal effect adds `.in` on intersection; content is in the DOM
  regardless, so nothing is hidden from crawlers.
- Screenshots carry `width`/`height` and lazy-load below the fold. The hero image is eager.
- Fonts: cluster pages use system fonts. The homepage loads Outfit from Google Fonts with
  preconnect; acceptable.
- Two large PNGs in the repo root (658 KB and 519 KB) are unused by the homepage (it uses
  WebP). Delete them in a cleanup commit.
- Core Web Vitals: with no third-party scripts beyond deferred GA4, LCP is the hero text or
  screenshot, CLS is controlled by image dimensions, INP has no heavy handlers. Verify in
  PageSpeed Insights after deploy for `/`, one hub, one cluster page, one guide.

## Mobile

- All templates are the existing responsive cluster layout (grid collapses at 900 px and
  560 px). The new table and prose blocks scroll horizontally inside `.tbl` on narrow screens
  rather than overflowing the page.
- Homepage mobile menu bug (HIMS → aurapacs) fixed.

## Structured data

See `12-schema-implementation-plan.md`. JSON-LD validity is checked at build time.

## Internal links and orphans

- QA script checks every internal `href` resolves to a file and every generated page has at
  least two inbound links. Hand-built cluster pages received a further-reading block; hub
  footers received guide and case-study links; the homepage footer lists the new hubs.

## Security and hygiene (affects trust and crawl)

- `.gitignore` now excludes the AuraPACS product source; the `aurapacs/` folder in the repo
  holds only public pages. Keep it that way.
- No mixed content: all assets are relative or same-origin; the only external calls are Google
  Fonts (homepage) and GA4.
- HTTPS enforced by GitHub Pages; keep "Enforce HTTPS" on in the repository settings.

## Monitoring set-up (owner tasks, one hour)

1. Google Search Console: verify `elevateaura.co.in` (DNS TXT), submit `sitemap.xml`. The
   segments make the Pages report readable by content type.
2. GA4 property `G-3XX97R8F1Y`: mark `whatsapp_click`, `phone_click`, `email_click`,
   `form_submit` and `cta_click` as key events (see `14-conversion-tracking-plan.md`).
3. Bing Webmaster Tools: import from Search Console, submit the same sitemap.
4. Monthly: Search Console Pages report for "Crawled, not indexed" on new URLs, Enhancements
   for FAQ and Breadcrumb errors, Core Web Vitals report.

## Deployment safety

- Build steps are idempotent: `build_pages.py` regenerates only generated pages;
  `patch_existing.py` skips files that already carry its markers; `build_sitemaps.py` rewrites
  the sitemaps from the file system.
- Nothing in the existing design or CSS was modified. New blocks use the existing class
  vocabulary plus a small scoped inline style.
- The Telegram bot and Python services in the repository were not touched.
