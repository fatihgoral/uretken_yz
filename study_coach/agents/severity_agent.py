import json
from llm.gemini_client import GeminiClient

client = GeminiClient()


def analyze_severity(feedback_text: str, emotion: dict) -> dict:
    """
    Severity Agent
    - Geri bildirimin ciddiyetini SADECE LLM ile belirler
    - Fallback yalnızca JSON / parse güvenliği içindir
    """

    if not feedback_text or not feedback_text.strip():
        return {
            "status": "invalid_input",
            "message": "Boş geri bildirim verildi."
        }

    prompt = f"""
Sen deneyimli bir EĞİTİM KOÇU etmensin.

Aşağıdaki öğrencinin geri bildiriminin
çalışma planı açısından ne kadar CİDDİ olduğunu değerlendir.

SADECE JSON DÖNDÜR:

{{
  "severity": "low | medium | high",
  "reason": "kısa gerekçe"
}}

GERİ BİLDİRİM METNİ:
{feedback_text}

DUYGU ANALİZİ:
{json.dumps(emotion, ensure_ascii=False)}
"""

    try:
        raw = client.generate(prompt)
        cleaned = raw.replace("```json", "").replace("```", "").strip()

        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("JSON bulunamadı")

        return json.loads(cleaned[start:end + 1])

    except Exception:
        # ❗ Fallback SADECE parse seviyesinde
        return {
            "status": "invalid_output",
            "message": "Severity Agent: LLM çıktısı JSON formatında çözümlenemedi."
        }
