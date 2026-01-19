import json
from pathlib import Path
from llm.gemini_client import GeminiClient

DATA_FILE = Path("progress.json")
client = GeminiClient()


def _safe_json_parse(text: str) -> dict:
    """
    LLM çıktısından JSON bloğunu güvenli şekilde ayıklar
    (SADECE parse fallback)
    """
    if not text:
        raise ValueError("Boş LLM çıktısı")

    cleaned = text.replace("```json", "").replace("```", "").strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("JSON bulunamadı")

    return json.loads(cleaned[start:end + 1])


def decide_plan_intensity() -> dict:
    """
    Coordinator Agent
    - Kararı SADECE LLM verir
    - LLM çalışmazsa sistem çökmez
    - Karar üretmez, sadece bilgilendirir
    """

    if not DATA_FILE.exists():
        return {
            "decision": "no_data",
            "multiplier": 1.0,
            "reason": "Henüz geri bildirim verisi yok."
        }

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    feedbacks = [d for d in data if d.get("type") == "feedback"]
    if not feedbacks:
        return {
            "decision": "no_feedback",
            "multiplier": 1.0,
            "reason": "Henüz geri bildirim yok."
        }

    last_feedback = feedbacks[-1]

    prompt = f"""
Sen oldukça rasyonel, sonuç odaklı ve gerektiğinde "ACIMASIZ" bir ÇALIŞMA KOORDİNATÖRÜ etmensin. 
Öğrencinin iyiliği için planı radikal şekilde değiştirmekten çekinmezsin.

Aşağıdaki geri bildirime göre çalışma planının yoğunluğunu değerlendir. 

Kurallar:
- Eğer öğrenci çok zorlanıyorsa veya verimliliği çok düşükse multiplier değerini sert bir şekilde düşür (örn: 0.4 - 0.6).
- Eğer öğrenci çok rahatsa ve daha fazlasını yapabilecekse multiplier değerini artır (örn: 1.3 - 1.6).
- Sadece saatleri değil, öğrencinin mental durumunu da gözet ama plana sadık kalması için en optimize kararı ver.

SADECE JSON DÖNDÜR:

{{
  "decision": "increase | decrease | keep",
  "multiplier": 0.3 ile 2.0 arasında bir sayı,
  "reason": "kısa ve öz otoriter gerekçe"
}}

GERİ BİLDİRİM:
{json.dumps(last_feedback, ensure_ascii=False)}
"""

    try:
        raw = client.generate(prompt)
        return _safe_json_parse(raw)

    except Exception:
        # 🔒 LLM yok → sistem çökmez ama karar da üretmez
        return {
            "decision": "unknown",
            "multiplier": 1.0,
            "reason": "LLM erişilemediği için koordinatör kararı üretilemedi."
        }
