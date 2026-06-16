import os
import json
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def generate_script(topic: str):
    prompt_instruction = f"""
    Act as an elite YouTube Shorts scriptwriter and Visual Director.
    Your task is to write a highly engaging, fast-paced storytelling script about: "{topic}".

    CRITICAL INSTRUCTION: You must divide the script into EXACTLY 6 equal scenes. 
    For each scene, provide the narration text and a highly specific visual search keyword that matches the EXACT words being spoken in that scene.

    Rules for Narration:
    - Keep the word count for EACH scene roughly equal (around 20-25 words per scene) so the video timing stays perfectly synced.
    - Write continuously, like a smooth story. DO NOT use list words like "First", "Second". 
    - No special characters or emojis.

    Rules for Keywords:
    - 1 to 3 words max. Highly cinematic and visual (e.g., "glowing jellyfish", "abandoned city").

    You MUST return ONLY a valid JSON object matching this exact structure:
    {{
        "scenes": [
            {{
                "narration": "Text for scene 1...",
                "keyword": "keyword 1"
            }},
            {{
                "narration": "Text for scene 2...",
                "keyword": "keyword 2"
            }},
            {{
                "narration": "Text for scene 3...",
                "keyword": "keyword 3"
            }},
            {{
                "narration": "Text for scene 4...",
                "keyword": "keyword 4"
            }},
            {{
                "narration": "Text for scene 5...",
                "keyword": "keyword 5"
            }},
            {{
                "narration": "Text for scene 6...",
                "keyword": "keyword 6"
            }}
        ]
    }}
    """
    
    max_retries = 3
    # Khởi tạo Client theo chuẩn SDK mới của Google
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    for attempt in range(max_retries):
        try:
            # Cú pháp gọi API thế hệ mới
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt_instruction,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)

        except Exception as e:
            error_message = str(e)
            if "429" in error_message or "Quota" in error_message:
                print(f"   ⏳ Google đang yêu cầu giảm tốc độ (Lỗi 429). Hệ thống tự động ngủ 30 giây... (Thử lại lần {attempt + 1}/{max_retries})")
                time.sleep(30)
            else:
                print(f"❌ Lỗi kết nối API Gemini: {error_message}")
                return None
                
    print("❌ Đã thử lại 3 lần nhưng API vẫn từ chối. Vui lòng kiểm tra lại API Key hoặc đổi Key mới.")
    return None