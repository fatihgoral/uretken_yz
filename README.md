# 🤖 AI Study Coach

AI Study Coach, öğrencilerin sınav hazırlık süreçlerini daha düzenli ve verimli hale getirmek için tasarlanmış akıllı bir çalışma asistanıdır. Gemini LLM altyapısını kullanarak kişiselleştirilmiş çalışma planları oluşturur, geri bildirimleri analiz eder ve motivasyon sağlar.

## ✨ Özellikler

- 📅 **Haftalık Plan Oluşturma**: Sınav tarihinize ve günlük müsaitliğinize göre dinamik haftalık planlar.
- 🧠 **Geri Bildirim Analizi**: Günlük ilerlemenize göre duygu ve yoğunluk analizi yapar, gerekirse planı günceller.
- 🎯 **Motivasyon Desteği**: Çalışma modunuza göre size özel motivasyon mesajları üretir.
- 📊 **Plan Eleştirisi**: Mevcut çalışma planınızı "Plan Critic Agent" ile değerlendirir ve iyileştirme önerileri sunar.
- 🧭 **Agentic Koordinasyon**: Feedback'lere göre plan yoğunluğunu otomatik (veya manuel) ayarlayan koordinatör sistemi.
- 🖥️ **Çift Arayüz**: Hem Terminal (CLI) hem de Streamlit üzerinden kullanım imkanı.

## 🚀 Kurulum

1. Depoyu klonlayın:
   ```bash
   git clone <repository-url>
   cd PythonProject9
   ```

2. Sanal ortam oluşturun ve aktif edin:
   ```bash
   python -m venv .venv
   # Windows için:
   .venv\Scripts\activate
   # macOS/Linux için:
   source .venv/bin/activate
   ```

3. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
   *(Not: Henüz bir requirements.txt yoksa `google-generativeai`, `streamlit`, `python-dotenv` kütüphanelerini yükleyin.)*

4. `.env` dosyasını oluşturun ve Gemini API anahtarınızı ekleyin:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

## 🛠️ Kullanım

### CLI (Terminal) Arayüzü
Ana menüye erişmek için:
```bash
python study_coach/main.py
```

### Streamlit (Web) Arayüzü
Görsel arayüzü başlatmak için:
```bash
streamlit run study_coach/ui_streamlit.py
```

## 📂 Proje Yapısı

- `study_coach/`: Uygulamanın ana dizini.
  - `agents/`: Planlama, motivasyon, eleştiri ve koordinatör agentları.
  - `llm/`: Gemini API istemcisi.
  - `plans/`: Kaydedilen çalışma planları.
  - `security/`: Kimlik doğrulama işlemleri.
  - `ui_streamlit.py`: Web tabanlı kullanıcı arayüzü.
  - `main.py`: Terminal tabanlı ana uygulama.

## 📄 Lisans
Bu proje eğitim amaçlı geliştirilmiştir.
