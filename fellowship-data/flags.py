"""Classify International applicants / Visa support text into simple flags for filtering."""
import re
NS = re.compile(r"^(not stated|check with|confirm current|not specified|contact programme|see official|unknown)", re.I)
POL = re.compile(r"^institution policy:\s*", re.I)
IM_YES = re.compile(r"^(yes|open|accepted|welcome|international|eligible|imgs?\b|fmgs?\b|foreign|non-us|graduates of non|applications accepted from|overseas)", re.I)
IM_NO = re.compile(r"^(no\b|limited\b|restricted\b)|\b(citizens?|permanent residents?|nationals?)\b[^.;]{0,40}\bonly\b|\bonly\b[^.;]{0,40}\b(citizens?|permanent residents?|nationals?)\b|requires?[^.;]*\bcitizens|must (be|hold)[^.;]*citizen|not (open|accepted|eligible)", re.I)
VS_NO = re.compile(r"^(no\b|none\b|not applicable|not (accepting|sponsoring|offered|available|provided))|does not (offer|provide|sponsor)|not (sponsor|offer)|no (visa|sponsorship|immigration)|unable to sponsor|cannot sponsor|must (apply for|arrange|obtain) their own", re.I)
VS_YES = re.compile(r"J-?1|H-?1B|sponsor|work permit|Training Employment Pass|visa (support|assistance|sponsorship)|immigration assistance|Tier ?[25]|Skilled Worker|Health and Care|subclass|\bTSS\b|employment pass|work visa|blue card|visit pass|assist(s|ance)? with (the )?visa", re.I)
NEG = re.compile(r"\b(not|no|does not|doesn't|cannot|unable)\b", re.I)


def flags(ia, vs):
    """im/vs: 1 yes, 0 no, -1 unknown."""
    ia, vs = POL.sub("", ia or ""), POL.sub("", vs or "")
    im = -1
    if ia and not NS.match(ia):
        if re.match(r"^yes", ia, re.I):
            im = 1
        elif IM_NO.search(ia):
            im = 1 if re.search(r"J-?1", ia) and not re.search(r"no J-?1|not .{0,20}J-?1", ia, re.I) else 0
        elif IM_YES.search(ia):
            im = 1
    v = -1
    if vs and not NS.match(vs):
        # "does not sponsor H-1B; J-1 only" still means a visa route exists
        kept = " ; ".join(c for c in re.split(r"[;.]", vs) if not ("H-1B" in c.upper().replace("H1B", "H-1B") and NEG.search(c) and not re.search(r"J-?1", c)))
        if re.search(r"J-?1", vs) and not re.search(r"no J-?1|not .{0,20}J-?1", vs, re.I):
            v = 1
        elif VS_NO.search(kept or vs):
            v = 0
        elif VS_YES.search(vs):
            v = 1
    return im, v
