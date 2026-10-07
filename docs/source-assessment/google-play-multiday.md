# Google Play bounded multi-day test

**Status: completed.** Observation window: **4–7 October 2026**, America/Los_Angeles. Four successful retained daily observations; no failed, partial or missed dates. [Daily log](evidence/google-play-multiday/README.md). The final comparison and conditional recommendation are below; collection ends with 7 October.

## Question and fixed scope

Does the same unofficial `google-play-scraper==1.2.7` collection observe new review IDs over several days, keep a reasonably fresh timestamp window, and avoid request or pagination inconsistencies? The September immediate-repeat result establishes neither arrival coverage nor long-term stability.

Keep Duolingo, Todoist and Airbnb. Add **Google Maps (`com.google.android.apps.maps`) as a high-volume Google Play app**, not a new review source: these are reviews of the Maps app, not business/place reviews from Maps. Its [public listing](https://play.google.com/store/apps/details?id=com.google.android.apps.maps&hl=en&gl=us) showed 19.5 million in the header review-count display when checked on 4 October. That aggregate is a selection signal, not a measured daily arrival rate. The baseline also returned 500 reviews spanning approximately 27 hours of displayed timestamps, making it a useful window-cap stress sample.

One retained observation per local day. On 6 October the user explicitly requested a replacement and then removal of the prior result; only the replacement is used in daily comparisons. Same configuration every day: English/US, `NEWEST`, 100/page, up to five pages per app (500 reviews; 2,000 across all four). This extends the earlier two-page diagnostic to a five-page window; comparisons for this experiment start with the new 4 October baseline, not the differently sized September sample.

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

At that stage, these two observations did not establish long-term stability or a final source recommendation.

## Third retained observation: 6 October (replacement)

At the user's explicit request, a fresh collection **replaced** the previous result for this date. The effective daily evidence is [2026-10-06.json](evidence/google-play-multiday/2026-10-06.json), collected **16:18:11–16:19:00 UTC (09:18:11–09:19:00 PDT)**, about 24.2 hours after the 5 October observation. It contains 500 unique IDs per app, 20/20 HTTP 200 responses, no recorded request errors, duplicate IDs or descending-timestamp violations. All four windows reached the five-page cap with continuation available.

Only the replacement supplies today's 2,000 retained records. The previous result and its archive were removed from the current repository files at the user's request; local temporary transfer copies were also deleted. The daily table and cumulative/prior-day comparisons use only the replacement for 6 October. The replacement retained the identical app/query configuration and was expressly authorized, rather than an automatic retry. Ordinary Git commits still retain historical versions; deleting current files does not erase Git history.

| App | First observed IDs | Repeated IDs | New IDs timestamped after prior newest | Newest timestamp movement |
|---|---:|---:|---:|---:|
| Duolingo | 499 | 1 | 37 | 393.27 hours |
| Todoist | 5 | 495 | 5 | 23.62 hours |
| Airbnb | 26 | 474 | 26 | 24.33 hours |
| Google Maps | 387 | 113 | 387 | 24.14 hours |

Counts were independently recomputed against the retained 4/5 October IDs. Repeated counts use all prior retained dates; immediate previous-day overlap is 1, 495, 473 and 111 respectively. Maps, Airbnb and Todoist again expose first-observed IDs with later timestamps. Their newest review ages were approximately 24.0, 24.6 and 25.6 hours respectively. Duolingo's newest timestamp is 27 September 05:47:29 UTC and still lags collection by 226.5 hours; its 499 first-observed IDs cannot be treated as a measured arrival count. Large changes among older returned IDs remain unresolved.

The stored future schedule was corrected to the verified 16:00 UTC equivalent of 09:00 PDT for this fixed October window. The corrected daytime heartbeat arrived at 16:05:51 UTC (09:05:51 PDT) and made no new requests; the later 09:18 replacement was separately requested by the user.

The final observation occurred on 7 October at 09:00 PDT, about 23.7 hours after this replacement. Actual intervals are used in the final comparison below; complete coverage remains unproven.

## Final observation and four-day decision

Collected **7 October, 16:00:16–16:01:07 UTC (09:00:16–09:01:07 PDT)** using the unchanged collector and configuration. [Final dated evidence](evidence/google-play-multiday/2026-10-07.json). The heartbeat woke a few minutes early; collection waited until 09:00 local time. All four retained dates completed: **8,000 sampled rows, 4,686 distinct app/review-ID pairs**, and **80/80 HTTP 200 responses in the retained runs**. Those request totals exclude the removed, superseded observation, not all requests ever made. No failed, partial or missed dates were found. Inter-observation start intervals were **17.59, 24.17 and 23.70 hours**; these are not three identical 24-hour periods.

Each app returned five pages of 100 unique IDs per date, with continuation still available. No recorded transport/parser errors, duplicate IDs, invalid scores, missing IDs/scores/timestamps, descending-timestamp violations or continuation-token cycles were detected. Source hashes matched across all retained runs. Independently recomputing cumulative first-seen/repeated counts and previous-day overlaps from the saved tuples matched the JSON comparisons. All eight offline tests passed. These checks establish short-window technical success, not long-term reliability or freshness for every app.

| App | First observed / repeated on 5, 6, 7 Oct | 7 Oct newest timestamp, UTC | 7 Oct movement / age | Interpretation |
|---|---|---|---|---|
| Duolingo | 499/1; 499/1; 496/4 | 27 Sep 06:45:12 | +0.96 h / 249.3 h | Large turnover of old IDs; unsuitable for claiming fresh arrivals |
| Todoist | 2/498; 5/495; 4/496 | 6 Oct 13:02:35 | +22.34 h / 27.0 h | Low volume, substantial overlap, steadily advancing timestamps |
| Airbnb | 20/480; 26/474; 29/471 | 6 Oct 15:30:29 | +23.80 h / 24.5 h | Moderate volume and consistently advancing timestamps |
| Google Maps | 436/64; 387/113; 283/217 | 6 Oct 15:58:30 | +23.70 h / 24.0 h | High-volume stress sample with overlap, but a capped window |

**New observations, not measured arrivals.** After the baseline, Todoist, Airbnb and Maps yielded 11, 75 and 1,106 first-observed IDs respectively; all had displayed timestamps later than the previous observation's newest. This supports recurring discovery of later-dated reviews, rather than merely identical immediate repeats. Duolingo yielded 1,494 first-observed IDs, but only 38 were later-dated by that test and its newest review remained over ten days old on 7 October. Its near-total older-ID turnover is an unresolved source/library sampling inconsistency, not a valid estimate of new reviews. HTTP success does not resolve it.

**Freshness and coverage limits.** The other three apps' newest returned reviews remained about 24–29 hours old throughout the experiment. This is observed lag in this method; its cause was not established. Do not promise real-time ingestion. Maps retained previous-day overlap of 64, 111 and 217 IDs, so the bounded no-overlap gap check was not triggered; cumulative repeats on 6 October were 113. However, every window hit the cap with more data available. Overlap is not evidence that all intervening reviews were captured, especially with delayed visibility or review edits. No overlap tuple showed a body/score or timestamp change, but this small window cannot rule out edits elsewhere. No query configuration or cap was increased during the test.

**Analytical tradeoff and recommendation.** Google Play remains the stronger **conditional prototype source**, rather than Steam as the default primary source: these observed apps span education, productivity, travel and navigation, while the collection successfully discovers later-dated reviews over multiple days. For a next-stage prototype, I would propose starting with **Airbnb and Todoist**, retain Maps as a volume/coverage stress case, and exclude Duolingo from freshness-sensitive analysis until its anomaly is understood. This is a recommendation for review, not a newly started collector or expanded source search.

The breadth is app-category breadth, not representative consumer/business feedback: the test is English/US, the Maps sample concerns the app rather than places, and an Airbnb app review is not necessarily a stay review. Maps also had 746 sampled rows under ten characters out of 2,000 repeated-inclusive rows (37.3%); row-level quality checks are needed before sentiment analysis. App versions and developer replies are optional/missing in parts of the samples. The minimized evidence stores hashes, not review bodies, so it cannot itself train a sentiment model. The unofficial third-party method and previously documented access/terms restrictions remain unresolved production considerations. **Approve a limited prototype only if delayed, non-exhaustive sampling is acceptable; do not approve production/completeness claims from this four-day test.**

The bounded test ends here. No collection after 7 October, backfill or additional source exploration is authorized. The scheduled follow-up is to be removed after this report and its evidence are published or a publication blocker is disclosed.

## Schedule and operating bounds

The requested follow-up time is **09:00 America/Los_Angeles**, through 7 October. The initial hour-only configuration was interpreted as UTC. On 6 October the saved future schedule was corrected to the equivalent 16:00 UTC and its nominal local time verified as 09:00 PDT. The scheduler may add a few minutes of timing offset. The first observation was collected at 15:32 on 4 October; the original 4 October scheduled wake was set for 16:00 and would reuse that day's saved result. The script refuses collection outside 4–7 October and refuses to overwrite/retry an existing daily result. Exactly one fresh 6 October replacement was explicitly authorized by the user; the guard itself was not changed. Missing dates stay missing; no synthetic backfills.

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

The final comparison above completes the bounded observation work. Supporting dated evidence and the daily table are retained for review. Do not select Steam automatically, broaden the source search or extend the window without direction.
