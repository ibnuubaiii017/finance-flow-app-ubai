import pytesseract
import re
from PIL import Image
import os

# Set path Tesseract cuma kalau lagi dijalankan di Windows lokal
if os.name == 'nt':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def parse_receipt_image(image_bytes):
    try:
        image = Image.open(image_bytes)
        raw_text = pytesseract.image_to_string(image)
        
        # Cari nominal angka terbesar dari hasil scan
        amounts = re.findall(r'(?:TOTAL|BAYAR|RP)?\s*[:.]?\s*([\d.,]{4,})', raw_text, re.IGNORECASE)
        cleaned_amounts = []
        for a in amounts:
            clean = a.replace('.', '').replace(',', '')
            if clean.isdigit():
                cleaned_amounts.append(float(clean))
                
        detected_amount = max(cleaned_amounts) if cleaned_amounts else 0.0
        
        return {
            'amount': detected_amount,
            'raw_text': raw_text
        }
    except Exception as e:
        # Jika engine OCR di server cloud belum siap, return 0 tanpa bikin app crash
        return {
            'amount': 0.0,
            'raw_text': f"Gagal membaca struk: {str(e)}"
        }