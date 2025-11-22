import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("models/gemini-2.5-pro")

response = model.generate_content("Hello")

print("Candidates:", response.candidates)
print("Finish reason:", response.candidates[0].finish_reason if response.candidates else None)

for idx, c in enumerate(response.candidates):
    print("Candidate", idx, "parts:", c.content.parts)
