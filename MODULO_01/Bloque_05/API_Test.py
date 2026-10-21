import requests
import json
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

api_key = os.getenv("AI_API_KEY_GENAI") or os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError(
        "Falta configurar AI_API_KEY_GENAI o GEMINI_API_KEY en el archivo .env"
    )

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"

payload = json.dumps({
  "contents": [
    {
      "role": "user",
      "parts": [
        {
          "text": "cuantas personas juegan por equipo en futbol"
        }
      ]
    }
  ]
})
headers = {
  'x-goog-api-key': api_key,
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
