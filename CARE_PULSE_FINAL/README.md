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

## Functional Decline Score & Data Confidence

CARE PULSE employs an explainable 0–100 **Functional Decline Score** backed by a transparent **Data Confidence Factor**:

### 1. Baseline & Recent Periods
- **14-Day Baseline Period**: Calculates historical baseline mean scores across Mobility (0–10), Nutrition (0–100), Social Participation (0–10), and Daily Activity (0–10).
- **7-Day Recent Window**: Calculates recent average scores for the latest 7 days.

### 2. Score Calculation & Weighting
Percentage changes ($\Delta\% = \frac{\text{Recent} - \text{Baseline}}{\text{Baseline}} \times 100$) contribute to the Functional Decline Score:

- **Mobility Drop**: $\min(|\Delta\%| \times 1.2, 30.0\text{ pts})$
- **Nutrition Intake Drop**: $\min(|\Delta\%| \times 0.8, 25.0\text{ pts})$
- **Participation Drop**: $\min(|\Delta\%| \times 0.7, 20.0\text{ pts})$
- **Daily Activity Drop**: $\min(|\Delta\%| \times 0.5, 15.0\text{ pts})$
- **Safety / Fall Incidents**: $15.0\text{ pts per recent incident}$ ($\max 30.0\text{ pts}$)
- **Freshness Adjustment**: $+8.0\text{ pts}$ for Stale (4–7d), $+15.0\text{ pts}$ for Very Stale (>7d)
- **Observation Gap Penalty**: $+5.0\text{ pts}$ for $\ge 3$-day breaks in daily records

$$\text{Functional Decline Score} = \min(\max(\sum \text{Points}, 0.0), 100.0)$$

### 3. Classification Thresholds
- **🚨 Urgent Review**: Score $\ge 60.0$ or $\ge 2$ core domain drops / recent incident
- **⚠️ Needs Review**: Score $30.0 – 59.9$ or $1$ core domain drop
- **✅ Doing Well**: Score $< 30.0$ with stable indicators
- **⚠️ Missing Information**: Core metric missing or $< 4$ total observation records
- **⏳ Data May Be Old**: Latest record $> 7$ days old

### 4. Missing & Stale Data Handling
- **Missing Data**: Missing values (`NaN`) are preserved (never filled with zero or silently interpolated). Missing core domains lower data confidence and flag `Missing Information`.
- **Stale Data Thresholds**:
  - **0–1 days**: 🟢 **Fresh**
  - **2–3 days**: 🟡 **Aging**
  - **4–7 days**: 🔴 **Stale**
  - **>7 days**: 🚨 **Very Stale**
  - Stale messages communicate data uncertainty (e.g. *"Observation data is several days old. Trend interpretation confidence is reduced."*) rather than claiming patient deterioration.

### 5. Data Confidence Score
$$\text{Data Confidence (\%)} = \text{Completeness} \times \text{Freshness Factor} \times \text{Continuity Factor} \times \text{History Factor} \times 100$$

- **Good Confidence**: $\ge 75\%$
- **Limited Confidence**: $40\% – 74\%$
- **Insufficient Data**: $< 40\%$ or $< 4$ observation records

### 6. Human-Review Requirement & Scope Boundary
CARE PULSE is purely an observational decision-support prototype. It surfaces longitudinal functional trends to assist authorized human staff. It **never** provides autonomous medical diagnoses, disease predictions, or treatment prescriptions.

## Edge and Failure Cases Tested

The automated test suite (`python -m pytest tests/ -v`) explicitly tests and verifies edge/failure cases:

| Case | Input Condition | Expected Behaviour |
|------|------------------|--------------------|
| Missing mobility | mobility unavailable | Reduced confidence, reports missing mobility |
| Observation gap | missing daily records | Gap warning, confidence penalty applied |
| Stale data | old latest observation | Stale indicator, confidence reduced |
| Insufficient history | too few observations (< 4) | Insufficient history status, score set to 0.0 |
| Duplicate record | same patient/date | Duplicate record detected and blocked by validation |
| Invalid range | metric outside allowed range | Validation warning/failure explaining invalid range |

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
