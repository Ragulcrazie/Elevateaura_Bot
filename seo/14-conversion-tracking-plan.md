# Deliverable 14: Conversion tracking plan

Implemented in `assets/js/ea-track.js`, loaded (deferred) on every public page including the
generated ones and the 404. GA4 property: `G-3XX97R8F1Y` (the ID already present on the
site's legal pages). The script loads gtag itself if no other tag is present, so pages that
previously had GA4 keep a single instance.

## Events

| Event | Fires when | Parameters | Key event? |
|---|---|---|---|
| `page_view` | every page (automatic) | page_path, page_title | no |
| `whatsapp_click` | click on any `wa.me` or WhatsApp link | link_text, product_cluster, page_path | yes |
| `phone_click` | click on a `tel:` link | link_text, product_cluster, page_path | yes |
| `email_click` | click on a `mailto:` link | link_text, product_cluster, page_path | yes |
| `cta_click` | click on a `.btn`, `.nav-cta`, or any link whose href or text contains demo, strategy, quote, call or contact | link_text, link_url, product_cluster, page_path | no (funnel step) |
| `file_download` | click on .exe .msi .zip .pdf .apk or a `download` attribute (AuraPACS installer) | link_url, product_cluster, page_path | yes |
| `form_start` | first focus in any form field | product_cluster, page_path | no |
| `form_submit` | any form submit | form_id, product_cluster, page_path | yes |

`product_cluster` is the first path segment (`aura-business`, `hims`, `aurapacs`, `aura-learn`,
`product-development`, `mobile-app-development`, `resources`, `compare`, `case-studies`,
`home`), so every report can be cut by product without extra configuration.

## GA4 configuration (done on 20 September 2026)

The property is `Elevate Aura - Website`, measurement ID `G-3XX97R8F1Y`, stream "Elevate Aura -
Landing Page". It is the account reached with `authuser=3`; the Chrome profile's default Google
account has no access to it, which is worth knowing before anyone tries to open it.

A key event named `generate_lead` was created in Admin, Events, Create event. GA4 only lets you
star an event it has already seen, and these events had never fired before the deploy, so the
event is defined by rule instead:

- Trigger: `event_name` matches the regular expression
  `^(whatsapp_click|phone_click|email_click|form_submit|file_download)$`
- Marked as a key event
- No default monetary value, because no revenue figure per enquiry is known
- Counted once per session, so a visitor who clicks WhatsApp three times is one enquiry, not
  three

That gives one conversion metric covering every enquiry channel, under the name Google
recommends for lead generation, which also makes it usable in Google Ads later. The individual
events still exist underneath for channel-level reporting.

Verified live after deployment: `page_view`, `cta_click` and `email_click` all appeared in the
Realtime report from the production site. The derived `generate_lead` event applies to traffic
collected after the rule was created, so it starts counting from the next real enquiry.

Remaining, optional:

1. Star `whatsapp_click`, `phone_click`, `email_click`, `file_download` and `form_submit`
   individually once they appear in Admin, Events, Recent events, which lags Realtime by up to
   a day. This is only needed if you want each channel counted as its own conversion as well.
2. Admin → Custom definitions: register `product_cluster`, `link_text`, `link_url`, `form_id`
   as event-scoped custom dimensions so they appear in Explorations.
3. Admin → Data settings → Data retention: 14 months.
4. Link Search Console to GA4 for the landing-page query report.

## The funnel as measured

```
organic session (Search Console click / GA4 session with source google organic)
  → landing page (page_path, product_cluster)
    → cta_click (intent)
      → whatsapp_click | phone_click | email_click | form_submit | file_download (enquiry)
        → qualified enquiry (logged in Aura Business CRM by the owner, source = page URL)
          → demo held → proposal → customer
```

The last three steps live in the CRM, not GA4. The WhatsApp links are pre-filled with the
page topic ("Hi, I'd like to discuss preventive maintenance software...") so the owner can
attribute the enquiry to the page without asking.

## Reports to build (Explorations)

1. **Enquiries by page**: event count for the five key events, dimension page_path, filter
   source organic. This is the one number that matters.
2. **Enquiries by cluster**: same, dimension product_cluster.
3. **Landing page → CTA → enquiry funnel**: funnel exploration with the three steps, by
   product_cluster.
4. **Country pages**: key events with dimension country, filter page_path contains
   `-uae/`, `-saudi-arabia/`, `-nigeria/`, `-kenya/`, `-usa/`, `-uk/`, `-australia/`.
5. **Guide assist**: path exploration from `/resources/` and `/compare/` pages to product pages
   and enquiries, to show research content earning its keep.

## What is not tracked, on purpose

- No personal data in event parameters. `link_text` is the button label, never a typed value.
- No cross-site or advertising cookies added. The Google Ads tag present on legal pages was
  left as it was.
- Form field values are never read.

## Attribution hygiene

- Every outbound WhatsApp link already carries a topic prefill; keep that convention on new
  pages (the `whatsapp_text` field in the content JSON).
- The email CTA on the homepage carries a subject line; keep it.
- When the owner logs an enquiry in the CRM, record the page URL as lead source. That is the
  join key between GA4 and revenue.
