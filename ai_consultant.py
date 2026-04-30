import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

def get_ai_consultation(full_data):
    """ฟังก์ชันสำหรับวิเคราะห์ ABG และข้อมูลผู้ป่วย"""
    if not API_KEY:
        return "ไม่พบ API Key กรุณาตรวจสอบการตั้งค่า"

    try:
        # ใช้ Gemini 2.5 Flash ตามสิทธิ์ใช้งาน
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        คุณคือผู้เชี่ยวชาญด้านเวชบำบัดวิกฤต (Critical Care Specialist) 
        จงวิเคราะห์ผล Arterial Blood Gas (ABG) ต่อไปนี้และให้คำแนะนำทางการแพทย์:
        
        ข้อมูลผลแล็บ:
        - pH: {full_data.get('pH')}
        - PaCO2: {full_data.get('PaCO2')} mmHg
        - PaO2: {full_data.get('PaO2')} mmHg
        - Electrolytes: Na {full_data.get('Na')}, K {full_data.get('K')}, Cl {full_data.get('Cl')}
        - อื่นๆ: Lactate {full_data.get('Lactate')}, Hb {full_data.get('Hb')}, SaO2 {full_data.get('SaO2')}%
        
        ค่าที่ระบบคำนวณให้:
        - P/F Ratio: {full_data.get('Calculated_PF')}
        - A-a Gradient: {full_data.get('Calculated_Aa')}
        
        ข้อมูลผู้ป่วย:
        - อายุ: {full_data.get('Age')} ปี
        - FiO2: {full_data.get('FiO2')}%
        - PEEP: {full_data.get('PEEP')}
        - Ventilator Mode: {full_data.get('Mode')}
        - ประวัติ/อาการ: {full_data.get('History')}
        
        กรุณาสรุปเป็นภาษาไทย:
        1. การแปลผลหลัก (Primary Acid-Base Disturbance)
        2. การวิเคราะห์สาเหตุ (Differential Diagnosis)
        3. คำแนะนำในการปรับ Ventilator setting หรือการจัดการเบื้องต้น
        """
        
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"เกิดข้อผิดพลาดในการวิเคราะห์: {str(e)}"

def chat_with_gemini(context, chat_history):
    """ฟังก์ชันสำหรับแชทถาม-ตอบต่อเนื่อง"""
    if not API_KEY:
        return "ไม่พบ API Key กรุณาตรวจสอบการตั้งค่า"

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        formatted_history = []
        for msg in chat_history[:-1]: 
            role = "model" if msg["role"] == "assistant" else "user"
            formatted_history.append({"role": role, "parts": [msg["content"]]})

        chat = model.start_chat(history=formatted_history)
        latest_prompt = chat_history[-1]["content"]

        if len(chat_history) == 1:
            latest_prompt = f"บริบทข้อมูลคนไข้ปัจจุบัน:\n{context}\n\nคำถามจากแพทย์: {latest_prompt}"

        response = chat.send_message(latest_prompt)
        return response.text

    except Exception as e:
        return f"เกิดข้อผิดพลาดในการเชื่อมต่อแชท: {str(e)}"
