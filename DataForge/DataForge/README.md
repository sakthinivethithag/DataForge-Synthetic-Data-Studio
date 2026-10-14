# DataForge — Privacy-Preserving Synthetic Data Studio

A beginner-friendly local Flask web application for CSV profiling, baseline synthetic data generation, utility evaluation, heuristic privacy checks, and report downloads.

## Requirements

- Windows 11
- Python 3.11 or newer (Python 3.11–3.12 recommended)
- VS Code (optional but recommended)
- Internet connection only for the Chart.js CDN chart library; core backend features run locally.

## Run in Windows Command Prompt

1. Install Python from https://www.python.org/downloads/ and enable **Add Python to PATH** during setup.
2. Open the `DataForge` folder in VS Code.
3. In VS Code choose **Terminal → New Terminal**. For the commands below, use Command Prompt (`cmd`) if the terminal is PowerShell.
4. Confirm Python:

   ```bat
   python --version
   ```

5. Create and activate a virtual environment:

   ```bat
   python -m venv .venv
   .venv\Scripts\activate
   ```

6. Install packages:

   ```bat
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

7. Start the server:

   ```bat
   python app.py
   ```

8. Open **http://127.0.0.1:5000** in your browser. Do not open the HTML files directly from File Explorer; Flask serves them and the API.

Alternatively, double-click `run.bat`.

## End-to-end feature test

1. Home → **Start Forging Data**.
2. On Dataset Workspace, load **Student Performance** or **Customer Transactions**. These are synthetic demo records.
3. Review row/column counts, missing values, duplicates, column types and preview.
4. Open Generate Data, set the row count, select a generation method, optionally enter a numeric column name and bounds, and generate.
5. View the generated preview; download the CSV.
6. Open Evaluation to see numeric statistics, categorical distribution charts and the measured descriptive similarity.
7. Open Privacy Lab to rerun overlap, repeated-record, rare-value and identifier-name checks.
8. Open Reports to download a JSON Synthetic Data Passport or HTML report.
9. Use **Try another candidate** to compare iterations. Up to five candidates are retained in the current workspace.
10. Use **Reset** to clear your workspace.

## Create a custom dataset

The simple form accepts comma-separated column names and creates text-like demonstration fields. For a typed schema, use the API `POST /api/dataset/create` with JSON like:

```json
{
  "name": "Exam demo",
  "rows": 100,
  "columns": [
    {"name": "marks", "type": "integer", "min": 0, "max": 100},
    {"name": "department", "type": "categorical", "values": ["AI&DS", "CSE", "IT"]},
    {"name": "present", "type": "boolean"}
  ]
}
```

## API overview

- `GET /api/health`
- `GET /api/samples`
- `GET /api/samples/<sample_name>` (`students`, `customers`)
- `POST /api/upload` (multipart form field `file`)
- `POST /api/dataset/create`
- `GET /api/dataset/profile`
- `POST /api/generate` (JSON: `rows`, `method`, `noise`, `constraints`)
- `GET /api/synthetic/preview`
- `POST /api/evaluate`
- `POST /api/privacy/check`
- `POST /api/iterate`
- `GET /api/download/csv`
- `GET /api/reports/passport`
- `GET /api/reports/summary`
- `POST /api/reset`

Responses are JSON objects with `success`, `message`/`error`, and `data` where applicable. Download routes return files.

## Troubleshooting

- **`python` is not recognized:** reinstall Python and enable Add Python to PATH, then reopen Command Prompt. You can also try `py --version`.
- **`No module named flask/pandas/numpy`:** activate `.venv` and run `pip install -r requirements.txt` from the project root.
- **`requirements.txt` not found:** run `cd` into the `DataForge` project folder first. Check with `dir`.
- **Port 5000 is busy:** in Command Prompt use `set PORT=5001` and then `python app.py`; visit `http://127.0.0.1:5001`.
- **Chart is missing:** Chart.js is loaded from jsDelivr CDN; check your internet connection. API and CSV generation do not depend on the chart library.
- **Upload rejected:** only CSV files are accepted; maximum upload size is 8 MB; maximum columns is 100.
- **Browser says no active dataset:** load a sample or upload a CSV in the same browser session. The starter app keeps workspace state in memory, so restarting Flask clears it.
- **Privacy:** use only data you are permitted to process. Do not expose raw source rows in reports. This MVP's heuristic checks do not prove anonymity and do not implement differential privacy.

## Architecture and limitations

Flask serves all HTML, CSS and JavaScript from the same origin and exposes JSON APIs. Pandas handles CSV/profile work; NumPy provides random sampling. The generator fits simple numeric distributions and categorical frequencies. It does not reliably preserve complex relationships, and numeric constraints only apply to numeric columns. The privacy indicators are educational heuristics, not formal privacy guarantees.

**Session isolation note:** the MVP assigns a random workspace token in a signed Flask session and keeps corresponding DataFrames in server memory. For production multi-user hosting, replace this in-memory state with a robust store keyed by authenticated users, add expiration/cleanup and CSRF protections, and deploy behind a production WSGI server. Do not run Flask debug mode on a public network.
