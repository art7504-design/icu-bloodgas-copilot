import streamlit as st
from image_processing import extract_data_from_image
from calculations import calculate_clinical_indices
from ai_consultant import get_ai_consultation, chat_with_gemini

# --- 1. ตั้งค่าหน้าเว็บให้เรียบหรู (เอาไอคอน 🏥 แบบเดิมออก เปลี่ยนเป็นสัญลักษณ์ทางการแพทย์ 🩺) ---
st.set_page_config(page_title="ICU Blood Gas Copilot", page_icon="🩺", layout="wide")

# --- 2. Custom CSS สำหรับปรับโทนสีพื้นหลังและส่วนประกอบทั้งหมด (ธีม Clinical High-Tech) ---
st.markdown("""
    <style>
        /* ปรับพื้นหลังหลักของแอปให้เป็นโทน Dark Slate เพื่ออ่านง่ายในห้อง ICU และลดแสงสะท้อน */
        .stApp {
            background-color: #0F172A;
        }
        
        /* ปรับแต่งสีฟอนต์ทั่วไปและข้อความให้อ่านง่าย มี Contrast สูง */
        p, span, label, .stMarkdown {
            color: #E2E8F0 !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        
        /* ปรับแต่งกล่อง Input Text / Number ให้กลืนไปกับธีมและดูทันสมัย */
        .stTextInput>div>div>input, .stNumberInput>div>div>input, .stTextArea>div>div>textarea {
            background-color: #1E293B !important;
            color: #F8FAFC !important;
            border: 1px solid #334155 !important;
            border-radius: 6px !important;
        }
        
        /* ปรับแต่งปุ่มกด (Buttons) ให้ดูเรียบหรู ไฮเทคแบบ Minimal */
        .stButton>button {
            background-color: #2563EB !important;
            color: #FFFFFF !important;
            border-radius: 6px !important;
            border: none !important;
            font-weight: 600 !important;
            padding: 0.5rem 1.5rem !important;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
        }
        .stButton>button:hover {
            background-color: #1D4ED8 !important;
            box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.4);
            border: none !important;
        }
        
        /* ปรับแต่งกล่องสรุปคำแนะนำ (st.info, st.success) */
        .stAlert {
            background-color: #1E293B !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
        }
        
        /* ปรับแต่งเส้นคั่นโครงสร้างแอป */
        hr {
            border-color: #334155 !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. ส่วนหัวข้อหลักแบบ High-Tech Title (ไม่มีไอคอนเด็กๆ) ---
st.markdown("""
    <h1 style='text-align: left; color: #F8FAFC; font-family: -apple-system, BlinkMacSystemFont, sans-serif; font-weight: 700; letter-spacing: -0.5px; margin-bottom: 2px;'>
        ICU Blood Gas <span style='color: #3B82F6;'>Copilot</span>
    </h1>
    <p style='color: #64748B; font-size: 0.95rem; margin-top: 0px;'>Clinical Decision Support System for Arterial Blood Gas Analysis</p>
""", unsafe_allow_html=True)

st.markdown("---")

# --- จัดการสถานะข้อมูล (Session State) ---
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = {}
if 'consultation_result' not in st.session_state:
    st.session_state.consultation_result = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# --- ส่วนอัปโหลดรูปภาพ ---
uploaded_file = st.file_uploader("📸 Upload ABG Slip / Image File", type=['jpg', 'png', 'jpeg'])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", width=300)
    
    if st.button("🔍 SCAN IMAGE"):
        with st.spinner('AI กำลังอ่านตัวเลขจากสลิป...'):
            result = extract_data_from_image(uploaded_file)
            
            if result and "Error" not in result:
                st.session_state.extracted_data = result
                st.success("อ่านข้อมูลสำเร็จ! โปรดตรวจสอบความถูกต้องด้านล่าง")
            else:
                error_msg = result.get("Message", "ไม่สามารถอ่านข้อมูลได้ หรือโควต้าเต็ม")
                st.error(f"❌ {error_msg}")

# --- ปรับหัวข้ออินพุตข้อมูลแล็บให้ดูเป็นทางการ ---
st.markdown("<h4 style='color: #94A3B8; margin-top: 20px; font-weight: 600;'>PATIENT ABG DATA</h4>", unsafe_allow_html=True)
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

# --- ส่วนข้อมูลเพิ่มเติม (ปรับดีไซน์หัวข้อ) ---
st.markdown("<h4 style='color: #94A3B8; font-weight: 600;'>VENTILATOR & CLINICAL METRICS</h4>", unsafe_allow_html=True)
ca, cb, cc = st.columns(3)
with ca:
    age = st.text_input("Age (ปี)", value="")
    fio2 = st.number_input("FiO2 (%)", min_value=21, max_value=100, value=21)
    temp = st.text_input("Temperature (°C)", value="37.0")
with cb:
    mode = st.text_input("Ventilator Mode", placeholder="e.g., PCV, PSV...")
    peep = st.text_input("PEEP", value="5")
with cc:
    rr = st.text_input("Resp. Rate (RR)", value="")
    tv = st.text_input("Tidal Volume (TV)", value="")

patient_info = st.text_area("Patient History / Clinical Note", placeholder="ระบุประวัติ อาการสำคัญ หรือข้อมูลเพิ่มเติมทางคลินิก...")

# --- รวบรวมข้อมูลทั้งหมดเพื่อใช้ส่งต่อ (ไม่มีการเปลี่ยนโครงสร้างตัวแปร) ---
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
# 🧮 ส่วนคำนวณดัชนีทางคลินิก (คงสไตล์เดิม ไม่ยุ่งเกี่ยวกับสูตรตัวเลข)
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
# 🚀 ปุ่มเรียกใช้ AI วิเคราะห์ผล
# ==========================================
if st.button("🚀 RUN CLINICAL AI ANALYSIS"):
    full_data["Calculated_PF"] = calc_results.get("PF_Ratio")
    full_data["Calculated_Aa"] = calc_results.get("Aa_Gradient")
    
    with st.spinner('AI กำลังวิเคราะห์ข้อมูลร่วมกับผลคำนวณ...'):
        advice = get_ai_consultation(full_data)
        st.session_state.consultation_result = advice
        st.session_state.chat_history = [] 
        st.rerun()

# ==========================================
# 💬 ส่วนแผงควบคุมแชทและการแสดงผลลัพธ์ (สไตล์โมเดิร์น ไร้อีโมจิเด็ก)
# ==========================================
if st.session_state.consultation_result:
    st.markdown("<h4 style='color: #3B82F6; font-weight: 600;'>AI CLINICAL CONSULTATION</h4>", unsafe_allow_html=True)
    st.info(st.session_state.consultation_result)
    
    st.markdown("---")
    st.markdown("<h4 style='color: #94A3B8; font-weight: 600;'>INTERACTIVE CASE COPILOT</h4>", unsafe_allow_html=True)
    
    # แสดงประวัติแชทเก่า
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ช่องรับคำถามใหม่
    if prompt := st.chat_input("พิมพ์คำถามทางคลินิกเพิ่มเติมเกี่ยวกับเคสนี้..."):
        
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        context_str = f"ข้อมูลคนไข้ทั้งหมด: {full_data}\nคำแนะนำเริ่มต้นที่ AI ให้ไปแล้ว: {st.session_state.consultation_result}"

        with st.chat_message("assistant"):
            with st.spinner("กำลังประมวลผลคำตอบ..."):
                response = chat_with_gemini(context_str, st.session_state.chat_history)
                st.markdown(response)
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
