# Evidence and Test Log

Unless otherwise noted, tests were run from the same environment on 2026-08-31. Review text and user/profile identifiers are intentionally omitted from stored evidence.

## Direct sample pulls

### Steam Reviews API

Test target: Counter-Strike 2 (`appid=730`), English, most recent, all purchase/review types.

- Request 1: HTTP 200, five reviews, cursor returned.
- Request 2 using returned cursor: HTTP 200, five reviews.
- Review-ID overlap between pages: zero.
- Reported matching volume: 2,605,378 reviews.
- Five first-page creation times ranged from 2026-08-31T19:17:01Z to 2026-08-31T19:23:24Z.
- Observed top-level fields: `recommendationid`, `review`, `timestamp_created`, `timestamp_updated`, `voted_up`, vote counts, language, purchase/refund/free/early-access flags, reactions, comment count, author object, and application release date.

Interpretation: direct evidence supports live access, cursor repeatability, high volume, labels and incremental timestamps. The result does not establish cross-domain representativeness.

### Apple App Store customer-review RSS

Test target: Instagram, US storefront (`id=389801252`), most recent.

- Pages 1 and 2: HTTP 200, 50 entries each, zero ID overlap.
- Page 10: HTTP 200, 50 entries.
- Page 11: HTTP 400.
- Page 1 covered approximately 2026-08-29 18:43 to 2026-08-30 08:39 PDT.
- Page 10 covered approximately 2026-08-25 09:32 to 18:34 PDT.
- Fields observed: author, content, ID, content type, rating, app version, vote count/sum, link, title and updated timestamp.

Interpretation: live and easy to parse, but the tested high-volume app exposed a rolling 500-entry window covering roughly five days. Historical backfill depth should not be assumed beyond what was observed.

### Mozilla Add-ons ratings API

Test target: `ublock-origin`, text reviews only, five records per page.

- Pages 1 and 2: HTTP 200, five entries each, zero ID overlap.
- Endpoint reported 5,829 matching reviews.
- Fields observed: add-on, body, created, ID, deletion/developer-reply/latest flags, prior count, reply, score, user and version.

Interpretation: direct evidence supports public paging and rich labeled records. Mozilla's own v5 documentation warns that the API is not frozen and may change.

### GitHub Issues API

Test target: `microsoft/vscode`, all states, sorted by most recently updated, five records per page.

- Pages 1 and 2: HTTP 200, five returned objects each, Link headers included next/previous cursors.
- After filtering objects containing a `pull_request` key, only one item on page 1 and three on page 2 were issues.
- Remaining unauthenticated rate-limit header decreased from 59 to 58.
- Issue-ID overlap between pages: zero.

Interpretation: the endpoint is live and incrementally sortable, but the sample directly demonstrates the need to remove pull requests. The data is product feedback, not rating-labeled consumer reviews.

### Hacker News API

- `maxitem.json`: HTTP 200, value 49,514,931 at test time.
- `updates.json`: HTTP 200, 72 changed item IDs and 29 profile IDs.
- Five descending item IDs resolved to current comments with ID, author, parent, text, time and type fields.

Interpretation: repeatable near-real-time polling is straightforward, but records are discussion comments with no product-rating label.

## Access and browser observations

| Source/check | Result on 2026-08-31 | What it supports |
|---|---|---|
| Amazon review page, browser | Loaded; ten review elements; “Most recent” sort; displayed review dates from Aug 29–31, 2026 | Public page content can be visible in an ordinary session. It does not prove a supported collection contract. |
| Amazon review page, raw HTTP | HTTP 200 | A simple request was not blocked at that moment; stability is still unknown. |
| Trustpilot public page, browser | Loaded; Amazon profile displayed 48,820 reviews and 1.6 score | Reviews are publicly viewable in a normal browser. |
| Trustpilot public page, raw HTTP | HTTP 403 | A non-browser client did not receive the page, demonstrating method-dependent access. |
| Trustpilot official API, no key | HTTP 403 | A credential is required before a real API sample can be assessed. |
| Yelp public page, browser | Loaded; sampled business showed about 2.8k reviews | Reviews and volume are publicly viewable in the browser. |
| Yelp public page, raw HTTP | HTTP 403 | Direct page collection was blocked for the simple client. |
| Yelp official API, no authorization | HTTP 400 | No credentialed sample was performed; published access requirements govern feasibility. |
| Google Play public app page, raw HTTP | HTTP 200 | The public page is reachable, but this is not evidence of a supported general review feed. |
| BoardGameGeek XML API2, no token | HTTP 401 | Application registration/token is a real prerequisite. |

An earlier browser visit on 2026-08-30 encountered a transient Trustpilot “verifying connection” page; the 2026-08-31 browser re-test loaded normally. The report therefore treats access as variable rather than claiming the site is always blocked.

## Documentation-only conclusions

- Trustpilot's official Business Units API documents API-key authentication, `pageToken` pagination and review fields. No credentialed pull was available.
- Yelp's official review endpoint states that it returns up to three review excerpts and requires an eligible plan. No full-review feed was demonstrated.
- Google Play's official `reviews.list` method supports pagination but requires the Android Publisher OAuth scope; this is appropriate for publisher-controlled apps, not arbitrary public apps.
- BoardGameGeek requires an approved application and Bearer token and asks clients to cache responses and minimize traffic.
- Amazon Reviews '23 is a fixed research dataset ending in September 2023.

## Reproduction notes

- Use a descriptive User-Agent and conservative request rate.
- Fetch two pages and confirm zero stable-ID overlap before claiming pagination works.
- Record response status, returned count, pagination token/header, min/max timestamps and field names.
- Do not store review text or profile identifiers in assessment logs unless they are necessary to demonstrate a schema problem.
- Stop and record the result if login, CAPTCHA, verification, authorization or plan restrictions appear; do not work around them.
