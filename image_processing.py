# image_processing.py
import os
import google.generativeai as genai
import PIL.Image
from dotenv import load_dotenv
import json

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def extract_data_from_image(image_file_data):
    if not API_KEY or API_KEY == "your_api_key_here":
        return {}

    try:
        img = PIL.Image.open(image_file_data)
        
        # ใช้ชื่อโมเดลที่คุณรันผ่านในแชทก่อนหน้า
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = """
        Analyze this blood gas slip. Extract these values into a clean JSON format:
        {
          "pH": number,
          "PaCO2": number,
          "PaO2": number,
          "Na": number,
          "K": number,
          "Cl": number,
          "Hb": number,
          "SaO2": number,
          "Lactate": number
        }
        Return ONLY the JSON object. If a value is missing, use null.
        """
        
        response = model.generate_content([prompt, img])
        
        # ทำความสะอาดสตริง JSON ที่ส่งกลับมา
        cleaned_text = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(cleaned_text)
        return data

    except Exception as e:
        print(f"Error in OCR: {e}")
        return {}
