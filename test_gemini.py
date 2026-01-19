import os
from google import genai

client = genai.Client(
    api_key=os.environ.get("GOOGLE_API_KEY")
)

response = client.models.generate_content(
    model="models/gemini-flash-latest",
    contents="Beni 1 cümleyle motive et"
)

print(response.text)
