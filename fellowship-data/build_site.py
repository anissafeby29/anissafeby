"""Build ../index.html (single self-contained page) from the fellowship data files.

Run: python3 fellowship-data/build_site.py
"""
import json
import os

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
            "n": r.get("notes", ""), "new": False,
        })
    for r in load("new_programs.json"):
        records.append({
            "t": r["title"], "i": r["inst"], "co": r.get("Country", ""),
            "ci": r.get("City", ""), "su": r.get("Summary", ""),
            "f": {k: r.get(k, "") for k in FIELDS},
            "u": [u.strip() for u in r["official_urls"].split("|") if u.strip()],
            "n": "", "new": True, "p": r.get("profile_url", ""),
        })
    records.sort(key=lambda x: (x["f"]["Specialty"], x["t"].lower(), x["i"].lower()))
    return records


def main():
    records = build_records()
    data = json.dumps(records, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    with open(os.path.join(HERE, "site_template.html"), encoding="utf-8") as fh:
        page = fh.read().replace("__DATA__", data).replace("__COUNT__", str(len(records)))
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(page)
    print("index.html:", len(records), "programmes,", round(len(page) / 1e6, 2), "MB")


if __name__ == "__main__":
    main()
