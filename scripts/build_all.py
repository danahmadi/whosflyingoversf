"""Generate the committed static site from repository data."""
import subprocess
import sys
from common import ROOT
for script in ('validate.py','build_site.py','build_stats.py','build_map.py','build_fly.py','build_meta.py'):
    subprocess.check_call([sys.executable,str(ROOT/'scripts'/script)],cwd=ROOT)
