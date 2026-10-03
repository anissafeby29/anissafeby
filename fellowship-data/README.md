# Fellowship data — The Fellowship Portal

Researched 3 October 2026 from official institution pages only (no aggregators).

| File | Contents |
|---|---|
| `programs.csv` / `.json` | The 331 programmes already on thefellowshipportal.com, with missing/vague fields filled from official sources. `research_status` = updated / no_new_info / source_unreachable. |
| `changes.csv` | Every field change: old value, new value, source URL. |
| `new_programs.csv` / `.json` | 346 new programmes: 197 Anaesthesiology, 149 Radiology (US, Canada, UK, Australia, Ireland, Germany, Switzerland, Belgium). |

"Not stated on official page" means the official page was checked and does not give that information.

## Check before publishing
- Entries whose `notes` mention search results / blocked pages (403): City of Hope, Michigan (×3), Moffitt, Hopkins Wilmer Vision Rehab, Northwell (×3) — values came from official-domain search snippets, not a full page read.
- UK posts sourced from NHS Jobs adverts (anaesthesia and radiology) are recurring/closed adverts, not standing programme pages.
- Short courses / exchange schemes in new radiology (USZ, ESOR/ESHI, CIRSE grant) are labelled as such in `Training type`.
- New subspecialty labels not yet on the site (e.g. "Oncologic imaging", "Cross-sectional imaging", "Oncological anaesthesia") may need mapping.
- `/programs/oncology-fellowship` on the live site does not load.
