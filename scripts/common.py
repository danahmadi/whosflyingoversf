"""Shared static-site data and HTML helpers. No network requests during a build."""
import csv
import hashlib
import html
import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import urlencode
from outbound import decorate_html

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
ORIGIN = 'https://whosflyingoversf.com'
REPO = 'https://github.com/danahmadi/whosflyingoversf'
REPORT = REPO + '/issues/new?template=sighting.yml'
e = html.escape


def json_text(value):
    # JSON is also embedded in script[type=application/json]. HTML still parses </script> there.
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')


def write(path, text):
    dest = SITE / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.suffix == '.html':
        text = decorate_html(text)
    dest.write_text(text, encoding='utf-8')


def date_label(value):
    return date.fromisoformat(value).strftime('%b %-d, %Y') if value else 'Date unconfirmed'


def report_url(day='', brand=''):
    return REPORT + '&' + urlencode({'date': day, 'brand': brand})


def load_data():
    brands = json.loads((ROOT / 'data/brands.json').read_text())
    brands = {k: dict(v, label=v.get('label', k)) for k, v in brands.items()}
    brands['Unknown'] = dict(label='Unidentified banner', url=None, logo=None, color='#666666', description='The source does not identify the advertiser.')
    def names(raw):
        result = []
        for part in raw.split(';'):
            match = next((k for k, v in brands.items() if v.get('match') and part.strip().startswith(v['match'])), 'Unknown')
            if match not in result: result.append(match)
        return result
    entries = {}
    with (ROOT / 'data/sightings.csv').open(newline='') as handle:
        rows = list(csv.DictReader(handle))
    excluded = 0
    for row in rows:
        if row['confidence'] == 'low' or row['location'] != 'sf':
            excluded += 1
            continue
        for brand in names(row['brand']):
            day = row['date_pt'] if row['date_precision'] == 'day' else ''
            source_identity = row['post_url'] or '|'.join(row[field] for field in ('source','posted_date_pt','brand','banner_text','notes'))
            key = (day, brand) if day else ('undated:' + source_identity, brand)
            identity = '|'.join(key)
            item = entries.setdefault(key, dict(id=hashlib.sha256(identity.encode()).hexdigest()[:12], date=day, brand=brand, texts=[], sources=[]))
            if row['banner_text'] and row['banner_text'].casefold() not in {text.casefold() for text in item['texts']}: item['texts'].append(row['banner_text'])
            item['sources'].append(dict(url=row['post_url'], source='Reader report' if row['source']=='Dan' else row['source'], author=row['author'], note=row['notes'], photo=row['has_image']=='yes', confidence=row['confidence'], posted=row['posted_date_pt']))
    entries = sorted(entries.values(), key=lambda x: (x['date'], x['brand']), reverse=True)
    by_day = defaultdict(list)
    for item in entries:
        if item['date'] and item['brand'] not in ('Unknown','Pylon','Vercel','HappyRobot'): by_day[item['date']].append(item['brand'])
    flights = []
    for original in json.loads((ROOT / 'data/flights.json').read_text()):
        # Same-day reports are leads, never a confirmed advertiser-to-aircraft match.
        flight = {k: original[k] for k in ('tail','date','track')}
        flight['candidates'] = sorted(set(by_day[flight['date']]))
        flights.append(flight)
    dated = [item['date'] for item in entries if item['date']]
    return dict(brands=brands, entries=entries, flights=flights, latest=max(dated, default=''), excluded=excluded)


def header(current):
    pages = [('/', 'Sightings'), ('/map', 'Flight map'), ('/stats', 'Stats'), ('/fly', 'Book a banner')]
    links = ''.join(f'<a href="{url}"'+(' aria-current="page"' if url==current else '')+f'>{label}</a>' for url,label in pages)
    return f'<a class="skip" href="#content">Skip to content</a><header class="top"><a class="wm" href="/">Who\'s flying over SF?</a><nav aria-label="Main">{links}</nav><a class="act" href="{REPORT}">Report a sighting</a></header>'


def page(title, description, path, body, scripts='', extra_head=''):
    full_title = title if path=='/' else title + " | Who's flying over SF?"
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<script>
  window.va = window.va || function () {{ (window.vaq = window.vaq || []).push(arguments); }};
</script>
<script defer src="/_vercel/insights/script.js"></script>
<script defer src="/outbound.js"></script>
<title>{e(full_title)}</title><meta name="description" content="{e(description)}">
<link rel="canonical" href="{ORIGIN}{path}"><meta property="og:type" content="website"><meta property="og:title" content="{e(full_title)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{ORIGIN}{path}"><meta property="og:image" content="{ORIGIN}/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="A banner plane above the San Francisco skyline"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(full_title)}"><meta name="twitter:description" content="{e(description)}"><meta name="twitter:image" content="{ORIGIN}/og.png">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="alternate icon" href="/favicon.ico"><link rel="apple-touch-icon" href="/favicon-180.png"><link rel="preload" href="/fonts/schibsted-grotesk.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="/style.css"><meta name="theme-color" content="#E9EDF0">{extra_head}</head>
<body>{header(path)}{body}<footer class="footer"><p>A community record of SF's banner planes. <a href="{REPORT}">Add a sighting</a> or <a href="{REPO}/issues/new">send a correction</a>.</p><p><a href="{REPO}">Source &amp; data</a> · <a href="{REPO}/blob/main/data/LICENSE">Data: CC BY 4.0</a> · <a href="mailto:hello@sfbannerplanes.com">Email</a></p></footer>{scripts}</body></html>'''


def hero(title, text):
    return f'<section class="hero"><div class="banner"><h1>{title}</h1></div><p class="lede">{text}</p></section>'


def evidence_card(item, brands):
    brand = brands[item['brand']]
    slogan = item['texts'][0] if item['texts'] else brand['label']
    date_text = date_label(item['date'])
    photo = any(s['photo'] for s in item['sources'])
    note = 'Photo linked' if photo else ('Reader report' if all(not s['url'] for s in item['sources']) else 'Text report')
    sources = ''.join(f'<li>{e(s["source"])}{(" · @"+e(s["author"])) if s["author"] else ""}: {e(s["note"])}'+(f' <a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">Open source</a>' if s['url'] else '')+'</li>' for s in item['sources'])
    return f'''<article class="sighting" id="sighting-{item['id']}"><div class="sighting-date">{e(date_text)}<span>{note}</span></div><div><h3>{e(slogan)}</h3><p class="sighting-brand">{e(brand['label'])}{' · drone airship' if item['brand']=='Pylon' else ' · blimp' if item['brand'] in ('Vercel','HappyRobot') else ''}</p><details><summary>Read {len(item['sources'])} source{'s' if len(item['sources'])!=1 else ''}</summary><ul class="source-list">{sources}</ul></details></div></article>'''
