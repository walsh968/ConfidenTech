from __future__ import annotations
import math
from typing import TypedDict
import requests, json, numpy as np, os
from langgraph.graph import StateGraph, START, END
from urllib.parse import urljoin
from openai import OpenAI
from django.conf import settings

API_KEY = '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'
URL = 'https://api.groq.com/openai/v1'

client = OpenAI(api_key=API_KEY, base_url=URL)
openai_client = OpenAI()
# ---------------- Config ----------------
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
GEN = urljoin(OLLAMA_HOST + "/", "api/generate")
EMB = urljoin(OLLAMA_HOST + "/", "api/embeddings")

# Use your locally available Gemma models
#MODEL_A = "gemma3:4b"
#MODEL_B = "deepseek-r1:8b"
MODEL_A = 'llama-3.3-70b-versatile'
MODEL_B = 'llama-3.1-8b-instant'
# Pick a small embedding model if you have one (pull one if missing)
#EMBED_MODEL = "nomic-embed-text"
EMBED_MODEL = "text-embedding-3-small"

# ---------------- State ----------------
class State(TypedDict, total=False):
    prompt: str
    model_a: str
    model_b: str
    embed_model: str
    weight_agreement: float

    a_answer: str
    a_self: float
    b_answer: str
    b_self: float

    agreement: float
    agreement_pct: int
    a_conf_pct: int
    b_conf_pct: int
    best_model: str
    best_answer: str

# ---------------- Helpers ----------------
def _pct(x: float) -> int:
    return int(round(max(0.0, min(1.0, x)) * 100))

def _cos(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denom) if denom else 0.0

def _ollama_generate(model: str, prompt: str) -> tuple[str, float]:
    """Ask a model to return JSON {answer, self_confidence}."""
    system = (
        "You are a precise assistant. "
        "Return ONLY valid JSON: {\"answer\": string, \"self_confidence\": number between 0 and 1}."
    )
    # payload = {
    #     "model": model,
    #     "prompt": f"{system}\n\nUser: {prompt}\nAssistant:",
    #     "format": "json",
    #     "options": {"temperature": 0.2},
    #     "stream": False,
    # }
    # r = requests.post(GEN, json=payload, timeout=120)
    # r.raise_for_status()
    # raw = r.json().get("response", "").strip()

    completion = client.chat.completions.create(
        model=model,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )

    raw = completion.choices[0].message.content.strip()
    data = json.loads(raw)
    answer = str(data.get("answer", "")).strip()
    self_conf = float(max(0.0, min(1.0, data.get("self_confidence", 0.0))))
    return answer, self_conf

def _embed(text: str, model: str) -> np.ndarray:
    # r = requests.post(EMB, json={"model": model, "prompt": text}, timeout=30)
    # r.raise_for_status()

    r = openai_client.embeddings.create(
        model=model,
        input=text,
    )
    #vec = r.json().get("embedding")
    vec = r.data[0].embedding
    # if not isinstance(vec, list):
    #     raise RuntimeError("Invalid embedding response from Ollama.")
    return np.array(vec, dtype=float)

def _gen_with_logprobs(prompt: str, model: str, *, max_tokens: int = 256, topk: int = 5):

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True,  
        "options": {
            "temperature": 0.0,
            "num_predict": max_tokens,
            "logprobs": topk,  
        },
    }

    try:
        r = requests.post(GEN, json=payload, stream=True, timeout=180)
        r.raise_for_status()
    except Exception as e:
        return {"text": "", "per_token": [], "error": str(e)}

    full_text = []
    tokens = []

    for line in r.iter_lines(decode_unicode=True):
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue

        piece = obj.get("response") or obj.get("content") or ""
        if piece:
            full_text.append(piece)

        lp = obj.get("logprobs") or obj.get("log_probs") or None
        if isinstance(lp, dict):
            tok = lp.get("token")
            logp = lp.get("logprob")
            topk_items = []
            if isinstance(lp.get("top_logprobs"), list):
                for cand in lp["top_logprobs"]:
                    ctok = cand.get("token")
                    clogp = cand.get("logprob")
                    if ctok is None or clogp is None:
                        continue
                    topk_items.append({
                        "token": ctok,
                        "logprob": clogp,
                        "prob": math.exp(clogp) if isinstance(clogp, (int, float)) else None
                    })
            tokens.append({
                "token": tok,
                "logprob": logp,
                "prob": math.exp(logp) if isinstance(logp, (int, float)) else None,
                "topk": topk_items
            })

    return {
        "text": "".join(full_text).strip(),
        "per_token": tokens,
        "error": None
    }

def _generate_explanation_text(prompt: str, answer: str, final_score: int, agreement: int) -> str:
    """
    Uses an LLM to generate a human-readable explanation for the confidence score.
    """

    system_prompt = f"""
    You are an AI transparency analyst. Your job is to write a brief, 1-2 sentences explanation for a confidence score.
    You will be given the user's prompt, the AI's final answer, the final confidence score (0-100), and the agreement score between the two AI models (0-100).

    - If the confidence is high (> 80) and agreement is high (>75), explain WHY the answer us well-supported.
        - If the answer is just a fact (e.g. "Paris is the capital of France"): Say something similar to "High confidence is supported by the definitive, factual nature of the statement and strong model agreement."

    - If the confidence is medium (60-80), explain WHY the answer is somewhat supported and what makes it uncertain.
        - For example, something similar to "The score reflects partial agreement between models, suggesting the topic may be nuanced or open to interpretation."

    - If the confidence is low (< 60) or agreement is low (< 60), state that the answer is speculative and it should be verified.
        - For example, something similar to "Low confidence indicates significant disagreement between internal models or inherent uncertainty in the prediction."

    - DO NOT mention "Model A", "Model B", or "log-likelihoods" in your response.

    - Be direct and professional. Write the explanation only.

    - DO NOT hallucinate that studies exist if they are not in the text.

    Example:

    Prompt: "What is the benefit of meditation?"

    Answer: Adding meditation to your daily routine can reduce stress levels by up to 40% according to recent studies. Even 10 minutes per day can make a significant difference in mental well-being.

    Confidence Score: 86

    Agreement Score: 92

    Explanation: The AI is highly confident. Multiple peer-reviewed studies and medical institutions consistently report stress reduction benefits from meditation, supporting the high confidence level.

    """
    user_prompt = f"""

    Prompt: {prompt}
    Answer: {answer}
    Confidence Score: {final_score}
    Agreement Score: {agreement}
    Explanation:

    """

    payload = {
        "model": MODEL_A,
        "prompt": f"{system_prompt}\n\nUser: {user_prompt}",
        "format": "", # Ask for text, not JSON\
        "options": {"temperature": 0.3},
        "stream": False,
    }

    try:
        # r = requests.post(GEN, json=payload, timeout=120)
        # r.raise_for_status()
        # response_text = r.json().get("response", "").strip() # Extract the generated text
        completion = client.chat.completions.create(
            model=MODEL_A,  # or whichever Groq model you prefer for explanations
            temperature=0.3,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        response_text = completion.choices[0].message.content.strip()

        return response_text or "No explanation could be generated."

    except Exception as e:
        print(f"Error generating explanation: {e}")
        return "Explanation is unavailable due to a backend error."

def build_raw_payload(
    *,
    prompt: str,
    chosen_model: str,
    final_confidence_pct: int,
    want_tokens: bool = True,
    yes_label: str = "yes",
    no_label: str = "no",
    topk: int = 5,
    max_tokens: int = 256,
):
    gen_text = ""
    per_token_block = []
    err = None

    if want_tokens:
        res = _gen_with_logprobs(prompt, chosen_model, max_tokens=max_tokens, topk=topk)
        gen_text = res.get("text", "") or ""
        per_token_block = res.get("per_token", []) or []
        err = res.get("error")

    p_yes = max(0.0, min(1.0, final_confidence_pct / 100.0))
    p_no = round(1.0 - p_yes, 6)

    payload = {
        "model": chosen_model,
        "generated_text": gen_text,
        "per_token": per_token_block,
        "binary_probs": {
            yes_label: p_yes,
            no_label: p_no,
        },
    }
    if err:
        payload["note"] = f"logprobs unavailable or backend error: {err}"
    return payload

# ---------------- Nodes ----------------
def ask_model_a(state: State) -> State:
    ans, conf = _ollama_generate(state.get("model_a", MODEL_A), state["prompt"])
    return {"a_answer": ans, "a_self": conf}

def ask_model_b(state: State) -> State:
    ans, conf = _ollama_generate(state.get("model_b", MODEL_B), state["prompt"])
    return {"b_answer": ans, "b_self": conf}

def compare_and_score(state: State) -> State:
    embed_model = state.get("embed_model", EMBED_MODEL)
    w = state.get("weight_agreement", 0.6)

    ea = _embed(state["a_answer"], embed_model)
    eb = _embed(state["b_answer"], embed_model)
    agreement = _cos(ea, eb)
    agreement_pct = _pct(agreement)

    a_conf_pct = _pct(w * agreement + (1 - w) * state["a_self"])
    b_conf_pct = _pct(w * agreement + (1 - w) * state["b_self"])

    if a_conf_pct > b_conf_pct:
        best_model, best_answer = state["model_a"], state["a_answer"]
    elif b_conf_pct > a_conf_pct:
        best_model, best_answer = state["model_b"], state["b_answer"]
    else:
        best_model, best_answer = state["model_a"], state["a_answer"]

    return {
        "agreement": agreement,
        "agreement_pct": agreement_pct,
        "a_conf_pct": a_conf_pct,
        "b_conf_pct": b_conf_pct,
        "best_model": best_model,
        "best_answer": best_answer,
    }

# ---------------- Graph ----------------
graph = StateGraph(State)
graph.add_node("ask_a", ask_model_a)
graph.add_node("ask_b", ask_model_b)
graph.add_node("compare", compare_and_score)

graph.add_edge(START, "ask_a")
graph.add_edge(START, "ask_b")
graph.add_edge("ask_a", "compare")
graph.add_edge("ask_b", "compare")
graph.add_edge("compare", END)

app = graph.compile()

# ---------------- Run test ----------------
# if __name__ == "__main__":
#     initial: State = {
#         "prompt": "Who is the CEO of google?",
#         "model_a": MODEL_A,
#         "model_b": MODEL_B,
#         "embed_model": EMBED_MODEL,
#         "weight_agreement": 0.6,
#     }
#
#     out = app.invoke(initial)
#     from pprint import pprint
#     pprint({
#         "prompt": initial["prompt"],
#         "agreement_pct": out["agreement_pct"],
#         "answers": [
#             {"model": initial["model_a"], "answer": out["a_answer"], "confidence_pct": out["a_conf_pct"]},
#             {"model": initial["model_b"], "answer": out["b_answer"], "confidence_pct": out["b_conf_pct"]},
#         ],
#         "best_model": out["best_model"],
#         "best_answer": out["best_answer"],
#     })

def confidence_and_answer(
    prompt: str,
    *,
    model_a: str = MODEL_A,
    model_b: str = MODEL_B,
    embed_model: str = EMBED_MODEL,
    weight_agreement: float = 0.6,
) -> dict:
    """
    Returns a dictionary.
    """
    initial: State = {
        "prompt": prompt,
        "model_a": model_a,
        "model_b": model_b,
        "embed_model": embed_model,
        "weight_agreement": weight_agreement,
    }
    out = app.invoke(initial)
    #if out.get("best_model") == model_b:
        #return int(out.get("b_conf_pct", 0)), out.get("b_answer", "")
    #return int(out.get("a_conf_pct", 0)), out.get("a_answer", "")
    return out


