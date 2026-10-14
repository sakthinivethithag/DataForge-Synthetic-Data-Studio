from flask import Flask, request, jsonify, send_file, send_from_directory, session
from pathlib import Path
import io, os, secrets
import pandas as pd
from backend.dataset_service import profile_frame, make_sample, create_from_schema
from backend.generator_service import generate_synthetic
from backend.evaluation_service import evaluate
from backend.privacy_service import check_privacy
from backend.report_service import passport, json_response

ROOT = Path(__file__).resolve().parent
FRONTEND = ROOT / "frontend"
app = Flask(__name__, static_folder=str(FRONTEND / "assets"), static_url_path="/assets")
app.secret_key = os.environ.get("DATAFORGE_SECRET", secrets.token_hex(32))
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
# Local MVP state is in-memory and scoped by Flask's signed session token.
STATES = {}

def state():
    key = session.get("workspace")
    if not key:
        key = secrets.token_urlsafe(20)
        session["workspace"] = key
    return STATES.setdefault(key, {"source": None, "name": None, "synthetic": None, "generation": {}, "evaluation": None, "privacy": None, "candidates": []})

def ok(data=None, message="OK"):
    return jsonify({"success": True, "message": message, "data": data})

def err(message, status=400):
    return jsonify({"success": False, "error": message}), status

def read_csv_upload(file):
    if not file or not file.filename: raise ValueError("Choose a CSV file first.")
    if Path(file.filename).suffix.lower() != ".csv": raise ValueError("Only .csv files are allowed.")
    raw = file.stream.read()
    if not raw: raise ValueError("The uploaded file is empty.")
    try: df = pd.read_csv(io.BytesIO(raw))
    except Exception: raise ValueError("Could not read this CSV. Check its encoding and formatting.")
    if df.empty: raise ValueError("CSV must contain at least one data row.")
    if len(df.columns) > 100: raise ValueError("CSV may contain at most 100 columns.")
    df.columns = [str(c).strip()[:100] for c in df.columns]
    if any(not c for c in df.columns) or len(set(df.columns)) != len(df.columns): raise ValueError("Column names must be non-empty and unique.")
    return df

@app.errorhandler(413)
def too_large(_): return err("File is too large. Maximum upload size is 8 MB.", 413)

@app.route("/")
def home(): return send_from_directory(FRONTEND, "index.html")

@app.route("/<page>.html")
def page(page):
    allowed = {"dashboard","upload","generate","privacy","evaluation","reports","about"}
    if page not in allowed: return err("Page not found.",404)
    return send_from_directory(FRONTEND, page+".html")

@app.get("/api/health")
def health(): return ok({"status":"running","app":"DataForge","version":"1.0-mvp"})

@app.get("/api/samples")
def samples(): return ok([{"id":"students","name":"Student Performance","description":"Synthetic demonstration marks, attendance, department and result."},{"id":"customers","name":"Customer Transactions","description":"Synthetic demonstration transactions with region, category and amount."}])

@app.get("/api/samples/<sample_name>")
def sample(sample_name):
    try:
        df=make_sample(sample_name); s=state(); s.update(source=df,name=f"{sample_name}_demo.csv",synthetic=None,evaluation=None,privacy=None,candidates=[])
        return ok(profile_frame(df,s["name"]),"Sample dataset loaded.")
    except ValueError as e: return err(str(e))

@app.post("/api/upload")
def upload():
    try:
        df=read_csv_upload(request.files.get("file")); s=state()
        s.update(source=df,name=Path(request.files["file"].filename).name[:100],synthetic=None,evaluation=None,privacy=None,candidates=[])
        return ok(profile_frame(df,s["name"]),"CSV uploaded and profiled.")
    except ValueError as e: return err(str(e))
    except Exception: return err("Upload could not be processed.")

@app.post("/api/dataset/create")
def create_dataset():
    try:
        payload=request.get_json(force=True); df,name=create_from_schema(payload); s=state()
        s.update(source=df,name=name,synthetic=None,evaluation=None,privacy=None,candidates=[])
        return ok(profile_frame(df,name),"Dataset created with demonstration records.")
    except Exception as e: return err(str(e))

@app.get("/api/dataset/profile")
def profile():
    s=state()
    if s["source"] is None: return err("Load a sample or upload a CSV first.",404)
    return ok(profile_frame(s["source"],s["name"]))

@app.post("/api/generate")
def generate():
    s=state()
    if s["source"] is None: return err("Load a dataset before generating synthetic data.",400)
    try:
        p=request.get_json(force=True); n=int(p.get("rows",len(s["source"]))); method=p.get("method","statistical")
        if method not in ("statistical","perturbed"): return err("Choose a supported generation method.")
        constraints=p.get("constraints",{})
        syn=generate_synthetic(s["source"],n,method,constraints,float(p.get("noise",0.08)))
        s["synthetic"]=syn; s["generation"]={"rows":n,"method":method,"constraints":constraints,"noise":float(p.get("noise",0.08)),"iteration":len(s["candidates"])+1}
        s["evaluation"]=evaluate(s["source"],syn); s["privacy"]=check_privacy(s["source"],syn)
        s["candidates"].append({"iteration":s["generation"]["iteration"],"rows":n,"method":method,"utility":s["evaluation"]["overall_similarity_pct"],"risk":s["privacy"]["risk_indicator_pct"]})
        return ok({"profile":profile_frame(syn,"synthetic.csv"),"preview":syn.head(10).replace({float("nan"):None}).to_dict(orient="records"),"generation":s["generation"],"evaluation":s["evaluation"],"privacy":s["privacy"]},"Synthetic data generated.")
    except Exception as e: return err(str(e))

@app.get("/api/synthetic/preview")
def preview():
    s=state()
    if s["synthetic"] is None: return err("Generate synthetic data first.",404)
    return ok({"profile":profile_frame(s["synthetic"],"synthetic.csv"),"preview":s["synthetic"].head(20).where(pd.notna(s["synthetic"]),None).to_dict(orient="records")})

@app.post("/api/evaluate")
def do_evaluate():
    s=state()
    if s["source"] is None or s["synthetic"] is None: return err("Load a dataset and generate synthetic data first.",400)
    s["evaluation"]=evaluate(s["source"],s["synthetic"]); return ok(s["evaluation"])

@app.post("/api/privacy/check")
def do_privacy():
    s=state()
    if s["source"] is None or s["synthetic"] is None: return err("Load a dataset and generate synthetic data first.",400)
    s["privacy"]=check_privacy(s["source"],s["synthetic"]); return ok(s["privacy"])

@app.post("/api/iterate")
def iterate():
    s=state()
    if s["source"] is None: return err("Load a dataset first.",400)
    if len(s["candidates"]) >= 5: return err("Maximum of 5 candidates per workspace reached. Reset to start again.")
    try:
        p=request.get_json(force=True); n=int(p.get("rows",len(s["source"])))
        noise=min(1.0,max(.01,float(p.get("noise",.15))))
        syn=generate_synthetic(s["source"],n,"perturbed",p.get("constraints",{}),noise)
        s["synthetic"]=syn
        s["generation"]={"rows":n,"method":"perturbed","constraints":p.get("constraints",{}),"noise":noise,"iteration":len(s["candidates"])+1}
        s["evaluation"]=evaluate(s["source"],syn); s["privacy"]=check_privacy(s["source"],syn)
        s["candidates"].append({"iteration":s["generation"]["iteration"],"rows":n,"method":"perturbed","utility":s["evaluation"]["overall_similarity_pct"],"risk":s["privacy"]["risk_indicator_pct"]})
        return ok({"profile":profile_frame(syn,"synthetic.csv"),"preview":syn.head(10).where(pd.notna(syn),None).to_dict(orient="records"),"generation":s["generation"],"evaluation":s["evaluation"],"privacy":s["privacy"]},"Revised candidate generated.")
    except Exception as e: return err(str(e))

@app.get("/api/download/csv")
def download_csv():
    s=state()
    if s["synthetic"] is None: return err("Generate synthetic data first.",404)
    buf=io.BytesIO(s["synthetic"].to_csv(index=False).encode("utf-8-sig")); buf.seek(0)
    return send_file(buf, mimetype="text/csv", as_attachment=True, download_name="dataforge_synthetic.csv")

@app.get("/api/reports/passport")
def download_passport():
    s=state()
    if s["source"] is None: return err("Load a dataset first.",404)
    return json_response(passport({"name":s["name"],"source_rows":len(s["source"]),"source_columns":len(s["source"].columns),"generation":s["generation"],"candidates":s["candidates"]},s["evaluation"],s["privacy"]))

@app.get("/api/reports/summary")
def summary():
    s=state()
    return ok({"dataset":profile_frame(s["source"],s["name"]) if s["source"] is not None else None,"generation":s["generation"],"evaluation":s["evaluation"],"privacy":s["privacy"],"candidates":s["candidates"]})

@app.post("/api/reset")
def reset():
    key=session.get("workspace")
    if key: STATES.pop(key,None)
    session.pop("workspace",None)
    return ok(message="Workspace reset.")

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=int(os.environ.get("PORT",5000)))
