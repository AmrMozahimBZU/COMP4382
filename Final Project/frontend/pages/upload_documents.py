import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api import post

st.title("📎 Upload Documents")
st.info("Upload required documents for your application.")

app_id = st.text_input("Application ID *", placeholder="66abc123...")
applicant_id = st.text_input("Your Applicant ID (optional)")

doc_type = st.selectbox("Document Type *", [
    "ownership_deed", "national_id_copy", "survey_map", "power_of_attorney",
    "title_deed", "court_order", "inheritance_document", "other"
], format_func=lambda x: x.replace("_", " ").title())

file_name = st.text_input("File Name", placeholder="deed_scan.pdf")
file_url = st.text_input("File URL (if hosted)", placeholder="https://...")

if st.button("📤 Upload Document", use_container_width=True):
    if not app_id:
        st.error("Application ID is required.")
    else:
        payload = {
            "document_type": doc_type,
            "file_name": file_name or None,
            "file_url": file_url or None,
            "applicant_id": applicant_id or None
        }
        result, err = post(f"/applications/{app_id}/documents", payload)
        if err:
            st.error(f"Error: {err}")
        else:
            st.success("✅ Document uploaded successfully!")
            st.json(result)
