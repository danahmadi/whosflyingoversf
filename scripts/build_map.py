import json,re
s=open("site/index.html").read()
D=json.loads(re.search(r"const D=(\{.*?\});const months",s,re.S).group(1))
data={"flights":D["flights"],"brands":D["brands"]}
html="""<!doctype html><html><head><meta charset=utf-8><title>Who's flying over SF? — map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"><script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script><script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
<style>body{margin:0;font-family:-apple-system,system-ui,Helvetica,Arial,sans-serif;display:flex;height:100vh}#side{width:290px;padding:16px;overflow:auto;background:#f4f7fb}#map{flex:1}
h1{font-size:22px;margin:0 0 4px}h1 span{color:#2a7de1}a{color:#2a7de1}.b{display:flex;align-items:center;gap:8px;margin:6px 0}.b img,.b .bd{width:22px;height:22px;border-radius:5px}.bd{color:#fff;font-weight:700;display:flex;align-items:center;justify-content:center;font-size:12px}
.s{font-size:12px;color:#667}label{cursor:pointer}</style></head><body>
<div id=side><a href="index.html">← Calendar</a> · <a href="stats.html">Statistics</a> · <a href="fly.html">Fly a banner</a><h1>Who's flying <span>over SF?</span> — map</h1><div class=s>Heatmap of ADS-B positions from detected banner-tow flights over SF (adsb.lol open archive). Brands come from same-day public sightings.</div>
<h3>Brands</h3><div id=br></div><h3>Dates</h3><input type=date id=d0> → <input type=date id=d1><h3>Layers</h3><label><input type=checkbox id=tr> Show individual tracks</label><div id=sum class=s style="margin-top:12px"></div></div><div id=map></div>
<script>const D=__DATA__;const map=L.map("map").setView([37.77,-122.43],12);L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",{attribution:"© OpenStreetMap"}).addTo(map);
const used=[...new Set(D.flights.map(f=>f.brand))];const on={};const br=document.getElementById("br");
used.forEach(b=>{on[b]=true;const B=D.brands[b]||D.brands.Unknown;const n=D.flights.filter(f=>f.brand==b).length;const r=document.createElement("label");r.className="b";r.innerHTML=`<input type=checkbox checked>${B.logo?`<img src="${B.logo}">`:`<span class=bd style="background:${B.color}">${b=="Unknown"?"?":b[0]}</span>`}${B.label} <span class=s>(${n})</span>`;r.querySelector("input").onchange=e=>{on[b]=e.target.checked;draw()};br.appendChild(r)});
const dates=D.flights.map(f=>f.date).sort();d0.value=dates[0];d1.value=dates[dates.length-1];d0.onchange=d1.onchange=tr.onchange=()=>draw();
let heat=null,lines=L.layerGroup().addTo(map);
function draw(){const fs=D.flights.filter(f=>on[f.brand]&&f.date>=d0.value&&f.date<=d1.value);const pts=[];fs.forEach(f=>f.track.forEach(p=>pts.push([p[0],p[1],0.5])));
if(heat)map.removeLayer(heat);heat=L.heatLayer(pts,{radius:14,blur:18,maxZoom:14}).addTo(map);lines.clearLayers();
if(tr.checked)fs.forEach(f=>L.polyline(f.track,{color:(D.brands[f.brand]||D.brands.Unknown).color,weight:1.5,opacity:.7}).bindTooltip(`${f.date} ${f.tail} ${(D.brands[f.brand]||{}).label||f.brand}`).addTo(lines));
const h=fs.reduce((a,f)=>a+f.hours_over_sf,0);sum.innerHTML=`${fs.length} flights · ${h.toFixed(1)} h over SF · ${pts.length.toLocaleString()} track points`}
draw();</script></body></html>"""
open("site/map.html","w").write(html.replace("__DATA__",json.dumps(data)))
print(len(data["flights"]),"flights in map")
