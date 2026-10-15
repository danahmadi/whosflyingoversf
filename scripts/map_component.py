"""Shared markup and assets for the homepage and full flight map."""
from common import json_text

HEAD = '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">'


def scripts(brands):
    labels = {k: v['label'] for k, v in brands.items()}
    return ('<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" defer></script>'
            '<script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js" defer></script>'
            f'<script type="application/json" id="map-brands">{json_text(labels)}</script>'
            '<script src="/map.js" defer></script>'
            '<script src="/plane.js" defer></script>')


def panel(embedded=False):
    if embedded:
        return '''<aside class="home-map" aria-labelledby="map-title"><div class="map-heading"><h2 id="map-title">Flight tracks</h2><a id="full-map-link" href="/map">Open full map ↗</a></div><p class="small">Choose a brand or a calendar day to explore its possible routes.</p><label class="map-brand-control" for="map-brand">Brand<select id="map-brand" disabled><option value="">All brands</option></select></label><p id="brand-context" class="small" hidden></p><p id="map-date-label">All recorded dates</p><button id="reset-map-day" class="quiet" hidden>Show all dates</button><p id="map-status" role="status" aria-live="polite">Loading flight tracks…</p><button id="retry-map" class="quiet" hidden>Try loading again</button><div id="map" aria-label="Map of candidate flight tracks"></div><p class="small map-caption">Colors show the concentration of recorded positions. Select a day to see its individual flight lines. No tracks here doesn’t mean no planes flew.</p><noscript><p>JavaScript is needed for the map.</p></noscript></aside>'''
    return '''<main id="content" class="mapapp"><aside id="side"><h1>Flight map</h1><p>Possible banner-tow flights from selected aircraft and dates. A track doesn't tell us what the banner said.</p><p class="small">Filter by brand to explore tracks from days it was sighted. Use dates or aircraft to narrow the view.</p><form id="map-filters" hidden><label class="map-brand-control" for="map-brand">Brand<select id="map-brand" disabled><option value="">All brands</option></select></label><p id="brand-context" class="small" hidden></p><label for="from">From<input type="date" id="from"></label><label for="to">Through<input type="date" id="to"></label><label for="tail">Aircraft<select id="tail"><option value="">All tracked aircraft</option></select></label><label class="check"><input type="checkbox" id="tracks"> Show individual tracks</label><button type="reset" class="quiet">Reset all filters</button></form><p id="map-status" role="status" aria-live="polite">Loading flight tracks…</p><button id="retry-map" class="quiet" hidden>Try loading again</button><p class="small">The heatmap shows recorded positions, not flight frequency. Coverage and sampling vary. <a href="/stats">Read the method</a>.</p><noscript><p>JavaScript is needed for the map. You can still <a href="/">browse sightings and sources</a>.</p></noscript></aside><div id="map" aria-label="Map of candidate flight tracks"></div></main>'''
