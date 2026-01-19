import os
import json
from datetime import datetime

from agents.motivation_agent import generate_motivation_message
from agents.planning_agent import generate_weekly_plan, update_plan_intensity
from agents.feedback_agent import collect_feedback
from agents.coordinator_agent import decide_plan_intensity
from agents.plan_critic_agent import critique_plan


# -------------------------------------------------
# EKRAN TEMİZLEME (PYCHARM İÇİN DEVRE DIŞI)
# -------------------------------------------------
def clear_screen():
    pass


# -------------------------------------------------
# MENÜ
# -------------------------------------------------
def print_menu():
    print("===================================")
    print(" 🤖 AI STUDY COACH")
    print("===================================")
    print("1️⃣ Motivasyon Mesajı")
    print("2️⃣ Haftalık Çalışma Planı Oluştur")
    print("3️⃣ Günlük Geri Bildirim (Serbest Metin)")
    print("4️⃣ Koordinatör Kararı (Plan Yoğunluğu)")
    print("5️⃣ Kaydedilen Planı Görüntüle")
    print("6️⃣ Plan Eleştirisi (Agent)")
    print("q️⃣ Çıkış")
    print("===================================")


# -------------------------------------------------
# PLAN GÖSTERME
# -------------------------------------------------
def plani_goster():
    try:
        with open("plan.json", "r", encoding="utf-8") as f:
            plan = json.load(f)
    except FileNotFoundError:
        print("❌ Henüz kaydedilmiş bir plan yok.")
        return

    print("\n📅 KAYITLI HAFTALIK ÇALIŞMA PLANI")
    print("=" * 45)
    print(f"📘 Ders        : {plan.get('course')}")
    print(f"📅 Sınav Tarihi: {plan.get('exam_date')}")
    print(f"⏰ Günlük Saat : {plan.get('daily_hours')}")
    print(f"🕒 Oluşturma   : {plan.get('generated_at')}")

    print("\n📆 Günlük Program")
    print("-" * 45)

    for gun in plan.get("schedule", []):
        print(f"\n🔹 {gun['date']}")
        for block in gun.get("blocks", []):
            print(f"   🕒 {block['hours']} saat → {block['topic']}")

    print("\n" + "=" * 45)


# -------------------------------------------------
# ANA PROGRAM
# -------------------------------------------------
def main():
    print("📌 Planlar JSON dosyasında kalıcı olarak saklanır.\n")

    while True:
        clear_screen()
        print_menu()

        choice = input("Seçimin (1 / 2 / 3 / 4 / 5 / 6 / q): ").strip().lower()

        if choice == "":
            continue

        # 1️⃣ MOTİVASYON MESAJI
        if choice == "1":
            level = input("Bugünkü çalışma durumunu yaz (low / medium / high): ").strip().lower()
            message = generate_motivation_message(level)

            print("\n🎯 Study Coach Mesajı:")
            print(message)
            input("\nDevam etmek için ENTER'a bas...")

        # 2️⃣ PLAN OLUŞTUR
        elif choice == "2":
            course = input("Ders adı: ").strip()
            exam_date = input("Sınav tarihi (YYYY-MM-DD): ").strip()

            try:
                datetime.strptime(exam_date, "%Y-%m-%d")
            except ValueError:
                print("❌ Tarih formatı hatalı. YYYY-MM-DD olmalı.")
                input("\nDevam etmek için ENTER'a bas...")
                continue

            try:
                daily_hours = int(input("Günlük kaç saat çalışabilirsin?: ").strip())
            except ValueError:
                print("❌ Günlük saat sayısı sayı olmalıdır.")
                input("\nDevam etmek için ENTER'a bas...")
                continue

            if daily_hours <= 0 or daily_hours > 24:
                print("❌ Günlük çalışma saati 1–24 arasında olmalıdır.")
                input("\nDevam etmek için ENTER'a bas...")
                continue

            generate_weekly_plan(course, exam_date, daily_hours)
            print("✅ Plan başarıyla oluşturuldu ve kaydedildi (plan.json)")
            input("\nDevam etmek için ENTER'a bas...")

        # 3️⃣ GERİ BİLDİRİM → SEVERITY + AGENTIC KARAR
        elif choice == "3":
            feedback = input("Bugünkü geri bildirimin: ").strip()

            if len(feedback) < 3:
                print("❌ Geri bildirim çok kısa.")
                input("\nDevam etmek için ENTER'a bas...")
                continue

            result = collect_feedback(feedback)

            emotion = result["emotion"]
            severity = result["severity"]
            decision = result["decision"]

            print("\n🧠 Duygu Analizi Sonucu:")
            print(f"Duygu : {emotion['emotion']}")
            print(f"Skor  : {emotion['polarity']}")

            print("\n🚨 Geri Bildirim Önemi:")
            print(f"Seviye : {severity['severity']}")
            print(f"Gerekçe: {severity['reason']}")

            if os.path.exists("plan.json"):
                print("\n🧭 Koordinatör (Agentic) Kararı:")
                print(f"Karar             : {decision['decision']}")
                print(f"Yoğunluk Katsayısı: {decision['multiplier']}")
                print(f"Gerekçe           : {decision['reason']}")

                if severity["severity"] == "high":
                    update_plan_intensity(decision.get("multiplier", 1.0))
                    print("⚠️ Ciddi geri bildirim → plan güncellendi.")
                elif severity["severity"] == "medium":
                    print("ℹ️ Orta seviye geri bildirim → plan korundu.")
                else:
                    print("✅ Hafif geri bildirim → sadece motivasyon yeterli.")


            input("\nDevam etmek için ENTER'a bas...")

        # 4️⃣ MANUEL KOORDİNATÖR
        elif choice == "4":
            if not os.path.exists("plan.json"):
                print("❌ Önce bir çalışma planı oluşturmalısın.")
                input("\nDevam etmek için ENTER'a bas...")
                continue

            decision = decide_plan_intensity()

            print("\n🧭 Koordinatör (Agentic) Kararı:")
            print(f"Karar             : {decision['decision']}")
            print(f"Yoğunluk Katsayısı: {decision['multiplier']}")
            print(f"Gerekçe           : {decision['reason']}")

            update_plan_intensity(decision["multiplier"])
            print("✅ Plan güncellendi.")
            input("\nDevam etmek için ENTER'a bas...")

        # 5️⃣ PLAN GÖRÜNTÜLE
        elif choice == "5":
            plani_goster()
            input("\nDevam etmek için ENTER'a bas...")

        # 6️⃣ PLAN ELEŞTİRİSİ
        elif choice == "6":
            result = critique_plan()

            print("\n📊 Plan Eleştirisi (Agentic):")
            print(f"Genel Kalite : {result.get('overall_quality')}/100")
            print(f"Yük Dengesi  : {result.get('load_balance')}")

            if result.get("strengths"):
                print("\n✅ Güçlü Yönler:")
                for s in result["strengths"]:
                    print(f"- {s}")

            if result.get("weaknesses"):
                print("\n⚠️ Zayıf Yönler:")
                for w in result["weaknesses"]:
                    print(f"- {w}")

            print("\n💡 Öneri:")
            print(result.get("suggestion"))

            input("\nDevam etmek için ENTER'a bas...")

        elif choice == "q":
            print("👋 AI Study Coach kapatıldı. Başarılar!")
            break

        else:
            print("❌ Geçersiz seçim.")
            input("\nDevam etmek için ENTER'a bas...")


# -------------------------------------------------
# ENTRY POINT
# -------------------------------------------------
if __name__ == "__main__":
    main()
