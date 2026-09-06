WEB URL : https://care-pulse.streamlit.app/


# CARE PULSE — Home-Care Early Functional Decline Detection

CARE PULSE is a Streamlit-based clinical decision-support prototype for identifying **early, longitudinal functional decline** in home-care patients from observational data. It compares recent observations with a historical baseline across mobility, nutrition, participation, activity, and incident history, then presents explainable risk signals for human review.

> **Important:** CARE PULSE is a prototype decision-support system. It does not diagnose medical conditions, prescribe treatment, or replace professional clinical judgement.

## Problem Statement

Home-care teams can miss subtle changes when observations are reviewed as isolated values or only after a major adverse event. CARE PULSE addresses this by analysing longitudinal observations and surfacing changes across multiple functional domains, together with evidence and data-quality/uncertainty information.

## Main Features

- Longitudinal functional-decline analysis
- Historical baseline vs. recent-trend comparison
- Explainable Functional Decline Score (0–100)
- Risk categories and review alerts
- Evidence drill-down for patient-level signals
- Data validation and rejected-record tracking
- Observation freshness and uncertainty indicators
- CSV upload and dataset processing
- Role-based access control for demo users
- Role-scoped navigation and patient access
- Experiment/evaluation page for early-detection analysis
- Automated tests for analysis, validation, RBAC, and requirements

## Technology Stack

- **Python**
- **Streamlit** — web application UI
- **Pandas / NumPy** — data processing
- **Scikit-learn** — machine-learning utilities included in the project
- **Pytest** — automated testing

## Project Structure

```text
CARE_PULSE_FINAL/
├── app.py
├── security.py
├── requirements.txt
├── README.md
├── sample_10_patients.csv
├── care.csv
│
├── analysis/
│   ├── baseline.py
│   ├── data_cleaning.py
│   ├── decline_score.py
│   ├── experiment.py
│   ├── metrics.py
│   ├── ml_model.py
│   ├── pipeline.py
│   └── trend_analysis.py
│
├── data/
│   ├── generate_synthetic.py
│   ├── sample_10_patients.csv
│   ├── sample_patients.csv
│   └── synthetic_data.csv
│
├── ui/
│   ├── alerts.py
│   ├── components.py
│   ├── dashboard.py
│   ├── evidence.py
│   ├── experiment_page.py
│   ├── patients.py
│   ├── styles.py
│   └── upload.py
│
├── utils/
│   ├── helpers.py
│   └── validation.py
│
└── tests/
    ├── test_analysis.py
    ├── test_coe_requirements.py
    ├── test_ml_model.py
    ├── test_rbac.py
    └── test_validation.py
```

## Data Schema

The main observation datasets use fields such as:

| Field | Description |
|---|---|
| `patient_id` | Unique patient identifier |
| `date` | Observation date |
| `mobility` | Mobility/ambulation score |
| `nutrition` | Nutritional intake score/percentage |
| `participation` | Participation and engagement score |
| `activity` | Supporting activity score |
| `incident` | Incident/safety indicator |
| `notes` | Optional qualitative observation |

The validation module checks the expected structure and value constraints before analysis.

## Analysis Pipeline

```text
CSV / Uploaded Data
        ↓
Schema & Value Validation
        ↓
Data Cleaning / Rejection Tracking
        ↓
Trend & Freshness Analysis
        ↓
Historical Baseline vs Recent Trend
        ↓
Functional Decline Score
        ↓
Risk / Alert Signals
        ↓
Dashboard + Evidence Drill-down
        ↓
Human Review
```

The analysis is designed to make the reason for a signal visible rather than presenting an unexplained prediction. Missing or stale observations are surfaced as uncertainty instead of being silently treated as reliable evidence.

## Role-Based Access Control

The application contains demo roles with different access scopes. The exact permissions are implemented in `security.py`. The main roles are:

- **Caregiver** — assigned-patient care workflow
- **Supervisor** — supervised patient review and evidence
- **Authorized Staff** — broader patient/data access and evaluation functions
- **Admin** — full system administration and access

The sidebar role switcher is provided for demonstration/testing of these access rules.

## Installation

### 1. Extract the ZIP

Open PowerShell in the extracted project folder — the folder containing `app.py` and `requirements.txt`.

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Start the application

```powershell
python -m streamlit run app.py
```

Streamlit will display the local application address in the terminal.

## Running Tests

From the same project directory:

```powershell
python -m pytest -q
```

If dependencies are not installed yet, install them first with `requirements.txt`.

## Sample Data

The repository contains sample and synthetic datasets for demonstration and testing. The application can also process an uploaded CSV through its upload workflow.

## Project Limitations

- The included users are demonstration accounts, not production authentication.
- The datasets are intended for prototype/testing use.
- A risk signal is not a clinical diagnosis.
- Real deployment would require secure authentication, audited data storage, encryption, privacy controls, clinical validation, and appropriate governance.

## Final Submission Checklist

Before presenting the project:

1. Run `python -m pip install -r requirements.txt`.
2. Run `python -m streamlit run app.py`.
3. Test the role switcher for each demo role.
4. Test CSV upload and validation.
5. Open Dashboard, Patients, Alerts, Evidence, and Experiment pages as permitted.
6. Run `python -m pytest -q`.

## License / Academic Use

This project is provided as an academic/prototype implementation. Add the license or institutional attribution required by your submission guidelines.
