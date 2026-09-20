# Elevate Aura verified facts sheet

Everything on a new page must be supported by this sheet or by the existing hub pages
(`aura-business.html`, `hims.html`, `aurapacs.html`, `aura-learn.html`, `product-development.html`,
`modules.html`). If a claim is not here, do not make it. When in doubt, describe the
workflow generically and point to the demo or a call.

## Company
- Name: Elevate Aura. Founder-led software studio in Chennai, Tamil Nadu, India.
- Founder and builder: Ragul Sekar. Solo end-to-end delivery. Before Elevate Aura: BFSI /
  healthcare technology at TCS (site says "3+ years BFSI" on some pages and "4 years healthcare
  tech" on Product Development). Azure AZ-104 certified.
- Contact: WhatsApp / phone +91 95789 71156 (wa.me/919578971156), email
  elevateauraofficial@gmail.com. In person in Chennai; remote everywhere else.
- Delivery framework: "live in 30 working days where scope allows". Fixed scope per project.
  Unlimited users on every Aura Business plan (priced by module tier: 15 / 47 / all 87).
- Stack used across products: React Native, Flutter, Next.js, Supabase, Azure, WordPress,
  Python, Playwright, embedded C/C++, MicroPython, .NET/C#.
- Real shipped work (only these three may be cited as case studies):
  1. Carna Medicare, medical-equipment distribution, Chennai. 12-module operations platform:
     field-staff app, manager dashboard, GST billing, payment tracking, service tracking.
     Stack: React Native, Supabase, WordPress. Shipped in 30 days.
  2. Medline Robotics, medical robotics, Chennai. Distributor and e-commerce platform:
     storefront, distributor portal, quotations, distributor ordering, payment (UTR)
     verification, and 253 product and city SEO landing pages across 4 product lines.
     Stack: Supabase, JavaScript, Playwright.
  3. Elevate Aura's own government-exam-prep app: Android app live on Google Play, Telegram
     practice bots, content automation. Stack: Flutter, Python, Supabase.
- Aura Business is "running two distribution businesses in Chennai today".
- Live demo environments: app.elevateaura.co.in (Aura Business), his.elevateaura.co.in (HIMS),
  pacs.elevateaura.co.in (AuraPACS), lms.elevateaura.co.in (Aura Learn). Demo pages on the
  site: /demo/aura-business.html, /demo/aura-business-trade.html, /demo/hospital.html,
  /demo/dental.html, /demo/lms.html.

## NEVER claim
- Client counts, revenue figures, percentages, ROI numbers, "trusted by X hospitals".
- Certifications other than Azure AZ-104 (no ISO, HIPAA, FDA, CE, NABH certification of the
  software; HIMS is described only as supporting "NABH-style documentation" and being
  "ABHA / ABDM ready").
- Offices, staff or on-site support outside Chennai. Other cities and countries are served
  remotely (cloud deployment, remote setup, WhatsApp support), unless the page is about Chennai
  or a place reachable for in-person work in Tamil Nadu (state the travel honestly).
- Named customers other than the three above. No testimonials, ratings, reviews.
- Prices. The site publishes no price in visible text anywhere. Aura Business tiers are
  described by module count only (15 / 47 / 87) with unlimited users; everything else is
  "scoped on a call". Do not reintroduce the 6,000 INR figure that used to sit in the hub's
  structured data: it was removed because nothing visible supported it, and only the owner can
  confirm whether it is current.
- Hardware design, PCB, manufacturing, or regulatory certification (Product Development is
  software-only).
- That AuraPACS is a diagnostic device. It stores, displays and shares imaging; the read is by
  the customer's radiologist.
- Non-GST tax regimes (VAT etc.) as built-in features. Billing is GST-native. For international
  pages say invoicing is configurable and confirm requirements on a call.

## Aura Business (operations platform for distributors, dealers, field-service businesses)
12 suites, 87 modules. Web dashboard for the office, mobile app for the field. GST-native.
Suites and modules (from modules.html):
1. CRM & Sales: Leads & Pipeline, Customer/Hospital Accounts, Contacts & Decision-Makers,
   Field Visits + GPS check-in, Sample Tracking, Activity Feed / Rep log, Territory & Target
   Management, Lead-Source & Conversion Analytics.
2. Quotation, Orders & GST Billing: GST Quotation Builder, Sales Orders, Tax Invoice (GST, PDF,
   gapless numbering, CGST/SGST/IGST), Delivery Challan, Payments & Receipts, Payment Tracker +
   reminders, E-Invoice (IRN/QR), E-Way Bill, Credit Notes / Returns, Proforma.
3. Inventory & Warehouse: Product Catalog & Lookup, Brand & Authorization, Serial / Unit-level
   Stock, Stock Movements / Ledger, Multi-Warehouse, Batch & Expiry Tracking, Low-Stock &
   Reorder Alerts, Barcode / QR Scan.
4. AMC & Service Contracts (revenue engine): Service Contracts (AMC), CMC Contracts, Warranty
   Tracking, Preventive Maintenance Schedules, SLA Definitions & Breach Tracking, Service
   Invoices, Contract Renewal Engine, Asset / Installed-Base Register, AMC Revenue & Leakage
   Dashboard (lapsing revenue shown in rupees).
5. Field Service (FSM): Breakdown / Service Call Intake, Technician Dispatch, Mobile Job Card,
   Spare Parts Used per Job (drops stock), Service History per Asset, Field Signature &
   Job-Done, Technician Route / Schedule, photo proof, offline mode.
6. Ticketing & Helpdesk: Ticket Management, Status Workflow, Internal Notes, SLA Timers,
   Customer Ticket Submission, CSAT / Feedback on Close.
7. Procurement & Suppliers: Supplier Master, Purchase Orders, Goods Receipt (GRN), Supplier
   Price Lists, PO Approval Workflow, Supplier Payments / Payables.
8. Tenders & Government Sales: Tender Tracker (government tenders auto-fetched every morning),
   Tender Document Vault, Bid / EMD & Deadline Reminders, Outcome & Win-Rate Analytics,
   Rate-Contract Management.
9. HRMS & Workforce: Attendance (Geo + Selfie), Leave, Staff Directory, Role-Based Access,
   GPS / Field Tracking, Staff Verification, Payroll Inputs, Shift & Roster.
10. Finance & Accounting: Receivables Ageing, Payables Ledger, Expense Management, Cashflow
    Dashboard, GST Returns Prep (GSTR-1/3B), Tally / Accounting Export, P&L by Product Line /
    Territory.
11. Customer & Distributor Portals: Customer Self-Service Portal, Distributor / B2B Order
    Portal, Distributor Payment / UTR, Order Tracking Page, Quote-Request Inbound, Branded Login
    + Docs Vault.
12. Analytics, AI & Platform: Owner / CEO Dashboard, Reports Engine, Notifications Hub,
    WhatsApp Business Integration (reminders), Audit Log, Tenant Admin & Module Store, AI
    Assistant, Settings / Branding / Org Config.
Also on the homepage module list: calibration and compliance checklists under preventive
maintenance, meter/usage-based PM, depreciation, asset transfers, multi-site contracts,
contract profitability, skill-based technician allocation, renewal prediction.
Setup: your Excel data migrated in, your branding on dashboard, app and invoices.
Industries: medical equipment (most shipped), industrial, electrical, building products, any
trade that sells, installs and services.

## HIMS (hospital & clinic management)
OP and IP registration, appointments and queue/tokens, EMR (structured; NABH-style
documentation), doctor and nursing workflows, e-prescription, pharmacy (dispensing queue,
low-stock and expiry alerts), laboratory / LIMS (order to verified result), inventory
(consumables, equipment, reorder levels), bed management (ward and bed occupancy), ICU (live
vitals per bed), operation theatre scheduling, emergency / casualty triage board, billing (cash,
insurance, TPA claims, GST), patient app / portal, doctor rosters, discharge, live dashboard of
OP, IP, beds and collections. AuraPACS imaging built in. ABHA / ABDM ready. Demo at
his.elevateaura.co.in and a dental clinic demo at /demo/dental.html. Built for Indian hospitals,
clinics, polyclinics, nursing homes and diagnostic centres. Live in 30 days where scope allows.

## AuraPACS (imaging)
Hybrid: an on-premise node on the centre's network (works without internet) plus a thin cloud
layer for remote viewing and encrypted offsite backup. Any modality: CT, MR, X-ray (CR/DR),
ultrasound, mammography "and more". Studies land automatically from the machine (DICOM
receive). Zero-download browser viewer (opens CT, MR, X-ray, ultrasound on any laptop; slice
scrolling, window/level). Modality worklist (schedule once, appears on the machine, no retyping).
Structured reporting templates per modality, finalised to PDF attached to the study. WhatsApp
report sharing via a secure link (no login for patient or referrer). Full searchable patient
history. Role-based access (radiologist, technician, front desk, referrer), audited. GST billing
and invoicing built in. Remote reading from home or a second site. Encrypted backup. Windows
demo installer (200 KB) that runs against the demo server; activation by Site ID via WhatsApp
after payment, then the full system runs on the customer's own network. Not a diagnostic
device. Live demo at pacs.elevateaura.co.in.

## Aura Learn (LMS)
Learner mobile app + instructor/admin web dashboard. Course & content library (video lessons,
downloads, offline access), quizzes and mock tests (auto-graded, instant scores, review),
question banks, certificates on completion, compliance tracking for regulated training, live
classes and webinars with recordings, discussion / doubt forum, batches and cohorts, timetable,
progress and analytics per learner and batch, WhatsApp reminders and drip content, Telegram bot
nudges, GST payments and subscriptions, fees. Unlimited learners. Built for coaching institutes,
exam-prep businesses, colleges, and companies training/certifying field and service staff.
Proven on the founder's own exam-prep app (Google Play). Demo at lms.elevateaura.co.in.

## Product Development (software-only)
Embedded firmware in C/C++ or MicroPython to the customer's hardware spec: core logic, state
handling, power management, sensor and peripheral integration. Communication: BLE (GATT,
pairing, streaming), Wi-Fi, serial/UART, Modbus, CAN. Companion mobile or web app (React
Native / same stack). Cloud telemetry and remote monitoring pipeline on Supabase or Azure.
OTA updates and drivers mentioned under firmware. Testing on the customer's hardware, delivered
ready to flash with documentation; customer owns the code. For medical-device and robotics
companies. Explicitly not: PCB design, manufacturing, mechanical/enclosure, hardware regulatory
certification.

## Also offered (homepage "Also available")
- Mobile apps: Android & iOS, GPS, offline mode, Play Store publishing (React Native / Flutter).
- Websites & e-commerce: WordPress and Next.js sites and online stores; distributor portals;
  product-line SEO pages (Medline Robotics: 253 pages). The Elevate Aura site itself is built
  by the founder.
- Marketing & SEO: programmatic SEO (50 to 250 pages per product and city), schema, GA4,
  WhatsApp campaigns.

## Auracare
Separate home-nursing service line in Chennai (its own cluster, leave untouched).
