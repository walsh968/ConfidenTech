from django.urls import path
from . import views

urlpatterns = [
    # Confidence score endpoint
    path("api/confidence/", views.get_confidence_score, name="confidence"),
    
    # Add other AI-related URLs
]