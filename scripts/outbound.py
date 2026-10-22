"""Referral attribution for rendered website anchors, never source data or assets."""
import html
from html.parser import HTMLParser
import re
from urllib.parse import parse_qsl, unquote, urlsplit

SOURCE = 'whosflyingoversf.com'
SITE_HOSTS = {SOURCE, 'sfbannerplanes.com', 'whosflyingoversf.vercel.app'}
ASSET = re.compile(r'\.(?:pdf|csv|json|xml|txt|zip|gz|tar|7z|exe|dmg|pkg|jpg|jpeg|png|gif|webp|avif|svg|ico|mp3|mp4|mov|webm|wav|woff2?|ttf|otf|css|js|mjs)$', re.I)
SIGNED = re.compile(r'^(?:x-amz-.+|x-goog-.+|signature|sig|token|access_token|auth|authorization|credential|policy|expires|expiry|hmac|jwt|hdnts|hdntl|key-pair-id|awsaccesskeyid)$', re.I)


def outbound_url(raw):
    if not re.match(r'^(?:https?:)?//', raw, re.I) or re.search(r'[\s\\]', raw):
        return raw
    try:
        url = urlsplit('https:' + raw if raw.startswith('//') else raw)
        # Accessing port validates malformed/non-numeric ports too.
        _ = url.port
        host = (url.hostname or '').lower().rstrip('.')
        if not host or url.username or url.password:
            return raw
        if any(host == site or host.endswith('.' + site) for site in SITE_HOSTS):
            return raw
        keys = {key.lower() for key, _ in parse_qsl(url.query, keep_blank_values=True)}
        if 'utm_source' in keys or 'download' in keys or any(SIGNED.match(key) for key in keys):
            return raw
        # GitHub blob URLs display a web page, even when the filename is a CSV.
        github_view = host == 'github.com' and re.match(r'^/[^/]+/[^/]+/blob/', url.path)
        if ASSET.search(unquote(url.path)) and not github_view:
            return raw
    except ValueError:
        return raw
    base, hash_mark, fragment = raw.partition('#')
    separator = ('&' if not base.endswith(('?', '&')) else '') if '?' in base else '?'
    return base + separator + 'utm_source=' + SOURCE + hash_mark + fragment


def decorate_html(text):
    """Change anchor start tags only; leave scripts, JSON and other markup intact."""
    offsets = [0] + [match.end() for match in re.finditer('\n', text)]
    edits = []

    class Anchors(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag != 'a':
                return
            values = dict(attrs)
            if 'download' in values or 'data-no-referral' in values:
                return
            raw = values.get('href')
            if not raw or (updated := outbound_url(raw)) == raw:
                return
            rendered = '<a' + ''.join(' ' + name + ('' if value is None else '="' + html.escape(updated if name == 'href' else value, quote=True) + '"') for name, value in attrs) + '>'
            line, column = self.getpos()
            start = offsets[line - 1] + column
            edits.append((start, start + len(self.get_starttag_text()), rendered))

    Anchors(convert_charrefs=True).feed(text)
    for start, end, replacement in reversed(edits):
        text = text[:start] + replacement + text[end:]
    return text
