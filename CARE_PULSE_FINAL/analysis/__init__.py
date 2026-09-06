"""
Analysis package for CARE PULSE.
"""

from analysis.pipeline import process_dataset
from analysis.data_cleaning import clean_observation_dataframe
from analysis.trend_analysis import analyze_all_patient_trends, evaluate_patient_trend
from analysis.decline_score import calculate_functional_decline_score
from analysis.baseline import evaluate_single_metric_baseline
from analysis.experiment import run_early_detection_experiment
from analysis.metrics import compute_dataset_metrics

__all__ = [
    "process_dataset",
    "clean_observation_dataframe",
    "analyze_all_patient_trends",
    "evaluate_patient_trend",
    "calculate_functional_decline_score",
    "evaluate_single_metric_baseline",
    "run_early_detection_experiment",
    "compute_dataset_metrics"
]
