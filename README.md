# whosflyingoversf — Who's flying over SF?

A public, community-maintained calendar of the brands that tow aerial banners over **San Francisco**, with evidence for each day, flight tracks from open ADS-B data, and rough cost/fuel/CO₂ estimates.

Site: https://whosflyingoversf.com (sfbannerplanes.com redirects). Built from `data/` by the scripts in `scripts/`, committed to `site/` and served as static files by Vercel (push to `main` = production). After editing `data/`, run `python scripts/build_all.py` and commit `site/` too; CI fails if it is stale.

## Data
| File | What |
|---|---|
| `data/sightings.csv` | One row per public piece of evidence (post, article, thread) |
| `data/brands.json` | Advertiser metadata: name, match prefix, url, logo, color, description |
| `data/flights.json` | Banner-tow flights detected from the adsb.lol open archive (derived) |

### `sightings.csv` schema
`source` (X/LinkedIn/Reddit/News/Dan), `date_pt` (YYYY-MM-DD, America/Los_Angeles), `time_pt`, `brand`, `banner_text` (only as stated in the source, never guessed), `post_url`, `author`, `has_image` (yes/no), `confidence` (high/medium/low), `notes`.

### Confidence rules
- **high**: photo of the banner, quoted banner text, or the advertiser itself says it flew that day.
- **medium**: names the brand without a photo, or the date is "yesterday"/"this week" style.
- **low**: jokes, vague references, or the brand is inferred. Low rows are kept but not shown on the site.
- Sightings outside SF proper (South Bay, San Mateo, Alameda…) are kept in the CSV but left off the calendar and stats.

### Flights
`scripts/detect.py` scans daily `trace_full_<icao>.json` files for the tracked banner-tow tails and keeps segments that loiter low (<3,500 ft median) and slow (<85 kt median) for at least 45 minutes inside an SF bounding box. Each flight gets matched to the brands seen that same day: a single brand is a match, several brands make it *ambiguous*, and no brand means *unknown* (shown as "?" on the calendar). Raw archives are not committed.

## Methodology (stats)
Day counts are a **floor**. Estimates use 4–6 h/day, $4.5k–9k/day, 7–12 gal/h of 100LL, and 8.31 kg CO₂/gal (EPA). Real ADS-B hours are shown wherever a flight was detected. Sources are cited on the stats page.

## Social preview image & favicon
`site/og.png` (1200×630) and `site/favicon.{svg,ico}` are generated, not hand-edited. Regenerate them with `python scripts/make_og_image.py` (renders HTML with headless Chrome/Chromium — set `CHROME_BIN` if it's not on `PATH`) and `python scripts/make_favicon.py` (Pillow only), then commit the results. Every page's Open Graph/Twitter meta tags are injected by `scripts/theme.py` as part of `build_all.py`, so they're regenerated automatically whenever the site is rebuilt.

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). The quickest way: open a **Report a sighting** issue.

## License
Code: MIT (`LICENSE`). Data in `data/`: CC-BY-4.0 (`data/LICENSE`).
