from common import *

D = load_data()
# Flight tracks belong on the map, not in every calendar page request.
summary = {k:v for k,v in D.items() if k!='flights'}
summary['flights'] = [{k:v for k,v in f.items() if k!='track'} for f in D['flights']]
dated = [x for x in D['entries'] if x['date']]
undated = [x for x in D['entries'] if not x['date']]
options = ''.join(f'<option value="{e(k)}">{e(v["label"])}</option>' for k,v in D['brands'].items() if any(x['brand']==k for x in D['entries']))
body = hero("Who's flying over SF?", 'A record of the banners above San Francisco. Search the words you caught, or pick a date to find the source.')
body += f'''<main id="content" class="sightings-main">
<div class="archive-meta">Sightings archive <span>Latest report: {date_label(D['latest'])}</span></div>
<form class="filters" role="search" id="filters" hidden>
<label class="search-label" for="search">Banner text or brand<input id="search" type="search" placeholder="Try “SaaS is dead” or “MCP”" autocomplete="off"></label>
<label for="brand">Brand<select id="brand"><option value="">All brands</option>{options}</select></label>
<button type="reset" class="quiet">Clear filters</button></form>
<div class="quick-search" id="quick-search" hidden><span>Search a slogan:</span><button data-query="SaaS is dead">SaaS is dead</button><button data-query="MCP">MCP doesn’t suck</button><button data-query="Stop hiring humans">Stop hiring humans</button><button data-query="Hire human beings">Hire human beings</button></div>
<div class="viewbar" id="viewbar" hidden><div class="view-toggle" role="group" aria-label="View"><button id="list-view" aria-pressed="true">Recent sightings</button><button id="calendar-view" aria-pressed="false">Calendar</button></div><p id="result-count" role="status" aria-live="polite"></p></div>
<section id="recent" aria-label="Recent sightings"><div id="results">{''.join(evidence_card(x,D['brands']) for x in dated[:12])}</div><button id="more" class="quiet" hidden>Show earlier sightings</button></section>
<section id="calendar" class="cal" aria-label="Calendar" hidden><div class="nav"><button id="prev" aria-label="Previous month">‹</button><label for="month">Month<select id="month"></select></label><button id="next" aria-label="Next month">›</button></div><div id="grid" class="grid"></div><p class="small">A blank day means we have no dated report here. Several posts can describe the same flight.</p></section>
<details id="undated" class="undated"><summary>Reports without a confirmed flight date ({len(undated)})</summary><p>These posts describe an earlier flight or a campaign spanning several days. They stay out of the calendar and day counts until someone can pin down the date.</p><div id="undated-results">{''.join(evidence_card(x,D['brands']) for x in undated)}</div></details>
<aside class="contribute"><h2>Saw one we missed?</h2><p>The words on the banner, the date and your neighborhood are enough to start. A photo helps. Leave the brand blank if you couldn't make it out.</p><a href="{REPORT}">Report a sighting →</a><p class="small">GitHub account required. You can also <a href="mailto:hello@sfbannerplanes.com?subject=SF%20banner%20sighting&amp;body=Date%20and%20time%20(PT)%3A%0ANeighborhood%3A%0ABanner%20text%3A%0ASource%20link%20or%20photo%3A">email a report</a>. Reports appear after review.</p></aside>
<noscript><p>Enable JavaScript to search and browse the calendar. The latest sightings and their sources appear above; the <a href="{REPO}/blob/main/data/sightings.csv">full archive is on GitHub</a>.</p></noscript></main>
<dialog id="evidence" aria-labelledby="evidence-title"><div class="dialog-top"><p id="evidence-date"></p><button id="close-evidence" aria-label="Close evidence">×</button></div><div id="evidence-body"></div></dialog>'''
write('index.html', page("Who's flying over SF?", 'Look up banner planes seen over San Francisco. Search slogans and brands, browse sightings by date, and inspect the sources.', '/', body, f'<script type="application/json" id="sighting-data">{json_text(summary)}</script><script src="/calendar.js" defer></script>'))
write('data/flights.json', json_text(D['flights']))
print(f"{len(dated)} dated brand-days; {len(undated)} undated reports")
