import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

def get_working_model():
    """ค้นหาชื่อโมเดลที่ใช้งานได้จริงในบัญชีนี้"""
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # เลือก Flash เป็นลำดับแรกเพื่อความประหยัด
                if 'gemini-1.5-flash' in m.name:
                    return m.name
        # ถ้าหา Flash ไม่เจอ ให้เอาตัวแรกที่ใช้ได้
        return 'models/gemini-1.5-flash' 
    except:
        return 'models/gemini-1.5-flash'

def get_ai_consultation(full_data):
    if not API_KEY:
        return "ไม่พบ API Key กรุณาตรวจสอบการตั้งค่า"

    try:
        # ใช้ฟังก์ชันหาชื่อรุ่นที่ถูกต้อง
        model_name = get_working_model()
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        คุณคือผู้เชี่ยวชาญด้านเวชบำบัดวิกฤต (Critical Care Specialist) 
        จงวิเคราะห์ผล Arterial Blood Gas (ABG) ต่อไปนี้และให้คำแนะนำในการดูแลผู้ป่วย:
        
        ข้อมูลผลแล็บ:
        - pH: {full_data.get('pH')}
        - PaCO2: {full_data.get('PaCO2')} mmHg
        - PaO2: {full_data.get('PaO2')} mmHg
        - Electrolytes: Na {full_data.get('Na')}, K {full_data.get('K')}, Cl {full_data.get('Cl')}
        - อื่นๆ: Lactate {full_data.get('Lactate')}, Hb {full_data.get('Hb')}, SaO2 {full_data.get('SaO2')}%
        
        ข้อมูลผู้ป่วยและเครื่องช่วยหายใจ:
        - อายุ: {full_data.get('Age')} ปี
        - FiO2: {full_data.get('FiO2')}%
        - PEEP: {full_data.get('PEEP')}
        - Ventilator Mode: {full_data.get('Mode')}
        - ประวัติเพิ่มเติม: {full_data.get('History')}
        
        จงสรุปเป็นภาษาไทย:
        1. การแปลผลหลัก (เช่น Metabolic Acidosis, Respiratory Alkalosis ฯลฯ)
        2. การวิเคราะห์สาเหตุที่เป็นไปได้
        3. คำแนะนำในการปรับเครื่องช่วยหายใจ หรือการรักษาเบื้องต้น
        """
        
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"เกิดข้อผิดพลาดในการวิเคราะห์: {str(e)}"
