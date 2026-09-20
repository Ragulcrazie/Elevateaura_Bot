# Deliverable 11: Metadata framework

## Title patterns

| Page type | Pattern | Example |
|---|---|---|
| Product hub | `{Product} \| {what it is} by Elevate Aura` | AuraPACS \| Medical image storage, viewing & WhatsApp report sharing by Elevate Aura |
| Feature page | `{Primary keyword} for {buyer} \| {Product}` | Preventive Maintenance Software for Medical Equipment \| Aura Business |
| Application / modality | `{Primary keyword} \| {differentiator} \| {Product}` | PACS for CT Scan Centres \| Worklist to Report \| AuraPACS |
| Industry / persona | `{Primary keyword} \| {outcome} \| {Product}` | Hospital Sales CRM \| From Purchase Committee to AMC \| Aura Business |
| City | `{Primary keyword} in {City} \| {delivery truth} \| {Product}` | PACS Software in Coimbatore \| On-Site Setup from Chennai \| AuraPACS |
| Country | `{Primary keyword} {Country} \| {deployment truth} \| {Product}` | PACS Software UAE \| Hybrid PACS, Remote Deployment \| AuraPACS |
| Guide | `What Is {Term}? {Plain-language descriptor}` | What Is PACS? Picture Archiving and Communication System Explained |
| Comparison | `{A} vs {B}: {who each is for}` | Cloud PACS vs On-Premise PACS: Which Fits Your Centre |
| Case study | `{Client}: {what was built} \| Case Study \| Elevate Aura` | Carna Medicare: 12-Module Distributor Platform \| Case Study |
| Service hub | `{Service} for {vertical} \| Elevate Aura` | Healthcare Mobile App Development \| Elevate Aura |

Rules: 50-70 characters; primary keyword in the first 40; brand or product last; no keyword
repeated twice; no ALL CAPS; ampersand written as `&amp;` in HTML. The build fails above 70.

## Meta descriptions

120-160 characters, plain text, one sentence or two. Structure: what it does for whom, then the
reason to click (the one thing the page offers that a directory listing does not). Contains the
primary keyword once. No "Learn more", no "Click here", no exclamation marks. The build fails
outside 80-165.

## H1

One per page, 8-16 words, primary keyword or its natural equivalent, one highlighted phrase in
`<span class="hl">` for the visual rhythm the existing pages use. H1 and title must differ.

## Heading hierarchy

`H1 → H2 (section heads, secondary keywords) → H3 (items inside pains, capability groups,
FAQ questions, prose sub-heads)`. No H4 outside the flow-step cards the design already uses.
FAQ questions are `summary` elements, not headings, matching the existing pages.

## Open Graph and Twitter

`og:type` website (article for guides, comparisons, case studies), `og:site_name` the product
or "Elevate Aura", `og:title` and `og:description` from title and meta unless `og_title` /
`og_desc` overrides are set, `og:image` the shared 1200x630 image, `twitter:card`
summary_large_image. A per-product OG image is a Phase 2 nicety.

## Canonical, robots, indexing

- Self-referencing canonical on every indexable page, absolute URL, trailing slash for folder
  pages, `.html` for the legacy root pages.
- No `robots` meta on indexable pages. `noindex` on 404, admin, portals, backups and drafts.
- Forward stubs carry the destination's canonical.
- Sitemaps list only indexable, canonical URLs.

## Images

- `alt` describes what is shown (screen, module, data visible), includes the product noun
  once, never stuffed with keywords. Decorative SVG icons have no alt.
- `width` and `height` attributes on every screenshot to prevent layout shift; lazy loading
  below the fold; hero image eager.
- File names: existing screenshot names are kept (renaming would break 60 pages); new
  screenshots should be `product-module-view.png`.

## Breadcrumbs

Visible `nav.crumb` and BreadcrumbList schema on every page: Home → Hub → Page, with names that
match the page's `crumb` field (2-5 words, not the full title).

## Language and locale

`<html lang="en">`, `inLanguage: en` on WebSite schema, British/Indian spelling in copy.
