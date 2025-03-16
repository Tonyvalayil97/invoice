import streamlit as st
import pandas as pd
import requests
import pdfplumber
from io import BytesIO

# Function to extract data from a PDF invoice
def extract_invoice_data(pdf_file):
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()

        # Debug: Print the extracted text
        st.write("Extracted Text:")
        st.write(text)

        # Initialize variables
        shipper = "Unknown"
        weight = "Unknown"
        volume = "Unknown"
        final_amount = "Unknown"
        invoice_number = "Unknown"

        # Extract Shipper
        if "SHIPPER" in text:
            shipper_section = text.split("SHIPPER")[1].split("\n")[0].strip()
            shipper = shipper_section.split("CONSIGNEE")[0].strip()

        # Extract Invoice Number
        if "INVOICE -" in text:
            invoice_number = text.split("INVOICE -")[1].split("\n")[0].strip()

        # Extract Weight
        if "WEIGHT" in text:
            weight_section = text.split("WEIGHT")[1].split("\n")[0].strip()
            weight = weight_section.split("KG")[0].strip()

        # Extract Volume
        if "VOLUME" in text:
            volume_section = text.split("VOLUME")[1].split("\n")[0].strip()
            volume = volume_section.split("M3")[0].strip()

        # Extract Final Amount
        if "TOTAL CHARGES" in text:
            final_amount_section = text.split("TOTAL CHARGES")[1].split("\n")[0].strip()
            final_amount = final_amount_section.split("USD")[0].strip()

        return {
            "Shipper": shipper,
            "Weight": weight,
            "Volume": volume,
            "Final Amount": final_amount,
            "Invoice Number": invoice_number,
        }
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

# Streamlit app
def main():
    st.title("Invoice Data Extractor")
    st.write("Upload PDFs from your local folder or via links to extract data and download the results as an Excel file.")

    # Option to upload local files
    uploaded_files = st.file_uploader("Upload PDF files from your local folder", type="pdf", accept_multiple_files=True)

    # Option to enter PDF links
    pdf_links = st.text_area("Alternatively, enter PDF links (one per line):")

    if st.button("Extract Data"):
        data = []

        # Process uploaded local files
        if uploaded_files:
            for uploaded_file in uploaded_files:
                st.write(f"Processing: {uploaded_file.name}")
                extracted_data = extract_invoice_data(uploaded_file)
                if extracted_data:
                    data.append(extracted_data)

        # Process PDF links
        if pdf_links:
            links = pdf_links.split("\n")
            for link in links:
                link = link.strip()
                if link:
                    st.write(f"Processing: {link}")
                    response = requests.get(link)
                    if response.status_code == 200:
                        pdf_file = BytesIO(response.content)
                        extracted_data = extract_invoice_data(pdf_file)
                        if extracted_data:
                            data.append(extracted_data)
                    else:
                        st.error(f"Failed to download PDF from {link}. Status code: {response.status_code}")

        if data:
            # Create a DataFrame
            df = pd.DataFrame(data)

            # Save DataFrame to Excel
            excel_file = BytesIO()
            with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Invoices")
            excel_file.seek(0)

            # Provide download link for the Excel file
            st.success("Data extraction complete!")
            st.download_button(
                label="Download Excel File",
                data=excel_file,
                file_name="extracted_invoice_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.warning("No data extracted. Please check the uploaded files or links.")

# Run the app
if __name__ == "__main__":
    main()
