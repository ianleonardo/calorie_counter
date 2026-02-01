import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json
from tenacity import retry, stop_after_attempt, wait_fixed

# --- Configuration ---
if "GOOGLE_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    GOOGLE_API_KEY = "YOUR_API_KEY"

# --- SAFETY FEATURE 1: Image Optimization ---
def process_image(image):
    """
    Resizes image to max 1024x1024 to reduce RAM usage.
    """
    image.thumbnail((1024, 1024))
    return image

# --- SAFETY FEATURE 2: Auto-Retry Logic ---
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_calorie_info(image):
    # 1. Initialize the new Client
    client = genai.Client(api_key=GOOGLE_API_KEY)
    
    # 2. Define the prompt
    sys_instruction = """
    You are an expert nutritionist. Analyze the food in this image.
    Return the response in this specific JSON format (no markdown code blocks, just raw JSON):
    {
        "food_items": ["item1", "item2"],
        "total_calories": 000,
        "macros": {
            "protein": "0%",
            "fat": "0%",
            "carbs": "0%"
        },
        "analysis": "Brief explanation."
    }
    """

    # 3. Call the new API method
    # Note: The new SDK handles PIL images automatically in the 'contents' list
    response = client.models.generate_content(
        model="gemini-2.0-flash", # Updated to latest standard model
        contents=[sys_instruction, image],
        config=types.GenerateContentConfig(
            response_mime_type="application/json" # Enforce JSON output natively
        )
    )
    
    # 4. Parse response
    # The new SDK might return a JSON object directly if configured, 
    # but parsing text is safer for compatibility.
    return json.loads(response.text)

# --- UI Layout ---
st.set_page_config(page_title="AI Calorie Estimator", page_icon="🥗")
st.header("🥗 AI Nutritionist")

uploaded_file = st.file_uploader("Upload your meal", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    raw_image = Image.open(uploaded_file)
    image = process_image(raw_image)
    
    st.image(image, width=300)
    
    if st.button("Analyze Meal"):
        with st.spinner("Analyzing nutrition..."):
            try:
                data = get_calorie_info(image)
                
                st.metric(label="Total Estimated Energy", value=f"{data['total_calories']} kcal")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Protein", data['macros']['protein'])
                col2.metric("Fats", data['macros']['fat'])
                col3.metric("Carbs", data['macros']['carbs'])
                
                st.write(f"**Identified Items:** {', '.join(data['food_items'])}")
                st.info(data['analysis'])
                
            except Exception as e:
                st.error("⚠️ The AI is currently busy or the image format is invalid.")
                st.write(e) # Check specific error if needed