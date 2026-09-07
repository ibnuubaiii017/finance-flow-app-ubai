import pytesseract
import re
from PIL import Image
import os

# Hanya set path jika di Windows lokal
if os.name == 'nt':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def parse_receipt_image(image_bytes):
    try:
        image = Image.open(image_bytes)
        raw_text = pytesseract.image_to_string(image)
        
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
        return {
            'amount': 0.0,
            'raw_text': f"Gagal membaca struk: {str(e)}"
        }

def parse_quick_text(text):
    try:
        numbers = re.findall(r'\d+', text.replace('.', '').replace(',', ''))
        amount = float(numbers[0]) if numbers else 0.0
        merchant = re.sub(r'\d+[kKbBmM]?', '', text).strip()
        
        if 'k' in text.lower() or 'rb' in text.lower():
            if amount < 1000:
                amount *= 1000
                
        return {
            'amount': amount,
            'merchant': merchant if merchant else "Transaksi Cepat"
        }
    except Exception:
        return {
            'amount': 0.0,
            'merchant': text
        }