def is_prompt_safe(user_input: str) -> bool:
    banned_keywords = [
        "intihal",
        "kopya",
        "sınav sorusu ver",
        "cevap anahtarı"
    ]

    for word in banned_keywords:
        if word.lower() in user_input.lower():
            return False

    return True
