from django.urls import path
from . import views

urlpatterns = [
    # Confidence score endpoint
    path("confidence/", views.get_confidence_score, name="confidence"),

    # Endpoint for confidence function
    path('analyze/', views.get_confidence_score_and_answer, name='analyze'),
    
    # Add other AI-related URLs
]