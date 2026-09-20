# Deliverable 5: International country strategy

Principle: a country page exists only where the product can actually be delivered there
without inventing anything. Elevate Aura has one office (Chennai), delivers remotely, invoices
in GST terms, and has no local partners or customers abroad. That rules a lot out, and the
pages say so plainly.

## Which products travel

| Product | Travels? | Why |
|---|---|---|
| AuraPACS | Yes | DICOM is universal; the on-premise node is installed by the centre's own IT with remote guidance; the browser viewer and WhatsApp sharing need no local presence; the product is not positioned as a diagnostic device. |
| Product Development (device software) | Yes | Fully remote, software-only, code handed over. Buyers in the US, UK and Australia already outsource firmware to India. |
| Mobile apps, websites, SEO services | Yes, opportunistically | Remote services; no dedicated country pages yet because the buyer usually searches by city or by "India" as the offshore signal. Handled by the India-facing service hubs. |
| Aura Business | Not yet | Billing is GST-native (CGST/SGST/IGST, e-invoice, e-way bill, GSTR prep). A UAE or Saudi page would have to promise VAT invoicing that is not on record. Revisit if a VAT variant is built. |
| HIMS | Not yet | TPA, ABHA/ABDM and GST workflows are India-specific. Gulf hospitals buy against local insurance-claim standards the product has not been verified against. |
| Aura Learn | Not yet | Global LMS SERPs are dominated by large platforms; the product's edge (GST fees, WhatsApp, Telegram, Indian exam prep) is domestic. |
| Auracare | No | Physical service in Chennai. |

## Market selection (scored on demand, business relevance, deliverability, regulation, language, competition)

| Market | AuraPACS | Device software | Verdict | Notes for the page |
|---|---|---|---|---|
| India | Pillar page built | Home market | Built: `/aurapacs/pacs-software-india/` | Hybrid for power and connectivity, GST built in, WhatsApp as the referral channel, ownership vs per-study billing. |
| UAE | Built | Later | Built: `/aurapacs/pacs-software-uae/` | English-speaking buyers, small regional vendors rank, Indian diaspora in clinic ownership. Page states remote deployment and tells buyers to confirm emirate health-information-exchange and data-residency obligations locally. No integration claims. |
| Saudi Arabia | Built | Later | Built: `/aurapacs/pacs-software-saudi-arabia/` | Large private diagnostic sector; English procurement; confirm local health-data rules. |
| Nigeria | Built | No | Built: `/aurapacs/pacs-software-nigeria/` | Open SERP, WhatsApp-dominant, power and bandwidth constraints suit the hybrid node. Volume likely small; low cost to hold the position. |
| Kenya | Built | No | Built: `/aurapacs/pacs-software-kenya/` | Same resilience angle; private diagnostic centres. |
| United States | No | Built | Built: `/product-development/embedded-software-development-usa/` | Time-zone overlap windows, NDA and IP assignment, fixed scope, USD quotes on request. No claim of a US entity or staff. |
| United Kingdom | No | Built | Built: `/product-development/embedded-software-development-uk/` | Same structure; UK working-hours overlap is easier. |
| Australia | No | Built | Built: `/product-development/embedded-software-development-australia/` | Strong overlap with Indian hours. |
| Singapore, Malaysia | Candidate | Candidate | Phase 5b | Small, English, high per-centre spend; build after UAE and Saudi show impressions. |
| South Africa | Candidate | No | Phase 5b | Private diagnostic sector; English. |
| Qatar, Oman, Kuwait | Fold into Gulf | No | Not built | Too small to justify separate pages without demand data; the UAE and Saudi pages carry Gulf intent. Add a Gulf section to the AuraPACS hub if impressions appear. |
| Germany, France, Netherlands | No | Maybe later | Not built | Language, procurement norms and CE expectations make a thin English page a doorway. Only with a German-language page and verified regulatory positioning. |
| Canada, New Zealand | No | Candidate | Phase 5b | Same playbook as US/UK/AU pages once those show demand. |

## Country page requirements (applied to every built page)

1. Market context written for that country (connectivity, procurement, who the buyer is),
   not a paragraph with the country name swapped.
2. Deployment truth: remote setup, on-premise node installed by local IT with guidance, cloud
   layer, WhatsApp and email support in English, time-zone overlap stated.
3. Regulation: one sentence telling the buyer to confirm local health-data and record-keeping
   rules with their advisers. No named regulation is asserted as satisfied.
4. Currency: quotes on request; no local price list.
5. No local office, partner, customer or case study. The three real case studies are Indian and
   are presented as such.
6. Country-specific FAQs (internet outages, data location, who installs, how support works).
7. `country` field set, `area_served` in Service schema, and the page listed in
   `sitemap-locations.xml`.

## Signals and language

- English only for now. `hreflang` is not needed until a second language exists. If Arabic
  or German pages are ever built, add `hreflang` pairs and self-references at that point.
- Google Search Console: register the property once and use the international-targeting
  report per page; do not create country subfolders (`/ae/`) for a site with one language
  and a shared product.
- Business Profile: keep the Chennai profile only. Do not create foreign listings.

## Measurement

Track per country page: impressions and clicks by country in Search Console, WhatsApp clicks
and form starts by page (GA4 events carry `page_path`), and enquiry outcomes logged in the CRM.
Promote a market to Phase 5b only when its page shows impressions for non-branded queries.
