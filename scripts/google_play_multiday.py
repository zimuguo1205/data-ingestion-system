#!/usr/bin/env python3
"""One bounded daily observation, 4–7 October 2026, America/Los_Angeles.

Unofficial method. No retry, credentials, proxy or challenge bypass. The date
guard and exclusive output reservation prevent unattended duplicate runs.
"""
import argparse
from datetime import datetime, timezone
import importlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import ssl
import time
from urllib.error import HTTPError
from urllib.request import urlopen
from zoneinfo import ZoneInfo
from google_play_package_test import digest, minimize, summarize

APPS = [('com.duolingo', 'Duolingo'), ('com.todoist', 'Todoist'),
        ('com.airbnb.android', 'Airbnb'), ('com.google.android.apps.maps', 'Google Maps')]
START, END = '2026-10-04', '2026-10-07'
TZ = ZoneInfo('America/Los_Angeles')
ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'docs/source-assessment/evidence/google-play-multiday'
CONFIG = {'method': 'unofficial google-play-scraper', 'version': '1.2.7',
          'lang': 'en', 'country': 'us', 'sort': 'NEWEST', 'page_size': 100,
          'max_pages_per_app': 5, 'max_review_requests_per_run': 20,
          'minimum_spacing_seconds': 2, 'retries': 0, 'timeout_seconds': 25,
          'tls_verification': True, 'timezone': 'America/Los_Angeles'}
FIELDS = ['review_id', 'at_utc', 'body_sha256', 'score', 'reply_sha256']


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def changes(records, previous, seen, prior_exists, fetched_at):
    """New means first seen by THIS experiment, not necessarily newly posted."""
    current = {r[0]: r for r in records if r[0]}
    prev = {r[0]: r for r in previous if r[0]}
    dates = [r[1] for r in current.values() if r[1]]
    old_dates = [r[1] for r in prev.values() if r[1]]
    newest, old_newest = max(dates, default=None), max(old_dates, default=None)
    common = current.keys() & prev.keys()
    new_ids = current.keys()-seen
    return {'baseline': not prior_exists,
            'newly_observed': len(new_ids) if prior_exists else None,
            'repeated_from_any_prior_day': len(current.keys() & seen) if prior_exists else None,
            'overlap_previous_run': len(common) if prior_exists else None,
            'changed_body_or_score': sum(current[k][2:4] != prev[k][2:4] for k in common) if prior_exists else None,
            'changed_timestamp': sum(current[k][1] != prev[k][1] for k in common) if prior_exists else None,
            'new_ids_with_at_after_prior_newest': sum(bool(current[k][1] and old_newest and current[k][1] > old_newest) for k in new_ids) if old_newest else None,
            'newest_at_utc': newest, 'previous_newest_at_utc': old_newest,
            'newest_moved_seconds': (datetime.fromisoformat(newest)-datetime.fromisoformat(old_newest)).total_seconds() if newest and old_newest else None,
            'newest_age_hours': (datetime.fromisoformat(fetched_at)-datetime.fromisoformat(newest)).total_seconds()/3600 if newest else None,
            'oldest_at_utc': min(dates, default=None),
            'note': 'Counts are observed IDs, not a complete arrival rate. at creation/update semantics are unverified.'}


def daily_history(folder, date):
    history = []
    for path in sorted(folder.glob('2026-10-*.json')):
        if START <= path.stem < date:
            history.append(json.loads(path.read_text()))
    return history


def table(folder):
    reports = [json.loads(p.read_text()) for p in sorted(folder.glob('2026-10-*.json'))]
    lines = ['# Daily observation log', '', 'Times and review timestamps below are UTC. First-day records are baseline, not newly arrived reviews.', '',
             '| Local date | App | Unique IDs | First observed | Repeated | Newest timestamp | Movement (hours) | Status / coverage |',
             '|---|---|---:|---:|---:|---|---:|---|']
    for report in reports:
        for app in report['apps']:
            c = app.get('comparison', {})
            val = lambda key: str(c[key]) if c.get(key) is not None else 'baseline / unavailable'
            movement = c.get('newest_moved_seconds')
            lines.append('| '+ ' | '.join([report['local_date'], app['name'], str(app.get('summary', {}).get('unique_ids', 0)),
                         val('newly_observed'), val('repeated_from_any_prior_day'), c.get('newest_at_utc') or 'unavailable',
                         str(round(movement/3600, 2)) if movement is not None else '—',
                         app['status']+'; '+app.get('coverage', 'not evaluated')])+' |')
    lines += ['', 'A missing date is a missed observation, not zero arrivals. Errors/HTTP traces and minimized record IDs/hashes are retained in each dated JSON.', '']
    (folder/'README.md').write_text('\n'.join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--summarize-only', action='store_true', help='Rebuild the log without network calls')
    args = parser.parse_args()
    if args.summarize_only:
        table(RESULTS)
        return
    date = datetime.now(TZ).date().isoformat()
    if not START <= date <= END:
        raise SystemExit('Outside the authorized four-day window; no collection.')
    RESULTS.mkdir(parents=True, exist_ok=True)
    output = RESULTS/(date+'.json')
    if output.exists():
        table(RESULTS)
        print('Observation already exists for '+date+'; no network calls.')
        return
    os.environ['TZ'] = 'UTC'
    time.tzset()
    from google_play_scraper import reviews, Sort
    transport = importlib.import_module('google_play_scraper.utils.request')
    feature = importlib.import_module('google_play_scraper.features.reviews')
    ssl._create_default_https_context = ssl.create_default_context
    if version('google-play-scraper') != CONFIG['version']:
        raise SystemExit('Unexpected package version; do not silently change experiment configuration.')
    transport.MAX_RETRIES = 1
    history = daily_history(RESULTS, date)
    if any(r['config'] != CONFIG for r in history):
        raise SystemExit('Configuration mismatch with prior observations.')
    report = {'local_date': date, 'started_at_utc': utcnow(), 'config': CONFIG,
              'record_columns': FIELDS, 'status': 'running', 'http': [], 'errors': [], 'apps': [],
              'source_sha256': digest(Path(__file__).read_bytes()),
              'previous_observation_dates': [r['local_date'] for r in history]}
    # Reserve the date before any request. An interrupted run is not silently rerun.
    with output.open('x') as file:
        json.dump(report, file)
    stopped, last_end = False, 0

    def save():
        temp = output.with_suffix('.json.tmp')
        temp.write_text(json.dumps(report, separators=(',', ':'), ensure_ascii=False)+'\n')
        temp.replace(output)

    def observed(request):
        nonlocal stopped, last_end
        if stopped or len(report['http']) >= CONFIG['max_review_requests_per_run']:
            raise RuntimeError('Stopped or at hard request cap')
        time.sleep(max(0, CONFIG['minimum_spacing_seconds']-(time.monotonic()-last_end)))
        start = time.monotonic()
        event = {'requested_at_utc': utcnow(), 'url': request.full_url, 'method': request.get_method()}
        try:
            with urlopen(request, timeout=25, context=ssl.create_default_context()) as response:
                body = response.read(5_000_001)
                event.update(status=response.status, bytes=len(body), body_sha256=digest(body), content_type=response.headers.get('Content-Type'))
            text = body.decode('utf-8')
            if len(body)>5_000_000 or 'text/html' in (event['content_type'] or '') or 'PlayGatewayError' in text:
                raise RuntimeError('Unexpected/oversize/challenge response; no bypass')
            return text
        except Exception as error:
            stopped = True
            event['error'] = type(error).__name__+': '+str(error)
            if isinstance(error, HTTPError):
                event['status'] = error.code
            raise
        finally:
            last_end = time.monotonic()
            event['seconds'] = round(last_end-start, 4)
            report['http'].append(event)

    transport._urlopen = observed
    original = feature._fetch_review_items

    def traced_fetch(*pos, **kw):
        nonlocal stopped
        try:
            return original(*pos, **kw)
        except Exception as error:
            stopped = True
            report['errors'].append({'at_utc': utcnow(), 'type': type(error).__name__, 'message': str(error)})
            raise

    feature._fetch_review_items = traced_fetch
    try:
        for package, name in APPS:
            app = {'package': package, 'name': name, 'status': 'skipped' if stopped else 'running', 'records': [], 'pages': []}
            report['apps'].append(app)
            if stopped:
                continue
            rows, token, tokens = [], None, set()
            for page in range(1, 6):
                first_http = len(report['http'])
                result, token = reviews(package, lang='en', country='us', sort=Sort.NEWEST, count=100, continuation_token=token)
                minimal = [minimize(r) for r in result]
                rows.extend(minimal)
                token_hash = digest(token.token) if isinstance(token.token, str) else None
                app['pages'].append({'page': page, 'count': len(result), 'continuation_present': bool(token.token),
                                     'continuation_sha256': token_hash, 'http_indices': list(range(first_http, len(report['http'])))})
                app['records'] = [[r[k] for k in FIELDS] for r in rows]
                save()
                if token_hash and token_hash in tokens:
                    app['token_cycle'] = True
                    break
                tokens.add(token_hash)
                if stopped or not token.token:
                    break
            app['status'] = 'failed' if stopped else 'inconsistent' if app.get('token_cycle') else 'ok'
            app['summary'] = summarize(rows)
            if app['summary']['duplicate_ids'] or not app['summary']['timestamps_descending'] or app['summary']['missing']['review_id']:
                app['status'] = 'inconsistent' if not stopped else 'failed'
            previous_apps = [a for run in history for a in run['apps'] if a['package']==package and a.get('records')]
            previous = previous_apps[-1]['records'] if previous_apps else []
            seen = {r[0] for a in previous_apps for r in a['records'] if r[0]}
            app['comparison'] = changes(app['records'], previous, seen, bool(previous_apps), utcnow())
            capped = len(app['pages'])==5 and bool(token.token)
            app['cap_reached_with_more_available'] = capped
            app['coverage'] = ('baseline; full history not tested' if not previous_apps else
                               'possible gap: capped without prior-ID overlap' if capped and not app['comparison']['overlap_previous_run'] else
                               'prior IDs overlap; completeness not proven' if app['comparison']['overlap_previous_run'] else
                               'no prior-ID overlap; inspect window and errors')
            if app['status'] != 'ok':
                app['coverage'] = 'partial/inconsistent observation; do not infer zero arrivals'
            save()
            print(json.dumps({'app': name, 'status': app['status'], 'count': app['summary']['unique_ids'], 'comparison': app['comparison']}), flush=True)
        report['status'] = 'complete' if all(a['status']=='ok' for a in report['apps']) else 'partial'
    except Exception as error:
        report['status'] = 'failed'
        report['errors'].append({'at_utc': utcnow(), 'type': type(error).__name__, 'message': str(error)})
    finally:
        report['finished_at_utc'] = utcnow()
        save()
        table(RESULTS)
    print('Saved', output, report['status'], flush=True)


if __name__ == '__main__':
    main()
