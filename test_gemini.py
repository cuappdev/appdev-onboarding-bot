import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("models/gemini-2.5-flash")

response = model.generate_content("Say hi to Cornell AppDev!")
print("✅ Gemini response:", response.text)
