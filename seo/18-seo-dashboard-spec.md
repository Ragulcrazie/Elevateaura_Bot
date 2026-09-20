# Deliverable 18: SEO dashboard specification

One page, refreshed weekly, built in Looker Studio (free) on three sources: Google Search
Console, GA4 (`G-3XX97R8F1Y`) and a Google Sheet exported from the Aura Business CRM. The
purpose is to answer four questions in this order: are enquiries growing, which pages produce
them, which pages are gaining visibility, and what is broken.

## Section 1: Enquiries (top of the page)

| Tile | Source | Definition |
|---|---|---|
| Organic enquiries, last 28 days vs previous 28 | GA4 | Sum of key events (`whatsapp_click`, `phone_click`, `email_click`, `form_submit`, `file_download`) where session source is google/organic |
| Qualified enquiries, last 28 days | CRM sheet | Leads with source = website page and status ≥ demo booked |
| Revenue from organic leads, quarter to date | CRM sheet | Sum of closed-won value where source = website page |
| Enquiry rate | GA4 | Key events ÷ organic sessions × 100 |

## Section 2: Enquiries by page and cluster

- Table: `page_path`, `product_cluster`, organic sessions, cta_click, key events, enquiry rate.
  Sorted by key events. Filter chips for cluster.
- Bar: key events by `product_cluster`.
- Pie (small): enquiries by channel (WhatsApp / phone / email / form / download).

## Section 3: Visibility (Search Console)

- Time series: clicks and impressions, 16 weeks, with an annotation on deployment date.
- Table: landing page, clicks, impressions, CTR, average position, change vs previous period.
  Grouped by sitemap segment using a regex on the URL (`/resources/|/compare/|/case-studies/`
  = research, `-uae/|-saudi-arabia/|-nigeria/|-kenya/|-usa/|-uk/|-australia/` = country,
  `-bangalore/|-hyderabad/|-mumbai/|-coimbatore/|-madurai/|-chennai/` = city, else product).
- Table: queries with impressions > 50 and position 8-20 (striking-distance list) with the
  landing page. This is the monthly optimisation queue.
- Scorecard: pages with at least one click in 28 days ÷ pages in sitemaps (coverage of demand).

## Section 4: Research content assist

- Path exploration summary (GA4): sessions that landed on `/resources/` or `/compare/` and
  reached a product page or a key event in the same session.
- Table: guide URL, sessions, next page, key events assisted.

## Section 5: Country and city pages

- Table: page, country of user (GA4), impressions and clicks (Search Console by country),
  key events. One row per location page.

## Section 6: Health

| Check | Source | Alert when |
|---|---|---|
| Indexed pages vs sitemap URLs | Search Console Pages report | "Crawled, not indexed" > 10% of new URLs after 6 weeks |
| FAQ and Breadcrumb enhancement errors | Search Console Enhancements | any error |
| Core Web Vitals | Search Console CWV | any URL group "poor" |
| 404 hits | GA4 page_view where page_title = "Page not found" | > 20 in a week (broken inbound link) |
| Tracking alive | GA4 | zero `whatsapp_click` in 7 days across the site |

## Cadence

- Weekly (15 minutes): Section 1 and 6.
- Monthly (1 hour): Sections 2-5; pick five striking-distance queries and improve their pages
  (title, intro, FAQ, internal links); log the change with a date annotation.
- Quarterly: compare cluster performance, decide which Phase 5b/6b pages to build from the
  evidence, retire or merge pages with zero impressions after two quarters.

## Data plumbing

- Search Console connector: property `elevateaura.co.in`, URL-level and query-level tables.
- GA4 connector: events with custom dimensions `product_cluster`, `link_text`, `link_url`.
- CRM sheet: columns lead_id, date, source_url, cluster, status, value, closed_date. Exported
  weekly from Aura Business (the platform's Reports Engine can schedule it).
