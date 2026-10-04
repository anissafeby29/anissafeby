"""Landing pages: /specialties/, /countries/, /training/, /institutions/, /deadlines/, /compare/.

Keeps the URLs of the original site alive and gives search engines a crawlable page per topic.
"""
import calendar
import datetime as dt
import json
import os
import re
import shutil
from collections import Counter, defaultdict

from profiles import SITE, e, iso, nav, slugify, spec_slug

TRAIN_SLUGS = {"Clinical fellowship": "clinical-fellowship", "Clinical + research fellowship": "clinical-research-fellowship",
               "Research fellowship": "research-fellowship", "Clinical instructorship": "clinical-instructorship",
               "Subspecialty training programme": "subspecialty-training", "Observership / visiting / short course": "observership",
               "Job advert / vacancy": "job-adverts"}
TRAIN_DESC = {"Clinical fellowship": "Hands-on clinical training posts after specialist training, usually one to two years.",
              "Clinical + research fellowship": "Fellowships that combine clinical work with protected research time.",
              "Research fellowship": "Research-focused posts, including postdoctoral and T32-funded positions.",
              "Clinical instructorship": "Junior faculty-style posts with clinical and teaching duties.",
              "Subspecialty training programme": "Structured subspecialty programmes run by colleges or training bodies.",
              "Observership / visiting / short course": "Observerships, visiting fellowships, travelling fellowships and short courses.",
              "Job advert / vacancy": "Fellow posts recruited through hospital or NHS job adverts. Adverts recur, so check for the next round."}
MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
MONTHS.update({m.lower(): i for i, m in enumerate(calendar.month_abbr) if m})
MONTHS["sept"] = 9
MON = r"(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sept?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
CLOSED = re.compile(r"closed|passed|expired|past cycle", re.I)


def shell(title, desc, path, body, logo_svg, crumbs=(), lede=None, ld=None):
    depth = path.strip("/").count("/") + 1
    p = "../" * depth
    url = f"{SITE}/{path.strip('/')}/"
    crumb_html = "".join(f'<span>›</span><a href="{p}{h}">{e(t)}</a>' if h else f"<span>›</span><span>{e(t)}</span>" for t, h in crumbs)
    ld_json = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/") if ld else ""
    ld_tag = f'<script type="application/ld+json">{ld_json}</script>' if ld else ""
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)} | The Fellowship Portal</title>
<meta name="description" content="{e(desc[:155])}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc[:155])}"><meta property="og:url" content="{url}"><meta property="og:image" content="https://thefellowshipportal.com/assets/og.png"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="{p}assets/logo.svg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<link rel="stylesheet" href="{p}assets/profile.css">
{ld_tag}
<script>try{{var t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
</head>
<body>
<header class="hero"><div class="wrap">
  <div class="top"><a class="brand" href="{p}">{logo_svg}<span>The Fellowship Portal</span></a>{nav(p)}</div>
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{p}">Home</a>{crumb_html}</nav>
  <h1>{e(title)}</h1>
  <p class="inst">{e(lede or desc)}</p>
</div></header>
<main class="wrap">{body}
<footer>The Fellowship Portal lists fellowships from official institution sources. · <a href="{p}specialties/">Specialties</a> · <a href="{p}countries/">Countries</a> · <a href="{p}institutions/">Institutions</a> · <a href="{p}deadlines/">Deadlines</a> · <a href="{p}about/">About</a> · <a href="{p}contact/">Contact</a></footer>
</main>
<script src="{p}assets/save.js" defer></script>
</body>
</html>'''


def tags(r):
    out = ""
    if r.get("im") == 1:
        out += '<span class="ftag ok">Open to IMGs</span>'
    elif r.get("im") == 0:
        out += '<span class="ftag warn">Citizens/PR only</span>'
    if r.get("vs") == 1:
        out += '<span class="ftag">Visa route</span>'
    return out


def row(r, p, extra=""):
    place = ", ".join(dict.fromkeys(x for x in [r["ci"], r["co"]] if x))
    return (f'<a class="prow" href="{p}programs/{e(r["s"])}/"><span class="code">{iso(r["co"])}</span>'
            f'<span class="pt"><b>{e(r["t"])}</b><span>{e(r["i"])}{" · " + e(place) if place else ""}{extra}</span></span>'
            f'<span class="ftags">{tags(r)}</span></a>')


def grouped(records, key, p, label_none="Other"):
    groups = defaultdict(list)
    for r in records:
        groups[key(r) or label_none].append(r)
    order = sorted(groups, key=lambda g: (-len(groups[g]), g))
    toc = '<nav class="toc">' + "".join(f'<a href="#g-{slugify(g)}">{e(g)} <span>{len(groups[g])}</span></a>' for g in order) + "</nav>" if len(order) > 1 else ""
    parts = []
    for g in order:
        items = sorted(groups[g], key=lambda r: (r["co"], r["t"].lower()))
        parts.append(f'<section class="panel plist" id="g-{slugify(g)}"><h2>{e(g)} <span class="n">{len(items)}</span></h2>' + "".join(row(r, p) for r in items) + "</section>")
    return toc + "".join(parts)


def side_counts(title, counter, link, limit=12):
    items = counter.most_common(limit)
    return (f'<section class="panel"><div class="label">{e(title)}</div><ul class="counts">' +
            "".join(f'<li><a href="{link(k)}">{e(k)}</a><span>{n}</span></li>' for k, n in items) + "</ul></section>")


def stat_panel(records, search_href, what):
    n = len(records)
    img = sum(1 for r in records if r.get("im") == 1)
    vs = sum(1 for r in records if r.get("vs") == 1)
    return (f'<section class="panel"><div class="label">{e(what)}</div><div class="big">{n:,}</div><p>programmes from official sources</p>'
            f'<ul class="counts" style="margin-top:12px"><li>Open to international applicants<span>{img:,}</span></li><li>Visa route stated<span>{vs:,}</span></li></ul>'
            f'<p style="margin-top:14px"><a class="btn solid" href="{search_href}">Filter and search these →</a></p></section>')


def write(root, path, html_text):
    d = os.path.join(root, path)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(html_text)


def q(**kw):
    from urllib.parse import urlencode
    return "?" + urlencode({k: v for k, v in kw.items() if v}) + "#results"


def collection_ld(name, url, records):
    return {"@context": "https://schema.org", "@type": "CollectionPage", "name": name, "url": url,
            "mainEntity": {"@type": "ItemList", "numberOfItems": len(records),
                           "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f'{SITE}/programs/{r["s"]}/', "name": r["t"]} for i, r in enumerate(records[:100])]}}


def parse_deadline(text, today):
    """Earliest upcoming date in a Deadline field. Returns (date, kind) with kind 'dated' or 'annual', or None."""
    if not text or CLOSED.search(text) or re.match(r"^(not stated|rolling|n/a|none)", text, re.I):
        return None
    found = []
    for m in re.finditer(rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+{MON}\.?,?\s+(20\d\d)\b", text, re.I):
        found.append((m.start(), int(m.group(3)), MONTHS[m.group(2).lower()[:3]], int(m.group(1))))
    for m in re.finditer(rf"\b{MON}\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?,?\s+(20\d\d)\b", text, re.I):
        found.append((m.start(), int(m.group(3)), MONTHS[m.group(1).lower()[:3]], int(m.group(2))))
    for m in re.finditer(r"\b(20\d\d)-(\d\d)-(\d\d)\b", text):
        found.append((m.start(), int(m.group(1)), int(m.group(2)), int(m.group(3))))
    if not found and not re.search(r"20\d\d", text):
        # "1 February" or "November 1" with no year: a recurring annual deadline
        mm = re.match(rf"^\s*(?:(\d{{1,2}})(?:st|nd|rd|th)?\s+{MON}|{MON}\s+(\d{{1,2}})(?:st|nd|rd|th)?)\b", text, re.I)
        if mm:
            d = int(mm.group(1) or mm.group(4))
            mon = MONTHS[(mm.group(2) or mm.group(3)).lower()[:3]]
            for y in (today.year, today.year + 1):
                try:
                    cand = dt.date(y, mon, d)
                except ValueError:
                    break
                if cand >= today:
                    return cand, "annual"
        return None
    if not found:
        return None
    # The first date written is the deadline; later ones are usually interviews, match day or start
    _, y, m, d = min(found)
    try:
        date = dt.date(y, m, d)
    except ValueError:
        return None
    return (date, "dated") if today <= date <= today + dt.timedelta(days=550) else None


def assign_inst_slugs(records):
    names = sorted({r.get("org") or r["i"] for r in records})
    slug, used = {}, set()
    for name in names:
        base = slugify(name)[:80].strip("-")
        s, k = base, 2
        while s in used:
            s, k = f"{base}-{k}", k + 1
        used.add(s)
        slug[name] = s
    for r in records:
        r["inst_slug"] = slug[r.get("org") or r["i"]]


def write_pages(records, logo, root, here):
    logo_svg = logo.replace("<svg ", '<svg aria-hidden="true" ', 1)
    for sub in ("specialties", "countries", "training", "institutions", "deadlines", "compare"):
        shutil.rmtree(os.path.join(root, sub), ignore_errors=True)
    shutil.copy(os.path.join(here, "save.js"), os.path.join(root, "assets", "save.js"))
    urls = []
    live = [r for r in records if not r.get("_closed")]

    # Specialties
    by_spec = defaultdict(list)
    for r in records:
        by_spec[r["f"].get("Specialty")].append(r)
    tiles = ""
    for s in sorted(by_spec, key=lambda s: -len(by_spec[s])):
        rs, slug = by_spec[s], spec_slug(s)
        subs = Counter(r["f"].get("Subspecialty") for r in rs if r["f"].get("Subspecialty"))
        cos = Counter(r["co"] for r in rs if r["co"])
        path = f"specialties/{slug}"
        p = "../../"
        title = f"{s} fellowships"
        desc = f"{len(rs):,} {s.lower()} fellowships in {len(cos)} countries, with eligibility, visa and deadline details from official institution pages."
        body = (f'<div class="grid"><div>{grouped(rs, lambda r: r["f"].get("Subspecialty"), p, "General " + s.lower())}</div><aside class="side">'
                + stat_panel(rs, p + q(sp=s), s)
                + side_counts("Top countries", cos, lambda k: p + q(sp=s, co=k))
                + side_counts("Subspecialties", subs, lambda k: p + q(sp=s, sub=k), 20) + "</aside></div>")
        write(root, path, shell(title, desc, path, body, logo_svg, [("Specialties", "specialties/"), (s, None)], ld=collection_ld(title, f"{SITE}/{path}/", rs)))
        urls.append(f"{SITE}/{path}/")
        tiles += f'<a class="tile" href="{slug}/"><b>{e(s)}</b><span>{len(rs):,} programmes · {len(cos)} countries</span></a>'
    write(root, "specialties", shell("Fellowships by specialty", f"Browse {len(records):,} fellowships in {len(by_spec)} specialties.", "specialties",
                                     f'<div class="tiles">{tiles}</div>', logo_svg, [("Specialties", None)]))
    urls.append(f"{SITE}/specialties/")

    # Countries
    by_co = defaultdict(list)
    for r in records:
        if r["co"]:
            by_co[r["co"]].append(r)
    tiles = ""
    for c in sorted(by_co, key=lambda c: -len(by_co[c])):
        rs, slug = by_co[c], slugify(c)
        specs = Counter(r["f"].get("Specialty") for r in rs)
        title = f"Fellowships in {c}"
        desc = f"{len(rs):,} medical and surgical fellowships in {c} across {len(specs)} specialties, from official institution pages."
        by_co[c] = (rs, None, title, desc, f"countries/{slug}")
        tiles += f'<a class="tile" href="{slug}/"><span class="code">{iso(c)}</span><b>{e(c)}</b><span>{len(rs):,} programmes · {len(specs)} specialties</span></a>'
    by_inst = defaultdict(list)
    for r in records:
        by_inst[r.get("org") or r["i"]].append(r)
    inst_slug = {name: rs[0]["inst_slug"] for name, rs in by_inst.items()}
    for c, (rs, body, title, desc, path) in list(by_co.items()):
        body = (f'<div class="grid"><div>{grouped(rs, lambda r: r["f"].get("Specialty"), "../../")}</div><aside class="side">'
                + stat_panel(rs, "../../" + q(co=c), c)
                + side_counts("Specialties", Counter(r["f"].get("Specialty") for r in rs), lambda k: "../../" + q(co=c, sp=k), 25)
                + side_counts("Top institutions", Counter(r.get("org") or r["i"] for r in rs), lambda k: f"../../institutions/{inst_slug[k]}/") + "</aside></div>")
        write(root, path, shell(title, desc, path, body, logo_svg, [("Countries", "countries/"), (c, None)], ld=collection_ld(title, f"{SITE}/{path}/", rs)))
        urls.append(f"{SITE}/{path}/")
    write(root, "countries", shell("Fellowships by country", f"Fellowships in {len(by_co)} countries and regions.", "countries",
                                   f'<div class="tiles">{tiles}</div>', logo_svg, [("Countries", None)]))
    urls.append(f"{SITE}/countries/")

    # Institutions
    letters = defaultdict(list)
    for name in sorted(by_inst, key=str.lower):
        rs = by_inst[name]
        slug = inst_slug[name]
        path, p = f"institutions/{slug}", "../../"
        cos = sorted({r["co"] for r in rs if r["co"]})
        where = ", ".join(cos)
        title = f"{name} fellowships"
        desc = f"{len(rs)} fellowship{'s' if len(rs) != 1 else ''} at {name}{' (' + where + ')' if where else ''}, with eligibility, visa and deadline details from official pages."
        specs = Counter(r["f"].get("Specialty") for r in rs)
        body = (f'<div class="grid"><div>{grouped(rs, lambda r: r["f"].get("Specialty"), p)}</div><aside class="side">'
                + stat_panel(rs, p + q(q=name), name)
                + side_counts("Specialties", specs, lambda k: f"{p}specialties/{spec_slug(k)}/", 25)
                + (f'<section class="panel"><div class="label">Location</div><p>' + " · ".join(f'<a href="{p}countries/{slugify(c)}/">{e(c)}</a>' for c in cos) + "</p></section>" if cos else "")
                + "</aside></div>")
        write(root, path, shell(title, desc, path, body, logo_svg, [("Institutions", "institutions/"), (name, None)], ld=collection_ld(title, f"{SITE}/{path}/", rs)))
        urls.append(f"{SITE}/{path}/")
        first = name[0].upper()
        letters[first if first.isalpha() else "#"].append((name, slug, len(rs), cos))
    az = '<nav class="toc">' + "".join(f'<a href="#l-{L}">{L}</a>' for L in sorted(letters)) + "</nav>"
    az += "".join(f'<section class="panel plist" id="l-{L}"><h2>{L}</h2>' + "".join(
        f'<a class="prow" href="{s}/"><span class="code">{iso(cos[0]) if len(cos) == 1 else "INT" if cos else "—"}</span><span class="pt"><b>{e(n)}</b><span>{e(", ".join(cos))}</span></span><span class="ftags"><span class="ftag">{c}</span></span></a>'
        for n, s, c, cos in items) + "</section>" for L, items in sorted(letters.items()))
    write(root, "institutions", shell("Institutions", f"{len(by_inst):,} hospitals, universities and training bodies offering fellowships.", "institutions", az, logo_svg, [("Institutions", None)]))
    urls.append(f"{SITE}/institutions/")

    # Training types
    by_g = defaultdict(list)
    for r in records:
        by_g[r["g"]].append(r)
    tiles = ""
    for g, rs in sorted(by_g.items(), key=lambda kv: -len(kv[1])):
        slug = TRAIN_SLUGS[g]
        path, p = f"training/{slug}", "../../"
        title = g if g.endswith("s") else g + "s" if not g.startswith("Observership") else "Observerships, visiting fellowships and short courses"
        title = {"Job advert / vacancy": "Fellowship job adverts", "Clinical + research fellowship": "Clinical and research fellowships"}.get(g, title)
        body = (f'<div class="grid"><div>{grouped(rs, lambda r: r["f"].get("Specialty"), p)}</div><aside class="side">'
                + stat_panel(rs, p + q(tt=g), g)
                + side_counts("Top countries", Counter(r["co"] for r in rs if r["co"]), lambda k: p + q(tt=g, co=k)) + "</aside></div>")
        write(root, path, shell(title, f"{len(rs):,} programmes. {TRAIN_DESC[g]}", path, body, logo_svg, [("Training types", "training/"), (g, None)], lede=TRAIN_DESC[g],
                                ld=collection_ld(title, f"{SITE}/{path}/", rs)))
        urls.append(f"{SITE}/{path}/")
        tiles += f'<a class="tile" href="{slug}/"><b>{e(title)}</b><span>{len(rs):,} programmes</span><span>{e(TRAIN_DESC[g])}</span></a>'
    write(root, "training", shell("Fellowships by training type", "Clinical, research and observership programmes.", "training", f'<div class="tiles">{tiles}</div>', logo_svg, [("Training types", None)]))
    urls.append(f"{SITE}/training/")

    # Deadlines
    today = dt.date.today()
    dl = []
    for r in live:
        got = parse_deadline(r["f"].get("Deadline"), today)
        if got:
            dl.append((got[0], got[1], r))
    dl.sort(key=lambda x: (x[0], x[2]["t"]))
    months = defaultdict(list)
    for date, kind, r in dl:
        months[(date.year, date.month)].append((date, kind, r))
    p = "../"
    toc = '<nav class="toc">' + "".join(f'<a href="#m-{y}-{m:02d}">{calendar.month_abbr[m]} {y} <span>{len(v)}</span></a>' for (y, m), v in sorted(months.items())) + "</nav>"
    secs = ""
    for (y, m), items in sorted(months.items()):
        secs += f'<section class="panel plist" id="m-{y}-{m:02d}"><h2>{calendar.month_name[m]} {y} <span class="n">{len(items)}</span></h2>'
        for date, kind, r in items:
            when = f'<span class="when"><b>{date.day}</b>{calendar.month_abbr[date.month]}</span>'
            note = " (usual annual date)" if kind == "annual" else ""
            txt = r["f"].get("Deadline", "")
            txt = txt if len(txt) <= 90 else txt[:88].rsplit(" ", 1)[0] + "…"
            secs += row(r, p, f'<br><i class="dlt">{e(txt)}{note}</i>').replace('<a class="prow"', f'<a class="prow" data-d="{date.isoformat()}"', 1).replace('<span class="code">' + iso(r["co"]) + "</span>", when + f'<span class="code">{iso(r["co"])}</span>', 1)
        secs += "</section>"
    dated = sum(1 for x in dl if x[1] == "dated")
    side = (f'<aside class="side"><section class="panel"><div class="label">Upcoming deadlines</div><div class="big">{len(dl):,}</div>'
            f'<p>{dated:,} with a published date, {len(dl) - dated:,} with a usual annual date. Updated {today.strftime("%-d %B %Y")}.</p></section>'
            '<section class="panel"><div class="label">How this works</div><p>Dates come from each programme\'s Deadline field on its official page. Programmes without a specific date, and closed adverts, are not listed. Always confirm the date on the official page.</p></section>'
            + side_counts("By specialty", Counter(x[2]["f"].get("Specialty") for x in dl), lambda k: f"{p}specialties/{spec_slug(k)}/", 25) + "</aside>")
    body = f'<div class="grid"><div>{toc}{secs or "<p>No upcoming dated deadlines.</p>"}</div>{side}</div>'
    # hide dates that pass between monthly rebuilds
    body += "<script>(function(){var t=new Date().toISOString().slice(0,10);document.querySelectorAll('[data-d]').forEach(function(a){if(a.dataset.d<t)a.hidden=true})})();</script>"
    write(root, "deadlines", shell("Fellowship deadline tracker", f"{len(dl):,} upcoming fellowship application deadlines, month by month, from official programme pages.", "deadlines", body, logo_svg, [("Deadlines", None)]))
    urls.append(f"{SITE}/deadlines/")

    # Compare / saved
    with open(os.path.join(here, "compare.html"), encoding="utf-8") as fh:
        cmp_body = fh.read()
    write(root, "compare", shell("Saved programmes", "Your shortlist, saved in this browser. Compare up to four programmes side by side.", "compare", cmp_body, logo_svg, [("Saved", None)]))

    with open(os.path.join(root, ".htaccess"), "a", encoding="utf-8") as fh:
        fh.write("""
# Old site URLs
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteRule ^fellowships/?$ /#results [R=301,NE,L]
  RewriteRule ^marketplace/?$ / [R=301,L]
  RewriteRule ^training/visiting-fellowship/?$ /training/observership/ [R=301,L]
  RewriteRule ^training/clinical-research/?$ /training/clinical-research-fellowship/ [R=301,L]
  RewriteRule ^specialties/(obstetrics-gynaecology|obstetrics-and-gynaecology)/?$ /specialties/obgyn/ [R=301,L]
  RewriteRule ^specialties/(otolaryngology|ent-otolaryngology)/?$ /specialties/ent/ [R=301,L]
  RewriteRule ^countries/hong-kong/?$ /countries/hong-kong-sar/ [R=301,L]
  RewriteRule ^countries/usa/?$ /countries/united-states/ [R=301,L]
  RewriteRule ^countries/uk/?$ /countries/united-kingdom/ [R=301,L]
</IfModule>
ErrorDocument 404 /404.html
""")
    nf = '<div class="panel"><h2>Page not found</h2><p class="summary">This page has moved or no longer exists. Try the <a href="/">search</a>, or browse by <a href="/specialties/">specialty</a>, <a href="/countries/">country</a> or <a href="/institutions/">institution</a>.</p></div>'
    with open(os.path.join(root, "404.html"), "w", encoding="utf-8") as fh:
        fh.write(shell("Page not found", "This page has moved.", "404", nf, logo_svg).replace('href="../', 'href="/').replace('src="../', 'src="/'))
    print("landing pages:", len(urls), "| deadlines:", len(dl))
    return urls
