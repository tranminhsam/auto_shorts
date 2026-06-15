import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_script(topic: str):
    """Gọi API Gemini để viết kịch bản Shorts dạng kể chuyện mượt mà, không liệt kê."""
    
    # ===== PROMPT CHUYÊN SÂU VỀ KỸ NĂNG KỂ CHUYỆN (STORYTELLING) =====
    prompt_instruction = f"""
    Act as an elite YouTube Shorts scriptwriter specializing in viral, mind-blowing facts and fascinating knowledge.
    Your task is to write a highly engaging, fast-paced storytelling script about: "{topic}".

    Follow this exact viral framework:
    1. THE HOOK (First 3 seconds): Start with a mind-blowing question, a shocking statement, or a strong curiosity gap to stop the scroll immediately.
    2. THE NARRATIVE (Main body): Deliver fascinating facts using a smooth, continuous storytelling flow. 
    CRITICAL RULE: DO NOT use list words like "First", "Second", "Third", "Number one", "Number two", or "Next". 
    Instead, weave the facts together using natural, conversational transitions (e.g., "But what's even crazier is...", "Think about it...", "It gets weirder when you realize..."). 
    The goal is to make the viewer feel like they are listening to a gripping, mysterious story rather than a list of facts.
    3. THE CTA (Ending): End with a seamless Call-To-Action focusing on curiosity (e.g., "Subscribe for more mind-blowing facts!", "Did you know this? Comment below!"). Do NOT mention learning English.

    Rules for TTS (Text-to-Speech) Optimization:
    - Write COMPLETELY IN ENGLISH.
    - Write continuously. DO NOT use special characters, emojis, or markdown like *, #, or brackets.
    - Spell out numbers if necessary for better AI voice reading.
    - Keep the total word count strictly between 120 and 140 words (perfect for a 50-60 second Short).

    Visuals: Provide 6 highly descriptive, cinematic English keywords matching the vibe of the script for stock video searching (e.g., "dark ocean abyss", "mysterious glowing forest").

    You MUST return ONLY a valid JSON object matching this exact structure, nothing else:
    {{
        "full_text": "The entire script text here...",
        "visual_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5", "keyword6"]
    }}
    """
    
    try:
        model = genai.GenerativeModel(
            'gemini-3.5-flash',
            generation_config={"response_mime_type": "application/json"}
        )
        response = model.generate_content(prompt_instruction)
        return json.loads(response.text)

    except Exception as e:
        print(f"❌ Lỗi kết nối API Gemini: {str(e)}")
        return None