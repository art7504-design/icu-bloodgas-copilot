# calculations.py

def calculate_clinical_metrics(ocr_data, manual_inputs):
    """
    ฟังก์ชันคำนวณค่าทางสรีรวิทยา พร้อมระบบดักจับตัวแปรที่ขาดหาย (Dependency Tracking)
    """
    results = {}
    
    # ฟังก์ชันช่วยดึงค่าตัวเลข (แปลงเป็น float ถ้ามีค่า)
    def get_val(data_dict, key):
        try:
            val = data_dict.get(key)
            if val is not None and str(val).strip() != "":
                return float(val)
            return None
        except ValueError:
            return None

    # ดึงตัวแปรทั้งหมดมาเตรียมไว้
    PaO2 = get_val(ocr_data, "PaO2")
    PaCO2 = get_val(ocr_data, "PaCO2")
    SaO2 = get_val(ocr_data, "SaO2")
    Hb = get_val(ocr_data, "Hb")
    
    Age = get_val(manual_inputs, "Age")
    FiO2 = get_val(manual_inputs, "FiO2")
    mPaw = get_val(manual_inputs, "mPaw")
    SvO2 = get_val(manual_inputs, "SvO2")
    PvO2 = get_val(manual_inputs, "PvO2")

    # --- 1. หมวด Oxygenation & Alveolar ---
    
    # PF Ratio
    if PaO2 is not None and FiO2 is not None and FiO2 > 0:
        results["PF_Ratio"] = {"value": round(PaO2 / FiO2, 1), "missing": None}
    else:
        results["PF_Ratio"] = {"value": None, "missing": "PaO2, FiO2"}

    # PAO2 (Alveolar O2)
    PAO2 = None
    if FiO2 is not None and PaCO2 is not None:
        PAO2 = (FiO2 * (760 - 47)) - (PaCO2 / 0.8)
        results["PAO2"] = {"value": round(PAO2, 1), "missing": None}
    else:
        results["PAO2"] = {"value": None, "missing": "FiO2, PaCO2"}

    # A-a Gradient
    if PAO2 is not None and PaO2 is not None:
        results["Aa_Gradient"] = {"value": round(PAO2 - PaO2, 1), "missing": None}
    else:
        results["Aa_Gradient"] = {"value": None, "missing": "PaO2, FiO2, PaCO2"}

    # Oxygenation Index (OI)
    if mPaw is not None and FiO2 is not None and PaO2 is not None and PaO2 > 0:
        results["OI"] = {"value": round((mPaw * FiO2 * 100) / PaO2, 1), "missing": None}
    else:
        results["OI"] = {"value": None, "missing": "mPaw, FiO2, PaO2"}

    # --- 2. หมวด Oxygen Content & Extraction ---
    
    CaO2 = None
    if Hb is not None and SaO2 is not None and PaO2 is not None:
        CaO2 = (1.34 * Hb * (SaO2 / 100)) + (0.0031 * PaO2)
        results["CaO2"] = {"value": round(CaO2, 2), "missing": None}
    else:
        results["CaO2"] = {"value": None, "missing": "Hb, SaO2, PaO2"}

    CvO2 = None
    if Hb is not None and SvO2 is not None and PvO2 is not None:
        CvO2 = (1.34 * Hb * (SvO2 / 100)) + (0.0031 * PvO2)
        results["CvO2"] = {"value": round(CvO2, 2), "missing": None}
    else:
        results["CvO2"] = {"value": None, "missing": "Hb, SvO2, PvO2"}
    
    # --- 3. หมวด การประเมิน Shunt (Qs/Qt) ---
    # Estimated Shunt (Simple Formula: A-a gradient / 20)
    if results.get("Aa_Gradient") and results["Aa_Gradient"]["value"] is not None:
        results["Shunt_Simple"] = {"value": round(results["Aa_Gradient"]["value"] / 20, 2), "missing": None}
    else:
        results["Shunt_Simple"] = {"value": None, "missing": "A-a Gradient"}

    # V/Q Index (100 - SaO2) / (100 - SvO2)
    if SaO2 is not None and SvO2 is not None and (100 - SvO2) != 0:
        results["VQ_Index"] = {"value": round((100 - SaO2) / (100 - SvO2), 2), "missing": None}
    else:
        results["VQ_Index"] = {"value": None, "missing": "SaO2, SvO2"}

    # --- 4. หมวด Expected Values (ตามอายุ) ---
    if Age is not None:
        results["Expected_PaO2"] = {"value": round(102 - (0.3 * Age), 1), "missing": None}
        results["Expected_Aa"] = {"value": round((Age / 4) + 4, 1), "missing": None}
    else:
        results["Expected_PaO2"] = {"value": None, "missing": "Age"}
        results["Expected_Aa"] = {"value": None, "missing": "Age"}

    return results