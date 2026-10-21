from Peticiones import create_request
import os
from dotenv import load_dotenv
load_dotenv()

result = create_request(
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent",
api_key = os.getenv("AI_API_KEY_GENAI") or os.getenv("GEMINI_API_KEY"),
prompt = "cuantas personas juegan por equipo en futbol"
)
print(result.text if result is not None else "No response received due to an error.")

