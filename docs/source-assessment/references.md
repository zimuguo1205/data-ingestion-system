# Documentation References

Links were checked on 2026-08-31. “Official” means published by the platform or API owner; it does not imply that every public webpage is licensed for automated extraction.

## Steam

- [Steamworks: User Reviews — Get List](https://partner.steamgames.com/doc/store/getreviews) — documents `recent`/`updated` ordering, URL-encoded cursors, up to 100 reviews per request, IDs, text, timestamps, recommendation label and other fields.

## Apple

- [Observed App Store customer-review RSS endpoint](https://itunes.apple.com/us/rss/customerreviews/page=1/id=389801252/sortby=mostrecent/json) — direct sample source used in this assessment.
- [Apple: List all customer reviews for an app](https://developer.apple.com/documentation/appstoreconnectapi/get-v1-apps-_id_-customerreviews) — official App Store Connect API for an app available to the authenticated developer account; it is not evidence of arbitrary cross-app access.

The public RSS endpoint worked in the sample, but a clear current Apple specification for this legacy public surface was not identified. This is why the report assigns it higher maintenance risk than Steam.

## Mozilla

- [Mozilla Add-ons Server: Ratings API](https://mozilla.github.io/addons-server/topics/api/ratings.html) — documents list filtering and numbered pages and warns that v5 is not frozen.
- [Mozilla Add-ons Server: API overview/versioning](https://mozilla.github.io/addons-server/topics/api/overview.html) — explains available API versions.

## Trustpilot

- [Trustpilot Business Units API](https://developers.trustpilot.com/business-units-api/) — documents the API-key-authenticated `all-reviews` endpoint, `pageToken` pagination and review response fields.
- [Trustpilot Data Solutions API](https://developers.trustpilot.com/data-solutions-api/) — documents licensed data access options and token/date-based retrieval.

## Yelp

- [Yelp Fusion: Reviews endpoint](https://docs.developer.yelp.com/reference/v3_business_reviews) — states that the endpoint returns up to three review excerpts and requires an eligible plan.
- [Yelp Places API FAQ](https://docs.developer.yelp.com/docs/places-faq) — product/access guidance, including review-text and caching limitations.

## Google Play

- [Google Play Developer API: `reviews.list`](https://developers.google.com/android-publisher/api-ref/rest/v3/reviews/list) — documents token/start-index pagination and requires the `androidpublisher` OAuth scope.
- [Google Play: Reply to reviews](https://developers.google.com/android-publisher/reply-to-reviews) — describes publisher review access and operational limitations.

## BoardGameGeek

- [BoardGameGeek: Using the XML API](https://boardgamegeek.com/using_the_xml_api) — requires approved application registration and Bearer tokens; asks clients to cache and minimize traffic.
- [BoardGameGeek XML API2 reference](https://boardgamegeek.com/wiki/page/BGG_XML_API2) — endpoint and pagination parameters.

## GitHub

- [GitHub REST API: Issues endpoints](https://docs.github.com/en/rest/issues/issues) — public repository reads, filters, fields and the need to distinguish pull requests returned by issue endpoints.
- [GitHub REST API pagination](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api) — Link-header pagination.
- [GitHub REST API rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api) — authenticated and unauthenticated limits.

## Hacker News

- [Official Hacker News API](https://github.com/HackerNews/API) — item schema, `maxitem`, `updates`, versioning and current rate-limit statement.

## Amazon

- [Amazon Reviews '23](https://amazon-reviews-2023.github.io/main.html) — static corpus with 571.54 million reviews across 33 domains, covering May 1996 through September 2023.
- [Observed Amazon customer-review page](https://www.amazon.com/product-reviews/B09B8V1LZ3/?sortBy=recent) — browser/raw-HTTP feasibility check only; not an API or permission statement.

No supported, general-purpose public Amazon customer-review API was identified in this assessment. Before any direct page automation, confirm the current applicable Amazon terms, robots rules and project authorization. The assessment intentionally did not attempt to bypass access controls.
