# app.py
import io
import pandas as pd
import streamlit as st
from parse_logic import parse_invoice_pdf_bytes, HEADERS

st.set_page_config(page_title="PDF → Excel Extractor", page_icon="📄", layout="centered")
st.title("📄 PDF → Excel Extractor")
st.caption("Upload one or more broker invoices (PDF). Click Extract to download a single Excel summary.")

uploads = st.file_uploader(
    "Upload PDF files",
    type=["pdf"],
    accept_multiple_files=True,
    help="Drag & drop or browse. Files are processed in memory and not stored."
)

MAX_MB = 25
too_big = False
if uploads:
    for f in uploads:
        if f.size > MAX_MB * 1024 * 1024:
            st.error(f"❌ {f.name} is larger than {MAX_MB} MB")
            too_big = True

extract = st.button("Extract", type="primary", disabled=(not uploads or too_big))

if extract and uploads and not too_big:
    rows = []
    progress = st.progress(0, text="Extracting…")
    status = st.empty()

    for i, f in enumerate(uploads, start=1):
        status.write(f"Parsing: **{f.name}**")
        data = f.read()
        row = parse_invoice_pdf_bytes(data, filename=f.name)
        if row:
            rows.append(row)
        else:
            st.warning(f"Nothing extracted from {f.name}")
        progress.progress(i / len(uploads))

    if not rows:
        st.error("No data extracted from any file.")
    else:
        df = pd.DataFrame(rows, columns=HEADERS)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Summary")
        output.seek(0)
        st.success(f"Done. {len(rows)} row(s) extracted.")
        st.download_button(
            label="⬇️ Download Excel",
            data=output,
            file_name="Invoice_Summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
