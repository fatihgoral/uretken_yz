import json
from pathlib import Path
from llm.gemini_client import GeminiClient

PLAN_FILE = Path("plan.json")
client = GeminiClient()


def _safe_json_parse(text: str) -> dict:
    """
    LLM çıktısından güvenli JSON ayıklar.
    Fallback yalnızca çıktı biçimi içindir.
    """
    if not text:
        raise ValueError("Boş LLM çıktısı")

    cleaned = text.replace("```json", "").replace("```", "").strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("JSON bulunamadı")

    return json.loads(cleaned[start:end + 1])


def critique_plan(plan_path: Path = None) -> dict:
    """
    PlanCriticAgent
    - Mevcut çalışma planını değerlendirir
    """
    if plan_path is None:
        plan_path = PLAN_FILE

    if not plan_path.exists():
        return {
            "status": "no_plan",
            "comment": f"'{plan_path.name}' planı bulunamadı."
        }

    try:
        with open(plan_path, "r", encoding="utf-8") as f:
            plan = json.load(f)
    except json.JSONDecodeError:
        return {
            "status": "invalid_plan",
            "comment": "Plan dosyası okunamadı veya bozuk."
        }

    prompt = f"""
Critique study plan. Ensure workload balance & logical flow.
IMPORTANT: All output (strengths, weaknesses, suggestion, reason_for_action) MUST be in TURKISH (TÜRKÇE).
Output ONLY JSON:
{{
  "overall_quality": 0-100,
  "load_balance": "low|balanced|high",
  "strengths": ["str"], "weaknesses": ["str"],
  "suggestion": "string",
  "proposed_improvement": {{
      "action": "multiplier|none",
      "value": float,
      "reason_for_action": "str"
  }}
}}
Plan: {json.dumps(plan, ensure_ascii=False)}
"""

    raw = client.generate(prompt)

    try:
        return _safe_json_parse(raw)
    except Exception:
        # ❗ Eleştiri üretmeyen fallback
        return {
            "status": "parse_error",
            "comment": "LLM eleştirisi üretildi ancak JSON biçimi çözümlenemedi."
        }
