import time
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY bulunamadı")

        genai.configure(api_key=api_key)
        # gemini-flash-latest genellikle 1.5 flash aliasıdır ve daha stabil kota sunar
        self.model_name = "gemini-flash-latest" 
        self.model = genai.GenerativeModel(self.model_name)

    def generate(self, prompt: str, retries: int = 3, delay: int = 5) -> str:
        for attempt in range(retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                if "429" in str(e) and attempt < retries - 1:
                    print(f"⚠️ Kota aşıldı (429), {delay} saniye sonra tekrar deneniyor... (Deneme {attempt + 1}/{retries})")
                    time.sleep(delay)
                    continue
                raise e

