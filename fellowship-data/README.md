# Fellowship data — The Fellowship Portal

Total in `index.html`: 2031 programmes.

Researched 3 October 2026 from official institution pages only (no aggregators).

| File | Contents |
|---|---|
| `programs.csv` / `.json` | The 331 programmes already on thefellowshipportal.com, with missing/vague fields filled from official sources. `research_status` = updated / no_new_info / source_unreachable. |
| `changes.csv` | Every field change: old value, new value, source URL. |
| `new_programs.csv` / `.json` | 1700 new programmes across 16 specialties (Internal Medicine 300, Anaesthesiology 247, Radiology 194, Obstetrics & Gynaecology 188, General Surgery 166, Orthopaedics 155, Paediatrics 66, Cardiology 61, Ophthalmology 56, ENT / Otolaryngology 44, Neurosurgery 44, Emergency Medicine 39, Urology 39, Cardiothoracic Surgery 38, Plastic Surgery 38, Dermatology 25). |

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
- Expiring soon / closed adverts: Moorfields glaucoma fellow (NHS Jobs, closes 8 Oct 2026), Chelsea & Westminster ortho advert (18 Oct 2026), RCS register posts with approval ending Nov–Dec 2026, several closed NHS/Australian adverts (marked in title or Deadline).
- GOSH International Medical Fellowship appears under Paediatrics, Ophthalmology and ENT; neuroendovascular programmes appear under both Neurosurgery and Radiology.
- Pages read through an alternate fetcher because they block automated requests (Hopkins, UCSF, Michigan, Mount Sinai, CHOP, Penn, Weill Cornell, RCS England, RCH Melbourne…) may look broken to a link checker but are official URLs.
