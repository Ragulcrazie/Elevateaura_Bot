# Deliverable 6: City and region strategy

The rule: a city page is written only when something true and different can be said about
serving buyers in that city. If the only difference is the city name, the page is not built.
Three things can make a city page legitimately different for Elevate Aura:

1. **In-person reach.** Chennai is home. Cities reachable by road or a short train ride
   (Coimbatore, Madurai, Trichy, Salem, Vellore, Pondicherry, Bengaluru at a stretch) can
   honestly be offered on-site kick-off, node installation and front-desk training.
2. **A real local industry cluster.** Bengaluru's medtech OEM and startup base, Hyderabad's
   device-manufacturing corridor, Mumbai's importer and national-distributor concentration,
   Coimbatore's engineering and hospital cluster. These change the buyer profile and the
   modules that matter.
3. **A distinct compliance or logistics reality.** Interstate billing (IGST, e-way bills) for a
   Mumbai importer shipping nationally versus intra-state billing for a Tamil Nadu dealer.

## Built in this pass

| Page | Product | What makes it different |
|---|---|---|
| `/hims/hospital-management-software-chennai/` (existing) | HIMS | Home city, on-site setup |
| `/aurapacs/pacs-software-chennai/` (existing) | AuraPACS | Home city, on-site node installation |
| `/auracare/*-chennai/` (existing) | Auracare | Physical service area |
| `/aura-business/medical-equipment-software-bangalore/` | Aura Business | OEM and startup ecosystem, multi-brand dealers, remote onboarding with same-day travel possible |
| `/aura-business/medical-equipment-software-hyderabad/` | Aura Business | Device-manufacturing base, dealers serving Telangana and Andhra, remote onboarding |
| `/aura-business/medical-equipment-software-mumbai/` | Aura Business | Importer hub, multi-state dealer networks, IGST-heavy interstate billing and e-way bills |
| `/aura-business/medical-equipment-software-coimbatore/` | Aura Business | Engineering and hospital city, in-person kick-off by road from Chennai, dealers serving Kerala |
| `/hims/hospital-management-software-coimbatore/` | HIMS | In-person setup and training by travel |
| `/hims/hospital-management-software-madurai/` | HIMS | Southern Tamil Nadu hospitals and nursing homes, in-person setup |
| `/aurapacs/pacs-software-coimbatore/` | AuraPACS | On-site node installation and modality connection by travel |
| `/aurapacs/pacs-software-madurai/` | AuraPACS | Same, southern Tamil Nadu |
| `/mobile-app-development/healthcare-app-development-chennai/` | Services | In-person discovery, Chennai case studies |

## Next candidates (Phase 6b, only after the above show impressions)

Tamil Nadu and neighbours with in-person reach: Trichy, Salem, Vellore, Pondicherry, Tirupati
(HIMS and AuraPACS). Metro dealer hubs for Aura Business: Delhi NCR (importers, government
tenders), Pune (device manufacturing), Ahmedabad (pharma and device trade), Kochi (Kerala
hospital density). Each needs its own local paragraph; the template is the four Aura
Business city pages already built.

## Explicitly rejected

- "Medical equipment software in [100 cities]": doorway pattern, no local content, and the
  product is delivered identically everywhere. Search Console would show near-zero clicks per
  page and the pattern risks a sitewide quality assessment.
- City pages for Aura Learn and Product Development: buyers of an LMS or firmware do not search
  by city, and delivery is remote. The Chennai service page covers local intent for apps.
- City pages for countries: only after a country page proves demand. A "PACS Dubai" page is a
  Phase 5b decision.

## What every city page must contain

- A local-context prose block that would not make sense with the city name swapped.
- Honest delivery statement: remote setup and WhatsApp support, in-person only where stated.
- The product's actual modules that matter for that buyer profile, with links to the
  feature pages.
- Use cases written for that profile (importer, OEM dealer, hospital cluster).
- City-specific FAQs (travel, training, language of support, interstate billing).
- BreadcrumbList and SoftwareApplication schema; `city` and `country` fields set so the page
  lands in `sitemap-locations.xml`.
- Never: a fake local office, "clients in [city]", local phone numbers other than the real one.

## Local entity signals to maintain

- One Google Business Profile for Elevate Aura in Chennai with the product categories, the real
  phone number and the website; the Auracare profile is separate and already has its own
  schema.
- Address and phone identical on the site footer, the profile, LinkedIn and every directory
  listing (Capterra India, SoftwareSuggest, TechnologyCounter, IndiaMART where relevant).
