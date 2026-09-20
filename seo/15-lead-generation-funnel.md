# Deliverable 15: Lead-generation funnel

Search → relevant page → trust → product interest → enquiry → sales conversation → customer.
Each stage has a page type, a trust element and a call to action already in the templates.

## Stage by stage

| Stage | Query type | Page that catches it | Trust element on the page | CTA offered |
|---|---|---|---|---|
| Problem-aware | "AMC renewals lapsing", "hospital patients re-explaining history", "scans on CDs" | Guides (`/resources/`), problem-led feature pages | Byline of the builder, plain language, no hype | Soft: "See how Aura Business handles AMC" (link), WhatsApp in the strip |
| Solution-aware | "what is PACS", "AMC vs CMC", "cloud PACS vs on-premise" | Guides and comparisons | Fairness (says when the other option wins), definitions, tables | Link to the relevant product page; WhatsApp |
| Vendor-evaluating | "preventive maintenance software", "hospital TPA billing software", "PACS software India" | Feature, application, industry, country and city pages | Real screens, module lists, honest comparison table, real case studies, founder section | Book a Free Strategy Call (Aura Business → `/contact.html`, others → `/pages/contact.html`), live demo, WhatsApp with topic prefill |
| Proof-seeking | "case study", brand searches | `/case-studies/`, hub pages | Named real projects, stacks, module lists, what changed (qualitative) | Book a call, WhatsApp |
| Ready | "Aura Business demo", "AuraPACS download" | Contact, pricing (module picker), AuraPACS download | Direct number, founder name, 30-day framework | WhatsApp, phone, email, installer download |

## The three enquiry channels and why they are all kept

- **WhatsApp** (primary): fastest for Indian SMB buyers; every page's WhatsApp link is
  pre-filled with the page topic, which doubles as attribution. Tracked as `whatsapp_click`.
- **Phone**: on the contact pages and hero strips. Tracked as `phone_click`.
- **Email**: the homepage email CTA carries a structured subject and body that asks the four
  qualifying questions. Tracked as `email_click`.
- **Forms**: the site has no lead form on public pages today. A form is not required for the
  funnel to work; if one is added, `form_start` and `form_submit` are already tracked.

## Qualification (what the owner should ask, and what the pages pre-answer)

The homepage email template already asks: core problem, timeline, budget allocated, phone or
WhatsApp. The pages pre-answer the buyer's side: what the product covers, who it is for, what
it costs in structure (unlimited users, module tiers), how long (30 working days where scope
allows), who supports (the builder). A conversation that starts from a feature page is already
half-qualified.

## Offers by cluster

| Cluster | Primary offer | Secondary |
|---|---|---|
| Aura Business | 30-minute demo on your own products and customers; see your AMC leakage | Live demo (`/demo/aura-business.html`), build your plan (`/pricing.html`) |
| HIMS | Strategy call, walkthrough on your hospital's workflow | Hospital demo, dental demo |
| AuraPACS | Try the live demo; download the Windows demo | WhatsApp a Site ID to activate |
| Aura Learn | Strategy call, walkthrough on your courses and cohorts | LMS demo |
| Product Development | Talk to us with your hardware spec | Email |
| Services | Strategy call | WhatsApp |

## Nurture without a marketing stack

The site has no email automation. The realistic loop: enquiry on WhatsApp → owner logs it in
Aura Business CRM with the page URL as source → follow-ups from the CRM's own WhatsApp
reminders → demo → proposal. The CRM is the nurture tool, and it is the product being sold,
which is itself a proof point in the conversation.

## Lead magnets worth building (Phase 2, product or owner work)

1. A public browser DICOM viewer (upload, view, no login) on the AuraPACS hub: the strongest
   top-of-funnel asset in the imaging cluster per the competitor research.
2. An AMC leakage calculator (contracts, average value, renewal rate → rupees at risk) on the
   AMC page; it produces a number the owner can quote in the demo.
3. A HIMS vendor-evaluation checklist as a downloadable PDF from the how-to-choose guide.
4. A hospital-software pricing explainer if tier prices are published.

## KPIs

Primary: qualified organic enquiries per month by cluster, and revenue from them (CRM).
Secondary: key events per 100 organic sessions, landing pages with at least one enquiry, share
of enquiries from research pages (guides and comparisons) versus commercial pages, country
page enquiries.
