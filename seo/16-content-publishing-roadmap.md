# Deliverable 16: Content publishing roadmap

Nothing here promises rankings or lead counts. The roadmap sequences work by commercial
intent and evidence: the highest-intent pages first, research content once there is something
to send it to, and geographic expansion only after the first pages show impressions.

## What ships in this branch (Phases 1 to 8, first tranche)

| Phase | Scope | Shipped now |
|---|---|---|
| 0 Technical | OG image, 404, robots, sitemap index, tracking on every page, schema fixes, entity schema, mobile nav bug, title collisions, further-reading links from ranking pages | All done |
| 1 Highest commercial intent | Service management, dealer management, GST billing for distributors, quotation, hospital sales CRM, ABHA/ABDM page, hospital ERP, case studies, service hubs | Done |
| 2 Core product authority | Feature pages across Aura Business, HIMS, AuraPACS, Product Development | Done |
| 3 Applications | Modality PACS pages, Aura Learn use pages, protocol pages for device software | Done |
| 4 Industries | Nursing home, dental, diagnostic centre, multi-specialty, imaging centre, medical robotics | Done |
| 5 Countries | PACS: India, UAE, Saudi Arabia, Nigeria, Kenya; device software: USA, UK, Australia | Done |
| 6 Cities | Aura Business: Bengaluru, Hyderabad, Mumbai, Coimbatore; HIMS and AuraPACS: Coimbatore, Madurai; apps: Chennai | Done |
| 7 Educational | 14 guides in `/resources/` | Done |
| 8 Comparisons | 9 comparisons in `/compare/` | Done |

Exact counts are in `20-seo-qa-report.md` after the build.

## Next tranches (from `03-master-page-database.csv`, status PLANNED)

**Month 1 after deploy (owner tasks, no new pages)**
- Verify Search Console, submit `sitemap.xml`, mark GA4 key events, link Search Console to GA4.
- Pricing is settled: no price figure will be published. Price-intent search is served by
  four pricing pages that explain the pricing model, what moves a quote up or down, and the
  questions to ask any vendor, then ask for a call. No Offer markup returns to the schema.
- List Elevate Aura on Capterra India, SoftwareSuggest, TechnologyCounter with consistent
  NAP and product descriptions; add those URLs to `sameAs`.
- Product task: expose a public upload-and-view DICOM page for the "free online DICOM viewer"
  intent.

**Month 2 to 3 (Phase 2b and 3b, ~25 pages)**
- Aura Business feature long-tail: AMC billing, lead management, service dispatch, mobile job
  card, warehouse, batch and expiry, delivery challan, receivables ageing, WhatsApp payment
  reminders, purchase orders and GRN, SLA management, helpdesk ticketing.
- HIMS: nursing management, hospital asset management, e-prescription, MIS dashboard,
  procurement, package billing.
- AuraPACS: PACS backup and disaster recovery, referring doctor access, radiology scheduling.
- Aura Learn: live classes, batch management, fee management with GST, offline learning.

**Month 3 to 4 (Phase 4b, ~15 pages)**
- Aura Business industries: industrial, electrical, building products, HVAC AMC, lift AMC,
  fire safety AMC (the platform already claims these trades).
- HIMS industries with genuine differences: eye hospital, maternity, orthopaedic,
  physiotherapy, ayurveda (only if workflows are confirmed by the product owner).
- Device software applications: patient monitoring, wearables, diagnostic analyser
  connectivity, lab automation.

**Month 4 to 6 (Phase 5b and 6b, evidence-gated)**
- Countries: Singapore, Malaysia, South Africa, Qatar, Oman (AuraPACS); Canada, Singapore,
  New Zealand, UAE (device software). Open a market only when the current country pages show
  non-branded impressions.
- Cities: Trichy, Salem, Vellore, Pondicherry (HIMS and AuraPACS); Delhi NCR, Pune,
  Ahmedabad, Kochi, Kolkata (Aura Business). Each with its own local context.

**Ongoing (Phase 7b, 8b, 9)**
- Guides: TPA in hospital billing, EMR vs EHR, UHID, teleradiology, e-invoice IRN, delivery
  challan, SLA, rate contracts, firmware handover documentation, BLE GATT, Modbus, CAN, OTA.
- Comparisons: PACS vs teleradiology service, HIMS vs EMR, Tally vs operations software, BLE vs
  Wi-Fi, Modbus vs CAN, in-house vs outsourced firmware, Flutter vs React Native.
- Long-tail problem pages once Search Console shows the query language buyers actually use.

## Phase 10: continuous optimisation (monthly, 1 hour)

1. Pull the striking-distance list (position 8-20, impressions > 50) from the dashboard.
2. For each of five queries: sharpen the title, add the query's phrasing to the answer block or
   an FAQ, add two internal links from related pages.
3. Refresh `dateModified` on touched guides; rebuild; rerun QA; deploy.
4. Quarterly: merge or retire pages with zero impressions after two quarters; promote
   PLANNED pages whose cluster shows demand.

## Prioritisation rule used throughout

Score = search demand (from Search Console once live; from SERP shape before) × commercial
intent × content uniqueness available × conversion potential ÷ competition. Pages only move
from PLANNED to CONTENT when the owner can confirm the product fact the page depends on.

## Publishing mechanics

1. Write `seo/build/content/<cluster>__<slug>.json` following `CONTENT_SCHEMA.md` and `FACTS.md`.
2. `python seo/build/build_pages.py` (fails on thin or duplicate content).
3. `python seo/build/patch_existing.py` if a new feature should be linked from the hand-built
   pages (add it to the `RELATED` map).
4. `python seo/build/build_sitemaps.py`, `python seo/build/inventory.py`,
   `python seo/build/build_master_db.py`, `python seo/build/qa.py`.
5. Commit and push to `main`; GitHub Pages deploys.
