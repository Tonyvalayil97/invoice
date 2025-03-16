import streamlit as st
import pandas as pd
import requests
import PyPDF2
from io import BytesIO

# Function to extract data from a PDF invoice
def extract_invoice_data(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # Example parsing logic (customize based on your invoice format)
        shipper = "Unknown"
        weight = "Unknown"
        volume = "Unknown"
        final_amount = "Unknown"
        invoice_number = "Unknown"

        # Add your parsing logic here
        if "Shipper:" in text:
            shipper = text.split("Shipper:")[1].split("\n")[0].strip()
        if "Invoice Number:" in text:
            invoice_number = text.split("Invoice Number:")[1].split("\n")[0].strip()
        if "Weight:" in text:
            weight = text.split("Weight:")[1].split("\n")[0].strip()
        if "Volume:" in text:
            volume = text.split("Volume:")[1].split("\n")[0].strip()
        if "Total Amount:" in text:
            final_amount = text.split("Total Amount:")[1].split("\n")[0].strip()

        return {
            "Shipper": shipper,
            "Weight": weight,
            "Volume": volume,
            "Final Amount": final_amount,
            "Invoice Number": invoice_number,
        }
    except PyPDF2.errors.PdfReadError:
        st.error("The uploaded file is not a valid PDF or is corrupted.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
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
