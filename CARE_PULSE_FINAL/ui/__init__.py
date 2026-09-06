"""
UI package for CARE PULSE.
"""

from ui.styles import apply_custom_styles
from ui.upload import render_upload_page
from ui.dashboard import render_dashboard
from ui.patients import render_patients_page
from ui.alerts import render_alerts_page
from ui.evidence import render_evidence_page
from ui.experiment_page import render_experiment_page

__all__ = [
    "apply_custom_styles",
    "render_upload_page",
    "render_dashboard",
    "render_patients_page",
    "render_alerts_page",
    "render_evidence_page",
    "render_experiment_page"
]
