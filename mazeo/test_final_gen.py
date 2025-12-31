import requests
import urllib.parse
import random

# Gemini API Key used in mazeo.py
GEMINI_API_KEY = "AIzaSyDBJh_FcjUVtA6XQpqYxMNrPscZEnm4MfE"

def call_gemini_ai(prompt, system_instruction=""):
    try:
        # Gemini 2.0 Flash is the latest stable in Dec 2025
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        full_prompt = f"{system_instruction}\n\nTask: {prompt}" if system_instruction else prompt
        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {"temperature": 0.7}
        }
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        if 'candidates' in data and len(data['candidates']) > 0:
            return data['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            print(f"Error detail: {data}")
            return None
    except Exception as e:
        return f"Error: {e}"

def test_generation():
    print("--- Mazeo Gemini 2.0 Test Mode ---")
    user_prompt = "اسد لابس بدلة فضاء فخمة"
    print(f"User Input: {user_prompt}")
    
    # 1. Translation via Gemini 2.0
    system_instruction = "You are an expert Image Prompt Engineer. Translate Arabic/slang to English. Enhance the prompt with artistic details (lighting, texture, style). Return ONLY the English prompt. No talk."
    translated = call_gemini_ai(user_prompt, system_instruction)
    print(f"Gemini Translation: {translated}")
    
    # 2. Image URL Generation (New Unified API)
    if translated and "Error" not in translated:
        seed = random.randint(1, 9999999)
        encoded_prompt = urllib.parse.quote(translated)
        image_url = f"https://gen.pollinations.ai/image/{encoded_prompt}?width=1024&height=1024&seed={seed}&model=flux&nologo=true"
        print(f"\n🚀 SUCCESS! Generated Image URL:\n{image_url}")
        print("\nقم بنسخ الرابط وفتحه في المتصفح لتشاهد إبداع Gemini الجديد!")
    else:
        print("\n❌ Failed to generate translation.")

if __name__ == "__main__":
    test_generation()
