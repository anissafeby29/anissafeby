# Fellowship data — The Fellowship Portal

Researched 3 October 2026 from official institution pages only (no aggregators).

| File | Contents |
|---|---|
| `programs.csv` / `.json` | The 331 programmes already on thefellowshipportal.com, with missing/vague fields filled from official sources. `research_status` = updated / no_new_info / source_unreachable. |
| `changes.csv` | Every field change: old value, new value, source URL. |
| `new_programs.csv` / `.json` | 758 new programmes: 224 Internal Medicine, 197 Anaesthesiology, 188 Obstetrics & Gynaecology, 149 Radiology (US, Canada, UK, Australia/NZ, Ireland, Germany, Switzerland, Belgium). |

"Not stated on official page" means the official page was checked and does not give that information.

## Check before publishing
- Entries whose `notes` mention search results / blocked pages (403): City of Hope, Michigan (×3), Moffitt, Hopkins Wilmer Vision Rehab, Northwell (×3) — values came from official-domain search snippets, not a full page read.
- UK posts sourced from NHS Jobs adverts (anaesthesia and radiology) are recurring/closed adverts, not standing programme pages.
- Short courses / exchange schemes in new radiology (USZ, ESOR/ESHI, CIRSE grant) are labelled as such in `Training type`.
- New subspecialty labels not yet on the site (e.g. "Oncologic imaging", "Cross-sectional imaging", "Oncological anaesthesia") may need mapping.
- `/programs/oncology-fellowship` on the live site does not load.
- UK Medical Training Initiative (MTI) visa route is paused/closed to new applicants (RCP; closed 31 March 2026), so no MTI programmes are listed — check any UK entry that mentions visa help.
- ObGyn NHS Jobs adverts (Somerset, Norfolk & Norwich, Croydon) close 11–15 October 2026.
- Many Canadian ObGyn programmes accept Canadian-trained applicants only (see `International applicants`).
- RCPI (Ireland) international fellowships are open only to government-sponsored Gulf-state applicants.
- Mass General Brigham is merging MGH/BWH programmes (anaesthesia, rheumatology, GI); `inst` names for MGB entries are not yet standardised, and Baylor appears under two names.
