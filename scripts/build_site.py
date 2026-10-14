import csv,json,collections
B=json.load(open("data/brands.json"))
def norm(b):
    for k,v in B.items():
        if b.startswith(v["match"]): return k
    return None
rank={"low":0,"medium":1,"high":2}
days=collections.defaultdict(dict)
for r in csv.DictReader(open("data/sightings.csv")):
    NONSF=["san mateo","south bay","san jose","sanjose","alameda","cupertino","fremont","silicon valley"]
    if any(k in (r["notes"]+" "+r["post_url"]).lower() for k in NONSF) and "sf" not in r["notes"].lower().replace("sfo",""): continue
    if r["confidence"]=="low": continue
    names=[norm(x.strip()) for x in r["brand"].split(";")]
    names=[n for n in names if n] or ["Unknown"]
    for n in names:
        e=days[r["date_pt"]].setdefault(n,{"texts":[],"sources":[],"conf":"low"})
        if r["banner_text"] and r["banner_text"] not in e["texts"]: e["texts"].append(r["banner_text"])
        e["sources"].append({"url":r["post_url"],"label":r["source"]+(" @"+r["author"] if r["author"] else ""),"note":r["notes"],"img":r["has_image"]=="yes","conf":r["confidence"],"brand_raw":r["brand"]})
        if rank[r["confidence"]]>rank[e["conf"]]: e["conf"]=r["confidence"]
import os
FL=json.load(open("data/flights.json")) if os.path.exists("data/flights.json") else []

flights_out=[]
for i,f in enumerate(FL):
    d=f["date"];known=[b for b in days.get(d,{}) if b not in ("Unknown","Pylon")]
    if len(known)==1: f["brand"]=known[0];f["match"]="high" if days[d][known[0]]["conf"]=="high" else "medium"
    elif len(known)>1: f["brand"]=known[0];f["match"]="ambiguous";f["candidates"]=known
    else: f["brand"]="Unknown";f["match"]="none"
    f["id"]=i;flights_out.append(f)
    e=days[d].setdefault(f["brand"],{"texts":[],"sources":[],"conf":"medium"})
    e.setdefault("flights",[]).append(i)
    if f["brand"]=="Unknown": e["detected"]=True
for d,v in days.items():
    for b,e in v.items():
        if b not in ("Unknown","Pylon") and not e.get("flights"): e["noflight"]=True
brands={k:{"label":v.get("label",k),"url":v["url"],"logo":v["logo"],"color":v["color"],"desc":v["description"]} for k,v in B.items()}
brands["Unknown"]={"label":"Unidentified banner","url":None,"logo":None,"color":"#999","desc":"Banner seen but advertiser not identified in the source."}
first=min(days); months=[]
y,m=int(first[:4]),int(first[5:7])
while (y,m)<=(2026,10):
    months.append([y,m-1]); y,m=(y+1,1) if m==12 else (y,m+1)
html=open("scripts/site_template.html").read().replace("__DATA__",json.dumps({"days":days,"brands":brands,"months":months,"flights":flights_out}))
open("site/index.html","w").write(html)
print(len(days),"days; months from",first)
