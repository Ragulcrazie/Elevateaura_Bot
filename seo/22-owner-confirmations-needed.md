# Deliverable 22: Claims that need the founder's confirmation

Every page on this site is written against `seo/build/FACTS.md`, which records what may be
claimed. While writing, the content writers flagged statements that extend a documented module
rather than restate it. None invents a new product. Each is listed here with what it would take
to settle it, so nothing sits on the site unexamined.

Where a claim would be embarrassing if a prospect tested it in a demo, it has already been
softened into language about what is configured or proposed rather than what always happens.
Those are marked SOFTENED. The rest read as written and simply need a yes or no.

## Aura Business

| Claim on the page | Status | What to confirm |
|---|---|---|
| Pro-rata or part-period instalments when an AMC starts mid-period | SOFTENED to "billing schedule set to the contract terms" | Does contract billing support part-period amounts? |
| Earliest-expiry batch proposed first at despatch | SOFTENED from "first-expiry-first-out picking" | Does the despatch screen suggest a batch, or does the user pick freely? |
| Ageing buckets are configurable | As written | Are the buckets fixed or set per client? |
| Near-expiry alert thresholds are configurable | As written | Fixed number of days, or set per product? |
| A WhatsApp enquiry can be logged as a lead, a WhatsApp message as a ticket | As written | Does the WhatsApp integration create records, or only send messages? |
| Vehicle details updated against an existing e-way bill after transhipment | As written | Does the platform handle the Part B update, or is that done on the government portal? |
| Contract billing frequency is configurable | As written | Monthly, quarterly, annual, all of them? |
| Credit limit and credit days per customer | Documented in FACTS | No action, already on record |
| Beat plans | As written, the page states plainly that the beat is built from territory, GPS visits and route scheduling rather than a separately named module | There is no beat-plan module in the module list. Confirm the workaround is how it is actually sold |
| Geo-fenced attendance | As written, "can be geo-fenced where that is agreed" | The module list has "Attendance (Geo + Selfie)" but not fencing. Does it fence to a site? |
| Rate contract quantity drawdown, what has been supplied and what remains | SOFTENED to "where a quantity ceiling exists" | Rate-Contract Management exists; confirm whether drawdown against a ceiling is tracked |
| Contract rate applied automatically to a quotation | As written, override deferred to role-based access | Confirm the quote honours the contract rate |
| Selfie image retention policy | As written, "settled during setup" | Confirm there is a retention setting |
| Tally export scope, format and frequency | As written, "agreed at setup" | Confirm what actually exports |
| A withheld or retained balance kept open against a customer | As written, never called a retention feature | Can a part-paid balance sit open in the payment tracker and ageing? |
| A site or an engineer's van treated as a stock location | As written, presented as an application of Multi-Warehouse | Can arbitrary stock locations be created? |
| Ordered, delivered and balance quantity per order line | As written, presented as a consequence of despatching against the order | Is the balance quantity actually shown? |
| Scanning a barcode to open the right asset on a phone | As written | Is scanning catalogue-only, or does it look up an asset? |
| Optical dispensing depth on the eye hospital page | Hedged | How far does retail-style dispensing go? |
| Unit or lot level implant tracking on the orthopaedic page | Hedged | Is implant traceability to the case supported? |
| How a session package's remaining balance is displayed | Hedged | Confirm drawdown display |

## HIMS

| Claim on the page | Status | What to confirm |
|---|---|---|
| HIMS is delivered as a cloud workspace | As written, hedged | Is on-premise HIMS ever offered? The facts sheet documents hybrid deployment only for AuraPACS, so the comparison page pushes the buyer to settle deployment on the call |
| Go-live training can be recorded for later hires | As written | Is a recording actually provided? |
| Nursing charts and medication administration against the patient record | As written | The facts sheet says "doctor and nursing workflows" and ICU "live vitals per bed"; confirm the nursing detail |
| Hospital has no general-ledger accounting | SOFTENED to "not where your accountant keeps the books" | Confirm the boundary so the page sets the right expectation |
| Prerequisites before an on-site visit, such as a machine on the modality network with a fixed address | As written | Operational detail, confirm the list is right |
| Purchase orders and goods receipt inside HIMS | SOFTENED, page frames buying as the front end of the documented inventory module and rules out a payables ledger | The facts sheet names purchase orders and GRN for Aura Business but only "inventory with reorder levels" for HIMS. Does HIMS actually raise orders and book receipts? |
| Wards raising their own indents | SOFTENED to "that is how it is set up", with depth agreed in scoping | Confirm ward indents exist |
| Nursing shift handover and medication administration recorded against the patient | As written, described as timed attributed entries rather than a separate module | Confirm the nursing detail |
| Duplicate prevention by searching before creating a patient | As written, phrased as a workflow not a feature | Confirm |
| A chair as a tracked place in a day care unit | As written, extends bed management; a dialysis module is explicitly refused | Confirm |
| Per-doctor consultation and collection figures in a polyclinic | As written; automated payout calculation explicitly deferred to a call | Confirm |
| WhatsApp appointment and follow-up reminders in HIMS | As written, templates "agreed at setup" | The facts sheet lists WhatsApp under Aura Business and AuraPACS, not HIMS. Confirm it is available for hospitals |
| Multi-location HIMS: shared patient base, central tariff, per-location and group views | As written, stated as configured during scoping | The facts sheet documents multi-warehouse and tenant admin for Aura Business but nothing explicit for multi-branch hospitals. Does HIMS run a group of hospitals on one instance? |
| Consent documentation held on the patient record | As written | The facts sheet covers structured EMR and NABH-style documentation but does not name consent forms |
| Which roles may amend or cancel, and searching the audit log by user or date | As written, phrased as "agreed during scoping" | The facts sheet documents an audit log and role-based access but not the search screen |

## Product Development

| Claim on the page | Status | What to confirm |
|---|---|---|
| Work delivered into the client's own repository and cloud account | SOFTENED to what can be offered | Is this how engagements actually run? |
| Testing on the client's hardware by a unit sent to Chennai or a rig reached remotely | SOFTENED to "whichever route we agree" | Which is normal? |
| An NDA is signed before scoping | As written | Standard practice, confirm |

## The two specialty questions still open

1. **Does HIMS differ by medical specialty?** Six pages (eye, maternity, orthopaedic,
   paediatric, physiotherapy, ayurveda) are being written around how each specialty's day runs,
   which is true of any general hospital system. If HIMS also has specialty-specific forms,
   records or templates, say so and those pages become far stronger. If it has none, the pages
   stay as written and remain honest.
2. **Is there a settled pricing model for HIMS and AuraPACS?** The facts sheet documents module
   tiers and unlimited users for Aura Business, and unlimited learners for Aura Learn, but
   nothing for the other two. Their pricing pages therefore say only that it is scoped on the
   call. A settled model would let those pages answer the question buyers actually ask.

## How to use this

Answer the ones you can in a single message. Anything confirmed gets added to `FACTS.md` and
the pages get sharper. Anything denied gets rewritten the same day. Nothing here blocks the
site from running as it is.
