from django.http import HttpResponse
from django.utils import timezone
import csv, io, json as pyjson
from datetime import datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated  
from rest_framework.response import Response
from .models import AIResponseLog, ExportAuditLog  
from .service import confidence_and_answer, build_raw_payload
from .compliance import detect_sensitive_data, sanitize_text


# ---------- helpers ----------
def _get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    return xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR")

def _log_export(*, request, endpoint, dataset, params, file_format,
                status="success", filename="", message=""):
    # ---- Compliance check ----
    text_to_check = ""
    if isinstance(params, dict):
        text_to_check = " ".join(str(v) for v in params.values())

    hits = detect_sensitive_data(text_to_check)  # ['email', 'phone', ...]
    compliance_passed = not hits
    safe_params = params
    note = ""
    if isinstance(params, dict) and hits:
        safe_params = {k: sanitize_text(str(v)) for k, v in params.items()}
        note = f" Sensitive data detected: {', '.join(hits)}"

    ExportAuditLog.objects.create(
        user=getattr(request, "user", None),
        endpoint=endpoint,
        dataset=dataset,
        params=safe_params,
        file_format=file_format,
        filename=filename,
        status=status if compliance_passed else "blocked",
        message=(message + note).strip(),
        ip=_get_client_ip(request),
    )


def _get_prompt_from_request(request, *, allow_get_query: bool = True):
    prompt = None
    if hasattr(request, "data") and isinstance(request.data, dict):
        prompt = request.data.get("text")
        if not prompt and allow_get_query:
            prompt = request.query_params.get("text")
    else:
        if allow_get_query:
            prompt = request.GET.get("text")
    return (prompt or "").strip()

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def get_confidence_score(request):
    """
    Take in a prompt from the front end, and retrieve an AI output and confidence score
    """
    if request.method == 'POST':
        prompt = (request.data.get('text') or '').strip()
    else:
        prompt = _get_prompt_from_request(request)

    if not prompt:
        return Response({'error': 'Prompt is empty'}, status=status.HTTP_400_BAD_REQUEST)

    result = confidence_and_answer(prompt)

    log_entry = AIResponseLog.objects.create(
        input_query=prompt,
        model_a=result.get("model_a"),
        model_b=result.get("model_b"),
        embed_model=result.get("embed_model"),
        model_a_confidence=result.get("a_self"),
        model_b_confidence=result.get("b_self"),
        agreement_score=result.get("agreement"),
        final_confidence=(
            result.get("a_conf_pct")
            if result.get("best_model") == result.get("model_a")
            else result.get("b_conf_pct")
        ),
        best_model=result.get("best_model"),
        best_answer=result.get("best_answer"),
    )

    return Response(
        {'confidence': log_entry.final_confidence, 'answer': log_entry.best_answer},
        status=status.HTTP_200_OK
    )


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def get_raw_outputs(request):

    prompt = _get_prompt_from_request(request, allow_get_query=True)
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
    final_conf_pct = a_conf_pct if best_model == model_a else b_conf_pct

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
        "per_token": raw_block.get("per_token", []),
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


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])   
def export_raw_outputs(request):

    if request.method == 'GET':
        prompt = (request.GET.get('text') or "").strip()
        fmt = (request.GET.get('export_format') or "json").lower()
    else:
        data = request.data if hasattr(request, "data") and isinstance(request.data, dict) else {}
        prompt = (data.get('text') or request.query_params.get('text') or "").strip()
        fmt = (data.get('export_format') or data.get('format')
               or request.query_params.get('export_format')
               or request.query_params.get('format') or "json").lower()

    if not prompt:
        return Response({
            "detail": "Provide prompt via POST {'text': '...','format':'csv|json'} "
                      "or GET ?text=...&export_format=csv|json"
        }, status=status.HTTP_400_BAD_REQUEST)

    if fmt not in ("json", "csv"):
        return Response({"detail": "export_format/format must be 'json' or 'csv'."},
                        status=status.HTTP_400_BAD_REQUEST)

    audit_params = {
        "prompt": prompt,
        "requested_format": fmt,
        "want_tokens": True, "topk": 5, "max_tokens": 256
    }

    try:
        result = confidence_and_answer(prompt)
    except Exception as e:
        _log_export(
            request=request, endpoint="/llm/api/raw/export/", dataset="raw_outputs",
            params=audit_params, file_format=fmt, status="error", message=f"compute_error: {e}"
        )
        return Response({'detail': f'backend error: {e}'}, status=status.HTTP_502_BAD_GATEWAY)

    model_a = result.get("model_a")
    model_b = result.get("model_b")
    a_conf_pct = int(result.get("a_conf_pct", 0))
    b_conf_pct = int(result.get("b_conf_pct", 0))
    best_model = result.get("best_model") or model_a
    best_answer = result.get("best_answer", "")
    final_conf_pct = a_conf_pct if best_model == model_a else b_conf_pct

    raw_block = build_raw_payload(
        prompt=prompt,
        chosen_model=best_model,
        final_confidence_pct=final_conf_pct,
        want_tokens=True,
        topk=5,
        max_tokens=256,
    )

    qs = AIResponseLog.objects.order_by("-timestamp").values_list("final_confidence", flat=True)[:200]
    vals = list(qs)
    n = len(vals)
    buckets = {"0-49": 0, "50-74": 0, "75-100": 0}
    for v in vals:
        if v < 50: buckets["0-49"] += 1
        elif v < 75: buckets["50-74"] += 1
        else: buckets["75-100"] += 1
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
        "per_token": raw_block.get("per_token", []),
        "binary_probs": raw_block["binary_probs"],
        "calibration": {
            "sample_size": n,
            "mean_final_confidence": avg,
            "bucket_counts": buckets
        }
    }
    if "note" in raw_block:
        payload["note"] = raw_block["note"]

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

    if fmt == "json":
        suggested = f"raw_export_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json"
        _log_export(
            request=request, endpoint="/llm/api/raw/export/", dataset="raw_outputs",
            params=audit_params, file_format="json", status="success", filename=suggested
        )
        return Response(payload, status=status.HTTP_200_OK)

    buf = io.StringIO()
    buf.write('\ufeff')
    writer = csv.writer(buf)
    writer.writerow([
        "prompt", "chosen_model",
        "final_confidence_pct", "agreement_pct", "a_conf_pct", "b_conf_pct",
        "binary_yes", "binary_no",
        "calib_sample_size", "calib_mean_final_conf",
        "calib_bucket_0_49", "calib_bucket_50_74", "calib_bucket_75_100",
        "token_index", "token", "logprob", "prob", "topk_json"
    ])

    per_token = payload["per_token"] or []
    if per_token:
        for idx, t in enumerate(per_token):
            writer.writerow([
                payload["prompt"], payload["chosen_model"],
                payload["overall"]["final_confidence_pct"], payload["overall"]["agreement_pct"],
                payload["overall"]["a_conf_pct"], payload["overall"]["b_conf_pct"],
                payload["binary_probs"]["yes"], payload["binary_probs"]["no"],
                payload["calibration"]["sample_size"], payload["calibration"]["mean_final_confidence"],
                payload["calibration"]["bucket_counts"]["0-49"],
                payload["calibration"]["bucket_counts"]["50-74"],
                payload["calibration"]["bucket_counts"]["75-100"],
                idx, t.get("token"), t.get("logprob"), t.get("prob"),
                pyjson.dumps(t.get("topk") or [], ensure_ascii=False),
            ])
    else:
        writer.writerow([
            payload["prompt"], payload["chosen_model"],
            payload["overall"]["final_confidence_pct"], payload["overall"]["agreement_pct"],
            payload["overall"]["a_conf_pct"], payload["overall"]["b_conf_pct"],
            payload["binary_probs"]["yes"], payload["binary_probs"]["no"],
            payload["calibration"]["sample_size"], payload["calibration"]["mean_final_confidence"],
            payload["calibration"]["bucket_counts"]["0-49"],
            payload["calibration"]["bucket_counts"]["50-74"],
            payload["calibration"]["bucket_counts"]["75-100"],
            "", "", "", "", ""
        ])

    csv_data = buf.getvalue()
    buf.close()

    fname = f'raw_export_{datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")}.csv'
    _log_export(
        request=request, endpoint="/llm/api/raw/export/", dataset="raw_outputs",
        params=audit_params, file_format="csv", status="success", filename=fname
    )
    resp = HttpResponse(csv_data, content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = f'attachment; filename="{fname}"'
    return resp


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def export_confidence_data(request):

    if request.method == "GET":
        text = (request.GET.get("text") or "").strip()
        fmt = (request.GET.get("format") or "csv").lower()
    else:
        data = request.data if hasattr(request, "data") and isinstance(request.data, dict) else {}
        text = (data.get("text") or request.query_params.get("text") or "").strip()
        fmt = (data.get("format") or request.query_params.get("format") or "csv").lower()

    latest = None
    if not text:
        latest = AIResponseLog.objects.order_by("-timestamp").first()
        if latest:
            text = latest.input_query
        else:
            _log_export(
                request=request, endpoint="/exportConfidenceData", dataset="confidence_export",
                params={"text": text, "format": fmt}, file_format=fmt, status="error",
                message="no_text_and_no_fallback"
            )
            return Response({"detail": "No prompt provided and no previous logs to fall back to."},
                            status=status.HTTP_400_BAD_REQUEST)

    if fmt not in ("csv", "json"):
        _log_export(
            request=request, endpoint="/exportConfidenceData", dataset="confidence_export",
            params={"text": text, "format": fmt}, file_format=fmt, status="error",
            message="invalid_format"
        )
        return Response({"detail": "format must be 'csv' or 'json'."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        result = confidence_and_answer(text)
    except Exception as e:
        _log_export(
            request=request, endpoint="/exportConfidenceData", dataset="confidence_export",
            params={"text": text, "format": fmt}, file_format=fmt, status="error",
            message=f"compute_error: {e}"
        )
        return Response({'detail': f'backend error: {e}'}, status=status.HTTP_502_BAD_GATEWAY)

    model_a = result.get("model_a")
    model_b = result.get("model_b")
    a_conf_pct = int(result.get("a_conf_pct", 0))
    b_conf_pct = int(result.get("b_conf_pct", 0))
    best_model = result.get("best_model") or model_a
    best_answer = result.get("best_answer", "")
    final_conf_pct = a_conf_pct if best_model == model_a else b_conf_pct

    raw_block = build_raw_payload(
        prompt=text,
        chosen_model=best_model,
        final_confidence_pct=final_conf_pct,
        want_tokens=True,
        topk=5,
        max_tokens=256,
    )

    qs = AIResponseLog.objects.order_by("-timestamp").values_list("final_confidence", flat=True)[:200]
    vals = list(qs)
    n = len(vals)
    buckets = {"0-49": 0, "50-74": 0, "75-100": 0}
    for v in vals:
        if v < 50: buckets["0-49"] += 1
        elif v < 75: buckets["50-74"] += 1
        else: buckets["75-100"] += 1
    avg = round(sum(vals) / n, 2) if n else None

    payload = {
        "prompt": text,
        "chosen_model": raw_block["model"],
        "overall": {
            "final_confidence_pct": final_conf_pct,
            "best_answer": best_answer,
            "agreement_pct": int(result.get("agreement_pct", 0)),
            "a_conf_pct": a_conf_pct,
            "b_conf_pct": b_conf_pct,
        },
        "per_token": raw_block.get("per_token", []),
        "binary_probs": raw_block["binary_probs"],
        "calibration": {
            "sample_size": n,
            "mean_final_confidence": avg,
            "bucket_counts": buckets
        }
    }
    if "note" in raw_block:
        payload["note"] = raw_block["note"]

    if fmt == "json":
        fname = f'confidence_export_{timezone.localdate().strftime("%Y%m%d")}.json'
        _log_export(
            request=request, endpoint="/exportConfidenceData", dataset="confidence_export",
            params={"text": text, "format": "json"}, file_format="json", status="success",
            filename=fname
        )
        resp = HttpResponse(pyjson.dumps(payload, ensure_ascii=False, indent=2),
                            content_type="application/json; charset=utf-8")
        resp['Content-Disposition'] = f'attachment; filename="{fname}"'
        return resp

    # CSV
    buf = io.StringIO()
    buf.write('\ufeff')  # UTF-8 BOM
    writer = csv.writer(buf)
    writer.writerow([
        "prompt", "chosen_model",
        "final_confidence_pct", "agreement_pct", "a_conf_pct", "b_conf_pct",
        "binary_yes", "binary_no",
        "calib_sample_size", "calib_mean_final_conf",
        "calib_bucket_0_49", "calib_bucket_50_74", "calib_bucket_75_100",
        "token_index", "token", "logprob", "prob", "topk_json"
    ])
    per_token = payload["per_token"] or []
    if per_token:
        for idx, t in enumerate(per_token):
            writer.writerow([
                payload["prompt"], payload["chosen_model"],
                payload["overall"]["final_confidence_pct"], payload["overall"]["agreement_pct"],
                payload["overall"]["a_conf_pct"], payload["overall"]["b_conf_pct"],
                payload["binary_probs"]["yes"], payload["binary_probs"]["no"],
                payload["calibration"]["sample_size"], payload["calibration"]["mean_final_confidence"],
                payload["calibration"]["bucket_counts"]["0-49"],
                payload["calibration"]["bucket_counts"]["50-74"],
                payload["calibration"]["bucket_counts"]["75-100"],
                idx, t.get("token"), t.get("logprob"), t.get("prob"),
                pyjson.dumps(t.get("topk") or [], ensure_ascii=False),
            ])
    else:
        writer.writerow([
            payload["prompt"], payload["chosen_model"],
            payload["overall"]["final_confidence_pct"], payload["overall"]["agreement_pct"],
            payload["overall"]["a_conf_pct"], payload["overall"]["b_conf_pct"],
            payload["binary_probs"]["yes"], payload["binary_probs"]["no"],
            payload["calibration"]["sample_size"], payload["calibration"]["mean_final_confidence"],
            payload["calibration"]["bucket_counts"]["0-49"],
            payload["calibration"]["bucket_counts"]["50-74"],
            payload["calibration"]["bucket_counts"]["75-100"],
            "", "", "", "", ""
        ])

    csv_data = buf.getvalue()
    buf.close()
    fname = f'confidence_export_{timezone.localdate().strftime("%Y%m%d")}.csv'
    _log_export(
        request=request, endpoint="/exportConfidenceData", dataset="confidence_export",
        params={"text": text, "format": "csv"}, file_format="csv", status="success",
        filename=fname
    )
    resp = HttpResponse(csv_data, content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = f'attachment; filename="{fname}"'
    return resp
