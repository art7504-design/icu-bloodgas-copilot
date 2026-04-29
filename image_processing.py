# image_processing.py
import os
import google.generativeai as genai
import PIL.Image
from dotenv import load_dotenv
import json
import re

# โหลดค่าจากไฟล์ .env (สำหรับรันในเครื่อง)
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# ตั้งค่า API Key
if API_KEY and API_KEY != "your_api_key_here":
    genai.configure(api_key=API_KEY)

def get_working_model_name():
    """
    ฟังก์ชันตรวจสอบว่าบัญชีนี้ใช้โมเดลชื่ออะไรได้บ้าง (แก้ปัญหา 404 Model Not Found)
    """
    try:
        # ดึงรายชื่อโมเดลที่รองรับการสร้างเนื้อหา
        available_models = [m.name for m in genai.list_models() 
                           if 'generateContent' in m.supported_generation_methods]
        
        # ลำดับความสำคัญ: 1.5 Flash -> 1.5 Pro -> อะไรก็ได้ที่ใช้ได้
        for name in available_models:
            if 'gemini-1.5-flash' in name:
                return name
        for name in available_models:
            if 'gemini-1.5-pro' in name:
                return name
        
        return available_models[0] if available_models else 'gemini-1.5-flash'
    except Exception:
        return 'gemini-1.5-flash' # ตัวสำรองกรณีเช็คไม่ได้

def extract_data_from_image(image_file_data):
    """
    ฟังก์ชันสกัดข้อมูลตัวเลขจากภาพสลิป ABG/VBG
    รวมการแก้ปัญหา JSON พัง และ Quota เต็ม
    """
    if not API_KEY or API_KEY == "your_api_key_here":
        return {"Error": "MISSING_API_KEY", "Message": "กรุณาใส่ API Key ใน Settings"}

    try:
        # เปิดไฟล์ภาพ
        img = PIL.Image.open(image_file_data)
        
        # เลือกโมเดลที่ใช้งานได้อัตโนมัติ
        target_model = get_working_model_name()
        model = genai.GenerativeModel(target_model)
        
        # Prompt ที่บังคับให้ตอบเฉพาะ JSON และแม่นยำที่สุด
        prompt = """
        Extract numerical values from this blood gas result image.
        Return ONLY a JSON object with these exact keys:
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
        Requirements:
        1. Return ONLY JSON. No explanations.
        2. If a value is missing or unreadable, use null.
        3. Do not include units (e.g., use 7.4 instead of "7.4 pH").
        """
        
        response = model.generate_content([prompt, img])
        raw_text = response.text.strip()
        
        # --- ระบบดักจับ JSON (Robust Parsing) ---
        # ใช้ Regex ค้นหาข้อความที่อยู่ในปีกกา {} เพื่อตัดส่วนเกินที่ AI อาจจะแถมมา
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            # ปรับแต่งค่าเล็กน้อยเพื่อให้ตรงกับความต้องการของแอป
            # ป้องกันกรณี AI ตอบชื่อ Key เป็นตัวเล็กทั้งหมด
            formatted_data = {}
            mapping = {
                "ph": "pH", "paco2": "PaCO2", "pao2": "PaO2", 
                "na": "Na", "k": "K", "cl": "Cl", 
                "hb": "Hb", "sao2": "SaO2", "lactate": "Lactate"
            }
            
            for k, v in data.items():
                std_key = mapping.get(k.lower(), k)
                formatted_data[std_key] = v
                
            return formatted_data
        else:
            return {"Error": "INVALID_FORMAT", "Message": "AI ตอบกลับในรูปแบบที่ไม่อ่านค่าไม่ได้"}

    except Exception as e:
        error_msg = str(e)
        # ดักจับปัญหาโควต้าเต็ม (Error 429)
        if "429" in error_msg or "quota" in error_msg.lower():
            return {"Error": "QUOTA_EXCEEDED", "Message": "โควต้าเต็มชั่วคราว (15 ครั้ง/นาที) กรุณารอสัก 30 วินาที"}
        
        # ดักจับปัญหาโมเดลหาไม่เจอ (Error 404)
        if "404" in error_msg:
            return {"Error": "MODEL_NOT_FOUND", "Message": f"ไม่พบโมเดล {target_model} ในบัญชีนี้"}
            
        return {"Error": "SYSTEM_ERROR", "Message": f"เกิดข้อผิดพลาด: {error_msg}"}
