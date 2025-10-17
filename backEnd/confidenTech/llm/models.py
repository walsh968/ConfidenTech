from django.db import models

class AIResponseLog(models.Model):
    input_query = models.TextField()
    model_a = models.CharField(max_length=100)
    model_b = models.CharField(max_length=100)
    embed_model = models.CharField(max_length=100)
    # Storing the raw self-confidence from the models
    model_a_confidence = models.FloatField()
    model_b_confidence = models.FloatField()
    agreement_score = models.FloatField()
    # Storing the final calculated confidence
    final_confidence = models.IntegerField()
    best_model = models.CharField(max_length=100)
    best_answer = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M')} - {self.input_query[:40]}..."