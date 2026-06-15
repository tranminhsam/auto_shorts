import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_script(topic: str):
    """Gọi API Gemini để viết kịch bản Shorts chuẩn Viral Framework."""
    
    # ===== PROMPT ĐÃ ĐƯỢC TỐI ƯU HÓA ĐỈNH CAO =====
    prompt_instruction = f"""
    Act as an elite YouTube Shorts scriptwriter specializing in viral educational and English learning content.
    Your task is to write a highly engaging, fast-paced script about: "{topic}".

    Follow this exact viral framework:
    1. THE HOOK (First 3 seconds): Start with a mind-blowing question, a shocking statement, or a strong curiosity gap to stop the scroll immediately.
    2. THE VALUE (Main body): Deliver 3 punchy, high-value points. Keep sentences short, conversational, and energetic. Use vocabulary that is natural but professional.
    3. THE CTA (Ending): End with a seamless Call-To-Action (e.g., "Subscribe to level up your English!", "What do you think? Comment below!").

    Rules for TTS (Text-to-Speech) Optimization:
    - Write COMPLETELY IN ENGLISH.
    - Write continuously. DO NOT use special characters, emojis, or markdown like *, #, or brackets.
    - Spell out numbers if necessary for better AI voice reading.
    - Keep the total word count strictly between 120 and 140 words (perfect for a 50-60 second Short).

    Visuals: Provide 4 highly descriptive, cinematic English keywords matching the vibe of the script for stock video searching (e.g., "dark ocean abyss", "students learning in modern cafe").

    You MUST return ONLY a valid JSON object matching this exact structure, nothing else:
    {{
        "full_text": "The entire script text here...",
        "visual_keywords": ["keyword1", "keyword2", "keyword3", "keyword4"]
    }}
    """
    
    try:
        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config={"response_mime_type": "application/json"}
        )
        response = model.generate_content(prompt_instruction)
        return json.loads(response.text)

    except Exception as e:
        print(f"❌ Lỗi kết nối API Gemini: {str(e)}")
        return None