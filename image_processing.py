# image_processing.py
import os
import google.generativeai as genai
from PIL import Image
import json
import re

def extract_data_from_image(uploaded_file):
    """
    ใช้ Gemini ในการอ่านข้อมูลจากรูปภาพสลิป Blood Gas
    """
    try:
        # โหลดรูปภาพ
        img = Image.open(uploaded_file)
        
        # ค้นหาโมเดล (ใช้เทคนิคเดียวกับที่คุยกันก่อนหน้า)
        model = genai.GenerativeModel('gemini-1.5-flash-latest') # หรือรุ่นที่คุณมีสิทธิ์ใช้
        
        prompt = """
        คุณคือผู้เชี่ยวชาญด้านการอ่านผล Lab 
        ช่วยอ่านค่าจากรูปสลิป Blood Gas นี้และส่งกลับมาเป็น JSON format เท่านั้น 
        โดยใช้ชื่อ Key ดังนี้: pH, PaCO2, PaO2, Na, K, Cl, Lactate, Hb, SaO2
        กฎ: 
        1. ถ้าหาค่าไหนไม่เจอให้ใส่เป็น null
        2. เอาเฉพาะตัวเลขที่เป็นผลลัพธ์ (ไม่ต้องเอาหน่วย)
        3. ตอบเฉพาะ JSON เท่านั้น ห้ามมีคำอธิบายอื่น
        """

        response = model.generate_content([prompt, img])
        
        # ทำความสะอาดข้อความ เผื่อ AI ตอบมามี ```json ... ```
        clean_text = re.search(r'\{.*\}', response.text, re.DOTALL).group()
        data = json.loads(clean_text)
        
        return data
    except Exception as e:
        print(f"Error in OCR: {e}")
        return {}
