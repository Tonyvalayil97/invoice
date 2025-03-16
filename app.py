import streamlit as st
import pandas as pd
import requests
import pdfplumber
import re
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
        order_numbers = "Unknown"
        packages = "Unknown"
        containers = "Unknown"

        # Extract Shipper Name (E-TEEN COMPANY LIMITED)
        if "E-TEEN COMPANY LIMITED" in text:
            shipper = "E-TEEN COMPANY LIMITED"

        # Extract Weight
        weight_match = re.search(r"WEIGHT\s*(\d+)\s*KG", text)
        if weight_match:
            weight = weight_match.group(1)

        # Extract Volume
        volume_match = re.search(r"VOLUME\s*(\d+\.\d+)\s*M3", text)
        if volume_match:
            volume = volume_match.group(1)

        # Extract Order Numbers
        order_numbers_match = re.search(r"ORDER NUMBERS / OWNER'S REFERENCE\s*(\d+)", text)
        if order_numbers_match:
            order_numbers = order_numbers_match.group(1)

        # Extract Packages
        packages_match = re.search(r"PACKAGES\s*(\d+)\s*CTN", text)
        if packages_match:
            packages = packages_match.group(1)

        # Extract Containers
        containers_match = re.search(r"CONTAINERS\s*([A-Za-z0-9-]+)", text)
        if containers_match:
            containers = containers_match.group(1)

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
