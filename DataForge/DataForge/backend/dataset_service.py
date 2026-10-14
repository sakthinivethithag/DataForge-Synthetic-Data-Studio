import re
import numpy as np
import pandas as pd

SENSITIVE_HINTS = ("email", "phone", "mobile", "name", "address", "ssn", "aadhaar", "passport", "customer_id")

def profile_frame(df, name="dataset"):
    if df is None or df.empty:
        raise ValueError("The dataset is empty.")
    if len(df.columns) == 0 or len(df.columns) > 100:
        raise ValueError("Dataset must contain between 1 and 100 columns.")
    columns = []
    for col in df.columns:
        s = df[col]
        kind = "text"
        if pd.api.types.is_bool_dtype(s): kind = "boolean"
        elif pd.api.types.is_numeric_dtype(s): kind = "integer" if pd.api.types.is_integer_dtype(s) else "decimal"
        elif pd.api.types.is_datetime64_any_dtype(s): kind = "date"
        else:
            parsed = pd.to_datetime(s.dropna(), errors="coerce")
            if len(s.dropna()) and parsed.notna().mean() > .85: kind = "date"
            elif s.nunique(dropna=True) <= min(30, max(8, int(len(s)*.25))): kind = "categorical"
        columns.append({"name": str(col), "type": kind, "missing": int(s.isna().sum()), "unique": int(s.nunique(dropna=True)),
                        "sensitive_warning": any(h in str(col).lower() for h in SENSITIVE_HINTS)})
    return {"name": name, "rows": int(len(df)), "columns": int(len(df.columns)),
            "missing_values": int(df.isna().sum().sum()), "duplicate_rows": int(df.duplicated().sum()),
            "column_details": columns, "quality": "Review needed" if df.isna().sum().sum() or df.duplicated().sum() else "No missing or duplicate rows detected",
            "preview": df.head(10).replace({np.nan: None}).to_dict(orient="records")}

def make_sample(sample_name):
    rng = np.random.default_rng(17)
    n = 120
    if sample_name == "students":
        departments = np.array(["AI&DS", "CSE", "ECE", "IT"])
        attendance = np.clip(rng.normal(82, 10, n), 45, 100).round(1)
        marks = np.clip(rng.normal(72, 13, n), 20, 100).round(1)
        df = pd.DataFrame({"student_id": [f"STU{i+1:04d}" for i in range(n)], "department": rng.choice(departments, n),
                           "attendance_pct": attendance, "internal_marks": marks,
                           "final_result": np.where((attendance >= 75) & (marks >= 40), "Pass", "Review")})
        return df
    if sample_name == "customers":
        return pd.DataFrame({"customer_id": [f"C{i+1:05d}" for i in range(n)],
          "age": rng.integers(18, 71, n), "region": rng.choice(["North", "South", "East", "West"], n),
          "category": rng.choice(["Books", "Electronics", "Home", "Clothing"], n, p=[.15,.35,.2,.3]),
          "transaction_amount": np.round(rng.gamma(3.5, 450, n), 2),
          "payment_method": rng.choice(["UPI", "Card", "Cash", "Net banking"], n)})
    raise ValueError("Unknown sample dataset. Choose 'students' or 'customers'.")

def create_from_schema(payload):
    name = str(payload.get("name", "Custom dataset"))[:80]
    cols = payload.get("columns")
    rows = payload.get("rows", 100)
    if not isinstance(rows, int) or rows < 1 or rows > 10000: raise ValueError("Row count must be between 1 and 10,000.")
    if not isinstance(cols, list) or not cols or len(cols) > 50: raise ValueError("Define between 1 and 50 columns.")
    rng = np.random.default_rng()
    data = {}
    for c in cols:
        col = re.sub(r"[^A-Za-z0-9_ -]", "", str(c.get("name", ""))).strip()[:50]
        typ = c.get("type", "text")
        if not col or col in data: raise ValueError("Column names must be non-empty and unique.")
        if typ in ("integer", "decimal"):
            lo, hi = float(c.get("min", 0)), float(c.get("max", 100))
            if lo > hi: raise ValueError(f"Minimum exceeds maximum for {col}.")
            vals = rng.uniform(lo, hi, rows)
            data[col] = np.floor(vals).astype(int) if typ == "integer" else np.round(vals, 2)
        elif typ == "categorical":
            vals = c.get("values") or ["A", "B", "C"]
            if not isinstance(vals, list) or not vals: raise ValueError(f"Provide category values for {col}.")
            data[col] = rng.choice([str(x)[:80] for x in vals], rows)
        elif typ == "boolean": data[col] = rng.choice([True, False], rows)
        elif typ == "date":
            start = pd.Timestamp("2020-01-01")
            data[col] = (start + pd.to_timedelta(rng.integers(0, 1800, rows), unit="D")).date.astype(str)
        else: data[col] = [f"demo_{i+1}" for i in range(rows)]
    return pd.DataFrame(data), name
