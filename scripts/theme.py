"""Post-build design pass: one stylesheet, one top bar, banner headlines,
SVG icons instead of emoji, no inline colours. Run after the page builders."""
import re
import html as H
SITE_URL="https://whosflyingoversf.com"
SITE_NAME="Who's flying over SF?"
FONT='<link rel="preload" href="fonts/schibsted-grotesk.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="style.css?v=4"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#E9EDF0"><link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="alternate icon" href="favicon.ico"><link rel="apple-touch-icon" href="favicon-180.png">'
PAGES=[("index.html","Calendar"),("map.html","Map"),("stats.html","Statistics"),("fly.html","Fly a banner")]
# Per-page SEO copy. Titles here match what each page builder + fix_dash()
# ends up rendering in <title>, so the OG/Twitter title always agrees with
# the tab title instead of drifting out of sync.
SEO={
    "index.html": dict(path="/", title=SITE_NAME,
        desc="A living calendar of every advertiser spotted towing a banner plane over San Francisco, with banner text, photos and public sources for each sighting."),
    "map.html": dict(path="/map", title=SITE_NAME+" | map",
        desc="A heatmap and flight-track map of every detected banner-tow flight over San Francisco, built from public ADS-B data."),
    "stats.html": dict(path="/stats", title=SITE_NAME+" | statistics",
        desc="Estimated flight hours, spend, fuel burn and CO\u2082 for every advertiser that's flown a banner plane over San Francisco."),
    "fly.html": dict(path="/fly", title="How to fly a banner over SF | "+SITE_NAME,
        desc="How much an aerial banner plane over San Francisco costs, how the process works, and vendors who offer it."),
}
def seo_tags(page):
    m=SEO[page]; url=SITE_URL+m["path"]; title=m["title"]; desc=m["desc"]
    e=lambda s:H.escape(s,quote=True)
    img=SITE_URL+"/og.png"
    alt=e(SITE_NAME+": a dark banner strip towed by a small plane over a foggy San Francisco skyline")
    return (
        f'<meta name="description" content="{e(desc)}">'
        f'<link rel="canonical" href="{url}">'
        f'<meta property="og:type" content="website">'
        f'<meta property="og:site_name" content="{e(SITE_NAME)}">'
        f'<meta property="og:title" content="{e(title)}">'
        f'<meta property="og:description" content="{e(desc)}">'
        f'<meta property="og:url" content="{url}">'
        f'<meta property="og:image" content="{img}">'
        f'<meta property="og:image:width" content="1200">'
        f'<meta property="og:image:height" content="630">'
        f'<meta property="og:image:alt" content="{alt}">'
        f'<meta name="twitter:card" content="summary_large_image">'
        f'<meta name="twitter:title" content="{e(title)}">'
        f'<meta name="twitter:description" content="{e(desc)}">'
        f'<meta name="twitter:image" content="{img}">'
        f'<meta name="twitter:image:alt" content="{alt}">'
    )
def top(cur):
    links="".join(f'<a href="{h}"{" aria-current=page" if h==cur else ""}>{n}</a>' for h,n in PAGES if h!="fly.html")
    return f'<header class="top"><a class="wm" href="index.html">Who\'s flying over SF?</a><nav>{links}</nav><a class="act" href="fly.html">Fly a banner</a></header>'
I=lambda p:f'<svg class=\\"icon\\" viewBox=\\"0 0 24 24\\" aria-hidden=\\"true\\">{p}</svg>'
PLANE='<path d=\\"M2 16l20-6-20-6 3 6-3 6z\\"/><path d=\\"M5 10h17\\"/>'
WARN='<path d=\\"M12 3l10 18H2z\\"/><path d=\\"M12 10v5M12 18h.01\\"/>'
CAM='<path d=\\"M4 7h4l2-3h4l2 3h4v13H4z\\"/><circle cx=\\"12\\" cy=\\"13\\" r=\\"4\\"/>'
def common(t,page):
    t=re.sub(r'<style>.*?</style>','',t,flags=re.S)
    t=re.sub(r'<meta name=["]?viewport["]? content="[^"]*">','',t)
    t=t.replace('</head>',FONT+seo_tags(page)+'</head>',1)
    t=t.replace('<html>','<html lang="en">',1)
    return t
def fix_dash(t):
    # prose em dashes -> punctuation (keep inside data cells written as lone —)
    h,b=t.split('</title>',1)
    return h.replace(' — ',' | ')+'</title>'+re.sub(r' — ',', ',b)
def index(t):
    t=re.sub(r'<header>.*?</header>',top("index.html")+'<section class="hero"><div class="banner"><h1>Who\'s flying over SF?</h1></div><p class="lede">Every brand seen towing an aerial banner over San Francisco, day by day. Built from public posts, Reddit threads, news and ADS-B flight tracks.<small>Click a logo for the evidence. Got a sighting we missed? <a href="mailto:hello@sfbannerplanes.com?subject=Banner%20sighting">Send it in</a>.</small></p></section>',t,flags=re.S)
    t=t.replace('<div class=\\"co\\" style=\\"display:block\\"><b>✈ ADS-B flight','<div class=\\"co fl\\"><div class=\\"fl-h\\">'+I(PLANE)+' ADS-B flight')
    t=t.replace('<div class="co" style="display:block"><b>✈ ADS-B flight','<div class="co fl"><b class="fl-h">'+I(PLANE).replace('\\"','"')+' ADS-B flight')
    for e,svg in (("✈",PLANE),("⚠",WARN),("📷",CAM)):
        t=t.replace(e+" ",I(svg)+" ").replace(e,I(svg))
    t=re.sub(r'style=\\?"background:#fff7e0;border-radius:10px;padding:10px\\?"','',t)
    t=re.sub(r'style=\\?"font-family:monospace;background:#eef3fa;padding:2px 6px;border-radius:4px\\?"','class="t"',t)
    t=re.sub(r'style=\\?"color:#445;margin-top:4px\\?"','style="margin-top:4px"',t)
    t=re.sub(r'style=\\?"color:#2a7de1\\?"','',t)
    t=t.replace('#2a7de1','#0E1A24')
    t=t.replace('hello@flyingoversf.com','hello@sfbannerplanes.com')
    t=t.replace('<h3 style=\\"margin:12px 0 4px;font-size:15px\\">Evidence','<h3 style=\\"margin:18px 0 4px;font-size:19px;font-weight:800\\">Evidence')
    t=t.replace('if(v){e.classList.add("has")','if(v){e.classList.add("has");e.style.setProperty("--i",dn++)')
    t=t.replace('function render(){','let dn=0;function render(){dn=0;',1)
    t=t.replace('</b> · ${f.start}','</b><br>${f.start}')
    return t
def stats(t):
    t=re.sub(r'<main><a href="index.html">.*?</h1>',top("stats.html")+'<section class="hero"><div class="banner"><h1>Statistics</h1></div><p class="lede">What each advertiser has likely spent, flown and burned, estimated from public sightings and ADS-B tracks.</p></section><main>',t,flags=re.S)
    t=t.replace('<div class=card><table>','<h2>Per advertiser</h2><div class="card tbl"><table>')
    return fix_dash(t)
def map_(t):
    t=re.sub(r'<div id=side><a href="index.html">.*?</h1>','<div class="mapapp"><div id=side>'+top("map.html").replace('<a class="act" href="fly.html">Fly a banner</a>','')+'<h1>Flight map</h1><p class=s>',t,flags=re.S)
    t=t.replace('banner-tow flights over SF (adsb.lol open archive). Brands come from same-day public sightings.</div>','banner-tow flights over SF (adsb.lol open archive). Brands come from same-day public sightings.</p>')
    t=t.replace('<h3>','<h2>').replace('</h3>','</h2>').replace('<div id=map></div>','<div id=map></div></div>',1)
    t=t.replace('<p class=s><div class=s>','<p class=s>')
    t=t.replace('#2a7de1','#C2380B')
    return fix_dash(t)
def fly(t):
    t=re.sub(r'<main>\s*<nav>.*?</nav>\s*<h1>.*?</h1><p class=s>(.*?)</p>',lambda m:top("fly.html").replace('<a class="act" href="fly.html">Fly a banner</a>','<a class="act" href="mailto:hello@sfbannerplanes.com?subject=Featured%20vendor">Get featured</a>')+'<section class="hero"><div class="banner"><h1>Fly a banner over SF</h1></div><p class="lede">How it works, what it costs and who flies them, from public sources.<small>'+m.group(1)+'</small></p></section><main>',t,flags=re.S)
    t=t.replace('<div class=call><b>Want to be featured on this list?</b> Email us at','<div class=call><b>Want to be featured on this list?</b> Operators can write to')
    t=t.replace('</small></p></section><main>','</small></p><figure class="photo"><img src="assets/yippee-ki-yay.jpg" alt="Several small planes towing red letter banners across a blue sky with thin clouds" width="1023" height="770"><figcaption>Letter banners on tow (not SF). "Yippee Ki Yay" by Joe Shlabotnik, CC BY 2.0, via Flickr.</figcaption></figure></section><main>',1)
    return fix_dash(t)
for f,fn in (("index.html",index),("stats.html",stats),("map.html",map_),("fly.html",fly)):
    p="site/"+f; t=open(p).read(); t=fn(common(t,f)); open(p,"w").write(t)
print("themed")
