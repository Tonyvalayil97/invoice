import streamlit as st
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import io

# Function to extract text from PDF using OCR
def extract_invoice_data_ocr(pdf_file):
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_file)

        text = ""
        for image in images:
            text += pytesseract.image_to_string(image)

        st.write("Extracted Text (OCR):")
        st.write(text)

        # Process the text to find key values
        shipper = "E-TEEN COMPANY LIMITED" if "E-TEEN COMPANY LIMITED" in text else "Unknown"
        weight = extract_from_text(text, "WEIGHT", "KG")
        volume = extract_from_text(text, "VOLUME", "M3")
        order_numbers = extract_from_text(text, "ORDER NUMBERS / OWNER'S REFERENCE", "\n")
        packages = extract_from_text(text, "PACKAGES", "CTN")
        containers = extract_from_text(text, "CONTAINERS", "\n")

        return {
            "Shipper Name": shipper,
            "Weight": weight,
            "Volume": volume,
            "Order Numbers": order_numbers,
            "Packages": packages,
            "Containers": containers,
        }
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

def extract_from_text(text, start_label, end_label):
    try:
        return text.split(start_label)[1].split(end_label)[0].strip()
    except IndexError:
        return "Unknown"

# Run the app with OCR
if __name__ == "__main__":
    main()
