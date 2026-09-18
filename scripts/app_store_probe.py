#!/usr/bin/env python3
"""Bounded public-page assessment, not a review ingestion service. Stdlib only.

Fetches robots rules, three app landing pages per store, two unauthenticated
official API checks and one repeat landing-page request per store. Never calls
RSS or undocumented review RPCs. No credentials, cookies, retries or proxies.
Outputs derived metadata and hashes; omits review text and author identities.
"""
import argparse
import collections
import datetime as dt
import hashlib
import html as html_module
from html.parser import HTMLParser
import json
import re
from pathlib import Path
import time
import urllib.error
import urllib.request
import urllib.robotparser

UA = 'DataIngestionSourceAssessment/0.1 (+https://github.com/zimuguo1205/data-ingestion-system)'
APPS = [
    ('Duolingo', 'Education', 'com.duolingo', 'duolingo-language-lessons/id570060128'),
    ('Todoist', 'Productivity', 'com.todoist', 'todoist-to-do-list-calendar/id572688855'),
    ('Airbnb', 'Travel', 'com.airbnb.android', 'airbnb/id401626263'),
]

def utcnow():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def sha(value):
    return hashlib.sha256(value.encode() if isinstance(value, str) else value).hexdigest()

def fetch(url):
    meta = {'url': url, 'requested_at_utc': utcnow()}
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        try:
            response = urllib.request.urlopen(req, timeout=25)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            data = response.read(4_000_001)
            meta.update(status=response.code, final_url=response.geturl(),
                        content_type=response.headers.get('Content-Type'),
                        server_date=response.headers.get('Date'), bytes=len(data),
                        body_sha256=sha(data), truncated=len(data) > 4_000_000)
            return meta, data.decode('utf-8', errors='replace')
    except (urllib.error.URLError, TimeoutError) as error:
        meta['error'] = str(error)
        return meta, ''
    finally:
        time.sleep(1)

class JsonLd(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.buffer = []
        self.objects = []
        self.errors = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'script' and dict(attrs).get('type') == 'application/ld+json':
            self.active = True
            self.buffer = []

    def handle_data(self, data):
        if self.active:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if tag == 'script' and self.active:
            try:
                self.objects.append(json.loads(''.join(self.buffer)))
            except ValueError:
                self.errors += 1
            self.active = False

def nodes(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)

def google_page_reviews(html):
    """Small visible-card sample only; selectors observed on 2026-09-17.

    Never invokes the review RPC. Breakage returns zero records rather than
    inventing fields. Body text and reviewer names are never written to disk.
    """
    samples = []
    for match in re.finditer(r'<header\b[^>]*data-review-id="([^"]+)"(.*?)</header>\s*<div class="h3YV2d">(.*?)</div>', html, re.S):
        identity, header, raw_body = match.groups()
        rating = re.search(r'aria-label="Rated (\d) stars? out of five stars"', header)
        date = re.search(r'<span class="bp9Aid">(.*?)</span>', header, re.S)
        body = html_module.unescape(re.sub('<[^>]+>', '', raw_body))
        samples.append({'review_id': identity, 'rating': int(rating.group(1)) if rating else None,
                        'displayed_date': html_module.unescape(date.group(1)) if date else None,
                        'date_semantics': 'UI date; creation versus update not established',
                        'body_characters': len(body), 'body_sha256': sha(body),
                        'body_withheld': True, 'author_withheld': True})
    return samples

def summarize(html):
    parser = JsonLd()
    parser.feed(html)
    all_nodes = list(nodes(parser.objects))
    reviews = [n for n in all_nodes if n.get('@type') == 'Review']
    apps = [n for n in all_nodes if n.get('@type') in ('SoftwareApplication', 'MobileApplication')]
    samples = []
    for review in reviews:
        body = review.get('reviewBody', review.get('description', '')) or ''
        identity = review.get('@id', review.get('identifier'))
        rating = review.get('reviewRating', {}).get('ratingValue')
        samples.append({
            'body_sha256': sha(body), 'body_characters': len(body),
            'rating': rating, 'datePublished': review.get('datePublished'),
            'dateModified': review.get('dateModified'),
            'stable_id_present_in_jsonld': bool(identity),
            'review_fields': sorted(review),
        })
    return {
        'jsonld_parse_errors': parser.errors,
        'app_metadata': [{k: a.get(k) for k in ('name', 'applicationCategory', 'aggregateRating')} for a in apps],
        'review_count_in_jsonld': len(reviews),
        'reviews': samples,
        'google_visible_card_sample': google_page_reviews(html),
        'rating_distribution': dict(collections.Counter(str(r['rating']) for r in samples)),
        'note': 'Counts cover JSON-LD only; do not imply all page or store reviews.',
    }

def main():
    args = argparse.ArgumentParser()
    args.add_argument('--output', type=Path, required=True)
    args.add_argument('--google-page-only', action='store_true', help='Bounded follow-up: Google landing pages only, no API or Apple requests')
    options = args.parse_args()
    output = options.output
    report = {'started_at_utc': utcnow(), 'user_agent': UA, 'robots': [], 'pages': [], 'api_checks': [], 'repeats': []}
    robot_parsers = {}
    for host in ('play.google.com', 'itunes.apple.com', 'apps.apple.com'):
        if options.google_page_only and host != 'play.google.com':
            continue
        meta, body = fetch('https://' + host + '/robots.txt')
        meta['rules'] = body
        report['robots'].append(meta)
        rp = urllib.robotparser.RobotFileParser()
        rp.parse(body.splitlines())
        robot_parsers[host] = rp if meta.get('status') == 200 else None
    for name, category, package, apple_path in APPS:
        for store, url, host in (
            ('Google Play', f'https://play.google.com/store/apps/details?id={package}&hl=en&gl=us', 'play.google.com'),
            ('Apple App Store', f'https://apps.apple.com/us/app/{apple_path}', 'apps.apple.com'),
        ):
            if options.google_page_only and store != 'Google Play':
                continue
            rp = robot_parsers[host]
            if rp is None or not rp.can_fetch(UA, url):
                report['pages'].append({'app': name, 'store': store, 'url': url, 'skipped': 'robots denied or unavailable'})
                continue
            meta, html = fetch(url)
            meta.update(app=name, category_selected=category, store=store)
            if meta.get('status') == 200:
                meta['parsed'] = summarize(html)
            report['pages'].append(meta)
    for label, url in (
        ('Google official API, no OAuth', 'https://androidpublisher.googleapis.com/androidpublisher/v3/applications/com.duolingo/reviews?maxResults=2'),
        ('Apple official API, no JWT', 'https://api.appstoreconnect.apple.com/v1/apps/570060128/customerReviews?limit=2'),
    ):
        if options.google_page_only:
            continue
        meta, body = fetch(url)
        meta['label'] = label
        try:
            meta['response'] = json.loads(body)
        except ValueError:
            meta['response'] = 'Non-JSON response; body omitted'
        report['api_checks'].append(meta)
    for prior in report['pages'][:1 if options.google_page_only else 2]:
        if prior.get('status') != 200:
            continue
        meta, html = fetch(prior['url'])
        meta.update(app=prior['app'], store=prior['store'])
        if meta.get('status') == 200:
            meta['parsed'] = summarize(html)
            old = {r['body_sha256'] for r in prior['parsed']['reviews']}
            new = {r['body_sha256'] for r in meta['parsed']['reviews']}
            meta['body_hash_overlap'] = len(old & new)
            meta['new_body_hashes'] = len(new - old)
            meta['jsonld_comparison_evaluable'] = bool(old and new)
            old_cards = {r['review_id']: r['body_sha256'] for r in prior['parsed']['google_visible_card_sample']}
            new_cards = {r['review_id']: r['body_sha256'] for r in meta['parsed']['google_visible_card_sample']}
            meta['visible_card_comparison'] = {
                'evaluable': bool(old_cards and new_cards),
                'overlapping_ids': len(old_cards.keys() & new_cards.keys()),
                'new_ids': len(new_cards.keys() - old_cards.keys()),
                'changed_bodies': sum(old_cards[k] != new_cards[k] for k in old_cards.keys() & new_cards.keys()),
                'note': 'Short-interval landing-page repeat, not pagination or a freshness guarantee.'}
            meta['seconds_since_first_request'] = (dt.datetime.fromisoformat(meta['requested_at_utc']) - dt.datetime.fromisoformat(prior['requested_at_utc'])).total_seconds()
        report['repeats'].append(meta)
    report['skipped_collection_routes'] = [
        {'url': 'https://itunes.apple.com/us/rss/customerreviews/page=1/id=570060128/sortby=mostrecent/json', 'reason': 'robots: Disallow /*/rss/*; prior 2026-08-31 RSS results are historical only'},
        {'url': 'https://play.google.com/_/PlayStoreUi/data/batchexecute', 'reason': 'robots: Disallow /_; google-play-scraper 1.2.7 review request source uses this route'},
    ]
    report['finished_at_utc'] = utcnow()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    for p in report['pages']:
        print(p['store'], p['app'], p.get('status', p.get('skipped')), json.dumps(p.get('parsed', {})))
    print('API checks:', [(r['label'], r.get('status')) for r in report['api_checks']])
    print('Repeats:', [(r['store'], r.get('body_hash_overlap'), r.get('new_body_hashes')) for r in report['repeats']])

if __name__ == '__main__':
    main()
