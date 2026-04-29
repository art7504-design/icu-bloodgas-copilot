# image_processing.py

def extract_data_from_image(image_file):
    """
    ฟังก์ชันสำหรับรับรูปภาพมาทำ OCR และ Augmentation
    ตอนนี้จะ Return ค่าสมมติ (Dummy Data) กลับไปก่อนเพื่อทดสอบ UI
    """
    # โครงสร้าง Data Payload ที่ดึงได้จาก OCR
    dummy_data = {
        "PaO2": 148.0,
        "PaCO2": 40.0,
        "pH": 7.40,
        "SaO2": 99.2,
        "Hb": 8.9,
    }
    return dummy_data