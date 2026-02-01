import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# --- Configuration ---
# 1. Get API Key
if "GOOGLE_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    # Replace with your actual key if running locally without secrets
    GOOGLE_API_KEY = "YOUR_API_KEY"

genai.configure(api_key=GOOGLE_API_KEY)

# --- The AI Logic ---
def get_calorie_info(image):
    # 2. Update to the latest Flash model
    model = genai.GenerativeModel('gemini-flash-latest')
    
    # 3. Refined Prompt with Macros & Specific JSON structure
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
        "analysis": "Brief explanation of the portion and health value."
    }
    
    Example:
    {
        "food_items": ["Grilled Chicken Breast", "Brown Rice"],
        "total_calories": 450,
        "macros": {
            "protein": "40%",
            "fat": "10%",
            "carbs": "50%"
        },
        "analysis": "A balanced meal high in lean protein."
    }
    """
    
    response = model.generate_content([input_prompt, image])
    
    # Cleanup to ensure we get clean JSON
    clean_text = response.text.strip().replace("```json", "").replace("```", "")
    return json.loads(clean_text)

# --- The Web App UI ---
st.set_page_config(page_title="AI Calorie Estimator", page_icon="🥗")

st.header("🥗 AI Nutritionist")

# File uploader
uploaded_file = st.file_uploader("Upload your meal", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, width=300)
    
    if st.button("Analyze Meal"):
        with st.spinner("Analyzing nutrition..."):
            try:
                # Get structured data from AI
                data = get_calorie_info(image)
                
                # --- Display Results ---
                
                # 1. Big Metric for Calories with Unit
                st.metric(label="Total Estimated Energy", value=f"{data['total_calories']} kcal")
                
                st.divider()
                
                # 2. Macronutrient Breakdown (Columns)
                st.subheader("Macronutrients Breakdown")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Protein", data['macros']['protein'])
                with col2:
                    st.metric("Fats", data['macros']['fat'])
                with col3:
                    st.metric("Carbs", data['macros']['carbs'])
                
                st.divider()
                
                # 3. Food Items & Analysis
                st.write(f"**Identified Items:** {', '.join(data['food_items'])}")
                st.info(data['analysis'])
                
            except Exception as e:
                st.error(f"Error parsing data: {e}")