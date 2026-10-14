import csv,json,re,sys
err=[]
B=json.load(open("data/brands.json"))
for k,v in B.items():
    for f in ("match","url","color","description"):
        if f not in v: err.append(f"brands.json {k}: missing {f}")
need=["source","date_pt","time_pt","brand","banner_text","post_url","author","has_image","confidence","notes"]
r=csv.DictReader(open("data/sightings.csv"))
if r.fieldnames!=need: err.append(f"sightings.csv header must be {need}")
for i,row in enumerate(r,2):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}",row["date_pt"] or ""): err.append(f"line {i}: bad date_pt")
    if row["confidence"] not in ("high","medium","low"): err.append(f"line {i}: bad confidence")
    if row["has_image"] not in ("yes","no",""): err.append(f"line {i}: has_image yes/no")
    if row["post_url"] and not row["post_url"].startswith("http"): err.append(f"line {i}: post_url must be a URL")
    if not row["brand"]: err.append(f"line {i}: brand required (use 'unknown')")
json.load(open("data/flights.json"))
print("\n".join(err) or "data OK"); sys.exit(1 if err else 0)
