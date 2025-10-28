#!/usr/bin/env python3
"""
Check the database logs to see what's been logged
"""
import os
import sys
import django

# Add the Django project to the path
sys.path.append('/Users/munnavar/Desktop/ConfidenTech/backEnd/confidenTech')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'confidenTech.settings')
django.setup()

from llm.models import AIResponseLog

def check_logs():
    """Check what's in the database logs"""
    print("📊 Checking Database Logs...")
    
    # Get all logs
    logs = AIResponseLog.objects.all().order_by('-timestamp')
    
    print(f"📈 Total logs in database: {logs.count()}")
    
    if logs.count() == 0:
        print("❌ No logs found in database")
        return
    
    # Show recent logs
    print(f"\n📋 Recent 5 logs:")
    for i, log in enumerate(logs[:5], 1):
        print(f"\n{i}. Log ID: {log.id}")
        print(f"   Timestamp: {log.timestamp}")
        print(f"   Input Query: \"{log.input_query}\"")
        print(f"   Best Answer: \"{log.best_answer[:100]}...\"")
        print(f"   Final Confidence: {log.final_confidence}%")
        print(f"   Best Model: {log.best_model}")
        print(f"   Agreement Score: {log.agreement_score}")
        print("-" * 50)
    
    # Statistics
    high_conf = logs.filter(final_confidence__gte=90).count()
    medium_conf = logs.filter(final_confidence__gte=70, final_confidence__lt=90).count()
    low_conf = logs.filter(final_confidence__lt=70).count()
    
    print(f"\n📊 Confidence Statistics:")
    print(f"   High confidence (≥90%): {high_conf}")
    print(f"   Medium confidence (70-89%): {medium_conf}")
    print(f"   Low confidence (<70%): {low_conf}")

if __name__ == "__main__":
    check_logs()
