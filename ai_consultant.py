import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

def get_ai_consultation(full_data):
    """
    ฟังก์ชันส่งข้อมูลวิเคราะห์โดยใช้โมเดล Gemini 2.5 Flash ตามสิทธิ์ใช้งานจริง
    """
    if not API_KEY:
        return "ไม่พบ API Key กรุณาตรวจสอบการตั้งค่า"

    try:
        # ปรับชื่อโมเดลให้ตรงตามที่ปรากฏในระบบของคุณหมอ
        # โดยปกติรุ่นใหม่จะใช้ชื่อ 'gemini-2.5-flash' หรือ 'models/gemini-2.5-flash'
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
        # หากชื่อ 2.5-flash ยังหาไม่เจอ ให้ลองถอยกลับไปใช้ระบบ Auto-detect รุ่นที่ใช้งานได้
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            # ค้นหาโมเดลที่มีคำว่า 'flash' ในชื่อ
            best_model = next((m for m in available_models if 'flash' in m), available_models[0])
            model = genai.GenerativeModel(best_model)
            response = model.generate_content(prompt)
            return response.text
    def chat_with_gemini(context, chat_history):
    """
    ฟังก์ชันสำหรับแชทถาม-ตอบต่อเนื่อง โดยจดจำบริบทของคนไข้และคำแนะนำก่อนหน้า
    """
    if not API_KEY:
        return "ไม่พบ API Key กรุณาตรวจสอบการตั้งค่า"

    try:
        model_name = get_working_model() # ดึงชื่อรุ่นที่ทำงานได้จากฟังก์ชันด้านบน
        model = genai.GenerativeModel(model_name)

        # แปลงประวัติแชทของ Streamlit ให้เข้ากับรูปแบบของ Gemini API
        formatted_history = []
        for msg in chat_history[:-1]: # ไม่เอาข้อความล่าสุด (เพราะเราจะส่งแยก)
            role = "model" if msg["role"] == "assistant" else "user"
            formatted_history.append({"role": role, "parts": [msg["content"]]})

        # เริ่ม Session แชทแบบมีความจำ
        chat = model.start_chat(history=formatted_history)

        # ดึงคำถามล่าสุดที่ผู้ใช้เพิ่งพิมพ์มา
        latest_prompt = chat_history[-1]["content"]

        # 💡 ทริคสำคัญ: ถ้าเป็นการถามครั้งแรก ให้เราแอบแนบ "ประวัติคนไข้" ไปกับคำถามด้วย
        # เพื่อให้ AI รู้ว่าเรากำลังคุยเรื่องเคสไหนอยู่ โดยที่หน้าจอแอปไม่ต้องโชว์ข้อความยาวๆ
        if len(chat_history) == 1:
            latest_prompt = f"บริบทข้อมูลคนไข้ปัจจุบัน:\n{context}\n\nคำถามจากแพทย์: {latest_prompt}"

        # ส่งคำถามและรับคำตอบ
        response = chat.send_message(latest_prompt)
        return response.text

    except Exception as e:
        return f"เกิดข้อผิดพลาดในการเชื่อมต่อแชท: {str(e)}"
        except:
            return f"เกิดข้อผิดพลาดในการวิเคราะห์: {str(e)}"
