# Fellowship data pipeline

Everything needed to rebuild thefellowshipportal.com from source data.

```
pipeline/
  sources/base_programs.json   331 programmes scraped from the original site
  sources/results/r*.json      field updates for those 331 (with sources)
  sources/new/*_all.json etc.  programmes added since, one file per research batch
  sources/patches/*.json       gap-fill patches: {"patches":[{slug, field, value, source, level}]}
  prompts/new_programmes.txt   brief for agents that add programmes (24-key schema)
  prompts/gap_fill.txt         brief for agents that fill missing fields
  merge.py                     sources -> fellowship-data/{programs,new_programs,changes}.*
  publish.sh                   merge + build index.html, profiles, landing pages, sitemap -> push both repos
```

`publish.sh` expects the site repo `anissafeby29/thefellowshipportal` cloned next to this repo
(override with `PORTAL_REPO=/path`). Hostinger auto-deploys the site repo's `main` branch to `public_html`.

## Site pages built from the data
- `fellowship-data/profiles.py`: one profile per programme (`/programs/<slug>/`), About, Contact, sitemap.
- `fellowship-data/pages.py`: `/specialties/`, `/countries/`, `/training/`, `/institutions/` (one page per institution),
  `/deadlines/` (upcoming dates parsed from the Deadline field), `/compare/` (shortlist), 404 page and old-URL redirects.
- `fellowship-data/flags.py`: turns International applicants / Visa support text into the "Open to IMGs" and "Visa route" filters.

## Rules for any new data
- Official sources only: the institution's own page, its GME/postgraduate office, an official college,
  society or match service. No aggregators (FREIDA, Doximity, ResidencyAdvisor, job boards other than NHS Jobs / hospital careers).
- Never invent. A field the official page does not state is "Not stated on official page".
- Patches only fill missing/vague fields; they never overwrite a concrete value (merge.py enforces this).
- Institution-wide values start with "Institution policy: ".

## Monthly refresh
1. Build a worklist of programmes whose Deadline, Start or Positions are missing, or whose Deadline mentions a past cycle.
2. Run gap-fill agents with `prompts/gap_fill.txt` (paths: replace `<PIPELINE>` with this folder); save to `sources/patches/refresh-YYYY-MM.json`.
3. Re-check adverts marked "(NHS Jobs advert)" / "(job advert)" and update their Deadline.
4. `pipeline/publish.sh "Monthly refresh YYYY-MM"`.
