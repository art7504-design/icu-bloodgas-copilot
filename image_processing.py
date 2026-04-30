# image_processing.py
import os
import google.generativeai as genai
import PIL.Image
from dotenv import load_dotenv
import json
import re

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY and API_KEY != "your_api_key_here":
    genai.configure(api_key=API_KEY)

def get_working_model_name():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for name in available_models:
            if 'gemini-1.5-flash' in name: return name
        return available_models[0] if available_models else 'gemini-1.5-flash'
    except: return 'gemini-1.5-flash'

def extract_data_from_image(image_file_data):
    if not API_KEY or API_KEY == "your_api_key_here":
        return {}

    try:
        img = PIL.Image.open(image_file_data)
        model_name = get_working_model_name()
        model = genai.GenerativeModel(model_name)
        
        # ปรับ Prompt ให้ระบุชื่อ Key ให้ตรงกับหน้าจอ app.py เป๊ะๆ
        prompt = """
        Extract numerical values from this medical slip.
        Return ONLY a JSON object with these EXACT keys:
        "pH", "PaCO2", "PaO2", "Na", "K", "Cl", "Hb", "SaO2", "Lactate"
        
        Important:
        - Use "pH" (not ph)
        - Use "PaCO2" (not pCO2)
        - Use "PaO2" (not pO2)
        - Return only numbers or null.
        - No markdown formatting.
        """
        
        response = model.generate_content([prompt, img])
        raw_text = response.text.strip()
        
        # สกัด JSON ออกมา
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            
            # ระบบ Re-mapping เพื่อความชัวร์ (ถ้า AI ตอบตัวเล็กมา เราแก้ให้เป็นตัวใหญ่)
            final_data = {}
            mapping = {
                "ph": "pH", "paco2": "PaCO2", "pao2": "PaO2",
                "na": "Na", "k": "K", "cl": "Cl",
                "hb": "Hb", "sao2": "SaO2", "lactate": "Lactate"
            }
            
            for k, v in data.items():
                std_key = mapping.get(k.lower(), k)
                # แปลงค่าให้เป็น string เพื่อให้ Text Input ของ Streamlit รับได้ง่าย
                final_data[std_key] = str(v) if v is not None else ""
                
            return final_data
        return {}
    except Exception as e:
        error_msg = str(e)
        # ดักจับปัญหาโควต้าเต็ม (Error 429)
        #if "429" in error_msg or "quota" in error_msg.lower():
            #return {"Error": "QUOTA_EXCEEDED", "Message": "โควต้าเต็มชั่วคราว (15 ครั้ง/นาที) กรุณารอสัก 30 วินาที"}
        
        # ดักจับปัญหาโมเดลหาไม่เจอ (Error 404)
        #if "404" in error_msg:
            #return {"Error": "MODEL_NOT_FOUND", "Message": f"ไม่พบโมเดล {target_model} ในบัญชีนี้"}
            
        return {"Error": "SYSTEM_ERROR", "Message": f"เกิดข้อผิดพลาด: {error_msg}"}
