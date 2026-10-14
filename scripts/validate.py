"""Validate contribution data before any HTML is generated."""
import csv
import json
import math
import re
import sys
from datetime import date, time
from urllib.parse import urlparse
from common import ROOT

FIELDS = ['source','date_pt','posted_date_pt','date_precision','location','time_pt','brand','banner_text','post_url','author','has_image','confidence','notes']

def validate(root=ROOT):
    errors=[]
    def fail(where,message):errors.append(f'{where}: {message}')
    def day(value,where,optional=False):
        if optional and not value:return
        try:
            if not isinstance(value,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):raise ValueError()
            date.fromisoformat(value)
        except (ValueError,TypeError):fail(where,'expected a real YYYY-MM-DD date')
    def url(value,where,optional=False):
        if optional and not value:return
        try:
            if not isinstance(value,str):raise ValueError()
            parsed=urlparse(value)
            if parsed.scheme not in ('https','http') or not parsed.hostname or parsed.username or any(c.isspace() for c in value):raise ValueError()
        except (ValueError,TypeError):fail(where,'expected an http(s) URL')
    def read(name):
        try:return json.loads((root/'data'/name).read_text())
        except (ValueError,OSError) as exc:fail(name,str(exc));return None
    brands=read('brands.json')
    if not isinstance(brands,dict):fail('brands.json','expected an object');brands={}
    for key,brand in brands.items():
        where=f'brands.json {key}'
        if not isinstance(brand,dict):fail(where,'expected an object');continue
        for field in ('match','url','logo','color','description'):
            if field not in brand:fail(where,f'missing {field}')
        for field in ('match','description'):
            if not isinstance(brand.get(field),str) or not brand[field].strip():fail(where,f'{field} must be text')
        url(brand.get('url'),where+' url')
        if not re.fullmatch(r'#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?',str(brand.get('color',''))):fail(where,'color must be a hex color')
        logo=brand.get('logo')
        if logo is not None and (not isinstance(logo,str) or not re.fullmatch(r'logos/[\w-]+\.(png|jpg|svg|webp)',logo) or not (root/'site'/logo).is_file()):fail(where,'logo must name an existing local logo')
    with (root/'data/sightings.csv').open(newline='') as handle:
        reader=csv.DictReader(handle)
        if reader.fieldnames != FIELDS:fail('sightings.csv','unexpected columns');return errors
        for number,row in enumerate(reader,2):
            where=f'sightings.csv:{number}'
            if None in row or any(value is None for value in row.values()):fail(where,'wrong number of fields');continue
            if row['date_precision'] not in ('day','unknown'):fail(where,'date_precision must be day or unknown')
            if row['date_precision']=='day':day(row['date_pt'],where+' date_pt')
            elif row['date_pt']:fail(where,'unknown dates must leave date_pt blank')
            day(row['posted_date_pt'],where+' posted_date_pt',optional=True)
            if row['location'] not in ('sf','outside-sf','uncertain'):fail(where,'invalid location')
            if row['confidence'] not in ('high','medium','low'):fail(where,'invalid confidence')
            if row['has_image'] not in ('yes','no',''):fail(where,'has_image must be yes/no or blank')
            if row['time_pt']:
                try:time.fromisoformat(row['time_pt'])
                except ValueError:fail(where,'invalid source time_pt')
            url(row['post_url'],where+' post_url',optional=True)
            if not row['brand'].strip():fail(where,'brand required; use unknown if unsure')
            if not row['source'].strip():fail(where,'source required')
    flights=read('flights.json')
    if not isinstance(flights,list):fail('flights.json','expected a list');flights=[]
    seen=set()
    for index,flight in enumerate(flights):
        where=f'flights.json[{index}]'
        if not isinstance(flight,dict):fail(where,'expected an object');continue
        day(flight.get('date'),where)
        tail=flight.get('tail')
        if not isinstance(tail,str) or not re.fullmatch(r'[A-Z0-9-]+',tail):fail(where,'invalid aircraft registration')
        identity=(str(tail),str(flight.get('date')))
        if identity in seen:fail(where,'duplicate aircraft/date')
        seen.add(identity)
        for field in ('hours_over_sf','median_kt','median_alt_ft'):
            value=flight.get(field)
            if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0:fail(where,f'invalid {field}')
        for field in ('start','end'):
            try:time.fromisoformat(flight.get(field,''))
            except (ValueError,TypeError):fail(where,f'invalid {field}')
        track=flight.get('track')
        if not isinstance(track,list) or len(track)<2:fail(where,'track requires two or more positions');continue
        for point in track:
            if not isinstance(point,list) or len(point)!=2 or any(isinstance(n,bool) or not isinstance(n,(int,float)) or not math.isfinite(n) for n in point) or not (-90<=point[0]<=90 and -180<=point[1]<=180):fail(where,'invalid track coordinates');break
    vendors=read('vendors.json')
    if not isinstance(vendors,dict):fail('vendors.json','expected an object');vendors={}
    for group in ('featured','vendors'):
        records=vendors.get(group)
        if not isinstance(records,list):fail('vendors.json',f'{group} must be a list');continue
        for index,vendor in enumerate(records):
            where=f'vendors.json {group}[{index}]'
            if not isinstance(vendor,dict):fail(where,'expected an object');continue
            for field in ('name','location','services','notes','evidence'):
                if not isinstance(vendor.get(field),str):fail(where,f'{field} must be text')
            url(vendor.get('url'),where+' url')
            if not isinstance(vendor.get('sources'),list):fail(where,'sources must be a list')
            else:
                for source in vendor['sources']:url(source,where+' source')
    return errors

if __name__=='__main__':
    errors=validate()
    print('\n'.join(errors) if errors else 'Data valid')
    sys.exit(bool(errors))
