"""
AI Chatbot router for agriculture expert advice.
Uses Google Gemini 2.5 Pro.
"""

import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

router = APIRouter(prefix="/ai", tags=["ai"])

# Load API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY missing in .env")

genai.configure(api_key=GEMINI_API_KEY)

# Best stable model
MODEL_NAME = "models/gemini-2.5-pro"

SYSTEM_PROMPT = """
You are AgriBot — an expert agriculture assistant.
Give responses in simple English (or the user’s language).
Avoid safety refusals unless strictly required.
"""

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=SYSTEM_PROMPT
        )

        response = model.generate_content(
            contents=[{"role": "user", "parts": [request.message]}],
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 300,
            }
        )

        # Correct extraction method (2025 format)
        reply = ""

        if response.candidates:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "text"):
                    reply += part.text

        if not reply.strip():
            reply = "I'm here to help! Please ask me anything about farming."

        return ChatResponse(reply=reply)

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")
