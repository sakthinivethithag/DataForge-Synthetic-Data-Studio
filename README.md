# DataForge – Privacy-Preserving Synthetic Data Studio

**Tagline:** Forge Data. Fuel Innovation.

## About the Project

DataForge is a web-based application designed to generate synthetic data, evaluate its quality, and identify potential privacy risks. It combines dataset profiling, synthetic data generation, quality evaluation, privacy checks, and reporting in one user-friendly platform.

## Features

- **Dataset Management:** Upload supported datasets or explore sample datasets.
- **Data Profiling:** Examine columns, data types, record counts, and statistical summaries.
- **Synthetic Data Generation:** Generate artificial records using statistical sampling techniques.
- **Quality Evaluation:** Compare relevant statistical characteristics of original and synthetic data.
- **Privacy Lab:** Identify potential risks such as repeated records, source-data overlap, rare values, and identifier-like columns.
- **Reports and Downloads:** Review summaries and export supported datasets and reports.
- **Interactive Dashboard:** Explore the application through a browser-based interface.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend processing |
| Flask | Web framework and API endpoints |
| HTML5 | Web page structure |
| CSS3 | Styling and responsive design |
| JavaScript | Interactions and API communication |
| Pandas | Dataset processing and analysis |
| NumPy | Numerical and statistical operations |
| Chart.js | Data visualization |

## Workflow

1. Select a sample dataset or upload a supported dataset.
2. Profile the dataset and examine its structure.
3. Configure the available settings and generate synthetic records.
4. Evaluate the quality of the generated data.
5. Run privacy-risk checks.
6. Review results and download supported outputs.

## Target Users

- Students and researchers
- Data analysts and data scientists
- Machine learning developers
- Software developers
- Academic project teams

## Project Structure

```text
DataForge/
├── app.py
├── requirements.txt
├── README.md
├── run.bat
├── backend/
│   ├── dataset_service.py
│   ├── generator_service.py
│   ├── evaluation_service.py
│   ├── privacy_service.py
│   └── report_service.py
├── assets/
│   ├── css/
│   │   └── style.css
│   └── js/
├── outputs/
└── tests/
    └── test_app.py
```

The exact filenames may vary depending on the project version.

## Installation and Setup

### Prerequisites

- Python 3.10 or a compatible version
- pip
- A modern web browser

### Step 1: Open the project folder

Open Windows Command Prompt in the folder containing `app.py` and `requirements.txt`.

### Step 2: Create a virtual environment

```bat
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install dependencies

```bat
python -m pip install -r requirements.txt
```

### Step 4: Run the application

```bat
python app.py
```

Alternatively, if `run.bat` is provided and configured for your project, run:

```bat
run.bat
```

### Step 5: Open the website

Visit the local address displayed in your terminal. For the default Flask development port, use:

`http://127.0.0.1:5000`

## Example Use Case

A student needs sample data to test a data-analysis application without directly using real personal records. The student selects a dataset, generates synthetic records, evaluates their quality, checks for potential privacy risks, and downloads the results for experimentation.

## Advantages

- Combines multiple data-processing tasks in one platform.
- Provides a simple and accessible interface.
- Helps users understand synthetic data quality.
- Supports preliminary testing and experimentation.
- Uses a modular structure that can be extended in the future.

## Limitations

The privacy checks are heuristic indicators and do not guarantee complete anonymity or provide formal differential privacy. Synthetic data must be evaluated carefully before being used in production, regulated, or high-stakes applications.

## Future Enhancements

- Advanced synthetic data generation algorithms
- Stronger privacy-preserving techniques
- Additional data quality metrics
- Support for larger datasets
- Enhanced reports and visualizations

