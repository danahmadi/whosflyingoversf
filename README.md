# Who's flying over SF?

A community archive of the banners above San Francisco: the words people saw, the date, and the source. [whosflyingoversf.com](https://whosflyingoversf.com)

The homepage has a calendar, sightings list and flight map. Selecting a calendar date filters the map to that day and lists its sightings; dates with recorded tracks have a dot. Share a filtered view with `/?date=YYYY-MM-DD`, or reset the map to all dates. Both maps can filter to tracks recorded on days a selected brand was sighted. Brand filters are saved in `?brand=Monaco` and can combine with a selected date; they do not confirm which aircraft carried a banner or where the advertiser intended to target. Reports without an established flight date stay in a separate section. The flight map shows candidate banner-tow tracks; a brand seen on the same day is a lead, not a confirmed aircraft match.

The map opens at zoom 11 with a blue-to-red heatmap calibrated to reserve warm colors for the densest recorded positions. Its intensity compensates for zoom so close-up routes retain their heat. The full map’s track checkbox adds clear individual flight lines; selecting a homepage calendar day isolates that day’s lines. On devices with a mouse, a small 3D Cessna follows the cursor in wide repeated passes. The footer has a pause control, and the animation stops for reduced-motion preferences and background tabs. The plane is rendered locally in Canvas with no model download or additional library.

## Build and contribute

No Node app, build service or environment variables. Vercel serves the committed `site/` folder. Python 3.12+ and the standard library generate the HTML and data files.

```sh
python3 scripts/build_all.py
python3 -m unittest discover -s tests -v
node --test tests/*.cjs
```

Node 22+ runs the browser-control regression checks with built-in test APIs; no npm install is needed. It is not part of the site build.

Commit the data and generated `site/` changes together. CI validates data, runs regression tests, rebuilds the pages and rejects stale generated files. Vercel creates PR previews and deploys `main` to production. CI must pass before merging; Vercel's build itself does not run Python validation.

To report a sighting, use the [issue form](https://github.com/danahmadi/whosflyingoversf/issues/new?template=sighting.yml). For data changes, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Data files

- `data/sightings.csv`: one row per source or direct report. Reposts can describe the same sighting.
- `data/brands.json`: names, matching prefixes, short descriptions, links and logos.
- `data/flights.json`: legacy candidate tracks derived from the adsb.lol archive. The raw traces are not committed. Existing durations have not been reprocessed with the corrected detector and are excluded from public estimates.
- `data/vendors.json`: operator and broker references.

### Dates and locations

`date_pt` is the **observed flight date**, when known. `posted_date_pt` preserves the source's publication date. `date_precision` is `day` or `unknown`; unknown dates leave `date_pt` empty. `time_pt` is the original source/post time, not a verified flight time.

`location` is `sf`, `outside-sf` or `uncertain`. Only `sf` rows with medium/high confidence enter the site. Low-confidence references and other locations stay in the CSV. A report's confidence does not establish its date, its location, or which aircraft carried the banner.

The initial date/location corrections use the existing research notes, with publication dates preserved. They are not a fresh independent verification of every linked post. Audit any source you change and describe the evidence in your PR.

### Flight traces

```sh
bash scripts/get.sh 2026.10.05
python3 scripts/detect.py --input adsb --output data/flights.json
python3 scripts/build_all.py
```

The downloader fetches the split daily archive and extracts the tracked aircraft into ignored `adsb/`. It downloads a large archive; it is separate from the normal site build. The detector sums short observed airborne intervals inside the SF box, excludes ground observations and gaps over two minutes, and requires at least 45 minutes of qualifying coverage per aircraft/day. Missing coverage is unknown time. Back up or version your input set before regenerating: the output covers only the traces you supply.

## Public estimates

The site publishes dated sighting counts, source links, and clearly labeled campaign pricing examples. It does not assign inferred tracks to an advertiser or publish per-brand spending, fuel or carbon totals.

Code: MIT. Data in `data/`: CC BY 4.0. Photos retain their original licenses; credits appear on the site and in `site/assets/credits.json`. Brand marks belong to their owners.

Share artwork and favicon assets are checked in. To regenerate them, install Pillow and run `python3 scripts/make_og_image.py` and `python3 scripts/make_favicon.py`; these are separate from the standard-library site build.

### Outbound referral links

Rendered external HTTP(S) website links receive `utm_source=whosflyingoversf.com`, including links added by sighting dialogs, map popups and map credits. The build decorates static anchors; `site/outbound.js` covers dynamically inserted or updated anchors. URL fixtures test the same policy in Python and JavaScript. Source data and asset requests are not rewritten.

An existing `utm_source` (including empty or differently cased keys) wins and is left byte-for-byte intact. Other query parameters and fragments retain their original encoding and values. Internal links, domain aliases, mail/phone links, downloads and common asset extensions are excluded; GitHub `/blob/` links are website viewers.

Known signature/auth/expiry query keys are conservatively excluded to avoid invalidating signed URLs. Custom or path-based signatures cannot be identified reliably from a URL alone: mark those anchors `data-no-referral`. This also provides an explicit opt-out for extensionless assets; use `download` for actual download links. No signed outbound website URLs were found in the current link inventory.

### Analytics

`site/analytics.js` loads GA4 on the HTTPS production domain only and respects Global Privacy Control and Do Not Track. It retains campaign parameters, strips other query parameters and fragments, and reduces referrers to their origin. Google signals and advertising personalization are disabled. Keep enhanced measurement off in the GA4 web stream so automatic events do not bypass this URL handling. Vercel Analytics remains separate.
