# Live Review Source Assessment

Assessment date: 2026-08-31  
Original scope: organize the previously reviewed sources. Latest focused update: 28 September 2026, direct google-play-scraper package test only. Older tests below are historical, not newly rerun.

## Executive conclusion

**Current recommendation (2026-09-28): [read the direct Google Play package test](google-play-package-test.md).** Google Play is the lead prototype candidate: the unofficial third-party package retrieved 600 distinct reviews across three categories, with successful pagination and a matching short-interval repeat. This establishes more than the earlier public-page sample, but not multi-day reliability, freshness or permitted production use. Official-API ownership restrictions should not be confused with this unofficial method's observed technical access.

**Steam remains the technical baseline**, not the primary analytical recommendation. **Trustpilot is not selected**, following project direction on commercial and analytical fit.

**The Apple RSS adapter recommendation is withdrawn.** The 31 August sample remains historical evidence; the current robots rules disallow the RSS path, which was not requested again. Assess authorized App Store Connect access instead.

Amazon Reviews '23 remains useful as a static schema, load-test, and modeling fixture, but it does **not** meet the repeatable live-ingestion requirement.

## How conclusions are supported

Evidence labels used below:

- **Sample pull:** direct HTTP/API response was parsed and compared across pages.
- **Browser observation:** visible behavior was checked in an ordinary browser session.
- **Raw HTTP check:** a simple non-browser client recorded only the response status.
- **Documentation:** conclusion comes from the source's published documentation, not from a successful credentialed pull.

The latest machine-readable results are in [`evidence/google-play-package-2026-09-28.json`](evidence/google-play-package-2026-09-28.json). Historical summaries remain in [`evidence/sample-pull-summary.json`](evidence/sample-pull-summary.json), [`evidence/test-log.md`](evidence/test-log.md), and [`references.md`](references.md).

## Historical comparison (31 August tests; current dispositions noted)

| Source | Live and repeatable? | Pagination / history | Useful fields | Access and maintenance | Assessment |
|---|---|---|---|---|---|
| **Steam Reviews API** | **Yes — historical sample pull** | Cursor; up to 100/page in docs; recent or updated order | Stable review ID, text, created/updated time, positive/negative label, helpfulness, purchase/context flags | No credential needed in test; documented JSON endpoint | **Technical baseline only.** Gaming-domain bias limits broader analytical use. |
| **Apple App Store RSS** | **Historical sample succeeded; current route not retested** | Pages 1–10 returned 50 each; page 11 returned 400 in old test | Review ID, title/text, 1–5 rating, app version, timestamp, votes | Current robots rules disallow RSS; see new report | **Do not implement this adapter under assessed access.** Investigate authorized App Store Connect API. |
| **Mozilla Add-ons ratings API** | **Yes — sample pull** | Numbered pages; 5,829 text reviews for sampled add-on | ID, body, score, created time, version, reply flags | Public v5 endpoint worked; Mozilla warns v5 may change | **Stable-looking narrow fallback.** Good schema, limited to browser extensions. |
| **Trustpilot** | **Conditional — docs + access checks** | Official API documents `pageToken` | ID, stars, title/text, language, created/updated/experience time, verification and company reply | Browser page was visible; raw client and no-key API returned 403; official endpoint requires an API key | **Not selected**, following project direction on commercial and analytical fit. |
| **Yelp** | **Not suitable for full-review ingestion under tested access** | Browser UI shows large review sets; official review API advertises only excerpts | Rating/text/date are visible in UI; API schema is useful but limited | Browser page visible; raw client returned 403; official endpoint requires a qualifying plan and says it returns up to three excerpts | **Reject as primary source.** It does not provide a sustainable full-review feed under the assessed method. |
| **Google Play** | **Unofficial package: two successful collection rounds; official API still requires authorized access** | Package: two pages of 100 per app tested; full history unknown | Sampled package: ID, text, stars, timestamp, optional version/reply; no device/OS or explicit lastModified | 600 distinct reviews across three apps; short repeat matched; robots/terms and freshness caveats apply | **Lead prototype candidate.** See latest report; not yet a validated production feed. |
| **BoardGameGeek XML API2** | **Conditional — token required** | Docs describe paging; no-token test could not reach data | Ratings/comments plus game metadata | No-token request returned 401; application approval and Bearer token required; caching and traffic minimization requested | **Defer.** Test only after application approval and license review. |
| **GitHub Issues API** | **Yes — sample pull** | Link-header pagination; sort by update time; timestamps support incremental pulls | ID, title/body, labels, state, reactions, comments, created/updated time | Public repositories can be read without authentication; current sample contained many pull requests and required filtering | **Useful complementary feedback stream.** Broad software feedback, but not a star-review dataset and strongly technical. |
| **Hacker News API** | **Yes — sample pull** | `maxitem`, item IDs and `updates` support polling | ID, text, timestamp, type, parent/thread relationship | Official public API; docs currently state no rate limit | **Technically easy but not a review source.** Useful for community sentiment experiments, not the primary Phase I review feed. |
| **Amazon product pages** | **Page visible; sustainable programmatic ingestion not established** | “Most recent” view and review records observed; no supported public review pagination API identified | Rating, title/text, review date, verified-purchase/helpful signals visible | Browser and raw HTTP both loaded in this re-test, but method depends on page structure/session/locale; usage permission remains unresolved | **Do not implement yet.** First obtain explicit approval for the collection method and document applicable terms/robots behavior. Never work around login, CAPTCHA, or access controls. |
| **Amazon Reviews '23** | **No — static dataset** | Fixed May 1996–Sep 2023 snapshot | Rich review, rating, timestamp and product metadata | Easy to reproduce as a fixed corpus; no new reviews arrive | **Reference fixture only.** Useful for schema/performance/model work, not live ingestion. |

## Recommendation and proposed decision gate

1. Treat **Steam Reviews API** as the technical baseline, not the primary analytical corpus.
2. Do not pursue Trustpilot as primary. Treat the Google Play unofficial method and official API as distinct access paths; confirm permitted use before ongoing collection.
3. Follow the [package test](google-play-package-test.md) with bounded multi-day checks of freshness, failures, new IDs and edits, particularly the stale-looking Duolingo window.
4. Advance Google Play as the prototype candidate, not a proven production feed. No automatic fallback to Steam is justified by the current evidence.
5. Preserve the same minimization principle for all sources: retain only review and product/context fields needed for the project, and avoid unnecessary profile identifiers.

The revised recommendation weighs analytical breadth, permitted access and demonstrated repeatability separately. The package test now demonstrates paginated short-interval repeatability, but not a complete or continuously fresh feed.

## Screenshots

The screenshots show only publicly visible page state. They do not prove that automated extraction is permitted or stable.

- [`evidence/screenshots/amazon-review-page-access.svg`](evidence/screenshots/amazon-review-page-access.svg): Amazon “Most recent” customer-review page loaded; session-identifying header was cropped out.
- [`evidence/screenshots/trustpilot-public-page.svg`](evidence/screenshots/trustpilot-public-page.svg): Trustpilot public business-review page loaded in a browser, while the raw HTTP and no-key API checks returned 403.
- [`evidence/screenshots/yelp-review-page.svg`](evidence/screenshots/yelp-review-page.svg): Yelp business page showed rating and review volume in a browser, while a raw client request returned 403.

## What this assessment does not claim

- A successful browser visit does not authorize scraping.
- A documented endpoint was not marked “tested” unless a sample response was actually pulled.
- HTTP status checks are point-in-time observations, not guarantees of future access.
- No login, CAPTCHA, bot check, or other access restriction was bypassed.
- This is a technical source assessment, not legal advice; production collection still needs the project's normal usage-policy review.
