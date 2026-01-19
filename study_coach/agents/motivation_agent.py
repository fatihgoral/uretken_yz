from llm.gemini_client import GeminiClient

client = GeminiClient()


def generate_motivation_message(progress_level: str | None = None) -> str:
    """
    Motivation Agent
    - LLM ile motive edici mesaj üretir
    - Hata olursa sabit fallback mesaj döner
    """

    if not progress_level:
        progress_level = "belirsiz"

    prompt = f"""
    Sen destekleyici bir ÇALIŞMA KOÇU etmensin.

    Öğrencinin bugünkü durumu: {progress_level}

    Kısa, samimi ve motive edici bir Türkçe mesaj yaz.
    """

    # ===== 1) LLM YOLU =====
    try:
        response = client.generate(prompt)

        if isinstance(response, str) and response.strip():
            return response.strip()

    except Exception:
        pass

    # ===== 2) FALLBACK =====
    return (
        "Bugün zor geçmiş olabilir ama bu, yarın daha iyi olamayacağı anlamına gelmez. "
        "Küçük adımlar bile büyük ilerlemelerin başlangıcıdır. Devam et 💪"
    )
