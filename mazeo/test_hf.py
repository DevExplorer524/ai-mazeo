import urllib.request
import json

HF_TOKEN = "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"

def test_url(url):
    print(f"\nTesting: {url}")
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"inputs": "A cat"}
    data = json.dumps(payload).encode("utf-8")
    
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as response:
            print("Success!")
            return True
    except urllib.error.HTTPError as e:
        print(f"Error {e.code}: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Connection Error: {e}")
    return False

urls = [
    "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0",
    "https://router.huggingface.co/v1/images/generations", # OpenAI compatible?
    "https://hessian-ai-4.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0" # Sometimes used
]

for u in urls:
    if test_url(u):
        print(f"FOUND WORKING URL: {u}")
        break
