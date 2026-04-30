import streamlit as st
from image_processing import extract_data_from_image

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="ICU Blood Gas Copilot", page_icon="🏥", layout="wide")

# --- จัดการสถานะข้อมูล (Session State) ---
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = {}
if 'consultation_result' not in st.session_state:
    st.session_state.consultation_result = ""

st.title("🏥 ICU Blood Gas Copilot")
st.markdown("---")

# --- ส่วนอัปโหลดรูปภาพ ---
uploaded_file = st.file_uploader("📸 ถ่ายรูปสลิป / เลือกไฟล์จากเครื่อง...", type=['jpg', 'png', 'jpeg'])

if uploaded_file is not None:
    st.image(uploaded_file, caption="รูปที่อัปโหลด", width=300)
    
    if st.button("🔍 รับข้อมูลจากรูปภาพ"):
        with st.spinner('AI กำลังอ่านตัวเลขจากสลิป...'):
            result = extract_data_from_image(uploaded_file)
            
            if result and "Error" not in result:
                st.session_state.extracted_data = result
                st.success("อ่านข้อมูลสำเร็จ! โปรดตรวจสอบความถูกต้องด้านล่าง")
            else:
                error_msg = result.get("Message", "ไม่สามารถอ่านข้อมูลได้ หรือโควต้าเต็ม")
                st.error(f"❌ {error_msg}")

# --- ลดขนาดหัวข้อลงโดยใช้ ### ---
st.markdown("#### 🩸 ข้อมูลจากสลิป (ตรวจสอบความถูกต้อง สามารถแก้ไขได้)")
data = st.session_state.extracted_data

# --- ส่วนแสดงช่องกรอกข้อมูล (3 คอลัมน์) ---
col1, col2, col3 = st.columns(3)

with col1:
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

# --- ส่วนข้อมูลเพิ่มเติม (ลดขนาดหัวข้อ และเพิ่มช่อง Age) ---
st.markdown("#### 📝 ข้อมูลผู้ป่วยและเครื่องช่วยหายใจเพิ่มเติม")
ca, cb, cc = st.columns(3)
with ca:
    age = st.text_input("Age (ปี)", value="") # เพิ่มช่องกรอกอายุ
    fio2 = st.number_input("FiO2 (%)", min_value=21, max_value=100, value=21)
    temp = st.text_input("Temperature (°C)", value="37.0")
with cb:
    mode = st.text_input("Ventilator Mode", placeholder="เช่น PCV, PSV...")
    peep = st.text_input("PEEP", value="5")
with cc:
    rr = st.text_input("Resp. Rate (RR)", value="")
    tv = st.text_input("Tidal Volume (TV)", value="")

patient_info = st.text_area("ประวัติสำคัญ / อาการเบื้องต้น", placeholder="ระบุประวัติหรืออาการเพิ่มเติมที่นี่...")

# --- ปุ่มวิเคราะห์ ---
if st.button("🚀 วิเคราะห์ผลและขอคำแนะนำ"):
    st.info("ระบบวิเคราะห์จะพร้อมใช้งานเมื่อเชื่อมต่อไฟล์ ai_consultant สำเร็จ")

if st.session_state.consultation_result:
    st.markdown("#### 🤖 คำแนะนำ")
    st.info(st.session_state.consultation_result)
