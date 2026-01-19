import json
from llm.gemini_client import GeminiClient

client = GeminiClient()


def analyze_emotion(text: str) -> dict:
    """
    Emotion Agent
    - Duygu analizini SADECE LLM ile yapar
    - Fallback yalnızca JSON / parse güvenliği içindir
    - ÇIKIŞ ŞEMASI HER ZAMAN AYNI
    """

    if not text or not text.strip():
        return {
            "emotion": "neutral",
            "polarity": 0.0,
            "source": "invalid_input"
        }

    prompt = f"""
Sen bir DUYGU ANALİZİ etmensin.

Aşağıdaki Türkçe öğrenci geri bildirimini analiz et.

SADECE JSON DÖNDÜR:

{{
  "emotion": "positive | negative | neutral",
  "polarity": -1 ile 1 arasında bir sayı
}}

METİN:
{text}
"""

    try:
        raw = client.generate(prompt)
        cleaned = raw.replace("```json", "").replace("```", "").strip()

        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("JSON bulunamadı")

        data = json.loads(cleaned[start:end + 1])

        return {
            "emotion": data.get("emotion", "neutral"),
            "polarity": float(data.get("polarity", 0.0)),
            "source": "llm"
        }

    except Exception:
        # ❗ SADECE FORMAT FALLBACK
        return {
            "emotion": "neutral",
            "polarity": 0.0,
            "source": "parse_fallback"
        }
