# Google Play bounded multi-day test

**Status: in progress.** Observation window: **4–7 October 2026**, America/Los_Angeles. The four-day result is not yet available. [Daily log](evidence/google-play-multiday/README.md).

## Question and fixed scope

Does the same unofficial `google-play-scraper==1.2.7` collection observe new review IDs over several days, keep a reasonably fresh timestamp window, and avoid request or pagination inconsistencies? The September immediate-repeat result establishes neither arrival coverage nor long-term stability.

Keep Duolingo, Todoist and Airbnb. Add **Google Maps (`com.google.android.apps.maps`) as a high-volume Google Play app**, not a new review source: these are reviews of the Maps app, not business/place reviews from Maps. Its [public listing](https://play.google.com/store/apps/details?id=com.google.android.apps.maps&hl=en&gl=us) showed 19.5 million in the header review-count display when checked on 4 October. That aggregate is a selection signal, not a measured daily arrival rate. The baseline also returned 500 reviews spanning approximately 27 hours of displayed timestamps, making it a useful window-cap stress sample.

One observation per local day. Same configuration every day: English/US, `NEWEST`, 100/page, up to five pages per app (500 reviews; 2,000 across all four). This extends the earlier two-page diagnostic to a five-page window; comparisons for this experiment start with the new 4 October baseline, not the differently sized September sample.

## Measurements and interpretation

- **First observed:** ID not seen on any earlier day of this experiment. This is not necessarily a newly posted review. The first day's whole dataset is baseline; it is not counted as arrivals.
- **Repeated:** ID already observed on an earlier day. Track overlap with the immediately preceding available observation as well as the cumulative set. Compare body hashes/scores and timestamps for overlapping IDs.
- **Freshness:** newest timestamp, its movement versus the previous observation, age at fetch, and first-observed IDs whose timestamp exceeds the previous maximum. The package's `at` creation/update semantics remain unverified.
- **Reliability:** actual HTTP statuses and timings, parser/transport errors (including errors the library normally swallows), duplicate IDs, timestamp ordering and continuation-token cycles. Failed/partial/missed observations must never be presented as zero arrivals.
- **Keeping up:** if the five-page cap is reached without overlap with prior IDs, flag a **possible coverage gap**. Even overlap is not proof of exhaustive coverage. Do not silently increase the cap or change sampling settings mid-test. Explain any gaps in the final assessment.

Review IDs and minimized tuples of timestamp, body hash, score and reply hash are saved in each dated JSON so daily counts can be independently recomputed. No reviewer names/images or review/reply bodies are committed. The experiment does not estimate market-wide sentiment or measure model quality.

## Baseline: 4 October

Collected 22:32–22:33 UTC (15:32–15:33 PDT): **2,000 distinct app/review IDs**, 500 per app, 20/20 HTTP responses successful, no duplicate IDs or detected ordering errors. All four windows reached the five-page cap with more data available. This is only a successful first observation.

| App | Newest returned timestamp, UTC | Age at fetch |
|---|---|---:|
| Duolingo | 10 Sep 2026 20:31:09 | 578.0 hours |
| Todoist | 3 Oct 2026 17:54:53 | 28.6 hours |
| Airbnb | 3 Oct 2026 20:54:07 | 25.6 hours |
| Google Maps | 3 Oct 2026 22:26:13 | 24.1 hours |

The persistent Duolingo lag remains unresolved. Neither it nor the other apps' returned newest times should be assumed to reflect every review currently visible elsewhere on Google Play.

## Second observation: 5 October

Collected **16:07:54–16:08:41 UTC (09:07:54–09:08:41 PDT)**, about 17.6 hours after the baseline: 500 unique IDs per app, 20/20 HTTP 200 responses, no recorded request errors, duplicate IDs or descending-timestamp violations. [Dated evidence](evidence/google-play-multiday/2026-10-05.json) and the daily log retain the recomputable comparison.

At 09:07, the schedule was active but no 5 October evidence file existed. This observation was started during the user's status check; it does **not** establish that the 09:00 scheduled wake executed successfully. The reason for the missing scheduled observation has not been established. The collector's existing-date guard prevents a later wake from collecting again today.

| App | First observed IDs | Repeated IDs | New IDs timestamped after prior newest | Newest timestamp movement |
|---|---:|---:|---:|---:|
| Duolingo | 499 | 1 | 0 | 0 hours |
| Todoist | 2 | 498 | 2 | 21.16 hours |
| Airbnb | 20 | 480 | 20 | 18.48 hours |
| Google Maps | 436 | 64 | 436 | 17.70 hours |

Maps, Airbnb and Todoist show new IDs with later timestamps. Maps retains only 64 IDs from yesterday's capped window; a full 24-hour interval may stress the 500-review cap more than this shortened interval. This is observed overlap, not proof of complete coverage. Their newest returned timestamps remain about 24–25 hours behind collection time.

Duolingo's 499 first-observed IDs have older timestamps than the unchanged newest review (10 September). They cannot be counted as 499 newly arriving reviews. This substantial window change with only one overlapping ID, alongside the persistent stale newest timestamp, is an unresolved collection/data inconsistency despite successful HTTP and within-page ordering checks. Keep it visible in the final assessment.

The four-day assessment remains in progress; these two observations do not yet establish long-term stability or a final source recommendation.

## Schedule and operating bounds

Baseline ran on 4 October. Starting 5 October, the bounded follow-up in the same task is scheduled daily at **09:00 America/Los_Angeles**, through 7 October, moved earlier at the user's request. The first observation was collected at 15:32 on 4 October; the 4 October scheduled wake was set for 16:00 and would reuse that day's saved result. The script refuses collection outside 4–7 October and refuses to overwrite/retry an existing daily result. Missing dates stay missing; no synthetic backfills.

The local computer must remain on with the desktop app running and the workspace available for the scheduled runs. This is a local scheduled task, not a deployed cloud collector. See [official scheduled-task operating conditions](https://learn.chatgpt.com/docs/automations?surface=app). The OpenAI Docs guidance informed this local-execution constraint. If scheduling or publication fails, preserve evidence and disclose the gap; do not claim four successful observation days.

Requests are spaced by at least two seconds, limited to 20 review requests/day and 25 seconds/request, with verified TLS and no retries, accounts, proxies or challenge handling. Stop collection on transport/parser/access errors and retain the partial run. The package is **unofficial**, and the previously documented Google robots/terms concerns remain; technical success is not permission for unrestricted production collection. No change in production status is implied by this experiment.

## Reproduction and follow-up

- [Daily collector](../../scripts/google_play_multiday.py)
- [Offline comparison tests](../../scripts/test_google_play_multiday.py)
- [Pinned dependency](../../scripts/google-play-test-requirements.txt)
- [Baseline evidence](evidence/google-play-multiday/2026-10-04.json) and [running daily table](evidence/google-play-multiday/README.md)

From the repository, using the existing isolated environment:

```sh
../app-store-venv/bin/python scripts/google_play_multiday.py
python3 scripts/google_play_multiday.py --summarize-only
python3 -m unittest discover -s scripts -p 'test_*.py'
```

The first command performs today's bounded observation only if permitted by the date/idempotency guards. The latter two commands do not access Google Play. Eight offline tests passed at setup; invoking the collector again after today's result exists must produce no further network calls.

After the final scheduled day, append the actual multi-day comparison, missing/failed dates if any, freshness/window-cap findings and a recommendation here, publish supporting evidence to this repository, and send a concise summary. Do not select Steam automatically or broaden the source search. Do not extend the window without direction.
