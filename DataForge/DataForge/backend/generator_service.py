import numpy as np
import pandas as pd

def generate_synthetic(df, n_rows, method="statistical", constraints=None, noise=0.08, seed=None):
    if not isinstance(n_rows, int) or n_rows < 1 or n_rows > 50000:
        raise ValueError("Synthetic row count must be between 1 and 50,000.")
    constraints = constraints or {}
    rng = np.random.default_rng(seed)
    out = {}
    for col in df.columns:
        s = df[col]
        spec = constraints.get(col, {})
        if pd.api.types.is_numeric_dtype(s):
            vals = pd.to_numeric(s, errors="coerce").dropna().to_numpy(dtype=float)
            if not len(vals): vals = np.array([0.0])
            if method == "perturbed":
                sampled = rng.choice(vals, n_rows, replace=True)
                scale = max(float(np.std(vals)), 1.0) * max(0, min(float(noise), 1.0))
                sampled = sampled + rng.normal(0, scale, n_rows)
            else:
                std = float(np.std(vals))
                if len(vals) > 2 and std > 0:
                    sampled = rng.normal(float(np.mean(vals)), std, n_rows)
                else: sampled = rng.choice(vals, n_rows, replace=True)
            lo = spec.get("min")
            hi = spec.get("max")
            if lo is not None: sampled = np.maximum(sampled, float(lo))
            if hi is not None: sampled = np.minimum(sampled, float(hi))
            if pd.api.types.is_integer_dtype(s): sampled = np.rint(sampled).astype(int)
            out[col] = sampled
        else:
            vals = s.dropna().astype(str)
            if vals.empty: out[col] = [None] * n_rows
            else:
                counts = vals.value_counts(normalize=True)
                out[col] = rng.choice(counts.index.to_numpy(), n_rows, p=counts.to_numpy())
    result = pd.DataFrame(out, columns=df.columns)
    # Reapply explicit numerical bounds for safety.
    for col, spec in constraints.items():
        if col in result and pd.api.types.is_numeric_dtype(result[col]):
            if spec.get("min") is not None: result[col] = result[col].clip(lower=float(spec["min"]))
            if spec.get("max") is not None: result[col] = result[col].clip(upper=float(spec["max"]))
    return result
