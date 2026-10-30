(() => {
  'use strict';

  if (location.hostname !== 'whosflyingoversf.com' || location.protocol !== 'https:') return;
  if (navigator.globalPrivacyControl || navigator.doNotTrack === '1' ||
      navigator.doNotTrack === 'yes' || window.doNotTrack === '1' ||
      navigator.msDoNotTrack === '1' || window.sfAnalyticsLoaded) return;
  window.sfAnalyticsLoaded = true;

  // Keep campaign attribution, but omit filters, unrelated parameters and fragments.
  const page = new URL(location.href);
  const campaignKeys = new Set(['utm_source', 'utm_medium', 'utm_campaign', 'utm_id', 'utm_term', 'utm_content']);
  for (const key of [...page.searchParams.keys()]) {
    if (!campaignKeys.has(key)) page.searchParams.delete(key);
  }
  page.hash = '';
  let referrer = '';
  try {
    const source = new URL(document.referrer);
    if (source.protocol === 'https:' || source.protocol === 'http:') referrer = source.origin + '/';
  } catch (_) { /* An empty or invalid referrer has no attribution. */ }

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  window.gtag('set', {
    allow_google_signals: false,
    allow_ad_personalization_signals: false,
    page_location: page.href,
    page_referrer: referrer
  });
  window.gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied'
  });
  window.gtag('js', new Date());
  window.gtag('config', 'G-B3NX9EE5BM');

  const tag = document.createElement('script');
  tag.async = true;
  tag.src = 'https://www.googletagmanager.com/gtag/js?id=G-B3NX9EE5BM';
  document.head.appendChild(tag);
})();
