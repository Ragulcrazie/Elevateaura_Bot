# Deliverable 12: Schema implementation plan

Rule: schema describes only what is visible on the page. No Offer, AggregateRating, Review,
Rating, price or availability anywhere on this site until real, visible prices or reviews
exist.

Two Offer blocks were removed for breaking that rule. The medical-equipment CRM page declared
a price of 0. The Aura Business hub declared 6,000 INR per month for 15 modules, a figure that
appears in no visible text on any page: `pricing.html` computes its tier in JavaScript and
renders no number at all. Google's structured-data policy requires markup to represent content
the visitor can see, so both were deleted rather than left in place. The owner has since decided
not to publish prices, so no Offer, price or priceRange property may appear anywhere on this
site. The pricing pages describe the model in words and carry no numbers to mark up.

## Site-wide entity (homepage)

```json
{ "@type": ["Organization", "ProfessionalService"], "@id": "https://elevateaura.co.in/#organization",
  "name": "Elevate Aura", "url": "https://elevateaura.co.in/", "logo": ".../assets/img/logo.png",
  "founder": { "@type": "Person", "name": "Ragul Sekar" },
  "telephone": "+91-95789-71156", "email": "elevateauraofficial@gmail.com",
  "address": { "@type": "PostalAddress", "addressLocality": "Chennai", "addressRegion": "Tamil Nadu", "addressCountry": "IN" },
  "sameAs": ["https://www.linkedin.com/in/ragul-sekar", "https://github.com/Ragulcrazie"],
  "areaServed": [...], "serviceType": [...], "knowsAbout": [...] }
{ "@type": "WebSite", "@id": "https://elevateaura.co.in/#website", "publisher": { "@id": ".../#organization" } }
```

Implemented. Add more `sameAs` URLs (Google Business Profile, Play Store developer page,
Capterra listing) as they exist; they are the strongest cheap entity signals available.

## Per page type

| Page type | Types emitted | Notes |
|---|---|---|
| Product hub | Organization (provider), SoftwareApplication, FAQPage | Existing; the Aura Business hub's Offer block was removed, see below |
| Product feature / application / industry / city / country | BreadcrumbList, SoftwareApplication (`applicationCategory` Business, Health or Educational), FAQPage | Generated. `operatingSystem` "Web, Android, iOS" matches the product claims |
| Product Development and service pages | BreadcrumbList, Service (`serviceType`, `provider`, optional `areaServed`), FAQPage | Generated |
| Guide, comparison, case study | BreadcrumbList, Article (`author` Person Ragul Sekar, `publisher` Organization with logo, `datePublished`, `dateModified`, `image`), FAQPage | Generated; visible byline and date match |
| Auracare | MedicalBusiness with areaServed cities, OpeningHoursSpecification, MedicalProcedure list | Existing, correct, untouched |
| 404, admin, portals | none | noindex |

## Validation

- Every generated page's JSON-LD is parsed by the QA script; the build fails on invalid JSON.
- Spot-check five URLs per type in Google's Rich Results Test after deployment (FAQ and
  Breadcrumb are the two rich-result-eligible types here; Article and SoftwareApplication
  without Offer/Rating are entity signals, not rich results).
- Search Console → Enhancements: watch FAQ and Breadcrumb reports monthly for errors.

## Deliberately not used

- `HowTo`: none of the pages are step-by-step instructions the user performs; the flow blocks
  describe how the software works, which is not HowTo's intent.
- `LocalBusiness` on city pages: Elevate Aura has no premises in those cities.
- `Product` with `Offer`: no public price list.
- `VideoObject`: no videos yet. If demo videos are added, emit it on the hub pages.
- `SpeakableSpecification`, `ClaimReview`, `Course`: not applicable.

## Future additions

- `Person` page for the founder with `sameAs` and `jobTitle` once `/pages/about.html` is
  rewritten as the entity page (Phase 2).
- `ItemList` on hub pages listing the cluster children (harmless, modest value).
- `Product` + `Offer` on `pricing.html` if tier prices are published in visible text.
