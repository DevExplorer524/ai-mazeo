import requests
import json

GEMINI_API_KEY = "AIzaSyDBJh_FcjUVtA6XQpqYxMNrPscZEnm4MfE"

def test_api():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{
            "parts": [{"text": "Translate 'cat' to Arabic"}]
        }]
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
