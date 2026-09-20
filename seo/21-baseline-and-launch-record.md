# Deliverable 21: Launch record and the baseline to measure against

Deployed to `main` on 20 September 2026, commit "Build the SEO system". GitHub Pages published
it within a minute and the live site was verified: every new page returns 200, every existing
page still returns 200 and now carries the tracking script, and the branded 404 works.

## The baseline, taken from Search Console before anything shipped

Measure everything against these numbers. They cover the three months to 18 September 2026.

| Metric | Value |
|---|---|
| Clicks | 47 |
| Impressions | 1,020 |
| Average CTR | 4.6% |
| Average position | 25.1 |
| Pages indexed | 68 |
| Pages not indexed | 40 |

### Where those clicks came from

| Query | Clicks | Impressions | Position |
|---|---|---|---|
| elevate aura | 21 | 118 | 3.0 |
| hms software in chennai | 0 | 61 | 45.1 |
| iv injection at home | 0 | 17 | 74.2 |
| wound dressing at home | 0 | 15 | 56.5 |
| aura business | 0 | 14 | 22.9 |
| auralearn | 0 | 12 | 4.3 |
| aura elevate | 0 | 11 | 8.9 |
| cloud pacs | 0 | 9 | 67.7 |
| aura learning | 0 | 7 | 10.4 |

Read plainly: 21 of the 47 clicks are people typing the brand name. Every commercial query is
far below the first page, so the site is shown to buyers and never clicked. There are no
striking-distance queries at all, which is why the work went into surface area and internal
linking rather than tweaking a handful of near-miss pages.

## What the indexing report showed

- 68 indexed, 40 not.
- 26 of the 40 are "Not found (404)": deleted exam-prep blog pages such as
  `/blog/free-ssc-syllogism-questions.html` and `/pages/bank-daily-practice.html`. They were
  left as 404s on purpose. The content is gone, it sold nothing to a hospital or a distributor,
  and redirecting it into the software cluster would be treated as a soft 404. The orphaned
  GitHub Actions workflow that once fed that `blog/` folder is bot-related and was not touched.
- 11 are "Discovered, currently not indexed", which on a low-authority site means Google has not
  thought them worth crawling yet. More internal links and a segmented sitemap are the levers,
  and both shipped.
- 2 redirects and 1 alternate-canonical, all expected.

## Checks that came back clean

- `www.elevateaura.co.in` already 301s to the apex domain, so nothing is splitting signals.
- The GA4 measurement ID on the property is `G-3XX97R8F1Y`, matching the tracking script.
- The Chennai HIMS page validates Breadcrumbs structured data and is indexed.

## What was configured in the accounts

**Search Console.** `sitemap.xml` was already submitted and reading successfully. It is now a
sitemap index over five segments, so the products, services, locations and resources maps can
be diagnosed separately; `sitemap-core.xml` and `sitemap-products.xml` were also submitted
directly. A fresh crawl was requested for
`/hims/hospital-management-software-chennai/`, the one page with proven impressions on a
commercial query.

**GA4.** See `14-conversion-tracking-plan.md`. A `generate_lead` key event now fires on any
enquiry action, with no invented monetary value and counted once per session.

## What to look for, and when

Give it time. New pages on a site with this little authority typically take weeks to be
crawled, indexed and ranked, and the first movement shows as impressions, not clicks.

| When | What should move |
|---|---|
| Week 1 to 2 | Indexed page count climbing from 68 toward 200; new URLs appearing in the Pages report |
| Week 3 to 6 | Impressions rising on non-brand queries; new queries appearing that the site never showed for |
| Week 6 to 12 | Average position improving on the long-tail pages first, which is where an unknown site wins |
| From the first enquiry | `generate_lead` in GA4, cut by `product_cluster` to see which product earns enquiries |

The honest measure of success here is not rankings. It is qualified enquiries, and the
tracking now exists to count them. Nothing in this work guarantees a position on any query.
