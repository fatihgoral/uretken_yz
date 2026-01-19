import streamlit as st
import json
import os
import pandas as pd
from pathlib import Path
from streamlit_calendar import calendar

from agents.planning_agent import generate_weekly_plan, update_plan_intensity, rename_course, rename_plan_file, clear_day_from_plan, clear_day_from_all_plans
from agents.feedback_agent import collect_feedback
from agents.coordinator_agent import decide_plan_intensity
from agents.plan_critic_agent import critique_plan
from agents.motivation_agent import generate_motivation_message


# -------------------------------------------------
# SAYFA AYARI
# -------------------------------------------------
st.set_page_config(
    page_title="ArtemisAI",
    page_icon="🤖",
    layout="wide"
)

# -------------------------------------------------
# YENİ YIL TEMASI (SABİT KAR)
# -------------------------------------------------
st.markdown(r"""
<style>
/* ============================================
   🎨 MODERN SOFT UI THEME
   ============================================ */

/* Ana arka plan - Soft gradient */
.stApp {
    background: linear-gradient(135deg, #e0f7fa 0%, #e8f5e9 50%, #f1f8e9 100%) !important;
    background-attachment: fixed !important;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(224, 247, 250, 0.95) 0%, rgba(232, 245, 233, 0.95) 100%) !important;
    backdrop-filter: blur(10px) !important;
}

/* Ana içerik kutuları - Glassmorphism */
.stTabs [data-baseweb="tab-panel"] {
    background: rgba(255, 255, 255, 0.7) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 16px !important;
    padding: 20px !important;
    box-shadow: 0 8px 32px rgba(0, 77, 64, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.5) !important;
}

/* Tab butonları */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255, 255, 255, 0.6) !important;
    border-radius: 12px !important;
    padding: 8px !important;
    gap: 8px !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    padding: 12px 20px !important;
    font-weight: 500 !important;cd C:\Users\fatih\Desktop\ArtemisAI/PythonProject9\study_coachcd C:\Users\fatih\Desktop\ArtemisAI/PythonProject9\study_coach

    transition: all 0.3s ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(0, 150, 136, 0.1) !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #00897b 0%, #26a69a 100%) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(0, 137, 123, 0.3) !important;
}

/* Butonlar */
.stButton > button {
    background: linear-gradient(135deg, #00897b 0%, #26a69a 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 24px !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(0, 137, 123, 0.2) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(0, 137, 123, 0.35) !important;
}

/* Input alanları */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: rgba(255, 255, 255, 0.8) !important;
    border: 1px solid rgba(0, 150, 136, 0.2) !important;
    border-radius: 10px !important;
    transition: all 0.3s ease !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #26a69a !important;
    box-shadow: 0 0 0 3px rgba(38, 166, 154, 0.15) !important;
}

/* Slider */
.stSlider > div > div > div {
    background: linear-gradient(90deg, #00897b, #26a69a) !important;
}

/* Metrikler ve bilgi kutuları */
.stMetric {
    background: rgba(255, 255, 255, 0.7) !important;
    padding: 16px !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 15px rgba(0, 77, 64, 0.08) !important;
}

/* Uyarı ve bilgi kutuları */
.stAlert {
    border-radius: 12px !important;
    border: none !important;
}

/* Başlık stilleri */
h1, h2, h3 {
    color: #00695c !important;
    font-weight: 600 !important;
}

/* DataFrame/Tablo */
.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: 0 4px 15px rgba(0, 77, 64, 0.08) !important;
}

/* Toggle ve Checkbox */
.stCheckbox > label > span,
[data-testid="stToggle"] {
    color: #00695c !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: rgba(255, 255, 255, 0.7) !important;
    border-radius: 10px !important;
}

/* Kar efektleri (Yeni yıl teması) */
.snow-fixed {
    position: fixed;
    pointer-events: none;
    z-index: 9999;
    color: #b2dfdb;
    font-size: 1.5em;
    opacity: 0.5;
}
.snow-tl { top: 10px; left: 10px; }
.snow-tr { top: 10px; right: 10px; }
.snow-bl { bottom: 10px; left: 10px; }
.snow-br { bottom: 10px; right: 10px; }

/* Takvim event wrap ve stil ayarları */
/* Takvim event wrap ve stil ayarları */
.fc-event-title, .fc-sticky {
    white-space: normal !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
    font-size: 0.75em !important;
    font-weight: 500 !important;
    line-height: 1.2 !important;
    padding: 2px !important;
    display: block !important;
}

.fc-daygrid-event {
    margin-top: 2px !important;
    border-radius: 6px !important;
    white-space: normal !important;
    height: auto !important;
    max-height: none !important;
}

.fc-daygrid-block-event .fc-event-main {
    white-space: normal !important;
}

.fc-event-main-frame {
    height: auto !important;
}
.fc-daygrid-event-harness {
    margin-bottom: 2px !important;
}

/* Hediye kutusu animasyonu */
@keyframes shake {
    0% { transform: translate(1px, 1px) rotate(0deg); }
    10% { transform: translate(-1px, -2px) rotate(-1deg); }
    20% { transform: translate(-3px, 0px) rotate(1deg); }
    30% { transform: translate(3px, 2px) rotate(0deg); }
    40% { transform: translate(1px, -1px) rotate(1deg); }
    50% { transform: translate(-1px, 2px) rotate(-1deg); }
    60% { transform: translate(-3px, 1px) rotate(0deg); }
    70% { transform: translate(3px, 1px) rotate(-1deg); }
    80% { transform: translate(-1px, -1px) rotate(1deg); }
    90% { transform: translate(1px, 2px) rotate(0deg); }
    100% { transform: translate(1px, -2px) rotate(-1deg); }
}

@keyframes open-gift {
    0% { transform: scale(1); opacity: 1; }
    100% { transform: scale(3); opacity: 0; }
}

@keyframes reveal {
    0% { opacity: 0; transform: scale(0.5); }
    50% { opacity: 1; transform: scale(1); }
    100% { opacity: 0; transform: scale(1.1); }
}

.gift-container {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 10000;
    text-align: center;
}

.gift-box {
    font-size: 100px;
    animation: shake 0.3s infinite, open-gift 2s forwards;
    animation-delay: 0s, 0s;
}

.reveal-img {
    animation: reveal 1.5s forwards;
    animation-delay: 2s;
    border-radius: 20px;
    box-shadow: 0 0 50px rgba(0, 150, 136, 0.4);
}

/* Scrollbar stillemesi */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: rgba(0, 150, 136, 0.1);
    border-radius: 10px;
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #00897b, #26a69a);
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #00695c, #00897b);
}

</style>
<div class="snow-fixed snow-tl">✦</div>
<div class="snow-fixed snow-tr">✧</div>
<div class="snow-fixed snow-bl">✦</div>
<div class="snow-fixed snow-br">✧</div>
""", unsafe_allow_html=True)

st.title("ArtemisAI - Yapay Zeka Destekli Eğitim Koçu")
col_title, col_btn1, col_help = st.columns([3, 1, 1])

with col_title:
    st.caption("LLM tabanlı kişiselleştirilmiş çalışma planı sistemi")
with col_btn1:
    if st.button("❄️ Kar Yağdır"):
        st.snow()
with col_help:
    if st.button("❓ Nasıl Kullanılır"):
        st.session_state["show_help"] = not st.session_state.get("show_help", False)

if st.session_state.get("show_help"):
    st.markdown("""
    <div style="background: rgba(255,255,255,0.9); padding: 20px; border-radius: 12px; margin: 10px 0; border-left: 4px solid #26a69a;">
    <h4 style="color: #00695c; margin-top: 0;">📖 ArtemisAI Kullanım Kılavuzu</h4>
    
    <p><strong>1️⃣ Plan Oluştur</strong><br>
    Ders adı, sınav tarihi ve günlük çalışma saatini girin. Hangi günlerde çalışabileceğinizi seçin. Yapay zeka sizin için kişiselleştirilmiş bir plan oluşturacak.</p>
    
    <p><strong>2️⃣ Geri Bildirim</strong><br>
    Çalışma durumunuzu anlatın. Örneğin "Bugün çok yorgunum" veya "Salı günü çalışamayacağım" yazarsanız, sistem planınızı buna göre güncelleyebilir.</p>
    
    <p><strong>3️⃣ Plan Görüntüleme</strong><br>
    Oluşturduğunuz tüm planları görüntüleyin, düzenleyin veya silin.</p>
    
    <p><strong>4️⃣ Takvim</strong><br>
    Çalışma planınızı görsel takvim üzerinde inceleyin.</p>
    
    <p><strong>5️⃣ Agent Analizi</strong><br>
    Planınızın kalitesini değerlendirin ve iyileştirme önerileri alın.</p>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# YARDIMCI
# -------------------------------------------------
def load_plan(file_path="plan.json"):
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_all_courses():
    plans_dir = Path("plans")
    if not plans_dir.exists():
        return []
    courses = []
    for d in plans_dir.iterdir():
        if d.is_dir():
            # En son plan dosyasından gerçek ismi almayı dene
            latest_plan = sorted(d.glob("*.json"))
            if latest_plan:
                try:
                    with open(latest_plan[-1], "r", encoding="utf-8") as f:
                        data = json.load(f)
                        courses.append(data.get("course", d.name.replace("_", " ")))
                except:
                    courses.append(d.name.replace("_", " "))
            else:
                courses.append(d.name.replace("_", " "))
    return courses

def get_course_plans(course_display_name):
    safe_name = course_display_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    course_path = Path("plans") / safe_name
    if not course_path.exists():
        return []
    return sorted([f.name for f in course_path.glob("*.json")], reverse=True)

# -------------------------------------------------
# SEKME YAPISI
# -------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📅 Plan Oluştur",
    "🧠 Geri Bildirim",
    "📊 Plan Görüntüleme",
    "🗓️ Takvim",
    "📈 İstatistikler",
    "🧪 Agent Analizi"
])

# =================================================
# 1️⃣ PLAN OLUŞTUR
# =================================================
with tab1:
    st.subheader("📅 Haftalık Çalışma Planı Oluştur")

    course = st.text_input("Ders Adı", placeholder="Örn: C Programlama, Java, Algoritmalar")
    exam_date = st.date_input("Sınav Tarihi")
    daily_hours = st.slider("Günlük Maksimum Çalışma Saati", 1, 12, 4)

    # Gün seçimi toggle'ları
    st.markdown("### 📆 Çalışma Günlerini Seçin")
    st.caption("Hangi günlerde çalışmak istediğinizi seçin. Ana toggle'lar tüm günleri açar/kapatır.")
    
    # Gün isimleri ve İngilizce karşılıkları (planning agent için)
    day_mapping = {
        "Pazartesi": "Monday",
        "Salı": "Tuesday", 
        "Çarşamba": "Wednesday",
        "Perşembe": "Thursday",
        "Cuma": "Friday",
        "Cumartesi": "Saturday",
        "Pazar": "Sunday"
    }
    
    weekday_names = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
    weekend_names = ["Cumartesi", "Pazar"]
    
    # Session state başlangıç değerleri
    if "day_states_initialized" not in st.session_state:
        st.session_state["day_states_initialized"] = True
        # Haftaiçi günleri varsayılan açık
        for day in weekday_names:
            st.session_state[f"cb_{day}"] = True
        # Haftasonu günleri varsayılan kapalı
        for day in weekend_names:
            st.session_state[f"cb_{day}"] = False
    
    # Toggle callback fonksiyonları
    def toggle_weekdays():
        new_val = st.session_state["toggle_weekdays"]
        for day in weekday_names:
            st.session_state[f"cb_{day}"] = new_val
    
    def toggle_weekend():
        new_val = st.session_state["toggle_weekend"]
        for day in weekend_names:
            st.session_state[f"cb_{day}"] = new_val
    
    col_weekdays, col_weekend = st.columns(2)
    
    with col_weekdays:
        # Ana toggle - varsayılan tüm haftaiçi günleri açık mı kontrol et
        all_weekdays_on = all(st.session_state.get(f"cb_{d}", True) for d in weekday_names)
        st.toggle("🗓️ Haftaiçi", value=all_weekdays_on, key="toggle_weekdays", on_change=toggle_weekdays)
        
        for day in weekday_names:
            st.checkbox(day, key=f"cb_{day}")
    
    with col_weekend:
        # Ana toggle - varsayılan tüm haftasonu günleri açık mı kontrol et
        all_weekend_on = all(st.session_state.get(f"cb_{d}", False) for d in weekend_names)
        st.toggle("🌙 Haftasonu", value=all_weekend_on, key="toggle_weekend", on_change=toggle_weekend)
        
        for day in weekend_names:
            st.checkbox(day, key=f"cb_{day}")
    
    # Seçilen günleri birleştir (İngilizce olarak)
    all_selected_days = []
    for day in weekday_names + weekend_names:
        if st.session_state.get(f"cb_{day}", False):
            all_selected_days.append(day_mapping[day])
    
    # Seçili günleri Türkçe göster
    selected_days_tr = [d for d in weekday_names + weekend_names if st.session_state.get(f"cb_{d}", False)]
    
    # Seçili gün sayısını göster
    if all_selected_days:
        st.info(f"📌 Seçilen günler: {', '.join(selected_days_tr)} ({len(all_selected_days)} gün)")
    else:
        st.warning("⚠️ En az bir gün seçmelisiniz!")

    if st.button("📌 Planı Oluştur"):
        if not course.strip():
            st.warning("Lütfen ders adı giriniz.")
        elif not all_selected_days:
            st.warning("Lütfen en az bir çalışma günü seçin.")
        else:
            with st.spinner("🤖 Koçunuz haftalık çalışma planınızı hazırlıyor..."):
                success, message = generate_weekly_plan(
                    course,
                    exam_date.strftime("%Y-%m-%d"),
                    daily_hours,
                    selected_days=all_selected_days
                )
            if success:
                st.success(f"✅ {message}")
                st.balloons()
            else:
                st.error(f"❌ {message}")

# =================================================
# 2️⃣ GERİ BİLDİRİM  ✅ DÜZELTİLEN KISIM
# =================================================
with tab2:
    courses = get_all_courses()
    selected_courses = st.multiselect("🎯 Hangi dersler için geri bildirim veriyorsun?", courses if courses else ["Henüz bir plan yok"])

    feedback_text = st.text_area(
        "Bugünkü çalışma durumunu anlat",
        placeholder="Örn: Bugün odaklanmakta zorlandım, verim düşüktü."
    )

    if st.button("📨 Geri Bildirimi Gönder"):
        if not courses:
            st.error("Önce bir plan oluşturmalısın.")
        elif not selected_courses:
            st.warning("Lütfen en az bir ders seçin.")
        else:
            with st.spinner("🤖 Koç geri bildiriminizi analiz ediyor..."):
                result = collect_feedback(feedback_text)
            
            st.session_state["feedback_result"] = result
            st.session_state["target_courses"] = selected_courses

    if "feedback_result" in st.session_state:
        result = st.session_state["feedback_result"]
        target_courses = st.session_state["target_courses"]
        
        emotion = result.get("emotion", {})
        severity = result.get("severity", {})
        decision = result.get("decision", {})
        schedule_action = result.get("schedule_action", {})

        st.write("---")
        st.write("🎭 **Duygu Analizi:**", emotion)
        st.warning(f"⚠️ **Ciddiyet:** {severity.get('severity')} — {severity.get('reason')}")
        st.info(f"🧭 **Koordinatör Kararı:** {decision.get('decision')} (Çarpan: {decision.get('multiplier')})")
        st.caption(f"Gerekçe: {decision.get('reason')}")

        # Takvim Aksiyonu Gösterimi
        if schedule_action.get("action") == "clear_day" and schedule_action.get("target_date"):
            st.markdown("---")
            st.markdown("### 📅 Takvim Değişikliği Önerisi")
            day_name = schedule_action.get("day_name", "")
            target_date = schedule_action.get("target_date")
            st.warning(f"🗓️ **{day_name} ({target_date})** tarihini plandan kaldırmak ister misiniz?")
            st.caption(f"Gerekçe: {schedule_action.get('reason')}")
            
            col_clear_selected, col_clear_all, col_skip = st.columns(3)
            with col_clear_selected:
                if st.button("✅ Seçili Derslerden", key="clear_day_selected_btn"):
                    for course in target_courses:
                        success, msg = clear_day_from_plan(course, target_date)
                        if success:
                            st.success(f"✅ {course}: {msg}")
                        else:
                            st.warning(f"⚠️ {course}: {msg}")
                    del st.session_state["feedback_result"]
                    st.rerun()
            with col_clear_all:
                if st.button("🔄 TÜM Derslerden", key="clear_day_all_btn"):
                    success_count, fail_count, messages = clear_day_from_all_plans(target_date)
                    for msg in messages:
                        st.write(msg)
                    st.success(f"✅ {success_count} dersten bu tarih kaldırıldı.")
                    del st.session_state["feedback_result"]
                    st.rerun()
            with col_skip:
                if st.button("❌ İptal", key="skip_clear_btn"):
                    st.info("Takvim değişikliği atlandı.")
                    st.session_state["feedback_result"]["schedule_action"] = {"action": "none"}
                    st.rerun()

        if decision.get("multiplier") != 1.0:
            st.markdown(f"### 🤖 Plan Değişikliği Önerisi")
            st.write(f"Koordinatör, seçili dersler ({', '.join(target_courses)}) için yoğunluğu **%{int(decision.get('multiplier')*100)}** oranına çekmeyi öneriyor.")
            
            col_apply, col_keep = st.columns(2)
            with col_apply:
                if st.button("✅ Değişikliği Uygula"):
                    for course in target_courses:
                        update_plan_intensity(decision.get("multiplier", 1.0), course)
                    st.success("✅ Seçili tüm planlar güncellendi!")
                    del st.session_state["feedback_result"]
                    st.rerun()
            with col_keep:
                if st.button("❌ Mevcut Planı Koru"):
                    st.info("Değişiklik reddedildi, mevcut plan korundu.")
                    del st.session_state["feedback_result"]
                    st.rerun()
        else:
            # schedule_action yoksa veya zaten işlendiyse
            if schedule_action.get("action") != "clear_day":
                st.success("✅ Hafif geri bildirim. Plan değişikliğine gerek görülmedi. İyi çalışmalar!")
                if st.button("Tamam"):
                    del st.session_state["feedback_result"]
                    st.rerun()


# =================================================
# 3️⃣ PLAN GÖRÜNTÜLEME
# =================================================
with tab3:
    st.subheader("📅 Plan Arşivi")

    courses = get_all_courses()
    
    if not courses:
        st.info("Henüz hiçbir plan oluşturulmamış.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            selected_course = st.selectbox("📂 Ders Seçin", courses)
        
        if selected_course:
            course_plans = get_course_plans(selected_course)
            with col2:
                selected_file = st.selectbox(
                    "📄 Plan Versiyonu", 
                    course_plans,
                    format_func=lambda x: x.replace(".json", "")
                )
            
            if selected_file:
                safe_name = selected_course.replace(" ", "_").replace("/", "_").replace("\\", "_")
                plan_path = Path("plans") / safe_name / selected_file
                plan = load_plan(plan_path)
                
                if plan:
                    st.markdown("---")
                    col_info, col_del = st.columns([4, 1])
                    with col_info:
                        st.markdown(f"### 📘 {plan.get('course')} - Plan Detayı")
                        st.write(f"**🕒 Oluşturulma:** {plan.get('generated_at')}")
                        if plan.get("updated_at"):
                            st.write(f"**🔄 Son Güncelleme:** {plan.get('updated_at')} (Çarpan: {plan.get('last_multiplier', 'N/A')})")
                    
                    with col_del:
                        if st.button("🗑️ Planı Sil", key=f"del_{selected_file}"):
                            os.remove(plan_path)
                            # Eğer klasör boşsa sil
                            safe_name = selected_course.replace(" ", "_").replace("/", "_").replace("\\", "_")
                            course_dir = Path("plans") / safe_name
                            if course_dir.exists() and not any(course_dir.iterdir()):
                                course_dir.rmdir()
                            st.success("Plan silindi. Sayfa yenileniyor...")
                            st.rerun()

                    with st.expander("⚙️ Ders Ayarları"):
                        # Dersi yeniden adlandır
                        new_course_name = st.text_input("Dersi Yeniden Adlandır", value=selected_course)
                        if st.button("💾 Ders İsmini Güncelle"):
                            success, msg = rename_course(selected_course, new_course_name)
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                        
                        st.divider()
                        
                        # Plan dosyasını yeniden adlandır
                        current_file_display = selected_file.replace(".json", "")
                        new_file_name = st.text_input("Plan Versiyonunu Yeniden Adlandır", value=current_file_display)
                        if st.button("💾 Versiyon İsmini Güncelle"):
                            success, msg = rename_plan_file(selected_course, selected_file, new_file_name)
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                    st.write(f"**📅 Sınav Tarihi:** {plan.get('exam_date')} | **⏰ Günlük Saat:** {plan.get('daily_hours')}")

                    # İlerleme özeti
                    total_topics = sum(len(day.get("blocks", [])) for day in plan.get("schedule", []))
                    completed = sum(1 for day in plan.get("schedule", []) for block in day.get("blocks", []) if block.get("completed", False))
                    progress = (completed / total_topics * 100) if total_topics > 0 else 0
                    
                    st.markdown(f"### 🎯 İlerleme: {completed}/{total_topics} konu (%{progress:.0f})")
                    st.progress(progress / 100 if progress <= 100 else 1.0)

                    st.markdown("---")
                    st.caption("✅ Tamamladığınız konuları işaretleyin")
                    
                    # Tablo başlıkları
                    header_cols = st.columns([0.5, 2, 5, 1])
                    with header_cols[0]:
                        st.markdown("**✓**")
                    with header_cols[1]:
                        st.markdown("**Tarih**")
                    with header_cols[2]:
                        st.markdown("**Konu**")
                    with header_cols[3]:
                        st.markdown("**Saat**")
                    
                    st.markdown("---")
                    
                    # Saat formatı fonksiyonu
                    def format_hours(h):
                        try:
                            val = float(h)
                            return f"{int(val)}" if val.is_integer() else f"{val}"
                        except:
                            return str(h)

                    plan_updated = False
                    for day_idx, day in enumerate(plan.get("schedule", [])):
                        date_str = day.get("date")
                        
                        for block_idx, block in enumerate(day.get("blocks", [])):
                            topic = block.get("topic")
                            hours = block.get("hours")
                            is_completed = block.get("completed", False)
                            
                            row_cols = st.columns([0.5, 2, 5, 1])
                            with row_cols[0]:
                                new_status = st.checkbox(
                                    "",
                                    value=is_completed,
                                    key=f"pv_{selected_course}_{day_idx}_{block_idx}",
                                    label_visibility="collapsed"
                                )
                            with row_cols[1]:
                                st.write(date_str)
                            with row_cols[2]:
                                # Üstü çizili yazı kaldırıldı, sadece normal yazı
                                st.write(topic)
                            with row_cols[3]:
                                # Saat formatlama: Tam sayı ise .0 at
                                st.write(f"{format_hours(hours)}s")
                            
                            # Satır arası ayırıcı çizgi
                            st.markdown("<div style='height: 1px; background-color: rgba(0, 150, 136, 0.2); margin: 8px 0;'></div>", unsafe_allow_html=True)
                            
                            if new_status != is_completed:
                                plan["schedule"][day_idx]["blocks"][block_idx]["completed"] = new_status
                                plan_updated = True
                    
                    if plan_updated:
                        import json
                        with open(plan_path, "w", encoding="utf-8") as f:
                            json.dump(plan, f, ensure_ascii=False, indent=2)
                        st.rerun()


# =================================================
# 4️⃣ TAKVİM GÖRÜNÜMÜ
# =================================================
with tab4:
    st.subheader("🗓️ Çalışma Takvimi")
    
    courses = get_all_courses()
    if not courses:
        st.info("Henüz bir plan yok.")
    else:
        selected_courses = st.multiselect("📅 Takvimde görmek istediğiniz dersleri seçin", courses, key="cal_courses")
        
        if selected_courses:
            all_calendar_events = []
            
            # Dersler için renk paleti
            course_colors = ["#1E88E5", "#D81B60", "#43A047", "#FB8C00", "#8E24AA", "#00ACC1"]
            
            for idx, course_name in enumerate(selected_courses):
                safe_name = course_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
                folder_path = Path("plans") / safe_name
                
                if folder_path.exists():
                    files = sorted(folder_path.glob("*.json"))
                    if files:
                        plan_path = files[-1] # En güncel versiyonu al
                        plan_data = load_plan(plan_path)
                        
                        if plan_data:
                            color = course_colors[idx % len(course_colors)]
                            for day in plan_data.get("schedule", []):
                                date_str = day.get("date")
                                for block in day.get("blocks", []):
                                    all_calendar_events.append({
                                        "title": f"⏰ {block.get('hours')}s | {block.get('topic')}",
                                        "start": date_str,
                                        "end": date_str,
                                        "allDay": True,
                                        "backgroundColor": color,
                                        "borderColor": color,
                                        "extendedProps": {"course": course_name}
                                    })
            
            if not all_calendar_events:
                st.warning("Seçili dersler için plan verisi bulunamadı.")
            else:
                calendar_options = {
                    "headerToolbar": {
                        "left": "prev,next today",
                        "center": "title",
                        "right": "dayGridMonth,dayGridWeek"
                    },
                    "initialView": "dayGridMonth",
                    "selectable": True,
                    "themeSystem": "standard",
                    "height": "auto",
                    "fixedWeekCount": False,
                    "eventDisplay": "block",
                }
                
                # Seçilen derslerin isimlerinden bir key üretelim ki seçim değişince takvim yenilensin
                cal_key = "_".join([c[:3] for c in selected_courses])
                calendar(events=all_calendar_events, options=calendar_options, key=f"calendar_{cal_key}")

                # RENK LEGENDI (TAKIM ANAHTARI)
                st.markdown("---")
                st.markdown("### 🎨 Ders Renk Anahtarı")
                legend_cols = st.columns(len(selected_courses))
                for i, course in enumerate(selected_courses):
                    color = course_colors[i % len(course_colors)]
                    with legend_cols[i]:
                        st.markdown(f"""
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <div style="width: 20px; height: 20px; background-color: {color}; border-radius: 4px;"></div>
                                <span>{course}</span>
                            </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("Lütfen takvimde görüntülemek için en az bir ders seçin.")

# =================================================
# 5️⃣ İSTATİSTİKLER VE HEDEF TAKİBİ
# =================================================
with tab5:
    st.subheader("📈 İstatistikler ve İlerleme Takibi")
    
    courses = get_all_courses()
    
    if not courses:
        st.info("Henüz bir plan oluşturulmamış. İstatistikleri görmek için önce bir plan oluşturun.")
    else:
        # Tüm planlardan istatistik topla
        total_hours = 0
        total_topics = 0
        completed_topics = 0
        daily_stats = {}  # {tarih: {planlanan: X, tamamlanan: Y}}
        
        for course_name in courses:
            safe_name = course_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
            folder_path = Path("plans") / safe_name
            
            if folder_path.exists():
                files = sorted(folder_path.glob("*.json"))
                if files:
                    plan_path = files[-1]
                    plan_data = load_plan(plan_path)
                    
                    if plan_data:
                        for day in plan_data.get("schedule", []):
                            date_str = day.get("date")
                            if date_str not in daily_stats:
                                daily_stats[date_str] = {"planlanan": 0, "tamamlanan": 0}
                            
                            for block in day.get("blocks", []):
                                hours = block.get("hours", 0)
                                total_hours += hours
                                total_topics += 1
                                daily_stats[date_str]["planlanan"] += hours
                                
                                # Tamamlandı olarak işaretlenmişse
                                if block.get("completed", False):
                                    completed_topics += 1
                                    daily_stats[date_str]["tamamlanan"] += hours
        
        # Özet Metrikler
        st.markdown("### 📊 Genel Özet")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📚 Toplam Ders", len(courses))
        with col2:
            total_hours_disp = f"{int(total_hours)}" if total_hours.is_integer() else f"{total_hours:.1f}"
            st.metric("⏱️ Toplam Saat", total_hours_disp)
        with col3:
            st.metric("📝 Toplam Konu", total_topics)
        with col4:
            completion_rate = (completed_topics / total_topics * 100) if total_topics > 0 else 0
            st.metric("✅ Tamamlanan", f"%{completion_rate:.0f}")
        
        # İlerleme Çubuğu
        st.markdown("### 🎯 Genel İlerleme")
        st.progress(completion_rate / 100 if completion_rate <= 100 else 1.0)
        
        # Haftalık Grafik
        if daily_stats:
            st.markdown("### 📈 Günlük Çalışma Grafiği")
            
            import plotly.graph_objects as go
            
            # Tarihleri sırala
            sorted_dates = sorted(daily_stats.keys())[-14:]  # Son 14 gün
            
            planlanan_values = [daily_stats[d]["planlanan"] for d in sorted_dates]
            tamamlanan_values = [daily_stats[d]["tamamlanan"] for d in sorted_dates]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Planlanan',
                x=sorted_dates,
                y=planlanan_values,
                marker_color='#26a69a'
            ))
            fig.add_trace(go.Bar(
                name='Tamamlanan',
                x=sorted_dates,
                y=tamamlanan_values,
                marker_color='#00695c'
            ))
            
            fig.update_layout(
                barmode='group',
                title='Günlük Planlanan vs Tamamlanan Saatler',
                xaxis_title='Tarih',
                yaxis_title='Saat',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)

# =================================================
# 6️⃣ AGENT ANALİZİ
# =================================================
with tab6:
    st.subheader("🧪 Agent Analizi")

    courses = get_all_courses()
    selected_course = st.selectbox("🎯 Analiz edilecek dersi seçin", courses, key="analiz_course")
    
    selected_file = None
    if selected_course:
        course_plans = get_course_plans(selected_course)
        selected_file = st.selectbox("📄 Analiz edilecek versiyon", course_plans, key="analiz_file", format_func=lambda x: x.replace(".json", ""))

    safe_name = selected_course.replace(" ", "_").replace("/", "_").replace("\\", "_") if selected_course else ""
    target_path = Path("plans") / safe_name / selected_file if selected_file else None

    if st.button("🧭 Plan Yoğunluğunu Değerlendir"):
        with st.spinner("🤖 Plan yoğunluğu değerlendiriliyor..."):
            # Değerlendirme için şimdilik global mantık çalışıyor ama veriyi buradan alabiliriz
            decision = decide_plan_intensity()
        st.info(f"**Karar:** {decision['decision']} | **Çarpan:** {decision['multiplier']}")
        st.caption(decision["reason"])

    if st.button("🧪 Planı Eleştir"):
        if not target_path:
            st.warning("Lütfen önce bir plan seçin.")
        else:
            with st.spinner("🤖 Eleştirmen planınızı inceliyor..."):
                critique = critique_plan(target_path)
                st.session_state["last_critique"] = critique
                st.session_state["critiqued_file"] = str(target_path)

    if "last_critique" in st.session_state:
        critique = st.session_state["last_critique"]
        critiqued_file = st.session_state.get("critiqued_file")

        if critique.get("status") == "no_plan":
            st.warning(critique["comment"])
        elif critique.get("status") == "invalid_plan" or critique.get("status") == "parse_error":
            st.error(critique.get("comment", "Bir hata oluştu."))
        else:
            st.metric("Genel Kalite", critique["overall_quality"])
            st.write("⚖️ **Yük Dengesi:**", critique["load_balance"])
            st.write("✅ **Güçlü Yönler:**", f" {', '.join(critique['strengths'])}")
            st.write("❌ **Zayıf Yönler:**", f" {', '.join(critique['weaknesses'])}")
            st.info("💡 **Öneri:** " + critique["suggestion"])

            improvement = critique.get("proposed_improvement")
            if improvement and improvement.get("action") == "multiplier":
                st.markdown("---")
                st.markdown("### ✨ Önerilen İyileştirme")
                st.write(f"**Gerekçe:** {improvement['reason_for_action']}")
                st.write(f"**Öneri:** Yoğunluğu **%{int(improvement['value']*100)}** oranına güncellemek.")
                
                if st.button("🚀 Bu İyileştirmeyi Uygula"):
                    # İyileştirmeyi seçili dosyaya uygula
                    update_plan_intensity(improvement["value"], specific_path=Path(critiqued_file))
                    st.success(f"✅ İyileştirme '{Path(critiqued_file).name}' için uygulandı! Plan güncellendi.")
                    del st.session_state["last_critique"]
                    st.rerun()

    st.markdown("---")
    if st.button("✨ Günlük Motivasyon Al"):
        with st.spinner("🤖 Koçunuz sizin için bir mesaj hazırlıyor..."):
            msg = generate_motivation_message("analiz edildi")
            st.session_state["mo_msg"] = msg
    
    if "mo_msg" in st.session_state:
        st.success(st.session_state["mo_msg"])


# -------------------------------------------------
# ALT BİLGİ
# -------------------------------------------------
st.markdown("---")
st.caption("🚀 Bir Fatih Göral ve Kerem Özcan Projesidir. Tüm Hakları Saklıdır.")
st.caption("Bu arayüz yalnızca girdi/çıktı katmanıdır. Tüm kararlar agent’lar tarafından verilir.")
