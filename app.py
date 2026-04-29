# app.py
import streamlit as st
from image_processing import extract_data_from_image
from calculations import calculate_clinical_metrics
from ai_consultant import get_initial_report, get_chat_response

st.set_page_config(page_title="ICU Blood Gas Copilot", page_icon="🏥", layout="centered")

# --- การตกแต่ง UI ด้วย CSS (Modern Teal & Sage) ---
st.markdown("""
    <style>
    /* สีพื้นหลังกล่องข้อมูล */
    .stTextInput input, .stNumberInput input {
        background-color: #f0f4f8;
        border-radius: 8px;
        border: 1px solid #d1e3ea;
    }
    /* สีของปุ่มหลัก */
    .stButton>button {
        background-color: #005f73;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0a9396;
        color: white;
    }
    /* สีกรอบและเงาของแชท/รายงาน */
    .report-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #94d2bd;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# --- State Management (ตัวแปรความจำของหน้าเว็บ) ---
if "ocr_data" not in st.session_state:
    st.session_state.ocr_data = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "report_generated" not in st.session_state:
    st.session_state.report_generated = False

# --- โซนที่ 1: Header & Input ---
st.markdown("<h2 style='color: #005f73;'>🏥 ICU Blood Gas Copilot</h2>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("📷 ถ่ายรูปสลิป / เลือกไฟล์จากเครื่อง...", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None and not st.session_state.report_generated:
    with st.spinner("กำลังใช้ AI อ่านข้อมูลจากภาพ..."):
        # เรียกใช้ฟังก์ชันที่แก้ใหม่
        extracted = extract_data_from_image(uploaded_file)
        if extracted:
            st.session_state.ocr_data = extracted
            st.success("อ่านข้อมูลสำเร็จ! โปรดตรวจสอบความถูกต้องด้านล่าง")
        else:
            st.error("ไม่สามารถอ่านข้อมูลจากภาพได้ กรุณาลองอัปโหลดภาพที่ชัดเจนขึ้น")

if st.session_state.ocr_data:
    st.markdown("---")
    # --- โซนที่ 2: Data Validation Grid ---
    st.markdown("##### 🩸 ข้อมูลจากสลิป (ตรวจสอบและแก้ไขได้)")
    
    col1, col2, col3 = st.columns(3)
    ocr = st.session_state.ocr_data
    
    with col1:
        ocr["pH"] = st.text_input("pH", value=str(ocr.get("pH", "")))
        ocr["Na"] = st.text_input("Na+", value=str(ocr.get("Na", "")))
        ocr["Hb"] = st.text_input("Hb", value=str(ocr.get("Hb", "")))
    with col2:
        ocr["PaCO2"] = st.text_input("PaCO2", value=str(ocr.get("PaCO2", "")))
        ocr["K"] = st.text_input("K+", value=str(ocr.get("K", "")))
        ocr["SaO2"] = st.text_input("SaO2", value=str(ocr.get("SaO2", "")))
    with col3:
        ocr["PaO2"] = st.text_input("PaO2", value=str(ocr.get("PaO2", "")))
        ocr["Cl"] = st.text_input("Cl-", value=str(ocr.get("Cl", "")))
        ocr["Lactate"] = st.text_input("Lactate", value=str(ocr.get("Lactate", "")))
        
    st.markdown("##### 📝 ข้อมูลผู้ป่วย / เครื่องช่วยหายใจ (กรอกเพิ่ม)")
    col4, col5 = st.columns(2)
    with col4:
        manual_age = st.text_input("📝 Age (อายุ)")
        manual_fio2 = st.text_input("📝 FiO2 (เช่น 0.21)")
    with col5:
        manual_mpaw = st.text_input("📝 mPaw")
        manual_svo2 = st.text_input("📝 SvO2")
        manual_pvo2 = st.text_input("📝 PvO2")

    manual_inputs = {"Age": manual_age, "FiO2": manual_fio2, "mPaw": manual_mpaw, "SvO2": manual_svo2, "PvO2": manual_pvo2}

    # --- ปุ่มสั่งการ ---
    if st.button("🧮 ประมวลผลและวิเคราะห์ข้อมูล", use_container_width=True):
        st.session_state.calc_results = calculate_clinical_metrics(st.session_state.ocr_data, manual_inputs)
        st.session_state.report_generated = True
        
        # ให้ AI สรุปผลครั้งแรกและเก็บลงแชท
        initial_report = get_initial_report(st.session_state.ocr_data, st.session_state.calc_results)
        st.session_state.chat_history = [{"role": "assistant", "content": initial_report}]
        st.rerun() # รีเฟรชหน้าจอเพื่อแสดงผล

# --- โซนที่ 3 & 4: แสดงผลการคำนวณ & ระบบ Chat ---
if st.session_state.report_generated:
    st.markdown("---")
    st.markdown("### 📈 ผลการประเมินทางคลินิก")
    
    res = st.session_state.calc_results
    
    # ฟังก์ชันช่วยแสดงผลบนจอ (เช็คว่ามีค่า หรือแจ้งเตือนว่าขาดอะไร)
    def display_metric(label, key):
        data = res.get(key, {})
        val = data.get("value")
        missing = data.get("missing")
        if val is not None:
            return f"**{label}:** `{val}`"
        else:
            return f"**{label}:** ⚠️ *(ขาดค่า {missing})*"

    st.markdown("##### ☁️ 1. Oxygenation & Alveolar")
    st.write(display_metric("PF Ratio", "PF_Ratio"))
    st.write(display_metric("A-a Gradient", "Aa_Gradient"))
    st.write(display_metric("Oxygenation Index", "OI"))
    
    st.markdown("##### 🩸 2. Oxygen Content")
    st.write(display_metric("Arterial O2 (CaO2)", "CaO2"))
    st.write(display_metric("Venous O2 (CvO2)", "CvO2"))

    st.markdown("##### 🫀 3. การประเมิน Shunt (Qs/Qt)")
    st.write(display_metric("Estimated Shunt (Simple %)", "Shunt_Simple"))
    st.write(display_metric("V/Q Index", "VQ_Index"))

    st.markdown("##### 👤 4. ค่าคาดคะเนตามอายุ (Expected Values)")
    st.write(display_metric("Expected PaO2", "Expected_PaO2"))
    st.write(display_metric("Expected A-a Gradient", "Expected_Aa"))

    st.markdown("---")
    st.markdown("<h3 style='color: #005f73;'>🤖 AI Clinical Consultation & Chat</h3>", unsafe_allow_html=True)
    
    # แสดงประวัติการแชททั้งหมด
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👨‍⚕️"):
            st.markdown(f"<div class='report-box'>{msg['content']}</div>", unsafe_allow_html=True)

    # ช่องพิมพ์ข้อความคุยกับ AI ด้านล่างสุด
    if prompt := st.chat_input("พิมพ์คำถามเพิ่มเติมที่นี่... (เช่น แนะนำการปรับ FiO2)"):
        # แสดงข้อความที่หมอพิมพ์
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👨‍⚕️"):
            st.markdown(prompt)
            
        # ส่งข้อความไปหา Gemini และรับคำตอบ
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("AI กำลังวิเคราะห์..."):
                reply = get_chat_response(st.session_state.chat_history[:-1], prompt)
                st.markdown(f"<div class='report-box'>{reply}</div>", unsafe_allow_html=True)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
