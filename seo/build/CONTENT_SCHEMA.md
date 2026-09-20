# Page content schema

One JSON file per page in `seo/build/content/`, named `<cluster>__<slug>.json`.
`python seo/build/build_pages.py` renders every file to `/<cluster-folder>/<slug>/index.html`.
The build fails on: missing fields, duplicate title/H1/URL, title > 70 chars, meta outside
80-165 chars, no FAQ block, no `answer`/`prose` block, fewer than ~450 words, or a banned claim
(certifications, client counts, percentages). Read `FACTS.md` before writing anything.

## Top-level fields

| field | required | notes |
|---|---|---|
| cluster | yes | one of: aura-business, hims, aurapacs, aura-learn, product-development, mobile-app-development, web-development, seo-services, resources, compare, case-studies |
| slug | yes | URL folder, lowercase-hyphen. `index` = the cluster hub page |
| title | yes | `<title>`, 50-70 chars, primary keyword first, ends with product or `Elevate Aura` |
| meta | yes | meta description, 120-160 chars, plain text, contains the primary keyword and a reason to click |
| h1 | yes | one H1. May wrap 2-4 words in `<span class="hl">…</span>` |
| crumb | yes | short breadcrumb label (2-5 words) |
| pill | no | small label above H1, e.g. `For diagnostic centres` |
| sub | yes | hero paragraph, 25-45 words, answers "what is this and for whom" |
| meta_ticks | no | 3 short trust ticks shown under the buttons |
| hero_image | no | `{ "src": "/assets/...", "alt": "...", "bar": "app.elevateaura.co.in/..." }` only use images that exist |
| cta_label / cta_href | no | override the primary button |
| demo_href / demo_label | no | override or `""` to hide the demo button |
| whatsapp_text | no | pre-filled WhatsApp message |
| cta_h2 / cta_p | no | closing CTA copy |
| schema | no | `SoftwareApplication`, `Service`, `Article` (default from cluster) |
| schema_name / service_type / area_served | no | schema details; `area_served` is a country name or list |
| date / modified | no | ISO dates for Article pages |
| primary_keyword | yes | the one query this page targets |
| secondary_keywords | yes | 3-8 close variants |
| intent | yes | `commercial`, `transactional`, `informational`, `comparison`, `local` |
| persona | yes | who searches, e.g. `Owner of a medical-equipment distribution business` |
| country | no | ISO code, default `IN`; `GLOBAL` for non-geo |
| city | no | city name for city pages |
| page_type | yes | `product`, `feature`, `application`, `industry`, `persona`, `problem`, `comparison`, `commercial`, `country`, `city`, `guide`, `case-study`, `hub` |
| phase | yes | 1-9 roadmap phase |
| sections | yes | ordered list of blocks (below) |

## Blocks (`sections[]`)

Every page (except hubs) must open with an `answer` block (2-3 short paragraphs that directly
answer the search query in plain, factual language) and must include a `faq` block (5-7
questions written the way buyers ask them). Typical commercial page order:
`answer, pains, flow, caps, usecases, who, compare, cases, faq, related`. Guides:
`answer, prose, prose, table?, faq, related`. Alternate tones are applied automatically.

- `answer`: `{ "type":"answer", "eyebrow":"In one sentence", "h2":"...", "paras":["...","..."] }`
- `prose`: `{ "type":"prose", "eyebrow":"...", "h2":"...", "lead":"...", "body":[ "para", {"h3":"..."}, {"ul":["..."]}, {"table":{"headers":[],"rows":[[]]}} ] }`
- `pains`: `{ "type":"pains", "eyebrow":"...", "h2":"...", "lead":"...", "items":[{"h":"...","p":"..."}] }` (4-6 items)
- `flow`: `{ "type":"flow", "eyebrow":"...", "h2":"...", "steps":[{"h":"...","p":"..."}] }` (4-7 steps)
- `caps`: `{ "type":"caps", "eyebrow":"...", "h2":"...", "groups":[{"icon":"&#128205;","h":"...","items":["..."]}], "more":{"href":"/modules.html","label":"See all 87 modules"} }`
- `split`: `{ "type":"split", "head_eyebrow":"...", "head_h2":"...", "image":{"src","alt","bar"}, "eyebrow":"...", "h2":"...", "ticks":["..."] }`
- `who`: `{ "type":"who", "eyebrow":"...", "h2":"...", "items":[{"icon":"&#127973;","b":"...","p":"..."}] }`
- `usecases`: `{ "type":"usecases", "eyebrow":"...", "h2":"...", "items":[{"h":"...","workflow":"...","result":"..."}] }`
- `why`: `{ "type":"why", "eyebrow":"...", "h2":"...", "items":[{"icon":"...","b":"...","p":"..."}] }`
- `compare`: `{ "type":"compare", "eyebrow":"...", "h2":"...", "cols":["Option A","Option B","Aura Business"], "rows":[["Capability","a","b","us"]] }` (last col is us)
- `table`: `{ "type":"table", "eyebrow":"...", "h2":"...", "headers":[...], "rows":[[...]] }`
- `faq`: `{ "type":"faq", "h2":"...", "items":[{"q":"...","a":"..."}] }` (also emits FAQPage schema; answers may contain `<a href>` links)
- `cases`: `{ "type":"cases", "which":[0,1] }` 0 Carna Medicare, 1 Medline Robotics, 2 exam-prep app. Only real projects.
- `related`: `{ "type":"related", "eyebrow":"...", "h2":"...", "items":[{"href":"/aura-business/.../","icon":"&#128205;","b":"...","p":"..."}] }` (4-6 links; every page must link up to its hub, sideways to 3+ siblings and, where relevant, to a guide/comparison/case study)
- `hubgrid` (hub pages): `{ "type":"hubgrid", "eyebrow":"...", "h2":"...", "items":[{"href":"...","b":"...","p":"..."}] }`

Inline HTML allowed inside strings: `<b>`, `<em>`, `<a href="...">`, `<span class="hl">`.
Use `&amp;` for ampersands in strings that will be rendered. Use real Unicode for ₹ and quotes.

## Writing rules

1. Answer the query in the first 80 words. No preamble.
2. Every claim must be backed by `FACTS.md`. No numbers, clients, certifications or prices
   beyond it. For countries/cities, say plainly that setup is remote and support is on
   WhatsApp, and that in-person work is Chennai (or Tamil Nadu by travel).
3. Unique angle per page: what the query needs that the sibling pages do not cover. Do not
   restate the hub page. Do not swap a city name into a template.
4. 600-1000 words of section content. Short paragraphs. Specific workflow language (job card,
   GRN, worklist, e-way bill, TPA claim) over adjectives.
5. Link out: hub, 3+ siblings, one guide or comparison, one case study where relevant. Use
   root-absolute URLs. Only link to URLs that exist in `seo/08-url-architecture.md` or the
   existing site.
6. FAQ answers 30-70 words, factual, no marketing filler.
7. British/Indian English, no em dashes, no exclamation marks.
