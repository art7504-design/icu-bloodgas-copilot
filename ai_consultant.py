# ai_consultant.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY and API_KEY != "your_api_key_here":
    genai.configure(api_key=API_KEY)

# กำหนด System Persona
SYSTEM_INSTRUCTION = """
คุณคือผู้เชี่ยวชาญด้านเวชบำบัดวิกฤต (ICU Clinical Assistant AI)
หน้าที่ของคุณคือวิเคราะห์ข้อมูล Blood Gas และค่าที่คำนวณได้ เพื่อสรุปข้อมูลให้แพทย์อย่างกระชับ
กฎเหล็ก:
1. ห้ามวินิจฉัยโรคฟันธงเด็ดขาด
2. ตอบเป็นภาษาไทย แต่ทับศัพท์ทางการแพทย์
3. หากค่าใดไม่มีข้อมูล ให้ข้ามการวิเคราะห์ส่วนนั้นไป
"""

# --- 🚀 ฟังก์ชันไม้ตาย: ค้นหาโมเดลที่บัญชีของคุณรองรับอัตโนมัติ ---
def get_working_model_name():
    try:
        # ดึงรายชื่อโมเดลทั้งหมดที่ API Key นี้มีสิทธิ์ใช้
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # ถ้าเจอ 1.5-flash ให้ใช้ตัวนี้ก่อนเพราะเหมาะกับงานแชท
                if 'gemini-1.5-flash' in m.name:
                    return m.name
        
        # ถ้าไม่มี flash เลย ให้ดึงโมเดลตัวแรกสุดที่มันอนุญาตให้พิมพ์ข้อความได้มาใช้
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
    except Exception:
        pass
    
    return 'gemini-1.5-flash' # ตัวสำรองกรณี API เช็คไม่ได้
# -----------------------------------------------------------

def get_initial_report(ocr_data, calc_results):
    if not API_KEY or API_KEY == "your_api_key_here":
        return "⚠️ กรุณาใส่ Gemini API Key ในไฟล์ .env ก่อนใช้งานระบบ AI"

    try:
        # เรียกใช้ฟังก์ชันค้นหาโมเดลอัตโนมัติ
        model_name = get_working_model_name()
        model = genai.GenerativeModel(model_name)
        
        payload = f"[คำสั่งควบคุม: {SYSTEM_INSTRUCTION}]\n\n"
        payload += f"ข้อมูลที่วัดได้ (Measured): {ocr_data}\n"
        payload += f"ข้อมูลที่คำนวณได้ (Calculated): {calc_results}\n\n"
        payload += "กรุณาสรุปรายงานโดยใช้รูปแบบ Markdown 3 หัวข้อ: 1. 🚨 สรุปความผิดปกติที่สำคัญ 2. 💡 ข้อควรพิจารณาและคำแนะนำเบื้องต้น 3. ⚠️ ข้อควรระวัง"

        response = model.generate_content(payload)
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            return "⏳ ขออภัยครับ โควต้าการใช้งาน AI ฟรีเต็มชั่วคราว (จำกัด 5 ครั้ง/นาที) รบกวนรอสัก 30 วินาทีแล้วลองกดใหม่นะครับ 🙏"
        return f"❌ เกิดข้อผิดพลาดในระบบ AI: {error_msg}"

def get_chat_response(chat_history, new_message):
    if not API_KEY or API_KEY == "your_api_key_here":
        return "⚠️ ระบบ AI ยังไม่พร้อมใช้งาน"

    try:
        formatted_history = []
        for msg in chat_history:
            role = "user" if msg["role"] == "user" else "model"
            formatted_history.append({"role": role, "parts": [msg["content"]]})
            
        # เรียกใช้ฟังก์ชันค้นหาโมเดลอัตโนมัติ
        model_name = get_working_model_name()
        model = genai.GenerativeModel(model_name)
        
        chat = model.start_chat(history=formatted_history)
        
        full_message = f"[{SYSTEM_INSTRUCTION}]\n\nคำถามจากแพทย์: {new_message}"
        response = chat.send_message(full_message)
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            return "⏳ ขออภัยครับ โควต้าการใช้งาน AI ฟรีเต็มชั่วคราว (จำกัด 5 ครั้ง/นาที) รบกวนรอสัก 30 วินาทีแล้วลองกดใหม่นะครับ 🙏"
        return f"❌ เกิดข้อผิดพลาดในระบบ AI: {error_msg}"