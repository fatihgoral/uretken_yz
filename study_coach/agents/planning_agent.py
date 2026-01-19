import json
from datetime import datetime, timedelta
from llm.gemini_client import GeminiClient
import os
from pathlib import Path


def extract_json(text: str) -> dict:
    """
    LLM çıktısından JSON bloğunu güvenli şekilde ayıklar
    """
    if not text:
        raise ValueError("LLM boş çıktı döndürdü")

    text = text.strip()
    
    # Markdown kod bloklarını temizle
    if "```" in text:
        # json dillerini de temizle (```json ... ```)
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("{") or part.startswith("json\n{"):
                text = part.replace("json\n", "", 1) if part.startswith("json\n") else part
                break

    start = text.find("{")
    end = text.rfind("}") + 1

    if start == -1 or end == -1:
        raise ValueError("JSON bloğu bulunamadı")

    json_text = text[start:end]
    
    # ⚠️ "Invalid \escape" hatalarını önlemek için ham backslash'leri temizle/düzelt
    # JSON içinde \ karakteri sadece kaçış karakteri olarak ( \", \\, \n vb.) geçerlidir.
    # LLM bazen tek başına \ yazarsa patlar.
    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        # Basit bir düzeltme denemesi: Tek başına duran backslash'leri çiftle
        import re
        # Arkasında geçerli bir json kaçış karakteri olmayan \ leri \\ yap
        fixed_text = re.sub(r'\\(?![\\"/bfnrtu])', r'\\\\', json_text)
        return json.loads(fixed_text)


def logical_round(val):
    """
    Değeri en yakın 0.5 katına yuvarlar. 
    0.25 -> 0.5, 0.75 -> 1.0 gibi.
    """
    rounded = int(float(val) * 2 + 0.5) / 2.0
    return max(0.5, rounded) # Minimum 30 dk



def generate_weekly_plan(course, exam_date, daily_hours, selected_days=None):
    """
    Planning Agent

    - Haftalık çalışma planını LLM ile üretir
    - selected_days: Seçilen günlerin listesi (örn: ["Monday", "Tuesday", "Wednesday"])
    - LLM hata verirse (kota, API, JSON bozukluğu)
      sistem çökmeden basit bir fallback plan üretir
    """

    client = GeminiClient()
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    exam_dt = datetime.strptime(exam_date, "%Y-%m-%d")
    days_to_exam = (exam_dt - today).days
    
    # ============================================
    # 🛡️ AKILLI TARİH DOĞRULAMASI
    # ============================================
    
    # 1. Sınav tarihi geçmişte mi?
    if days_to_exam < 0:
        return False, "⏰ Sınav tarihi geçmişte! Lütfen gelecekte bir tarih seçin."
    
    # 2. Sınav bugün mü?
    if days_to_exam == 0:
        return False, "📚 Sınav bugün! Artık çalışma planı oluşturmak için çok geç. Sınava odaklanın ve başarılar!"
    
    # Seçilen günler belirtilmemişse tüm günleri dahil et
    if selected_days is None:
        selected_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # 3. Seçilen günler sınav öncesi dönemde var mı kontrol et
    day_to_weekday = {
        "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
        "Friday": 4, "Saturday": 5, "Sunday": 6
    }
    allowed_weekdays = [day_to_weekday[d] for d in selected_days if d in day_to_weekday]
    
    # Bugünden sınav gününe kadar olan günleri kontrol et
    available_study_days = []
    for i in range(days_to_exam):
        check_date = today + timedelta(days=i)
        if check_date.weekday() in allowed_weekdays:
            available_study_days.append(check_date)
    
    if not available_study_days:
        # Seçilen günler hiçbiri sınav öncesine denk gelmiyor
        day_names_tr = {
            "Monday": "Pazartesi", "Tuesday": "Salı", "Wednesday": "Çarşamba",
            "Thursday": "Perşembe", "Friday": "Cuma", "Saturday": "Cumartesi", "Sunday": "Pazar"
        }
        selected_tr = [day_names_tr.get(d, d) for d in selected_days]
        return False, f"📅 Seçtiğiniz günler ({', '.join(selected_tr)}) sınav tarihine ({exam_date}) kadar olan sürede bulunmuyor. Lütfen farklı günler seçin veya sınav tarihini güncelleyin."
    
    # En az 1 gün, max 30 gün gibi bir sınır koyabiliriz
    plan_duration = max(1, days_to_exam)
    
    # Seçilen günleri prompt için hazırla
    selected_days_str = ", ".join(selected_days)

    prompt = f"""
Create a detailed study plan for "{course}".
Duration: {plan_duration} days (from {today.strftime("%Y-%m-%d")} to {exam_dt.strftime("%Y-%m-%d")}).
Max daily study: {daily_hours}h.

CRITICAL - COURSE NAME VALIDATION:
First, analyze if "{course}" is a valid course name input:
- If it contains minor typos (like "javaa" or "matemtik"), correct it to the proper name.
- If it is COMPLETELY RANDOM GIBBERISH (like "hfausdjf", "asdfgh", "xyzabc", random letters), 
  you MUST set course to "INVALID_COURSE" - do NOT make up a random course name!
- Only correct to a real course if the input is CLOSE to a real course name.

Examples:
- "javaa" -> "Java Programlama" (minor typo, correct it)
- "matemtik" -> "Matematik" (minor typo, correct it)  
- "hfausdjf" -> "INVALID_COURSE" (complete gibberish, reject)
- "asdfghjk" -> "INVALID_COURSE" (random letters, reject)
- "xxxxxxx" -> "INVALID_COURSE" (repeated letters with no meaning, reject)

IMPORTANT - SELECTED STUDY DAYS:
Only create schedule entries for these days of the week: {selected_days_str}
Skip all other days completely. Do NOT include any dates that fall on unselected days.

Rules:
1. Spread tasks across the entire {plan_duration} days, but ONLY on the selected days ({selected_days_str}).
2. Lower intensity (30-50% of {daily_hours}h) if {plan_duration} > 14 days.
3. Higher intensity if exam is within 7 days.
4. Each block "topic" must be specific.
5. IMPORTANT: All topics and descriptions MUST be in TURKISH (TÜRKÇE).
6. IMPORTANT: DO NOT USE BACKSLASHES (\\) OR ILLEGAL ESCAPE CHARACTERS.

Return ONLY JSON:
{{
  "course": "Corrected Course Name OR INVALID_COURSE if gibberish",
  "exam_date": "{exam_date}",
  "daily_hours": {daily_hours},
  "selected_days": {json.dumps(selected_days)},
  "schedule": [
    {{
      "date": "YYYY-MM-DD",
      "blocks": [
        {{ "topic": "Detaylı Çalışma Konusu", "hours": number }}
      ]
    }}
  ]
}}
"""


    plan = {
        "course": course,
        "exam_date": exam_date,
        "daily_hours": daily_hours,
        "schedule": [],
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        # ===== 1) LLM YOLU =====
        text = client.generate(prompt)
        plan = extract_json(text)
        
        # Ders adı doğrulaması - LLM tanıyamadıysa uyar
        corrected_course = plan.get("course", course)
        
        # LLM INVALID_COURSE döndürdüyse reddet
        if "INVALID_COURSE" in corrected_course.upper() or "INVALID" in corrected_course.upper():
            return False, "Geçersiz ders adı. Lütfen geçerli bir ders adı giriniz. (Örn: C Programlama, Matematik, Fizik)"
        
        # Eğer LLM ders adını "Bilinmeyen", "Unknown", "?" gibi bıraktıysa
        invalid_markers = ["bilinmeyen", "unknown", "belirsiz", "?", "geçersiz", "tanımsız"]
        if any(marker in corrected_course.lower() for marker in invalid_markers):
            return False, "Geçersiz ders adı. Lütfen geçerli bir ders adı giriniz. (Örn: C Programlama, Matematik, Fizik)"
        
        # Saatleri yuvarla
        plan["daily_hours"] = logical_round(plan.get("daily_hours", daily_hours))
        for day in plan.get("schedule", []):
            for block in day.get("blocks", []):
                block["hours"] = logical_round(block.get("hours", 0))
                
        plan["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        plan["original_input"] = course  # Orijinal girdiyi de sakla

    except Exception as e:
        # ===== 2) FALLBACK (SADE, KARAR ÜRETMEZ) =====
        print(f"⚠️ Planning Agent Hatası: {e}")
        
        # Fallback'te de girdi kontrolü yap
        import re
        is_gibberish = bool(re.match(r'^(.)\1{2,}$', course.strip())) or len(set(course.lower().replace(" ", ""))) < 2
        if is_gibberish:
            return False, "Geçersiz ders adı. Lütfen geçerli bir ders adı giriniz. (Örn: C Programlama, Matematik, Fizik)"
        
        schedule = []
        
        # Gün isimlerini Python weekday numaralarına eşle (0=Pazartesi, 6=Pazar)
        day_to_weekday = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
            "Friday": 4, "Saturday": 5, "Sunday": 6
        }
        allowed_weekdays = [day_to_weekday[d] for d in selected_days if d in day_to_weekday]
        
        for i in range(plan_duration):
            day = today + timedelta(days=i)
            # Sadece seçilen günleri ekle
            if day.weekday() in allowed_weekdays:
                schedule.append({
                    "date": day.strftime("%Y-%m-%d"),
                    "blocks": [
                        {
                            "topic": f"{course} genel çalışma",
                            "hours": daily_hours * 0.5
                        }
                    ]
                })

        plan["schedule"] = schedule
        plan["selected_days"] = selected_days
        corrected_course = course  # Fallback'te düzeltme yok

    # Klasörleme Mantığı: LLM'den gelen düzeltilmiş ismi kullan
    final_course_name = plan.get("course", course)
    safe_course_name = final_course_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    folder_path = Path("plans") / safe_course_name
    folder_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = folder_path / f"plan_{timestamp}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    
    # Geriye dönük uyumluluk için (en son planı tutar)
    with open("plan.json", "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    
    return True, f"Plan başarıyla oluşturuldu: {final_course_name}"


def rename_course(old_name: str, new_name: str):
    """
    Bir dersin klasör adını ve içindeki tüm planların 'course' alanını günceller.
    """
    safe_old = old_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    safe_new = new_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    
    old_folder = Path("plans") / safe_old
    new_folder = Path("plans") / safe_new
    
    if not old_folder.exists():
        return False, "Eski ders klasörü bulunamadı."
    
    if new_folder.exists() and safe_old != safe_new:
        return False, "Yeni isimle zaten bir ders mevcut."

    # Dosyaları güncelle
    for plan_file in old_folder.glob("*.json"):
        with open(plan_file, "r", encoding="utf-8") as f:
            plan = json.load(f)
        plan["course"] = new_name
        with open(plan_file, "w", encoding="utf-8") as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)

    # Klasörü yeniden adlandır
    if safe_old != safe_new:
        old_folder.rename(new_folder)
        
    # Ana plan.json daki ders adı buysa onu da güncelle
    if os.path.exists("plan.json"):
        with open("plan.json", "r", encoding="utf-8") as f:
            main_plan = json.load(f)
        if main_plan.get("course") == old_name:
            main_plan["course"] = new_name
            with open("plan.json", "w", encoding="utf-8") as f:
                json.dump(main_plan, f, ensure_ascii=False, indent=2)
                
    return True, "Başarıyla yeniden adlandırıldı."


def rename_plan_file(course_name: str, old_filename: str, new_display_name: str):
    """
    Belirli bir dersin belirli bir plan dosyasını yeniden adlandırır.
    """
    safe_course = course_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    folder = Path("plans") / safe_course
    
    old_path = folder / old_filename
    
    # Yeni isim .json ile bitmiyorsa ekle
    if not new_display_name.endswith(".json"):
        new_filename = new_display_name + ".json"
    else:
        new_filename = new_display_name
        
    new_path = folder / new_filename
    
    if not old_path.exists():
        return False, "Eski dosya bulunamadı."
    if new_path.exists() and old_filename != new_filename:
        return False, "Bu isimle zaten bir dosya mevcut."
        
    old_path.rename(new_path)
    return True, "Dosya başarıyla yeniden adlandırıldı."



def update_plan_intensity(multiplier: float, course_name: str = None, specific_path: Path = None):
    """
    Belirli bir plan dosyasını veya dersin en güncel dosyasını günceller.
    """
    target_plan_path = specific_path
    
    if not target_plan_path and course_name:
        safe_course_name = course_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        folder_path = Path("plans") / safe_course_name
        if folder_path.exists():
            files = sorted(folder_path.glob("*.json"))
            if files:
                target_plan_path = files[-1]
    
    if not target_plan_path and Path("plan.json").exists():
        target_plan_path = Path("plan.json")

    if target_plan_path and target_plan_path.exists():
        with open(target_plan_path, "r", encoding="utf-8") as f:
            plan = json.load(f)
        
        _apply_multiplier(plan, multiplier)
        
        with open(target_plan_path, "w", encoding="utf-8") as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
            
        # Eğer archive dosyasını güncellediysek, ana plan.json'u da (eğer o dertse) eşitleyelim
        if os.path.exists("plan.json"):
            with open("plan.json", "r", encoding="utf-8") as f:
                current_main = json.load(f)
            if current_main.get("course") == plan.get("course"):
                with open("plan.json", "w", encoding="utf-8") as f:
                    json.dump(plan, f, ensure_ascii=False, indent=2)

def _apply_multiplier(plan, multiplier):
    plan["daily_hours"] = logical_round(plan["daily_hours"] * multiplier)

    for day in plan.get("schedule", []):
        for block in day.get("blocks", []):
            block["hours"] = logical_round(block["hours"] * multiplier)
    
    plan["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    plan["last_multiplier"] = multiplier


def clear_day_from_plan(course_name: str, target_date: str):
    """
    Belirli bir tarihi plandaki schedule'dan kaldırır.
    
    Args:
        course_name: Dersin adı
        target_date: Kaldırılacak tarih (YYYY-MM-DD formatında)
    
    Returns:
        Tuple[bool, str]: (başarı durumu, mesaj)
    """
    safe_course_name = course_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    folder_path = Path("plans") / safe_course_name
    
    if not folder_path.exists():
        return False, "Ders klasörü bulunamadı."
    
    # En güncel plan dosyasını bul
    files = sorted(folder_path.glob("*.json"))
    if not files:
        return False, "Plan dosyası bulunamadı."
    
    target_plan_path = files[-1]
    
    try:
        with open(target_plan_path, "r", encoding="utf-8") as f:
            plan = json.load(f)
        
        original_count = len(plan.get("schedule", []))
        
        # Belirtilen tarihi schedule'dan kaldır
        plan["schedule"] = [
            day for day in plan.get("schedule", [])
            if day.get("date") != target_date
        ]
        
        new_count = len(plan["schedule"])
        
        if original_count == new_count:
            return False, f"'{target_date}' tarihi planda bulunamadı."
        
        plan["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        plan["cleared_dates"] = plan.get("cleared_dates", []) + [target_date]
        
        with open(target_plan_path, "w", encoding="utf-8") as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
        
        # Ana plan.json'u da güncelle (eğer aynı derse aitse)
        if os.path.exists("plan.json"):
            with open("plan.json", "r", encoding="utf-8") as f:
                main_plan = json.load(f)
            if main_plan.get("course") == plan.get("course"):
                with open("plan.json", "w", encoding="utf-8") as f:
                    json.dump(plan, f, ensure_ascii=False, indent=2)
        
        return True, f"'{target_date}' tarihi başarıyla plandan kaldırıldı."
    
    except Exception as e:
        return False, f"Hata oluştu: {str(e)}"


def clear_day_from_all_plans(target_date: str):
    """
    Belirli bir tarihi TÜM derslerin planlarından kaldırır.
    
    Args:
        target_date: Kaldırılacak tarih (YYYY-MM-DD formatında)
    
    Returns:
        Tuple[int, int, list]: (başarılı sayısı, başarısız sayısı, mesajlar listesi)
    """
    plans_dir = Path("plans")
    if not plans_dir.exists():
        return 0, 0, ["Plans klasörü bulunamadı."]
    
    success_count = 0
    fail_count = 0
    messages = []
    
    for course_folder in plans_dir.iterdir():
        if course_folder.is_dir():
            course_name = course_folder.name.replace("_", " ")
            success, msg = clear_day_from_plan(course_name, target_date)
            if success:
                success_count += 1
                messages.append(f"✅ {course_name}: {msg}")
            else:
                # "bulunamadı" mesajı varsa bu normal, sayma
                if "bulunamadı" not in msg.lower():
                    fail_count += 1
                messages.append(f"ℹ️ {course_name}: {msg}")
    
    return success_count, fail_count, messages
