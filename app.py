import streamlit as st
import pandas as pd
import requests
import PyPDF2
from io import BytesIO

# Function to download a PDF from a URL
def download_pdf_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        st.error(f"Failed to download PDF from {url}. Status code: {response.status_code}")
        return None

# Function to extract data from a PDF invoice
def extract_invoice_data(pdf_file):
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
    # Example: Extract shipper name if the text contains "Shipper:"
    if "Shipper:" in text:
        shipper = text.split("Shipper:")[1].split("\n")[0].strip()

    # Example: Extract invoice number if the text contains "Invoice Number:"
    if "Invoice Number:" in text:
        invoice_number = text.split("Invoice Number:")[1].split("\n")[0].strip()

    # Example: Extract weight if the text contains "Weight:"
    if "Weight:" in text:
        weight = text.split("Weight:")[1].split("\n")[0].strip()

    # Example: Extract volume if the text contains "Volume:"
    if "Volume:" in text:
        volume = text.split("Volume:")[1].split("\n")[0].strip()

    # Example: Extract final amount if the text contains "Total Amount:"
    if "Total Amount:" in text:
        final_amount = text.split("Total Amount:")[1].split("\n")[0].strip()

    return {
        "Shipper": shipper,
        "Weight": weight,
        "Volume": volume,
        "Final Amount": final_amount,
        "Invoice Number": invoice_number,
    }

# Streamlit app
def main():
    st.title("Invoice Data Extractor")
    st.write("Upload PDFs via links to extract data and download the results as an Excel file.")

    # Input for PDF links
    pdf_links = st.text_area("Enter PDF links (one per line):")

    if st.button("Extract Data"):
        if pdf_links:
            links = pdf_links.split("\n")
            data = []

            for link in links:
                link = link.strip()
                if link:
                    st.write(f"Processing: {link}")
                    pdf_file = download_pdf_from_url(link)
                    if pdf_file:
                        extracted_data = extract_invoice_data(pdf_file)
                        data.append(extracted_data)

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
                st.warning("No data extracted. Please check the PDF links and content.")
        else:
            st.warning("Please enter at least one PDF link.")

# Run the app
if __name__ == "__main__":
    main()
