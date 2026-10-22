from common import *
from collections import defaultdict
D = load_data()
days = defaultdict(set)
for item in D['entries']:
    if item['date']: days[item['brand']].add(item['date'])
rows = ''
for brand, dates in sorted(days.items(), key=lambda x:(-len(x[1]),x[0])):
    name = D['brands'][brand]['label']
    rows += f'<tr><th scope="row">{e(name)}'+(' <span class="small">(drone airship)</span>' if brand=='Pylon' else '')+f'</th><td>{len(dates)}</td><td>{date_label(min(dates))}</td><td>{date_label(max(dates))}</td></tr>'
undated = len([x for x in D['entries'] if not x['date']])
# Day-based estimates. Legacy ADS-B durations are not used (see "What the flight map shows").
HOURS, COST, GPH, CO2_KG = (4, 6), (4500, 9000), (7, 12), 8.31
NOT_PLANES = {'Pylon': 'drone airship', 'Vercel': 'blimp', 'HappyRobot': 'blimp'}
est_rows = ''
tot = dict(days=0, h=[0, 0], c=[0, 0], g=[0, 0], co=[0, 0])
def rng(a, b, fmt): return f'{fmt(a)}–{fmt(b)}'
money = lambda x: (f'${x/1000:.1f}k' if x < 1e4 else f'${x/1000:,.0f}k') if x < 1e6 else f'${x/1e6:.2f}M'
num = lambda x: f'{x:,.0f}'
tonnes = lambda x: f'{x:,.1f}'
for brand, dates in sorted(days.items(), key=lambda x:(-len(x[1]),x[0])):
    name, n = D['brands'][brand]['label'], len(dates)
    if brand in NOT_PLANES:
        est_rows += f'<tr><th scope="row">{e(name)} <span class="small">({NOT_PLANES[brand]}; not estimated)</span></th><td>{n}</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>'
        continue
    h = (n*HOURS[0], n*HOURS[1]); c = (n*COST[0], n*COST[1]); g = (h[0]*GPH[0], h[1]*GPH[1]); co = (g[0]*CO2_KG/1000, g[1]*CO2_KG/1000)
    tot['days'] += n
    for k, v in (('h', h), ('c', c), ('g', g), ('co', co)): tot[k][0] += v[0]; tot[k][1] += v[1]
    est_rows += f'<tr><th scope="row">{e(name)}</th><td>{n}</td><td>{rng(*h, num)}</td><td>{rng(*c, money)}</td><td>{rng(*g, num)}</td><td>{rng(*co, tonnes)}</td></tr>'
est_total = f'<tr><th scope="row">Total (banner planes)</th><td>{tot["days"]}</td><td>{rng(*tot["h"], num)}</td><td>{rng(*tot["c"], money)}</td><td>{rng(*tot["g"], num)}</td><td>{rng(*tot["co"], tonnes)}</td></tr>'
body = hero('Stats and method', 'A photo can identify a banner. A flight track can show where a plane went. Connecting the two takes more evidence.')
body += f'''<main id="content" class="reading">
<section><h2>Days with a dated sighting</h2><p>We count each brand once per day, even when several people post about it. We use the date of the sighting when a source specifies one, rather than the date of a later post. These counts describe this archive; they do not measure how often a company flies.</p>
<div class="tbl"><table><caption>Dated SF sightings by brand</caption><thead><tr><th scope="col">Brand</th><th scope="col">Days</th><th scope="col">First report</th><th scope="col">Latest report</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="small">We keep {undated} reports with unconfirmed flight dates separate. Reports outside SF, uncertain locations and low-confidence references stay in the source CSV but do not enter these counts. Direct reader reports carry a label when no public link is available.</p></section>
<section><h2>How we handle a report</h2><ol><li>Keep the source link and the wording the person reported. A quoted slogan is not a transcript we independently verified.</li><li>Separate the flight date from the post date. “Yesterday” can establish a date; “last week” cannot establish a single day.</li><li>Check the location. A banner at SaaStr in San Mateo does not establish a sighting over San Francisco.</li><li>Keep unconfirmed dates visible as undated reports. Corrections can change the counts.</li></ol><p>You can inspect the <a href="{REPO}/blob/main/data/sightings.csv">source CSV</a>, <a href="{REPO}/blob/main/CONTRIBUTING.md">contribution notes</a>, or <a href="{REPO}/issues/new">flag an error</a>.</p></section>
<section><h2>What the flight map shows</h2><p>The <a href="/map">map</a> contains {len(D['flights'])} candidate tracks from the <a href="https://www.adsb.lol/">adsb.lol</a> archive. The detector looks for tracked aircraft spending at least 45 minutes inside an SF bounding box, with median speed below 85 knots and median altitude below 3,500 feet.</p><p>That pattern suggests banner towing. It does not prove that a plane carried a banner. A brand seen on the same date is a lead, so we list it as a possible match without assigning the flight to that advertiser.</p><p>The archive covers selected aircraft and dates. Missing tracks do not establish that a flight never happened. Older duration values came from a detector that could include gaps and ground time; we have removed those durations from the public estimates until the raw traces can be reprocessed.</p></section>
<section><h2>What a day might cost</h2><p>Monaco CEO Sam Blond reported about <strong>$6,000 for six flight hours</strong>, including up to two hours of transit. That is one campaign's price; the estimates below use a range around it rather than treating it as every company's rate. <a href="https://www.linkedin.com/posts/sam-blond-791026b_the-monaco-plane-economics-and-impact-activity-7468079804244959232-pCx2">Read his account</a>.</p><p>Aerial Messages currently lists $1,275 per hour for a two-hour booking and $935 per hour at 100 hours. Ask an operator about transit, banner production and weather cancellations before comparing quotes. <a href="https://www.aerialmessages.com/commercial-advertising-rates/">Published rates</a> · <a href="/fly">Booking guide</a>.</p></section>
<section id="estimates"><h2>Estimated flight hours, spend, fuel and CO₂</h2><p>These are rough ranges built from the dated sightings above, not measurements. Day counts are a floor: a day only counts when someone posted a dated report, and some advertisers flew far more often than people posted.</p>
<div class="tbl"><table><caption>Estimates by brand (low–high)</caption><thead><tr><th scope="col">Brand</th><th scope="col">Days</th><th scope="col">Flight hours</th><th scope="col">Spend</th><th scope="col">Avgas (gallons)</th><th scope="col">CO₂ (tonnes)</th></tr></thead><tbody>{est_rows}</tbody><tfoot>{est_total}</tfoot></table></div>
<ul><li><strong>Flight hours: 4–6 per day.</strong> Sam Blond's Monaco figure of six hours includes up to two hours of transit; the low end counts about four hours over SF.</li><li><strong>Spend: $4,500–$9,000 per day.</strong> About six hours at published volume rates up to $1,500 an hour; Blond reported about $6,000 a day.</li><li><strong>Fuel: 7–12 gallons of 100LL avgas per hour.</strong> An <a href="https://data.ntsb.gov/carol-repgen/api/Aviation/ReportMain/GenerateNewestReport/68426/pdf">NTSB report</a> on a banner-tow Super Cub cites about eight gallons an hour; towing at high power and low speed raises burn.</li><li><strong>CO₂: 8.31 kg per gallon</strong>, from the <a href="https://www.epa.gov/system/files/documents/2025-01/ghg-emission-factors-hub-2025.pdf">EPA emission factors</a>. Combustion only, not lifecycle; leaded avgas emissions are not counted.</li><li>Low = days × 4 h × 7 gal/h; high = days × 6 h × 12 gal/h. One plane per brand per day. Drone airships and blimps are listed but left out of the estimates. Legacy ADS-B durations are not used.</li></ul></section><section><h2>Image credits</h2><p>Social previews use <a href="https://www.flickr.com/photos/9763931@N04/4838791175">“Adversiting banner airplane” by Lee Cannon</a>, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC BY-SA 2.0</a>. The booking guide credits its photo below the image.</p></section></main>'''
write('stats.html', page('Stats and method', 'Estimated flight hours, spend, avgas burned and CO₂ emissions from SF banner planes, plus how we date sightings and interpret aircraft tracks.', '/stats', body))
