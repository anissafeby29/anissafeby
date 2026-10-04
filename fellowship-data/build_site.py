"""Build ../index.html (single self-contained page) from the fellowship data files.

Run: python3 fellowship-data/build_site.py
"""
import json
import os
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

FIELDS = ["Specialty", "Subspecialty", "Department", "State or region", "Training type", "Duration",
          "Start", "Deadline", "Eligibility", "International applicants", "Accreditation",
          "Application method", "Positions", "Funding", "Visa support", "Licence requirement",
          "Last verified"]


def load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return json.load(fh)


def build_records():
    meta = load("site_meta.json")
    records = []
    for r in load("programs.json"):
        m = meta.get(r["slug"], {})
        records.append({
            "t": r["title"], "i": r["institution"], "co": m.get("Country") or "",
            "ci": m.get("City") or "", "su": m.get("Summary") or "",
            "f": {k: r.get(k, "") for k in FIELDS},
            "u": [u.strip() for u in r["official_urls"].split("|") if u.strip()],
            "n": r.get("notes", ""), "new": False, "s": r["slug"],
        })
    for r in load("new_programs.json"):
        records.append({
            "t": r["title"], "i": r["inst"], "co": r.get("Country", ""),
            "ci": r.get("City", ""), "su": r.get("Summary", ""),
            "f": {k: r.get(k, "") for k in FIELDS},
            "u": [u.strip() for u in r["official_urls"].split("|") if u.strip()],
            "n": "", "new": True, "p": r.get("profile_url", ""), "s": r["slug"],
        })
    fix = {"Hong Kong SAR, China": "Hong Kong SAR"}
    for r in records:
        r["co"] = fix.get(r["co"], r["co"])
        if r["co"].startswith("International"):
            r["co"] = "International (multi-country)"
        if r["co"].startswith("Hong Kong"):
            r["co"] = "Hong Kong SAR"
        if r["co"].startswith("Europe"):
            r["co"] = "Europe (multi-country)"
    import re
    def group(r):
        t = (r["f"].get("Training type") or "").lower() + " " + r["t"].lower()
        if "advert" in t or "vacancy" in t: return "Job advert / vacancy"
        if re.search(r"observ|visiting|travell|exchange|short course|scholarship|grant|elective", t): return "Observership / visiting / short course"
        if re.search(r"residency|subspecialty training|training programme|program\b|af[cn]|area of focused", t) and "fellow" not in t: return "Subspecialty training programme"
        if "research" in t and "clinical" in t: return "Clinical + research fellowship"
        if "research" in t or "postdoc" in t or "t32" in t: return "Research fellowship"
        if "instructor" in t: return "Clinical instructorship"
        return "Clinical fellowship"
    import sys
    sys.path.insert(0, HERE)
    from normalize import canon_sub, canon_org
    from flags import flags
    for r in records:
        r["g"] = group(r)
        r["im"], r["vs"] = flags(r["f"].get("International applicants"), r["f"].get("Visa support"))
        r["_closed"] = bool(re.search(r"advert", r["t"], re.I) and re.search(r"closed|past|expired", f'{r["f"].get("Deadline", "")} {r["f"].get("Start", "")}', re.I))
        raw = r["f"].get("Subspecialty") or ""
        canon = canon_sub(r["f"].get("Specialty"), raw)
        r["focus"] = raw if raw and raw != canon else ""
        r["f"]["Subspecialty"] = canon
        r["org"] = canon_org(r["i"], r["co"])
    seen = set()
    for r in records:
        base = r["s"].rstrip("/").split("/")[-1] or "programme"
        name, k = base, 2
        while name in seen:
            name, k = f"{base}-{k}", k + 1
        seen.add(name)
        r["s"] = name
    records.sort(key=lambda x: (x["f"]["Specialty"], x["t"].lower(), x["i"].lower()))
    return records


def main():
    records = build_records()
    import re as _re
    NS = _re.compile(r"^(not stated|check with|confirm current|not specified|contact programme|see official|unknown)", _re.I)
    SCORED = ["Duration", "Start", "Positions", "Accreditation", "Eligibility", "International applicants", "Visa support",
              "Licence requirement", "Deadline", "Application method", "Funding", "Department"]
    KEEP = ["Specialty", "Subspecialty", "State or region", "Training type", "Duration", "Deadline", "Positions",
            "International applicants", "Visa support", "Funding", "Start"]
    slim = [{"t": r["t"], "i": r["i"], "o": r["org"], "co": r["co"], "ci": r["ci"], "su": r["su"], "s": r["s"], "g": r["g"],
             "new": r["new"], "im": r["im"], "vs": r["vs"], "u": r["u"][:1], "sc": sum(1 for k in SCORED if r["f"].get(k) and not NS.match(str(r["f"][k]))),
             "f": {k: r["f"].get(k, "") for k in KEEP}} for r in records]
    data = json.dumps(slim, ensure_ascii=False, separators=(",", ":"))
    import hashlib
    ver = hashlib.sha1(data.encode()).hexdigest()[:10]
    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    with open(os.path.join(ROOT, "assets", "programmes.json"), "w", encoding="utf-8") as fh:
        fh.write(data)
    with open(os.path.join(HERE, "site_template.html"), encoding="utf-8") as fh:
        page = fh.read()
    with open(os.path.join(HERE, "logo.svg"), encoding="utf-8") as fh:
        logo = fh.read().strip()
    page = (page.replace("__FAVICON__", "data:image/svg+xml," + urllib.parse.quote(logo))
            .replace("__LOGO__", logo.replace("<svg ", '<svg aria-hidden="true" ', 1))
            .replace("__COUNT__", f"{len(records):,}")
            .replace("__SPECS__", str(len({r["f"]["Specialty"] for r in records})))
            .replace("__COUNTRIES__", str(len({r["co"] for r in records if r["co"]})))
            .replace("__VER__", ver))
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(page)
    print("index.html:", len(records), "programmes,", round(len(page) / 1e6, 2), "MB")
    import sys
    sys.path.insert(0, HERE)
    import profiles
    profiles.write_all(records, logo, ROOT, HERE)


if __name__ == "__main__":
    main()
