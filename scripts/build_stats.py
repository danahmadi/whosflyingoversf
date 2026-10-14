import json,re
s=open("site/index.html").read()
D=json.loads(re.search(r"const D=(\{.*?\});const months",s,re.S).group(1))
days={}
for d,v in D["days"].items():
    for b in v: days.setdefault(b,[]).append(d)
A=dict(hrs=(4,6),cost=(4500,9000),costmid=6000,gph=(7,12),co2=8.31)
FH={}
for fl in D.get("flights",[]):
    FH.setdefault(fl["brand"],[0,0,0]);FH[fl["brand"]][0]+=1;FH[fl["brand"]][1]+=fl["hours_over_sf"];FH[fl["brand"]][2]+=fl["airborne_hours"]
rows=[]
for b,ds in sorted(days.items(),key=lambda x:-len(x[1])):
    n=len(ds);lbl=D["brands"].get(b,{}).get("label",b)
    drone=b=="Pylon"
    h=(n*A["hrs"][0],n*A["hrs"][1])
    c=(n*A["cost"][0],n*A["cost"][1]) if not drone else None
    g=(h[0]*A["gph"][0],h[1]*A["gph"][1]) if not drone else None
    co=(g[0]*A["co2"]/1000,g[1]*A["co2"]/1000) if g else None
    rows.append((lbl,n,min(ds),max(ds),h,c,g,co,drone))
f=lambda a,fmt:"—" if a is None else f"{fmt(a[0])} – {fmt(a[1])}"
money=lambda x:f"${x/1000:,.0f}k" if x<1e6 else f"${x/1e6:.2f}M"
tr="".join(f"<tr><td><b>{l}</b>{' <span class=s>(drone airship; excluded from fuel/cost)</span>' if dr else ''}</td><td>{n}</td><td>{a} → {z}</td><td>{f(h,lambda x:f'{x:,.0f}')}</td><td>{(lambda q: f'{q[0]} · {q[1]:.1f} · {q[2]:.1f}' if q else '—')(FH.get(next((k for k,v in D['brands'].items() if v.get('label',k)==l),l)))}</td><td>{f(c,money)}</td><td>{f(g,lambda x:f'{x:,.0f}')}</td><td>{f(co,lambda x:f'{x:,.1f}')}</td></tr>" for l,n,a,z,h,c,g,co,dr in rows)
P=[r for r in rows if not r[8]]
T=lambda i,j:sum(r[i][j] for r in P)
tot=f"<tr class=tot><td>Total (planes)</td><td>{sum(r[1] for r in P)}</td><td></td><td>{T(4,0):,} – {T(4,1):,}</td><td>{sum(v[0] for v in FH.values())} · {sum(v[1] for v in FH.values()):.1f} · {sum(v[2] for v in FH.values()):.1f}</td><td>{money(T(5,0))} – {money(T(5,1))}</td><td>{T(6,0):,.0f} – {T(6,1):,.0f}</td><td>{T(7,0):,.1f} – {T(7,1):,.1f}</td></tr>"
html=f"""<!doctype html><html><head><meta charset=utf-8><title>Who's flying over SF? — statistics</title><style>
body{{font-family:-apple-system,system-ui,Helvetica,Arial,sans-serif;margin:0;background:#f4f7fb;color:#1b2430}}main{{max-width:1050px;margin:auto;padding:24px 32px}}
h1 span{{color:#2a7de1}}a{{color:#2a7de1}}.card{{background:#fff;border-radius:14px;box-shadow:0 2px 10px #0001;padding:18px;margin:16px 0}}
table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{padding:7px 8px;border-bottom:1px solid #eef;text-align:left}}th{{font-size:12px;color:#667;text-transform:uppercase}}
.tot td{{font-weight:700;border-top:2px solid #ccd}}.s{{color:#889;font-size:12px}}li{{margin:5px 0}}.warn{{background:#fff7e0;border-radius:10px;padding:10px 14px}}
</style></head><body><main><a href="index.html">← Calendar</a> · <a href="fly.html">How to fly a banner</a><h1>Who's flying <span>over SF?</span> — statistics</h1>
<div class="warn"><b>Day counts are a floor.</b> A day only counts if a dated public post (X, LinkedIn, Reddit, news) with medium/high confidence exists. Advertisers such as Monaco flew far more days than were posted about. All other figures are rough estimates shown as low – high ranges.</div>
<div class=card><table><tr><th>Advertiser</th><th>Days seen</th><th>First → last</th><th>Flight hours (est.)</th><th>ADS-B flights · h over SF · h airborne</th><th>Est. spend</th><th>Avgas (gal)</th><th>CO₂ (tonnes)</th></tr>{tr}{tot}</table></div>
<div class=card><h2>Methodology &amp; assumptions</h2><ul>
<li><b>Flight hours per day: 4–6 h.</b> Monaco CEO Sam Blond: "~$6,000 / day. This includes 6 hours of flight time, up to 2 of which are from the airport to SF (they have to refuel once during the day)." Low = ~4 h over SF only; high = the full 6 h including transit. <a href="https://www.linkedin.com/posts/sam-blond-791026b_the-monaco-plane-economics-and-impact-activity-7468079804244959232-pCx2">LinkedIn, Jun 3 2026</a></li>
<li><b>Spend per day: $4,500–$9,000</b> (mid $6,000 = Blond's figure). Low ≈ 6 h at published volume rates (~$750–935/h); high ≈ 6 h at $1,500/h, the rate Nathan Flurry (Rivet) quoted for SF (<a href="https://x.com/NathanFlurry/status/2072761245216952777">X, Jul 2 2026</a>). Prices vary by operator, banner type (letter vs. printed billboard) and how many days are booked.</li>
<li><b>Fuel burn: 7–12 gal/h of 100LL avgas.</b> An NTSB report on a PA-18A-150 banner-tow flight says "During banner tow operations the fuel burn off rate is about 8 gallons per hour" (<a href="https://data.ntsb.gov/carol-repgen/api/Aviation/ReportMain/GenerateNewestReport/68426/pdf">NTSB LAX08CA224</a>). The PA-18-150 manual lists 9 gph at 75% power (<a href="https://alaskafloatratings.com/wp-content/uploads/2021/12/pa-18-owners-manual-fuel-systems.pdf">manual excerpt</a>). The Champion 7KCAB (e.g. N7589F, registered to Aerial Advertising Services, Livermore) is listed at 6–9 gph at 75% power. A Cessna 180 burns ~13 gph at 75% (<a href="https://www.aopa.org/news-and-media/all-news/2014/february/pilot/cessna-180-skywagon">AOPA</a>). Towing a banner at high power and low speed raises burn, so 12 gph is the upper bound.</li>
<li><b>CO₂: 8.31 kg per gallon of aviation gasoline</b>, EPA GHG Emission Factors Hub (40 CFR 98 Table C-1), combustion only, not lifecycle (<a href="https://www.epa.gov/system/files/documents/2025-01/ghg-emission-factors-hub-2025.pdf">EPA 2025</a>). 100LL also emits lead, which isn't counted here.</li>
<li><b>ADS-B column:</b> real flights detected in the adsb.lol open archive for the tracked tails (low, slow loitering inside an SF box), with brands matched from same-day sightings. "Ambiguous" days are credited to the first brand. Real hours replace the 4–6 h guess wherever a flight was found; ADS-B coverage of small planes is incomplete.</li><li>Pylon's drone airship is shown in the table but left out of fuel, cost and CO₂.</li>
<li>Low estimate = days × 4 h × 7 gph; high estimate = days × 6 h × 12 gph. One plane per advertiser per day.</li></ul></div>
<div class=card><h2>Other public banner pricing</h2><ul>
<li>Monaco: ~$6,000/day for 6 h, vs. ~$120k/month for a premium 101 billboard (Blond, above).</li>
<li>Nathan Flurry (Rivet): "a banner plane for $1.5k/hr" vs. a $240k/yr billboard on 101 (<a href="https://x.com/NathanFlurry/status/2072761245216952777">X</a>).</li>
<li>Aerial Messages (national operator): $1,275/h for 2 h, falling to $935/h at 100 h (<a href="https://www.aerialmessages.com/commercial-advertising-rates/">rates</a>).</li>
<li>US Air Ads: ~$625–925/h for campaigns (<a href="https://usairads.com/rates.php">rates</a>). Fly Sky Ads (NY beaches): $375–700+/h (<a href="https://flyskyads.com/pricing/">pricing</a>).</li>
<li>FlySigns (Hayward base): aerial billboards printed at $1.15–1.89 per sq ft (<a href="http://www.flysigns.com/op-san-francisco.php">FlySigns SF</a>).</li>
<li>An unsourced X post claimed "+$10k for a 15 min flight" (<a href="https://x.com/GazvodaMatjaz/status/2099668018473083220">X</a>); it conflicts with every figure above.</li></ul></div>
</main></body></html>"""
open("site/stats.html","w").write(html);print(*[(r[0],r[1]) for r in rows])
