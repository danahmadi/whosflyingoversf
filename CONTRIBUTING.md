# Contributing
1. **Report a sighting:** open an issue using the *Report a sighting* template (date, brand, banner text, source URL, photo).
2. **Pull request:** add a row to `data/sightings.csv` following the schema in the README. Use PT dates, copy banner text verbatim, and link a public source. CI checks the CSV.
3. **New brand:** add an entry to `data/brands.json` (name, `match` prefix, `url`, a factual one-line `description` from the brand's own site, and `logo`, optionally a PNG in `site/logos/`).
4. **Unknown flights ("?")**: if you know which brand flew on a "?" day, open an issue with your evidence.
Please don't add private info about pilots or bystanders.
