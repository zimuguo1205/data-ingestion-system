# Google Play: direct package test

Tested **28 September 2026, 07:44–07:46 UTC** (00:44–00:46 America/Los_Angeles). This is a focused follow-up using **Python `google-play-scraper==1.2.7`**, an **unofficial third-party library**, not Google's Android Publisher API. No additional sources were assessed.

## Recommendation

**Keep Google Play as the lead prototype candidate; do not fall back to Steam as primary.** The package successfully retrieved and paginated a meaningful cross-category sample without developer-account credentials. This materially improves on the previous nine-card webpage sample. The prior official-API authentication limitation does not establish that this third-party method is technically unusable.

The next gate is a bounded, multi-day freshness/reliability check and review of permitted use—not a claim that production ingestion is already validated. The stale-looking Duolingo window below is particularly important. Steam remains only a technical comparison baseline.

## Test and observed results

Each round requested two pages of 100 reviews per app using `Sort.NEWEST`, `lang='en'`, `country='us'`. Round two restarted from the first page, then followed its new continuation token. The harness waited 120 seconds after completing round one; per-app start-to-start intervals were 132–135 seconds.

| App / category | Round 1 → round 2 | Round 1 timestamp range (UTC dates) | Missing app version | Bodies under 10 characters | Developer replies |
|---|---|---|---|---|---|
| Duolingo / education | 200 → 200 | 31 Aug–10 Sep 2026 | 15/200 (7.5%) | 43/200 | 0/200 |
| Todoist / productivity | 200 → 200 | 29 Jun–26 Sep 2026 | 22/200 (11%) | 29/200 | 171/200 |
| Airbnb / travel | 200 → 200 | 20–27 Sep 2026 | 24/200 (12%) | 30/200 | 0/200 |

- **1,200 returned observations, 600 distinct app/review IDs**, not 1,200 unique reviews. Each app had 200 unique IDs in each round, with no duplicate IDs across its two pages.
- **12/12 review HTTP requests returned 200**; no recorded transport/parser errors, retries, login prompts or CAPTCHA responses. Measured request/response durations were 0.17–1.31 seconds, excluding the deliberate spacing.
- All 12 pages returned 100 records and a nonempty continuation token. This demonstrates two-page traversal, **not unlimited history or the validity of every later token**.
- All 600 IDs reappeared in the same order; body hashes, ratings, timestamps and reply hashes were unchanged. No newly observed IDs or edits appeared. This supports short-interval repeatability, **not proven new-review detection or long-term stability**.
- Every sampled row had an ID, nonempty body, rating from 1–5, and timestamp. Body-length medians were 26/52/38 characters, respectively; the observed maximum was 500. Short or low-information feedback will need quality handling.

## Fields and limitations

The package actually returned review ID, text, stars, `at`, helpful-vote count, version fields, author fields and developer-reply fields. Author names/images and review/reply bodies are omitted from committed evidence; IDs, lengths, hashes and selected metadata remain. This permits structural review, not independent semantic analysis of the withheld text.

Important distinctions from the earlier official-API comparison:

- This package sample did **not** provide the official API's device/OS metadata or an explicit `lastModified` field. Those official features must not be attributed to this collection method.
- The package derives `appVersion` and `reviewCreatedVersion` from the same response location; they are not two independent version measurements. Review timestamp creation/update semantics were not established.
- All sampled dates were descending, but Duolingo's newest returned date was **10 September**, about **17.5 days before collection**, despite `NEWEST`. Cause remains unknown: the test cannot distinguish filtering, endpoint behavior, caching, or another explanation. It does not prove there were no newer reviews on Google Play.
- English/US are request settings, not verified author language or residence. Three purposively selected apps and their recent sample windows cannot represent all categories, users or sentiment prevalence. No full-history, outage-recovery, sustained-load or multi-day test was performed.

## Method, maintenance and access caveats

The package's own review parsing and continuation handling were used. Instrumentation restored **TLS certificate verification** (v1.2.7 disables it on import), set a 25-second timeout, disabled retries, capped the test at 12 review requests, spaced requests by at least two seconds and logged exceptions that the package can otherwise swallow into empty/partial results. These are disclosed harness changes, not an unmodified out-of-the-box benchmark. No authentication, proxies, cookie replay, challenge solving or endpoint substitutions were used.

The library calls an undocumented Google Play `/_/PlayStoreUi/data/batchexecute` endpoint. The saved robots snapshot still disallows `/_`. Unlike the earlier page-only assessment, this explicitly requested diagnostic did call that route. Successful responses establish technical access, **not permission for ongoing collection, redistribution, commercial analysis or model training**. The package's MIT license does not grant rights to Google's service or review content; applicable terms/permissions remain a separate project decision. Stop on access restrictions; do not evade them.

Source checks: [package release and usage](https://pypi.org/project/google-play-scraper/1.2.7/), [maintainer repository](https://github.com/JoMingyu/google-play-scraper), [Google robots rules](https://play.google.com/robots.txt), [Google terms](https://policies.google.com/terms). Installed transport/review-source hashes are recorded in the evidence because repository code can change independently of a release.

## Evidence and reproduction

- [Machine-readable results](evidence/google-play-package-2026-09-28.json): request status/timing/hashes, robots snapshot, all returned IDs, page/app metrics, repeat comparisons and three minimized examples per page. Full per-record metadata was used for calculations; this compact export avoids repeating it 1,200 times.
- [Test harness](../../scripts/google_play_package_test.py), [pinned dependency](../../scripts/google-play-test-requirements.txt), [offline tests](../../scripts/test_google_play_package_test.py).

After reviewing the access caveats, reproduce in an isolated environment:

```sh
python3 -m venv .venv
.venv/bin/pip install -r scripts/google-play-test-requirements.txt
.venv/bin/python scripts/google_play_package_test.py --output /tmp/google-play-full.json
.venv/bin/python scripts/google_play_package_test.py --summarize /tmp/google-play-full.json --output /tmp/google-play-summary.json
python3 -m unittest discover -s scripts -p 'test_*.py'
```

Four offline checks passed: privacy/time normalization, missing/duplicate/invalid-value accounting, distinguishing new IDs from edits, and compact-evidence ID retention. No scheduled collector or production deployment was created.
