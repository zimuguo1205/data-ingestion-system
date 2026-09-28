#!/usr/bin/env python3
"""Bounded, explicitly requested evaluation of an UNOFFICIAL collection method.

Not a production collector or a permission determination. No accounts, proxies,
CAPTCHA handling, cookie replay or retries. Uses package pagination/parsing;
transport instrumentation retains TLS verification and records swallowed errors.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import ssl
import time
from urllib.error import HTTPError
from urllib.request import urlopen

APPS = [('com.duolingo', 'Education'), ('com.todoist', 'Productivity'),
        ('com.airbnb.android', 'Travel')]


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(value):
    if isinstance(value, str):
        value = value.encode('utf-8')
    return hashlib.sha256(value).hexdigest()


def iso(value):
    return value.replace(tzinfo=timezone.utc).isoformat() if value else None


def minimize(row):
    body = row.get('content') or ''
    reply = row.get('replyContent')
    return {'review_id': row.get('reviewId'), 'score': row.get('score'),
            'at_utc': iso(row.get('at')), 'body_characters': len(body),
            'body_sha256': digest(body), 'thumbs_up': row.get('thumbsUpCount'),
            'review_created_version': row.get('reviewCreatedVersion'),
            'app_version': row.get('appVersion'), 'reply_present': bool(reply),
            'reply_sha256': digest(reply) if reply else None,
            'replied_at_utc': iso(row.get('repliedAt')),
            'package_fields': sorted(row)}


def summarize(rows):
    ids = [r['review_id'] for r in rows]
    dates = [r['at_utc'] for r in rows if r['at_utc']]
    sizes = sorted(r['body_characters'] for r in rows)
    fields = ['review_id', 'score', 'at_utc', 'app_version', 'review_created_version', 'replied_at_utc']
    return {'rows': len(rows), 'unique_ids': len(set(ids) - {None}),
            'duplicate_ids': len(ids) - len(set(ids)),
            'missing': {k: sum(r[k] in (None, '') for r in rows) for k in fields},
            'empty_bodies': sum(r['body_characters'] == 0 for r in rows),
            'short_bodies_under_10_chars': sum(r['body_characters'] < 10 for r in rows),
            'invalid_scores': sum(r['score'] not in range(1, 6) for r in rows),
            'score_distribution': dict(Counter(r['score'] for r in rows)),
            'oldest_at_utc': min(dates) if dates else None,
            'newest_at_utc': max(dates) if dates else None,
            'timestamps_descending': dates == sorted(dates, reverse=True),
            'body_length_min': sizes[0] if sizes else None,
            'body_length_median': sizes[len(sizes)//2] if sizes else None,
            'body_length_max': sizes[-1] if sizes else None,
            'developer_replies': sum(r['reply_present'] for r in rows)}


def compare(before, after):
    a = {r['review_id']: r for r in before if r['review_id']}
    b = {r['review_id']: r for r in after if r['review_id']}
    common = a.keys() & b.keys()
    return {'overlap_ids': len(common), 'new_to_sample_ids': sorted(b.keys()-a.keys()),
            'absent_from_repeat_ids': sorted(a.keys()-b.keys()),
            'jaccard': len(common)/len(a.keys() | b.keys()) if a or b else None,
            'same_order': list(a) == list(b),
            'changed_body_ids': sorted(k for k in common if a[k]['body_sha256'] != b[k]['body_sha256']),
            'changed_score_ids': sorted(k for k in common if a[k]['score'] != b[k]['score']),
            'changed_timestamp_ids': sorted(k for k in common if a[k]['at_utc'] != b[k]['at_utc']),
            'changed_reply_ids': sorted(k for k in common if a[k]['reply_sha256'] != b[k]['reply_sha256'])}


def public_summary(report):
    """Retain IDs, metrics, HTTP provenance and three minimized examples/page.

    Full results remain reproducible with the normal probe command. Avoid
    repeating every per-record field across 1,200 observations in the repository.
    """
    compact = json.loads(json.dumps(report))
    compact['evidence_format'] = 'All returned IDs; three minimized examples per page; full-row hashes and summaries'
    compact['full_report_canonical_json_sha256'] = digest(json.dumps(report, sort_keys=True))
    for run in compact['rounds']:
        for app in run['apps']:
            app['summary'] = summarize([r for page in app['pages'] for r in page['rows']])
            for page in app['pages']:
                rows = page.pop('rows')
                page['summary'] = summarize(rows)
                page['review_ids'] = [r['review_id'] for r in rows]
                page['ordered_minimized_rows_sha256'] = digest(json.dumps(rows, sort_keys=True))
                page['sample_rows'] = rows[:3]
    return compact


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--repeat-gap-seconds', type=int, default=120)
    parser.add_argument('--summarize', type=Path, help='Produce compact public evidence from an existing full report; no network calls')
    args = parser.parse_args()
    if args.summarize:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(public_summary(json.loads(args.summarize.read_text())), indent=2, ensure_ascii=False)+'\n')
        return
    if not 30 <= args.repeat_gap_seconds <= 600:
        parser.error('repeat gap must be 30–600 seconds')
    # The library uses naive datetime.fromtimestamp; fix process timezone first.
    os.environ['TZ'] = 'UTC'
    time.tzset()
    from google_play_scraper import reviews, Sort
    transport = importlib.import_module('google_play_scraper.utils.request')
    feature = importlib.import_module('google_play_scraper.features.reviews')
    # v1.2.7 changes the global HTTPS context on import. Restore verification.
    ssl._create_default_https_context = ssl.create_default_context
    transport.MAX_RETRIES = 1
    report = {'started_at_utc': now(), 'method': 'UNOFFICIAL google-play-scraper Python package',
              'package_version': version('google-play-scraper'), 'python': platform.python_version(),
              'source_hashes': {label: digest(Path(module.__file__).read_bytes())
                                for label, module in [('transport', transport), ('reviews', feature)]},
              'config': {'lang': 'en', 'country': 'us', 'sort': 'NEWEST',
                         'apps': APPS, 'pages_per_app_per_round': 2, 'page_size': 100,
                         'rounds': 2, 'repeat_gap_seconds_after_round_one': args.repeat_gap_seconds,
                         'minimum_request_gap_seconds': 2, 'max_review_http_requests': 12,
                         'tls_verification': True, 'retries': 0, 'timeout_seconds': 25},
              'http': [], 'parser_errors': [], 'rounds': [], 'comparisons': []}
    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)

    def save():
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n')

    # Policy snapshot only; user's explicit test is not platform authorization.
    with urlopen('https://play.google.com/robots.txt', timeout=25,
                 context=ssl.create_default_context()) as response:
        body = response.read().decode()
        report['robots'] = {'url': response.url, 'status': response.status,
                            'retrieved_at_utc': now(), 'text': body, 'sha256': digest(body)}
    last_end = 0
    stopped = False

    def observed_urlopen(request):
        nonlocal last_end, stopped
        if stopped or len(report['http']) >= 12:
            raise RuntimeError('Stopped or diagnostic request budget exhausted')
        time.sleep(max(0, 2 - (time.monotonic()-last_end)))
        entry = {'requested_at_utc': now(), 'url': request.full_url,
                 'method': request.get_method(), 'request_bytes': len(request.data or b'')}
        started = time.monotonic()
        try:
            with urlopen(request, timeout=25, context=ssl.create_default_context()) as response:
                raw = response.read(5_000_001)
                entry.update(status=response.status, response_bytes=len(raw),
                             body_sha256=digest(raw), content_type=response.headers.get('Content-Type'))
                if len(raw) > 5_000_000:
                    raise RuntimeError('Response size cap exceeded')
                text = raw.decode('utf-8')
                if 'text/html' in (entry['content_type'] or '') or 'PlayGatewayError' in text:
                    raise RuntimeError('Unexpected HTML or gateway error; stopping, no bypass/retry')
                return text
        except Exception as error:
            stopped = True
            entry['error'] = type(error).__name__ + ': ' + str(error)
            if isinstance(error, HTTPError):
                entry['status'] = error.code
            raise
        finally:
            last_end = time.monotonic()
            entry['elapsed_seconds'] = round(last_end-started, 4)
            report['http'].append(entry)

    transport._urlopen = observed_urlopen
    original_fetch = feature._fetch_review_items

    def observed_fetch(*pos, **kw):
        try:
            return original_fetch(*pos, **kw)
        except Exception as error:
            report['parser_errors'].append({'at_utc': now(), 'type': type(error).__name__, 'message': str(error)})
            raise

    feature._fetch_review_items = observed_fetch
    for round_number in (1, 2):
        if stopped:
            break
        if round_number == 2:
            report['repeat_wait_started_at_utc'] = now()
            save()
            print('Waiting for bounded repeat; first-round evidence saved.', flush=True)
            deadline = time.monotonic()+args.repeat_gap_seconds
            while time.monotonic() < deadline:
                time.sleep(min(10, deadline-time.monotonic()))
        run = {'round': round_number, 'started_at_utc': now(), 'apps': []}
        report['rounds'].append(run)
        for app, category in APPS:
            if stopped:
                break
            result = {'app_id': app, 'category': category, 'started_at_utc': now(), 'pages': []}
            run['apps'].append(result)
            token, rows = None, []
            for page in (1, 2):
                if stopped:
                    break
                errors_before = len(report['parser_errors'])
                http_before = len(report['http'])
                fetched, token = reviews(app, lang='en', country='us', sort=Sort.NEWEST,
                                         count=100, continuation_token=token)
                minimal = [minimize(row) for row in fetched]
                page_meta = {'page': page, 'rows': minimal, 'fetched_at_utc': now(),
                             'returned_count': len(minimal), 'continuation_present': bool(token.token),
                             'continuation_sha256': digest(token.token) if isinstance(token.token, str) else None,
                             'http_request_indices': list(range(http_before, len(report['http']))),
                             'parser_error_count': len(report['parser_errors'])-errors_before}
                result['pages'].append(page_meta)
                rows.extend(minimal)
                save()
                if page_meta['parser_error_count'] or not token.token:
                    break
            result['summary'] = summarize(rows)
            result['finished_at_utc'] = now()
            print(json.dumps({'round': round_number, 'app': app, 'summary': result['summary']}), flush=True)
        run['finished_at_utc'] = now()
        save()
    if len(report['rounds']) == 2:
        first = {x['app_id']: x for x in report['rounds'][0]['apps']}
        for second in report['rounds'][1]['apps']:
            original = first[second['app_id']]
            a = [r for p in original['pages'] for r in p['rows']]
            b = [r for p in second['pages'] for r in p['rows']]
            comparison = compare(a, b)
            comparison.update(app_id=second['app_id'], start_to_start_seconds=(
                datetime.fromisoformat(second['started_at_utc'])-datetime.fromisoformat(original['started_at_utc'])).total_seconds())
            report['comparisons'].append(comparison)
    report['stopped_on_error'] = stopped
    report['finished_at_utc'] = now()
    save()
    print('Complete:', json.dumps(report['comparisons']), flush=True)


if __name__ == '__main__':
    main()
