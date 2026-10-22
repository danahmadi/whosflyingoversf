import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from outbound import decorate_html, outbound_url


class OutboundTests(unittest.TestCase):
    def test_shared_url_cases(self):
        for raw, expected in json.loads((ROOT / 'tests/outbound_urls.json').read_text()):
            with self.subTest(url=raw):
                result = outbound_url(raw)
                self.assertEqual(result, raw if expected is None else expected)
                self.assertEqual(outbound_url(result), result)

    def test_only_website_anchors_change(self):
        untouched = '''<link href="https://cdn.test/style.css"><img src="https://cdn.test/image">
<script src="https://cdn.test/code"></script><script>const html = '<a href="https://example.org/">';</script>
<script type="application/json">{"url":"https://example.org/"}</script>
<a download href="https://example.org/export">Download</a>
<a data-no-referral href="https://example.org/opaque-signed-path">Signed</a>
<a href="mailto:hi@example.org">Mail</a><a href="/map">Map</a>'''
        self.assertEqual(decorate_html(untouched), untouched)
        rendered = decorate_html(untouched + '\n<a class="source" href="https://example.org/?q=one&amp;x=two#proof" target="_blank">Source</a>')
        self.assertIn('href="https://example.org/?q=one&amp;x=two&amp;utm_source=whosflyingoversf.com#proof"', rendered)
        self.assertIn('class="source"', rendered)
        self.assertTrue(rendered.startswith(untouched))
        self.assertEqual(decorate_html(rendered), rendered)

    def test_unicode_text_does_not_shift_anchor_edits(self):
        text = '<p>First\u2028second\rthird</p>\n<a href="https://example.org">Source</a>'
        self.assertEqual(decorate_html(text), text.replace('https://example.org"', 'https://example.org?utm_source=whosflyingoversf.com"'))

    def test_all_generated_pages_are_decorated(self):
        for path in (ROOT / 'site').glob('*.html'):
            with self.subTest(page=path.name):
                html = path.read_text()
                self.assertEqual(html.count('<script defer src="/outbound.js"></script>'), 1)
                self.assertEqual(decorate_html(html), html)
