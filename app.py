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

        # Debug: Print the extracted text
        st.write("Extracted Text:")
        st.write(text)

        # Split text into lines for easier parsing
        lines = text.split("\n")

        # Initialize variables
        shipper = "Unknown"
        weight = "Unknown"
        volume = "Unknown"
        order_numbers = "Unknown"
        packages = "Unknown"
        containers = "Unknown"

        # Function to extract the value below a specific keyword
        def extract_value_below_keyword(keyword, lines):
            for i, line in enumerate(lines):
                if keyword in line:
                    # Return the next line (value below the keyword)
                    if i + 1 < len(lines):
                        return lines[i + 1].strip()
            return "Unknown"

        # Function to extract only the numeric part for specific fields
        def extract_specific_numeric_part(value, unit):
            # Find the numeric part before the unit (e.g., "KG", "M3", "CTN")
            if unit in value:
                return value.split(unit)[0].strip()
            return value

        # Extract Shipper
        shipper = extract_value_below_keyword("SHIPPER", lines)

        # Extract Order Numbers
        order_numbers = extract_value_below_keyword("ORDER NUMBERS / OWNER'S REFERENCE", lines)

        # Extract Weight
        weight = extract_value_below_keyword("WEIGHT", lines)
        if weight != "Unknown":
            weight = extract_specific_numeric_part(weight, "KG")  # Extract numeric part before "KG"

        # Extract Volume
        volume = extract_value_below_keyword("VOLUME", lines)
        if volume != "Unknown":
            volume = extract_specific_numeric_part(volume, "M3")  # Extract numeric part before "M3"

        # Extract Packages
        packages = extract_value_below_keyword("PACKAGES", lines)
        if packages != "Unknown":
            packages = extract_specific_numeric_part(packages, "CTN")  # Extract numeric part before "CTN"

        # Extract Containers
        containers = extract_value_below_keyword("CONTAINERS", lines)

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
                st.write(f"**Volume:** {entry['Volume']} M3")
                st.write(f"**Order Numbers:** {entry['Order Numbers']}")
                st.write(f"**Packages:** {entry['Packages']} CTN")
                st.write(f"**Containers:** {entry['Containers']}")
        else:
            st.warning("No data extracted. Please check the uploaded files or links.")

# Run the app
if __name__ == "__main__":
    main()
