# Deliverable 8: URL architecture

Static site on GitHub Pages (custom domain `elevateaura.co.in`, no server-side redirects).
Rules: lowercase, hyphenated, keyword-led slugs; one folder per product or content hub; every
page lives at `/<hub>/<slug>/` so the hub is the crawlable parent; no `.html` in new URLs; old
root-level `.html` product stubs stay as meta-refresh forwards with canonicals.

```
/                                   Homepage (entity page for Elevate Aura)
/pages/about.html                   Company about (entity)          /pages/contact.html   Contact
/aura-business.html                 Hub: Aura Business             /modules.html   87 modules   /pricing.html   Build your plan
/hims.html                          Hub: HIMS
/aurapacs.html                      Hub: AuraPACS
/aura-learn.html                    Hub: Aura Learn
/product-development.html           Hub: Product Development
/auracare/                          Hub: Auracare (home nursing, separate line, untouched)
/mobile-app-development/            Hub: Mobile apps (new)
/web-development/                   Hub: Websites & e-commerce (new)
/seo-services/                      Hub: SEO services (new)
/resources/                         Hub: plain-language guides (new)
/compare/                           Hub: comparisons (new)
/case-studies/                      Hub: real projects (new)
```

## Existing pages (keep)

Aura Business: medical-equipment-crm-software, medical-equipment-management-software,
medical-equipment-field-service-software, medical-equipment-amc-cmc-software,
medical-equipment-inventory-software, medical-equipment-asset-management,
medical-equipment-billing-software, healthcare-crm-software,
medical-equipment-distributor-software, healthcare-business-automation-software.

HIMS: hospital-management-system, clinic-management-software, hospital-billing-software,
hospital-appointment-management, patient-management-software, doctor-management-software,
hospital-pharmacy-management, hospital-laboratory-management, hospital-inventory-management,
hospital-management-software-chennai.

AuraPACS: pacs-software, dicom-viewer, cloud-pacs-software, ris-pacs-software,
dicom-worklist-software, medical-imaging-software, radiology-workflow-software,
diagnostic-centre-pacs, hospital-pacs-software, pacs-software-chennai.

Aura Learn: learning-management-system, lms-software, online-exam-platform,
online-quiz-platform, student-management-system, course-management-software,
training-management-software, learning-app-development, exam-preparation-platform,
custom-lms-development.

Product Development: medical-device-software-development, embedded-software-development,
firmware-development, ble-device-software, iot-product-development,
medical-device-app-development, device-companion-app-development, healthcare-app-development,
custom-healthcare-software, medical-technology-product-development.

## New pages (Phase 1 to 6 build, generated from `seo/build/content/`)

### /aura-business/
| slug | primary keyword | type |
|---|---|---|
| medical-equipment-service-management-software | medical equipment service management software | feature |
| preventive-maintenance-software | preventive maintenance software for medical equipment | feature |
| service-contract-management-software | service contract management software | feature |
| medical-equipment-quotation-software | medical equipment quotation software | feature |
| field-technician-tracking-app | technician tracking software / service engineer app | feature |
| medical-spare-parts-inventory-software | medical spare parts inventory software | feature |
| medical-equipment-tender-management-software | tender management software for medical equipment | feature |
| medical-device-crm-software | medical device CRM software (manufacturer / OEM sales) | product |
| installed-base-management-software | installed base management software | feature |
| medical-equipment-dealer-management-software | medical equipment dealer management software | product |
| gst-billing-software-medical-equipment-distributors | GST billing software for medical equipment distributors | commercial |
| medical-equipment-warranty-management-software | equipment warranty management software | feature |
| medical-distributor-dashboard-analytics | medical distributor analytics / sales & service dashboard | feature |
| hospital-sales-crm | hospital sales CRM (selling to hospitals) | persona |
| medical-equipment-software-bangalore | medical equipment software Bangalore | city |
| medical-equipment-software-hyderabad | medical equipment software Hyderabad | city |
| medical-equipment-software-mumbai | medical equipment software Mumbai | city |
| medical-equipment-software-coimbatore | medical equipment software Coimbatore | city |

### /hims/
| slug | primary keyword | type |
|---|---|---|
| hospital-emr-software | hospital EMR software | feature |
| hospital-opd-management-software | hospital OPD software | feature |
| hospital-ipd-management-software | hospital IPD software | feature |
| hospital-insurance-tpa-billing-software | hospital TPA / insurance billing software | feature |
| hospital-bed-management-software | hospital bed management software | feature |
| hospital-queue-management-software | hospital queue / token management software | feature |
| operation-theatre-management-software | operation theatre management software | feature |
| icu-management-software | ICU management software | feature |
| emergency-department-software | emergency department / casualty software | feature |
| multi-specialty-hospital-software | multi-specialty hospital software | industry |
| nursing-home-management-software | nursing home management software | industry |
| dental-clinic-management-software | dental clinic management software | industry |
| diagnostic-centre-management-software | diagnostic centre management software | industry |
| hospital-erp-software | hospital ERP software | product |
| abha-abdm-ready-hospital-software | ABHA / ABDM ready hospital software | commercial |
| hospital-management-software-coimbatore | hospital management software Coimbatore | city |
| hospital-management-software-madurai | hospital management software Madurai | city |

### /aurapacs/
| slug | primary keyword | type |
|---|---|---|
| on-premise-pacs | on-premise PACS | feature |
| hybrid-pacs | hybrid PACS | feature |
| pacs-for-ct-scan-centres | PACS for CT scan centres | application |
| pacs-for-mri-centres | PACS for MRI centres | application |
| digital-x-ray-pacs | digital X-ray PACS / CR DR archive | application |
| ultrasound-pacs | ultrasound PACS / image archive | application |
| mammography-pacs | mammography PACS | application |
| radiology-reporting-software | radiology reporting software | feature |
| whatsapp-medical-report-sharing | WhatsApp medical report sharing | feature |
| medical-image-archive-storage | medical image storage / archive | feature |
| teleradiology-remote-reading-software | teleradiology / remote reading software | feature |
| dicom-server-software | DICOM server software | feature |
| imaging-centre-software | imaging centre software | industry |
| pacs-software-india | PACS software India | country |
| pacs-software-uae | PACS software UAE | country |
| pacs-software-saudi-arabia | PACS software Saudi Arabia | country |
| pacs-software-nigeria | PACS software Nigeria | country |
| pacs-software-kenya | PACS software Kenya | country |
| pacs-software-coimbatore | PACS software Coimbatore | city |
| pacs-software-madurai | PACS software Madurai | city |

### /aura-learn/
| slug | primary keyword | type |
|---|---|---|
| coaching-institute-management-software | coaching institute software | industry |
| mock-test-platform | mock test platform | feature |
| online-assessment-platform | online assessment platform | feature |
| certification-training-platform | certification platform / training certification software | feature |
| corporate-training-lms | corporate training LMS | industry |
| healthcare-training-lms | healthcare / medical staff training software | industry |
| question-bank-software | question bank software | feature |

### /product-development/
| slug | primary keyword | type |
|---|---|---|
| medical-device-firmware-development | medical device firmware development | product |
| healthcare-iot-software-development | healthcare IoT software development | product |
| device-to-cloud-telemetry-software | device-to-cloud / IoT telemetry software | feature |
| modbus-software-development | Modbus software development | feature |
| can-bus-software-development | CAN bus software development | feature |
| wifi-connected-device-software | Wi-Fi connected device software | feature |
| micropython-development-services | MicroPython development | feature |
| ota-firmware-update-development | OTA firmware update system | feature |
| medical-robotics-software-development | medical robotics software | industry |
| device-dashboard-development | device monitoring dashboard development | feature |
| embedded-c-cpp-development-services | embedded C/C++ development services | feature |
| sensor-integration-software | sensor integration software | feature |
| embedded-software-development-usa | embedded software development for US companies | country |
| embedded-software-development-uk | embedded software development for UK companies | country |
| embedded-software-development-australia | embedded software development for Australian companies | country |

### /mobile-app-development/
index, healthcare-mobile-app-development, hospital-mobile-app-development,
doctor-app-development, patient-app-development, field-service-mobile-app-development,
flutter-healthcare-app-development, react-native-healthcare-app-development,
medical-equipment-service-app, healthcare-app-development-chennai.

### /web-development/
index, medical-equipment-website-development, medical-equipment-ecommerce-development,
medical-distributor-portal-development, healthcare-website-development,
medical-product-catalogue-website, healthcare-b2b-ecommerce-platform.

### /seo-services/
index, medical-equipment-seo, healthcare-seo-services, hospital-seo-services,
programmatic-seo-services, healthcare-saas-seo, medical-equipment-lead-generation,
medical-device-seo.

### /resources/ (guides, Article schema)
index, what-is-pacs, what-is-dicom, what-is-ris, what-is-hims, what-is-amc-software,
what-is-cmc, what-is-medical-equipment-crm, how-medical-equipment-service-management-works,
how-to-choose-hospital-management-software, how-to-choose-pacs,
what-is-dicom-modality-worklist, what-is-lms, what-is-preventive-maintenance-software,
what-is-installed-base-management.

### /compare/
index, pacs-vs-dicom-viewer, pacs-vs-cloud-storage, cloud-pacs-vs-on-premise-pacs,
crm-vs-erp-for-medical-equipment-distributors, amc-vs-cmc, hims-vs-hospital-erp,
generic-crm-vs-medical-equipment-crm, spreadsheets-vs-distributor-software,
lms-vs-youtube-and-whatsapp-for-coaching.

### /case-studies/
index, carna-medicare-medical-equipment-distributor-platform,
medline-robotics-ecommerce-distributor-platform, exam-prep-learning-app.

## Deliberately not built (and why)

- Specialty HIMS pages (cardiology, orthopaedics, ENT, ...): HIMS has no specialty-specific
  modules on record. They would be the same page with a specialty name swapped in. Revisit
  when specialty templates or EMR forms exist.
- Aura Business / HIMS country pages: billing is GST-native and HIMS is built around Indian
  TPA / ABDM workflows. International pages would have to claim VAT or local claim workflows
  that are not verified. AuraPACS and device software travel; those get country pages.
- 100 city pages: only cities where something true and different can be said (in-person
  reach from Chennai, a real local industry cluster, or a distinct buyer profile).
- Pricing pages with numbers: no verified price list. Recommended as a Phase 2 owner task.
- A free online DICOM viewer tool page: strong lead magnet per competitor research, but it
  needs the product team to expose a public upload endpoint. Logged in the roadmap.

## Redirect / canonical rules

- Root stubs (`/medical-equipment-crm.html` etc.) keep a meta refresh plus canonical to the
  cluster page. GitHub Pages cannot issue 301s; if the site ever moves behind Cloudflare, convert
  these to 301 rules.
- `/about.html`, `/contact.html`, `/how-it-works.html`, `/pricing.html`, `/modules.html` are
  Aura Business pages. The company pages are `/pages/about.html` and `/pages/contact.html`.
  Titles are adjusted so the two sets do not compete.
- Every page declares one self-referencing canonical. No parameters, no trailing-slash variants
  in internal links.

## Batch 2: HIMS and Aura Business focus (September 2026)

The owner's priority is HIMS and Aura Business (CRM), so the next tranche builds only those two
clusters. These are the exact slugs; link to them freely from either cluster.

### /hims/ (batch 2)
| slug | primary keyword | type |
|---|---|---|
| hospital-nursing-management-software | hospital nursing management software | feature |
| hospital-asset-management-software | hospital asset management software | feature |
| e-prescription-software | e-prescription software India | feature |
| hospital-mis-dashboard | hospital MIS dashboard | feature |
| hospital-procurement-software | hospital procurement software | feature |
| hospital-package-billing-software | hospital package billing software | feature |
| hospital-corporate-credit-billing | hospital credit and corporate billing | feature |
| uhid-patient-registration-software | UHID patient registration software | feature |
| hospital-whatsapp-appointment-reminders | hospital WhatsApp appointment reminders | feature |
| polyclinic-management-software | polyclinic management software | product |
| small-hospital-software | small hospital software India | product |
| day-care-centre-software | day care centre software | product |
| hospital-software-for-administrators | hospital software for administrators | persona |
| hospital-owner-dashboard | software for hospital owners dashboard | persona |
| clinic-management-software-chennai | clinic management software Chennai | city |
| hospital-management-software-trichy | hospital management software Trichy | city |
| hospital-management-software-salem | hospital management software Salem | city |
| hospital-management-software-vellore | hospital management software Vellore | city |
| hospital-management-software-pondicherry | hospital management software Pondicherry | city |

### /aura-business/ (batch 2)
| slug | primary keyword | type |
|---|---|---|
| amc-billing-software | AMC billing software | feature |
| medical-equipment-lead-management-software | medical equipment lead management software | feature |
| service-dispatch-software | service dispatch software | feature |
| mobile-job-card-software | mobile job card software | feature |
| medical-equipment-warehouse-management | medical equipment warehouse management | feature |
| batch-expiry-tracking-software | batch and expiry tracking software | feature |
| delivery-challan-software | delivery challan software | feature |
| receivables-ageing-software | receivables ageing software | feature |
| whatsapp-payment-reminder-software | WhatsApp payment reminder software | feature |
| purchase-order-grn-software | purchase order and GRN software | feature |
| sla-management-software | SLA management software field service | feature |
| helpdesk-ticketing-equipment-dealers | helpdesk ticketing software for equipment dealers | feature |
| e-invoice-software-distributors | e-invoice software for distributors | feature |
| e-way-bill-software-distributors | e-way bill software distributors | feature |
| software-for-diagnostic-equipment-suppliers | software for diagnostic equipment suppliers | application |
| software-for-medical-device-importers | software for medical device importers | application |
| software-for-surgical-instrument-distributors | software for surgical instrument distributors | application |
| software-for-laboratory-equipment-dealers | software for laboratory equipment dealers | application |
| software-for-imaging-equipment-dealers | software for imaging equipment dealers | application |
| software-for-dental-equipment-dealers | software for dental equipment dealers | application |
| software-for-hospital-furniture-suppliers | software for hospital furniture suppliers | application |
| software-for-medical-consumables-distributors | software for medical consumables distributors | application |
| software-for-biomedical-service-companies | software for biomedical service companies | application |
| industrial-equipment-distributor-software | industrial equipment distributor software | industry |
| electrical-equipment-dealer-software | electrical equipment dealer software | industry |
| hvac-amc-software | HVAC AMC software | industry |

### /resources/ and /compare/ (batch 2, supporting these two clusters only)
what-is-tpa-hospital-billing, emr-vs-ehr, what-is-uhid,
hospital-software-implementation-checklist, what-is-e-invoice-irn,
how-to-choose-medical-equipment-crm, what-is-sla-equipment-service;
compare: hims-vs-emr, cloud-vs-on-premise-hospital-software.

### Held back pending owner confirmation
Eye, maternity, orthopaedic, paediatric, physiotherapy and ayurveda HIMS pages. These are only
worth building if the platform genuinely differs for them (different forms, records or
workflows). Without that, they would be the generic page with a specialty name swapped in,
which is the doorway pattern this system refuses.
