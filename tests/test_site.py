import csv
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from common import load_data, json_text
from detect import candidates
from validate import validate, FIELDS

class ScriptParser(HTMLParser):
    def __init__(self):super().__init__();self.scripts=0
    def handle_starttag(self,tag,attrs):
        if tag=='script':self.scripts+=1

class ArchiveTests(unittest.TestCase):
    def test_generated_pages_keep_vercel_analytics(self):
        for path in (ROOT/'site').glob('*.html'):
            with self.subTest(page=path.name):
                html=path.read_text()
                self.assertEqual(html.count('<script defer src="/_vercel/insights/script.js"></script>'),1)
                self.assertEqual(html.count('window.va = window.va || function ()'),1)
                self.assertIn('(window.vaq = window.vaq || []).push(arguments)',html)

    def test_reposts_do_not_create_extra_days(self):
        data=load_data()
        paid={item['date']:item for item in data['entries'] if item['brand']=='Paid' and item['date']}
        self.assertNotIn('2026-05-15',paid)
        self.assertNotIn('2026-05-16',paid)
        self.assertEqual(len(paid['2026-05-14']['sources']),3)
        self.assertEqual({s['posted'] for s in paid['2026-05-14']['sources']},{'2026-05-14','2026-05-15','2026-05-16'})

    def test_outside_sf_and_uncertain_dates_do_not_enter_calendar(self):
        data=load_data()
        self.assertFalse(any(item['brand']=='Paid' and item['date']=='2026-05-13' for item in data['entries']))
        retrospective=next(item for item in data['entries'] if any('2110021698330542255' in source['url'] for source in item['sources']))
        self.assertEqual(retrospective['date'],'')
        self.assertFalse(any(item['date']=='2026-02-02' for item in data['entries']))  # flight-only day

    def test_same_day_flights_remain_unattributed(self):
        flights=[f for f in load_data()['flights'] if f['date']=='2026-10-05']
        self.assertTrue(flights)
        self.assertTrue(all('Apify' in flight['candidates'] for flight in flights))
        self.assertTrue(all('brand' not in flight and 'match' not in flight for flight in flights))

    def test_json_script_cannot_be_closed_by_contributed_text(self):
        payload={'notes':'</script><script>/*review probe*/</script><img src=x onerror=alert(1)> &'}
        encoded=json_text(payload)
        parser=ScriptParser();parser.feed('<script type="application/json">'+encoded+'</script>')
        self.assertEqual(parser.scripts,1)
        self.assertEqual(json.loads(encoded),payload)

    def test_invalid_contribution_dates_and_urls_fail(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            shutil.copytree(ROOT/'data',root/'data')
            shutil.copytree(ROOT/'site/logos',root/'site/logos')
            path=root/'data/sightings.csv'
            with path.open(newline='') as handle:rows=list(csv.DictReader(handle))
            rows[-1]['date_pt']='2026-02-30';rows[-1]['post_url']='javascript:alert(1)'
            with path.open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=FIELDS);writer.writeheader();writer.writerows(rows)
            errors=validate(root)
            self.assertTrue(any('real YYYY-MM-DD' in error for error in errors))
            self.assertTrue(any('http(s) URL' in error for error in errors))

    def test_safe_full_build_with_future_sighting_and_markup(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for directory in ('data','scripts','site'):shutil.copytree(ROOT/directory,root/directory)
            path=root/'data/sightings.csv'
            with path.open(newline='') as handle:rows=list(csv.DictReader(handle))
            row=dict(rows[-1],date_pt='2026-11-01',notes='</script><script>/*probe*/</script>',banner_text='<img src=x onerror=alert(1)>')
            rows.append(row)
            with path.open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=FIELDS);writer.writeheader();writer.writerows(rows)
            subprocess.run([sys.executable,'scripts/build_all.py'],cwd=root,check=True,capture_output=True)
            html=(root/'site/index.html').read_text()
            self.assertNotIn('<script>/*probe*/</script>',html)
            self.assertNotIn('<img src=x onerror=alert(1)>',html)
            self.assertIn('2026-11-01',html)
            self.assertIn('Latest report: Nov 1, 2026',html)

class FlightTests(unittest.TestCase):
    def make_trace(self):
        timestamp=datetime(2026,10,1,16,tzinfo=timezone.utc).timestamp()
        points=[]
        for minute in range(0,30):points.append([minute*60,37.68,-122.35,'ground',0])
        for minute in range(30,91):points.append([minute*60,37.77,-122.43,1000,50])
        for minute in range(91,120):points.append([minute*60,37.68,-122.35,'ground',0])
        return dict(timestamp=timestamp,trace=points)

    def test_ground_reports_do_not_inflate_airborne_hours(self):
        result=candidates(self.make_trace(),'aa3b5a')
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['hours_over_sf'],1)
        self.assertEqual(result[0]['airborne_hours'],1)

    def test_reception_gap_is_not_counted_as_flight_time(self):
        trace=self.make_trace()
        trace['trace']=[p for p in trace['trace'] if not 45*60<=p[0]<=75*60]
        self.assertEqual(candidates(trace,'aa3b5a'),[])

    def test_empty_input_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);out=root/'flights.json';out.write_text('["keep"]')
            result=subprocess.run([sys.executable,str(ROOT/'scripts/detect.py'),'--input',td,'--output',str(out)],capture_output=True)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(out.read_text(),'["keep"]')

if __name__=='__main__':unittest.main()
