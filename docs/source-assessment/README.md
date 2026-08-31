# Live Review Source Assessment

Assessment date: 2026-08-31  
Scope: organize the previously reviewed sources; no new sources were added.

## Executive conclusion

**Recommended Phase I pilot: Steam Reviews API.** It is the strongest immediately usable source because a live, unauthenticated sample pull succeeded; cursor pagination produced distinct pages; each review has stable IDs, creation/update timestamps, text, and an explicit positive/negative label; and the collection method is documented by Steam.

**Recommended secondary adapter: Apple App Store customer-review RSS.** It broadens the domain beyond games and has ratings, text, app version, IDs, and timestamps. The observed public feed is easy to ingest but only exposed a rolling 500-review window in this test, and it is less clearly documented than Steam. It should therefore be treated as a useful second source, not the sole long-history source.

**Conditional broader source: Trustpilot official API.** Its documented schema and pagination are attractive for business/service reviews, but the API requires a key and was not sample-tested with credentials. A public webpage being visible in a browser is not evidence that automated collection is supported. Do not select it until access and permitted use are confirmed and a credentialed sample pull succeeds.

Amazon Reviews '23 remains useful as a static schema, load-test, and modeling fixture, but it does **not** meet the repeatable live-ingestion requirement.

## How conclusions are supported

Evidence labels used below:

- **Sample pull:** direct HTTP/API response was parsed and compared across pages.
- **Browser observation:** visible behavior was checked in an ordinary browser session.
- **Raw HTTP check:** a simple non-browser client recorded only the response status.
- **Documentation:** conclusion comes from the source's published documentation, not from a successful credentialed pull.

The machine-readable summary is in [`evidence/sample-pull-summary.json`](evidence/sample-pull-summary.json), the detailed observations are in [`evidence/test-log.md`](evidence/test-log.md), and documentation links are in [`references.md`](references.md).

## Comparison

| Source | Live and repeatable? | Pagination / history | Useful fields | Access and maintenance | Assessment |
|---|---|---|---|---|---|
| **Steam Reviews API** | **Yes — sample pull** | Cursor; up to 100/page in docs; recent or updated order | Stable review ID, text, created/updated time, positive/negative label, helpfulness, purchase/context flags | No credential needed in test; documented JSON endpoint | **Best Phase I pilot.** High volume and clear incremental design; gaming-domain bias must be recorded. |
| **Apple App Store RSS** | **Yes — sample pull** | Pages 1–10 returned 50 each; page 11 returned 400 in test | Review ID, title/text, 1–5 rating, app version, timestamp, votes | Public feed worked, but this RSS surface is less clearly documented; observed window was about five days for a high-volume app | **Good secondary adapter.** Broad app categories, but recent-window depth and stability need monitoring. |
| **Mozilla Add-ons ratings API** | **Yes — sample pull** | Numbered pages; 5,829 text reviews for sampled add-on | ID, body, score, created time, version, reply flags | Public v5 endpoint worked; Mozilla warns v5 may change | **Stable-looking narrow fallback.** Good schema, limited to browser extensions. |
| **Trustpilot** | **Conditional — docs + access checks** | Official API documents `pageToken` | ID, stars, title/text, language, created/updated/experience time, verification and company reply | Browser page was visible; raw client and no-key API returned 403; official endpoint requires an API key | **Promising only after approved access.** Broader domain than Steam, but not yet proven by a credentialed pull. |
| **Yelp** | **Not suitable for full-review ingestion under tested access** | Browser UI shows large review sets; official review API advertises only excerpts | Rating/text/date are visible in UI; API schema is useful but limited | Browser page visible; raw client returned 403; official endpoint requires a qualifying plan and says it returns up to three excerpts | **Reject as primary source.** It does not provide a sustainable full-review feed under the assessed method. |
| **Google Play** | **Only for apps the account controls via official API** | Official API supports tokens/start index; public page is dynamic | Rating, text, device/app metadata, developer reply and timestamps in official API | Public page visible, but no supported general-public review API was identified; official API requires Android Publisher OAuth | **Reject for general cross-app ingestion.** Reconsider only for a developer-owned app portfolio. |
| **BoardGameGeek XML API2** | **Conditional — token required** | Docs describe paging; no-token test could not reach data | Ratings/comments plus game metadata | No-token request returned 401; application approval and Bearer token required; caching and traffic minimization requested | **Defer.** Test only after application approval and license review. |
| **GitHub Issues API** | **Yes — sample pull** | Link-header pagination; sort by update time; timestamps support incremental pulls | ID, title/body, labels, state, reactions, comments, created/updated time | Public repositories can be read without authentication; current sample contained many pull requests and required filtering | **Useful complementary feedback stream.** Broad software feedback, but not a star-review dataset and strongly technical. |
| **Hacker News API** | **Yes — sample pull** | `maxitem`, item IDs and `updates` support polling | ID, text, timestamp, type, parent/thread relationship | Official public API; docs currently state no rate limit | **Technically easy but not a review source.** Useful for community sentiment experiments, not the primary Phase I review feed. |
| **Amazon product pages** | **Page visible; sustainable programmatic ingestion not established** | “Most recent” view and review records observed; no supported public review pagination API identified | Rating, title/text, review date, verified-purchase/helpful signals visible | Browser and raw HTTP both loaded in this re-test, but method depends on page structure/session/locale; usage permission remains unresolved | **Do not implement yet.** First obtain explicit approval for the collection method and document applicable terms/robots behavior. Never work around login, CAPTCHA, or access controls. |
| **Amazon Reviews '23** | **No — static dataset** | Fixed May 1996–Sep 2023 snapshot | Rich review, rating, timestamp and product metadata | Easy to reproduce as a fixed corpus; no new reviews arrive | **Reference fixture only.** Useful for schema/performance/model work, not live ingestion. |

## Recommendation and proposed decision gate

1. Approve **Steam Reviews API** for the first automated ingestion module.
2. Implement incremental collection using the review ID plus both `timestamp_created` and `timestamp_updated`; persist the returned cursor only as a run checkpoint, not as the sole identity.
3. Store only the review and product/context fields needed for the project. Do not retain unnecessary profile identifiers from the nested author object.
4. Add a small **Apple App Store RSS** adapter after the Steam path works, so downstream sentiment analysis is not evaluated only on gaming language.
5. If a broader business/service source is important, request a Trustpilot API key and permission clarification, then rerun the same two-page sample test before revisiting the shortlist.

The recommendation is based on observed repeatability and field coverage, not just subject-matter fit. Steam's main weakness is representativeness: the gaming-specific population, vocabulary, review-bombing behavior, and binary recommendation label may not generalize to ordinary retail or service feedback. That bias should be tracked in downstream analysis.

## Screenshots

The screenshots show only publicly visible page state. They do not prove that automated extraction is permitted or stable.

- [`evidence/screenshots/amazon-review-page-access.jpg`](evidence/screenshots/amazon-review-page-access.jpg): Amazon “Most recent” customer-review page loaded; session-identifying header was cropped out.
- [`evidence/screenshots/trustpilot-public-page.jpg`](evidence/screenshots/trustpilot-public-page.jpg): Trustpilot public business-review page loaded in a browser, while the raw HTTP and no-key API checks returned 403.
- [`evidence/screenshots/yelp-review-page.jpg`](evidence/screenshots/yelp-review-page.jpg): Yelp business page showed rating and review volume in a browser, while a raw client request returned 403.

## What this assessment does not claim

- A successful browser visit does not authorize scraping.
- A documented endpoint was not marked “tested” unless a sample response was actually pulled.
- HTTP status checks are point-in-time observations, not guarantees of future access.
- No login, CAPTCHA, bot check, or other access restriction was bypassed.
- This is a technical source assessment, not legal advice; production collection still needs the project's normal usage-policy review.
