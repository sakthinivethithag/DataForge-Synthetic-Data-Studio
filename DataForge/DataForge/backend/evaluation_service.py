import numpy as np
import pandas as pd

def evaluate(source, synthetic):
    shared = [c for c in source.columns if c in synthetic.columns]
    numeric, categorical = {}, {}
    for c in shared:
        a, b = source[c], synthetic[c]
        if pd.api.types.is_numeric_dtype(a) and pd.api.types.is_numeric_dtype(b):
            aa, bb = pd.to_numeric(a, errors="coerce").dropna(), pd.to_numeric(b, errors="coerce").dropna()
            if len(aa) and len(bb):
                scale = max(float(aa.std(ddof=0)), 1.0)
                numeric[c] = {"source_mean": round(float(aa.mean()), 4), "synthetic_mean": round(float(bb.mean()), 4),
                    "source_median": round(float(aa.median()), 4), "synthetic_median": round(float(bb.median()), 4),
                    "source_std": round(float(aa.std(ddof=0)), 4), "synthetic_std": round(float(bb.std(ddof=0)), 4),
                    "mean_absolute_difference": round(float(abs(aa.mean()-bb.mean())), 4),
                    "similarity_pct": round(max(0, 100*(1-abs(float(aa.mean()-bb.mean()))/scale)), 2),
                    "source_values": aa.head(250).tolist(), "synthetic_values": bb.head(250).tolist()}
        else:
            ac = a.fillna("[Missing]").astype(str).value_counts(normalize=True)
            bc = b.fillna("[Missing]").astype(str).value_counts(normalize=True)
            keys = sorted(set(ac.index) | set(bc.index))
            tvd = sum(abs(float(ac.get(k,0))-float(bc.get(k,0))) for k in keys)/2
            categorical[c] = {"categories": keys[:40], "source_pct": [round(float(ac.get(k,0)*100),2) for k in keys[:40]],
                              "synthetic_pct": [round(float(bc.get(k,0)*100),2) for k in keys[:40]],
                              "similarity_pct": round(100*(1-tvd),2)}
    missing = {"source": int(source.isna().sum().sum()), "synthetic": int(synthetic.isna().sum().sum())}
    similarities = [v["similarity_pct"] for v in numeric.values()] + [v["similarity_pct"] for v in categorical.values()]
    return {"numeric": numeric, "categorical": categorical, "missing": missing,
            "overall_similarity_pct": round(float(np.mean(similarities)),2) if similarities else None,
            "source_shape": list(source.shape), "synthetic_shape": list(synthetic.shape),
            "note": "Similarity is a descriptive statistical heuristic, not a privacy guarantee or a downstream ML score."}
