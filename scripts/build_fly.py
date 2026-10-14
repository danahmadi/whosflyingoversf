import json,html as H
V=json.load(open("data/vendors.json"))
e=H.escape
def card(v):
    src=" · ".join(f'<a href="{e(s)}">source</a>' for s in v["sources"])
    ev=f'<div class=ev><b>Linked campaigns:</b> {e(v["evidence"])}</div>' if v["evidence"] else ""
    return f'<div class=card><h3><a href="{e(v["url"])}">{e(v["name"])}</a></h3><div class=s>{e(v["location"])}</div><p>{e(v["services"])}</p><p class=s>{e(v["notes"])}</p>{ev}<div class=s>{src}</div></div>'
feat="".join(card(v) for v in V["featured"]) or '<div class="card empty">No featured vendors yet.</div>'
page=f"""<!doctype html><html><head><meta charset=utf-8><title>How to fly a banner over SF — Who's flying over SF?</title><meta name=viewport content="width=device-width,initial-scale=1"><style>
body{{font-family:-apple-system,system-ui,Helvetica,Arial,sans-serif;margin:0;background:#f4f7fb;color:#1b2430}}main{{max-width:900px;margin:auto;padding:24px 28px}}h1 span{{color:#2a7de1}}a{{color:#2a7de1}}
.card{{background:#fff;border-radius:14px;box-shadow:0 2px 10px #0001;padding:16px 18px;margin:12px 0}}.card h3{{margin:0 0 4px}}.s{{color:#667;font-size:13px}}.ev{{background:#eef3fa;border-radius:8px;padding:8px 10px;font-size:13px;margin:8px 0}}
.call{{background:#fff7e0;border-radius:12px;padding:14px 18px;margin:16px 0}}.empty{{color:#889;font-style:italic}}ol li{{margin:8px 0}}nav a{{margin-right:14px}}</style></head><body><main>
<nav><a href="index.html">Calendar</a><a href="map.html">Map</a><a href="stats.html">Statistics</a><b>How to fly a banner</b></nav>
<h1>How to fly a banner <span>over SF</span></h1><p class=s>A neutral overview from public sources. We're not affiliated with any operator.</p>
<div class=card><h2>Steps</h2><ol>
<li><b>Pick an operator.</b> Banner towing needs a specially equipped plane and an FAA certificate of waiver for towing (14 CFR 91.311), so book through an established operator (list below).</li>
<li><b>Design the banner.</b> The choices are a <i>letter banner</i> (individual tall letters; operators cap the character count, e.g. Fly Sky Ads includes up to 45 characters) or a printed <i>aerial billboard</i>/logo board (FlySigns quotes $1.15–$1.89 per sq ft, up to 40×120 ft from its LA location). Several Reddit posters said banners were hard to read from below or only legible from one side, so short, high-contrast text works best.</li>
<li><b>Airspace &amp; timing.</b> SF sits beneath busy SFO/OAK airspace and the operator coordinates routing. FlySigns says it flies about 1,000 ft over downtown SF and 500 ft over the bay, and that banners must be on the ground by sunset. Monaco's CEO said up to 2 of 6 daily flight hours went to transit from the airport, with one midday refuel.</li>
<li><b>Weather.</b> Banner flights need visual conditions. Low clouds or fog can delay or cancel a flight, so ask the operator about its weather and rescheduling policy.</li>
<li><b>Duration.</b> In the ADS-B data on this site, flights over SF typically lasted about 1.5–4 hours per day (up to ~5 hours on multi-session days). Monaco described ~6 flight hours/day including transit. Campaigns ranged from a single day to repeated multi-week runs.</li></ol></div>
<div class=card><h2>What it costs</h2><ul>
<li>~$6,000/day for ~6 flight hours: Monaco CEO Sam Blond (<a href="https://www.linkedin.com/posts/sam-blond-791026b_the-monaco-plane-economics-and-impact-activity-7468079804244959232-pCx2">LinkedIn</a>).</li>
<li>~$1.5k/hour, quoted by Nathan Flurry (Rivet) (<a href="https://x.com/NathanFlurry/status/2072761245216952777">X</a>).</li>
<li>Aerial Messages: $1,275/h (2 h), down to $935/h at 100 h (<a href="https://www.aerialmessages.com/commercial-advertising-rates/">rates</a>). US Air Ads: ~$625–925/h (<a href="https://usairads.com/rates.php">rates</a>). Fly Sky Ads (NY): $375–700+/h (<a href="https://flyskyads.com/pricing/">pricing</a>).</li>
<li>For our cost, fuel and CO₂ estimates, see <a href="stats.html">Statistics</a>.</li></ul></div>
<h2>Featured vendors</h2>{feat}
<div class=call><b>Want to be featured on this list?</b> Email us at <a href="mailto:hello@sfbannerplanes.com">hello@sfbannerplanes.com</a></div>
<h2>Vendors serving SF</h2>{''.join(card(v) for v in V['vendors'])}
<p class=s>"Linked campaigns" appear only where public evidence exists. Vendor data: <code>data/vendors.json</code> (CC-BY-4.0). Corrections welcome via GitHub issues.</p>
</main></body></html>"""
open("site/fly.html","w").write(page);print("fly.html")
