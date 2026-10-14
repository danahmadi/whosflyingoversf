"""Detect candidate banner-tow sessions from downloaded adsb.lol traces.

Run from any directory: python scripts/detect.py --input adsb --output data/flights.json
Durations sum short observed airborne intervals; they do not bridge missing coverage.
"""
import argparse
from collections import defaultdict
from datetime import datetime
import gzip
import json
import statistics
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
PT=ZoneInfo('America/Los_Angeles')
BOX=(37.69,37.84,-122.54,-122.34)
TAILS={'aa3b5a':'N7589F','a783b4':'N5832J','aaec64':'N8025T','a06bba':'N126TW','ad9518':'N97413','a2ca97':'N2792P'}
MAX_GAP=120  # Coverage gaps are unknown time, not observed flight time.

def airborne(point):return isinstance(point[3],(int,float)) and point[3]>0 and isinstance(point[4],(int,float)) and point[4]>0

def in_sf(point):return BOX[0]<=point[1]<=BOX[1] and BOX[2]<=point[2]<=BOX[3]

def candidates(trace,hex_code):
    # Split on ground reports, long reception gaps, and PT midnight.
    chunks=[];chunk=[]
    for raw in sorted(trace['trace'],key=lambda q:q[0]):
        if raw[1] is None or raw[2] is None:continue
        point=(trace['timestamp']+raw[0],raw[1],raw[2],raw[3],raw[4])
        date=datetime.fromtimestamp(point[0],PT).date()
        if chunk and (not airborne(point) or point[0]-chunk[-1][0]>MAX_GAP or date!=datetime.fromtimestamp(chunk[-1][0],PT).date()):chunks.append(chunk);chunk=[]
        if airborne(point):chunk.append(point)
    if chunk:chunks.append(chunk)
    grouped=defaultdict(list)
    for chunk in chunks:
        inside=[p for p in chunk if in_sf(p)]
        if len(inside)<2:continue
        seconds=sum(b[0]-a[0] for a,b in zip(chunk,chunk[1:]) if in_sf(a) and in_sf(b))
        speed=statistics.median(p[4] for p in inside);alt=statistics.median(p[3] for p in inside)
        if seconds and speed<85 and alt<3500:grouped[datetime.fromtimestamp(inside[0][0],PT).strftime('%Y-%m-%d')].append((chunk,inside,seconds))
    result=[]
    for day,segments in grouped.items():
        sf_seconds=sum(s[2] for s in segments)
        if sf_seconds<2700:continue
        points=[p for _,inside,_ in segments for p in inside]
        result.append(dict(tail=TAILS[hex_code],hex=hex_code,date=day,start=datetime.fromtimestamp(points[0][0],PT).strftime('%H:%M'),end=datetime.fromtimestamp(points[-1][0],PT).strftime('%H:%M'),hours_over_sf=round(sf_seconds/3600,2),airborne_hours=round(sum(chunk[-1][0]-chunk[0][0] for chunk,_,_ in segments)/3600,2),median_kt=round(statistics.median(p[4] for p in points)),median_alt_ft=round(statistics.median(p[3] for p in points)),sessions=len(segments),track=[[round(p[1],4),round(p[2],4)] for p in points[::max(1,len(points)//1500)]]))
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,default=ROOT/'adsb')
    parser.add_argument('--output',type=Path,default=ROOT/'data/flights.json')
    args=parser.parse_args()
    files=sorted(args.input.rglob('trace_full_*.json'))
    if not files:parser.error('No trace files found. Existing output was not changed.')
    # UTC archives can split a PT flight day; combine and deduplicate samples first.
    traces=defaultdict(dict)
    for path in files:
        code=path.stem.removeprefix('trace_full_')
        if code not in TAILS:continue
        raw=path.read_bytes()
        if raw[:2]==b'\x1f\x8b':raw=gzip.decompress(raw)
        trace=json.loads(raw)
        for point in trace['trace']:
            timestamp=trace['timestamp']+point[0]
            traces[code][timestamp]=[timestamp,*point[1:]]
    if not traces:parser.error('No tracked aircraft found. Existing output was not changed.')
    flights=[]
    for code,points in traces.items():flights.extend(candidates({'timestamp':0,'trace':list(points.values())},code))
    flights.sort(key=lambda f:(f['date'],f['tail']))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(flights,separators=(',',':'))+'\n')
    print(f'{len(flights)} candidate tracks written to {args.output}')
if __name__=='__main__':main()
