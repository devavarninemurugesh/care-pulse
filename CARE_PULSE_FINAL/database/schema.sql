-- CARE PULSE Database Schema
-- SQL Schema Definition for Production Data Persistence (SQLite / PostgreSQL Compatible)

-- 1. Users & RBAC Profiles
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(64) PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    full_name VARCHAR(128) NOT NULL,
    role VARCHAR(32) NOT NULL CHECK (role IN ('Caregiver', 'Supervisor', 'Authorized Staff', 'Admin')),
    assigned_patients TEXT DEFAULT 'ALL',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Patient Profiles & Assignment
CREATE TABLE IF NOT EXISTS patients (
    patient_id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128),
    age INTEGER CHECK (age >= 0),
    gender VARCHAR(16),
    address TEXT,
    existing_conditions TEXT,
    care_plan TEXT,
    assigned_caregiver_id VARCHAR(64),
    status VARCHAR(32) DEFAULT 'Doing Well',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assigned_caregiver_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- 3. Daily Telemetry Observations
CREATE TABLE IF NOT EXISTS daily_observations (
    observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id VARCHAR(64) NOT NULL,
    date DATE NOT NULL,
    mobility REAL CHECK (mobility >= 0.0 AND mobility <= 10.0),
    nutrition REAL CHECK (nutrition >= 0.0 AND nutrition <= 100.0),
    participation REAL CHECK (participation >= 0.0 AND participation <= 10.0),
    activity REAL CHECK (activity >= 0.0 AND activity <= 10.0),
    incident INTEGER DEFAULT 0 CHECK (incident IN (0, 1)),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    CONSTRAINT unique_patient_observation_date UNIQUE (patient_id, date)
);

-- 4. Incident Logs
CREATE TABLE IF NOT EXISTS incidents (
    incident_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id VARCHAR(64) NOT NULL,
    date DATE NOT NULL,
    incident_type VARCHAR(64) NOT NULL,
    severity VARCHAR(32) NOT NULL CHECK (severity IN ('Low', 'Medium', 'High', 'Critical')),
    description TEXT,
    reported_by VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (reported_by) REFERENCES users(user_id) ON DELETE SET NULL
);

-- 5. Caregiver Visits
CREATE TABLE IF NOT EXISTS visits (
    visit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id VARCHAR(64) NOT NULL,
    caregiver_id VARCHAR(64) NOT NULL,
    visit_date TIMESTAMP NOT NULL,
    notes TEXT,
    status VARCHAR(32) DEFAULT 'Completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (caregiver_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 6. Clinical Staff Reviews & Triage Notes
CREATE TABLE IF NOT EXISTS staff_reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id VARCHAR(64) NOT NULL,
    reviewer_id VARCHAR(64) NOT NULL,
    review_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    decline_score REAL CHECK (decline_score >= 0.0 AND decline_score <= 100.0),
    risk_category VARCHAR(32) NOT NULL,
    clinical_notes TEXT,
    action_taken TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_obs_patient_date ON daily_observations(patient_id, date);
CREATE INDEX IF NOT EXISTS idx_incidents_patient ON incidents(patient_id);
CREATE INDEX IF NOT EXISTS idx_reviews_patient ON staff_reviews(patient_id);
