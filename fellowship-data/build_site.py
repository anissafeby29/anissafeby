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
        if r["co"].startswith("Europe ("):
            r["co"] = "Switzerland"
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
    data = json.dumps(records, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    with open(os.path.join(HERE, "site_template.html"), encoding="utf-8") as fh:
        page = fh.read()
    with open(os.path.join(HERE, "logo.svg"), encoding="utf-8") as fh:
        logo = fh.read().strip()
    page = (page.replace("__FAVICON__", "data:image/svg+xml," + urllib.parse.quote(logo))
            .replace("__LOGO__", logo.replace("<svg ", '<svg aria-hidden="true" ', 1))
            .replace("__COUNT__", f"{len(records):,}")
            .replace("__SPECS__", str(len({r["f"]["Specialty"] for r in records})))
            .replace("__COUNTRIES__", str(len({r["co"] for r in records if r["co"]})))
            .replace("__DATA__", data))
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(page)
    print("index.html:", len(records), "programmes,", round(len(page) / 1e6, 2), "MB")
    import sys
    sys.path.insert(0, HERE)
    import profiles
    profiles.write_all(records, logo, ROOT, HERE)


if __name__ == "__main__":
    main()
