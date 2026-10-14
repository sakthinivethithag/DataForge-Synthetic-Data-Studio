import re
import pandas as pd

SENSITIVE = re.compile(r"(email|e-mail|phone|mobile|telephone|full.?name|first.?name|last.?name|address|aadhaar|ssn|passport)", re.I)

def check_privacy(source, synthetic):
    cols = [c for c in source.columns if c in synthetic.columns]
    if not cols: return {"checks": [], "risk_level": "Unknown", "note": "No shared columns to compare."}
    # Compare string-normalized complete records without returning record contents.
    a = source[cols].fillna("<NA>").astype(str).agg("|".join, axis=1)
    b = synthetic[cols].fillna("<NA>").astype(str).agg("|".join, axis=1)
    source_set = set(a.tolist())
    exact = sum(x in source_set for x in b.tolist())
    dup_counts = b.value_counts()
    repeated = int(sum(max(0, int(v)-1) for v in dup_counts.values))
    rare = 0
    for c in cols:
        counts = source[c].fillna("<NA>").astype(str).value_counts()
        rare += int(sum(1 for x in synthetic[c].fillna("<NA>").astype(str) if counts.get(x,0) == 1))
    sensitive = [str(c) for c in cols if SENSITIVE.search(str(c))]
    n = max(1, len(synthetic))
    risk_pct = min(100, round(100*(0.55*exact/n + 0.25*repeated/n + 0.20*min(rare, n*len(cols))/(n*max(1,len(cols)))),2))
    level = "Elevated heuristic signal" if risk_pct >= 30 else "Some heuristic signal" if risk_pct >= 10 else "Lower observed signal"
    checks = [
      {"name":"Exact source-record overlap","matches":int(exact),"explanation":"Counts generated rows that exactly match a source row across shared columns. This is a heuristic, not proof of identity or anonymity."},
      {"name":"Repeated generated records","matches":repeated,"explanation":"Counts extra occurrences of duplicated rows in the synthetic dataset."},
      {"name":"Rare attribute values","matches":int(rare),"explanation":"Counts synthetic column values that occur once in the source column. This simple check can overcount and does not model real-world linkage attacks."},
      {"name":"Potentially identifying columns","matches":len(sensitive),"columns":sensitive,"explanation":"Column names suggest identifiers may be present. Inspect and remove or generalize identifiers before sharing."}
    ]
    return {"checks":checks,"risk_indicator_pct":risk_pct,"risk_level":level,
            "note":"Heuristic checks only. They do not prove anonymity, do not implement differential privacy, and should not be used as a formal privacy certification."}
