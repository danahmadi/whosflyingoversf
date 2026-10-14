import json,gzip,glob,datetime,zoneinfo,statistics,math,os
PT=zoneinfo.ZoneInfo("America/Los_Angeles")
BOX=(37.69,37.84,-122.54,-122.34)
TAILS={"aa3b5a":"N7589F","a783b4":"N5832J","aaec64":"N8025T","a06bba":"N126TW","ad9518":"N97413","a2ca97":"N2792P"}
extra=os.environ.get("EXTRA_HEX","")
for x in extra.split(","):
    if ":" in x: h,t=x.split(":"); TAILS[h]=t
def load(f):
    b=open(f,'rb').read()
    try:b=gzip.decompress(b)
    except:pass
    return json.loads(b)
flights=[]
for f in sorted(glob.glob("2026.*/traces/*/trace_full_*.json")):
    hx=f.split("_")[-1][:-5]
    if hx not in TAILS: continue
    j=load(f);t0=j["timestamp"]
    pts=[(t0+q[0],q[1],q[2],q[3] if isinstance(q[3],(int,float)) else None,q[4]) for q in j["trace"] if q[1] is not None]
    inb=[p for p in pts if BOX[0]<=p[1]<=BOX[1] and BOX[2]<=p[2]<=BOX[3]]
    # sessions
    ses=[];cur=[]
    for p in inb:
        if cur and p[0]-cur[-1][0]>1200: ses.append(cur);cur=[]
        cur.append(p)
    if cur: ses.append(cur)
    # merge sessions within 2h (refuel break) into one day-flight
    for s in ses:
        dur=(s[-1][0]-s[0][0])/3600
        spd=[p[4] for p in s if p[4]];alt=[p[3] for p in s if p[3] is not None]
        if dur<0.75 or not spd: continue
        ms=statistics.median(spd);ma=statistics.median(alt) if alt else 0
        if ms>85 or ma>3500: continue
        # turning: total heading change / hours
        trk=s[::max(1,len(s)//1500)]
        st=datetime.datetime.fromtimestamp(s[0][0],PT);en=datetime.datetime.fromtimestamp(s[-1][0],PT)
        # whole airborne window around session
        i0=pts.index(s[0]);i1=pts.index(s[-1])
        while i0>0 and pts[i0][0]-pts[i0-1][0]<1800: i0-=1
        while i1<len(pts)-1 and pts[i1+1][0]-pts[i1][0]<1800: i1+=1
        allt=[pts[i0][0],pts[i1][0]]
        flights.append(dict(tail=TAILS[hx],hex=hx,date=st.strftime("%Y-%m-%d"),start=st.strftime("%H:%M"),end=en.strftime("%H:%M"),
          hours_over_sf=round(dur,2),win=[allt[0],allt[-1]],median_kt=round(ms),median_alt_ft=round(ma),
          track=[[round(p[1],4),round(p[2],4)] for p in trk]))
# merge same tail same date
m={}
for fl in flights:
    k=(fl["tail"],fl["date"])
    if k in m:
        a=m[k];a["end"]=max(a["end"],fl["end"]);a["start"]=min(a["start"],fl["start"]);a["hours_over_sf"]=round(a["hours_over_sf"]+fl["hours_over_sf"],2);a["wins"].append(fl["win"]);a["track"]+=fl["track"];a["sessions"]+=1
    else: fl["sessions"]=1;fl["wins"]=[fl["win"]];m[k]=fl
for a in m.values():
    w=sorted(set(map(tuple,a.pop("wins"))));a.pop("win");a["airborne_hours"]=round(sum(b-a_ for a_,b in w)/3600,2)
out=sorted(m.values(),key=lambda x:(x["date"],x["tail"]))
json.dump(out,open("flights.json","w"))
for o in out: print(o["date"],o["tail"],o["start"],o["end"],o["hours_over_sf"],o["airborne_hours"],o["median_kt"],o["median_alt_ft"],o["sessions"])
print(len(out),"flights")
