from django.contrib import admin
from .models import AIResponseLog

# Register your models here.
@admin.register(AIResponseLog)
class AIResponseLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'input_query_short', 'best_answer_short', 'final_confidence', 'best_model', 'agreement_score')
    list_filter = ('best_model', 'final_confidence', 'timestamp')
    search_fields = ('input_query', 'best_answer')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
    
    def input_query_short(self, obj):
        return obj.input_query[:50] + '...' if len(obj.input_query) > 50 else obj.input_query
    input_query_short.short_description = 'Input Query'
    
    def best_answer_short(self, obj):
        return obj.best_answer[:50] + '...' if len(obj.best_answer) > 50 else obj.best_answer
    best_answer_short.short_description = 'Best Answer'
    
    fieldsets = (
        ('Query Information', {
            'fields': ('input_query', 'timestamp')
        }),
        ('Model Information', {
            'fields': ('model_a', 'model_b', 'embed_model', 'best_model')
        }),
        ('Confidence Scores', {
            'fields': ('model_a_confidence', 'model_b_confidence', 'agreement_score', 'final_confidence')
        }),
        ('Response', {
            'fields': ('best_answer',)
        }),
    )