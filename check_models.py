import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load your API key
load_dotenv()
genai.configure(api_key="AIzaSyD99jYR9oT-j1x3ImtwN0vbBRaWXBRDbPo") # Or use os.getenv("GOOGLE_API_KEY")

print("List of available models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)