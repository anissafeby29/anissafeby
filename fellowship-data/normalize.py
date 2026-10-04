"""Canonical labels for subspecialties and institutions.

The raw subspecialty stays available as the programme's "Focus" when it is more specific
than the canonical label. The raw institution name stays as the display name; `org`
groups sites of the same university or health system.
"""
import re

# (specialty or "*", regex on lower-cased raw label, canonical label). First match wins.
SUB_RULES = [
    ("Anaesthesiology", r"regional|acute pain", "Regional anaesthesia & acute pain"),
    ("Anaesthesiology", r"chronic pain|pain medicine", "Chronic pain medicine"),
    ("Anaesthesiology", r"paediatric cardiac|pediatric cardiac", "Paediatric cardiac anaesthesia"),
    ("Anaesthesiology", r"paediatric|pediatric", "Paediatric anaesthesia"),
    ("Anaesthesiology", r"thoracic|cardiothoracic|cardiac|echocardio", "Cardiothoracic anaesthesia"),
    ("Anaesthesiology", r"obstetric", "Obstetric anaesthesia"),
    ("Anaesthesiology", r"critical care", "Critical care anaesthesia"),
    ("Anaesthesiology", r"neuro", "Neuroanaesthesia"),
    ("Anaesthesiology", r"transplant", "Transplant anaesthesia"),
    ("Anaesthesiology", r"periop|ultrasound|pocus", "Perioperative medicine"),
    ("Anaesthesiology", r"simulation|education", "Simulation & medical education"),
    ("Anaesthesiology", r"quality|safety|informatics", "Quality, safety & informatics"),
    ("Anaesthesiology", r"research|malignant hyperthermia", "Clinical research"),
    ("Anaesthesiology", r"global", "Global health"),
    ("Anaesthesiology", r"airway", "Airway management"),
    ("Anaesthesiology", r"trauma|burn", "Trauma & burns anaesthesia"),
    ("Anaesthesiology", r"onco", "Oncological anaesthesia"),
    ("Anaesthesiology", r"hyperbaric", "Undersea & hyperbaric medicine"),
    ("Anaesthesiology", r".", "Advanced clinical anaesthesia"),
    ("Cardiology", r"electrophys|pacing|devices", "Electrophysiology & devices"),
    ("Cardiology", r"structural", "Interventional & structural cardiology"),
    ("Cardiology", r"interventional|cto|pci", "Interventional & structural cardiology"),
    ("Cardiology", r"heart failure|transplant|amyloid|cardiomyopathy", "Heart failure, transplant & cardiomyopathy"),
    ("Cardiology", r"imaging|echo|cmr|nuclear", "Cardiac imaging"),
    ("Cardiology", r"congenital", "Adult congenital heart disease"),
    ("Cardiology", r"onco", "Cardio-oncology"),
    ("Cardiology", r"vascular|peripheral", "Vascular medicine"),
    ("Cardiology", r"prevent|hypertension|sports|women|geriatric", "Preventive & specialty cardiology"),
    ("Cardiology", r"critical", "Cardiac critical care"),
    ("Cardiology", r".", "General cardiology"),
    ("Cardiothoracic Surgery", r"congenital", "Congenital cardiac surgery"),
    ("Cardiothoracic Surgery", r"transplant|mcs|ecmo|circulatory", "Heart & lung transplant / MCS"),
    ("Cardiothoracic Surgery", r"aort", "Aortic surgery"),
    ("Cardiothoracic Surgery", r"thoracic", "General thoracic surgery"),
    ("Cardiothoracic Surgery", r".", "Adult cardiac surgery"),
    ("Dermatology", r"mohs|procedural", "Mohs & procedural dermatology"),
    ("Dermatology", r"dermatopath", "Dermatopathology"),
    ("Dermatology", r"paediatric|pediatric", "Paediatric dermatology"),
    ("Dermatology", r"oncology|melanoma", "Cutaneous oncology"),
    ("Dermatology", r"laser|cosmetic|photo", "Laser, cosmetic & photodermatology"),
    ("Dermatology", r"visiting", "Visiting opportunities"),
    ("Dermatology", r".", "Medical dermatology"),
    ("Emergency Medicine", r"ultrasound", "Emergency ultrasound"),
    ("Emergency Medicine", r"ems|emergency medical services|pre-?hospital|retrieval|hems|aviation|tactical|transport", "Pre-hospital, EMS & retrieval"),
    ("Emergency Medicine", r"admin|operations|leadership|quality|safety|informatics|innovation|digital", "Administration, quality & informatics"),
    ("Emergency Medicine", r"education|simulation", "Medical education & simulation"),
    ("Emergency Medicine", r"global|disaster|wilderness", "Global, disaster & wilderness medicine"),
    ("Emergency Medicine", r"paediatric|pediatric", "Paediatric emergency medicine"),
    ("Emergency Medicine", r"toxicol", "Medical toxicology"),
    ("Emergency Medicine", r"research", "Research"),
    ("Emergency Medicine", r"critical|resusc|trauma", "Resuscitation & critical care"),
    ("Emergency Medicine", r".", "Clinical emergency medicine"),
    ("ENT / Otolaryngology", r"head|neck", "Head & neck oncology"),
    ("ENT / Otolaryngology", r"otolog|neurotolog", "Otology & neurotology"),
    ("ENT / Otolaryngology", r"facial", "Facial plastics"),
    ("ENT / Otolaryngology", r"rhinolog|skull", "Rhinology & skull base"),
    ("ENT / Otolaryngology", r"paediatric|pediatric", "Paediatric ENT"),
    ("ENT / Otolaryngology", r"laryng", "Laryngology"),
    ("ENT / Otolaryngology", r".", "General otolaryngology"),
    ("Neurosurgery", r"vascular|endovascular", "Cerebrovascular & endovascular"),
    ("Neurosurgery", r"skull|pituitary", "Skull base"),
    ("Neurosurgery", r"functional|epilep|pain", "Functional & epilepsy surgery"),
    ("Neurosurgery", r"paediatric|pediatric", "Paediatric neurosurgery"),
    ("Neurosurgery", r"onco", "Neuro-oncology"),
    ("Neurosurgery", r"spine", "Spine"),
    ("Neurosurgery", r".", "General neurosurgery"),
    ("Obstetrics & Gynaecology", r"urogyn", "Urogynecology & reconstructive pelvic surgery"),
    ("Obstetrics & Gynaecology", r"infectious", "Reproductive infectious disease"),
    ("Obstetrics & Gynaecology", r"vulv|lower genital", "Vulvovaginal disease"),
    ("Obstetrics & Gynaecology", r"women's health|menopause|sexual|breast", "Women's health"),
    ("Obstetrics & Gynaecology", r"quality|leadership|rural|hospital medicine", "Hospitalist, quality & leadership"),
    ("Ophthalmology", r"multiple|comprehensive", "Multiple / comprehensive ophthalmology"),
    ("Ophthalmology", r"uveitis|immunology", "Uveitis & ocular immunology"),
    ("Ophthalmology", r"medical retina", "Medical retina"),
    ("Ophthalmology", r"vitreo|retina", "Vitreoretinal surgery"),
    ("Ophthalmology", r"cornea|refractive|cataract|anterior", "Cornea, cataract & refractive"),
    ("Ophthalmology", r"paediatric|pediatric|strabismus|myopia", "Paediatric ophthalmology & strabismus"),
    ("Ophthalmology", r"oncology|pathology|genetic", "Ocular oncology & pathology"),
    ("Ophthalmology", r"research|innovation|imaging|informatics|global|low vision", "Research, global & other"),
    ("Orthopaedics", r"hip preservation|arthroplasty|reconstruction", "Adult reconstruction / arthroplasty"),
    ("Paediatrics", r"cardiac critical", "Cardiac critical care"),
    ("Paediatrics", r"haemat|hemat", "Haematology-oncology"),
    ("Paediatrics", r"multiple", "Multiple paediatric subspecialties"),
    ("Paediatrics", r"child abuse|child protection", "Child abuse paediatrics"),
    ("Paediatrics", r"developmental|neurodevelopmental", "Developmental-behavioural paediatrics"),
    ("Paediatrics", r"global|bioethics|education|pharmacology|obesity|complex care|sports", "Other paediatric fellowships"),
    ("Plastic Surgery", r"craniofacial|cleft", "Craniofacial & cleft"),
    ("Plastic Surgery", r"hand", "Hand & peripheral nerve"),
    ("Plastic Surgery", r"gender", "Gender-affirming surgery"),
    ("Plastic Surgery", r"breast", "Breast reconstruction & microsurgery"),
    ("Plastic Surgery", r"micro", "Reconstructive microsurgery"),
    ("Plastic Surgery", r"aesthetic|cosmetic", "Aesthetic surgery"),
    ("Plastic Surgery", r".", "Burns & reconstructive surgery"),
    ("Radiology", r"paediatric neuro|pediatric neuro", "Paediatric radiology"),
    ("Radiology", r"interventional neuro|neurointerventional|neuroendovascular", "Interventional neuroradiology"),
    ("Radiology", r"paediatric|pediatric", "Paediatric radiology"),
    ("Radiology", r"interventional", "Interventional radiology"),
    ("Radiology", r"neuro|head and neck", "Neuroradiology"),
    ("Radiology", r"abdominal|body|urogenital|cross-sectional", "Abdominal & body imaging"),
    ("Radiology", r"breast|women", "Breast & women's imaging"),
    ("Radiology", r"musculoskeletal", "Musculoskeletal imaging"),
    ("Radiology", r"cardiac|cardiothoracic|thoracic|chest", "Cardiothoracic imaging"),
    ("Radiology", r"nuclear|molecular|pet", "Nuclear medicine & molecular imaging"),
    ("Radiology", r"emergency|trauma", "Emergency radiology"),
    ("Radiology", r"onco", "Oncologic imaging"),
    ("Radiology", r"informatics|ai\b|management|leadership", "Informatics, AI & leadership"),
    ("Radiology", r".", "General & multi-subspecialty radiology"),
    ("Urology", r"onco|robotic", "Urologic oncology & robotics"),
    ("Urology", r"androl|infertil|sexual", "Andrology & sexual medicine"),
    ("Urology", r"paediatric|pediatric", "Paediatric urology"),
    ("Urology", r"endourol|stone", "Endourology & stone disease"),
    ("Urology", r"female pelvic|reconstructive|functional|gender", "Reconstructive & functional urology"),
    ("Urology", r"transplant", "Transplant urology"),
    ("Internal Medicine", r"haemat|hemat|oncolog", "Haematology & oncology"),
    ("Internal Medicine", r"pulmon|respir|critical", "Pulmonary & critical care"),
]

ORG_RULES = [
    (r"university of toronto|sickkids|hospital for sick children|sunnybrook|university health network|toronto (general|western)|princess margaret|mount sinai hospital.*toronto|sinai health|women's college hospital|st\.? michael's hospital|unity health|humber river|north york general|trillium|michael garron|credit valley", "University of Toronto"),
    (r"mcgill|montreal children|jewish general", "McGill University"),
    (r"columbia university|newyork-presbyterian/columbia|morgan stanley children|harlem hospital", "Columbia University / NewYork-Presbyterian"),
    (r"mass general brigham|massachusetts general|brigham and women|\bmgh\b|\bbwh\b|mass eye and ear|dana-farber", "Mass General Brigham"),
    (r"university of michigan|michigan medicine|c\.s\. mott|kellogg eye", "University of Michigan"),
    (r"mayo clinic", "Mayo Clinic"),
    (r"stanford|lucile packard|byers eye", "Stanford Medicine"),
    (r"ucla|david geffen|jules stein", "UCLA Health"),
    (r"ucsf|university of california,? san francisco|benioff", "UCSF"),
    (r"uc san diego|university of california,? san diego|rady children|shiley", "UC San Diego"),
    (r"icahn|mount sinai (?!hospital \(sinai health\))(health system|kravis|morningside|west|beth)?|new york eye and ear", "Mount Sinai (New York)"),
    (r"johns hopkins|wilmer", "Johns Hopkins"),
    (r"children's hospital of philadelphia|\bchop\b", "Children's Hospital of Philadelphia"),
    (r"university of pennsylvania|penn medicine|perelman|scheie", "Penn Medicine"),
    (r"washington university|st\. louis children|mallinckrodt|barnes-jewish", "Washington University in St. Louis"),
    (r"university of washington|harborview|seattle children|fred hutch", "University of Washington"),
    (r"upmc|university of pittsburgh", "UPMC / University of Pittsburgh"),
    (r"nyu|hassenfeld", "NYU Langone"),
    (r"weill cornell|newyork-presbyterian/weill", "Weill Cornell Medicine"),
    (r"northwestern|lurie children|shirley ryan", "Northwestern Medicine"),
    (r"ut southwestern|utsw|children's health dallas", "UT Southwestern"),
    (r"baylor college of medicine|texas children", "Baylor College of Medicine / Texas Children's"),
    (r"cleveland clinic(?! abu dhabi)(?! florida)", "Cleveland Clinic"),
    (r"duke", "Duke University"),
    (r"emory|children's healthcare of atlanta", "Emory University"),
    (r"vanderbilt|monroe carell", "Vanderbilt University Medical Center"),
    (r"yale", "Yale School of Medicine"),
    (r"indiana university|riley hospital", "Indiana University"),
    (r"cincinnati children", "Cincinnati Children's"),
    (r"boston children", "Boston Children's Hospital"),
    (r"children's national", "Children's National"),
    (r"children's hospital colorado|cu anschutz|university of colorado", "University of Colorado"),
    (r"medical college of wisconsin|children's wisconsin", "Medical College of Wisconsin"),
    (r"university of british columbia|\bubc\b|bc children|vancouver general|st\.? paul's hospital", "University of British Columbia"),
    (r"university of calgary|alberta children|foothills", "University of Calgary"),
    (r"university of alberta|stollery|mazankowski", "University of Alberta"),
    (r"university of ottawa|ottawa hospital|cheo|children's hospital of eastern ontario|ottawa heart", "University of Ottawa"),
    (r"mcmaster|hamilton health sciences|juravinski", "McMaster University"),
    (r"western university|schulich|london health sciences|children's hospital, london", "Western University"),
    (r"great ormond street|gosh", "Great Ormond Street Hospital"),
    (r"moorfields", "Moorfields Eye Hospital"),
    (r"royal children's hospital melbourne|rch melbourne", "Royal Children's Hospital Melbourne"),
    (r"university hospitals leuven|uz leuven", "UZ Leuven"),
    (r"university hospital zurich|universitätsspital zürich|\busz\b", "University Hospital Zurich"),
    (r"singapore national eye|snec", "Singapore National Eye Centre"),
    (r"kk women|kkh", "KK Women's and Children's Hospital"),
    (r"national university hospital|nuhs|national university health system", "National University Hospital Singapore"),
    (r"chinese university of hong kong|cuhk|hong kong eye hospital|prince of wales hospital", "CUHK / Hong Kong Eye Hospital"),
    (r"hamad medical", "Hamad Medical Corporation"),
    (r"sidra", "Sidra Medicine"),
]


def canon_sub(specialty, raw):
    raw = (raw or "").strip()
    low = raw.lower()
    for sp, rx, label in SUB_RULES:
        if sp in (specialty, "*") and label and re.search(rx, low):
            return label
    # Generic tidy-up: drop parenthetical detail and secondary parts after " / ".
    base = re.sub(r"\s*\(.*?\)", "", raw).split(" / ")[0].strip()
    return base or raw


def canon_org(inst, country=""):
    low = (inst or "").lower()
    if "mount sinai" in low and country == "Canada":
        return "University of Toronto"
    for rx, label in ORG_RULES:
        if re.search(rx, low):
            return label
    return inst


# Internal Medicine subspecialties that have their own specialty pages.
SPLIT = [
    ("Gastroenterology & Hepatology", r"gastro|hepat|liver|endoscop|\beus\b|ercp|\bibd\b|inflammatory bowel|motility|pancrea", [
        (r"transplant hepat|liver transplant", "Transplant hepatology"), (r"hepat|liver", "Hepatology"),
        (r"endoscop|\beus\b|ercp", "Advanced endoscopy (EUS/ERCP)"), (r"\bibd\b|inflammatory bowel", "Inflammatory bowel disease"),
        (r"motility|neurogastro", "Neurogastroenterology & motility"), (r"nutrition", "Clinical nutrition"), (r"pancrea", "Pancreatobiliary")],
     "General gastroenterology"),
    ("Haematology & Medical Oncology", r"haemat|hemat|oncolog|\bbmt\b|stem cell|marrow|cellular therap|leuk|lymphoma|myeloma|thromb", [
        (r"\bbmt\b|stem cell|marrow|cellular therap", "Bone marrow transplant & cellular therapy"),
        (r"thromb|haemostasis|hemostasis", "Thrombosis & haemostasis"), (r"leuk|lymphoma|myeloma|malignan", "Haematological malignancies"),
        (r"breast", "Breast oncology"), (r"thoracic|lung", "Thoracic oncology"), (r"genitourinary|\bgu\b|prostate", "Genitourinary oncology"),
        (r"gastrointestinal|\bgi\b", "GI oncology"), (r"genetic", "Cancer genetics"),
        (r"^(?!.*hemat)(?!.*haemat).*medical oncology", "Medical oncology"), (r"^(?!.*onco).*(haemat|hemat)", "Haematology")],
     "Hematology & oncology"),
    ("Nephrology", r"nephro|kidney|renal|dialysis|glomerul", [
        (r"transplant", "Transplant nephrology"), (r"interventional", "Interventional nephrology"), (r"critical", "Critical care nephrology"),
        (r"glomerul", "Glomerular disease"), (r"dialysis|home therap", "Dialysis & home therapies"), (r"onco", "Onconephrology")],
     "General nephrology"),
]


def split_specialty(specialty, raw, canon):
    """Move Internal Medicine GI / haem-onc / nephrology programmes to their own specialty; tidy their subspecialty."""
    text = f"{raw} {canon}".lower()
    for new, rx, subs, default in SPLIT:
        if specialty == new or (specialty == "Internal Medicine" and re.search(rx, text)):
            sub_text = (raw or canon or "").lower()
            for srx, label in subs:
                if re.search(srx, sub_text):
                    return new, label
            return new, default
    return specialty, canon
