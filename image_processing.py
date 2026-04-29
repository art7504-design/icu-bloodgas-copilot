# image_processing.py
import os
import google.generativeai as genai
import PIL.Image
from dotenv import load_dotenv
import json

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY and API_KEY != "your_api_key_here":
    genai.configure(api_key=API_KEY)

# --- 🚀 ฟังก์ชันไม้ตาย: ค้นหาโมเดลที่บัญชีของคุณรองรับอัตโนมัติ ---
# (เราเอามันมาใช้ในนี้ด้วยเพื่อความชัวร์)
def get_working_model_name():
    try:
        # ดึงรายชื่อโมเดลทั้งหมดที่ API Key นี้มีสิทธิ์ใช้
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # ถ้าเจอ 1.5-flash หรือ pro (ที่มี Vision) ให้ใช้ก่อน
                if 'gemini-1.5-flash' in m.name or 'gemini-pro-vision' in m.name:
                    return m.name
        
        # ถ้าไม่มี flash/pro-vision เลย ให้ดึงโมเดลตัวแรกสุดที่อนุญาตให้พิมพ์ข้อความได้มาใช้
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
    except Exception:
        pass
    
    return 'gemini-1.5-flash' # ตัวสำรอง (ซึ่งถ้า error ก็จะเหมือนเดิม)
# -----------------------------------------------------------

def extract_data_from_image(image_file_data):
    """
    ฟังก์ชันสกัดข้อมูลตัวเลขทางการแพทย์จากสลิป ABG/VBG 
    โดยใช้ Gemini Vision API (Multimodal) แบบ Auto-detect
    """
    if not API_KEY or API_KEY == "your_api_key_here":
        # ถ้าไม่มี API Key ให้ส่ง Dummy data กลับไปเพื่อไม่ให้แอปพัง (สำหรับเทสต์ UI)
        return {"pH": "7.40", "PaCO2": "40", "PaO2": "148", "Error": "Missing API Key"}

    try:
        # เปิดไฟล์ภาพที่รับมาจาก Streamlit
        img = PIL.Image.open(image_file_data)
        
        # เรียกใช้ฟังก์ชันค้นหาโมเดลอัตโนมัติ
        model_name = get_working_model_name()
        
        # กรองเพื่อให้ได้โมเดลที่รองรับการอ่านภาพ (ถ้ามี)
        model = genai.GenerativeModel(model_name)
        
        # เขียน Command Prompt (Instruction) เพื่อสั่ง AI ให้อ่านภาพแบบ JSON
        prompt = """
        Analyze this medical blood gas slip image. 
        Extract numerical values for THESE parameters only into a clean JSON format:
        {
          "pH": number,
          "PaCO2": number,
          "PaO2": number,
          "Na": number,
          "K": number,
          "Cl": number,
          "Lactate": number,
          "Hb": number,
          "SaO2": number
        }
        Return ONLY the JSON. If a value is missing or unreadable, use null.
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
            print(f"Error in JSON decoding: {text_response}")
            return {}

    except Exception as e:
        error_msg = str(e)
        # ตรวจสอบว่า Error เกี่ยวกับโควต้า (429) หรือไม่
        if "429" in error_msg or "quota" in error_msg.lower():
            return {"Error": "QUOTA_EXCEEDED", "Message": "โควต้าการใช้งาน AI เต็มชั่วคราว (15 ครั้ง/นาที) กรุณารอสักครู่ครับ"}
        elif "404" in error_msg:
            return {"Error": "MODEL_NOT_FOUND", "Message": "ไม่พบโมเดล AI ในระบบ โปรดตรวจสอบชื่อโมเดล"}
        else:
            # ถ้าเป็น Error อื่นๆ ให้แสดงข้อความ Error จริงออกมาเลยจะได้แก้ถูกจุด
            return {"Error": "SYSTEM_ERROR", "Message": f"เกิดข้อผิดพลาด: {error_msg}"}
