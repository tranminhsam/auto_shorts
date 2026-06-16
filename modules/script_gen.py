import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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
    
    try:
        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            generation_config={"response_mime_type": "application/json"}
        )
        response = model.generate_content(prompt_instruction)
        return json.loads(response.text)

    except Exception as e:
        print(f"❌ Lỗi kết nối API Gemini: {str(e)}")
        return None