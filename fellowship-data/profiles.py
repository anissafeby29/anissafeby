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
       "Sri Lanka": "LKA", "Denmark": "DNK", "Norway": "NOR", "Finland": "FIN"}
GROUPS = [
    ("The programme", ["Training type", "Duration", "Start", "Positions", "Accreditation", "Department"]),
    ("Eligibility and visa", ["Eligibility", "International applicants", "Visa support", "Licence requirement"]),
    ("How to apply", ["Deadline", "Application method"]),
    ("Funding", ["Funding"]),
]
SCORED = ["Duration", "Start", "Positions", "Accreditation", "Eligibility", "International applicants", "Visa support",
          "Licence requirement", "Deadline", "Application method", "Funding", "Department"]
e = lambda s: html.escape(str(s or ""), quote=True)


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
        f'<section class="panel"><h2>{g}</h2><dl class="facts">' + "".join(f"<dt>{e(k)}</dt><dd>{fmt(f.get(k))}</dd>" for k in keys) + "</dl></section>"
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
<meta property="og:type" content="website"><meta property="og:title" content="{e(r["t"])}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}">
<link rel="icon" type="image/svg+xml" href="../../assets/logo.svg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<link rel="stylesheet" href="../../assets/profile.css">
<script type="application/ld+json">{ld_json}</script>
<script>try{{var t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
</head>
<body>
<header class="hero"><div class="wrap">
  <div class="top"><a class="brand" href="../../">{logo_svg}<span>The Fellowship Portal</span></a><a class="back" href="../../#results">← All programmes</a></div>
  <nav class="crumbs" aria-label="Breadcrumb"><a href="../../">Home</a><span>›</span><span>{e(f.get("Specialty"))}</span><span>›</span><span>{e(r["co"])}</span></nav>
  <div class="headrow">
    <div>
      <h1>{e(r["t"])}</h1>
      <p class="inst">{e(r["i"])}</p>
      <div class="chips"><span class="chip">{e(f.get("Specialty"))}</span>{f'<span class="chip">{e(f["Subspecialty"])}</span>' if f.get("Subspecialty") else ""}{f'<span class="chip gold">{e(f["Training type"])}</span>' if f.get("Training type") else ""}</div>
    </div>
    <div class="dest"><div class="label">Destination</div><div class="code">{iso(r["co"])}</div><div class="where">{e(place)}</div></div>
  </div>
  <div class="cta">{f'<a class="btn primary" href="{e(r["u"][0])}" target="_blank" rel="noopener">Open official programme page ↗</a>' if r["u"] else ""}{f'<a class="btn ghost" href="{e(r["p"])}" target="_blank" rel="noopener">Specialist directory profile ↗</a>' if r.get("p") else ""}</div>
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
  {rel(same_inst, "More at " + e(r["i"]))}
  <footer>The Fellowship Portal lists fellowships from official institution sources. Spotted an error? Tell the programme or contact us so we can update this profile.</footer>
</main>
</body>
</html>'''


def write_all(records, logo, root, here):
    out = os.path.join(root, "programs")
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(root, "assets"), exist_ok=True)
    shutil.copy(os.path.join(here, "profile.css"), os.path.join(root, "assets", "profile.css"))
    with open(os.path.join(root, "assets", "logo.svg"), "w", encoding="utf-8") as fh:
        fh.write(logo)
    logo_svg = logo.replace("<svg ", '<svg aria-hidden="true" ', 1)
    by_sub, by_inst = defaultdict(list), defaultdict(list)
    for r in records:
        by_sub[(r["f"].get("Specialty"), r["f"].get("Subspecialty"))].append(r)
        by_inst[r["i"]].append(r)
    for r in records:
        sims = [x for x in by_sub[(r["f"].get("Specialty"), r["f"].get("Subspecialty"))] if x is not r and x["i"] != r["i"]]
        sims.sort(key=lambda x: (x["co"] != r["co"], x["t"]))
        inst = [x for x in by_inst[r["i"]] if x is not r][:6]
        d = os.path.join(out, r["s"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(page(r, logo_svg, sims[:6], inst))
    urls = [f"{SITE}/"] + [f'{SITE}/programs/{r["s"]}/' for r in records]
    with open(os.path.join(root, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                 "".join(f"<url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    with open(os.path.join(root, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    print("profiles:", len(records), "pages + sitemap.xml")
