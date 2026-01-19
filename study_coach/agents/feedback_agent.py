import json
from pathlib import Path
from datetime import datetime

from llm.gemini_client import GeminiClient

DATA_FILE = Path("progress.json")
llm_client = GeminiClient()

def process_feedback_unified(text: str) -> dict:
    """
    Duygu, Ciddiyet, Koordinatör kararını ve Takvim Aksiyonunu TEK BİR LLM çağrısında birleştirir.
    Quota tasarrufu sağlar.
    """
    # Bugünün tarihini al (LLM'in tarih hesaplaması için)
    from datetime import datetime, timedelta
    today = datetime.now()
    
    # Hafta günlerini hesapla
    week_dates = {}
    day_names_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    for i in range(7):
        future_date = today + timedelta(days=i)
        day_name = day_names_tr[future_date.weekday()]
        week_dates[day_name] = future_date.strftime("%Y-%m-%d")
    
    week_info = ", ".join([f"{k}: {v}" for k, v in week_dates.items()])
    
    prompt = f"""
Analyze feedback: "{text}"
Roles: AI Coach & Coordinator.
Today's date: {today.strftime("%Y-%m-%d")}
This week's dates: {week_info}

IMPORTANT: All 'reason' fields MUST be in TURKISH (TÜRKÇE).

If the user mentions they CANNOT study on a specific day (e.g., "Salı çalışamayacağım", "bu hafta Cuma boş geç"), 
extract that information in schedule_action.

Output ONLY JSON:
{{
  "emotion": {{ "emotion": "pos|neg|neu", "polarity": float }},
  "severity": {{ "severity": "low|med|high", "reason": "str" }},
  "decision": {{ "decision": "inc|dec|keep", "multiplier": float, "reason": "str" }},
  "schedule_action": {{
    "action": "clear_day|reschedule|none",
    "target_date": "YYYY-MM-DD or null",
    "day_name": "Gün adı or null",
    "reason": "str"
  }}
}}

If no schedule action is needed, set action to "none" and target_date to null.
"""
    try:
        raw = llm_client.generate(prompt)
        cleaned = raw.replace("```json", "").replace("```", "").strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        result = json.loads(cleaned[start:end + 1])
        
        # schedule_action yoksa varsayılan ekle
        if "schedule_action" not in result:
            result["schedule_action"] = {"action": "none", "target_date": None, "day_name": None, "reason": "Takvim değişikliği gerekmiyor."}
        
        return result
    except Exception as e:
        print(f"Unified Feedback Error: {e}")
        return {
            "emotion": {"emotion": "neutral", "polarity": 0.0},
            "severity": {"severity": "low", "reason": "Analiz hatası oluştu."},
            "decision": {"decision": "keep", "multiplier": 1.0, "reason": "Hata nedeniyle plan korundu."},
            "schedule_action": {"action": "none", "target_date": None, "day_name": None, "reason": "Analiz hatası."}
        }

def collect_feedback(text: str) -> dict:
    """
    Geri bildirim alır, birleşik analiz yapar ve kaydeder.
    """
    if not text or not text.strip():
        return {
            "emotion": {"emotion": "neutral", "polarity": 0.0},
            "severity": {"severity": "low", "reason": "Boş girdi"},
            "decision": {"decision": "keep", "multiplier": 1.0, "reason": "Boş girdi"}
        }

    # TEK ÇAĞRI
    result = process_feedback_unified(text)

    record = {
        "type": "feedback",
        "text": text,
        "emotion": result["emotion"],
        "severity": result["severity"],
        "decision": result["decision"],
        "timestamp": datetime.now().isoformat()
    }

    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.append(record)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    return result

