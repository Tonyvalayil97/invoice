import streamlit as st
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

        # Split text into lines for easier parsing
        lines = text.split("\n")

        # Initialize variables
        shipper = "Unknown"
        weight = "Unknown"
        order_number = "Unknown"
        container_number = "Unknown"
        invoice_number = "Unknown"
        amount = "Unknown"

        # Function to extract the value below a specific keyword
        def extract_value_below_keyword(keyword, lines):
            for i, line in enumerate(lines):
                if keyword in line:
                    # Return the next line (value below the keyword)
                    if i + 1 < len(lines):
                        return lines[i + 1].strip()
            return "Unknown"

        # Function to extract the numeric part before a specific unit
        def extract_numeric_before_unit(value, unit):
            if unit in value:
                # Split the value by the unit and take the part before it
                part_before_unit = value.split(unit)[0].strip()
                # Remove any non-numeric characters (keep digits and decimal points)
                return ''.join(filter(lambda x: x.isdigit() or x == '.', part_before_unit))
            return value

        # Extract Shipper Name
        shipper = extract_value_below_keyword("SHIPPER", lines)

        # Extract Order Number
        order_number = extract_value_below_keyword("ORDER NUMBER", lines)

        # Extract Container Number
        container_number = extract_value_below_keyword("CONTAINER NO", lines)

        # Extract Invoice Number
        invoice_number = extract_value_below_keyword("INVOICE NO", lines)

        # Extract Amount
        amount = extract_value_below_keyword("AMOUNT", lines)

        # Extract Weight (numeric value before "KG")
        weight = extract_value_below_keyword("WEIGHT", lines)
        if weight != "Unknown":
            weight = extract_numeric_before_unit(weight, "KG")

        return {
            "Shipper Name": shipper,
            "Weight": weight,
            "Order Number": order_number,
            "Container Number": container_number,
            "Invoice Number": invoice_number,
            "Amount": amount,
        }
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

# Streamlit app
def main():
    st.title("Invoice Data Extractor")
    st.write("Upload PDFs from your local folder or via links to extract data.")

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
            st.success("Data extraction complete!")
            for idx, entry in enumerate(data, start=1):
                st.write(f"### Entry {idx}")
                st.write(f"**Shipper Name:** {entry['Shipper Name']}")
                st.write(f"**Weight:** {entry['Weight']} KG")
                st.write(f"**Order Number:** {entry['Order Number']}")
                st.write(f"**Container Number:** {entry['Container Number']}")
                st.write(f"**Invoice Number:** {entry['Invoice Number']}")
                st.write(f"**Amount:** {entry['Amount']}")
        else:
            st.warning("No data extracted. Please check the uploaded files or links.")

# Run the app
if __name__ == "__main__":
    main()
