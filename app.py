import streamlit as st
import pandas as pd
import pytesseract
from pdf2image import convert_from_path
from io import BytesIO

# Function to extract data from PDF using OCR (via Tesseract)
def extract_invoice_data(pdf_file):
    try:
        # Convert PDF to images (each page will be an image)
        images = convert_from_path(pdf_file)

        # Extract text from all pages using OCR
        full_text = ""
        for page_num, image in enumerate(images):
            text = pytesseract.image_to_string(image)
            full_text += text

        st.write("Extracted Text (OCR):")
        st.write(full_text)  # Output the extracted text for debugging

        # Now extract the needed information from the full text
        shipper = "E-TEEN COMPANY LIMITED" if "E-TEEN COMPANY LIMITED" in full_text else "Unknown"
        weight = extract_from_text(full_text, "WEIGHT", "KG")
        volume = extract_from_text(full_text, "VOLUME", "M3")
        order_numbers = extract_from_text(full_text, "ORDER NUMBERS / OWNER'S REFERENCE", "\n")
        packages = extract_from_text(full_text, "PACKAGES", "CTN")
        containers = extract_from_text(full_text, "CONTAINERS", "\n")

        # Return the extracted data in a dictionary
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

# Helper function to extract text between two labels
def extract_from_text(text, start_label, end_label):
    try:
        return text.split(start_label)[1].split(end_label)[0].strip()
    except IndexError:
        return "Unknown"

# Main application function
def main():
    st.title("Invoice Data Extractor (Using OCR)")
    st.write("Upload PDF to extract data using Optical Character Recognition (OCR).")

    # Option to upload local files
    uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

    if st.button("Extract Data"):
        data = []

        # Process uploaded local files
        if uploaded_files:
            for uploaded_file in uploaded_files:
                st.write(f"Processing: {uploaded_file.name}")
                extracted_data = extract_invoice_data(uploaded_file)
                if extracted_data:
                    data.append(extracted_data)

        # Show data and export to Excel if data extraction was successful
        if data:
            df = pd.DataFrame(data)

            # Save DataFrame to an Excel file
            excel_file = BytesIO()
            with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Invoices")
            excel_file.seek(0)

            # Provide a download button for the Excel file
            st.success("Data extraction complete!")
            st.download_button(
                label="Download Excel File",
                data=excel_file,
                file_name="extracted_invoice_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.warning("No data extracted. Please check the uploaded files.")

# Entry point for the application
if __name__ == "__main__":
    main()

