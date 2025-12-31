import mazeo
import os
import time

print("Testing Image Generation...")
try:
    # Test the function directly
    image_url = mazeo.ai_generate_image("test cat", style="Realistic")
    print(f"Returned URL: {image_url}")
    
    # Check if file exists if it returns a local path
    if image_url.startswith("/static/generated/"):
        # Convert URL to file path
        # URL: /static/generated/filename.jpg -> File: static/generated/filename.jpg
        # relative to current dir E:\mazeo
        filepath = image_url.lstrip("/")
        filepath = filepath.replace("/", os.sep)
        
        if os.path.exists(filepath):
            print(f"SUCCESS: File created at {filepath}")
            print(f"Size: {os.path.getsize(filepath)} bytes")
        else:
            print(f"FAILURE: File not found at {filepath}")
    else:
        print("Returned web URL (Fallback used?)")

except Exception as e:
    print(f"ERROR: {e}")
