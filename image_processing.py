# image_processing.py
import os
import google.generativeai as genai
import PIL.Image
from dotenv import load_dotenv
import json

# โหลด API Key เพื่อใช้ Gemini Vision
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def extract_data_from_image(image_file_data):
    """
    ฟังก์ชันสกัดข้อมูลตัวเลขทางการแพทย์จากสลิป ABG/VBG 
    โดยใช้ Gemini Vision API (Multimodal)
    """
    if not API_KEY or API_KEY == "your_api_key_here":
        # ถ้าไม่มี API Key ให้ส่ง Dummy data กลับไปเพื่อไม่ให้แอปพัง (สำหรับเทสต์ UI)
        return {"pH": "7.40", "PaCO2": "40", "PaO2": "148", "Error": "Missing API Key"}

    try:
        # เปิดไฟล์ภาพที่รับมาจาก Streamlit
        img = PIL.Image.open(image_file_data)
        
        # เลือกใช้โมเดล Vision (แนะนำ gemini-pro-vision หรือ gemini-1.5-flash-latest)
        # ตรงนี้เราจะลองสุ่มใช้ gemini-pro-vision ก่อนเพื่อความเสถียร
        model = genai.GenerativeModel('gemini-pro-vision')
        
        # เขียน Command Prompt (Instruction) เพื่อสั่ง AI ให้อ่านภาพแบบเฉพาะเจาะจง
        prompt = """
        Analyze this medical blood gas slip. 
        Extract the numerical values for the following parameters ONLY.
        Respond with a clean JSON format using these keys:
        - "pH" (The numerical pH value)
        - "PaCO2" (The carbon dioxide partial pressure)
        - "PaO2" (The oxygen partial pressure)
        - "Na" (Sodium)
        - "K" (Potassium)
        - "Cl" (Chloride)
        - "Lactate" (Lactate)
        - "Hb" (Hemoglobin)
        - "SaO2" (Oxygen saturation, if present)
        
        Ignore references, units (like mmol/L, mmHg), and comments. 
        If a value is not present, use null.
        Provide only the JSON. No extra text.
        """
        
        # ส่งภาพและคำสั่งไปให้ AI
        response = model.generate_content([prompt, img])
        text_response = response.text
        
        # สกัดข้อความในรูปแบบ JSON ออกมาใช้งาน
        try:
            # ทำความสะอาดข้อความ เผื่อ AI ตอบมาเกิน
            cleaned_response = text_response.strip().replace("```json", "").replace("```", "")
            data = json.loads(cleaned_response)
            return data
        except json.JSONDecodeError:
            return {"Error": "AI did not return valid JSON.", "RawOutput": text_response}

    except Exception as e:
        return {"Error": f"OCR Process Failed: {str(e)}"}
