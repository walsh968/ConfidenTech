from django.urls import path
from . import views

urlpatterns = [
    # Confidence score endpoint
    path("confidence/", views.get_confidence_score, name="confidence"),
    
    # Add other AI-related URLs
    path("api/raw/", views.get_raw_outputs, name="raw-outputs"),
    path("api/raw/export/", views.export_raw_outputs, name="raw-exports"),
    path("exportConfidenceData", views.export_confidence_data, name="export-confidence-data"),
]