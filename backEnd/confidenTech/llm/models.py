from django.db import models
from django.conf import settings

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

class ExportAuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="Who triggered the export"
    )
    endpoint = models.CharField(max_length=128, help_text="API path used")
    dataset = models.CharField(max_length=128, help_text="Logical dataset name")
    params = models.JSONField(help_text="Parameters used to export")
    file_format = models.CharField(max_length=16)
    filename = models.CharField(max_length=256, blank=True)
    status = models.CharField(max_length=16, default="success")
    message = models.TextField(blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.created_at:%Y-%m-%d %H:%M:%S}] {self.user_id} {self.endpoint} {self.dataset} {self.file_format} {self.status}"