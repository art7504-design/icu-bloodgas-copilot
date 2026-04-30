# calculations.py

def safe_float(val):
    """ฟังก์ชันแปลงค่าเป็นตัวเลขอย่างปลอดภัย ถ้าแปลงไม่ได้ให้คืนค่า None"""
    try:
        if val is None or str(val).strip() == "":
            return None
        return float(val)
    except ValueError:
        return None

def calculate_clinical_indices(data):
    """
    คำนวณค่าทางคลินิกจากสูตรมาตรฐาน (จากภาพอ้างอิงของคุณหมอ)
    """
    results = {}
    
    # ดึงค่าและแปลงเป็นตัวเลข
    pao2 = safe_float(data.get("PaO2"))
    paco2 = safe_float(data.get("PaCO2"))
    fio2_percent = safe_float(data.get("FiO2"))
    age = safe_float(data.get("Age"))
    hb = safe_float(data.get("Hb"))
    sao2_percent = safe_float(data.get("SaO2"))
    
    # 1. P/F Ratio (PaO2 / FiO2)
    if pao2 is not None and fio2_percent is not None:
        fio2_decimal = fio2_percent / 100.0
        pf_ratio = pao2 / fio2_decimal
        results["PF_Ratio"] = round(pf_ratio, 2)
        
        # ประเมินความรุนแรง (ARDS criteria แบบคร่าวๆ)
        if pf_ratio <= 100: results["PF_Severity"] = "รุนแรง (Severe)"
        elif pf_ratio <= 200: results["PF_Severity"] = "ปานกลาง (Moderate)"
        elif pf_ratio <= 300: results["PF_Severity"] = "เล็กน้อย (Mild)"
        else: results["PF_Severity"] = "ปกติ"

    # 2. Alveolar-arterial O2 gradient (A-a gradient)
    if pao2 is not None and paco2 is not None and fio2_percent is not None:
        fio2_decimal = fio2_percent / 100.0
        patm = 760
        pwater = 47
        # PAO2 = (FiO2 * [Patm - Pwater]) - (PaCO2 / 0.8)
        PAO2 = (fio2_decimal * (patm - pwater)) - (paco2 / 0.8)
        aa_gradient = PAO2 - pao2
        results["Aa_Gradient"] = round(aa_gradient, 2)
        
        # Expected A-a gradient based on age: (Age/4) + 4
        if age is not None:
            expected_aa = (age / 4) + 4
            results["Expected_Aa"] = round(expected_aa, 2)

    # 3. Arterial Oxygen Content (CaO2)
    if hb is not None and sao2_percent is not None and pao2 is not None:
        sao2_decimal = sao2_percent / 100.0
        # CaO2 = (1.34 * Hb * SaO2) + (0.0031 * PaO2)
        cao2 = (1.34 * hb * sao2_decimal) + (0.0031 * pao2)
        results["CaO2"] = round(cao2, 2)

    return results
