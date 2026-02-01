import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from PIL import Image
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Robust API Key Loading ---
GOOGLE_API_KEY = None

# Priority 1: Check OS Environment (Works for Local + .env)
# We check this FIRST to avoid triggering the Streamlit error locally
if os.getenv("_GOOGLE_API_KEY"):
    GOOGLE_API_KEY = os.getenv("_GOOGLE_API_KEY")

# Priority 2: Check Streamlit Secrets (Works for Streamlit Cloud)
# We use a try-except block because accessing st.secrets crashes if no file exists
if not GOOGLE_API_KEY:
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    except FileNotFoundError:
        # This happens if secrets.toml doesn't exist. We just ignore it.
        pass
    except Exception:
        # Catch other Streamlit specific errors (like StreamlitSecretNotFoundError)
        pass

# Final Check: If we still don't have a key, stop the app
if not GOOGLE_API_KEY:
    st.error("❌ API Key Missing. Please set GOOGLE_API_KEY in a .env file or Streamlit secrets.")
    st.stop()

# --- TRANSLATIONS (Updated with Profile Fields) ---
TRANSLATIONS = {
    "English": {
        "title": "🥗 AI Health Coach",
        "sidebar_title": "👤 Your Profile",
        "gender": "Gender",
        "age": "Age (years)",
        "weight": "Weight (kg)",
        "height": "Height (cm)",
        "activity": "Activity Level",
        "goal_label": "Current Goal",
        "diet_label": "Dietary Preference",
        "upload_label": "Upload your meal photo",
        "analyze_btn": "Analyze Nutrition",
        "analyzing": "🍎 Consulting the AI Nutritionist...",
        "calories": "Total Energy",
        "daily_target": "Daily Target",
        "meal_impact": "Meal Impact",
        "health_score": "Health Score",
        "compliant": "Diet Compliant",    
        "non_compliant": "Not Compliant",
        "macros": "📊 Macronutrients",
        "burn": "🔥 Time to Burn It Off",
        "feedback": "💡 AI Coach Feedback",
        "identified": "Identified Items",
        "pro_tip": "💪 Pro Tip",
        "walk": "Walking",
        "run": "Running",
        "swim": "Swimming",
        "min": "min",
        "goals": ["Maintain Weight", "Weight Loss", "Muscle Gain"],
        "diets": ["No Restriction", "Keto", "Vegan", "Vegetarian", "Paleo", "Low Carb"],
        "genders": ["Male", "Female"],
        "activities": ["Sedentary (Office Job)", "Lightly Active (1-3 days/wk)", "Moderately Active (3-5 days/wk)", "Very Active (6-7 days/wk)"],
        "impact_msg": "This meal is **{pct}%** of your daily needs."
    },
    "Bahasa Indonesia": {
        "title": "🥗 AI Pelatih Kesehatan",
        "sidebar_title": "👤 Profil Anda",
        "gender": "Jenis Kelamin",
        "age": "Usia (tahun)",
        "weight": "Berat (kg)",
        "height": "Tinggi (cm)",
        "activity": "Tingkat Aktivitas",
        "goal_label": "Tujuan",
        "diet_label": "Preferensi Diet",
        "upload_label": "Unggah foto makanan",
        "analyze_btn": "Analisis Nutrisi",
        "analyzing": "🍎 Menghubungi Ahli Gizi AI...",
        "calories": "Total Energi",
        "daily_target": "Target Harian",
        "meal_impact": "Dampak Makanan",
        "health_score": "Skor Kesehatan",
        "macros": "📊 Makronutrisi",
        "burn": "🔥 Waktu Bakar Kalori",
        "feedback": "💡 Masukan Pelatih",
        "identified": "Item Teridentifikasi",
        "pro_tip": "💪 Tips Pro",
        "walk": "Berjalan",
        "run": "Lari",
        "swim": "Renang",
        "min": "mnt",
        "goals": ["Pertahankan Berat", "Turun Berat Badan", "Tambah Otot"],
        "diets": ["Tidak Ada Pantangan", "Keto", "Vegan", "Vegetarian", "Paleo", "Rendah Karbo"],
        "genders": ["Pria", "Wanita"],
        "activities": ["Kurang Gerak (Kantoran)", "Sedikit Aktif (1-3 hari/mgg)", "Cukup Aktif (3-5 hari/mgg)", "Sangat Aktif (6-7 hari/mgg)"],
        "impact_msg": "Makanan ini memenuhi **{pct}%** kebutuhan harian."
    },
    "Simplified Chinese": {
        "title": "🥗 AI 健康教练",
        "sidebar_title": "👤 您的资料",
        "gender": "性别",
        "age": "年龄 (岁)",
        "weight": "体重 (kg)",
        "height": "身高 (cm)",
        "activity": "活动水平",
        "goal_label": "目标",
        "diet_label": "饮食偏好",
        "upload_label": "上传膳食照片",
        "analyze_btn": "分析营养",
        "analyzing": "🍎 正在咨询 AI...",
        "calories": "总能量",
        "daily_target": "每日目标",
        "meal_impact": "膳食影响",
        "health_score": "健康评分",
        "macros": "📊 宏量营养素",
        "burn": "🔥 燃烧所需时间",
        "feedback": "💡 教练反馈",
        "identified": "识别食物",
        "pro_tip": "💪 专业建议",
        "walk": "步行",
        "run": "跑步",
        "swim": "游泳",
        "min": "分钟",
        "goals": ["保持体重", "减肥", "增肌"],
        "diets": ["无限制", "生酮", "纯素食", "素食", "原始饮食", "低碳水"],
        "genders": ["男", "女"],
        "activities": ["久坐 (办公室)", "轻度活跃 (1-3天/周)", "中度活跃 (3-5天/周)", "非常活跃 (6-7天/周)"],
        "impact_msg": "此餐占每日需求的 **{pct}%**。"
    },
    "Filipino": {
        "title": "🥗 AI Health Coach",
        "sidebar_title": "👤 Ang Iyong Profile",
        "gender": "Kasarian",
        "age": "Edad",
        "weight": "Timbang (kg)",
        "height": "Tangkad (cm)",
        "activity": "Antas ng Aktibidad",
        "goal_label": "Layunin",
        "diet_label": "Diet",
        "upload_label": "I-upload ang litrato",
        "analyze_btn": "Suriin",
        "analyzing": "🍎 Kumukunsulta sa AI...",
        "calories": "Kabuuang Enerhiya",
        "daily_target": "Target kada Araw",
        "meal_impact": "Epekto ng Pagkain",
        "health_score": "Health Score",
        "macros": "📊 Macronutrients",
        "burn": "🔥 Oras para Matunaw",
        "feedback": "💡 Payo ng Coach",
        "identified": "Pagkain",
        "pro_tip": "💪 Pro Tip",
        "walk": "Paglalakad",
        "run": "Pagtakbo",
        "swim": "Paglangoy",
        "min": "min",
        "goals": ["Panatilihin ang Timbang", "Magbawas ng Timbang", "Magpalaki ng Katawan"],
        "diets": ["Walang Limitasyon", "Keto", "Vegan", "Vegetarian", "Paleo", "Low Carb"],
        "genders": ["Lalaki", "Babae"],
        "activities": ["Sedentary (Opisina)", "Lightly Active (1-3 araw)", "Moderately Active (3-5 araw)", "Very Active (6-7 araw)"],
        "impact_msg": "Ang pagkaing ito ay **{pct}%** ng iyong daily needs."
    }
}

# --- CALCULATOR LOGIC ---
def calculate_target_calories(gender, age, weight, height, activity_idx, goal_idx):
    """
    Mifflin-St Jeor Equation to calculate BMR and TDEE.
    """
    # 1. Base BMR
    if gender == 0: # Male
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else: # Female
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

    # 2. Activity Multiplier
    multipliers = [1.2, 1.375, 1.55, 1.725] # Matches the index of the dropdown
    tdee = bmr * multipliers[activity_idx]

    # 3. Goal Adjustment
    if goal_idx == 0: # Maintain
        target = tdee
    elif goal_idx == 1: # Lose Weight
        target = tdee - 500
    else: # Gain Muscle
        target = tdee + 400
        
    return int(target)

# --- AI & IMAGE LOGIC ---
def process_image(image):
    image.thumbnail((1024, 1024))
    return image

# @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_calorie_info(image, diet_goal, diet_type, language):
    client = genai.Client(api_key=GOOGLE_API_KEY)
    
    sys_instruction = f"""
    You are an expert Personal Nutritionist speaking {language}.
    User Profile: Goal={diet_goal}, Diet={diet_type}.

    Analyze the food image. Respond in {language} for text fields.
    Return ONLY JSON:
    {{
        "food_items": ["item1", "item2"],
        "total_calories": 000,
        "macros": {{ "protein": "0%", "fat": "0%", "carbs": "0%" }},
        "health_score": 0,  
        "burn_off": {{ "walking": 0, "running": 0, "swimming": 0 }},
        "is_diet_compliant": true, 
        "analysis": "Brief analysis in {language}.",
        "suggestion": "One specific tip in {language}."
    }}
    """
    
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=[image, sys_instruction],
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    return json.loads(response.text)

# --- UI LAYOUT ---
st.set_page_config(page_title="AI Health Coach", page_icon="🥗", layout="wide")

# 1. Language & Sidebar
with st.sidebar:
    lang_choice = st.selectbox("Language / Bahasa / 语言 / Wika", list(TRANSLATIONS.keys()))
    t = TRANSLATIONS[lang_choice]

    st.title(t["sidebar_title"])
    
    # --- CALCULATOR INPUTS ---
    gender_inp = st.radio(t["gender"], t["genders"])
    age_inp = st.number_input(t["age"], min_value=10, max_value=100, value=25)
    weight_inp = st.number_input(t["weight"], min_value=30, max_value=200, value=70)
    height_inp = st.number_input(t["height"], min_value=100, max_value=250, value=170)
    activity_inp = st.selectbox(t["activity"], t["activities"])
    
    # Goals
    goal_inp = st.selectbox(t["goal_label"], t["goals"])
    diet_type = st.selectbox(t["diet_label"], t["diets"])

    # Calculate Daily Target Immediately
    # Map inputs to indices for the calculation function
    gender_idx = t["genders"].index(gender_inp)
    activity_idx = t["activities"].index(activity_inp)
    goal_idx = t["goals"].index(goal_inp)
    
    daily_target = calculate_target_calories(gender_idx, age_inp, weight_inp, height_inp, activity_idx, goal_idx)
    
    st.divider()
    # Display the Calculated Target in Sidebar
    st.metric(label=t["daily_target"], value=f"{daily_target} kcal")

# 2. Main Page
st.title(t["title"])

uploaded_file = st.file_uploader(t["upload_label"], type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    raw_image = Image.open(uploaded_file)
    image = process_image(raw_image)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(image, use_container_width=True)
    
    if st.button(t["analyze_btn"], type="primary"):
        with st.spinner(t["analyzing"]):
            try:
                # Get AI Analysis
                data = get_calorie_info(image, goal_inp, diet_type, lang_choice)
                
                # --- RESULTS ---
                st.divider()
                
                # SECTION: Calorie Impact
                st.subheader(t["meal_impact"])
                cal_val = data['total_calories']
                
                # Progress Bar Logic
                pct_impact = min((cal_val / daily_target), 1.0) # Cap at 100%
                pct_display = int((cal_val / daily_target) * 100)
                
                c_bar1, c_bar2 = st.columns([3, 1])
                with c_bar1:
                    st.progress(pct_impact)
                with c_bar2:
                    st.write(f"**{pct_display}%**")
                
                st.info(t["impact_msg"].format(pct=pct_display))
                
                # SECTION: Detailed Metrics
                c1, c2, c3 = st.columns(3)
                
                score = data['health_score']
                score_color = "green" if score >= 8 else "orange" if score >= 5 else "red"
                
                c1.metric(t["calories"], f"{data['total_calories']} kcal")
                c2.markdown(f"### {t['health_score']}: :{score_color}[{score}/10]")
                
                if data['is_diet_compliant']:
                    c3.success(f"✅ {t['compliant']}")
                else:
                    c3.error(f"⚠️ {t['non_compliant']}")

                # SECTION: Macros
                st.subheader(t["macros"])
                m1, m2, m3 = st.columns(3)
                m1.metric("Protein", data['macros']['protein'])
                m2.metric("Fat", data['macros']['fat'])
                m3.metric("Carbs", data['macros']['carbs'])

                # SECTION: Burn off
                st.subheader(t["burn"])
                b1, b2, b3 = st.columns(3)
                b1.info(f"🚶 {t['walk']}: {data['burn_off']['walking']} {t['min']}")
                b2.warning(f"🏃 {t['run']}: {data['burn_off']['running']} {t['min']}")
                b3.success(f"🏊 {t['swim']}: {data['burn_off']['swimming']} {t['min']}")

                # SECTION: Feedback
                st.divider()
                st.markdown(f"### {t['feedback']}")
                st.write(f"**{t['identified']}:** {', '.join(data['food_items'])}")
                st.info(data['analysis'])
                st.markdown(f"> **{t['pro_tip']}:** {data['suggestion']}")
                
            except ClientError as e:
                # Convert error to string to check the code
                error_text = str(e)
                
                if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
                    st.error("🚨 **Traffic Limit Reached (Free Tier)**")
                    st.warning("You have used up your free requests for this minute.")
                    
                    # Optional: Extract the exact wait time using basic string search
                    # The error says: "Please retry in 33.036s."
                    if "Please retry in" in error_text:
                        # Extract the number roughly
                        try:
                            import re
                            wait_time = re.search(r"retry in ([0-9\.]+)s", error_text).group(1)
                            st.info(f"⏳ **Please wait {float(wait_time):.0f} seconds** before clicking Analyze again.")
                        except:
                            st.info("⏳ Please wait about 30-60 seconds.")
                else:
                    # Some other API error (like 400 Bad Request)
                    st.error(f"⚠️ API Error: {e}")
                                    
            except Exception as e:
                st.error("⚠️ Error / Kesalahan / 错误")
                st.write(e)