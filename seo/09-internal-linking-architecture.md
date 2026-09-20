# Deliverable 9: Internal-linking architecture

Goal: every page has one parent, several siblings and at least one link into a different
content type (guide, comparison or case study), so authority flows down from the hubs and
research pages feed the commercial ones.

## The graph

```
Homepage
├── Product hubs (aura-business.html, hims.html, aurapacs.html, aura-learn.html, product-development.html, /auracare/)
│   ├── Head-term pages (existing 10 per hub)                      link: hub ↔ page, page ↔ 3+ siblings
│   ├── Feature / application / persona pages (new)                link: hub ↔ page, page ↔ 3+ siblings, page → 1 guide, page → 1 comparison, page → case study
│   ├── City and country pages (new)                               link: hub ↔ page, page → feature pages that matter for that buyer
│   └── Footer on every page → all hubs + Case Studies + Guides + Comparisons + About + Contact
├── Service hubs (/mobile-app-development/, /web-development/, /seo-services/)
│   └── Service pages                                              link: hub ↔ page, page → product pages they build on (HIMS, Aura Business), page → case study
├── /resources/ (guides)                                           each guide → 2-3 sibling guides, 1 comparison, 1-2 product pages
├── /compare/                                                      each comparison → the two product pages compared, 1 guide, hub
└── /case-studies/                                                 each case study → the feature pages that were built, the service hubs
```

## Link rules (enforced by the generator and the patch script)

1. **Breadcrumb**: Home → Hub → Page on every generated page, with matching BreadcrumbList
   schema. The hub crumb is the hub URL, never a `#anchor`.
2. **Hub down-links**: the five product hubs already list their ten children. Their footers now
   carry the guide, comparison and case-study links for that product. New service hubs list
   every child in a `hubgrid` block.
3. **Sibling links**: every generated page has a `related` block of 5-6 links. At least three
   point to sibling pages in the same cluster; at least one points to `/resources/` or
   `/compare/`; one points to a case study where the project is relevant.
4. **Up-links from the old pages**: every hand-built cluster page received a "Further reading"
   block (six links: three new feature pages, one guide, one comparison, one case study) so the
   pages that already rank pass authority to the new ones. Marked with `<!-- ea-related -->`.
5. **Guides link commercially, once**: a guide links to the product page that solves the
   problem at the natural point in the text and again in its related block. It does not link to
   the same commercial page five times.
6. **Anchor text**: descriptive and varied ("preventive maintenance software", "PM visits from
   the contract"), never "click here". Exact-match anchors are used at most once per page.
7. **Root-absolute URLs** in all new content (`/aura-business/...`). The hand-built pages use
   relative links; both resolve identically on the custom domain.
8. **No orphan rule**: the QA script checks that every generated page is linked from at least
   two other pages (its hub or a sibling, and one cross-type page).

## Topic clusters and their spine links

| Cluster spine | Pages that must link to each other |
|---|---|
| Aura Business after-sales loop | CRM → quotation → billing → installed base → AMC/CMC → service contracts → preventive maintenance → service management → field technician app → spare parts → warranty → dashboard |
| HIMS patient journey | OPD → appointments/queue → EMR → IPD → beds → OT/ICU/emergency → pharmacy → lab → billing/TPA → patient app; ABHA page links to EMR and billing |
| AuraPACS image path | DICOM server → worklist → archive/storage → viewer → reporting → WhatsApp sharing → remote reading; modality pages link to viewer, worklist and reporting; deployment pages (on-premise, hybrid, cloud) link to each other and to the comparison |
| Aura Learn | LMS → course management → question bank → mock tests → assessment → certification → coaching institute / corporate / healthcare training |
| Product Development | embedded → firmware → medical device firmware → BLE / Wi-Fi / Modbus / CAN → sensors → telemetry → dashboard → OTA → companion app → mobile hub |
| Research to commercial | what-is-X guide → how-to-choose guide → comparison → product page → case study → contact |

## Maintenance

- Adding a page: write its JSON with a `related` block that satisfies rule 3, then add it to the
  `related` blocks of at least two siblings and, if it is a new feature, to the `RELATED` map in
  `patch_existing.py` for its cluster.
- Removing a page: search `seo/build/content/` for its URL and the hand-built pages for the
  same string before deleting; the QA script fails on dead internal links.
