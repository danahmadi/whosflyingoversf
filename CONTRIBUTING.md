# Add a sighting or correct a report

Use the [sighting form](https://github.com/danahmadi/whosflyingoversf/issues/new?template=sighting.yml), or email hello@sfbannerplanes.com. Include the date, neighborhood, words you could read and a source link or photo. Leave the advertiser blank if you are unsure. Reports appear after review.

## Data PRs

Edit `data/sightings.csv`, preserving the header. One row represents one source. Several sources can describe the same brand on the same day; the site combines them.

- `date_pt`: flight date in America/Los_Angeles, formatted YYYY-MM-DD. If a May 15 post says “yesterday,” use May 14.
- `posted_date_pt`: publication date, if known. Keep it separate from the flight date.
- `date_precision`: `day` when the source establishes the day, otherwise `unknown` with a blank `date_pt`. “Last week” does not establish a day.
- `location`: `sf`, `outside-sf` or `uncertain`. San Mateo and other Bay Area cities do not count as SF. Choose `uncertain` when the source cannot establish the location.
- `time_pt`: original source/post time, if known. Do not infer a flight time from it.
- `brand`: an existing brand name, or `unknown`. Separate multiple brands with `;` only if the source describes both.
- `banner_text`: the words the source reports. Leave blank when unreadable; do not invent the wording.
- `post_url`, `author`, `source`: public source link and attribution. Direct reader reports may omit a link; the site labels them.
- `has_image`: `yes`, `no`, or blank when unknown. A linked photo does not by itself establish a flight date.
- `confidence`: `high` for a clear banner photo/wording or a firsthand advertiser account; `medium` for a plausible named report; `low` for jokes, vague references or inferred brands. Low-confidence rows stay out of the site.
- `notes`: what the source establishes, what is uncertain, and the basis for any date correction.

To add a brand, include `match`, `url`, `logo`, `color` and `description` in `data/brands.json`. `logo` can be null or an existing path under `site/logos/`. Use one factual sentence in the description and a source on the company's own website. Keep marketing claims out of it.

Run:

```sh
python3 scripts/build_all.py
python3 -m unittest discover -s tests -v
node --test tests/*.cjs
```

Commit the source data and regenerated files. Review the Vercel preview, including the evidence for any corrected dates. Do not merge while validation is failing. Source changes and generated output must agree.

## Aircraft tracks

A same-day sighting does not prove that a particular aircraft carried that advertiser's banner. Keep flight candidates separate from confirmed sightings. The map lists possible same-day brands without assigning the flight to one of them.

Do not include private contact details or information about bystanders. Attach only photos you have permission to share.
