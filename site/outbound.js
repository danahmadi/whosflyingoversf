// Keep this policy aligned with scripts/outbound.py (shared URL fixtures test both).
(() => {
  'use strict';
  const source = 'whosflyingoversf.com';
  const siteHosts = [source, 'sfbannerplanes.com', 'whosflyingoversf.vercel.app', location.hostname.toLowerCase().replace(/\.$/, '')];
  const asset = /\.(?:pdf|csv|json|xml|txt|zip|gz|tar|7z|exe|dmg|pkg|jpg|jpeg|png|gif|webp|avif|svg|ico|mp3|mp4|mov|webm|wav|woff2?|ttf|otf|css|js|mjs)$/i;
  const signed = /^(?:x-amz-.+|x-goog-.+|signature|sig|token|access_token|auth|authorization|credential|policy|expires|expiry|hmac|jwt|hdnts|hdntl|key-pair-id|awsaccesskeyid)$/i;

  function decorate(anchor) {
    if (anchor.hasAttribute('download') || anchor.hasAttribute('data-no-referral')) return;
    const raw = anchor.getAttribute('href');
    if (!raw || !/^(?:https?:)?\/\//i.test(raw) || /[\s\\]/.test(raw)) return;
    try {
      const url = new URL(raw, location.href);
      const host = url.hostname.toLowerCase().replace(/\.$/, '');
      if (!host || url.username || url.password || siteHosts.some(site => host === site || host.endsWith('.' + site))) return;
      const keys = [...url.searchParams.keys()].map(key => key.toLowerCase());
      if (keys.some(key => key === 'utm_source' || key === 'download' || signed.test(key))) return;
      const githubView = host === 'github.com' && /^\/[^/]+\/[^/]+\/blob\//.test(url.pathname);
      if (asset.test(decodeURIComponent(url.pathname)) && !githubView) return;
      // Append to the original string so encoded query values and hashes stay intact.
      const hash = raw.indexOf('#');
      const base = hash < 0 ? raw : raw.slice(0, hash);
      const fragment = hash < 0 ? '' : raw.slice(hash);
      const separator = base.includes('?') ? (/[?&]$/.test(base) ? '' : '&') : '?';
      anchor.setAttribute('href', base + separator + 'utm_source=' + source + fragment);
    } catch {
      // Malformed or opaque URLs are safest left untouched.
    }
  }

  function scan(root) {
    if (root.nodeType !== 1) return;
    if (root.matches('a[href]')) decorate(root);
    root.querySelectorAll('a[href]').forEach(decorate);
  }

  scan(document.documentElement);
  new MutationObserver(records => {
    for (const record of records) {
      if (record.type === 'attributes') scan(record.target);
      else record.addedNodes.forEach(scan);
    }
  }).observe(document.documentElement, {subtree: true, childList: true, attributes: true, attributeFilter: ['href']});

  // Also handle an anchor inserted/changed and activated before the observer runs.
  for (const event of ['click', 'auxclick', 'contextmenu']) {
    document.addEventListener(event, e => {
      const anchor = e.target.closest?.('a[href]');
      if (anchor) decorate(anchor);
    }, true);
  }
})();
