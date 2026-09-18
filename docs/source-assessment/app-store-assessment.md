# App Store source assessment

Assessment: 17 September 2026, America/Los_Angeles (machine logs use 18 September UTC). Scope: Google Play and Apple App Store only. Steam remains the technical baseline; Trustpilot is not selected, following project direction.

## Decision in brief

**Prefer Google Play for the next authorized pilot, not yet as an approved primary feed.** Its documented update timestamps and version/device context fit product-quality analysis. Both stores offer broader subject matter than Steam, but neither official API is an unrestricted feed of competitors' reviews. The decisive unresolved issue is access to a sufficiently varied, authorized app portfolio.

If the project requires arbitrary third-party apps, **neither source currently passes the ingestion gate**. Do not substitute an undocumented scraper for a supported access plan. Apple remains a useful alternative, particularly to investigate history; this assessment did not prove its authorized pagination or retention depth.

## What was actually tested

The same three apps were sampled in the US storefront: Duolingo (education), Todoist (productivity), and Airbnb (travel). These are purposive examples, not a representative market sample.

| Test | Direct observation | What it does not establish |
|---|---|---|
| Six public app landing pages | All returned HTTP 200; all exposed application/aggregate-rating JSON-LD | Permission for commercial harvesting; full review availability |
| Google visible review cards | Three cards per app: **9 distinct review IDs**, ratings 1–5, body lengths 369–499 characters, displayed dates from 18 March 2021 to 9 September 2026 | Exhaustive history, chronological order, uncapped text, or representative sentiment |
| Repeat Google Duolingo page | After 3.74 seconds: same 3 IDs and body hashes | Long-running reliability or successful detection of newly arriving reviews |
| Apple JSON-LD extraction | App metadata, but **zero individual Review objects** found | Absence of reviews elsewhere on the page; an Apple review sample was not obtained |
| Official API requests without credentials | Google and Apple both returned **401**, with JSON errors retained | A valid credentialed request, ownership permission, pagination or full schema coverage |

The two initial metadata-only repeats had empty review sets; their zero overlap/new counts are **not evaluable as review-repeatability evidence**. A separate Google visible-card extraction provides the actual review sample. UI dates are not assumed to be creation or modification timestamps. Author names and review bodies are withheld; sample IDs, ratings, dates, lengths and hashes are retained. This supports structural checks, not independent semantic interpretation of withheld text.

Point-in-time aggregate counts were substantial: Google Duolingo 49,113,097; Todoist 304,765; Airbnb 1,964,306 (`ratingCount`). Apple reported 5,453,088; 128,981; 702,751 under `aggregateRating.reviewCount`. **These are aggregate rating counts, not an ingestible written-review inventory or daily arrival rate**; populations and storefront scopes are not directly comparable.

## Supported ingestion versus public-page access

| Dimension | Google Play official API — documentation, not authenticated test | Apple App Store Connect API — documentation, not authenticated test |
|---|---|---|
| Access scope | Authorized production apps; OAuth/service account and Play Console review permission | Apps accessible to the authenticated App Store Connect account; JWT authentication |
| Review fields | ID, text, stars, lastModified; optional language, app version, device/OS context and developer replies | ID, title, body, stars, createdDate, territory; optional developer response; version-specific listing exists |
| Pagination/history | Token pagination, up to 100/page; list includes reviews created/modified within the last week; older history requires owner-side Console export | Up to 200/page; next-page links; created-date/rating sorting and territory filters. No one-week window stated on this endpoint; unlimited history is **not proven** |
| Incremental design | Upsert by app + review ID, using lastModified with overlap; monitor missed runs before the one-week window expires | Upsert by app + review ID; overlap rereads/content hashes needed because documented review attributes lack a review-modified timestamp |
| Maintenance | Official interface preferable to changing HTML selectors; documented GET quota 200/hour/app | Official interface preferable to legacy RSS; authenticated rate/error behavior still needs testing |

Sources: [Google access/history guide](https://developers.google.com/android-publisher/reply-to-reviews), [Google review schema](https://developers.google.com/android-publisher/api-ref/rest/v3/reviews), [Google list method](https://developers.google.com/android-publisher/api-ref/rest/v3/reviews/list), [Apple customer reviews](https://developer.apple.com/documentation/appstoreconnectapi/customer-reviews), [Apple authentication](https://developer.apple.com/documentation/appstoreconnectapi), [Apple list method](https://developer.apple.com/documentation/appstoreconnectapi/get-v1-apps-_id_-customerreviews), [Apple attributes](https://developer.apple.com/documentation/appstoreconnectapi/customerreview/attributes-data.dictionary), [Apple version-specific reviews](https://developer.apple.com/documentation/appstoreconnectapi/get-v1-appstoreversions-_id_-customerreviews).

### Access restrictions observed

- The saved Google robots rules disallow `/_` and `/store/getreviews`. Source inspection of **google-play-scraper 1.2.7** showed that its review method uses `/_/PlayStoreUi/data/batchexecute`. That RPC was **not requested**. Only the public app landing pages were sampled. [Library source](https://github.com/JoMingyu/google-play-scraper/blob/master/google_play_scraper/constants/request.py)
- The saved `itunes.apple.com/robots.txt` disallows `/*/rss/*`. The RSS route was **not requested**; this supersedes the prior recommendation to build an RSS adapter. The successful 31 August RSS pull remains historical evidence, not current approval or a guaranteed feed.
- Apple Media Services terms contain restrictions on automated scraping/analysis and commercial use; Google's terms address automated access contrary to machine-readable rules. These are reasons to verify the applicable rights and developer agreements, not a legal conclusion that every authorized API use is forbidden. Public visibility and an open-source scraper license do not grant platform collection or model-training rights. [Apple terms, section F](https://www.apple.com/legal/internet-services/itunes/us/terms.html), [Google terms](https://policies.google.com/terms)

No CAPTCHA, login, or other restriction was bypassed. A robots exclusion is a recorded policy restriction, **not a claim that an HTTP request was blocked**. The six-page metadata probe was not a permission or commercial-use test; no ongoing collector is enabled.

## Analytical interpretation

The sampled categories support a broader product-analysis hypothesis than gaming alone: subscription friction, usability, release regressions and service experience could be compared across categories. Google version/device fields could help attribute complaints to releases or devices; Apple's territory field could support geographic comparisons. These are proposed uses, **not demonstrated business value or measured model performance**.

Important limits remain: app reviewers are self-selected; platform, language, prompts and featured-card ranking introduce bias. Nine page-selected cards cannot estimate sentiment prevalence. App-store reviews concern digital products; Airbnb app feedback is not a substitute for accommodation reviews. Stars are imperfect sentiment labels, and a multi-category authorized sample is necessary to realize the apparent breadth.

## Next decision gate

First confirm whether the team has authorized access to apps spanning multiple categories and permission for the intended storage/analysis. If yes, test Google Play with two pages per app, ID deduplication, missing-field rates, timestamp coverage, a later repeat and update detection; validate a historical export if backfill matters. Test Apple's equivalent only if that portfolio/access is available. No credentials should be committed to this repository.

If such access is unavailable, report the gap and agree on access or scope before implementation. Keep Steam as a technical benchmark, not an automatic analytical fallback. Do not restart a broad source search.

## Evidence and reproduction

- [Initial HTTP, robots and aggregate-metadata results](evidence/app-store-2026-09-17.json)
- [Google nine-review structural sample and short repeat](evidence/google-play-visible-sample-2026-09-17.json)
- [Bounded probe script](../../scripts/app_store_probe.py) — Python 3 standard library, no credentials/cookies/proxies/retries. This is a diagnostic, not a production collector.

The first run preceded the visible-card parser addition, so its JSON-LD-only output is preserved unchanged. Four extra single-page Google fetches were used to inspect the current HTML selectors before the recorded follow-up; no RPCs were called. Re-running accesses live sites: recheck applicable permission/terms first. The default probe performs metadata/API-boundary checks; `--google-page-only` repeats the bounded Google landing-page sample:

```sh
python3 scripts/app_store_probe.py --google-page-only --output /tmp/google-play-assessment.json
```

No scheduled ingestion or production implementation has begun.
