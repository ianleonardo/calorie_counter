import streamlit as st
from google import genai
from PIL import Image
import json
from tenacity import retry, stop_after_attempt, wait_fixed # New: For auto-retries

# --- Configuration ---
if "GOOGLE_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    GOOGLE_API_KEY = "YOUR_API_KEY"

genai.configure(api_key=GOOGLE_API_KEY)

# --- SAFETY FEATURE 1: Image Optimization ---
def process_image(image):
    """
    Resizes image to max 1024x1024 to reduce RAM usage.
    A 12MP photo uses ~50MB RAM. This resize drops it to ~2MB.
    """
    image.thumbnail((1024, 1024)) 
    return image

# --- SAFETY FEATURE 2: Auto-Retry Logic ---
# If the API fails (busy/error), it waits 2 seconds and tries again (up to 3 times)
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_calorie_info(image):
    model = genai.GenerativeModel('gemini-flash-latest')
    
    input_prompt = """
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
    
    response = model.generate_content([input_prompt, image])
    clean_text = response.text.strip().replace("```json", "").replace("```", "")
    return json.loads(clean_text)

# --- UI Layout ---
st.set_page_config(page_title="AI Calorie Estimator", page_icon="🥗")
st.header("🥗 AI Nutritionist")

uploaded_file = st.file_uploader("Upload your meal", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Load and immediately optimize the image
    raw_image = Image.open(uploaded_file)
    image = process_image(raw_image)
    
    st.image(image, width=300)
    
    if st.button("Analyze Meal"):
        with st.spinner("Analyzing nutrition..."):
            try:
                # Call the robust function
                data = get_calorie_info(image)
                
                # Display Results
                st.metric(label="Total Estimated Energy", value=f"{data['total_calories']} kcal")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Protein", data['macros']['protein'])
                col2.metric("Fats", data['macros']['fat'])
                col3.metric("Carbs", data['macros']['carbs'])
                
                st.write(f"**Identified Items:** {', '.join(data['food_items'])}")
                st.info(data['analysis'])
                
            except Exception as e:
                # Graceful Error Message (instead of crashing)
                st.error("⚠️ The AI is currently busy. Please wait 5 seconds and try again.")
                # st.error(f"Debug details: {e}") # Uncomment for debugging