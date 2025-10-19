from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import AIResponseLog
from .service import confidence_and_answer, build_raw_payload
from django.db.models import F

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def get_confidence_score(request):
    """
    Take in a prompt from the front end, and retrieve and AI output and confidence score
    """
    if request.method == 'POST':
        prompt = request.data.get('text', '')

        if not prompt:
            return Response({'error': 'Prompt is empty'}, status=status.HTTP_400_BAD_REQUEST)
    
        # Get full result dictionary from service.py
        result = confidence_and_answer(prompt)         

        # Set up log to MongoDB here
        log_entry = AIResponseLog.objects.create(
            input_query=prompt,
            model_a=result.get("model_a"),
            model_b=result.get("model_b"),
            embed_model=result.get("embed_model"),
            model_a_confidence=result.get("a_self"),
            model_b_confidence=result.get("b_self"),
            agreement_score=result.get("agreement"),

            # Determine which confidence to use as the final one
            final_confidence=(
                result.get("a_conf_pct")
                if result.get("best_model") == result.get("model_a")
                else result.get("b_conf_pct")
            ),
            
            best_model=result.get("best_model"),
            best_answer=result.get("best_answer")
        )

        # Return the simplified response to frontend
        return Response({
            'confidence': log_entry.final_confidence,
            'answer': log_entry.best_answer
        }, status=status.HTTP_200_OK)

    return Response({'message': 'Success'}, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def get_raw_outputs(request):
    prompt = (request.data.get('text') or "").strip()
    if not prompt:
        return Response({'error': 'Prompt is empty'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        result = confidence_and_answer(prompt)
    except Exception as e:
        return Response({'detail': f'backend error: {e}'}, status=status.HTTP_502_BAD_GATEWAY)

    model_a = result.get("model_a")
    model_b = result.get("model_b")
    a_conf_pct = int(result.get("a_conf_pct", 0))
    b_conf_pct = int(result.get("b_conf_pct", 0))
    best_model = result.get("best_model") or model_a
    best_answer = result.get("best_answer", "")

    if best_model == model_a:
        final_conf_pct = a_conf_pct
    else:
        final_conf_pct = b_conf_pct

    raw_block = build_raw_payload(
        prompt=prompt,
        chosen_model=best_model,
        final_confidence_pct=final_conf_pct,
        want_tokens=True,     
        topk=5,
        max_tokens=256,
    )

    AIResponseLog.objects.create(
        input_query=prompt,
        model_a=model_a,
        model_b=model_b,
        embed_model=result.get("embed_model"),
        model_a_confidence=result.get("a_self"),
        model_b_confidence=result.get("b_self"),
        agreement_score=result.get("agreement"),
        final_confidence=final_conf_pct,
        best_model=best_model,
        best_answer=best_answer
    )

    qs = AIResponseLog.objects.order_by("-timestamp").values_list("final_confidence", flat=True)[:200]
    vals = list(qs)
    n = len(vals)
    buckets = {"0-49": 0, "50-74": 0, "75-100": 0}
    for v in vals:
        if v < 50:
            buckets["0-49"] += 1
        elif v < 75:
            buckets["50-74"] += 1
        else:
            buckets["75-100"] += 1
    avg = round(sum(vals) / n, 2) if n else None

    payload = {
        "prompt": prompt,
        "chosen_model": raw_block["model"],
        "overall": {
            "final_confidence_pct": final_conf_pct,
            "best_answer": best_answer,
            "agreement_pct": int(result.get("agreement_pct", 0)),
            "a_conf_pct": a_conf_pct,
            "b_conf_pct": b_conf_pct,
        },
        "per_token": raw_block["per_token"],        
        "binary_probs": raw_block["binary_probs"],  
        "calibration": {
            "sample_size": n,
            "mean_final_confidence": avg,
            "bucket_counts": buckets
        }
    }
    if "note" in raw_block:
        payload["note"] = raw_block["note"]

    return Response(payload, status=status.HTTP_200_OK)
    