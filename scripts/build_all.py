import subprocess,sys
for s in ["build_site.py","build_stats.py","build_map.py","build_fly.py"]:
    subprocess.check_call([sys.executable,"scripts/"+s])
subprocess.check_call([sys.executable,"scripts/theme.py"])
