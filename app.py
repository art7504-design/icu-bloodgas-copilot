import streamlit as st
from image_processing import extract_data_from_image
from calculations import calculate_clinical_indices
from ai_consultant import get_ai_consultation, chat_with_gemini # <-- เพิ่ม chat_with_gemini

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="ICU Blood Gas Copilot", page_icon="🏥", layout="wide")

# --- จัดการสถานะข้อมูล (Session State) ---
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = {}
if 'consultation_result' not in st.session_state:
    st.session_state.consultation_result = ""
if 'chat_history' not in st.session_state: # <-- เพิ่ม State สำหรับเก็บประวัติแชท
    st.session_state.chat_history = []

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

# --- ลดขนาดหัวข้อลงโดยใช้ #### ---
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
    age = st.text_input("Age (ปี)", value="")
    fio2 = st.number_input("FiO2 (%)", min_value=21, max_value=100, value=21)
    temp = st.text_input("Temperature (°C)", value="37.0")
with cb:
    mode = st.text_input("Ventilator Mode", placeholder="เช่น PCV, PSV...")
    peep = st.text_input("PEEP", value="5")
with cc:
    rr = st.text_input("Resp. Rate (RR)", value="")
    tv = st.text_input("Tidal Volume (TV)", value="")

patient_info = st.text_area("ประวัติสำคัญ / อาการเบื้องต้น", placeholder="ระบุประวัติหรืออาการเพิ่มเติมที่นี่...")

# --- รวบรวมข้อมูลทั้งหมด ---
full_data = {
    "pH": ph, "PaCO2": paco2, "PaO2": pao2,
    "Na": na, "K": k, "Cl": cl,
    "Hb": hb, "SaO2": sao2, "Lactate": lactate,
    "Age": age, "FiO2": fio2, "Temp": temp,
    "Mode": mode, "PEEP": peep, "RR": rr, "TV": tv,
    "History": patient_info
}

st.markdown("---")

# ==========================================
# 🧮 ค่าคำนวณทางคลินิก (Calculated Indices)
# ==========================================
st.markdown("#### 🧮 ค่าคำนวณทางคลินิก (Calculated Indices)")
st.caption("คำนวณโดยตรงจากสูตรสรีรวิทยา (อัปเดตอัตโนมัติตามข้อมูลด้านบน)")

calc_results = calculate_clinical_indices(full_data)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(label="P/F Ratio", value=calc_results.get("PF_Ratio", "N/A"), delta=calc_results.get("PF_Severity", ""), delta_color="off")
with m2:
    st.metric(label="A-a Gradient", value=calc_results.get("Aa_Gradient", "N/A"))
with m3:
    st.metric(label="Expected A-a (Age)", value=calc_results.get("Expected_Aa", "N/A"))
with m4:
    st.metric(label="CaO2 (ml/dL)", value=calc_results.get("CaO2", "N/A"))

st.markdown("---")

# ==========================================
# 🚀 วิเคราะห์ผลและขอคำแนะนำ
# ==========================================
if st.button("🚀 วิเคราะห์ผลและขอคำแนะนำ"):
    full_data["Calculated_PF"] = calc_results.get("PF_Ratio")
    full_data["Calculated_Aa"] = calc_results.get("Aa_Gradient")
    
    with st.spinner('AI กำลังวิเคราะห์ข้อมูลร่วมกับผลคำนวณ...'):
        advice = get_ai_consultation(full_data)
        st.session_state.consultation_result = advice
        st.session_state.chat_history = [] # <-- ล้างประวัติแชทเก่าทิ้ง เมื่อเริ่มเคสใหม่
        st.rerun()

# ==========================================
# 💬 ส่วนของคำแนะนำ และ CHATBOT ถาม-ตอบ
# ==========================================
if st.session_state.consultation_result:
    st.markdown("#### 🤖 สรุปคำแนะนำจาก AI")
    st.info(st.session_state.consultation_result)
    
    st.markdown("---")
    st.markdown("#### 💬 ถาม-ตอบเพิ่มเติมเกี่ยวกับเคสนี้")
    
    # 1. ลูปแสดงประวัติแชทเก่าบนหน้าจอ
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 2. ช่องรับคำถามใหม่จากผู้ใช้
    if prompt := st.chat_input("พิมพ์คำถามที่นี่ เช่น 'ขอวิธีปรับ PEEP' หรือ 'อธิบาย A-a gradient เพิ่มเติม'"):
        
        # เพิ่มคำถามของผู้ใช้ลงในประวัติและแสดงผล
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # เตรียมบริบททั้งหมดส่งให้ AI (ข้อมูลสลิป + คำแนะนำเดิม)
        context_str = f"ข้อมูลคนไข้ทั้งหมด: {full_data}\nคำแนะนำเริ่มต้นที่ AI ให้ไปแล้ว: {st.session_state.consultation_result}"

        # ส่งไปให้ AI คิดและแสดงผล
        with st.chat_message("assistant"):
            with st.spinner("กำลังพิมพ์คำตอบ..."):
                response = chat_with_gemini(context_str, st.session_state.chat_history)
                st.markdown(response)
        
        # นำคำตอบที่ได้ไปเก็บในประวัติแชท
        st.session_state.chat_history.append({"role": "assistant", "content": response})
