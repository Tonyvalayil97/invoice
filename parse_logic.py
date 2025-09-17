# parse_logic.py
import io, os, re, traceback
from datetime import datetime
from typing import Optional, Dict
import pdfplumber

HEADERS = [
    "Timestamp", "Filename", "Reference",
    "Commercial_Value", "GST_HST", "Duties", "Broker_Fee"
]

def parse_invoice_pdf_bytes(pdf_bytes: bytes, filename: str = "upload.pdf") -> Optional[Dict]:
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            pg1_text = pdf.pages[0].extract_text() or ""

            # Reference number (starts with 13…)
            ref = None
            for pat in (
                r"Reference:\s*(13[\d-]+)",
                r"Customs Transaction:\s*(13[\d-]+)",
                r"Cargo Control Number:\s*(13[\d-]+)"
            ):
                m = re.search(pat, pg1_text)
                if m:
                    ref = m.group(1)
                    break

            # Broker Fee (Amount Due CAD … on page 1)
            fee = None
            mfee = re.search(r"Amount\s+Due\s*:?\s*CAD\s*([\d,]+\.\d{2})", pg1_text)
            if mfee:
                fee = float(mfee.group(1).replace(",", ""))

            # Search all pages for Commercial Value, Duties, GST
            val = gst = dut = None
            for page in pdf.pages:
                txt = page.extract_text() or ""
                if val is None:
                    m = re.search(r"Value for Fee \(CDN\):\s*([\d,]+\.\d{2})", txt)
                    if m: val = float(m.group(1).replace(",", ""))
                if gst is None or dut is None:
                    m1 = re.search(r"Duties\s*=\s*\$([\d,]+\.\d{2})", txt)
                    m2 = re.search(r"GST\s*=\s*\$([\d,]+\.\d{2})", txt)
                    if m1: dut = float(m1.group(1).replace(",", ""))
                    if m2: gst = float(m2.group(1).replace(",", ""))
                if all(v is not None for v in (ref, val, gst, dut, fee)):
                    break

        return {
            "Timestamp":        datetime.now(),
            "Filename":         os.path.basename(filename),
            "Reference":        ref,
            "Commercial_Value": val,
            "GST_HST":          gst,
            "Duties":           dut,
            "Broker_Fee":       fee,
        }
    except Exception:
        traceback.print_exc()
        return None
