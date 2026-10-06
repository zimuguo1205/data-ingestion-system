# Google Play bounded multi-day test

**Status: in progress.** Observation window: **4–7 October 2026**, America/Los_Angeles. The four-day result is not yet available. [Daily log](evidence/google-play-multiday/README.md).

## Question and fixed scope

Does the same unofficial `google-play-scraper==1.2.7` collection observe new review IDs over several days, keep a reasonably fresh timestamp window, and avoid request or pagination inconsistencies? The September immediate-repeat result establishes neither arrival coverage nor long-term stability.

Keep Duolingo, Todoist and Airbnb. Add **Google Maps (`com.google.android.apps.maps`) as a high-volume Google Play app**, not a new review source: these are reviews of the Maps app, not business/place reviews from Maps. Its [public listing](https://play.google.com/store/apps/details?id=com.google.android.apps.maps&hl=en&gl=us) showed 19.5 million in the header review-count display when checked on 4 October. That aggregate is a selection signal, not a measured daily arrival rate. The baseline also returned 500 reviews spanning approximately 27 hours of displayed timestamps, making it a useful window-cap stress sample.

One retained observation per local day. On 6 October the user explicitly requested a replacement; the superseded early run is archived and excluded from daily comparisons. Same configuration every day: English/US, `NEWEST`, 100/page, up to five pages per app (500 reviews; 2,000 across all four). This extends the earlier two-page diagnostic to a five-page window; comparisons for this experiment start with the new 4 October baseline, not the differently sized September sample.

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

At 09:07, the schedule was active but no 5 October evidence file existed. This observation was started during the user's status check; it does **not** establish that the 09:00 scheduled wake executed successfully. A subsequent diagnostic found the saved next run was 09:00 UTC (02:00 PDT), rather than the intended 09:00 PDT. The collector's existing-date guard prevents a later wake from collecting again on a date already observed.

| App | First observed IDs | Repeated IDs | New IDs timestamped after prior newest | Newest timestamp movement |
|---|---:|---:|---:|---:|
| Duolingo | 499 | 1 | 0 | 0 hours |
| Todoist | 2 | 498 | 2 | 21.16 hours |
| Airbnb | 20 | 480 | 20 | 18.48 hours |
| Google Maps | 436 | 64 | 436 | 17.70 hours |

Maps, Airbnb and Todoist show new IDs with later timestamps. Maps retains only 64 IDs from yesterday's capped window; a full 24-hour interval may stress the 500-review cap more than this shortened interval. This is observed overlap, not proof of complete coverage. Their newest returned timestamps remain about 24–25 hours behind collection time.

Duolingo's 499 first-observed IDs have older timestamps than the unchanged newest review (10 September). They cannot be counted as 499 newly arriving reviews. This substantial window change with only one overlapping ID, alongside the persistent stale newest timestamp, is an unresolved collection/data inconsistency despite successful HTTP and within-page ordering checks. Keep it visible in the final assessment.

The four-day assessment remains in progress; these two observations do not yet establish long-term stability or a final source recommendation.

## Third retained observation: 6 October (replacement)

At the user's explicit request, a fresh collection **replaced** the early 02:01 PDT result for this date. The effective daily evidence is [2026-10-06.json](evidence/google-play-multiday/2026-10-06.json), collected **16:18:11–16:19:00 UTC (09:18:11–09:19:00 PDT)**, about 24.2 hours after the 5 October observation. It contains 500 unique IDs per app, 20/20 HTTP 200 responses, no recorded request errors, duplicate IDs or descending-timestamp violations. All four windows reached the five-page cap with continuation available.

The original 02:01–02:02 PDT output is preserved unchanged in [the superseded archive](evidence/google-play-multiday/superseded/2026-10-06T020122-PDT.json). It is **excluded** from the daily table and cumulative/prior-day comparisons, which use only retained daily observations. The replacement retained the identical app/query configuration. This is one expressly authorized exception to the normal one-attempt-per-date rule: 40 review requests actually occurred on 6 October (20 early plus 20 replacement), while only the replacement supplies today's 2,000 retained records. Neither run is hidden or presented as an automatic retry.

| App | First observed IDs | Repeated IDs | New IDs timestamped after prior newest | Newest timestamp movement |
|---|---:|---:|---:|---:|
| Duolingo | 499 | 1 | 37 | 393.27 hours |
| Todoist | 5 | 495 | 5 | 23.62 hours |
| Airbnb | 26 | 474 | 26 | 24.33 hours |
| Google Maps | 387 | 113 | 387 | 24.14 hours |

Counts were independently recomputed against the retained 4/5 October IDs. Repeated counts use all prior retained dates; immediate previous-day overlap is 1, 495, 473 and 111 respectively. Maps, Airbnb and Todoist again expose first-observed IDs with later timestamps. Their newest review ages were approximately 24.0, 24.6 and 25.6 hours respectively. Duolingo's newest timestamp is 27 September 05:47:29 UTC and still lags collection by 226.5 hours; its 499 first-observed IDs cannot be treated as a measured arrival count. Large changes among older returned IDs remain unresolved.

Scheduling history remains part of the evidence: the early heartbeat arrived at 09:00:39 UTC (02:00:39 PDT), seven hours before the requested time. A named-zone attempt still produced 02:00 PDT in the saved next-run state. The stored future schedule was then corrected to the verified 16:00 UTC equivalent for this fixed October window. The corrected daytime heartbeat arrived at 16:05:51 UTC (09:05:51 PDT) and reused the then-existing result without new requests; the later 09:18 replacement was separately requested by the user.

The intended final observation remains 7 October around 09:00 PDT, about 23.7 hours after this replacement rather than the previously projected 31-hour interval. Actual intervals must still be used in the final comparison. Complete coverage and the final source recommendation remain pending.

## Schedule and operating bounds

The requested follow-up time is **09:00 America/Los_Angeles**, through 7 October. The initial hour-only configuration was interpreted as UTC; the actual 6 October observation ran at 02:01 PDT. On 6 October the saved future schedule was corrected to the equivalent 16:00 UTC and its nominal local time verified as 09:00 PDT. The scheduler may add a few minutes of timing offset. The first observation was collected at 15:32 on 4 October; the original 4 October scheduled wake was set for 16:00 and would reuse that day's saved result. The script refuses collection outside 4–7 October and refuses to overwrite/retry an existing daily result. For the user-authorized 6 October replacement, the old result was first archived and its byte-for-byte integrity verified before releasing the daily file for exactly one fresh run; the guard itself was not changed. Missing dates stay missing; no synthetic backfills.

The local computer must remain on with the desktop app running and the workspace available for the scheduled runs. This is a local scheduled task, not a deployed cloud collector. See [official scheduled-task operating conditions](https://learn.chatgpt.com/docs/automations?surface=app). The OpenAI Docs guidance informed this local-execution constraint. If scheduling or publication fails, preserve evidence and disclose the gap; do not claim four successful observation days.

Requests are spaced by at least two seconds, limited to 20 review requests per observation and 25 seconds/request, with verified TLS and no retries, accounts, proxies or challenge handling. Stop collection on transport/parser/access errors and retain the partial run. The package is **unofficial**, and the previously documented Google robots/terms concerns remain; technical success is not permission for unrestricted production collection. No change in production status is implied by this experiment.

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
