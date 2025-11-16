from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from llm.models import AIResponseLog
from unittest.mock import patch
import csv, json

class ExportTests(APITestCase):

    @patch('llm.service._ollama_generate')
    def test_confidence_response_has_all_fields(self, mock_ollama):
        """Ensure API includes all fields required for export."""

        mock_ollama.return_value = ("Paris", 0.95)
        url = reverse('confidence')
        data = {'text': 'What is the capital of France?'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('confidence', response.data)
        self.assertIn('answer', response.data)
        
    def test_log_entry_fields_in_database(self):
        """Ensure AIResponseLog stores all required fields."""
        entry = AIResponseLog.objects.create(
            input_query="Sample query",
            model_a="gemma3:latest",
            model_b="gemma3:4b",
            embed_model="nomic-embed-text",
            model_a_confidence=0.85,
            model_b_confidence=0.88,
            agreement_score=0.92,
            final_confidence=90,
            best_model="gemma3:latest",
            best_answer="Paris is the capital of France.",
            timestamp= timezone.now(),        
        )    
        
        # Fetch it back from the database to be sure it exists there
        entry_from_db = AIResponseLog.objects.get(pk=entry.pk)

        # Assert the value, not just the attribute's existence
        self.assertEqual(entry_from_db.input_query, "Sample query")
        self.assertEqual(entry_from_db.final_confidence, 90)
        self.assertEqual(entry_from_db.model_a, "gemma3:latest")
        self.assertIsNotNone(entry_from_db.timestamp)


class ExportFormatValidationTests(APITestCase):
    def setUp(self):

        # 1. Get the custom user model
        User = get_user_model()

        # 2. Create the user. 
        #    Your custom model uses email, not username.
        self.user = User.objects.create_user(
            email="test@test.com", password="testpassword"
        )

        # Mock confidence result 
        self.mock_confidence_result = {
            "model_a": "gemma3:latest",
            "model_b": "gemma3:4b",
            "a_conf_pct": 90,
            "b_conf_pct": 80,
            "embed_model": "nomic-embed-text",
            "agreement_pct": 85,
            "a_self": 0.9,
            "b_self": 0.8,
            "agreement": 0.85,
            "best_model": "gemma3:4b",
            "best_answer": "Answer 1",
        }

        # Mock transient data that is not in the database
        self.mock_raw_payload = {
            "model": "gemma3:latest",
            "note": "Mocked raw payload",

            # Distributions and log-likelihoods
            "per_token": [
                {"token": "Paris", "prob": 0.9, "logprob": -0.105, "topk": []}
            ],
            "binary_probs": {"yes": 0.98, "no": 0.02},
        }
    @patch('llm.service._ollama_generate', return_value=("This is a mocked answer", 0.88))
    def test_confidence_response_is_json_serializable(self, mock_ollama):
        """Ensure backend response is valid JSON"""
        url = reverse('confidence')
        data = {'text': 'Who is the President of the United States?'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        try:
            json.dumps(response.data)
        except TypeError as e:
            self.fail(f"Response data not JSON serializable: {e}")

    @patch('llm.views.confidence_and_answer')
    @patch('llm.views.build_raw_payload')
    def test_export_confidence_response_is_csv(self, mock_build_raw_payload, mock_confidence):

        # Set up mock responses
        mock_confidence.return_value = self.mock_confidence_result
        mock_build_raw_payload.return_value = self.mock_raw_payload
        
        self.client.force_authenticate(user=self.user)      # Bypass authentication

        url = reverse('export-confidence-data')
        response = self.client.post(url, {'text': 'climate change', 'format': 'csv'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('text/csv', response['Content-Type'])
        self.assertIn('climate change', response.content.decode())


@patch('llm.views.confidence_and_answer')
@patch('llm.views.build_raw_payload')
class LargeDatasetExportTests(APITestCase):
    def setUp(self):
        now = datetime.now()
        for i in range(1001):
            AIResponseLog.objects.create(
                input_query=f"Query {i}",
                model_a="gemma3:latest",
                model_b="gemma3:4b",
                embed_model="nomic-embed-text",
                model_a_confidence=0.7,
                model_b_confidence=0.8,
                agreement_score=0.75,
                final_confidence=80,
                best_model="gemma3:4b",
                best_answer=f"Answer {i}",
                timestamp= now - timedelta(minutes=i), 
            )

        # 1. Get the custom user model
        User = get_user_model()

        # 2. Create the user. 
        #    Your custom model uses email, not username.
        self.user = User.objects.create_user(
            email="test@test.com", password="testpassword"
        )

        # Mock confidence result 
        self.mock_confidence_result = {
            "model_a": "gemma3:latest",
            "model_b": "gemma3:4b",
            "a_conf_pct": 90,
            "b_conf_pct": 80,
            "embed_model": "nomic-embed-text",
            "agreement_pct": 85,
            "a_self": 0.9,
            "b_self": 0.8,
            "agreement": 0.85,
            "best_model": "gemma3:4b",
            "best_answer": "Answer 1",
        }

        # Mock transient data that is not in the database
        self.mock_raw_payload = {
            "model": "gemma3:latest",
            "note": "Mocked raw payload",

            # Distributions and log-likelihoods
            "per_token": [
                {"token": "Paris", "prob": 0.9, "logprob": -0.105, "topk": []}
            ],
            "binary_probs": {"yes": 0.98, "no": 0.02},
        }

    def test_large_export_does_not_fail(self, mock_build_raw_payload, mock_confidence):
        """Ensure backend handles large datasets gracefully."""

        # Set up mock responses
        mock_confidence.return_value = self.mock_confidence_result
        mock_build_raw_payload.return_value = self.mock_raw_payload

        self.client.force_authenticate(user=self.user)      # Bypass authentication

        url = reverse('export-confidence-data')
        response = self.client.post(url)

        # Check response from server + Get the CSV content from the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)                  # Asserts that there is no crash
        self.assertIn('text/csv', response['Content-Type'])
        
        # Check CSV content is large and contains the data
        csv_output = response.content.decode()
        self.assertIn("prompt", csv_output)     # CSV header check

        # Ensure output generated successfully
        self.assertTrue(len(csv_output) > 0, "CSV content is empty")  # Check if the CSV content is large

        # Ensure system can handle large dataset
        log_count = AIResponseLog.objects.count()
        self.assertGreaterEqual(log_count, 1000, "Log count is less than 1000")

        # Confirm that a record from the dataset was used (the most recent one)
        latest_log = AIResponseLog.objects.order_by('-timestamp').first()
        self.assertIn(latest_log.input_query, csv_output)


class ExportPayloadTests(APITestCase):
    def setUp(self):
        # 1. Get the custom user model
        User = get_user_model()

        # 2. Create the user. 
        #    Your custom model uses email, not username.
        self.user = User.objects.create_user(
            email="test@test.com", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)

        # Mock confidence result
        self.mock_confidence_result = {
            "model_a": "gemma3:latest",
            "model_b": "gemma3:4b",
            "a_conf_pct": 90,
            "b_conf_pct": 80,
            "embed_model": "nomic-embed-text",
            "agreement_pct": 85,
            "a_self": 0.9,
            "b_self": 0.8,
            "agreement": 0.85,
            "best_model": "gemma3:4b",
            "best_answer": "Answer 1",
        }

        # Mock transient data that is not in the database
        self.mock_raw_payload = {
            "model": "gemma3:latest",
            "note": "Mocked raw payload",

            # Distributions and log-likelihoods
            "per_token": [
                {"token": "Paris", "prob": 0.9, "logprob": -0.105, "topk": []}
            ],
            "binary_probs": {"yes": 0.98, "no": 0.02},
        }

        # Patch the functions where they are used in the views.py file
    @patch('llm.views.confidence_and_answer')
    @patch('llm.views.build_raw_payload')
    def test_raw_json_export_contains_all_transient_fields(self, mock_build_raw_payload, mock_confidence_and_answer):
        """
        Ensure the raw JSON export contains all transient fields which aren't in database
        """
        # Set up mock responses
        mock_confidence_and_answer.return_value = self.mock_confidence_result
        mock_build_raw_payload.return_value = self.mock_raw_payload
        # Call the raw-exports API endpoint
        url = reverse('raw-exports')    # Use the URL for 'export_raw_outputs'
        data = {'text': 'What is the capital of France?', 'format': 'json'}
        response = self.client.post(url, data, format='json')
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.data
        # Check if all transient fields are present in the response data
        self.assertIn('per_token', response_data, "Missing 'per_token' (distributions)")
        self.assertIn('binary_probs', response_data, "Missing 'binary_probs' (log-likelihoods)")
        # Check if the transient fields have the expected values
        self.assertEqual(response_data['per_token'][0]['token'], 'Paris')
        self.assertEqual(response_data['binary_probs']['yes'], 0.98)
        # Check for calibration stats
        self.assertIn('calibration', response_data, "Missing 'calibration' stats")
        # Check for a field from database log
        self.assertEqual(response_data['overall']['best_answer'], 'Answer 1')