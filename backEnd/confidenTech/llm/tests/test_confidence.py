from django.test import TestCase
from unittest.mock import patch
from llm.service import confidence_and_answer, compare_and_score, _pct, _cos

import numpy as np

class ConfidenceCalculationTests(TestCase):
    def test_pct_function(self):
        self.assertEqual(_pct(0.95), 95)
        self.assertEqual(_pct(1.5), 100)     # Upper bound
        self.assertEqual(_pct(-0.3), 0)      # Lower bound
        self.assertEqual(_pct(0), 0)         # Exact bound
        self.assertEqual(_pct(1), 100)       # Exact bound

    def test_cosine_similarity(self):
        a = np.array([1, 0])
        b = np.array([0, 1])
        c = np.array([-1, 0])
        self.assertAlmostEqual(_cos(a, b), 0.0)
        self.assertAlmostEqual(_cos(a, a), 1.0)         # Identical vectors should have 1 similarity
        self.assertAlmostEqual(_cos(a, c), -1.0)        # Opposite vectors should have -1 similarity

    def test_cosine_similarity_with_zero_vector(self):
        # Tests that a zero-length vector doesn't cause a crash
        a = np.array([1, 2, 3])
        b = np.array([0, 0, 0])

        # Should safely return 0 instead of a DivisionByZeroError
        self.assertEqual(_cos(a, b), 0.0)


    @patch("llm.service.app.invoke")
    def test_confidence_and_answer(self, mock_invoke):
        """
        Test the main confidence_and_answer without real HTTP calls
        """
        # --- Mock the two models' text outputs ---
        mock_invoke.return_value = {
            "prompt": "Who is the president of the United States?",
            "model_a": "Answer A",
            "model_b": "Answer B",
            "best_model": "A",
            "best_answer": "Answer A",
            "a_conf_pct": 96,
            "b_conf_pct": 88
        }        
        

        result = confidence_and_answer("Who is the president of the United States?")

        self.assertEqual(result["prompt"], "Who is the president of the United States?")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["model_a"], "Answer A")
        self.assertEqual(result["model_b"], "Answer B")
        self.assertEqual(result["best_model"], "A")
        self.assertEqual(result["best_answer"], "Answer A")
        self.assertEqual(result["a_conf_pct"], 96)
        self.assertEqual(result["b_conf_pct"], 88)

# Strong Aggreement Path Test
    @patch("llm.service._embed")
    def test_compare_and_score_logic_high_confidence(self, mock_embed):
        """
        Directly test compare_and_score with mock embeddings
        Tests a standard case with strong agreement and high confidence.
        SCENARIO: High agreement, and Model A has higher self-confidence
        """
        mock_embed.side_effect = [
            np.array([1, 0]),               # Embedding for Answer A
            np.array([0.9, 0.1]),           # Embedding for Asnwer B
        ]
        
        state = {
            "a_answer": "Test A",
            "b_answer": "Test B",
            "a_self": 0.9,
            "b_self": 0.7,
            "embed_model": "fake-embed",
            "weight_agreement": 0.6,
            "model_a": "A",
            "model_b": "B",
        }

        """Calculation: 
        agreement = _cos([1, 0], [0.9, 0.1]) ~= 0.9939
        final_confidence = weight * agreement + (1 - weight) * self_confidence
        a_conf = 0.6 * 0.9939 + 0.4 * 0.9 = 0.95634 -> 96
        b_conf = 0.6 * 0.9939 + 0.4 * 0.7 = 0.87634 -> 88
        Model A should win.
        """
        result = compare_and_score(state)

        self.assertAlmostEqual(result['agreement'], 0.9939, places=4)
        self.assertEqual(result['a_conf_pct'], 96)
        self.assertEqual(result['b_conf_pct'], 88)
        self.assertEqual(result['best_model'], "A")
        self.assertEqual(result['best_answer'], "Test A")

# Strong Disagreement Path Test
    @patch("llm.service._embed")
    def test_compare_and_score_logic_strong_disagreement(self, mock_embed):
        """
        Tests that when answers disagree, the final score relies on self-confidence
        # SCENARIO: The answers are completely different
        """
        mock_embed.side_effect = [
            np.array([1, 0]),   # Embedding for Answer A
            np.array([0, 1]),   # Embedding for Answer B 
        ]

        state = {
            "a_answer": "Cats",
            "b_answer": "Dogs",
            "a_self": 0.9,
            "b_self": 0.8,
            "embed_model": "fake-embed",
            "weight_agreement": 0.6,
            "model_a": "A",
            "model_b": "B",
        }

        """ Calculation:
        agreement = _cos([1, 0], [0, 1]) = 0.0
        a_conf = 0.6 * 0.0 + 0.4 * 0.9 = 0.36 -> 36
        b_conf = 0.6 * 0.0 + 0.4 * 0.8 = 0.32 -> 32
        Final scores are low, and Model A wins.
        """
        result = compare_and_score(state)

        self.assertEqual(result['agreement'], 0.0)
        self.assertEqual(result['a_conf_pct'], 36)
        self.assertEqual(result['b_conf_pct'], 32)
        self.assertEqual(result['best_model'], "A")


    # Identical Self-Confidence Path Test
    @patch("llm.service._embed")
    def test_compare_and_score_logic_tiebreaker(self, mock_embed):
        """
        Tests that Model A wins when the final scores are identical
        SCENARIO: Agreement and self-confidence result in a perfect tie.
        """

        mock_embed.side_effect = [
            np.array([1, 0]),           # Identical embeddings
            np.array([1, 0]),       
        ]

        state = {
            "a_answer": "Same",
            "b_answer": "Same",
            "a_self": 0.8,          # Identical self-confidence (a_self = b_self)
            "b_self": 0.8,
            "embed_model": "fake-embed",
            "weight_agreement": 0.6,
            "model_a": "A",
            "model_b": "B",
        }

        """ Calculation:
        agreement = _cos([1, 0], [1, 0]) = 1.0
        a_conf = 0.6 * 1.0 + 0.4 * 0.8 = 0.92 -> 92
        b_conf = 0.6 * 1.0 + 0.4 * 0.8 = 0.92 -> 92
        It's a tie, so the code should default to Model A
        """
        result = compare_and_score(state)

        self.assertEqual(result['agreement'], 1.0)
        self.assertEqual(result['a_conf_pct'], 92)
        self.assertEqual(result['b_conf_pct'], 92)
        self.assertEqual(result['best_model'], "A")


    # One High/One Low Self Confidence Path Test
    @patch("llm.service._embed")
    def test_compare_and_score_logic_one_high_one_low_self_confidence(self, mock_embed):
        """
        Tests that the logic favors a model with much higher self-confidence
        SCENARIO: Perfect agreement, but Model A is certain and Model B is guessing.
        """
        mock_embed.side_effect = [
            np.array([1, 0]),       # Identical embeddings for perfect agreement
            np.array([1, 0]),
        ]

        state = {
            "a_answer": "Same",
            "b_answer": "Same",
            "a_self": 0.95,          # Large gap in self-confidence
            "b_self": 0.10,
            "embed_model": "fake-embed",
            "weight_agreement": 0.6,
            "model_a": "A",
            "model_b": "B",
        }

        """ Calculation:
        agreement = 1.0
        a_conf = 0.6 * 1.0 + 0.4 * 0.95 = 0.6 + 0.38 = 0.98 -> 98
        b_conf = 0.6 * 1.0 + 0.4 * 0.10 = 0.6 + 0.04 = 0.64 -> 64
        Model A should win by a large margin.
        """
        result = compare_and_score(state)

        self.assertEqual(result['agreement'], 1.0)
        self.assertEqual(result['a_conf_pct'], 98)
        self.assertEqual(result['b_conf_pct'], 64)
        self.assertEqual(result['best_model'], "A")
