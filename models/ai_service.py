import json
import os
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.api_key = self._load_api_key()
    
    def _load_api_key(self):
        """Load API key from environment variables."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        return api_key
    
    def process_image(self, image):
        """Process image for AI analysis."""
        image.thumbnail((1024, 1024))
        return image
    
    def get_nutrition_analysis(self, image, diet_goal, diet_type, language):
        """
        Get nutrition analysis from Google Gemini AI.
        """
        client = genai.Client(api_key=self.api_key)
        
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
        
        try:
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=[image, sys_instruction],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except ClientError as e:
            error_text = str(e)
            if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
                raise Exception("RATE_LIMIT_EXCEEDED")
            else:
                raise Exception(f"API_ERROR: {e}")
        except Exception as e:
            raise Exception(f"ANALYSIS_ERROR: {e}")
