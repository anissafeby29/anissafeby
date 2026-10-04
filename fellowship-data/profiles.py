"""Write one static profile page per programme to <root>/programs/<slug>/index.html, plus sitemap.xml and robots.txt."""
import html
import json
import os
import re
import shutil
from collections import defaultdict

SITE = "https://thefellowshipportal.com"
NS = re.compile(r"^(not stated|check with|confirm current|not specified|contact programme|see official|unknown)", re.I)
ISO = {"United States": "USA", "Canada": "CAN", "United Kingdom": "GBR", "Australia": "AUS", "Ireland": "IRL", "Switzerland": "CHE",
       "Singapore": "SGP", "Germany": "DEU", "Qatar": "QAT", "Belgium": "BEL", "New Zealand": "NZL", "United Arab Emirates": "ARE",
       "India": "IND", "Thailand": "THA", "Lebanon": "LBN", "Hong Kong SAR": "HKG", "Spain": "ESP", "Japan": "JPN", "Netherlands": "NLD",
       "Saudi Arabia": "SAU", "Malaysia": "MYS", "South Korea": "KOR", "Taiwan": "TWN", "Italy": "ITA", "South Africa": "ZAF",
       "Israel": "ISR", "France": "FRA", "Austria": "AUT", "Sweden": "SWE", "Philippines": "PHL", "China": "CHN", "Nepal": "NPL",
       "Sri Lanka": "LKA", "Denmark": "DNK", "Norway": "NOR", "Finland": "FIN", "Europe (multi-country)": "EUR", "International (multi-country)": "INT", "Türkiye": "TUR", "Turkey": "TUR", "Greece": "GRC", "Portugal": "PRT", "Czech Republic": "CZE", "Slovakia": "SVK", "Lithuania": "LTU", "Poland": "POL", "Hungary": "HUN", "Romania": "ROU", "Croatia": "HRV", "Brazil": "BRA", "Mexico": "MEX", "Egypt": "EGY", "Kenya": "KEN", "Pakistan": "PAK", "Bangladesh": "BGD", "Vietnam": "VNM", "Indonesia": "IDN"}
GROUPS = [
    ("The programme", ["Training type", "Duration", "Start", "Positions", "Accreditation", "Department"]),
    ("Eligibility and visa", ["Eligibility", "International applicants", "Visa support", "Licence requirement"]),
    ("How to apply", ["Deadline", "Application method"]),
    ("Funding", ["Funding"]),
]
SCORED = ["Duration", "Start", "Positions", "Accreditation", "Eligibility", "International applicants", "Visa support",
          "Licence requirement", "Deadline", "Application method", "Funding", "Department"]
e = lambda s: html.escape(str(s or ""), quote=True)


# Slugs used by the original site; new specialties fall back to slugify().
SPEC_SLUGS = {"Obstetrics & Gynaecology": "obgyn", "ENT / Otolaryngology": "ent", "Physical Medicine & Rehabilitation": "physical-medicine-rehabilitation"}


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower().replace("&", " and ").replace("ü", "u").replace("é", "e")).strip("-")
    return s or "other"


def spec_slug(s):
    return SPEC_SLUGS.get(s) or slugify(s)


def nav(p):
    return (f'<nav class="toplinks"><a href="{p}specialties/">Specialties</a><a href="{p}countries/">Countries</a>'
            f'<a href="{p}deadlines/">Deadlines</a><a href="{p}compare/" class="savedlink">Saved <span data-saved-count>0</span></a></nav>')


def iso(c):
    return ISO.get(c, (c or "")[:3].upper() or "—")


def known(v):
    return bool(v) and not NS.match(str(v))


def fmt(v):
    if not known(v):
        return '<span class="ns">Not stated on official page</span>'
    v = str(v)
    if v.lower().startswith("institution policy:"):
        return '<span class="inst-tag">Institution policy</span>' + e(v.split(":", 1)[1].strip())
    return e(v)


def status(r):
    f = r["f"]
    intl = str(f.get("International applicants", ""))
    if re.search(r"advert", r["t"], re.I) and re.search(r"closed|past|expired", str(f.get("Deadline", "")) + str(f.get("Start", "")), re.I):
        return '<span class="status warn">Advert closed. Check for the next round</span>'
    if re.search(r"citizens?|permanent residents?", intl, re.I) and re.search(r"only|must be|required|limited to", intl, re.I) and not re.search(r"^yes", intl, re.I):
        return '<span class="status warn">Citizens or permanent residents only</span>'
    if re.match(r"(yes|open|accepted|welcome|international)", intl, re.I):
        return '<span class="status ok">Open to international applicants</span>'
    return ""


def page(r, logo_svg, related, same_inst):
    f = r["f"]
    place = ", ".join(dict.fromkeys(x for x in [r["ci"], f.get("State or region"), r["co"]] if x))
    score = sum(1 for k in SCORED if known(f.get(k)))
    pct = round(100 * score / len(SCORED))
    desc = (r["su"] or f'{r["t"]} at {r["i"]}')[:155]
    title = f'{r["t"]} · {r["i"]} | The Fellowship Portal'
    url = f'{SITE}/programs/{r["s"]}/'
    ld = {"@context": "https://schema.org", "@type": "EducationalOccupationalProgram", "name": r["t"], "description": r["su"] or r["t"],
          "url": url, "provider": {"@type": "Organization", "name": r["i"], **({"url": r["u"][0]} if r["u"] else {})},
          "occupationalCategory": f.get("Specialty"), "educationalProgramMode": f.get("Training type") or None,
          "location": {"@type": "Place", "address": {"@type": "PostalAddress", "addressLocality": r["ci"] or None, "addressRegion": f.get("State or region") or None, "addressCountry": r["co"] or None}}}
    if known(f.get("Duration")):
        ld["timeToComplete"] = f["Duration"]
    groups = "".join(
        f'<section class="panel"><h2>{g}</h2><dl class="facts">' + (f"<dt>Focus</dt><dd>{e(r['focus'])}</dd>" if g == "The programme" and r.get("focus") else "") + "".join(f"<dt>{e(k)}</dt><dd>{fmt(f.get(k))}</dd>" for k in keys) + "</dl></section>"
        for g, keys in GROUPS)
    rel = lambda items, heading: (f'<section class="more"><h2>{heading}</h2><div class="related">' + "".join(
        f'<a class="rel" href="../{x["s"]}/"><span class="code">{iso(x["co"])} · {e(x["f"].get("Subspecialty") or x["f"].get("Specialty"))}</span><b>{e(x["t"])}</b><span>{e(x["i"])}</span></a>'
        for x in items) + "</div></section>") if items else ""
    st = status(r)
    ld_json = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
    sources = "".join(f'<a href="{e(u)}" target="_blank" rel="noopener">{e(u)}</a>' for u in r["u"])
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:title" content="{e(r["t"])}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="https://thefellowshipportal.com/assets/og.png"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="../../assets/logo.svg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<link rel="stylesheet" href="../../assets/profile.css">
<script type="application/ld+json">{ld_json}</script>
<script>try{{var t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
</head>
<body>
<header class="hero"><div class="wrap">
  <div class="top"><a class="brand" href="../../">{logo_svg}<span>The Fellowship Portal</span></a><a class="back" href="../../#results">← All programmes</a>{nav("../../")}</div>
  <nav class="crumbs" aria-label="Breadcrumb"><a href="../../">Home</a><span>›</span><a href="../../specialties/{spec_slug(f.get("Specialty"))}/">{e(f.get("Specialty"))}</a><span>›</span>{f'<a href="../../countries/{slugify(r["co"])}/">{e(r["co"])}</a>' if r["co"] else ""}</nav>
  <div class="headrow">
    <div>
      <h1>{e(r["t"])}</h1>
      <p class="inst"><a href="../../institutions/{r.get("inst_slug", "")}/" style="color:inherit">{e(r["i"])}</a></p>
      <div class="chips"><span class="chip">{e(f.get("Specialty"))}</span>{f'<span class="chip">{e(f["Subspecialty"])}</span>' if f.get("Subspecialty") else ""}{f'<span class="chip gold">{e(f["Training type"])}</span>' if f.get("Training type") else ""}</div>
    </div>
    <div class="dest"><div class="label">Destination</div><div class="code">{iso(r["co"])}</div><div class="where">{e(place)}</div></div>
  </div>
  <div class="cta">{f'<a class="btn primary" href="{e(r["u"][0])}" target="_blank" rel="noopener">Open official programme page ↗</a>' if r["u"] else ""}{f'<a class="btn ghost" href="{e(r["p"])}" target="_blank" rel="noopener">Specialist directory profile ↗</a>' if r.get("p") else ""}<button class="btn save" type="button" data-save="{e(r["s"])}">☆ Save</button><a class="btn ghost" href="../../compare/">Compare saved →</a></div>
</div></header>
<main class="wrap">
  <div class="grid">
    <div>
      {f'<section class="panel"><h2>Overview</h2><p class="summary">{e(r["su"])}</p></section>' if r["su"] else ""}
      {groups}
      <section class="panel"><h2>Official sources</h2><div class="sources">{sources}</div>{f'<div class="note">{e(r["n"])}</div>' if r.get("n") else ""}</section>
    </div>
    <aside class="side">
      <section class="panel"><div class="label">Profile completeness</div><div class="big">{score}/{len(SCORED)}</div><div class="meter"><i style="width:{pct}%"></i></div><p>Key details found on the official page. Gaps mean the page does not publish them.</p></section>
      <section class="panel"><div class="label">Status</div>{st or '<p>Check the official page for the current intake.</p>'}<p style="margin-top:10px">Last verified: {e(f.get("Last verified") or "October 2026")}</p></section>
      <section class="panel"><div class="label">Before you apply</div><p>Requirements, dates and visa rules change. Confirm every detail on the official page and contact the programme coordinator if anything is unclear.</p></section>
    </aside>
  </div>
  {rel(related, "Similar programmes")}
  {rel(same_inst, "More at " + e(r.get("org") or r["i"]))}
  <footer>The Fellowship Portal lists fellowships from official institution sources. Spotted an error? <a href="../../contact/">Contact us</a> so we can update this profile. · <a href="../../about/">About</a></footer>
</main>
<script src="../../assets/save.js" defer></script>
</body>
</html>'''


def write_all(records, logo, root, here):
    out = os.path.join(root, "programs")
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(root, "assets"), exist_ok=True)
    shutil.copy(os.path.join(here, "profile.css"), os.path.join(root, "assets", "profile.css"))
    shutil.copy(os.path.join(here, "og.png"), os.path.join(root, "assets", "og.png"))
    with open(os.path.join(root, "assets", "logo.svg"), "w", encoding="utf-8") as fh:
        fh.write(logo)
    logo_svg = logo.replace("<svg ", '<svg aria-hidden="true" ', 1)
    import pages
    pages.assign_inst_slugs(records)
    by_sub, by_inst = defaultdict(list), defaultdict(list)
    for r in records:
        by_sub[(r["f"].get("Specialty"), r["f"].get("Subspecialty"))].append(r)
        by_inst[r.get("org") or r["i"]].append(r)
    for r in records:
        sims = [x for x in by_sub[(r["f"].get("Specialty"), r["f"].get("Subspecialty"))] if x is not r and x["i"] != r["i"]]
        sims.sort(key=lambda x: (x["co"] != r["co"], x["t"]))
        inst = [x for x in by_inst[r.get("org") or r["i"]] if x is not r][:6]
        d = os.path.join(out, r["s"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(page(r, logo_svg, sims[:6], inst))
    write_static(records, logo, root)
    landing = pages.write_pages(records, logo, root, here)
    urls = [f"{SITE}/", f"{SITE}/about/", f"{SITE}/contact/"] + landing + [f'{SITE}/programs/{r["s"]}/' for r in records]
    with open(os.path.join(root, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                 "".join(f"<url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    with open(os.path.join(root, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    print("profiles:", len(records), "pages + sitemap.xml")


def static_page(title, desc, slug, body, logo_svg):
    url = f"{SITE}/{slug}/"
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)} | The Fellowship Portal</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}"><meta property="og:image" content="https://thefellowshipportal.com/assets/og.png"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="../assets/logo.svg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<link rel="stylesheet" href="../assets/profile.css">
<script>try{{var t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
</head>
<body>
<header class="hero"><div class="wrap">
  <div class="top"><a class="brand" href="../">{logo_svg}<span>The Fellowship Portal</span></a><a class="back" href="../#results">← All programmes</a>{nav("../")}</div>
  <nav class="crumbs" aria-label="Breadcrumb"><a href="../">Home</a><span>›</span><span>{e(title)}</span></nav>
  <h1>{e(title)}</h1>
  <p class="inst">{e(desc)}</p>
</div></header>
<main class="wrap"><div class="grid">{body}</div>
<footer>The Fellowship Portal · <a href="../specialties/">Specialties</a> · <a href="../countries/">Countries</a> · <a href="../deadlines/">Deadlines</a> · <a href="../about/">About</a> · <a href="../contact/">Contact</a></footer>
</main>
<script src="../assets/save.js" defer></script>
</body>
</html>'''


def write_static(records, logo, root):
    logo_svg = logo.replace("<svg ", '<svg aria-hidden="true" ', 1)
    n = len(records)
    specs = len({r["f"].get("Specialty") for r in records})
    countries = len({r["co"] for r in records if r["co"]})
    insts = len({r.get("org") or r["i"] for r in records})
    about = f'''<div>
<section class="panel"><h2>What this is</h2><p class="summary">The Fellowship Portal is a free directory of clinical and research fellowships for doctors who want to train abroad. It lists {n:,} programmes in {specs} specialties at {insts:,} institutions across {countries} countries, with each programme's eligibility, visa, funding and application details where the institution publishes them.</p></section>
<section class="panel"><h2>Who it is for</h2><p class="summary">Specialists and senior trainees, especially international medical graduates, who are comparing fellowships across countries and need to know early whether a programme accepts overseas applicants, sponsors visas and pays a salary.</p></section>
<section class="panel"><h2>How the data is collected</h2><dl class="facts">
<dt>Sources</dt><dd>Every programme is researched from the institution's own fellowship page, its graduate medical education office, or an official college, society or match service. We do not copy from aggregator sites.</dd>
<dt>Institution policy</dt><dd>Values marked “Institution policy” come from the hospital's or university's general rules, for example its visa sponsorship policy or salary scale. They apply to all its programmes, but a single programme may differ.</dd>
<dt>Not stated</dt><dd>“Not stated on official page” means we checked the official page and it does not publish that detail. Ask the programme coordinator directly.</dd>
<dt>Closed adverts</dt><dd>Some posts are recruited through job adverts. Closed adverts are hidden by default because they usually recur each year.</dd>
<dt>Last checked</dt><dd>October 2026. Dates and requirements change every cycle, so always confirm on the official page before applying.</dd>
</dl></section>
<section class="panel"><h2>Specialist directories</h2><p class="summary">For surgical specialties we also run dedicated directories with deeper listings: <a href="https://orthofellow.com">OrthoFellow</a>, <a href="https://urofellow.com">UroFellow</a>, <a href="https://neurosurgfellow.com">NeuroSurgFellow</a>, <a href="https://surgfellow.com">SurgFellow</a>, <a href="https://plasticfellow.com">PlasticFellow</a>, <a href="https://ctsfellow.com">CTSFellow</a> and <a href="https://vascfellow.com">VascFellow</a>.</p></section>
</div>
<aside class="side">
<section class="panel"><div class="label">Directory size</div><div class="big">{n:,}</div><p>programmes in {specs} specialties and {countries} countries</p></section>
<section class="panel"><div class="label">Independent</div><p>We are not affiliated with any hospital, university or match service, and we do not process applications. Apply through each programme's official route.</p></section>
<section class="panel"><div class="label">Questions</div><p><a href="../contact/">Contact us</a> to report an error or update a programme.</p></section>
</aside>'''
    contact = '''<div>
<section class="panel"><h2>Email</h2><p class="summary">Write to <b>info@thefellowshipportal.com</b>. We read every message and usually reply within a few working days.</p>
<p style="margin-top:14px"><a class="btn primary" href="mailto:info@thefellowshipportal.com" style="display:inline-flex">Email us</a> <button class="btn" type="button" id="copy" style="border:1px solid var(--line);background:var(--surface);color:var(--ink)">Copy address</button> <span id="copied" class="label" hidden>Copied</span></p></section>
<section class="panel"><h2>Report an error in a programme</h2><dl class="facts">
<dt>Include</dt><dd>The programme name and the link to its page on this site, the field that is wrong (for example deadline or visa support), and the correct information.</dd>
<dt>Source</dt><dd>A link to the official page that shows the correct detail. We only publish information we can confirm on an official source.</dd>
</dl></section>
<section class="panel"><h2>Programme directors and coordinators</h2><p class="summary">If you run a fellowship and want to add it, update its details or link a new official page, email us from your institutional address with the programme's official URL. We update listings free of charge.</p></section>
<section class="panel"><h2>What we cannot help with</h2><p class="summary">We do not accept or forward applications, and we cannot advise on individual eligibility, visas or licensing. Contact the programme or the relevant licensing body directly.</p></section>
</div>
<aside class="side">
<section class="panel"><div class="label">Email</div><p><b style="color:var(--ink)">info@thefellowshipportal.com</b></p></section>
<section class="panel"><div class="label">Response time</div><p>Usually within a few working days.</p></section>
<section class="panel"><div class="label">Before you write</div><p>Many questions are answered on each programme's official page, linked from every profile.</p></section>
</aside>
<script>document.getElementById('copy').onclick=function(){var a='info@thefellowshipportal.com';var s=document.getElementById('copied');(navigator.clipboard?navigator.clipboard.writeText(a):Promise.reject()).then(function(){s.hidden=false},function(){s.textContent=a;s.hidden=false})};</script>'''
    for slug, title, desc, body in [("about", "About", "A free, source-checked directory of medical and surgical fellowships worldwide.", about),
                                    ("contact", "Contact", "Report an error, update a programme or ask a question.", contact)]:
        d = os.path.join(root, slug)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(static_page(title, desc, slug, body, logo_svg))
    with open(os.path.join(root, ".htaccess"), "w", encoding="utf-8") as fh:
        fh.write("""# Compression and caching for The Fellowship Portal
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json image/svg+xml text/xml application/xml
</IfModule>
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType application/json "access plus 1 day"
  ExpiresByType text/css "access plus 7 days"
  ExpiresByType image/svg+xml "access plus 30 days"
  ExpiresByType text/html "access plus 1 hour"
</IfModule>
""")
    print("static pages: about, contact, .htaccess")
