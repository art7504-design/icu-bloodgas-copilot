import streamlit as st
from image_processing import extract_data_from_image
from calculations import calculate_abg_results  # สมมติว่ามีไฟล์คำนวณแยกไว้
from ai_consultant import get_ai_consultation  # สมมติว่ามีไฟล์ปรึกษา AI แยกไว้

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="ICU Blood Gas Copilot", page_icon="🏥", layout="wide")

# --- 2. จัดการสถานะข้อมูล (Session State) ---
# เพื่อให้ค่าที่ AI อ่านได้ไม่หายไปเมื่อหน้าเว็บรีเฟรช
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = {}
if 'consultation_result' not in st.session_state:
    st.session_state.consultation_result = ""

st.title("🏥 ICU Blood Gas Copilot")
st.markdown("---")

# --- 3. ส่วนอัปโหลดรูปภาพ ---
uploaded_file = st.file_uploader("📸 ถ่ายรูปสลิป / เลือกไฟล์จากเครื่อง...", type=['jpg', 'png', 'jpeg'])

if uploaded_file is not None:
    # แสดงรูปที่อัปโหลด
    st.image(uploaded_file, caption="รูปที่อัปโหลด", width=300)
    
    # ปุ่มกดเพื่อเริ่มอ่านค่า
    if st.button("🔍 สกัดข้อมูลจากรูปภาพ"):
        with st.spinner('AI กำลังอ่านตัวเลขจากสลิป...'):
            # เรียกใช้ฟังก์ชันจาก image_processing.py
            result = extract_data_from_image(uploaded_file)
            
            if result and "Error" not in result:
                # บันทึกข้อมูลลง Session State
                st.session_state.extracted_data = result
                st.success("อ่านข้อมูลสำเร็จ! โปรดตรวจสอบความถูกต้องด้านล่าง")
            else:
                error_msg = result.get("Message", "ไม่สามารถอ่านข้อมูลได้")
                st.error(f"❌ {error_msg}")

st.markdown("### 🩸 ข้อมูลจากสลิป (ตรวจสอบและแก้ไขได้)")

# ดึงข้อมูลจาก Session State มาแสดงในช่องกรอก
data = st.session_state.extracted_data

# --- 4. ส่วนแสดงช่องกรอกข้อมูล (แบ่งเป็น 3 คอลัมน์) ---
col1, col2, col3 = st.columns(3)

with col1:
    # value=str(...) จะดึงค่าที่ AI อ่านได้มาใส่ในช่อง ถ้าไม่มีจะว่างไว้
    ph = st.text_input("pH", value=str(data.get("pH", "")) if data.get("pH") is not None else "")
    na = st.text_input("Na+", value=str(data.get("Na", "")) if data.get("Na") is not None else "")
    hb = st.text_input("Hb", value=str(data.get("Hb", "")) if data.get("Hb") is not None else "")

with col2:
    paco2 = st.text_input("PaCO2", value=str(data.get("PaCO2", "")) if data.get("PaCO2") is not None else "")
    k = st.text_input("K+", value=str(data.get("K", "")) if data.get("K") is not None else "")
    sao2 = st.text_input("SaO2", value=str(data.get("SaO2", "")) if data.get("SaO2") is not None else "")

with col3:
    pao2 = st.text_input("PaO2", value=str(data.get("PaO2", "")) if data.get("PaO2") is not None else "")
    cl = st.text_input("Cl-", value=str(data.get("Cl", "")) if data.get("Cl") is not None else "")
    lactate = st.text_input("Lactate", value=str(data.get("Lactate", "")) if data.get("Lactate") is not None else "")

st.markdown("---")

# --- 5. ส่วนข้อมูลผู้ป่วยเพิ่มเติม ---
st.markdown("### 📝 ข้อมูลผู้ป่วย / เครื่องช่วยหายใจ (กรอกเพิ่ม)")
c1, c2 = st.columns(2)
with c1:
    fio2 = st.number_input("FiO2 (%)", min_value=21, max_value=100, value=21)
with c2:
    patient_info = st.text_area("อาการเบื้องต้น / ประวัติสำคัญ (ถ้ามี)", placeholder="เช่น ผู้ป่วยมาด้วยอาการหอบเหนื่อย...")

# --- 6. ปุ่มประมวลผลการรักษา ---
if st.button("🚀 วิเคราะห์ผลและขอคำแนะนำการปรับเครื่องช่วยหายใจ"):
    # รวบรวมข้อมูลทั้งหมด
    full_data = {
        "pH": ph, "PaCO2": paco2, "PaO2": pao2,
        "Na": na, "K": k, "Cl": cl,
        "Hb": hb, "SaO2": sao2, "Lactate": lactate,
        "FiO2": fio2, "History": patient_info
    }
    
    with st.spinner('AI กำลังวิเคราะห์ข้อมูลและสร้างคำแนะนำ...'):
        # เรียกใช้ฟังก์ชันปรึกษา AI
        advice = get_ai_consultation(full_data)
        st.session_state.consultation_result = advice

# --- 7. แสดงผลลัพธ์คำแนะนำ ---
if st.session_state.consultation_result:
    st.markdown("### 🤖 คำแนะนำจาก AI Clinical Assistant")
    st.info(st.session_state.consultation_result)
    
    # ปุ่มสำหรับล้างข้อมูลเพื่อเริ่มเคสใหม่
    if st.button("♻️ เริ่มเคสใหม่ (Clear Data)"):
        st.session_state.extracted_data = {}
        st.session_state.consultation_result = ""
        st.rerun()
